import re
import ast
import operator
import logging
from decimal import Decimal, getcontext
from Hazel import Tele
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger("Mods.calculator")

getcontext().prec = 28

allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}

def calculate(expression: str) -> Decimal:
    expression = re.sub(r'\b0+(\d+)', r'\1', expression)
    node = ast.parse(expression, mode='eval').body

    def evaluate(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return Decimal(str(node.value))
            raise ValueError("Invalid constant")

        elif isinstance(node, ast.BinOp):
            if type(node.op) not in allowed_operators:
                raise ValueError("Operator not allowed")

            left = evaluate(node.left)
            right = evaluate(node.right)

            return allowed_operators[type(node.op)](left, right)

        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -evaluate(node.operand)
            raise ValueError("Invalid unary operator")

        else:
            raise ValueError("Invalid expression")

    return evaluate(node)


@Tele.on_message(filters.regex(r'^//') & filters.me)
async def calculateFunc(c: Client, m: Message):
    exp = m.text.strip()

    if not exp.startswith('//'):
        return

    exp = exp[2:].strip()

    if not re.fullmatch(r'[0-9+\-*/%.() ]+', exp):
        return

    if not exp: return

    try:
        result = calculate(exp)
        result_str = str(result.normalize())
        await m.reply(f'» {exp} = `{result_str}`')

    except Exception as e:
        logger.error(f'Failed to calculate: {exp}. Error: {e}')


MOD_NAME = "Calculator"
MOD_HELP = """**Usage:**
> //2+2
> //2/2
> //2-2
> //2*2
> //(2+3)*4
> //1.1-1.2

Only `//` prefix is allowed. Defualt prefixes will NOT work.
"""