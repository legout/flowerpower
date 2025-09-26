#!/usr/bin/env python3
"""
Test script to reproduce the msgspec.convert() error with Config.from_dict()
"""

import sys
from pathlib import Path

def test_reproduce_bug():
    # Add the src directory to the path so we can import flowerpower modules
    sys.path.insert(0, 'src')

    try:
        from flowerpower.cfg import Config
        
        print("=== Testing Config.from_dict() bug reproduction ===")
        
        # Step 1: Load a config (this should work)
        print("\n1. Loading config...")
        cfg = Config.load("/home/volker/coding/flowerpower/.worktree/code-simplification-analysis/examples/hello-world/base/", pipeline_name="hello_world")
        print(f"✓ Config loaded successfully")
        print(f"   - base_dir type: {type(cfg.base_dir)}")
        print(f"   - base_dir value: {cfg.base_dir}")
        
        # Step 2: Convert to dict (this should work)
        print("\n2. Converting config to dict...")
        config_dict = cfg.to_dict()
        print(f"✓ to_dict() succeeded")
        print(f"   - base_dir in dict type: {type(config_dict.get('base_dir'))}")
        print(f"   - base_dir in dict value: {config_dict.get('base_dir')}")
        
        # Step 3: Try to convert back to Config (this should fail)
        print("\n3. Attempting to convert dict back to Config...")
        try:
            new_cfg = Config.from_dict(config_dict)
            print(f"✓ from_dict() succeeded unexpectedly!")
            print(f"   - This means the bug is not reproduced")
            return False  # Bug not reproduced
        except Exception as e:
            print(f"✗ from_dict() failed with expected error:")
            print(f"   - Error type: {type(e).__name__}")
            print(f"   - Error message: {str(e)}")
            
            # Analyze the error
            if "Type unions containing a custom type" in str(e):
                print(f"   ✓ Confirmed: This is the msgspec type union limitation error")
            else:
                print(f"   ? Unexpected error type")
                
            return True  # Bug successfully reproduced
        
    except ImportError as e:
        print(f"✗ Failed to import required modules: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during test: {e}")
        return False

if __name__ == "__main__":
    reproduced = test_reproduce_bug()
    if reproduced:
        print(f"\n=== BUG REPRODUCTION SUCCESSFUL ===")
        sys.exit(1)  # Exit with error code to indicate bug was found
    else:
        print(f"\n=== BUG NOT REPRODUCED ===")
        sys.exit(0)