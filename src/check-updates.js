/**
 * check-updates.js
 * Runs in GitHub Actions daily.
 * 1. Checks npm for the latest @anthropic-ai/claude-code version
 * 2. Compares against the last known version in data/version.json
 * 3. If newer: fetches release notes from GitHub, updates commands.json changelog,
 *    updates version.json, then triggers a build
 *
 * No paid APIs. No LLMs. Pure free-tier infrastructure.
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} fetching ${url}`);
  return res.json();
}

async function fetchText(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'claude-code-reference-updater/1.0' }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} fetching ${url}`);
  return res.text();
}

function readJSON(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

function writeJSON(path, data) {
  writeFileSync(path, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

async function getLatestNpmVersion() {
  const data = await fetchJSON('https://registry.npmjs.org/@anthropic-ai/claude-code/latest');
  return data.version;
}

async function getGitHubRelease(version) {
  // Try exact tag first, fall back to latest release
  const REPO = 'anthropics/claude-code';
  try {
    const data = await fetchJSON(`https://api.github.com/repos/${REPO}/releases/tags/v${version}`);
    return data;
  } catch {
    const data = await fetchJSON(`https://api.github.com/repos/${REPO}/releases/latest`);
    return data;
  }
}

/**
 * Parse release notes markdown into structured change entries.
 * Extracts lines that look like new or changed commands.
 * Works on Anthropic's conventional changelog format.
 */
function parseReleaseNotes(body = '') {
  const lines = body.split('\n');
  const changes = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;

    // Capture lines mentioning slash commands
    const commandMatch = trimmed.match(/(`\/[\w-]+`|\/[\w-]+)/g);
    if (commandMatch) {
      changes.push({
        type: detectChangeType(trimmed),
        text: trimmed.replace(/^[-*]\s*/, ''),
        commands: commandMatch.map(c => c.replace(/`/g, ''))
      });
    }
  }

  return changes;
}

function detectChangeType(line) {
  const lower = line.toLowerCase();
  if (lower.includes('new') || lower.includes('add') || lower.includes('introduc')) return 'new';
  if (lower.includes('fix') || lower.includes('bug') || lower.includes('patch')) return 'fix';
  if (lower.includes('deprecat') || lower.includes('remov')) return 'removed';
  return 'updated';
}

async function main() {
  const versionPath = join(ROOT, 'data', 'version.json');
  const commandsPath = join(ROOT, 'data', 'commands.json');

  const stored = readJSON(versionPath);
  const latestVersion = await getLatestNpmVersion();
  const today = new Date().toISOString().split('T')[0];

  console.log(`Stored version : ${stored.last_version}`);
  console.log(`Latest version : ${latestVersion}`);

  // Always update last_checked date
  stored.last_checked = today;

  // Short-circuit: if we already have the latest version stored, skip the update
  if (latestVersion !== stored.last_version) {
    console.log('No new version — nothing to do.');
    writeJSON(versionPath, stored);
    return;
  }

  console.log(`New version detected: ${stored.last_version} → ${latestVersion}`);

  // Fetch release notes
  let release = null;
  let changes = [];
  try {
    release = await getGitHubRelease(latestVersion);
    changes = parseReleaseNotes(release.body);
    console.log(`Parsed ${changes.length} command-related changes from release notes`);
  } catch (err) {
    console.warn(`Could not fetch GitHub release: ${err.message}`);
  }

  // Update version.json
  stored.last_version = latestVersion;
  stored.last_updated = today;
  writeJSON(versionPath, stored);

  // Append changelog entry to commands.json
  const commands = readJSON(commandsPath);
  if (!commands.changelog) commands.changelog = [];
  commands.changelog.unshift({
    version: latestVersion,
    date: today,
    release_url: release?.html_url || `https://github.com/anthropics/claude-code/releases`,
    release_notes_raw: release?.body?.slice(0, 2000) || '',
    parsed_changes: changes
  });
  commands.meta.last_updated = today;
  writeJSON(commandsPath, commands);

  console.log(`Updated data/commands.json and data/version.json for v${latestVersion}`);
  console.log('Run `npm run build` to regenerate index.html');
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
