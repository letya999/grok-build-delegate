# Grok Build Delegate

Headless Grok Build CLI delegate skill by [Artem Letyushev](https://github.com/letya999).

This repository packages a cross-platform agent skill that lets a controlling agent run Grok Build once, non-interactively, capture the result as JSON, and verify the work outside the delegated agent.

## What It Does

- Runs `grok -p` through `scripts/delegate_grok.py`
- Captures stdout, stderr, exit code, output files, and the final response
- Supports macOS, Linux, WSL, and Windows
- Uses `GROK_BIN` when the executable is not on `PATH`
- Disables auto-update checks for scripted runs
- Keeps delegated output untrusted until the controlling agent checks diffs and tests

## Install

With `npx skills`:

```sh
npx skills add letya999/grok-build-delegate
```

Or copy this repository into an agent skill directory such as `.agents/skills/`, `.grok/skills/`, or `~/.codex/skills/`.

## Quick Start

```sh
python3 scripts/delegate_grok.py \
  --cwd "$PWD" \
  --task "Review this repository and report the highest-risk issue." \
  --timeout 45m
```

Windows users can run the same wrapper with `py -3`. See [QUICKSTART.md](QUICKSTART.md) and [references/runtime-setup.md](references/runtime-setup.md) for the full cross-platform pre-flight.

## Agent Skill Entry Points

- [SKILL.md](SKILL.md) is the skill instruction file.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) is the discovery index.
- [dist/grok-build-delegate.zip](dist/grok-build-delegate.zip) is the archive artifact referenced by the index.

## License

MIT License. See [LICENSE](LICENSE).
