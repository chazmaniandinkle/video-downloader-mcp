# Security Guide

## 🔒 Security Architecture

The MCP server implements a comprehensive security framework to protect against common vulnerabilities when handling file downloads and user input.

## 🛡️ Core Security Components

### 1. SecureConfigManager
- **TOML-based configuration** with secure defaults
- **No deserialization vulnerabilities** (unlike YAML/Pickle)
- **Deep merging** of user config with secure defaults
- **Automatic config creation** with safe permissions

### 2. PathValidator
- **Path traversal protection** - blocks `../`, `..\\`, and variants
- **Absolute path restriction** - only relative paths allowed
- **Filename length limits** - prevents filesystem issues
- **Extension allowlisting** - only permitted file types
- **Template sanitization** - removes dangerous shell characters

### 3. LocationManager
- **Configured download locations** - no arbitrary path access
- **Directory creation with safe permissions** (755)
- **Write permission validation** before use
- **Path boundary enforcement** - files cannot escape designated areas

## 🚧 Security Features

### Path Security
```python
# ✅ Safe - relative path within allowed location
{
    "location_id": "default",
    "relative_path": "movies/action",
    "filename_template": "%(title)s.%(ext)s"
}

# ❌ Blocked - path traversal attempt
{
    "location_id": "default", 
    "relative_path": "../../../etc/passwd"
}

# ❌ Blocked - absolute path
{
    "output_path": "/etc/shadow"
}
```

### Template Security
```python
# ✅ Safe template variables
"%(title)s - %(uploader)s.%(ext)s"

# 🛡️ Sanitized - dangerous characters removed
"%(title)s | rm -rf /.%(ext)s"  # → "%(title)s _ rm -rf _.%(ext)s"
```

### Extension Security
```toml
# Only these extensions are allowed
allowed_extensions = [
    "mp4", "webm", "mkv", "avi", "mov",    # Video
    "m4a", "mp3", "aac", "ogg", "wav",     # Audio  
    "vtt", "srt", "ass", "ssa"             # Subtitles
]
```

## 📋 Security Configuration

### Default Security Settings
```toml
[security]
# Enforce location restrictions
enforce_location_restrictions = true

# Prevent long filenames that could cause filesystem issues
max_filename_length = 255

# Block path traversal attempts
block_path_traversal = true

# Allowed file extensions
allowed_extensions = ["mp4", "webm", "mkv", "avi", "mov", "m4a", "mp3", "aac", "ogg", "wav", "vtt", "srt", "ass", "ssa"]

[logging]
# Log security events for monitoring
log_security_events = true
log_downloads = true
```

### Secure Download Locations
```toml
[download_locations]
# Default secure location
default = "~/video-downloader"

# Additional restricted locations
media = "~/Videos/Downloads" 
temp = "/tmp/video-cache"
archive = "~/Documents/VideoArchive"
```

## 🔧 MCP Tool Security

### Secure download_video Tool
```json
{
    "url": "https://example.com/video",
    "location_id": "default",           // Required: must be configured location
    "relative_path": "subfolder",       // Optional: validated relative path
    "filename_template": "%(title)s.%(ext)s"  // Optional: sanitized template
}
```

### Legacy Support (Deprecated)
```json
{
    "url": "https://example.com/video", 
    "output_path": "/path/to/file.mp4"  // DEPRECATED: bypasses security
}
```

**⚠️ Warning**: Legacy `output_path` bypasses security validation and should only be used in trusted environments.

## 🚫 Attack Prevention

### Path Traversal
```bash
# These are automatically blocked:
../../../etc/passwd
..\\..\\..\\windows\\system32
file:///etc/shadow
```

### Command Injection
```bash
# Template sanitization prevents:
$(rm -rf /)
`dangerous command`
| malicious pipe
& background process
```

### Directory Escape
```python
# Symlink attacks and canonicalization bypass attempts are prevented
# by realpath() validation and boundary checking
```

## 📊 Security Monitoring

### Logging
All security events are logged when `log_security_events = true`:

```
INFO:server:Path validation failed: Path traversal sequences detected
INFO:server:Download completed: https://example.com -> /secure/path/video.mp4
WARNING:server:Using deprecated output_path parameter
```

### Validation Results
Every path operation returns structured validation results:
```python
(is_valid, normalized_path, error_message)
```

## 🔍 Security Testing

### Automated Tests
```bash
# Run security test suite
python test_security.py

# Test MCP tool security  
python test_mcp_security.py
```

### Manual Validation
```python
from server import SecureConfigManager, PathValidator, LocationManager

config = SecureConfigManager()
validator = PathValidator(config)
location_manager = LocationManager(config)

# Test path validation
valid, path, error = validator.validate_path("../escape.mp4", "/safe/dir")
print(f"Valid: {valid}, Error: {error}")

# Test location management
valid, path, error = location_manager.construct_download_path("default", "test", "%(title)s.%(ext)s")
```

## 🎯 Best Practices

### For LLM Clients
1. **Always use location_id** instead of output_path
2. **Validate user input** before passing to tools
3. **Use relative paths** for organization within locations
4. **Monitor security logs** for unusual activity

### For System Administrators
1. **Review download locations** in config.toml
2. **Set appropriate file permissions** on download directories
3. **Monitor disk usage** in download locations
4. **Rotate logs** to prevent disk space issues

### For Developers
1. **Never bypass security validation** in custom tools
2. **Use PathValidator** for all path operations
3. **Sanitize templates** before use
4. **Log security events** for audit trails

## 🚨 Security Incident Response

### If Path Traversal is Detected
1. Check logs for the source of malicious input
2. Review and strengthen input validation
3. Consider blocking the source if automated

### If Unauthorized Files are Downloaded
1. Check download locations for unexpected files
2. Review security configuration
3. Ensure proper file permissions

### If Performance Issues Occur
1. Check for extremely long filenames
2. Monitor download directory sizes
3. Review filename length limits

## 🔒 Security Assumptions

### Trusted Environment
- The MCP server runs in a trusted environment
- yt-dlp binary is trusted and up-to-date
- Configuration files have appropriate permissions

### Threat Model
- **Protected against**: Path traversal, command injection, unauthorized file access
- **Not protected against**: Network-level attacks, compromised yt-dlp binary, root-level system compromise

## 📞 Security Contact

For security issues or questions:
1. Check existing security tests and documentation
2. Review configuration for proper setup
3. Consider the threat model limitations

Remember: **Security is layered** - this framework provides strong protection against common file handling vulnerabilities, but should be part of a broader security strategy.