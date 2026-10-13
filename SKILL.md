---
name: grok-build-delegate
description: Run Grok Build CLI as a headless delegate. Use when the user names Grok Build or grok, says "ask Grok", wants an xAI-backed second opinion, or compares coding agents. Do NOT use for interactive sessions, other CLIs, or tasks not meant for delegation.
---

# Grok Build Delegate

Run Grok Build as a bounded headless subprocess and hand its final response back to the user. Keep the current project as the working directory unless the user specifies another directory.

## Anti-Rationalization

Trigger this skill when the user explicitly asks for Grok Build, `grok`, an xAI-backed second opinion, or a comparison that needs Grok evidence. Do not skip it just because another model can answer; the requested value is the separate Grok Build run.

Pause instead when Grok Build is missing or unauthenticated, the user wants an interactive session, the task requires exposing secrets, or the requested approval mode exceeds the user's authorization.

## Runtime Pre-Flight

Read [runtime-setup.md](references/runtime-setup.md) before invoking the wrapper. Verify Python 3.10+ and `grok` or `GROK_BIN`; stop and report the missing prerequisite instead of inventing an installer or assuming a specific shell.

## Workflow

1. Clarify the delegated objective, scope, and whether Grok may edit files or run commands. Do not delegate secrets or expose protected files in the prompt.
2. Resolve the project directory to an absolute path. Prefer the current working directory. Verify it exists before starting.
3. Run the bundled wrapper with the Python command discovered by [runtime-setup.md](references/runtime-setup.md).
4. Read [headless-reference.md](references/headless-reference.md) when flags, sessions, output parsing, or authentication details are needed.

5. Report the wrapper's result, output-file path, exit status, and any stderr warning. A successful process is not proof that the requested change is correct: inspect the diff and run relevant tests independently when the delegated task changed files.
6. If the task is long-running, use a generous explicit timeout. Never create a hidden daemon, polling loop, or unbounded background process.

## Wrapper behavior

- `delegate_grok.py` invokes `grok` directly, never through a shell, and supports `GROK_BIN` for an explicit executable path.
- It uses Grok Build headless mode with `-p`, `--cwd`, `--output-format json`, and `--no-auto-update`; it adds `--always-approve` or project `--trust` only when requested.
- It writes stdout, stderr, and a small result manifest to a temporary output directory, then prints the final captured response as JSON.
- It returns nonzero for missing Grok, an invalid project directory, timeout, failed process, or malformed JSON. Do not hide these failures.
- Prefer a one-shot invocation. Use `--session-id` only when the user explicitly asks for a resumable Grok session.

## Safety and verification

- Do not read or print `XAI_API_KEY`, OAuth tokens, `~/.grok` credentials, `.env*`, private keys, or browser profiles.
- Do not add MCP servers, disable repository protections, publish code, push commits, or delete data unless the user explicitly asks for that exact action.
- Treat Grok's report as unverified. Inspect changed files, `git diff`, and tests from the controlling agent.
- If `grok` is not found, tell the user to verify the official installation and PATH; do not install packages or run an installer automatically.

## Resources

Use `references/runtime-setup.md` for Python and CLI pre-flight, `scripts/delegate_grok.py` for deterministic invocation, and `references/headless-reference.md` for the documented Grok Build interface.
