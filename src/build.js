/**
 * build.js
 * Reads data/commands.json and writes index.html.
 * Pure Node.js — no dependencies.
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

const data = JSON.parse(readFileSync(join(ROOT, 'data', 'commands.json'), 'utf8'));
const version = JSON.parse(readFileSync(join(ROOT, 'data', 'version.json'), 'utf8'));

// ─── Helpers ──────────────────────────────────────────────────────────────────

function esc(str = '') {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function kbd(keys = []) {
  return keys.map(k => `<kbd>${esc(k)}</kbd>`).join(' <span class="key-sep">or</span> ');
}

function riskBadge(risk) {
  const map = { low: 'badge-green', medium: 'badge-yellow', high: 'badge-red' };
  return `<span class="badge ${map[risk] || 'badge-gray'}">${esc(risk)}</span>`;
}

// ─── Sections ─────────────────────────────────────────────────────────────────

function buildQuickStart() {
  const rows = data.quick_start.map(item => `
    <div class="qs-card">
      <div class="qs-cmd" onclick="copyCmd('${esc(item.command)}')" title="Click to copy">
        <code>${esc(item.command)}</code>
        <span class="copy-hint">copy</span>
      </div>
      <p class="qs-why">${esc(item.why)}</p>
    </div>`).join('');
  return `<div class="qs-grid">${rows}</div>`;
}

function buildCommandSection(section) {
  const rows = section.commands.map(cmd => {
    const aliases = cmd.aliases?.length
      ? `<div class="aliases">${cmd.aliases.map(a => `<code class="alias">${esc(a)}</code>`).join('')}</div>`
      : '';
    const usageHtml = cmd.usage
      ? `<code class="args">${esc(cmd.usage)}</code>`
      : `<span class="muted-dash">—</span>`;
    const exampleHtml = cmd.example
      ? `<code class="example-cmd">${esc(cmd.example)}</code>`
      : '';
    return `
    <tr data-search="${esc(cmd.command + ' ' + cmd.description + ' ' + (cmd.aliases || []).join(' '))}">
      <td>
        <div class="cmd-cell">
          <code class="cmd-pill" onclick="copyCmd('${esc(cmd.command)}')" title="Click to copy">${esc(cmd.command)}</code>
          ${aliases}
        </div>
      </td>
      <td>${esc(cmd.description)}</td>
      <td>${usageHtml}</td>
      <td>${exampleHtml}</td>
      <td class="notes-cell">${esc(cmd.notes || '')}</td>
    </tr>`;
  }).join('');

  return `
  <div class="table-wrap">
    <table>
      <thead><tr><th>Command</th><th>Description</th><th>Usage</th><th>Example</th><th>Notes</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </div>`;
}

function buildShortcuts() {
  const sc = data.keyboard_shortcuts;

  function table(rows) {
    return `
    <div class="table-wrap">
      <table>
        <thead><tr><th>Shortcut</th><th>Description</th></tr></thead>
        <tbody>${rows.map(r => `
          <tr data-search="${esc(r.keys.join(' ') + ' ' + r.description)}">
            <td class="kbd-cell">${kbd(r.keys)}</td>
            <td>${esc(r.description)}</td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>`;
  }

  return `
    <h3 class="sub-heading">General Controls</h3>${table(sc.general)}
    <h3 class="sub-heading">Text Editing</h3>${table(sc.text_editing)}
    <h3 class="sub-heading">Multiline Input</h3>${table(sc.multiline)}
    <h3 class="sub-heading">Vim Mode — Mode Switching</h3>${table(sc.vim_mode.mode_switching)}
    <h3 class="sub-heading">Vim Mode — Navigation</h3>${table(sc.vim_mode.navigation)}
    <h3 class="sub-heading">Vim Mode — Editing</h3>${table(sc.vim_mode.editing)}`;
}

function buildPermissionModes() {
  const rows = data.permission_modes.map(m => `
    <tr data-search="${esc(m.mode + ' ' + m.description)}">
      <td><code class="mode-pill mode-${esc(m.mode)}">${esc(m.mode)}</code></td>
      <td><kbd>${esc(m.shortcut)}</kbd></td>
      <td>${esc(m.description)}${m.requires ? `<div class="requires">Requires: ${esc(m.requires)}</div>` : ''}</td>
      <td>${riskBadge(m.risk)}</td>
    </tr>`).join('');

  return `
  <div class="table-wrap">
    <table>
      <thead><tr><th>Mode</th><th>Cycle Key</th><th>Behavior</th><th>Risk</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </div>`;
}

function buildInputPrefixes() {
  const rows = data.input_prefixes.map(p => `
    <tr data-search="${esc(p.prefix + ' ' + p.description)}">
      <td><code class="prefix-pill">${esc(p.prefix)}</code></td>
      <td>${esc(p.description)}</td>
    </tr>`).join('');
  return `
  <div class="table-wrap">
    <table>
      <thead><tr><th>Prefix</th><th>What it does</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </div>`;
}

function buildCliFlags() {
  const rows = data.cli_flags.map(f => `
    <tr data-search="${esc(f.flag + ' ' + f.description)}">
      <td><code class="flag-pill">${esc(f.flag)}</code></td>
      <td>${esc(f.description)}</td>
      <td><code class="example">${esc(f.example)}</code></td>
    </tr>`).join('');
  return `
  <div class="table-wrap">
    <table>
      <thead><tr><th>Flag</th><th>Description</th><th>Example</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </div>`;
}

function buildChangelog() {
  if (!data.changelog?.length) {
    return `<p class="muted">No updates recorded yet — the workflow will populate this automatically when a new Claude Code version is released.</p>`;
  }
  return data.changelog.slice(0, 10).map(entry => `
    <div class="changelog-entry">
      <div class="changelog-header">
        <span class="changelog-version">v${esc(entry.version)}</span>
        <span class="changelog-date">${esc(entry.date)}</span>
        <a class="changelog-link" href="${esc(entry.release_url)}" target="_blank" rel="noopener">Release notes ↗</a>
      </div>
      ${entry.parsed_changes?.length ? `
        <ul class="changelog-changes">
          ${entry.parsed_changes.map(c => `<li><span class="change-type change-${esc(c.type)}">${esc(c.type)}</span> ${esc(c.text)}</li>`).join('')}
        </ul>` : '<p class="muted">See release notes for full details.</p>'}
    </div>`).join('');
}

// ─── Sidebar nav ──────────────────────────────────────────────────────────────

function buildNav() {
  const staticLinks = [
    { id: 'quick-start', label: 'Quick Start', icon: '★' },
    ...data.sections.map(s => ({ id: s.id, label: s.title, icon: s.icon })),
    { id: 'shortcuts', label: 'Keyboard Shortcuts', icon: '⌨' },
    { id: 'permission-modes', label: 'Permission Modes', icon: '⊛' },
    { id: 'input-prefixes', label: 'Input Prefixes', icon: '❯' },
    { id: 'cli-flags', label: 'CLI Flags', icon: '⚑' },
    { id: 'changelog', label: 'Changelog', icon: '↻' },
  ];

  return staticLinks.map(l =>
    `<a class="nav-link" href="#${esc(l.id)}" onclick="closeDrawer()"><span class="nav-icon">${l.icon}</span>${esc(l.label)}</a>`
  ).join('');
}

// ─── Full page ────────────────────────────────────────────────────────────────

const sectionsHTML = data.sections.map(s => `
  <section id="${esc(s.id)}" class="content-section">
    <h2 class="section-heading" style="--accent:${esc(s.color)}">
      <span class="section-icon">${s.icon}</span>${esc(s.title)}
    </h2>
    ${buildCommandSection(s)}
  </section>`).join('');

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code Reference</title>
<style>
/* ── Reset & Variables ─────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0d1117;
  --bg2: #161b22;
  --bg3: #1f2937;
  --border: #30363d;
  --text: #e6edf3;
  --text2: #8b949e;
  --accent: #da8a67;
  --accent2: #79c0ff;
  --green: #3fb950;
  --yellow: #d29922;
  --red: #f85149;
  --purple: #bc8cff;
  --orange: #ffa657;
  --sidebar-w: 240px;
  --header-h: 56px;
  --radius: 6px;
  --font-mono: 'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
  --font-ui: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}

[data-theme="light"] {
  --bg: #ffffff;
  --bg2: #f6f8fa;
  --bg3: #eaeef2;
  --border: #d0d7de;
  --text: #1f2328;
  --text2: #57606a;
}

html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--text); font-family: var(--font-ui); font-size: 14px; line-height: 1.6; }

/* ── Header ────────────────────────────────────────────────────────────────── */
.header {
  position: fixed; top: 0; left: 0; right: 0; height: var(--header-h);
  background: var(--bg2); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px; padding: 0 16px; z-index: 100;
}
.header-logo { font-family: var(--font-mono); font-size: 18px; color: var(--accent); font-weight: 700; white-space: nowrap; }
.header-logo span { color: var(--accent2); }
.header-version { font-family: var(--font-mono); font-size: 11px; color: var(--text2); background: var(--bg3); padding: 2px 7px; border-radius: 10px; white-space: nowrap; }
.header-updated { font-size: 11px; color: var(--text2); white-space: nowrap; }

.search-wrap { flex: 1; max-width: 420px; margin-left: auto; }
.search-input {
  width: 100%; background: var(--bg3); border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text); font-family: var(--font-ui); font-size: 13px; padding: 6px 12px 6px 32px;
  outline: none; transition: border-color .15s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%238b949e' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.35-4.35'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: 10px center;
}
.search-input:focus { border-color: var(--accent2); }

.header-actions { display: flex; gap: 8px; align-items: center; }
.btn-icon {
  background: none; border: 1px solid var(--border); color: var(--text2); cursor: pointer;
  border-radius: var(--radius); padding: 5px 10px; font-size: 13px; transition: all .15s; white-space: nowrap;
}
.btn-icon:hover { border-color: var(--accent2); color: var(--accent2); }
.hamburger { display: none; }

/* ── Layout ────────────────────────────────────────────────────────────────── */
.layout { display: flex; padding-top: var(--header-h); min-height: 100vh; }

/* ── Sidebar ───────────────────────────────────────────────────────────────── */
.sidebar {
  position: fixed; top: var(--header-h); left: 0; bottom: 0;
  width: var(--sidebar-w); background: var(--bg2); border-right: 1px solid var(--border);
  overflow-y: auto; padding: 12px 0; z-index: 90;
  scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.nav-link {
  display: flex; align-items: center; gap: 8px; padding: 7px 16px;
  color: var(--text2); text-decoration: none; font-size: 13px; transition: all .1s;
  border-left: 2px solid transparent;
}
.nav-link:hover { color: var(--text); background: var(--bg3); }
.nav-link.active { color: var(--accent2); border-left-color: var(--accent2); background: var(--bg3); }
.nav-icon { font-size: 12px; width: 16px; text-align: center; flex-shrink: 0; }

/* ── Main ──────────────────────────────────────────────────────────────────── */
.main { margin-left: var(--sidebar-w); flex: 1; padding: 32px 40px 80px; max-width: 1100px; }

/* ── Section headings ──────────────────────────────────────────────────────── */
.content-section { margin-bottom: 56px; }
.section-heading {
  font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px;
  border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px;
  color: var(--text);
}
.section-heading::before { content: ''; display: block; width: 3px; height: 22px; background: var(--accent); border-radius: 2px; }
.section-icon { font-size: 16px; }
.sub-heading { font-size: 14px; font-weight: 600; color: var(--text2); margin: 24px 0 10px; letter-spacing: .05em; text-transform: uppercase; }

/* ── Tables ────────────────────────────────────────────────────────────────── */
.table-wrap { overflow-x: auto; border-radius: var(--radius); border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; }
thead { background: var(--bg3); }
th { padding: 10px 14px; text-align: left; font-size: 12px; font-weight: 600; color: var(--text2); letter-spacing: .05em; text-transform: uppercase; white-space: nowrap; }
td { padding: 10px 14px; border-top: 1px solid var(--border); vertical-align: top; }
tr:hover td { background: var(--bg3); }
tr.hidden { display: none; }
.notes-cell { font-size: 12px; color: var(--text2); }

/* ── Command pills ─────────────────────────────────────────────────────────── */
.cmd-cell { display: flex; flex-direction: column; gap: 4px; }
.cmd-pill {
  display: inline-block; background: var(--bg3); border: 1px solid var(--border);
  color: var(--accent); font-family: var(--font-mono); font-size: 13px; padding: 2px 8px;
  border-radius: var(--radius); cursor: pointer; transition: all .15s; white-space: nowrap;
  user-select: none;
}
.cmd-pill:hover { border-color: var(--accent); background: rgba(218,138,103,.1); }
.cmd-pill:hover + .copy-hint, .cmd-pill:focus + .copy-hint { opacity: 1; }
.copy-hint { font-size: 10px; color: var(--text2); opacity: 0; transition: opacity .15s; pointer-events: none; }
.aliases { display: flex; gap: 4px; flex-wrap: wrap; }
.alias { font-family: var(--font-mono); font-size: 11px; color: var(--text2); background: var(--bg); border: 1px solid var(--border); padding: 1px 6px; border-radius: var(--radius); }
.args { font-family: var(--font-mono); font-size: 12px; color: var(--accent2); white-space: nowrap; }
.example-cmd { font-family: var(--font-mono); font-size: 12px; color: var(--text2); white-space: nowrap; }
.muted-dash { color: var(--border); font-size: 13px; }
.flag-pill { font-family: var(--font-mono); font-size: 12px; color: var(--purple); white-space: nowrap; }
.prefix-pill { font-family: var(--font-mono); font-size: 18px; color: var(--orange); font-weight: 700; }
.example { font-family: var(--font-mono); font-size: 12px; color: var(--text2); white-space: nowrap; }
.mode-pill { font-family: var(--font-mono); font-size: 12px; padding: 2px 8px; border-radius: var(--radius); border: 1px solid; }
.mode-default { color: var(--text2); border-color: var(--border); }
.mode-acceptEdits { color: var(--yellow); border-color: var(--yellow); }
.mode-plan { color: var(--accent2); border-color: var(--accent2); }
.mode-auto { color: var(--green); border-color: var(--green); }
.mode-bypassPermissions { color: var(--red); border-color: var(--red); }
.requires { font-size: 11px; color: var(--text2); margin-top: 4px; }

/* ── Keyboard keys ─────────────────────────────────────────────────────────── */
kbd {
  display: inline-block; background: var(--bg3); border: 1px solid var(--border);
  border-bottom-width: 2px; border-radius: 4px; font-family: var(--font-mono);
  font-size: 11px; padding: 1px 6px; color: var(--text); white-space: nowrap;
}
.kbd-cell { white-space: nowrap; }
.key-sep { color: var(--text2); font-size: 11px; margin: 0 2px; }

/* ── Badges ────────────────────────────────────────────────────────────────── */
.badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 1px 7px; border-radius: 10px; text-transform: uppercase; letter-spacing: .04em; }
.badge-green { background: rgba(63,185,80,.15); color: var(--green); }
.badge-yellow { background: rgba(210,153,34,.15); color: var(--yellow); }
.badge-red { background: rgba(248,81,73,.15); color: var(--red); }
.badge-gray { background: var(--bg3); color: var(--text2); }

/* ── Quick Start ───────────────────────────────────────────────────────────── */
.qs-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.qs-card { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 16px; transition: border-color .15s; }
.qs-card:hover { border-color: var(--accent2); }
.qs-cmd { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer; }
.qs-cmd code { font-family: var(--font-mono); font-size: 14px; color: var(--accent); font-weight: 600; }
.qs-cmd .copy-hint { font-size: 10px; color: var(--text2); opacity: 0; transition: opacity .15s; }
.qs-card:hover .copy-hint { opacity: 1; }
.qs-why { font-size: 13px; color: var(--text2); line-height: 1.5; }

/* ── Hero ──────────────────────────────────────────────────────────────────── */
.hero { margin-bottom: 40px; padding: 28px 32px; background: linear-gradient(135deg, rgba(218,138,103,.08) 0%, rgba(121,192,255,.08) 100%); border: 1px solid var(--border); border-radius: 10px; }
.hero-title { font-size: 28px; font-weight: 700; margin-bottom: 6px; }
.hero-title span { color: var(--accent); font-family: var(--font-mono); }
.hero-sub { color: var(--text2); font-size: 14px; margin-bottom: 16px; }
.hero-meta { display: flex; gap: 16px; flex-wrap: wrap; }
.hero-chip { font-size: 12px; color: var(--text2); background: var(--bg3); border: 1px solid var(--border); border-radius: 10px; padding: 3px 10px; }
.hero-chip a { color: var(--accent2); text-decoration: none; }
.hero-chip a:hover { text-decoration: underline; }

/* ── Changelog ─────────────────────────────────────────────────────────────── */
.changelog-entry { padding: 16px; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 12px; background: var(--bg2); }
.changelog-header { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
.changelog-version { font-family: var(--font-mono); font-size: 14px; font-weight: 700; color: var(--accent); }
.changelog-date { font-size: 12px; color: var(--text2); }
.changelog-link { font-size: 12px; color: var(--accent2); text-decoration: none; margin-left: auto; }
.changelog-link:hover { text-decoration: underline; }
.changelog-changes { list-style: none; display: flex; flex-direction: column; gap: 6px; }
.changelog-changes li { font-size: 13px; color: var(--text2); display: flex; gap: 8px; align-items: flex-start; }
.change-type { display: inline-block; font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; text-transform: uppercase; letter-spacing: .04em; flex-shrink: 0; margin-top: 2px; }
.change-new { background: rgba(63,185,80,.15); color: var(--green); }
.change-updated { background: rgba(121,192,255,.15); color: var(--accent2); }
.change-fix { background: rgba(210,153,34,.15); color: var(--yellow); }
.change-removed { background: rgba(248,81,73,.15); color: var(--red); }
.muted { color: var(--text2); font-size: 13px; font-style: italic; }

/* ── Toast (copy feedback) ─────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(20px);
  background: var(--bg3); border: 1px solid var(--border); color: var(--text);
  padding: 8px 18px; border-radius: 20px; font-size: 13px; opacity: 0;
  transition: all .25s; pointer-events: none; z-index: 999;
}
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }

/* ── Back to top ───────────────────────────────────────────────────────────── */
.back-top {
  position: fixed; bottom: 28px; right: 28px; background: var(--bg3);
  border: 1px solid var(--border); color: var(--text2); cursor: pointer;
  border-radius: 50%; width: 38px; height: 38px; font-size: 16px;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: all .25s; pointer-events: none; z-index: 90;
}
.back-top.visible { opacity: 1; pointer-events: all; }
.back-top:hover { border-color: var(--accent2); color: var(--accent2); }

/* ── Overlay ───────────────────────────────────────────────────────────────── */
.overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 85; }
.overlay.open { display: block; }

/* ── Responsive ────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .sidebar { left: calc(-1 * var(--sidebar-w)); transition: left .25s; }
  .sidebar.open { left: 0; }
  .main { margin-left: 0; padding: 20px 16px 80px; }
  .hamburger { display: flex; }
  .header-updated { display: none; }
  .qs-grid { grid-template-columns: 1fr; }
  .hero { padding: 20px; }
  .hero-title { font-size: 22px; }
}
</style>
</head>
<body>

<!-- Header -->
<header class="header">
  <button class="btn-icon hamburger" onclick="toggleDrawer()" aria-label="Menu">☰</button>
  <div class="header-logo">claude<span>/</span>ref</div>
  <span class="header-version">v${esc(version.last_version)}</span>
  <span class="header-updated">Updated ${esc(version.last_updated)}</span>

  <div class="search-wrap">
    <input class="search-input" type="search" placeholder="Search commands, shortcuts…" id="search" oninput="handleSearch(this.value)" autocomplete="off" spellcheck="false">
  </div>

  <div class="header-actions">
    <button class="btn-icon" onclick="toggleTheme()" id="theme-btn" title="Toggle light/dark">◑</button>
    <a class="btn-icon" href="https://docs.anthropic.com/en/docs/claude-code/cli-reference" target="_blank" rel="noopener" title="Official docs">Docs ↗</a>
  </div>
</header>

<!-- Sidebar overlay (mobile) -->
<div class="overlay" id="overlay" onclick="closeDrawer()"></div>

<!-- Sidebar -->
<nav class="sidebar" id="sidebar">
  ${buildNav()}
</nav>

<!-- Main content -->
<main class="main">

  <!-- Hero -->
  <div class="hero">
    <h1 class="hero-title"><span>Claude Code</span> Reference Guide</h1>
    <p class="hero-sub">Every command, shortcut, and mode — always current. Click any command to copy it.</p>
    <div class="hero-meta">
      <span class="hero-chip">v${esc(version.last_version)}</span>
      <span class="hero-chip">Updated ${esc(version.last_updated)}</span>
      <span class="hero-chip"><a href="https://github.com/anthropics/claude-code/releases" target="_blank" rel="noopener">anthropics/claude-code releases ↗</a></span>
    </div>
  </div>

  <!-- Quick Start -->
  <section id="quick-start" class="content-section">
    <h2 class="section-heading" style="--accent:#da8a67">
      <span class="section-icon">★</span>Quick Start — Top 10 for New Agentic Engineers
    </h2>
    ${buildQuickStart()}
  </section>

  <!-- All command sections -->
  ${sectionsHTML}

  <!-- Keyboard Shortcuts -->
  <section id="shortcuts" class="content-section">
    <h2 class="section-heading" style="--accent:#79c0ff">
      <span class="section-icon">⌨</span>Keyboard Shortcuts
    </h2>
    ${buildShortcuts()}
  </section>

  <!-- Permission Modes -->
  <section id="permission-modes" class="content-section">
    <h2 class="section-heading" style="--accent:#bc8cff">
      <span class="section-icon">⊛</span>Permission Modes
    </h2>
    <p style="color:var(--text2);font-size:13px;margin-bottom:16px;">Cycle through modes with <kbd>Shift+Tab</kbd>. The mode you pick determines how much Claude does autonomously vs. how much requires your approval.</p>
    ${buildPermissionModes()}
  </section>

  <!-- Input Prefixes -->
  <section id="input-prefixes" class="content-section">
    <h2 class="section-heading" style="--accent:#ffa657">
      <span class="section-icon">❯</span>Special Input Prefixes
    </h2>
    ${buildInputPrefixes()}
  </section>

  <!-- CLI Flags -->
  <section id="cli-flags" class="content-section">
    <h2 class="section-heading" style="--accent:#3fb950">
      <span class="section-icon">⚑</span>CLI Flags
    </h2>
    <p style="color:var(--text2);font-size:13px;margin-bottom:16px;">Flags for the <code style="font-family:var(--font-mono);color:var(--accent)">claude</code> startup command. Combine freely.</p>
    ${buildCliFlags()}
  </section>

  <!-- Changelog -->
  <section id="changelog" class="content-section">
    <h2 class="section-heading" style="--accent:#f85149">
      <span class="section-icon">↻</span>Auto-Update Changelog
    </h2>
    ${buildChangelog()}
  </section>

</main>

<!-- Toast notification -->
<div class="toast" id="toast">Copied!</div>

<!-- Back to top -->
<button class="back-top" id="back-top" onclick="window.scrollTo({top:0,behavior:'smooth'})" title="Back to top">↑</button>

<script>
// ── Theme ────────────────────────────────────────────────────────────────────
const root = document.documentElement;
const savedTheme = localStorage.getItem('theme') || 'dark';
if (savedTheme === 'light') root.setAttribute('data-theme', 'light');

function toggleTheme() {
  const isLight = root.getAttribute('data-theme') === 'light';
  root.setAttribute('data-theme', isLight ? 'dark' : 'light');
  localStorage.setItem('theme', isLight ? 'dark' : 'light');
}

// ── Copy to clipboard ────────────────────────────────────────────────────────
function copyCmd(text) {
  navigator.clipboard.writeText(text).then(() => showToast('Copied: ' + text));
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1800);
}

// ── Search ───────────────────────────────────────────────────────────────────
function handleSearch(query) {
  const q = query.toLowerCase().trim();
  document.querySelectorAll('tr[data-search]').forEach(row => {
    const match = !q || row.dataset.search.toLowerCase().includes(q);
    row.classList.toggle('hidden', !match);
  });
  // Also filter quick-start cards
  document.querySelectorAll('.qs-card').forEach(card => {
    const text = card.textContent.toLowerCase();
    card.style.display = (!q || text.includes(q)) ? '' : 'none';
  });
}

// ── Sidebar active link ──────────────────────────────────────────────────────
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('.content-section');

const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      navLinks.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + e.target.id));
    }
  });
}, { rootMargin: '-20% 0px -70% 0px' });

sections.forEach(s => observer.observe(s));

// ── Mobile drawer ────────────────────────────────────────────────────────────
function toggleDrawer() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}
function closeDrawer() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
}

// ── Back to top ──────────────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('back-top').classList.toggle('visible', window.scrollY > 400);
});
</script>
</body>
</html>`;

writeFileSync(join(ROOT, 'index.html'), html, 'utf8');
console.log('Built index.html successfully.');
