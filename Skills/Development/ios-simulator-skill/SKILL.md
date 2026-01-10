---
name: ios-simulator-skill
description: iOS app building, navigation, and testing through automation. Uses semantic navigation on accessibility APIs to interact with iOS simulators by meaning, not pixel coordinates. Includes 21 production scripts for building, testing, navigation, accessibility audits, visual testing, and device lifecycle management. Works across different screen sizes and survives UI redesigns. Token optimized (96% reduction vs raw tools). Use when building iOS apps, testing iOS applications, automating iOS simulator interactions, or performing accessibility audits on iOS apps. Based on conorluddy/ios-simulator-skill.
---

# iOS Simulator Skill

**iOS app building, navigation, and testing through automation.**

Production-ready automation for iOS app testing and building. Uses semantic navigation on accessibility APIs to interact with iOS simulators by meaning, not pixel coordinates. Works across different screen sizes and survives UI redesigns.

**Original Repository:** [conorluddy/ios-simulator-skill](https://github.com/conorluddy/ios-simulator-skill)

## What It Does

Instead of pixel-based navigation that breaks when UI changes:

```bash
# Fragile - breaks if UI changes
idb ui tap 320 400

# Robust - finds by meaning
python scripts/navigator.py --find-text "Login" --tap
```

Uses semantic navigation on accessibility APIs to interact with elements by their meaning, not coordinates. Works across different screen sizes and survives UI redesigns.

## Features

- **21 production scripts** for building, testing, and automation
- **Semantic navigation** - find elements by text, type, or ID
- **Token optimized** - 96% reduction vs raw tools (3-5 lines default)
- **Zero configuration** - works immediately on macOS with Xcode
- **Structured output** - JSON and formatted text, easy to parse
- **Auto-UDID detection** - no need to specify device each time
- **Batch operations** - boot, delete, erase multiple simulators at once
- **Comprehensive testing** - WCAG compliance, visual diffs, accessibility audits
- **CI/CD ready** - JSON output, exit codes, automated device lifecycle

## Installation

### From Original Repository

```bash
# Clone the repository
git clone https://github.com/conorluddy/ios-simulator-skill.git

# Install as Claude Code Skill
cp -r ios-simulator-skill/ios-simulator-skill ~/.claude/skills/ios-simulator-skill

# Or for project installation
cp -r ios-simulator-skill/ios-simulator-skill .claude/skills/ios-simulator-skill

# Restart Claude Code
```

### Prerequisites

- macOS 12+
- Xcode Command Line Tools (`xcode-select --install`)
- Python 3
- IDB (optional, for interactive features): `brew tap facebook/fb && brew install idb-companion`

## Quick Start

```bash
# 1. Check environment
bash scripts/sim_health_check.sh

# 2. Launch your app
python scripts/app_launcher.py --launch com.example.app

# 3. See what's on screen
python scripts/screen_mapper.py
# Output:
# Screen: LoginViewController (45 elements, 7 interactive)
# Buttons: "Login", "Cancel", "Forgot Password"
# TextFields: 2 (0 filled)

# 4. Tap login button
python scripts/navigator.py --find-text "Login" --tap

# 5. Enter text
python scripts/navigator.py --find-type TextField --enter-text "user@test.com"

# 6. Check accessibility
python scripts/accessibility_audit.py
```

## 21 Scripts Organized by Category

### Build & Development

- **build_and_test.py** - Build projects, run tests, parse results
- **log_monitor.py** - Real-time log monitoring

### Navigation & Interaction

- **screen_mapper.py** - Analyze current screen
- **navigator.py** - Find and interact with elements
- **gesture.py** - Swipes, scrolls, pinches
- **keyboard.py** - Text input and hardware buttons
- **app_launcher.py** - App lifecycle control

### Testing & Analysis

- **accessibility_audit.py** - WCAG compliance checking
- **visual_diff.py** - Screenshot comparison
- **test_recorder.py** - Automated test documentation
- **app_state_capture.py** - Debugging snapshots
- **sim_health_check.sh** - Environment verification

### Advanced Testing & Permissions

- **clipboard.py** - Clipboard management
- **status_bar.py** - Status bar control
- **push_notification.py** - Push notifications
- **privacy_manager.py** - Permission management

### Device Lifecycle

- **simctl_boot.py** - Boot simulator
- **simctl_shutdown.py** - Shutdown simulator
- **simctl_create.py** - Create simulator
- **simctl_delete.py** - Delete simulator
- **simctl_erase.py** - Factory reset

## Usage Examples

### Example 1: Login Flow

```bash
# Launch app
python scripts/app_launcher.py --launch com.example.app

# Map screen to find fields
python scripts/screen_mapper.py

# Enter credentials
python scripts/navigator.py --find-type TextField --index 0 --enter-text "user@test.com"
python scripts/navigator.py --find-type SecureTextField --enter-text "password"

# Tap login
python scripts/navigator.py --find-text "Login" --tap

# Verify accessibility
python scripts/accessibility_audit.py
```

### Example 2: Test Documentation

```bash
# Record test execution
python scripts/test_recorder.py --test-name "Login Flow" --output test-reports/

# Generates:
# - Screenshots per step
# - Accessibility trees
# - Markdown report with timing
```

### Example 3: Visual Testing

```bash
# Capture baseline
python scripts/app_state_capture.py --output baseline/

# Make changes...

# Compare
python scripts/visual_diff.py baseline/screenshot.png current/screenshot.png
```

### Example 4: Permission Testing

```bash
# Grant permissions
python scripts/privacy_manager.py --bundle-id com.example.app --grant camera,location

# Test app behavior with permissions...

# Revoke permissions
python scripts/privacy_manager.py --bundle-id com.example.app --revoke camera,location
```

### Example 5: Device Lifecycle in CI/CD

```bash
# Create test device
DEVICE_ID=$(python scripts/simctl_create.py --device "iPhone 16 Pro" --json | jq -r '.new_udid')

# Run tests
python scripts/build_and_test.py --project MyApp.xcodeproj

# Clean up
python scripts/simctl_delete.py --udid $DEVICE_ID --yes
```

## Design Principles

**Semantic Navigation**: Find elements by meaning (text, type, ID) not pixel coordinates. Survives UI changes and works across device sizes.

**Token Efficiency**: Default output is 3-5 lines. Use `--verbose` for details or `--json` for machine parsing. 96% reduction vs raw tools.

**Accessibility-First**: Built on iOS accessibility APIs for reliability. Better for users with accessibility needs and more robust for automation.

**Zero Configuration**: Works immediately on any macOS with Xcode. No complex setup, no configuration files.

**Structured Data**: Scripts output JSON or formatted text, not raw logs. Easy to parse, integrate, and understand.

**Auto-Learning**: Build system learns your device preference and remembers it for next time.

## Output Efficiency

All scripts minimize output by default:

| Task              | Raw Tools  | This Skill | Savings |
| ----------------- | ---------- | ---------- | ------- |
| Screen analysis   | 200+ lines | 5 lines    | 97.5%   |
| Find & tap button | 100+ lines | 1 line     | 99%     |
| Enter text        | 50+ lines  | 1 line     | 98%     |
| Login flow        | 400+ lines | 15 lines   | 96%     |

This efficiency keeps AI agent conversations focused and cost-effective.

## Troubleshooting

### Environment Issues

```bash
# Run health check
bash scripts/sim_health_check.sh

# Checks: macOS, Xcode, simctl, IDB, Python, simulators, packages
```

### Script Help

```bash
# All scripts support --help
python scripts/navigator.py --help
python scripts/accessibility_audit.py --help
```

### Not Finding Elements

```bash
# Use verbose mode to see all elements
python scripts/screen_mapper.py --verbose

# Check for exact text match
python scripts/navigator.py --find-text "Exact Button Text" --tap
```

## Integration with Claude Code

Claude Code automatically detects when to use this skill based on your request. You don't need to manually invoke it.

**Example conversation:**

```
You: "Set up my iOS app for testing"
Claude: [Uses simctl_boot.py and app_launcher.py automatically]

You: "Tap the login button"
Claude: [Uses navigator.py to find and tap]

You: "Check if the form is accessible"
Claude: [Uses accessibility_audit.py]
```

## Resources

- **Original Repository**: https://github.com/conorluddy/ios-simulator-skill
- **MCP Version**: https://github.com/conorluddy/xc-mcp (if you prefer MCP)
- **Plugin Version**: https://github.com/conorluddy/xclaude-plugin (easier installation)

## Key Takeaways

1. **Semantic over Pixel-based** - Find elements by meaning, not coordinates
2. **Token Efficient** - 96% reduction vs raw tools
3. **Accessibility-First** - Built on accessibility APIs
4. **CI/CD Ready** - JSON output, exit codes, automated lifecycle
5. **Comprehensive Testing** - WCAG, visual diffs, accessibility audits

**Remember**: Use semantic navigation for robust, maintainable iOS automation.
