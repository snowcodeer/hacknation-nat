# AeroCraft Technical Blueprint Design System

## Design Philosophy

AeroCraft's interface is inspired by **precision aerospace engineering**, **technical CAD software**, and **blueprint aesthetics**. The design creates a professional, information-dense environment that feels like mission-critical aerospace tooling while maintaining excellent usability.

## Visual Identity

### Core Aesthetic Principles

1. **Technical Precision**: Every element conveys engineering accuracy with measured spacing, technical typography, and precise alignments
2. **Blueprint Inspiration**: Cyan/blue technical lines, grid backgrounds, and schematic-style visualizations
3. **Information Density**: Maximum data visibility without overwhelming clutter - professional engineers need details
4. **Modular Hierarchy**: Clear component relationships with visual assembly tree structures
5. **Status-Driven Color**: Functional color system tied to component states (ready, configuring, error)

### Color Palette

#### Blueprint Foundation
- `--blueprint-bg: #0a1628` - Primary dark background (deep aerospace blue)
- `--blueprint-bg-secondary: #0f1f36` - Secondary surfaces
- `--blueprint-surface: #152841` - Elevated panels
- `--blueprint-surface-elevated: #1a324d` - Highest elevation

#### Technical Cyan (Primary Accent)
- `--cyan-400: #29b6f6` - Interactive elements
- `--cyan-500: #03a9f4` - Primary accent color
- `--cyan-600: #039be5` - Hover states
- `--cyan-700: #0288d1` - Pressed states
- `--cyan-glow: rgba(3, 169, 244, 0.4)` - Glow effects

#### Status Colors
- **Success/Complete**: `--green-success: #66bb6a` with green glow
- **Warning/Processing**: `--amber-warning: #ffa726` with amber glow
- **Error/Alert**: `--red-error: #ef5350` with red glow

#### Technical Grays
- `--gray-100: #f5f7fa` - Primary text
- `--gray-200: #e4e9f0` - Secondary text
- `--gray-300: #b8c5d6` - Tertiary text
- `--gray-400: #8899ac` - Labels/metadata
- `--gray-500: #5a6c7d` - Muted text
- `--gray-600: #3d4f5d` - Disabled states

#### Grid & Lines
- `--grid-line: rgba(3, 169, 244, 0.08)` - Subtle background grid
- `--grid-line-major: rgba(3, 169, 244, 0.15)` - Major grid lines (100px intervals)
- `--border-technical: rgba(3, 169, 244, 0.3)` - Prominent technical borders
- `--border-subtle: rgba(255, 255, 255, 0.1)` - Subtle dividers

### Typography

#### Font Families
- **Display/UI**: `--font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Technical/Data**: `--font-technical: 'Roboto Mono', 'Consolas', 'Monaco', monospace`

#### Type Scale & Usage

**Technical Labels** (0.625rem / 10px)
- All-caps, 0.1-0.15em letter-spacing
- Used for: Component codes (WNG-01), section headers, metadata
- Color: cyan-400 or gray-400

**Parameter Labels** (0.625-0.75rem / 10-12px)
- All-caps, tight letter-spacing
- Used for: Control labels, status indicators
- Color: gray-300

**Body Text** (0.8125rem / 13px)
- Used for: Message content, descriptions, tooltips
- Color: gray-200

**Values/Data** (0.875-1.25rem / 14-20px)
- Monospace technical font
- Used for: Parameter values, measurements, coordinates
- Color: cyan-400

**Titles** (1.25rem+ / 20px+)
- All-caps, wide letter-spacing
- Used for: Panel headers, component names
- Color: gray-100

### Spacing System

8px base grid system:
- `--space-1: 0.25rem` (4px) - Minimal gaps
- `--space-2: 0.5rem` (8px) - Tight spacing
- `--space-3: 0.75rem` (12px) - Small gaps
- `--space-4: 1rem` (16px) - Default spacing
- `--space-5: 1.5rem` (24px) - Section gaps
- `--space-6: 2rem` (32px) - Major separations
- `--space-8: 3rem` (48px) - Large divisions

### Visual Effects

#### Glows & Shadows
- **Cyan Glow**: `0 0 20px rgba(3, 169, 244, 0.4)` - Active/hover states
- **Amber Glow**: `0 0 20px rgba(255, 167, 38, 0.3)` - Processing states
- **Green Glow**: `0 0 20px rgba(102, 187, 106, 0.3)` - Complete states
- **Elevated Shadow**: `0 4px 12px rgba(0, 0, 0, 0.4)` - Panel depth
- **Deep Shadow**: `0 8px 24px rgba(0, 0, 0, 0.5)` - Maximum elevation

## Component Patterns

### Header System

**Main Application Header**
- Three-column grid layout (branding | status | controls)
- Geometric aircraft icon in cyan
- Assembly progress bar with technical markers
- Component code labels (e.g., "CAD SYSTEM v2.1")

### Panel Architecture

**Standard Panel Structure**:
```
┌─────────────────────────────────┐
│ Header (component code + status)│
│ ▸ Component Title (all-caps)    │
│ ─── Divider (cyan gradient) ───  │
│ Subtitle/Description             │
├─────────────────────────────────┤
│                                  │
│ Panel Content                    │
│                                  │
└─────────────────────────────────┘
```

**Panel Types**:
1. **Editor Panel** (left) - Parameter controls and configuration
2. **Copilot Panel** (right) - AI chat interface
3. **Viewport** (center) - 3D preview with corner brackets

### Status Indicators

**Pulsing Dot Pattern**:
- 8px circle with border
- Subtle pulse animation (1s cycle, 0.6-1.0 opacity)
- Color matches status: gray (config), green (ready), amber (processing)
- Paired with uppercase status text

**Progress Visualization**:
- Linear bar with gradient fill
- Technical markers at 25% intervals
- Smooth width transitions (0.4s ease)
- Cyan glow on active bar

### Parameter Controls

**Technical Slider Design**:
```
PARAMETER LABEL          12.50 m
├──────────●──────────────────┤
5.0       10.0              15.0
```

Features:
- Label + real-time value display with unit
- Square cyan thumb (16px) with glow
- Dark track with subtle border
- Min/mid/max markers in monospace
- Hover enlarges thumb (1.1x scale)

**Select Dropdowns**:
- Dark background with subtle border
- All-caps options
- Cyan focus glow
- Hover highlights border

**Checkboxes**:
- 18px squares with cyan accent color
- Full-width clickable row
- Icon + label layout
- Hover highlights entire control

### Assembly Tree

**Node Structure**:
```
MODULE STATUS
├─ [WNG-01] Wings
│  └─ ✓ CONFIGURED
├─ [FSL-02] Fuselage
│  └─ PENDING
```

- Vertical connector lines (2px)
- Green connectors for complete modules
- Horizontal branch at 50% height
- Technical code + label layout
- Status with checkmark icon

### Chat Interface

**Message Pattern**:
```
┌──────────────────────────────┐
│ 👤 USER           14:23:15   │
│ Message content here...      │
└──────────────────────────────┘
```

- Left accent bar (3px) colored by sender
- Icon + sender label + timestamp header
- User: cyan accent, AI: green accent
- Processing messages: amber with pulsing dots animation

### Module Selector Tabs

**Bottom Navigation**:
- Equal-width grid (4 columns)
- Component code + status icon header
- All-caps label
- 3px indicator bar at bottom
- Active tab: dark background + cyan gradient indicator with glow

**Status Icons**:
- Complete: Checkmark in circle (green)
- Generating: Spinning circle (cyan/amber)
- Pending: Dashed circle (gray)

### Viewport Features

**Corner Brackets**:
- 40px L-shaped corners at viewport edges
- 2px cyan borders
- 60% opacity
- CAD/technical schematic aesthetic

**Coordinate Display**:
```
X: 0.00  Y: 0.00  Z: 0.00
```
- Monospace values
- Cyan color
- Uppercase axis labels

## Interaction Patterns

### Hover States
- Border color shifts to lighter cyan
- Subtle glow appears (cyan/amber/green depending on context)
- Transform: translateY(-1-2px) for buttons
- Transform: translateX(2-4px) for list items
- Transition: 0.2s for most properties

### Focus States
- 2px cyan outline with 2px offset
- Stronger glow effect
- Never remove outlines (accessibility)

### Loading/Processing
- Spinning circle animation (0.8s linear infinite)
- Amber color scheme
- Border with transparent top
- Paired with pulsing message/panel

### Active States
- Cyan background gradient
- White text color
- Cyan glow shadow
- Enhanced border

## Animations

### Subtle Pulse (Status Dots)
```css
@keyframes pulse-subtle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
```
Duration: 2s, Timing: ease-in-out

### Bright Pulse (Indicators)
```css
@keyframes pulse-bright {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.85); }
}
```
Duration: 2s, Timing: ease-in-out

### Spin (Loading)
```css
@keyframes spin {
  to { transform: rotate(360deg); }
}
```
Duration: 0.8s, Timing: linear infinite

### Bounce (Processing Dots)
```css
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
```
Duration: 1.4s, Timing: ease-in-out, Staggered delays

## Accessibility

### Color Contrast
- All text meets WCAG AA minimum (4.5:1 for normal text, 3:1 for large text)
- Cyan on dark background: ~7:1 ratio
- White on dark background: ~15:1 ratio
- Status colors distinguishable without color (icons + text)

### Keyboard Navigation
- All controls keyboard accessible
- Focus states clearly visible (cyan outline + glow)
- Logical tab order
- No keyboard traps

### Screen Readers
- Semantic HTML structure
- Descriptive labels
- Status announcements via ARIA live regions (implicit in Svelte)
- Icon-only buttons have accessible labels

### Motion
- Animations respect `prefers-reduced-motion` (should be added in production)
- No rapid flashing (all animations > 3 flashes/second threshold)
- Animations enhance but don't block functionality

## Responsive Considerations

### Current Layout
- Fixed 3-column grid: 340px | 1fr | 380px
- Minimum supported width: ~1280px
- Panels are scrollable independently

### Future Responsive Strategy
- Tablet (768-1024px): Stack panels vertically, collapse chat to modal
- Mobile: Single-panel view with tab navigation
- Maintain 8px grid system across all breakpoints

## Technical Implementation Notes

### Grid Background
- CSS multi-layer linear gradients
- 20px minor grid, 100px major grid
- Fixed positioning, pointer-events: none
- 50% opacity on body::before pseudo-element

### Glows
- Box-shadow with spread radius
- RGBA with 0.3-0.4 alpha
- Multiple shadows for enhanced effect when needed
- Hardware-accelerated (transform, opacity only for animations)

### Performance
- Minimal reflows (avoid layout-triggering properties)
- GPU-accelerated animations (transform, opacity)
- Debounced parameter updates (onChange vs onInput)
- Virtualization recommended for long lists (future)

## Brand Voice

**Technical but Approachable**
- All-caps for labels and codes (engineering precision)
- Monospace for data values (technical readability)
- Clear hierarchy through size, weight, color
- Confident, professional tone

**Component Naming Convention**
- Format: `[TYPE]-[NUMBER]` (e.g., WNG-01, FSL-02)
- Types: WNG (wings), FSL (fuselage), TAL (tail), ENG (engines), ASM (assembly)
- Numbers: Zero-padded two digits

## File Structure

```
frontend/src/
├── app.css                          # Design system foundation
├── routes/
│   └── +page.svelte                 # Main application layout
└── lib/components/
    ├── chat/
    │   └── AircraftChat.svelte      # AI co-pilot interface
    └── editor/
        └── ComponentEditor.svelte   # Parameter controls
```

## Future Enhancements

### Planned Features
1. **Measurement Overlays**: Real-time dimension annotations on 3D viewport
2. **Assembly Animation**: Compile sequence with component fly-in effects
3. **Technical Annotations**: Blueprint-style callout lines and notes
4. **Dark/Light Mode**: Inverse color scheme (white background, dark text)
5. **Preset Configurations**: Quick-load common aircraft types
6. **Export Previews**: Technical drawing generation from 3D model

### Design Expansions
1. **Notification System**: Toast messages with technical styling
2. **Modal Dialogs**: Full-screen overlays for complex workflows
3. **Data Visualization**: Charts/graphs for performance metrics
4. **Comparison View**: Side-by-side aircraft configurations
5. **History Timeline**: Version control UI with diff visualization

---

**Design Version**: 2.1
**Last Updated**: 2025-11-09
**Designer**: Claude (Anthropic)
**Implementation**: SvelteKit + CSS Variables
