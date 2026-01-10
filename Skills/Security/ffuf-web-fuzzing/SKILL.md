---
name: ffuf-web-fuzzing
description: Expert guidance for ffuf web fuzzing during penetration testing, including authenticated fuzzing with raw requests, auto-calibration, and result analysis. Use when performing web application security testing, fuzzing endpoints, testing authentication mechanisms, or conducting penetration tests. Based on jthack/ffuf_claude_skill.
---

# FFUF Web Fuzzing Skill

**Expert guidance for ffuf web fuzzing during penetration testing.**

Comprehensive web fuzzing capabilities using ffuf for security testing, including authenticated fuzzing with raw requests, auto-calibration, and detailed result analysis.

**Original Repository:** [jthack/ffuf_claude_skill](https://github.com/jthack/ffuf_claude_skill)

## What It Does

Provides expert guidance and automation for:
- Web application fuzzing with ffuf
- Authenticated fuzzing with raw HTTP requests
- Auto-calibration for optimal fuzzing performance
- Result analysis and filtering
- Directory and file discovery
- Parameter fuzzing

## Key Features

- **Authenticated Fuzzing** - Support for authenticated requests with cookies/tokens
- **Auto-Calibration** - Automatic baseline calibration for better results
- **Result Analysis** - Advanced filtering and analysis of fuzzing results
- **Raw Request Support** - Direct HTTP request manipulation
- **Multiple Fuzzing Modes** - Directory, file, parameter fuzzing

## Installation

```bash
# Clone the repository
git clone https://github.com/jthack/ffuf_claude_skill.git

# Install ffuf if not already installed
# macOS: brew install ffuf
# Linux: Download from https://github.com/ffuf/ffuf/releases

# Copy skill to your skills directory
cp -r ffuf_claude_skill/ffuf-skill ~/.claude/skills/ffuf-web-fuzzing
```

## Usage Examples

### Basic Directory Fuzzing

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -mc 200,204,301,302,307,401,403
```

### Authenticated Fuzzing

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ \
  -H "Cookie: session=abc123" \
  -H "Authorization: Bearer token123" \
  -mc 200,204
```

### Parameter Fuzzing

```bash
ffuf -w params.txt -u https://example.com/page?FUZZ=value -mc 200
```

## Resources

- **Original Repository**: https://github.com/jthack/ffuf_claude_skill
- **FFUF Documentation**: https://github.com/ffuf/ffuf
- **Wordlists**: https://github.com/danielmiessler/SecLists

## Security Note

⚠️ **Important**: Only use this skill on systems you own or have explicit written permission to test. Unauthorized security testing is illegal.

**Remember**: Use responsibly and ethically for authorized security testing only.
