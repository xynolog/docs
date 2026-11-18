# Styles

How to use `@xynolog/react-ui`'s styles in your own app: importing them, the
design tokens, and the classes the components are built from.

Your app's own styling is unconstrained. Take all the styles with
`@xynolog/react-ui/styles`, or only the tokens with
`@xynolog/react-ui/styles/variables.css`.

Dark mode is `data-theme="dark"` on a parent element. The semantic tokens
(`--xynolog-text-*`, `--xynolog-bg-*`, `--xynolog-border-*`) change with it;
the palette tokens (`--xynolog-color-*`) are one fixed hue in both themes.

How the styles are written, named and linted inside the package is in its
[STYLES.md](https://github.com/xynolog/sdk/blob/main/typescript/react-ui/docs/STYLES.md).

## Using the Styles in Your App

### Import Styles

Add this to your app's main CSS file:

```css
/* app/globals.css (Next.js) or src/index.css (Vite/CRA) */
@import '@xynolog/react-ui/styles';
```

### Requirements

Your build system must support:
- **PostCSS** with the **`postcss-import`** plugin
- This is standard in Next.js, Vite, and most modern React frameworks

### What Happens

1. Your build system resolves `@import '@xynolog/react-ui/styles'` to `node_modules/@xynolog/react-ui/src/styles/index.css`
2. PostCSS processes all nested `@import` statements (including component CSS)
3. All CSS is bundled into a single optimized file

The package exports **source CSS files**, not built CSS, so your framework's build system processes them. Vite does it with no configuration: the Xynolog Browser's own stylesheet starts with this import.

### Debugging

Because your bundler processes the source files, its CSS source maps lead to them: a rule in the browser's developer tools opens at its file under `node_modules/@xynolog/react-ui/src/styles/`. In Vite, `css: { devSourcemap: true }` turns them on for development.

```
src/styles/
├── index.css       # the entry point, which imports the rest
├── variables.css   # design tokens
├── base/           # reset and base utilities
├── core/           # buttons, forms, badges, indicators
├── motivations/    # one stylesheet per annotation motivation
├── panels/         # the panels
├── patterns/       # cards and what panels share
├── features/       # feature-specific styles
├── layout/         # layout
└── utilities/      # accessibility utilities
```

## CSS Variables

Design tokens are defined in `variables.css`:

### Color Palette

```css
--xynolog-color-primary-500: #0080ff;
--xynolog-color-gray-50: #f9fafb;
--xynolog-color-gray-900: #111827;
--xynolog-color-white: #ffffff;
--xynolog-color-black: #000000;
/* Full palettes for primary, gray, red, yellow, green, blue, etc. */
```

### Typography

```css
--xynolog-font-sans: /* system font stack */;
--xynolog-font-mono: /* monospace font stack */;
--xynolog-text-xs: 0.75rem;
--xynolog-text-sm: 0.875rem;
--xynolog-text-base: 1rem;
--xynolog-text-lg: 1.125rem;
/* ... and more */
```

### Spacing

```css
--xynolog-spacing-xs: 0.25rem;
--xynolog-spacing-sm: 0.5rem;
--xynolog-spacing-md: 1rem;
--xynolog-spacing-lg: 1.5rem;
/* ... and more */
```

### Panel Design Tokens

```css
/* Centralized panel styling for consistency */
--xynolog-panel-padding: 1rem;
--xynolog-panel-gap: 1rem;
--xynolog-panel-border-radius: var(--xynolog-radius-lg);
--xynolog-panel-title-size: var(--xynolog-text-lg);
--xynolog-panel-title-weight: var(--xynolog-font-semibold);
--xynolog-panel-header-margin-bottom: 0.75rem;
--xynolog-panel-section-gap: 1.5rem;
--xynolog-panel-field-gap: 0.5rem;
--xynolog-panel-icon-size: 1.125rem;
```

### Border Radius

```css
--xynolog-radius-sm: 0.125rem;
--xynolog-radius-md: 0.375rem;
--xynolog-radius-lg: 0.5rem;
--xynolog-radius-full: 9999px;
```

## Core UI Elements

The `core/` directory contains fundamental UI elements that are reused throughout the application:

### Buttons
Located in `core/buttons.css`, provides a comprehensive button system:

```jsx
<button className="xynolog-button xynolog-button--primary">
  Primary Button
</button>
```

Available modifiers:
- `xynolog-button--primary` - Primary action (cyan/blue gradient)
- `xynolog-button--secondary` - Secondary action
- `xynolog-button--tertiary` - Tertiary action
- `xynolog-button--danger` - Destructive action
- `xynolog-button--warning` - Amber; highlight actions
- `xynolog-button--large` - Full width, larger padding
- `xynolog-button--scale` - Grows on hover

`buttonStyles` (exported from `@xynolog/react-ui`) holds these combinations as ready-made class strings. The `Button` component styles itself through data attributes instead: `data-variant` (`primary`, `secondary`, `tertiary`, `danger`, `warning`, `ghost`) and `data-size` (`xs` through `xl`) on `.xynolog-button`.

### Toggle Switches
Located in `core/toggles.css`, for binary on/off controls:

```jsx
<label className="xynolog-toggle-label">
  <span className="xynolog-toggle-label__text">Line numbers</span>
  <button
    type="button"
    role="switch"
    aria-checked={isOn}
    className={`xynolog-toggle ${isOn ? 'xynolog-toggle--active' : ''}`}
  >
    <span className={`xynolog-toggle__slider ${isOn ? 'xynolog-toggle__slider--active' : ''}`} />
  </button>
</label>
```

### Progress Bars
Located in `core/progress.css`, for showing completion status:

```jsx
<div className="xynolog-progress">
  <div className="xynolog-progress__fill" style={{width: '60%'}}></div>
</div>
```

### Range Sliders
Located in `core/sliders.css`, for numeric range inputs:

```jsx
<input type="range" className="xynolog-slider" min="0" max="100" />
```

### Tags
Located in `core/tags.css`, for content categorization:

```jsx
<span className="xynolog-tag">Category</span>
<span className="xynolog-tag xynolog-tag--secondary">Secondary Tag</span>
```

## W3C Web Annotation Motivations

The `motivations/` directory contains styles for the five W3C Web Annotation standard motivations. Each file defines its `--xynolog-motivation-<type>-*` custom properties on `:root`, styles inline annotations through an `annotation-<type>` class, and styles that motivation's panel entries (`.xynolog-annotation-entry[data-type="<type>"]`). The class an annotation renders with comes from its entry in `ANNOTATORS` (`src/lib/annotation-registry.ts`).

### Linking (References)
Located in `motivation-reference.css`:
- Visual: Cyan to blue gradient background; dashed outline in dark mode
- Use: For annotations that link to other resources

```css
.annotation-reference {
  background: var(--xynolog-motivation-reference-bg);   /* cyan-200 → blue-200 */
  color: var(--xynolog-motivation-reference-text);
}
```

### Highlighting
Located in `motivation-highlight.css`:
- Visual: Yellow background; dashed outline in dark mode
- Use: For text highlighting and emphasis

```css
.annotation-highlight {
  background: var(--xynolog-motivation-highlight-bg);   /* yellow-200 */
  color: var(--xynolog-motivation-highlight-text);
}
```

### Assessing
Located in `motivation-assessment.css`:
- Visual: Red wavy underline
- Use: For quality assessments and evaluations

```css
.annotation-assessment {
  text-decoration: underline wavy;
  text-decoration-color: var(--xynolog-motivation-assessment-primary);   /* red-500 */
}
```

### Commenting
Located in `motivation-comment.css`:
- Visual: Dark (light theme) or light (dark theme) dashed outline
- Use: For discussion and commentary

```css
.annotation-comment {
  outline: 2px dashed var(--xynolog-motivation-comment-outline);   /* gray-900 */
  outline-offset: 1px;
}
```

### Tagging
Located in `motivation-tag.css`:
- Visual: Orange to amber gradient background; dashed outline in dark mode
- Use: For categorization and classification

```css
.annotation-tag {
  background: var(--xynolog-motivation-tag-bg);   /* orange-200 → amber-200 */
  color: var(--xynolog-motivation-tag-text);
}
```

## Patterns

### Cards
Located in `patterns/cards.css`:

```jsx
<div className="xynolog-card">
  <h3>Card Title</h3>
  <p>Content goes here</p>
</div>
```

### Forms
Located in `core/forms.css` and `core/inputs.css`:

```jsx
<div className="xynolog-form">
  <div className="xynolog-form__field">
    <label htmlFor="title" className="xynolog-form__label">Label</label>
    <input id="title" className="xynolog-input" />
    <p className="xynolog-form__help">Helper text</p>
  </div>
</div>
```

### Panels
Located in `patterns/panels-base.css`:

```jsx
<div className="xynolog-panel">
  <div className="xynolog-panel-header">
    <h2 className="xynolog-panel-header__title">Panel Title</h2>
  </div>
  <div className="xynolog-panel__content">
    Panel content
  </div>
</div>
```
