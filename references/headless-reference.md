# Grok Build headless reference

This skill follows xAI's Grok Build documentation (checked 2026-08-06):

- Headless invocation: `grok -p "..."`
- Working directory: `--cwd <PATH>`
- Machine-readable output: `--output-format json` (one JSON object at the end)
- Streaming alternative: `--output-format streaming-json` (NDJSON events)
- Model selection: `--model <MODEL>`
- Resumable sessions: `--session-id <ID>`, `--resume <ID>`, or `--continue`
- Automated execution: `--always-approve`
- Avoid fullscreen takeover: `--no-alt-screen`
- Avoid background update checks in scripts: `--no-auto-update`

Authentication is expected to be preconfigured by the user through Grok login or `XAI_API_KEY`. Never inspect or print credentials. If authentication fails, return Grok's error and ask the user to authenticate separately.

Primary sources:

- [xAI Headless & Scripting](https://docs.x.ai/build/cli/headless-scripting)
- [xAI Grok Build overview](https://docs.x.ai/build/overview)
- [xAI Grok Build repository](https://github.com/xai-org/grok-build)
