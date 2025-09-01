import msgspec
from typing import Callable, Any, Tuple, Dict, Optional, Union

# Define the problematic types
CallbackType = Union[Callable, Tuple[Callable, Optional[Tuple], Optional[Dict]]]

class TestConfig(msgspec.Struct):
    """Test configuration with the problematic callback type"""
    on_success: Optional[CallbackType] = None
    on_failure: Optional[CallbackType] = None

def test_msgspec_conversion():
    """Test if msgspec can convert a dictionary to our config type"""
    print("="*50)
    print("Testing msgspec conversion with problematic type definition")
    print("="*50)
    
    # Create test data that matches our YAML structure
    test_data = {
        "on_success": None,
        "on_failure": None
    }
    
    try:
        # Try to convert the dictionary to our config type
        config = msgspec.convert(test_data, TestConfig)
        print("✓ Basic conversion with None values succeeded")
        
        # Test with a simple callable
        def test_callback():
            pass
            
        test_data2 = {
            "on_success": test_callback,
            "on_failure": None
        }
        
        try:
            config2 = msgspec.convert(test_data2, TestConfig)
            print("✓ Conversion with simple callable succeeded (unexpected!)")
        except Exception as e:
            print(f"✗ Conversion with simple callable failed: {type(e).__name__}: {str(e)}")
            
        # Test with tuple format
        test_data3 = {
            "on_success": (test_callback, (), {}),
            "on_failure": None
        }
        
        try:
            config3 = msgspec.convert(test_data3, TestConfig)
            print("✓ Conversion with tuple format succeeded (unexpected!)")
        except Exception as e:
            print(f"✗ Conversion with tuple format failed: {type(e).__name__}: {str(e)}")
            
    except Exception as e:
        print(f"✗ Basic conversion failed: {type(e).__name__}: {str(e)}")

def main():
    test_msgspec_conversion()
    
    print("\nConclusion:")
    print("If you see errors about 'Type unions containing a custom type', this confirms")
    print("the issue with the current type definition in RunConfig.")
    print("\nRecommended fix:")
    print("1. Replace the union type with a dedicated CallbackSpec class")
    print("2. Implement conversion logic for different callback patterns")

if __name__ == "__main__":
    main()