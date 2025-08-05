#!/usr/bin/env python3
"""
Test the security enhancements
"""

import sys
import json
import tempfile
import os
from pathlib import Path

sys.path.append('.')
from server import SecureConfigManager, PathValidator, LocationManager

def test_config_manager():
    """Test SecureConfigManager"""
    print("🔧 Testing SecureConfigManager")
    print("=" * 40)
    
    # Test with default config
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.toml"
        config = SecureConfigManager(str(config_path))
        
        print(f"✅ Config loaded successfully")
        print(f"   Default location: {config.get('download_locations.default')}")
        print(f"   Security enabled: {config.get('security.enforce_location_restrictions')}")
        print(f"   Max filename length: {config.get('security.max_filename_length')}")
        print()

def test_path_validator():
    """Test PathValidator"""
    print("🛡️  Testing PathValidator")
    print("=" * 40)
    
    config = SecureConfigManager()
    validator = PathValidator(config)
    
    test_cases = [
        ("safe.mp4", "/tmp/test", True, "Safe relative path"),
        ("subdir/video.mp4", "/tmp/test", True, "Safe subdirectory"),
        ("../escape.mp4", "/tmp/test", False, "Path traversal attempt"),
        ("..\\\\escape.mp4", "/tmp/test", False, "Windows path traversal"),
        ("/absolute/path.mp4", "/tmp/test", False, "Absolute path (not allowed)"),
        ("very_long_filename_" + "x" * 300 + ".mp4", "/tmp/test", False, "Filename too long"),
        ("script.sh", "/tmp/test", False, "Invalid extension"),
    ]
    
    for path, base_dir, expected, description in test_cases:
        valid, normalized, error = validator.validate_path(path, base_dir)
        status = "✅" if valid == expected else "❌"
        print(f"   {status} {description}")
        print(f"      Path: {path}")
        print(f"      Valid: {valid}, Error: {error}")
        if valid and normalized:
            print(f"      Normalized: {normalized}")
        print()

def test_location_manager():
    """Test LocationManager"""
    print("📁 Testing LocationManager")
    print("=" * 40)
    
    config = SecureConfigManager()
    location_manager = LocationManager(config)
    
    # Test getting locations
    locations = location_manager.get_locations()
    print(f"✅ Found {len(locations)} configured locations:")
    for location_id, info in locations.items():
        print(f"   {location_id}: {info['original']} ({'writable' if info['writable'] else 'not writable'})")
    print()
    
    # Test path construction
    test_cases = [
        ("default", None, None, "Default location with default template"),
        ("default", "subdir", "%(title)s.%(ext)s", "Subdirectory with template"),
        ("nonexistent", None, None, "Invalid location ID"),
    ]
    
    for location_id, rel_path, template, description in test_cases:
        print(f"🧪 Testing: {description}")
        valid, path, error = location_manager.construct_download_path(location_id, rel_path, template)
        if valid:
            print(f"   ✅ Valid path: {path}")
        else:
            print(f"   ❌ Invalid: {error}")
        print()

def test_template_sanitization():
    """Test template variable sanitization"""
    print("🧹 Testing Template Sanitization")
    print("=" * 40)
    
    config = SecureConfigManager()
    validator = PathValidator(config)
    
    test_templates = [
        "%(title)s.%(ext)s",
        "%(title)s | dangerous.%(ext)s", 
        "%(title)s $(rm -rf /).%(ext)s",
        "%(title)s & evil command.%(ext)s",
    ]
    
    for template in test_templates:
        sanitized = validator.sanitize_template_vars(template)
        print(f"   Original:  {template}")
        print(f"   Sanitized: {sanitized}")
        print()

def test_integration():
    """Test integrated security flow"""
    print("🔗 Testing Security Integration")
    print("=" * 40)
    
    try:
        config = SecureConfigManager()
        location_manager = LocationManager(config)
        
        # Test secure download path construction
        valid, path, error = location_manager.construct_download_path(
            "default", 
            "tests", 
            "%(title)s.%(ext)s"
        )
        
        if valid:
            print(f"✅ Integration test passed")
            print(f"   Constructed path: {path}")
        else:
            print(f"❌ Integration test failed: {error}")
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
    
    print()

if __name__ == "__main__":
    print("🔐 Testing Video Downloader Security Framework")
    print("=" * 60)
    print()
    
    test_config_manager()
    test_path_validator()
    test_location_manager()
    test_template_sanitization()
    test_integration()
    
    print("🎉 Security testing completed!")