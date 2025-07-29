"""
mcp_server_testing.server の最小限テスト
"""

from mcp_server_testing.server import greet


def test_greet():
    """greet関数のテスト"""
    result = greet("Alice")
    assert result == "Hello, Alice!"


def test_greet_empty_name():
    """空文字名のテスト"""
    result = greet("")
    assert result == "Hello, !"


def test_greet_multiple_names():
    """複数の名前のテスト"""
    names = ["Bob", "Charlie", "Diana"]
    for name in names:
        result = greet(name)
        assert result == f"Hello, {name}!"
