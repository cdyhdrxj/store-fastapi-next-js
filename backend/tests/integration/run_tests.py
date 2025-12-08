import pytest
import sys

if __name__ == "__main__":
    result = pytest.main(["-v", "-s", "--tb=short",
                          "tests/integration/1.py",
                          "tests/integration/2.py",
                          "tests/integration/3.py",
                          "tests/integration/4.py",
                          "tests/integration/5.py",
                          "tests/integration/6.py",
                          "tests/integration/7.py"])
    
    sys.exit(result)
