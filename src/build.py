#!/usr/bin/env python3
"""
build.py — Python equivalent of build.js for local use when Node isn't installed.
Usage: python3 src/build.py
Reads data/commands.json + data/version.json → writes index.html
"""

import json
import html as htmllib
from pathlib import Path

ROOT = Path(__file__).parent.parent
data = json.loads((ROOT / "data" / "commands.json").read_text())
version = json.loads((ROOT / "data" / "version.json").read_text())
user_md = (ROOT / "data" / "user.md").read_text()
custom_agents = json.loads((ROOT / "data" / "custom-agents.json").read_text())

def esc(s):
    return htmllib.escape(str(s or ""), quote=True)

def kbd(keys):
    parts = [f"<kbd>{esc(k)}</kbd>" for k in keys]
    return ' <span class="key-sep">or</span> '.join(parts)

def risk_badge(risk):
    cls = {"low": "badge-green", "medium": "badge-yellow", "high": "badge-red"}.get(risk, "badge-gray")
    return f'<span class="badge {cls}">{esc(risk)}</span>'

# ── Quick Start ───────────────────────────────────────────────────────────────

def build_quick_start():
    cards = ""
    for item in data["quick_start"]:
        cmd = esc(item["command"])
        why = esc(item["why"])
        cards += f'''
    <div class="qs-card">
      <div class="qs-cmd" onclick="copyCmd('{cmd}')" title="Click to copy">
        <code>{cmd}</code>
        <span class="copy-hint">copy</span>
      </div>
      <p class="qs-why">{why}</p>
    </div>'''
    return f'<div class="qs-grid">{cards}</div>'

# ── Command sections ──────────────────────────────────────────────────────────

def build_command_section(section):
    rows = ""
    for cmd in section["commands"]:
        aliases = cmd.get("aliases", [])
        alias_html = ""
        if aliases:
            alias_html = '<div class="aliases">' + "".join(
                f'<code class="alias">{esc(a)}</code>' for a in aliases
            ) + "</div>"
        search = esc(cmd["command"] + " " + cmd["description"] + " " + " ".join(aliases))
        c = esc(cmd["command"])
        usage = cmd.get("usage") or ""
        usage_html = f'<code class="args">{esc(usage)}</code>' if usage else '<span class="muted-dash">—</span>'
        example = cmd.get("example") or ""
        example_html = f'<code class="example-cmd">{esc(example)}</code>' if example else ""
        rows += f'''
    <tr data-search="{search}">
      <td>
        <div class="cmd-cell">
          <code class="cmd-pill" onclick="copyCmd('{c}')" title="Click to copy">{c}</code>
          {alias_html}
        </div>
      </td>
      <td>{esc(cmd["description"])}</td>
      <td>{usage_html}</td>
      <td>{example_html}</td>
      <td class="notes-cell">{esc(cmd.get("notes") or "")}</td>
    </tr>'''
    return f'''
  <div class="table-wrap">
    <table>
      <thead><tr><th>Command</th><th>Description</th><th>Usage</th><th>Example</th><th>Notes</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>'''

# ── Shortcuts ─────────────────────────────────────────────────────────────────

def shortcut_table(rows_data):
    rows = ""
    for r in rows_data:
        search = esc(" ".join(r["keys"]) + " " + r["description"])
        rows += f'''
          <tr data-search="{search}">
            <td class="kbd-cell">{kbd(r["keys"])}</td>
            <td>{esc(r["description"])}</td>
          </tr>'''
    return f'''
    <div class="table-wrap">
      <table>
        <thead><tr><th>Shortcut</th><th>Description</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>'''

def build_shortcuts():
    sc = data["keyboard_shortcuts"]
    return f"""
    <h3 class="sub-heading">General Controls</h3>{shortcut_table(sc["general"])}
    <h3 class="sub-heading">Text Editing</h3>{shortcut_table(sc["text_editing"])}
    <h3 class="sub-heading">Multiline Input</h3>{shortcut_table(sc["multiline"])}
    <h3 class="sub-heading">Vim Mode — Mode Switching</h3>{shortcut_table(sc["vim_mode"]["mode_switching"])}
    <h3 class="sub-heading">Vim Mode — Navigation</h3>{shortcut_table(sc["vim_mode"]["navigation"])}
    <h3 class="sub-heading">Vim Mode — Editing</h3>{shortcut_table(sc["vim_mode"]["editing"])}"""

# ── Permission modes ──────────────────────────────────────────────────────────

def build_permission_modes():
    rows = ""
    for m in data["permission_modes"]:
        req = f'<div class="requires">Requires: {esc(m["requires"])}</div>' if m.get("requires") else ""
        search = esc(m["mode"] + " " + m["description"])
        rows += f'''
    <tr data-search="{search}">
      <td><code class="mode-pill mode-{esc(m["mode"])}">{esc(m["mode"])}</code></td>
      <td><kbd>{esc(m["shortcut"])}</kbd></td>
      <td>{esc(m["description"])}{req}</td>
      <td>{risk_badge(m["risk"])}</td>
    </tr>'''
    return f'''
  <div class="table-wrap">
    <table>
      <thead><tr><th>Mode</th><th>Cycle Key</th><th>Behavior</th><th>Risk</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>'''

# ── Input prefixes ────────────────────────────────────────────────────────────

def build_input_prefixes():
    rows = ""
    for p in data["input_prefixes"]:
        search = esc(p["prefix"] + " " + p["description"])
        rows += f'''
    <tr data-search="{search}">
      <td><code class="prefix-pill">{esc(p["prefix"])}</code></td>
      <td>{esc(p["description"])}</td>
    </tr>'''
    return f'''
  <div class="table-wrap">
    <table>
      <thead><tr><th>Prefix</th><th>What it does</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>'''

# ── CLI flags ─────────────────────────────────────────────────────────────────

def build_cli_flags():
    rows = ""
    for f in data["cli_flags"]:
        search = esc(f["flag"] + " " + f["description"])
        rows += f'''
    <tr data-search="{search}">
      <td><code class="flag-pill">{esc(f["flag"])}</code></td>
      <td>{esc(f["description"])}</td>
      <td><code class="example">{esc(f["example"])}</code></td>
    </tr>'''
    return f'''
  <div class="table-wrap">
    <table>
      <thead><tr><th>Flag</th><th>Description</th><th>Example</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>'''

# ── Changelog ─────────────────────────────────────────────────────────────────

def build_changelog():
    if not data.get("changelog"):
        return '<p class="muted">No updates recorded yet — the GitHub Actions workflow will populate this automatically when a new Claude Code version is released.</p>'
    out = ""
    for entry in data["changelog"][:10]:
        changes_html = ""
        if entry.get("parsed_changes"):
            items = "".join(
                f'<li><span class="change-type change-{esc(c["type"])}">{esc(c["type"])}</span> {esc(c["text"])}</li>'
                for c in entry["parsed_changes"]
            )
            changes_html = f'<ul class="changelog-changes">{items}</ul>'
        else:
            changes_html = '<p class="muted">See release notes for full details.</p>'
        out += f'''
    <div class="changelog-entry">
      <div class="changelog-header">
        <span class="changelog-version">v{esc(entry["version"])}</span>
        <span class="changelog-date">{esc(entry["date"])}</span>
        <a class="changelog-link" href="{esc(entry["release_url"])}" target="_blank" rel="noopener">Release notes ↗</a>
      </div>
      {changes_html}
    </div>'''
    return out

# ── User profile ──────────────────────────────────────────────────────────────

def simple_md_to_html(md):
    """Minimal markdown → HTML for user.md (headings, bold, lists, paragraphs)."""
    lines = md.strip().split('\n')
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# '):
            out.append(f'<h3 class="profile-h1">{esc(stripped[2:])}</h3>')
        elif stripped.startswith('## '):
            out.append(f'<h4 class="profile-h2">{esc(stripped[3:])}</h4>')
        elif stripped.startswith('- '):
            text = stripped[2:]
            # Handle **bold**
            import re
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            out.append(f'<li>{text}</li>')
        elif stripped == '':
            out.append('<br>')
        else:
            import re
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            out.append(f'<p>{text}</p>')
    return '\n'.join(out)

def build_user_profile():
    rendered = simple_md_to_html(user_md)
    # Escape the raw markdown for embedding in a JS variable
    escaped_md = user_md.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
    return f'''
    <div class="profile-card" id="profile-card">
      <div class="profile-header">
        <span class="profile-icon">&#9671;</span>
        <span class="profile-title">User Profile</span>
        <div class="profile-actions">
          <button class="btn-sm" onclick="toggleEditProfile()" id="profile-edit-btn">Edit</button>
          <button class="btn-sm btn-export" onclick="exportProfile()" title="Copy markdown to clipboard">Export</button>
        </div>
      </div>
      <div class="profile-view" id="profile-view">{rendered}</div>
      <textarea class="profile-editor" id="profile-editor" style="display:none" spellcheck="false">{esc(user_md)}</textarea>
    </div>
    <script>const DEFAULT_PROFILE = `{escaped_md}`;</script>'''

# ── Built-in agents ───────────────────────────────────────────────────────────

def build_builtin_agents():
    agents = data.get("agents", {}).get("built_in", [])
    rows = ""
    for a in agents:
        edit_badge = '<span class="badge badge-green">yes</span>' if a.get("can_edit") else '<span class="badge badge-yellow">read-only</span>'
        search = esc(a["type"] + " " + a["description"])
        rows += f'''
    <tr data-search="{search}">
      <td><code class="agent-pill">{esc(a["type"])}</code></td>
      <td>{esc(a["description"])}</td>
      <td class="tools-cell">{esc(a["tools"])}</td>
      <td>{edit_badge}</td>
    </tr>'''
    return f'''
    <p style="color:var(--text2);font-size:13px;margin-bottom:12px;">Spawn with <code style="font-family:var(--font-mono);color:var(--accent)">subagent_type</code> parameter in the Agent tool, or Claude auto-selects based on your task.</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Agent Type</th><th>Description</th><th>Tool Access</th><th>Can Edit Files</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>'''

# ── Custom agents ─────────────────────────────────────────────────────────────

def build_custom_agents():
    agents_json = json.dumps(custom_agents).replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
    cards = ""
    for a in custom_agents:
        cards += f'''
      <div class="ca-card" data-name="{esc(a["name"])}">
        <div class="ca-header">
          <code class="agent-pill">{esc(a["name"])}</code>
          <span class="ca-path">{esc(a.get("file_path", ""))}</span>
          <button class="btn-sm btn-delete" onclick="deleteCustomAgent('{esc(a["name"])}')" title="Remove">&#10005;</button>
        </div>
        <p class="ca-desc">{esc(a["description"])}</p>
        <p class="ca-when"><strong>When to use:</strong> {esc(a.get("when_to_use", ""))}</p>
      </div>'''

    return f'''
    <p style="color:var(--text2);font-size:13px;margin-bottom:12px;">Custom agents live in <code style="font-family:var(--font-mono);color:var(--accent)">.claude/agents/</code> as markdown files. Add them here to track what you've built.</p>
    <div id="custom-agents-list">{cards}</div>
    <div class="ca-add-form" id="ca-add-form">
      <div class="ca-form-row">
        <input type="text" id="ca-name" placeholder="agent-name" class="ca-input" spellcheck="false">
        <input type="text" id="ca-path" placeholder=".claude/agents/my-agent.md" class="ca-input" spellcheck="false">
      </div>
      <textarea id="ca-desc" placeholder="What does this agent do?" class="ca-textarea" rows="2" spellcheck="false"></textarea>
      <textarea id="ca-when" placeholder="When should Claude use this agent?" class="ca-textarea" rows="2" spellcheck="false"></textarea>
      <button class="btn-sm btn-add" onclick="addCustomAgent()">+ Add Agent</button>
    </div>
    <div style="margin-top:12px;">
      <button class="btn-sm btn-export" onclick="exportCustomAgents()" title="Copy JSON to clipboard">Export JSON</button>
    </div>
    <script>const DEFAULT_CUSTOM_AGENTS = `{agents_json}`;</script>'''

# ── Sidebar nav ───────────────────────────────────────────────────────────────

def build_nav():
    links = [
        ("user-profile", "User Profile", "◇"),
        ("quick-start", "Quick Start", "★"),
    ]
    for s in data["sections"]:
        links.append((s["id"], s["title"], s["icon"]))
    links += [
        ("built-in-agents", "Built-in Agents", "⬢"),
        ("custom-agents", "Custom Agents", "✦"),
        ("shortcuts", "Keyboard Shortcuts", "⌨"),
        ("permission-modes", "Permission Modes", "⊛"),
        ("input-prefixes", "Input Prefixes", "❯"),
        ("cli-flags", "CLI Flags", "⚑"),
        ("changelog", "Changelog", "↻"),
    ]
    return "".join(
        f'<a class="nav-link" href="#{esc(i)}" onclick="closeDrawer()"><span class="nav-icon">{icon}</span>{esc(label)}</a>'
        for i, label, icon in links
    )

# ── All sections HTML ─────────────────────────────────────────────────────────

sections_html = ""
for s in data["sections"]:
    sections_html += f'''
  <section id="{esc(s["id"])}" class="content-section">
    <h2 class="section-heading" style="--accent:{esc(s["color"])}">
      <span class="section-icon">{s["icon"]}</span>{esc(s["title"])}
    </h2>
    {build_command_section(s)}
  </section>'''

v = esc(version["last_version"])
updated = esc(version["last_updated"])

# ── Full HTML ─────────────────────────────────────────────────────────────────

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code Reference</title>
<style>
/* ── Reset & Variables ─────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
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
}}

[data-theme="light"] {{
  --bg: #ffffff;
  --bg2: #f6f8fa;
  --bg3: #eaeef2;
  --border: #d0d7de;
  --text: #1f2328;
  --text2: #57606a;
}}

html {{ scroll-behavior: smooth; }}
body {{ background: var(--bg); color: var(--text); font-family: var(--font-ui); font-size: 14px; line-height: 1.6; }}

/* ── Header ────────────────────────────────────────────────────────────────── */
.header {{
  position: fixed; top: 0; left: 0; right: 0; height: var(--header-h);
  background: var(--bg2); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px; padding: 0 16px; z-index: 100;
}}
.header-logo {{ font-family: var(--font-mono); font-size: 18px; color: var(--accent); font-weight: 700; white-space: nowrap; }}
.header-logo span {{ color: var(--accent2); }}
.header-version {{ font-family: var(--font-mono); font-size: 11px; color: var(--text2); background: var(--bg3); padding: 2px 7px; border-radius: 10px; white-space: nowrap; }}
.header-updated {{ font-size: 11px; color: var(--text2); white-space: nowrap; }}

.search-wrap {{ flex: 1; max-width: 420px; margin-left: auto; }}
.search-input {{
  width: 100%; background: var(--bg3); border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text); font-family: var(--font-ui); font-size: 13px; padding: 6px 12px 6px 32px;
  outline: none; transition: border-color .15s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%238b949e' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.35-4.35'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: 10px center;
}}
.search-input:focus {{ border-color: var(--accent2); }}

.header-actions {{ display: flex; gap: 8px; align-items: center; }}
.btn-icon {{
  background: none; border: 1px solid var(--border); color: var(--text2); cursor: pointer;
  border-radius: var(--radius); padding: 5px 10px; font-size: 13px; transition: all .15s; white-space: nowrap;
  text-decoration: none; display: inline-flex; align-items: center;
}}
.btn-icon:hover {{ border-color: var(--accent2); color: var(--accent2); }}
.hamburger {{ display: none; }}

/* ── Layout ────────────────────────────────────────────────────────────────── */
.layout {{ display: flex; padding-top: var(--header-h); min-height: 100vh; }}

/* ── Sidebar ───────────────────────────────────────────────────────────────── */
.sidebar {{
  position: fixed; top: var(--header-h); left: 0; bottom: 0;
  width: var(--sidebar-w); background: var(--bg2); border-right: 1px solid var(--border);
  overflow-y: auto; padding: 12px 0; z-index: 90;
  scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}}
.sidebar::-webkit-scrollbar {{ width: 4px; }}
.sidebar::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

.nav-link {{
  display: flex; align-items: center; gap: 8px; padding: 7px 16px;
  color: var(--text2); text-decoration: none; font-size: 13px; transition: all .1s;
  border-left: 2px solid transparent;
}}
.nav-link:hover {{ color: var(--text); background: var(--bg3); }}
.nav-link.active {{ color: var(--accent2); border-left-color: var(--accent2); background: var(--bg3); }}
.nav-icon {{ font-size: 12px; width: 16px; text-align: center; flex-shrink: 0; }}

/* ── Main ──────────────────────────────────────────────────────────────────── */
.main {{ margin-left: var(--sidebar-w); flex: 1; padding: 32px 40px 80px; max-width: 1100px; }}

/* ── Section headings ──────────────────────────────────────────────────────── */
.content-section {{ margin-bottom: 56px; }}
.section-heading {{
  font-size: 20px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px;
  border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px;
  color: var(--text);
}}
.section-heading::before {{ content: ''; display: block; width: 3px; height: 22px; background: var(--accent); border-radius: 2px; }}
.section-icon {{ font-size: 16px; }}
.sub-heading {{ font-size: 14px; font-weight: 600; color: var(--text2); margin: 24px 0 10px; letter-spacing: .05em; text-transform: uppercase; }}

/* ── Tables ────────────────────────────────────────────────────────────────── */
.table-wrap {{ overflow-x: auto; border-radius: var(--radius); border: 1px solid var(--border); }}
table {{ width: 100%; border-collapse: collapse; }}
thead {{ background: var(--bg3); }}
th {{ padding: 10px 14px; text-align: left; font-size: 12px; font-weight: 600; color: var(--text2); letter-spacing: .05em; text-transform: uppercase; white-space: nowrap; }}
td {{ padding: 10px 14px; border-top: 1px solid var(--border); vertical-align: top; }}
tr:hover td {{ background: var(--bg3); }}
tr.hidden {{ display: none; }}
.notes-cell {{ font-size: 12px; color: var(--text2); }}

/* ── Command pills ─────────────────────────────────────────────────────────── */
.cmd-cell {{ display: flex; flex-direction: column; gap: 4px; }}
.cmd-pill {{
  display: inline-block; background: var(--bg3); border: 1px solid var(--border);
  color: var(--accent); font-family: var(--font-mono); font-size: 13px; padding: 2px 8px;
  border-radius: var(--radius); cursor: pointer; transition: all .15s; white-space: nowrap;
  user-select: none;
}}
.cmd-pill:hover {{ border-color: var(--accent); background: rgba(218,138,103,.1); }}
.aliases {{ display: flex; gap: 4px; flex-wrap: wrap; }}
.alias {{ font-family: var(--font-mono); font-size: 11px; color: var(--text2); background: var(--bg); border: 1px solid var(--border); padding: 1px 6px; border-radius: var(--radius); }}
.args {{ font-family: var(--font-mono); font-size: 12px; color: var(--accent2); white-space: nowrap; }}
.example-cmd {{ font-family: var(--font-mono); font-size: 12px; color: var(--text2); white-space: nowrap; }}
.muted-dash {{ color: var(--border); font-size: 13px; }}
.flag-pill {{ font-family: var(--font-mono); font-size: 12px; color: var(--purple); white-space: nowrap; }}
.prefix-pill {{ font-family: var(--font-mono); font-size: 18px; color: var(--orange); font-weight: 700; }}
.example {{ font-family: var(--font-mono); font-size: 12px; color: var(--text2); white-space: nowrap; }}
.mode-pill {{ font-family: var(--font-mono); font-size: 12px; padding: 2px 8px; border-radius: var(--radius); border: 1px solid; }}
.mode-default {{ color: var(--text2); border-color: var(--border); }}
.mode-acceptEdits {{ color: var(--yellow); border-color: var(--yellow); }}
.mode-plan {{ color: var(--accent2); border-color: var(--accent2); }}
.mode-auto {{ color: var(--green); border-color: var(--green); }}
.mode-bypassPermissions {{ color: var(--red); border-color: var(--red); }}
.requires {{ font-size: 11px; color: var(--text2); margin-top: 4px; }}

/* ── Keyboard keys ─────────────────────────────────────────────────────────── */
kbd {{
  display: inline-block; background: var(--bg3); border: 1px solid var(--border);
  border-bottom-width: 2px; border-radius: 4px; font-family: var(--font-mono);
  font-size: 11px; padding: 1px 6px; color: var(--text); white-space: nowrap;
}}
.kbd-cell {{ white-space: nowrap; }}
.key-sep {{ color: var(--text2); font-size: 11px; margin: 0 2px; }}

/* ── Badges ────────────────────────────────────────────────────────────────── */
.badge {{ display: inline-block; font-size: 11px; font-weight: 600; padding: 1px 7px; border-radius: 10px; text-transform: uppercase; letter-spacing: .04em; }}
.badge-green {{ background: rgba(63,185,80,.15); color: var(--green); }}
.badge-yellow {{ background: rgba(210,153,34,.15); color: var(--yellow); }}
.badge-red {{ background: rgba(248,81,73,.15); color: var(--red); }}
.badge-gray {{ background: var(--bg3); color: var(--text2); }}

/* ── Quick Start ───────────────────────────────────────────────────────────── */
.qs-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }}
.qs-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 16px; transition: border-color .15s; }}
.qs-card:hover {{ border-color: var(--accent2); }}
.qs-cmd {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer; }}
.qs-cmd code {{ font-family: var(--font-mono); font-size: 14px; color: var(--accent); font-weight: 600; }}
.qs-cmd .copy-hint {{ font-size: 10px; color: var(--text2); opacity: 0; transition: opacity .15s; }}
.qs-card:hover .copy-hint {{ opacity: 1; }}
.qs-why {{ font-size: 13px; color: var(--text2); line-height: 1.5; }}

/* ── Hero ──────────────────────────────────────────────────────────────────── */
.hero {{ margin-bottom: 40px; padding: 28px 32px; background: linear-gradient(135deg, rgba(218,138,103,.08) 0%, rgba(121,192,255,.08) 100%); border: 1px solid var(--border); border-radius: 10px; }}
.hero-title {{ font-size: 28px; font-weight: 700; margin-bottom: 6px; }}
.hero-title span {{ color: var(--accent); font-family: var(--font-mono); }}
.hero-sub {{ color: var(--text2); font-size: 14px; margin-bottom: 16px; }}
.hero-meta {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.hero-chip {{ font-size: 12px; color: var(--text2); background: var(--bg3); border: 1px solid var(--border); border-radius: 10px; padding: 3px 10px; }}
.hero-chip a {{ color: var(--accent2); text-decoration: none; }}
.hero-chip a:hover {{ text-decoration: underline; }}

/* ── Changelog ─────────────────────────────────────────────────────────────── */
.changelog-entry {{ padding: 16px; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 12px; background: var(--bg2); }}
.changelog-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }}
.changelog-version {{ font-family: var(--font-mono); font-size: 14px; font-weight: 700; color: var(--accent); }}
.changelog-date {{ font-size: 12px; color: var(--text2); }}
.changelog-link {{ font-size: 12px; color: var(--accent2); text-decoration: none; margin-left: auto; }}
.changelog-link:hover {{ text-decoration: underline; }}
.changelog-changes {{ list-style: none; display: flex; flex-direction: column; gap: 6px; }}
.changelog-changes li {{ font-size: 13px; color: var(--text2); display: flex; gap: 8px; align-items: flex-start; }}
.change-type {{ display: inline-block; font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; text-transform: uppercase; letter-spacing: .04em; flex-shrink: 0; margin-top: 2px; }}
.change-new {{ background: rgba(63,185,80,.15); color: var(--green); }}
.change-updated {{ background: rgba(121,192,255,.15); color: var(--accent2); }}
.change-fix {{ background: rgba(210,153,34,.15); color: var(--yellow); }}
.change-removed {{ background: rgba(248,81,73,.15); color: var(--red); }}
.muted {{ color: var(--text2); font-size: 13px; font-style: italic; }}

/* ── User Profile ──────────────────────────────────────────────────────────── */
.profile-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px; }}
.profile-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }}
.profile-icon {{ font-size: 18px; color: var(--accent); }}
.profile-title {{ font-size: 16px; font-weight: 600; color: var(--text); }}
.profile-actions {{ margin-left: auto; display: flex; gap: 6px; }}
.profile-view p {{ color: var(--text2); font-size: 13px; margin: 4px 0; }}
.profile-view strong {{ color: var(--text); }}
.profile-view li {{ color: var(--text2); font-size: 13px; margin-left: 16px; list-style: disc; }}
.profile-view br {{ display: block; margin: 4px 0; }}
.profile-h1 {{ font-size: 16px; font-weight: 600; color: var(--text); margin: 12px 0 6px; }}
.profile-h2 {{ font-size: 14px; font-weight: 600; color: var(--accent2); margin: 12px 0 6px; }}
.profile-editor {{ width: 100%; min-height: 200px; background: var(--bg3); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text); font-family: var(--font-mono); font-size: 13px; padding: 12px; resize: vertical; outline: none; }}
.profile-editor:focus {{ border-color: var(--accent2); }}

/* ── Buttons ───────────────────────────────────────────────────────────────── */
.btn-sm {{ background: var(--bg3); border: 1px solid var(--border); color: var(--text2); border-radius: var(--radius); padding: 4px 12px; font-size: 12px; cursor: pointer; transition: all .15s; }}
.btn-sm:hover {{ border-color: var(--accent2); color: var(--accent2); }}
.btn-add {{ background: rgba(63,185,80,.1); border-color: var(--green); color: var(--green); }}
.btn-add:hover {{ background: rgba(63,185,80,.2); }}
.btn-delete {{ background: none; border: none; color: var(--text2); cursor: pointer; font-size: 14px; padding: 2px 6px; }}
.btn-delete:hover {{ color: var(--red); }}
.btn-export {{ background: rgba(121,192,255,.08); border-color: var(--accent2); color: var(--accent2); }}
.btn-save {{ background: rgba(63,185,80,.1); border-color: var(--green); color: var(--green); }}

/* ── Agent pills ───────────────────────────────────────────────────────────── */
.agent-pill {{ display: inline-block; background: var(--bg3); border: 1px solid var(--border); color: var(--purple); font-family: var(--font-mono); font-size: 12px; padding: 2px 8px; border-radius: var(--radius); cursor: pointer; white-space: nowrap; }}
.agent-pill:hover {{ border-color: var(--purple); }}
.tools-cell {{ font-size: 12px; color: var(--text2); }}

/* ── Custom Agents ─────────────────────────────────────────────────────────── */
.ca-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 16px; margin-bottom: 10px; transition: border-color .15s; }}
.ca-card:hover {{ border-color: var(--purple); }}
.ca-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
.ca-path {{ font-family: var(--font-mono); font-size: 11px; color: var(--text2); margin-left: auto; }}
.ca-desc {{ font-size: 13px; color: var(--text2); margin-bottom: 4px; }}
.ca-when {{ font-size: 12px; color: var(--text2); }}
.ca-when strong {{ color: var(--text); }}
.ca-add-form {{ background: var(--bg2); border: 1px dashed var(--border); border-radius: var(--radius); padding: 16px; margin-top: 16px; }}
.ca-form-row {{ display: flex; gap: 8px; margin-bottom: 8px; }}
.ca-input {{ flex: 1; background: var(--bg3); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text); font-family: var(--font-mono); font-size: 13px; padding: 6px 10px; outline: none; }}
.ca-input:focus {{ border-color: var(--accent2); }}
.ca-textarea {{ width: 100%; background: var(--bg3); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text); font-family: var(--font-ui); font-size: 13px; padding: 6px 10px; outline: none; resize: vertical; margin-bottom: 8px; }}
.ca-textarea:focus {{ border-color: var(--accent2); }}

/* ── Toast ─────────────────────────────────────────────────────────────────── */
.toast {{
  position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(20px);
  background: var(--bg3); border: 1px solid var(--border); color: var(--text);
  padding: 8px 18px; border-radius: 20px; font-size: 13px; opacity: 0;
  transition: all .25s; pointer-events: none; z-index: 999;
}}
.toast.show {{ opacity: 1; transform: translateX(-50%) translateY(0); }}

/* ── Back to top ───────────────────────────────────────────────────────────── */
.back-top {{
  position: fixed; bottom: 28px; right: 28px; background: var(--bg3);
  border: 1px solid var(--border); color: var(--text2); cursor: pointer;
  border-radius: 50%; width: 38px; height: 38px; font-size: 16px;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: all .25s; pointer-events: none; z-index: 90;
}}
.back-top.visible {{ opacity: 1; pointer-events: all; }}
.back-top:hover {{ border-color: var(--accent2); color: var(--accent2); }}

/* ── Overlay ───────────────────────────────────────────────────────────────── */
.overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 85; }}
.overlay.open {{ display: block; }}

/* ── Responsive ────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {{
  .sidebar {{ left: calc(-1 * var(--sidebar-w)); transition: left .25s; }}
  .sidebar.open {{ left: 0; }}
  .main {{ margin-left: 0; padding: 20px 16px 80px; }}
  .hamburger {{ display: flex; }}
  .header-updated {{ display: none; }}
  .qs-grid {{ grid-template-columns: 1fr; }}
  .hero {{ padding: 20px; }}
  .hero-title {{ font-size: 22px; }}
}}
</style>
</head>
<body>

<!-- Header -->
<header class="header">
  <button class="btn-icon hamburger" onclick="toggleDrawer()" aria-label="Menu">&#9776;</button>
  <div class="header-logo">claude<span>/</span>ref</div>
  <span class="header-version">v{v}</span>
  <span class="header-updated">Updated {updated}</span>

  <div class="search-wrap">
    <input class="search-input" type="search" placeholder="Search commands, shortcuts&#8230;" id="search" oninput="handleSearch(this.value)" autocomplete="off" spellcheck="false">
  </div>

  <div class="header-actions">
    <button class="btn-icon" onclick="toggleTheme()" title="Toggle light/dark">&#9681;</button>
    <a class="btn-icon" href="https://docs.anthropic.com/en/docs/claude-code/cli-reference" target="_blank" rel="noopener">Docs &#8599;</a>
  </div>
</header>

<!-- Mobile overlay -->
<div class="overlay" id="overlay" onclick="closeDrawer()"></div>

<!-- Sidebar -->
<nav class="sidebar" id="sidebar">
  {build_nav()}
</nav>

<!-- Main -->
<main class="main">

  <div class="hero">
    <h1 class="hero-title"><span>Claude Code</span> Reference Guide</h1>
    <p class="hero-sub">Every command, shortcut, and mode &#8212; always current. Click any command to copy it.</p>
    <div class="hero-meta">
      <span class="hero-chip">v{v}</span>
      <span class="hero-chip">Updated {updated}</span>
      <span class="hero-chip"><a href="https://github.com/anthropics/claude-code/releases" target="_blank" rel="noopener">anthropics/claude-code releases &#8599;</a></span>
    </div>
  </div>

  <section id="user-profile" class="content-section">
    <h2 class="section-heading" style="--accent:#da8a67">
      <span class="section-icon">&#9671;</span>User Profile
    </h2>
    {build_user_profile()}
  </section>

  <section id="quick-start" class="content-section">
    <h2 class="section-heading" style="--accent:#da8a67">
      <span class="section-icon">&#9733;</span>Quick Start &#8212; Top 10 for New Agentic Engineers
    </h2>
    {build_quick_start()}
  </section>

  {sections_html}

  <section id="built-in-agents" class="content-section">
    <h2 class="section-heading" style="--accent:#bc8cff">
      <span class="section-icon">&#11042;</span>Built-in Agents
    </h2>
    {build_builtin_agents()}
  </section>

  <section id="custom-agents" class="content-section">
    <h2 class="section-heading" style="--accent:#ffa657">
      <span class="section-icon">&#10022;</span>My Custom Agents
    </h2>
    {build_custom_agents()}
  </section>

  <section id="shortcuts" class="content-section">
    <h2 class="section-heading" style="--accent:#79c0ff">
      <span class="section-icon">&#9000;</span>Keyboard Shortcuts
    </h2>
    {build_shortcuts()}
  </section>

  <section id="permission-modes" class="content-section">
    <h2 class="section-heading" style="--accent:#bc8cff">
      <span class="section-icon">&#8859;</span>Permission Modes
    </h2>
    <p style="color:var(--text2);font-size:13px;margin-bottom:16px;">Cycle through modes with <kbd>Shift+Tab</kbd>. The mode you pick determines how much Claude does autonomously vs. how much requires your approval.</p>
    {build_permission_modes()}
  </section>

  <section id="input-prefixes" class="content-section">
    <h2 class="section-heading" style="--accent:#ffa657">
      <span class="section-icon">&#10095;</span>Special Input Prefixes
    </h2>
    {build_input_prefixes()}
  </section>

  <section id="cli-flags" class="content-section">
    <h2 class="section-heading" style="--accent:#3fb950">
      <span class="section-icon">&#9873;</span>CLI Flags
    </h2>
    <p style="color:var(--text2);font-size:13px;margin-bottom:16px;">Flags for the <code style="font-family:var(--font-mono);color:var(--accent)">claude</code> startup command. Combine freely.</p>
    {build_cli_flags()}
  </section>

  <section id="changelog" class="content-section">
    <h2 class="section-heading" style="--accent:#f85149">
      <span class="section-icon">&#8635;</span>Auto-Update Changelog
    </h2>
    {build_changelog()}
  </section>

</main>

<div class="toast" id="toast">Copied!</div>
<button class="back-top" id="back-top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" title="Back to top">&#8593;</button>

<script>
const root = document.documentElement;
const saved = localStorage.getItem('theme') || 'dark';
if (saved === 'light') root.setAttribute('data-theme', 'light');

function toggleTheme() {{
  const isLight = root.getAttribute('data-theme') === 'light';
  root.setAttribute('data-theme', isLight ? 'dark' : 'light');
  localStorage.setItem('theme', isLight ? 'dark' : 'light');
}}

function copyCmd(text) {{
  navigator.clipboard.writeText(text).then(() => showToast('Copied: ' + text));
}}

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1800);
}}

function handleSearch(query) {{
  const q = query.toLowerCase().trim();
  document.querySelectorAll('tr[data-search]').forEach(row => {{
    row.classList.toggle('hidden', !!q && !row.dataset.search.toLowerCase().includes(q));
  }});
  document.querySelectorAll('.qs-card').forEach(card => {{
    card.style.display = (!q || card.textContent.toLowerCase().includes(q)) ? '' : 'none';
  }});
}}

const navLinks = document.querySelectorAll('.nav-link');
const observer = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      navLinks.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + e.target.id));
    }}
  }});
}}, {{ rootMargin: '-20% 0px -70% 0px' }});
document.querySelectorAll('.content-section').forEach(s => observer.observe(s));

function toggleDrawer() {{
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}}
function closeDrawer() {{
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
}}

window.addEventListener('scroll', () => {{
  document.getElementById('back-top').classList.toggle('visible', window.scrollY > 400);
}});

// ── User Profile (localStorage) ──────────────────────────────────────────────
function loadProfile() {{
  const saved = localStorage.getItem('user-profile-md');
  if (saved) {{
    document.getElementById('profile-editor').value = saved;
    document.getElementById('profile-view').innerHTML = renderMd(saved);
  }}
}}
function renderMd(md) {{
  return md.split('\\n').map(line => {{
    const t = line.trim();
    if (t.startsWith('# ')) return '<h3 class="profile-h1">' + esc(t.slice(2)) + '</h3>';
    if (t.startsWith('## ')) return '<h4 class="profile-h2">' + esc(t.slice(3)) + '</h4>';
    if (t.startsWith('- ')) return '<li>' + t.slice(2).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') + '</li>';
    if (t === '') return '<br>';
    return '<p>' + t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') + '</p>';
  }}).join('\\n');
}}
function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

let profileEditing = false;
function toggleEditProfile() {{
  profileEditing = !profileEditing;
  const view = document.getElementById('profile-view');
  const editor = document.getElementById('profile-editor');
  const btn = document.getElementById('profile-edit-btn');
  if (profileEditing) {{
    view.style.display = 'none';
    editor.style.display = '';
    btn.textContent = 'Save';
    btn.classList.add('btn-save');
  }} else {{
    const md = editor.value;
    localStorage.setItem('user-profile-md', md);
    view.innerHTML = renderMd(md);
    view.style.display = '';
    editor.style.display = 'none';
    btn.textContent = 'Edit';
    btn.classList.remove('btn-save');
    showToast('Profile saved');
  }}
}}
function exportProfile() {{
  const md = document.getElementById('profile-editor').value;
  navigator.clipboard.writeText(md).then(() => showToast('Profile markdown copied — paste into data/user.md'));
}}
loadProfile();

// ── Custom Agents (localStorage) ─────────────────────────────────────────────
function loadCustomAgents() {{
  const saved = localStorage.getItem('custom-agents-json');
  if (saved) {{
    try {{
      const agents = JSON.parse(saved);
      renderCustomAgents(agents);
    }} catch(e) {{}}
  }}
}}
function getCustomAgents() {{
  const saved = localStorage.getItem('custom-agents-json');
  if (saved) {{ try {{ return JSON.parse(saved); }} catch(e) {{}} }}
  return JSON.parse(DEFAULT_CUSTOM_AGENTS);
}}
function saveCustomAgents(agents) {{
  localStorage.setItem('custom-agents-json', JSON.stringify(agents));
  renderCustomAgents(agents);
}}
function renderCustomAgents(agents) {{
  const list = document.getElementById('custom-agents-list');
  if (!agents.length) {{
    list.innerHTML = '<p class="muted">No custom agents yet — add one below.</p>';
    return;
  }}
  list.innerHTML = agents.map(a => `
    <div class="ca-card" data-name="${{esc(a.name)}}">
      <div class="ca-header">
        <code class="agent-pill">${{esc(a.name)}}</code>
        <span class="ca-path">${{esc(a.file_path || '')}}</span>
        <button class="btn-sm btn-delete" onclick="deleteCustomAgent('${{esc(a.name)}}')" title="Remove">&#10005;</button>
      </div>
      <p class="ca-desc">${{esc(a.description)}}</p>
      <p class="ca-when"><strong>When to use:</strong> ${{esc(a.when_to_use || '')}}</p>
    </div>`).join('');
}}
function addCustomAgent() {{
  const name = document.getElementById('ca-name').value.trim();
  const desc = document.getElementById('ca-desc').value.trim();
  const when = document.getElementById('ca-when').value.trim();
  const path = document.getElementById('ca-path').value.trim();
  if (!name || !desc) {{ showToast('Need at least a name and description'); return; }}
  const agents = getCustomAgents();
  agents.push({{ name, description: desc, when_to_use: when, file_path: path || '.claude/agents/' + name + '.md' }});
  saveCustomAgents(agents);
  document.getElementById('ca-name').value = '';
  document.getElementById('ca-desc').value = '';
  document.getElementById('ca-when').value = '';
  document.getElementById('ca-path').value = '';
  showToast('Agent added: ' + name);
}}
function deleteCustomAgent(name) {{
  const agents = getCustomAgents().filter(a => a.name !== name);
  saveCustomAgents(agents);
  showToast('Removed: ' + name);
}}
function exportCustomAgents() {{
  const agents = getCustomAgents();
  navigator.clipboard.writeText(JSON.stringify(agents, null, 2)).then(() => showToast('Custom agents JSON copied — paste into data/custom-agents.json'));
}}
loadCustomAgents();
</script>
</body>
</html>"""

out = ROOT / "index.html"
out.write_text(HTML, encoding="utf-8")
print(f"Built {out} successfully.")
