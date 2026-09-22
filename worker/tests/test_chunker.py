import pytest
from chunker import _chunk_python


def test_chunk_python_functions():
    content = """
def hello_world():
    print("Hello")

class MyClass:
    def method_one(self):
        pass
"""
    chunks = _chunk_python(content, "test.py")

    # Should find CLASS and FUNCTION
    assert (
        len(chunks) == 3
    )  # 1 function, 1 class, 1 method (wait, class and method are separate chunks or nested?)
    # Actually, ast.walk will find ClassDef and FunctionDef separately.
    types = [c.chunk_type for c in chunks]
    assert "FUNCTION" in types
    assert "CLASS" in types
    assert "METHOD" in types


def test_chunk_python_syntax_error():
    content = "def invalid_syntax(:"
    chunks = _chunk_python(content, "test.py")

    assert len(chunks) == 1
    assert chunks[0].chunk_type == "MODULE"
    assert chunks[0].metadata.get("parse_error") is True
