---
name: web-asset-generator
description: Generates web assets like favicons, app icons, and social media images for web applications. Use when creating favicons, generating app icons, creating social media preview images, optimizing web assets, or preparing assets for deployment. Based on alonw0/web-asset-generator.
---

# Web Asset Generator Skill

**Generates web assets like favicons, app icons, and social media images.**

Comprehensive tool for generating all types of web assets needed for modern web applications, including favicons, app icons, and social media preview images.

**Original Repository:** [alonw0/web-asset-generator](https://github.com/alonw0/web-asset-generator)

## What It Does

Generates:
- **Favicons** - Multiple sizes and formats (ICO, PNG, SVG)
- **App Icons** - iOS, Android, web app icons in required sizes
- **Social Media Images** - Open Graph images, Twitter cards, LinkedIn previews
- **PWA Assets** - Progressive Web App icons and manifests
- **Responsive Images** - Multiple sizes for different devices
- **Optimized Formats** - WebP, AVIF, optimized PNG/JPEG

## Key Features

- **Multiple Formats** - ICO, PNG, SVG, WebP, AVIF
- **Multiple Sizes** - All required sizes for different platforms
- **Optimization** - Automatic image optimization
- **Batch Processing** - Generate all assets at once
- **Template Support** - Use templates for consistent styling
- **CI/CD Ready** - Automated asset generation

## Installation

```bash
# Clone the repository
git clone https://github.com/alonw0/web-asset-generator.git

# Install dependencies
npm install

# Copy skill to your skills directory
cp -r web-asset-generator ~/.claude/skills/web-asset-generator
```

## Usage Examples

### Generate Favicon Set

```bash
# Generate favicons from source image
node generate-favicons.js source.png

# Outputs:
# - favicon.ico
# - favicon-16x16.png
# - favicon-32x32.png
# - favicon-96x96.png
# - favicon.svg
```

### Generate App Icons

```bash
# Generate app icons for all platforms
node generate-app-icons.js app-icon.png

# Outputs iOS, Android, and web app icons
```

### Generate Social Media Images

```bash
# Generate social media preview images
node generate-social.js banner.png

# Outputs:
# - og-image.png (1200x630)
# - twitter-card.png (1200x675)
# - linkedin-preview.png (1200x627)
```

## Resources

- **Original Repository**: https://github.com/alonw0/web-asset-generator
- **Favicon Generator**: https://realfavicongenerator.net/
- **Social Media Sizes**: https://sproutsocial.com/insights/social-media-image-sizes-guide/

**Remember**: Web assets are essential for professional web applications - generate them systematically, not manually.
