import re
import ast
import operator
import logging
from Hazel import Tele
from typing import Any
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger("Mods.calculator")

allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv
}

def calculate(expression: str) -> (bool | int | float):
    expression = re.sub(r'\b0+(\d+)', r'\1', expression)
    node = ast.parse(expression, mode='eval').body

    def evaluate(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Invalid constant")

        elif isinstance(node, ast.BinOp):
            if type(node.op) not in allowed_operators:
                raise ValueError("Operator not allowed")
            left = evaluate(node.left)
            right = evaluate(node.right)
            return allowed_operators[type(node.op)](left, right)
        else:
            raise ValueError("Invalid expression")

    return evaluate(node)


@Tele.on_message(filters.regex('//') & filters.me)
async def calculateFunc(c: Client, m: Message):
    exp = m.text
    rm = ['//', ' ']
    for x in rm:
        exp = exp.replace(x, '')
    try:
        result = calculate(exp)
        if result is False or result is None:
            return
        await m.reply(f'» {exp} = `{result}`')
    except Exception as e:
        logger.error(f'Failed to calculate: {exp}. Error: {e}')

MOD_NAME = "Calculator"
MOD_HELP = """**Usage:**
> //2+2 (add)
> //2/2 (divide)
> //2-2 (subract)
> //2*2 (multiply)

Default prefixes will not work for this command only `//` is allowed.
"""