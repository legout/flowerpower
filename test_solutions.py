#!/usr/bin/env python3
"""
Test script to validate potential solutions for the msgspec.convert() error
"""

import sys
from pathlib import Path
import msgspec
from typing import Union

# Add the src directory to the path so we can import flowerpower modules
sys.path.insert(0, 'src')

# Solution 1: Custom StringPath type
class StringPath:
    """A custom type that can handle both str and Path objects for msgspec."""
    
    def __init__(self, value: Union[str, Path, None]):
        if value is None:
            self._value = None
        elif isinstance(value, Path):
            self._value = str(value)
        elif isinstance(value, str):
            self._value = value
        else:
            raise TypeError(f"StringPath must be str, Path, or None, got {type(value)}")
    
    def __str__(self) -> str:
        return self._value if self._value is not None else ""
    
    @property
    def value(self) -> Union[str, None]:
        return self._value
    
    @property
    def path(self) -> Union[Path, None]:
        return Path(self._value) if self._value is not None else None
    
    def __eq__(self, other):
        if isinstance(other, StringPath):
            return self._value == other._value
        return self._value == other
    
    def __repr__(self) -> str:
        return f"StringPath({self._value!r})"

def test_solution_1():
    """Test Solution 1: Custom StringPath type"""
    print("=== Testing Solution 1: Custom StringPath type ===")
    
    # Test the StringPath type
    try:
        # Test basic functionality
        sp1 = StringPath("test/path")
        sp2 = StringPath(Path("test/path"))
        sp3 = StringPath(None)
        
        print(f"✓ StringPath creation works:")
        print(f"   - from str: {sp1} (type: {type(sp1.value)})")
        print(f"   - from Path: {sp2} (type: {type(sp2.value)})")
        print(f"   - from None: {sp3} (type: {type(sp3.value)})")
        
        # Test path property
        print(f"✓ Path conversion works:")
        print(f"   - sp1.path: {sp1.path} (type: {type(sp1.path)})")
        print(f"   - sp2.path: {sp2.path} (type: {type(sp2.path)})")
        print(f"   - sp3.path: {sp3.path} (type: {type(sp3.path)})")
        
        # Test msgspec compatibility
        print(f"✓ Testing msgspec compatibility...")
        
        # Create a test struct with StringPath
        class TestConfig(msgspec.Struct):
            base_dir: StringPath = msgspec.field(default_factory=lambda: StringPath(None))
        
        # Test conversion from dict
        test_dict = {"base_dir": "test/path"}
        config = msgspec.convert(test_dict, TestConfig)
        print(f"   - msgspec.convert from str: {config.base_dir} (type: {type(config.base_dir)})")
        
        test_dict = {"base_dir": None}
        config = msgspec.convert(test_dict, TestConfig)
        print(f"   - msgspec.convert from None: {config.base_dir} (type: {type(config.base_dir)})")
        
        print(f"✓ Solution 1 appears viable!")
        return True
        
    except Exception as e:
        print(f"✗ Solution 1 failed: {e}")
        return False

def test_solution_2():
    """Test Solution 2: Use only str type with internal conversion"""
    print("\n=== Testing Solution 2: Use only str type ===")
    
    try:
        # This would be the simpler approach - just use str type
        # and handle Path conversion in the class methods
        
        class SimpleConfig(msgspec.Struct):
            base_dir: str | None = None
        
        # Test basic functionality
        test_dict = {"base_dir": "test/path"}
        config = msgspec.convert(test_dict, SimpleConfig)
        print(f"✓ Simple str type works: {config.base_dir} (type: {type(config.base_dir)})")
        
        test_dict = {"base_dir": None}
        config = msgspec.convert(test_dict, SimpleConfig)
        print(f"✓ None handling works: {config.base_dir} (type: {type(config.base_dir)})")
        
        print(f"✓ Solution 2 is viable and simpler!")
        return True
        
    except Exception as e:
        print(f"✗ Solution 2 failed: {e}")
        return False

def main():
    """Run all solution tests"""
    print("Testing potential solutions for the msgspec.convert() error...\n")
    
    solution1_works = test_solution_1()
    solution2_works = test_solution_2()
    
    print(f"\n=== SOLUTION SUMMARY ===")
    print(f"Solution 1 (Custom StringPath type): {'✓ WORKS' if solution1_works else '✗ FAILED'}")
    print(f"Solution 2 (Simple str type): {'✓ WORKS' if solution2_works else '✗ FAILED'}")
    
    if solution2_works:
        print(f"\n🎯 RECOMMENDED: Solution 2 - Use only str type")
        print(f"   - Simpler implementation")
        print(f"   - No custom types needed")
        print(f"   - Easier to maintain")
        print(f"   - Path conversion can be handled in property getters")
    elif solution1_works:
        print(f"\n🎯 RECOMMENDED: Solution 1 - Custom StringPath type")
        print(f"   - More type-safe")
        print(f"   - Explicit handling of both str and Path")
        print(f"   - Better documentation of intent")
    else:
        print(f"\n❌ No viable solution found in this test")
    
    return solution1_works or solution2_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)