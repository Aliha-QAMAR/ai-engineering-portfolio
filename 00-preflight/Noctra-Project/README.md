# NOCTRA
**Beyond the Obvious.**

NOCTRA is an AI Detective Investigation Platform.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`
3. `python app.py`

## Architecture
Flask backend, SQLAlchemy ORM, OpenAI agent tools.

## Tech Stack
- Python 3
- Flask
- SQLAlchemy
- OpenAI API

---

## Status — what's built vs. what's next

### Fixed this pass
Your live screen wasn't showing rain/blink/tilt/eye-tracking because **four
JS files were corrupted** — every template literal backtick and `${}` had
been escaped (`` \` `` and `\$` instead of `` ` `` and `$`), which is invalid
JavaScript. Since `base.html` loads `app.js` as an ES module
(`<script type="module">`), and `app.js` imports from `orion.js`, `scene.js`,
and `atmosphere.js`, a syntax error in *any one* of them silently broke the
whole script — nothing animated, nothing initialized. Fixed files:
`orion.js`, `scene.js`, `atmosphere.js`, `api.js`. Verified with
`node --check` (as both script and ES module) and by running the Flask app
and confirming all routes + static assets serve the corrected files.

**Landing page (Screen 1) was NOT touched** — same HTML, same Orion SVG
(locked geometry, untouched), same layout. Only the broken JS underneath it
was repaired. With the fix, the behavior that was already coded now actually
runs:
- Window rain (`#window-rain`) + ambient rain (`#ambient-rain`)
- Dust motes drifting
- Occasional lightning flashes
- Orion's head tilts toward the cursor, eyes track the cursor, and he blinks
  on a randomized interval (with occasional double-blinks)

### Already built (confirmed working)
- **Screen 1 — Landing**: locked, unchanged.
- **Screen 2 — Access Clearance** (`/access`): folder/personnel-file reveal
  → "Verify Identity" → `/auth`.
- **Screen 3 — Authentication** (`/auth`): document-style Codename/Passphrase
  form, `ACCESS ARCHIVES` / `CREATE DOSSIER`, `ACCESS GRANTED` stamp on
  success, real login/register wired to `backend/auth.py`.
- **Screen 4 — Investigation Hub** (`/hub`): desk-as-interface with
  interactive desk items (new case, evidence wall, archive, memory vault,
  search), Orion present, session-aware.
- **Backend**: Flask app factory-style routes, SQLAlchemy models
  (`User`, `Investigation`, `Evidence`), auth blueprint, investigation
  create/list/get + evidence upload, SSE streaming endpoint for
  `investigate`, planner/agent/memory/mcp/evaluate/injection-test modules
  scaffolded.

### Screens 5–10 — now built
- **Screen 5 — Create Investigation** (`/investigation/new`): case name +
  description form styled as a case folder, drag-and-drop evidence
  dropzone (CSV/PDF/Images/Audio/Notes, auto-tagged), "Begin Investigation"
  → creates the case, uploads evidence, redirects into the workspace.
- **Screen 6 — Investigation Workspace** (`/investigation/<id>`): evidence
  board, live timeline, a simple relationship graph, and an Investigation
  Log — all populated in real time from the `/investigate` SSE stream using
  detective terminology (Inspecting Evidence, Consulting Previous Cases,
  Building Timeline, Finding Relationships…). Re-visiting a completed case
  reloads the same log/timeline from the database.
- **Screen 7 — Case Report** (`/investigation/<id>/report`): confidential
  report sheet with confidence/coverage bars from `evaluate_investigation`,
  evidence list, timeline, and reasoning. "Export PDF" uses a print
  stylesheet (`window.print()` → Save as PDF) rather than a server-side PDF
  dependency, to keep the stack light.
- **Screen 8 — Archive** (`/archive`): search + status filters (Active /
  Closed / Removed), open / view report / delete / restore per case.
  Delete is a soft delete (`status='deleted'`) so Restore works.
- **Screen 9 — Memory Vault** (`/memory`): now actually populated —
  finishing an investigation writes a memory entry ("Case Closed: <name>")
  tied to the signed-in investigator. Previously `store_memory` was never
  called anywhere; it's now wired into investigation completion.
- **Screen 10 — Settings** (`/settings`): leather-notebook profile view
  (codename/clearance from `/api/auth/status`), reduced-motion toggle
  (applies instantly, saved locally), notification toggles, sign out.

All new screens reuse Orion (`orion.js`, unmodified), the same rain/dust/
lightning atmosphere, and the existing type system/color tokens — no new
visual language was introduced.

### Bug fixed while wiring these up
`app.py` read the logged-in user from `request.cookies.get('user_id')` in
three places, but login only ever set `session['user_id']` — a signed
cookie under a different name Flask manages itself. That mismatch meant:
new cases were never attached to the logged-in user, and `/api/memory`
always returned an empty list. Fixed to read from `session` consistently,
and confirmed live: register → login → create case → upload evidence →
run investigation via SSE → case report → memory vault entry appears →
archive delete/restore — all tested end-to-end against a running server.

### Still open (small, deliberately deferred)
- The AI planner (`backend/planner.py`) uses a mock step list unless
  `OPENAI_API_KEY` is set in `.env` — add your key to get real
  GPT-generated investigation strategies instead of the default sequence.
- The relationship graph on Screen 6 is a simple radial placeholder tied to
  step count, not a real entity graph — upgrading it would mean having
  `map_relationships` return structured entities instead of a mock string.
- Screen 8's "Closed" filter has no case ever reaches `status: closed`
  yet — nothing currently marks a case closed vs. just "investigated."
