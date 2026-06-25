# Tokens Studio for Figma

## Token format

Generated **`tokens.json`** uses **W3C Design Tokens (DTCG)** shape: each leaf has `$type` and `$value`.

In **Tokens Studio for Figma**, open **Settings** and set the token format to **W3C DTCG** before importing, so the plugin parses this folder correctly.

## Files

| File | Role |
|------|------|
| `tokens.json` | Generated from `src/styles/tokens.css` via `npm run tokens:studio`. |
| `base.json` | Semantic aliases and reset/layout dimensions aligned with `src/styles/base.css`. |
| `$metadata.json` | Token set order: `tokens` (foundation) then `base` (aliases reference foundation). |

## Import

1. Run `npm run tokens:studio` after editing `src/styles/tokens.css`.
2. In the plugin, load or sync this directory (`frontend/tokens-studio/`).
3. Push tokens to **Figma Variables** when ready.

## Naming

JSON nesting matches Figma slash paths (e.g. `color.surface.page` ↔ Variable `color/surface/page`). See also `src/figma/variableCatalog.ts`.
