import ast
import logging
from decimal import Decimal, getcontext, DivisionByZero
from typing import Callable, Dict, Union

from Hazel import Tele
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

logger: logging.Logger = logging.getLogger("Mods.calculator")

getcontext().prec = 28

# Allowed operators mapped to Decimal-safe functions
allowed_operators: Dict[type, Callable[[Decimal, Decimal], Decimal]] = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Mod: lambda a, b: a % b,
}


def clean_decimal(value: Decimal) -> str:
    """
    Remove trailing zeros and unnecessary decimal points.
    """
    s: str = format(value, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def calculate(expression: str) -> Decimal:
    """
    Safely evaluate a mathematical expression using AST and Decimal.
    """
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise ValueError("Invalid expression")

    def evaluate(node: ast.AST) -> Decimal:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, int):
                return Decimal(node.value)

            if isinstance(node.value, float):
                # Use repr to avoid precision corruption
                return Decimal(repr(node.value))

            raise ValueError("Invalid constant")

        if isinstance(node, ast.BinOp):
            if type(node.op) not in allowed_operators:
                raise ValueError("Operator not allowed")

            left: Decimal = evaluate(node.left)
            right: Decimal = evaluate(node.right)

            if isinstance(node.op, ast.Div) and right == 0:
                raise DivisionByZero("Division by zero")

            return allowed_operators[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -evaluate(node.operand)

            if isinstance(node.op, ast.UAdd):
                return evaluate(node.operand)

            raise ValueError("Invalid unary operator")

        raise ValueError("Invalid expression")

    return evaluate(parsed.body)


@Tele.on_message(filters.regex(r"^//"), sudo=True)
async def calculateFunc(c: Client, m: Message) -> None:
    exp: str = m.text.strip()  # type: ignore

    if not exp.startswith("//"):
        return

    exp = exp[2:].strip()

    if not exp:
        return
    if not all(ch in "0123456789+-*/%.() " for ch in exp):
        return

    try:
        result: Decimal = calculate(exp)
        result_str: str = clean_decimal(result)

        await m.reply(f"» {exp} = `{result_str}`")

    except DivisionByZero:
        await m.reply("Division by zero is not allowed.")

    except Exception as e:
        logger.error(f"Failed to calculate: {exp}. Error: {e}")


MOD_NAME: str = "Calculator"
MOD_HELP: str = """**Usage:**
> //2+2
> //2/2
> //2-2
> //2*2
> //(2+3)*4
> //1.1-1.2

Only `//` prefix is allowed. Default prefixes will NOT work.
"""