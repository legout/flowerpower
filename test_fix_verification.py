#!/usr/bin/env python3
"""
Test script to verify that the msgspec.convert() error fix works correctly
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import flowerpower modules
sys.path.insert(0, 'src')

def test_fix_verification():
    """Test that the fix resolves the msgspec.convert() error"""
    print("=== Testing Fix Verification ===")
    
    try:
        from flowerpower.cfg import Config
        
        print("\n1. Loading config...")
        cfg = Config.load("/home/volker/coding/flowerpower/.worktree/code-simplification-analysis/examples/hello-world/base/", pipeline_name="hello_world")
        print(f"✓ Config loaded successfully")
        print(f"   - base_dir type: {type(cfg.base_dir)}")
        print(f"   - base_dir value: {cfg.base_dir}")
        
        # Test the new base_dir_path property
        print(f"   - base_dir_path type: {type(cfg.base_dir_path)}")
        print(f"   - base_dir_path value: {cfg.base_dir_path}")
        
        print("\n2. Converting config to dict...")
        config_dict = cfg.to_dict()
        print(f"✓ to_dict() succeeded")
        print(f"   - base_dir in dict type: {type(config_dict.get('base_dir'))}")
        print(f"   - base_dir in dict value: {config_dict.get('base_dir')}")
        
        print("\n3. Converting dict back to Config (the fix test)...")
        try:
            new_cfg = Config.from_dict(config_dict)
            print(f"✓ from_dict() succeeded! The fix works!")
            print(f"   - base_dir type: {type(new_cfg.base_dir)}")
            print(f"   - base_dir value: {new_cfg.base_dir}")
            print(f"   - base_dir_path type: {type(new_cfg.base_dir_path)}")
            print(f"   - base_dir_path value: {new_cfg.base_dir_path}")
            
            # Verify data integrity
            if cfg.base_dir == new_cfg.base_dir:
                print(f"✓ Data integrity verified: base_dir values match")
            else:
                print(f"✗ Data integrity issue: base_dir values don't match")
                return False
                
            if cfg.base_dir_path == new_cfg.base_dir_path:
                print(f"✓ Data integrity verified: base_dir_path values match")
            else:
                print(f"✗ Data integrity issue: base_dir_path values don't match")
                return False
                
        except Exception as e:
            print(f"✗ from_dict() still fails: {e}")
            return False
        
        print("\n4. Testing edge cases...")
        
        # Test with None base_dir
        try:
            config_dict_none = config_dict.copy()
            config_dict_none['base_dir'] = None
            new_cfg_none = Config.from_dict(config_dict_none)
            print(f"✓ from_dict() with None base_dir works")
            print(f"   - base_dir: {new_cfg_none.base_dir}")
            print(f"   - base_dir_path: {new_cfg_none.base_dir_path}")
        except Exception as e:
            print(f"✗ from_dict() with None base_dir fails: {e}")
            return False
        
        # Test with empty string base_dir
        try:
            config_dict_empty = config_dict.copy()
            config_dict_empty['base_dir'] = ""
            new_cfg_empty = Config.from_dict(config_dict_empty)
            print(f"✓ from_dict() with empty string base_dir works")
            print(f"   - base_dir: '{new_cfg_empty.base_dir}'")
            print(f"   - base_dir_path: {new_cfg_empty.base_dir_path}")
        except Exception as e:
            print(f"✗ from_dict() with empty string base_dir fails: {e}")
            return False
        
        print("\n5. Testing backward compatibility...")
        
        # Test that existing functionality still works
        try:
            # Test pipeline and project access
            print(f"   - Pipeline name: {new_cfg.pipeline.name}")
            print(f"   - Project name: {new_cfg.project.name}")
            print(f"✓ Backward compatibility maintained")
        except Exception as e:
            print(f"✗ Backward compatibility issue: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import required modules: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during test: {e}")
        return False

def main():
    """Run the fix verification test"""
    print("Verifying that the msgspec.convert() error fix works correctly...\n")
    
    success = test_fix_verification()
    
    if success:
        print(f"\n🎉 FIX VERIFICATION SUCCESSFUL!")
        print(f"   - The msgspec.convert() error has been resolved")
        print(f"   - Config.from_dict() now works correctly")
        print(f"   - Data integrity is maintained")
        print(f"   - Backward compatibility is preserved")
        print(f"   - The base_dir_path property provides Path access")
    else:
        print(f"\n❌ FIX VERIFICATION FAILED!")
        print(f"   - The fix did not resolve the issue")
        print(f"   - Further investigation is needed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)