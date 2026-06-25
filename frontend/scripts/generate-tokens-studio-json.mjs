/**
 * Generates tokens-studio/tokens.json (W3C DTCG-style tokens) from src/styles/tokens.css.
 *
 * Tokens Studio: set the plugin to **W3C DTCG** token format to match this output.
 * Paths match figmaPath in src/figma/variableCatalog.ts (slash → nested JSON keys).
 *
 * Usage: node scripts/generate-tokens-studio-json.mjs
 */

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.join(__dirname, '..')
const TOKENS_CSS = path.join(ROOT, 'src/styles/tokens.css')
const OUT_JSON = path.join(ROOT, 'tokens-studio/tokens.json')

/** figmaPath, cssVar, and W3C $type for the leaf token */
const CATALOG = [
  { figmaPath: 'color/surface/page', cssVar: '--color-surface-page', type: 'color' },
  { figmaPath: 'color/surface/auth', cssVar: '--color-surface-auth', type: 'color' },
  { figmaPath: 'color/surface/form', cssVar: '--color-surface-form', type: 'color' },
  { figmaPath: 'color/border/default', cssVar: '--color-border-default', type: 'color' },
  { figmaPath: 'color/border/subtle', cssVar: '--color-border-subtle', type: 'color' },
  { figmaPath: 'color/text/primary', cssVar: '--color-text-primary', type: 'color' },
  { figmaPath: 'color/text/secondary', cssVar: '--color-text-secondary', type: 'color' },
  { figmaPath: 'color/text/muted', cssVar: '--color-text-muted', type: 'color' },
  { figmaPath: 'color/accent', cssVar: '--color-accent', type: 'color' },
  { figmaPath: 'elevation/shadow/card', cssVar: '--shadow-card', type: 'shadow' },
  { figmaPath: 'radius/lg', cssVar: '--radius-lg', type: 'dimension' },
  { figmaPath: 'radius/md', cssVar: '--radius-md', type: 'dimension' },
  { figmaPath: 'space/1', cssVar: '--space-1', type: 'dimension' },
  { figmaPath: 'space/2', cssVar: '--space-2', type: 'dimension' },
  { figmaPath: 'space/3', cssVar: '--space-3', type: 'dimension' },
  { figmaPath: 'space/4', cssVar: '--space-4', type: 'dimension' },
  { figmaPath: 'space/5', cssVar: '--space-5', type: 'dimension' },
  { figmaPath: 'space/header', cssVar: '--space-header', type: 'dimension' },
  { figmaPath: 'font-size/brand-icon', cssVar: '--font-size-brand-icon', type: 'dimension' },
  { figmaPath: 'font-size/title-page', cssVar: '--font-size-title-page', type: 'dimension' },
  { figmaPath: 'font-size/section', cssVar: '--font-size-section', type: 'dimension' },
  { figmaPath: 'font-size/accent', cssVar: '--font-size-accent', type: 'dimension' },
  { figmaPath: 'font-weight/title', cssVar: '--font-weight-title', type: 'number' },
  { figmaPath: 'font-weight/semibold', cssVar: '--font-weight-semibold', type: 'number' },
  { figmaPath: 'letter-spacing/tight-title', cssVar: '--letter-spacing-tight-title', type: 'dimension' },
  { figmaPath: 'line-height/body', cssVar: '--line-height-body', type: 'number' },
  { figmaPath: 'layout/viewport-height', cssVar: '--layout-viewport-height', type: 'dimension' },
  { figmaPath: 'layout/login-card-width', cssVar: '--layout-login-card-width', type: 'dimension' },
  { figmaPath: 'layout/login-logo-max', cssVar: '--layout-login-logo-max', type: 'dimension' },
  { figmaPath: 'border-width/card', cssVar: '--border-width-card', type: 'dimension' },
  { figmaPath: 'section/accent-bar-width', cssVar: '--section-accent-bar-width', type: 'dimension' },
  { figmaPath: 'el/color/primary', cssVar: '--el-color-primary', type: 'color' },
  { figmaPath: 'el/color/primary-light-3', cssVar: '--el-color-primary-light-3', type: 'color' },
  { figmaPath: 'el/color/primary-light-5', cssVar: '--el-color-primary-light-5', type: 'color' },
  { figmaPath: 'el/color/primary-light-7', cssVar: '--el-color-primary-light-7', type: 'color' },
  { figmaPath: 'el/color/primary-light-8', cssVar: '--el-color-primary-light-8', type: 'color' },
  { figmaPath: 'el/color/primary-light-9', cssVar: '--el-color-primary-light-9', type: 'color' },
  { figmaPath: 'el/color/primary-dark-2', cssVar: '--el-color-primary-dark-2', type: 'color' }
]

function parseCssCustomProps(css) {
  const map = Object.create(null)
  const re = /--([\w-]+)\s*:\s*([^;]+);/g
  let m
  while ((m = re.exec(css))) {
    map[`--${m[1]}`] = m[2].trim()
  }
  return map
}

/** Parse `0 4px 12px rgba(0, 0, 0, 0.05)` (no spread) into DTCG shadow object */
function cssBoxShadowToDtcg(value) {
  const s = value.trim()
  const rgbaMatch = s.match(/\s+(rgba?\([^)]+\))\s*$/i)
  if (!rgbaMatch) {
    return {
      offsetX: '0px',
      offsetY: '4px',
      blur: '12px',
      spread: '0px',
      color: 'rgba(0, 0, 0, 0.05)'
    }
  }
  const color = rgbaMatch[1]
  const before = s.slice(0, s.length - color.length).trim()
  const parts = before.split(/\s+/)
  if (parts.length >= 3) {
    const ox = parts[0].endsWith('px') ? parts[0] : `${parts[0]}px`
    return {
      offsetX: ox,
      offsetY: parts[1],
      blur: parts[2],
      spread: parts[3] && parts[3] !== color ? parts[3] : '0px',
      color
    }
  }
  return {
    offsetX: '0px',
    offsetY: '4px',
    blur: '12px',
    spread: '0px',
    color
  }
}

function leafToken(type, rawValue) {
  if (type === 'color') {
    return { $type: 'color', $value: rawValue }
  }
  if (type === 'dimension') {
    return { $type: 'dimension', $value: rawValue }
  }
  if (type === 'number') {
    const n = Number(rawValue)
    if (Number.isNaN(n)) throw new Error(`Not a number: ${rawValue}`)
    return { $type: 'number', $value: n }
  }
  if (type === 'shadow') {
    return {
      $type: 'shadow',
      $value: cssBoxShadowToDtcg(rawValue)
    }
  }
  throw new Error(`Unknown type: ${type}`)
}

function setNested(root, segments, leaf) {
  let cur = root
  for (let i = 0; i < segments.length - 1; i++) {
    const k = segments[i]
    if (cur[k] !== undefined && typeof cur[k] !== 'object') {
      throw new Error(`Path conflict at ${segments.slice(0, i + 1).join('.')}`)
    }
    if (!cur[k]) cur[k] = {}
    cur = cur[k]
  }
  const last = segments[segments.length - 1]
  if (cur[last] !== undefined) throw new Error(`Duplicate leaf: ${segments.join('.')}`)
  cur[last] = leaf
}

function main() {
  const css = fs.readFileSync(TOKENS_CSS, 'utf8')
  const vars = parseCssCustomProps(css)
  const tree = {}

  for (const row of CATALOG) {
    const raw = vars[row.cssVar]
    if (raw === undefined) {
      throw new Error(`Missing ${row.cssVar} in ${path.relative(ROOT, TOKENS_CSS)}`)
    }
    const segments = row.figmaPath.split('/')
    setNested(tree, segments, leafToken(row.type, raw))
  }

  fs.mkdirSync(path.dirname(OUT_JSON), { recursive: true })
  fs.writeFileSync(OUT_JSON, JSON.stringify(tree, null, 2) + '\n', 'utf8')
  console.log(`Wrote ${path.relative(ROOT, OUT_JSON)} (${CATALOG.length} tokens)`)
}

main()
