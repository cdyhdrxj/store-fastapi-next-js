import pytest
import sys

if __name__ == "__main__":
    result = pytest.main(["-v", "--tb=short",
                          "tests/integration/test_auth.py"])
    
    sys.exit(result)
