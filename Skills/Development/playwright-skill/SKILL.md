---
name: playwright-skill
description: General-purpose browser automation using Playwright for UI verification, testing, and debugging web applications. Use when testing web applications, automating browser interactions, verifying UI elements, debugging frontend issues, or performing end-to-end testing. Based on lackeyjb/playwright-skill.
---

# Playwright Skill

**General-purpose browser automation using Playwright.**

Comprehensive browser automation and testing capabilities using Playwright for UI verification, end-to-end testing, and web application debugging.

**Original Repository:** [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill)

## What It Does

Provides automation and testing capabilities for:
- Browser automation and interaction
- UI element verification and testing
- End-to-end testing workflows
- Screenshot capture and comparison
- Form filling and submission
- Navigation and routing testing
- Performance monitoring

## Key Features

- **Multi-Browser Support** - Chrome, Firefox, Safari, Edge
- **Auto-Waiting** - Automatic waiting for elements and network
- **Screenshot Testing** - Visual regression testing
- **Network Interception** - Mock and intercept network requests
- **Mobile Emulation** - Test responsive designs
- **CI/CD Integration** - Headless mode for automated testing

## Installation

```bash
# Clone the repository
git clone https://github.com/lackeyjb/playwright-skill.git

# Install Playwright if not already installed
npm install -g playwright
playwright install

# Copy skill to your skills directory
cp -r playwright-skill ~/.claude/skills/playwright-skill
```

## Usage Examples

### Basic Navigation

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://example.com');
  await page.screenshot({ path: 'screenshot.png' });
  await browser.close();
})();
```

### Form Filling

```javascript
await page.fill('#username', 'user@example.com');
await page.fill('#password', 'password123');
await page.click('button[type="submit"]');
```

### Element Verification

```javascript
const title = await page.textContent('h1');
expect(title).toBe('Welcome');
```

## Resources

- **Original Repository**: https://github.com/lackeyjb/playwright-skill
- **Playwright Documentation**: https://playwright.dev
- **Best Practices**: https://playwright.dev/docs/best-practices

**Remember**: Playwright enables robust, reliable browser automation for testing and verification.
