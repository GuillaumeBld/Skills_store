---
name: claude-d3js-skill
description: Create data visualizations using d3.js for interactive charts, graphs, and data-driven visualizations. Use when creating interactive data visualizations, building charts and graphs, visualizing datasets, or creating data-driven art. Based on chrisvoncsefalvay/claude-d3js-skill.
---

# Claude d3.js Skill

**Create data visualizations using d3.js.**

Comprehensive d3.js capabilities for creating interactive charts, graphs, and data-driven visualizations with full control over visual representation.

**Original Repository:** [chrisvoncsefalvay/claude-d3js-skill](https://github.com/chrisvoncsefalvay/claude-d3js-skill)

## What It Does

Enables creation of:
- Interactive data visualizations
- Custom charts and graphs
- Data-driven art and animations
- SVG-based visualizations
- Interactive dashboards
- Complex data representations

## Key Features

- **Full d3.js Control** - Access to entire d3.js API
- **Interactive Visualizations** - Mouse events, zoom, pan
- **Custom Styling** - Complete control over appearance
- **Data Binding** - Powerful data-driven updates
- **Animation** - Smooth transitions and animations
- **Responsive** - Adapts to different screen sizes

## Installation

```bash
# Clone the repository
git clone https://github.com/chrisvoncsefalvay/claude-d3js-skill.git

# Copy skill to your skills directory
cp -r claude-d3js-skill ~/.claude/skills/claude-d3js-skill
```

## Usage Examples

### Basic Bar Chart

```javascript
import * as d3 from 'd3';

const data = [4, 8, 15, 16, 23, 42];
const svg = d3.select('body').append('svg');

svg.selectAll('rect')
  .data(data)
  .enter()
  .append('rect')
  .attr('x', (d, i) => i * 30)
  .attr('y', d => 100 - d)
  .attr('width', 25)
  .attr('height', d => d);
```

### Interactive Scatter Plot

```javascript
const circles = svg.selectAll('circle')
  .data(data)
  .enter()
  .append('circle')
  .attr('cx', d => xScale(d.x))
  .attr('cy', d => yScale(d.y))
  .on('mouseover', handleMouseOver)
  .on('mouseout', handleMouseOut);
```

## Resources

- **Original Repository**: https://github.com/chrisvoncsefalvay/claude-d3js-skill
- **d3.js Documentation**: https://d3js.org
- **Gallery**: https://observablehq.com/@d3/gallery

**Remember**: d3.js provides powerful, flexible data visualization capabilities for creating custom, interactive charts and graphs.
