from enum import Enum
import json
from typing import List, Union

import rich
from pydantic import BaseModel

import openai
from openai import OpenAI
import configparser

config_path = '/home/miasdz/桌面/py-test/study/config.ini'
config = configparser.ConfigParser()
config.read(config_path)

llm_type = config['common']['llm']
api_key = config[llm_type]['OPENAI_API_KEY']
base_url = config[llm_type]['OPENAI_API_BASE_URL']
model = config[llm_type]['OPENAI_API_MODEL']

print(llm_type, base_url, model, api_key)

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"


class Column(str, Enum):
    id = "id"
    status = "status"
    expected_delivery_date = "expected_delivery_date"
    delivered_at = "delivered_at"
    shipped_at = "shipped_at"
    ordered_at = "ordered_at"
    canceled_at = "canceled_at"


class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"
    le = "<="
    ge = ">="
    ne = "!="


class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class DynamicValue(BaseModel):
    column_name: str


class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int, DynamicValue]


class Query(BaseModel):
    table_name: Table
    columns: List[Column]
    conditions: List[Condition]
    order_by: OrderBy


# ---------------------------------------------------------------------------
# 本地“数据库”：用内存中的小数据集模拟真实数据库。
# 实际项目中把 execute_query 换成 SQL / API 调用即可。
# ---------------------------------------------------------------------------

ORDERS = [
    {"id": 1, "status": "fulfilled", "expected_delivery_date": "2023-11-12",
     "delivered_at": "2023-11-10", "shipped_at": "2023-11-06", "ordered_at": "2023-11-05", "canceled_at": None},
    {"id": 2, "status": "fulfilled", "expected_delivery_date": "2023-11-20",
     "delivered_at": "2023-11-25", "shipped_at": "2023-11-15", "ordered_at": "2023-11-14", "canceled_at": None},
    {"id": 3, "status": "fulfilled", "expected_delivery_date": "2023-11-28",
     "delivered_at": None, "shipped_at": "2023-11-22", "ordered_at": "2023-11-21", "canceled_at": None},
    {"id": 4, "status": "fulfilled", "expected_delivery_date": "2023-12-10",
     "delivered_at": "2023-12-09", "shipped_at": "2023-12-04", "ordered_at": "2023-12-03", "canceled_at": None},
    {"id": 5, "status": "canceled", "expected_delivery_date": "2023-11-15",
     "delivered_at": None, "shipped_at": None, "ordered_at": "2023-11-02", "canceled_at": "2023-11-04"},
    {"id": 6, "status": "fulfilled", "expected_delivery_date": "2023-10-28",
     "delivered_at": "2023-10-27", "shipped_at": "2023-10-22", "ordered_at": "2023-10-20", "canceled_at": None},
]

CUSTOMERS = [
    {"id": 1, "status": "active", "expected_delivery_date": None,
     "delivered_at": None, "shipped_at": None, "ordered_at": "2023-01-01", "canceled_at": None},
    {"id": 2, "status": "active", "expected_delivery_date": None,
     "delivered_at": None, "shipped_at": None, "ordered_at": "2023-02-01", "canceled_at": None},
]

PRODUCTS = [
    {"id": 1, "status": "active", "expected_delivery_date": None,
     "delivered_at": None, "shipped_at": None, "ordered_at": "2023-03-01", "canceled_at": None},
    {"id": 2, "status": "discontinued", "expected_delivery_date": None,
     "delivered_at": None, "shipped_at": None, "ordered_at": "2023-04-01", "canceled_at": None},
]

TABLES = {
    "orders": ORDERS,
    "customers": CUSTOMERS,
    "products": PRODUCTS,
}


def _compare(left, operator: Operator, right):
    """对一行中某一列的值执行比较。right 可能是字面值，也可能是另一列（DynamicValue）。"""
    if operator == Operator.eq:
        return left == right
    if operator == Operator.ne:
        return left != right
    # 大小比较需要两个值都有意义；None 表示“无值”，不参与排序类比较
    if left is None or right is None:
        return False
    if isinstance(left, int) and isinstance(right, str):
        right = int(right)
    if operator == Operator.gt:
        return left > right
    if operator == Operator.lt:
        return left < right
    if operator == Operator.le:
        return left <= right
    if operator == Operator.ge:
        return left >= right
    raise ValueError(f"unknown operator: {operator}")


def execute_query(query: Query) -> str:
    """在本地执行模型生成的 Query，返回可回传给模型的 JSON 字符串。"""
    rows = [dict(row) for row in TABLES[query.table_name.value]]

    # 1) 过滤：所有 condition 都满足才保留
    for cond in query.conditions:
        matched = []
        for row in rows:
            left = row.get(cond.column)
            # DynamicValue 表示与同行的另一列比较，这里取该列的值
            right = row.get(cond.value.column_name) if isinstance(cond.value, DynamicValue) else cond.value
            if _compare(left, cond.operator, right):
                matched.append(row)
        rows = matched

    # 2) 排序：按第一个选中的列排序
    if query.columns:
        rows.sort(key=lambda r: r.get(query.columns[0].value) or "", reverse=query.order_by == OrderBy.desc)

    # 3) 投影：只保留请求的列
    result = [
        {c.value: row.get(c.value) for c in query.columns}
        for row in rows
    ]

    return json.dumps({"row_count": len(result), "rows": result}, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 第一轮：把用户请求解析成结构化的 Query 工具调用
# ---------------------------------------------------------------------------

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. The current date is August 6, 2024. You help users query for the data they are looking for by calling the query function.",
    },
    {
        "role": "user",
        "content": "look up all my orders in november of last year that were fulfilled but not delivered on time",
    },
]

completion = client.chat.completions.parse(
    model=model,
    messages=messages,
    tools=[
        openai.pydantic_function_tool(Query),
    ],
)

message = completion.choices[0].message
tool_call = (message.tool_calls or [])[0]
rich.print(tool_call.function)
print('-------------')

# parsed_arguments 是模型返回的结构化参数，已被自动反序列化成 Query 对象
assert isinstance(tool_call.function.parsed_arguments, Query)
parsed_query = tool_call.function.parsed_arguments
rich.print(parsed_query.table_name)

# ---------------------------------------------------------------------------
# 第二步：本地执行返回的 function
# ---------------------------------------------------------------------------

result_json = execute_query(parsed_query)
print('-------------')
print("本地执行结果:")
rich.print(json.loads(result_json))

# ---------------------------------------------------------------------------
# 第三步：把工具调用与执行结果回传给模型，让模型生成最终答复
# ---------------------------------------------------------------------------

# 1) 先把 assistant 的 tool_calls 消息原样追加进会话
#    注意 arguments 必须是原始 JSON 字符串，不能传解析后的对象
messages.append(
    {
        "role": "assistant",
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
        ],
    }
)

# 2) 追加 role="tool" 的执行结果，tool_call_id 必须与上面的 id 对应
messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result_json,
    }
)

# 3) 再次提交模型（这次用普通 create，拿到自然语言答复）
final_completion = client.chat.completions.create(
    model=model,
    messages=messages,
)
print('-------------')
print("模型最终答复:")
print(final_completion.choices[0].message.content)

# 说明：
# - 上述三步就是一次完整的 function calling 闭环。若工具执行后又返回新的
#   tool_calls，则需要把结果继续追加进 messages，循环执行直到模型不再调用工具。
# - 多工具/并发调用时（parallel_tool_calls=True），需要遍历 message.tool_calls，
#   逐个执行并追加对应的 tool 消息。