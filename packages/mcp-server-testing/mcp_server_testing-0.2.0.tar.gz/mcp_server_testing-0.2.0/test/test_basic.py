"""
最小限のpytestテスト例
"""

def test_simple_assertion():
    """基本的なアサーションテスト"""
    assert 1 + 1 == 2


def test_string_operations():
    """文字列操作のテスト"""
    text = "Hello, World!"
    assert "Hello" in text
    assert len(text) == 13


def test_list_operations():
    """リスト操作のテスト"""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert max(numbers) == 5
    assert min(numbers) == 1


def test_dictionary():
    """辞書のテスト"""
    data = {"name": "Alice", "age": 30}
    assert data["name"] == "Alice"
    assert "age" in data


class TestCalculator:
    """計算機クラスのテスト例"""
    
    def test_addition(self):
        assert self.add(2, 3) == 5
    
    def test_subtraction(self):
        assert self.subtract(5, 3) == 2
    
    def test_multiplication(self):
        assert self.multiply(3, 4) == 12
    
    def test_division(self):
        assert self.divide(10, 2) == 5
    
    def test_division_by_zero(self):
        """ゼロ除算のテスト"""
        try:
            self.divide(10, 0)
            assert False, "Should raise ZeroDivisionError"
        except ZeroDivisionError:
            assert True
    
    # 簡単な計算メソッド
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
