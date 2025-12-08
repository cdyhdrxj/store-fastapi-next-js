import pytest
import sys

if __name__ == "__main__":
    result = pytest.main(["-v", "--tb=short",
                          "tests/unit/test_buy.py",
                          "tests/unit/test_item.py", 
                          "tests/unit/test_password.py",
                          "tests/unit/test_permission_checker.py",
                          "tests/unit/test_connection_manager.py",
                          "tests/unit/test_image.py"])
    
    sys.exit(result)
