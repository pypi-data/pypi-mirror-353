import sys
import ast
from typing import Any, Iterable
from glob import glob


class FileUtils:

    @staticmethod
    def get_python_files(directory: str) -> Iterable[str]:
        """
        Generator to yield Python files from a directory.
        """
        for filepath in glob(f"{directory}/**/*.py", recursive=True):
            yield filepath


class ReqLint:
    """
    Python Requests Linter

    Use case:
        - Identify requests.request() calls that don't specify a timeout param
    """

    @staticmethod
    def __has_timeout_kwarg(kwargs: list[ast.keyword]) -> bool:
        for kwarg in kwargs:
            if "timeout=" in ast.unparse(kwarg):
                return True
        return False

    @staticmethod
    def __is_request_call(node: Any) -> bool:
        """Check if the AST node is a call to requests.get() or similar."""
        targetted_attributes = [
            "request",
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
        ]
        is_call = isinstance(node, ast.Call)
        if not is_call:
            return False

        is_requests_call = is_call and node.func.value.id == "requests"  # type: ignore
        if not is_requests_call:
            return False

        has_request_call_attr = False
        for attr in targetted_attributes:
            if node.func.attr == attr:  # type: ignore
                has_request_call_attr = True

        return is_call and is_requests_call and has_request_call_attr

    @classmethod
    def parse(cls, s: str) -> Iterable[Any]:
        """Parse a string containing Python code and yield request calls without a timeout parameter."""
        parsed_ast = ast.parse(s)
        for node in ast.walk(parsed_ast):
            if cls.__is_request_call(node):
                keywords = [kw for kw in node.keywords]  # type: ignore
                if not cls.__has_timeout_kwarg(keywords):
                    yield node

    @classmethod
    def has_lint_errors(cls, code: str) -> bool:
        return any(cls.parse(code))

    @classmethod
    def lint(cls, code: str) -> Iterable[str]:
        for node in cls.parse(code):
            line_number = node.lineno
            yield f"Line {line_number}: Request call without timeout parameter."


if __name__ == "__main__":
    target_dir = sys.argv[-1]
    for filepath in FileUtils.get_python_files(target_dir):
        with open(filepath, "r") as f:
            code = f.read()
            for error in ReqLint().lint(code):
                print(f"{filepath}: {error}")
