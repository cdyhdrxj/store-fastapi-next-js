import pytest
import sys

if __name__ == "__main__":
    result = pytest.main(["-v", "--tb=short", "tests/test_unit_buy.py", "tests/test_unit_item.py", 
                         "tests/test_unit_password.py", "tests/test_unit_permission_checker.py",
                         "tests/test_unit_connection_manager.py", "tests/test_unit_image.py"])
    
    sys.exit(result)