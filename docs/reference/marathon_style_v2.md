## UI Design System: "Marathon / Bungie Sci-Fi Terminal"

You are designing a desktop GUI application with a dark sci-fi aesthetic inspired by Bungie's Marathon (2025). Follow these rules strictly:

### Color Palette
- Background: #000000 (primary), #1C1C1C (secondary/panels)
- Foreground/Text: #FFFFFF (primary), #717171 (muted/decorative)
- Accent/Primary: #C8FF00 (acid green/yellow-green, used for highlights, active states, CTA buttons)
- Error: Red (#FF3333)
- No gradients. No shadows. Pure flat design with hard edges.

### Typography
- All text UPPERCASE throughout the interface
- Headings: Wide geometric sans-serif (like Shapiro/Microgramma/Eurostile Extended), bold weight, large size
- Body/Labels: Monospace font (like JetBrains Mono, IBM Plex Mono, or Space Mono), regular weight
- Data/Decorative: Small monospace text at 9-10px for coordinate-style decorations
- Letter-spacing: slightly expanded (+0.5px to +1px) on labels
- Line-height: tight (1.2-1.35)

### Layout Principles
- Grid-based: use strict column alignment (multiples of 10px or 60px modules)
- No border-radius anywhere — all corners are sharp 0px
- Panels separated by 1px lines or hard color boundaries
- Navigation bar: fixed top, 60px height, black background
- Sidebar panels: fixed width (e.g., 280px), used for metadata/secondary info
- Content areas: full-bleed imagery with overlaid text panels

### Components Style
- Buttons: rectangular, height 48-60px, min-width 200px, uppercase text, no border-radius
  - Primary: accent background (#C8FF00) + black text; hover → black bg + accent text + 1px accent border
  - Secondary: transparent bg + 1px white border + white text; hover → accent bg + black text
- Input fields: black background, 1px white/gray border bottom only, white text, monospace font
- Cards: black or #1C1C1C background, no rounded corners, 1px border or no border
- Scrollbars: thin (4px), accent color thumb, dark track, no rounded ends

### Decorative Elements
- Pixel-stepped corners (staircase/chamfer shapes) on key panels using clip-path or layered rectangles
- Small crosshair marks (+) at corners of important sections
- Dot-grid overlays (small circles in a grid pattern) on hover states or backgrounds
- Coordinate/data strings as decorative text in corners (e.g., "SYN-G X29047 // ALFA-2 // 09.875")
- Diagonal stripe patterns (45°) for section dividers or footer areas
- Custom bracket-arrow icons for external links: [↗]

### Animation Guidelines
- Entrance: fade-in + slight translateY (20px → 0) with 200-400ms ease-out
- Hover transitions: 200ms ease for color/background changes
- Stagger animations for list items (50ms delay between each)
- Optional: subtle blink/pulse on primary CTA button (accent color opacity oscillation)
- No bouncy/elastic easing — use linear or ease-out only

### Interaction Patterns
- High contrast focus indicators: 2px accent outline with 2px offset
- Hover states always provide clear visual feedback (color inversion preferred)
- Active/selected states: accent color fill or accent left-border indicator
- Disabled states: 30% opacity, no interaction cursor

### Tone & Atmosphere
- Military-technical aesthetic: think spaceship terminal, mission briefing screen
- Information-dense but hierarchically clear
- Cold, precise, functional — no playful or organic shapes
- Text content should feel like classified documents or system readouts
