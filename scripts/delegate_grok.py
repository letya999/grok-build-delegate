#!/usr/bin/env python3
"""Run Grok Build once in headless mode and capture its result."""

from __future__ import annotations

import argparse
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_bounded(command: list[str], cwd: Path, timeout: float) -> subprocess.CompletedProcess[str]:
    """Run in a process group so a timeout can terminate the whole CLI tree."""
    group_options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True})
    process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", **group_options)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        else:
            os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        exc.stdout, exc.stderr = stdout, stderr
        raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def parse_duration(value: str) -> float:
    value = value.strip().lower()
    units = {"s": 1, "m": 60, "h": 3600}
    if value[-1:] in units:
        seconds = float(value[:-1]) * units[value[-1]]
    else:
        seconds = float(value)
    if seconds <= 0:
        raise ValueError("timeout must be greater than zero")
    return seconds


def find_grok() -> str | None:
    explicit = os.environ.get("GROK_BIN")
    if explicit:
        return explicit
    found = shutil.which("grok")
    if found:
        return found
    for candidate in (Path.home() / ".grok" / "bin" / "grok.exe", Path.home() / ".grok" / "bin" / "grok"):
        if candidate.is_file():
            return str(candidate)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", required=True, help="Absolute project directory")
    parser.add_argument("--task", required=True, help="Task to delegate")
    parser.add_argument("--timeout", default="45m", help="Timeout, e.g. 90s, 45m, 2h")
    parser.add_argument("--model", help="Optional Grok model")
    parser.add_argument("--json-schema", help="Optional JSON Schema for structured output")
    parser.add_argument("--max-turns", type=int, help="Optional maximum number of agent turns")
    parser.add_argument("--session-id", help="Optional resumable headless session id")
    parser.add_argument("--always-approve", action="store_true", help="Approve Grok tool executions")
    parser.add_argument("--trust", action="store_true", help="Trust the project for repo-local MCP, hooks, and plugins")
    parser.add_argument("--output-dir", help="Directory for captured output")
    args = parser.parse_args()

    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        print(f"error: project directory does not exist: {cwd}", file=sys.stderr)
        return 2

    grok = find_grok()
    if not grok:
        print("error: grok executable not found; set GROK_BIN or add grok to PATH", file=sys.stderr)
        return 127
    if not Path(grok).is_file():
        resolved = shutil.which(grok)
        if not resolved:
            print("error: grok executable not found; set GROK_BIN or add grok to PATH", file=sys.stderr)
            return 127
        grok = resolved

    try:
        timeout = parse_duration(args.timeout)
    except (TypeError, ValueError) as exc:
        parser.error(f"invalid --timeout: {exc}")

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="grok-build-delegate-"))
    output_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = output_dir / "stdout.json"
    stderr_path = output_dir / "stderr.log"
    manifest_path = output_dir / "result.json"

    command = [grok, "--no-auto-update", "-p", args.task, "--cwd", str(cwd), "--output-format", "json", "--no-alt-screen"]
    if args.model:
        command.extend(["--model", args.model])
    if args.json_schema:
        command.extend(["--json-schema", args.json_schema])
    if args.max_turns is not None:
        if args.max_turns <= 0:
            parser.error("--max-turns must be greater than zero")
        command.extend(["--max-turns", str(args.max_turns)])
    if args.session_id:
        command.extend(["--session-id", args.session_id])
    if args.always_approve:
        command.append("--always-approve")
    if args.trust:
        command.append("--trust")

    try:
        completed = run_bounded(command, cwd, timeout)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        stdout_path.write_text(stdout if isinstance(stdout, str) else stdout.decode("utf-8", "replace"), encoding="utf-8")
        stderr_path.write_text(stderr if isinstance(stderr, str) else stderr.decode("utf-8", "replace"), encoding="utf-8")
        manifest = {"tool": "grok", "cwd": str(cwd), "exit_code": 124, "timed_out": True, "output_dir": str(output_dir), "stdout": str(stdout_path), "stderr": str(stderr_path)}
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        print(f"error: Grok timed out after {args.timeout}; output: {output_dir}", file=sys.stderr)
        return 124
    except OSError as exc:
        print(f"error: could not start Grok: {exc}", file=sys.stderr)
        return 126

    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    manifest = {"tool": "grok", "cwd": str(cwd), "exit_code": completed.returncode, "output_dir": str(output_dir), "stdout": str(stdout_path), "stderr": str(stderr_path)}
    try:
        payload = json.loads(completed.stdout)
        if isinstance(payload, dict):
            manifest["response"] = next((payload[key] for key in ("structuredOutput", "result", "response", "content", "text", "output", "message") if key in payload), payload)
        else:
            manifest["response"] = payload
        manifest["raw"] = payload
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    except json.JSONDecodeError:
        manifest["parse_error"] = "Grok did not return one JSON object"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"error: Grok returned invalid JSON; raw output: {stdout_path}", file=sys.stderr)
        return 65 if completed.returncode == 0 else completed.returncode

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
