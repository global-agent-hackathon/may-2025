# Components Directory Structure

This directory contains all the React components used in the application. The components are organized as follows:

## Directory Structure

```
components/
├── layout/           # Layout components like headers, sidebars, etc.
│   ├── app-sidebar/  # App sidebar related components
│   └── header/       # Header related components
├── features/         # Feature-specific components
│   ├── workspace/    # Workspace related components
│   ├── forms/        # Form related components
│   └── user/         # User related components
├── common/           # Shared components used across features
├── magicui/          # Special UI effects and animations
├── ui/               # Core UI components (shadcn/ui)
└── providers/        # Context providers and wrappers
```

## Component Categories

### Layout Components
Components that define the overall structure and layout of the application.
- App Sidebar
- Dashboard Header
- etc.

### Feature Components
Components that are specific to a particular feature or domain.
- Workspace related
- Forms related
- User related

### Common Components
Shared components that are used across multiple features.
- Generic cards
- Common buttons
- Shared utilities

### Magic UI Components
Special UI effects and animations that enhance the user experience.
- Interactive hover effects
- Rainbow buttons
- Border beams

### UI Components
Core UI components from shadcn/ui library.
- Buttons
- Inputs
- Modals
- etc.

### Providers
Context providers and wrapper components.
- Theme Provider
- Other context providers

## Best Practices

1. Keep components focused and single-responsibility
2. Use consistent naming conventions
3. Group related components together
4. Maintain clear component boundaries
5. Document complex components
6. Keep UI components pure and reusable 