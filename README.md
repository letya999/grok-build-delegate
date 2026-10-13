<p align="center">
  <strong>English</strong> · <a href="README.ru.md">Русский</a>
</p>

<p align="center">
  <h1 align="center">Grok Build Delegate</h1>
</p>

<p align="center">
  <a href="https://github.com/letya999/grok-build-delegate"><img src="https://img.shields.io/badge/status-active-brightgreen" alt="status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT"></a>
  <a href="https://skills.sh/letya999/grok-build-delegate"><img src="https://skills.sh/b/letya999/grok-build-delegate" alt="skills.sh"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cli-grok-purple" alt="CLI: grok">
</p>

Headless Grok Build CLI delegate skill by [Artem Letyushev](https://github.com/letya999).

The command is `scripts/delegate_grok.py`. The primary consumer is the controlling agent or orchestrator: every execution runs Grok Build once as a bounded, non-interactive subprocess (`grok -p`) and returns one structured JSON envelope.

---

## One objective, bounded subprocess, zero trust

The wrapper acts as a deterministic isolation layer between your controlling agent and the Grok Build CLI:

- **Single non-interactive execution:** Invokes `grok -p` directly via `subprocess.run(..., shell=False)` without terminal takeovers.
- **Strict workspace scoping:** Restricts Grok Build to the target project directory via `--cwd <path>`.
- **Scripting stability:** Passes `--no-auto-update` and `--no-alt-screen` to prevent unexpected background checks or screen corruption.
- **Structured output support:** Forwards `--json-schema` to extract verified JSON responses directly into the manifest.
- **Zero-trust verification:** Outputs are unverified until independently confirmed by diffs and tests.
- **Credential isolation:** Never inspects or prints `XAI_API_KEY`, `~/.grok` credentials, or `.env` files.

## Capability matrix

| Capability / Setting | Specification | Behavior & Guarantees |
|---|---|---|
| **Headless command** | `grok -p "<task>"` | Non-interactive execution in print mode |
| **Workspace scoping** | `--cwd <cwd>` | Restricts Grok Build to the target project working directory |
| **Output format** | `--output-format json` | Single JSON object captured at completion |
| **Structured output** | `--json-schema <schema>` | Constrains output to a strict JSON Schema |
| **Scripting hygiene** | `--no-auto-update --no-alt-screen` | Disables background update checks and fullscreen mode |
| **Turn control** | `--max-turns <int>` | Restricts max interaction turns in headless execution |
| **Autonomous edits** | `--always-approve` / `--trust` | Enables autonomous modification only when explicitly granted |
| **Session resumption** | `--session-id <id>` | Resumes existing Grok session |
| **Executable override** | `GROK_BIN` env var | Custom executable path before searching PATH |
| **Standard exit codes** | `0, 2, 65, 124, 126, 127` | Standardized error signaling |

## Install

With `npx skills`:

```bash
npx skills add letya999/grok-build-delegate
```

Or clone into an agent skill directory:

```bash
git clone https://github.com/letya999/grok-build-delegate.git .agents/skills/grok-build-delegate
```

## Quick Start

### POSIX (macOS, Linux, WSL)

```bash
python3 scripts/delegate_grok.py \
  --cwd "$PWD" \
  --task "Review this repository and report the highest-risk issue." \
  --timeout 45m
```

### Windows PowerShell

```powershell
py -3 .\scripts\delegate_grok.py `
  --cwd (Get-Location).Path `
  --task "Review this repository and report the highest-risk issue." `
  --timeout 45m
```

---

<details>
<summary>JSON Manifest Schema & Agent Integration</summary>

The wrapper writes `stdout.json`, `stderr.log`, and `result.json` into a temporary directory:

```json
{
  "tool": "grok",
  "cwd": "C:\\work\\repo",
  "exit_code": 0,
  "output_dir": "C:\\Temp\\grok-build-delegate-xyz",
  "stdout": "C:\\Temp\\grok-build-delegate-xyz\\stdout.json",
  "stderr": "C:\\Temp\\grok-build-delegate-xyz\\stderr.log",
  "response": {
    "issue": "High risk vulnerability in auth handler",
    "severity": "critical"
  },
  "raw": {
    "text": "...",
    "structuredOutput": { "..." }
  }
}
```

If Grok completes with exit code 0 but returns an empty response or malformed payload, the wrapper returns code `65`.

</details>

<details>
<summary>CLI Flags & Configuration Reference</summary>

| Flag | Type | Description |
|---|---|---|
| `--cwd` | Path (required) | Project directory for execution. Exits with `2` if directory is missing. |
| `--task` | String (required) | Instruction / task to delegate to Grok Build. |
| `--timeout` | Duration (default: `45m`) | Timeout formatted as `90s`, `45m`, `2h`, or integer seconds. |
| `--model` | String | Grok model override. |
| `--json-schema` | String | JSON Schema string to enforce structured JSON output. |
| `--max-turns` | Integer | Maximum turns for multi-step tasks. |
| `--always-approve` | Flag | Passes `--always-approve` to grant automated tool execution. |
| `--trust` | Flag | Passes `--trust` for repository-level trust permissions. |
| `--session-id` | String | Resumes conversation by session ID. |
| `--output-dir` | Path | Custom artifact directory. |

</details>

<details>
<summary>Safety Posture & Credential Guardrails</summary>

- **No credential leaks:** Never reads or logs `XAI_API_KEY`, OAuth tokens, or `~/.grok` credential files.
- **Bounded execution:** No persistent background daemons or unbounded polling loops.
- **Anti-recursion rule:** Delegated Grok instances must not recursively spawn further delegate wrappers.

</details>

<details>
<summary>Independent Verification Protocol</summary>

Outputs are unverified evidence. After delegated file modifications:

1. Check changes independently: `git diff --stat` and `git diff`.
2. Run test suites outside the delegated environment: `pytest`, `npm test`, etc.
3. Verify newly generated files and imports.

</details>

<details>
<summary>Test Suite & Quality Checks</summary>

Run the test suite with standard library `unittest`:

```bash
python -m unittest discover -s tests -v
```

</details>

<details>
<summary>Agent Skill Entry Points</summary>

- [SKILL.md](SKILL.md) — Skill instruction specification for coding agents.
- [QUICKSTART.md](QUICKSTART.md) — Quick command reference.
- [references/runtime-setup.md](references/runtime-setup.md) — Cross-platform pre-flight checks.
- [references/headless-reference.md](references/headless-reference.md) — Grok Build CLI headless reference.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) — Discovery index for skills.sh.
- [dist/grok-build-delegate.zip](dist/grok-build-delegate.zip) — Discoverable archive artifact.

</details>

<details>
<summary>License</summary>

MIT License. See [LICENSE](LICENSE) for full text. Copyright (c) 2026 Artem Letyushev.

</details>
