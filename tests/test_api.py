"""
Basic tests for MT5-TradeBot API
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all required modules can be imported"""
    try:
        import fastapi
        import uvicorn
        import pandas
        import pydantic
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required module: {e}")


def test_fastapi_version():
    """Test FastAPI version"""
    import fastapi
    assert hasattr(fastapi, '__version__')
    print(f"FastAPI version: {fastapi.__version__}")


def test_pandas_available():
    """Test pandas functionality"""
    import pandas as pd
    
    # Create a simple DataFrame
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    assert len(df) == 3
    assert list(df.columns) == ['A', 'B']


def test_pydantic_models():
    """Test Pydantic model creation"""
    from pydantic import BaseModel
    
    class TestModel(BaseModel):
        name: str
        value: int
    
    model = TestModel(name="test", value=42)
    assert model.name == "test"
    assert model.value == 42


def test_python_version():
    """Test Python version compatibility"""
    assert sys.version_info >= (3, 8), "Python 3.8+ required"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
