# Runtime setup

Use this check before running `scripts/delegate_grok.py`. The wrapper requires Python 3.10+ and an installed/authenticated Grok Build CLI.

## POSIX shell: macOS, Linux, WSL

```sh
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=python
else
  echo "FAIL: Python 3.10+ not found"
  exit 127
fi

"$PYTHON_CMD" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' || {
  echo "FAIL: Python 3.10+ required"
  exit 127
}

command -v grok >/dev/null 2>&1 || [ -n "${GROK_BIN:-}" ] || {
  echo "FAIL: grok not found; set GROK_BIN or update PATH"
  exit 127
}

"$PYTHON_CMD" "<skill-dir>/scripts/delegate_grok.py" \
  --cwd "<absolute-project-path>" \
  --task "<delegated task>" \
  --timeout 45m
```

## Windows PowerShell

```powershell
$PythonExe = $null
$PythonArgs = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
  $PythonExe = "py"
  $PythonArgs = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $PythonExe = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
  $PythonExe = "python3"
} else {
  throw "Python 3.10+ not found"
}

& $PythonExe @PythonArgs -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) { throw "Python 3.10+ required" }

if (-not $env:GROK_BIN -and -not (Get-Command grok -ErrorAction SilentlyContinue)) {
  throw "grok not found; set GROK_BIN or update PATH"
}

& $PythonExe @PythonArgs "<skill-dir>\scripts\delegate_grok.py" `
  --cwd "<absolute-project-path>" `
  --task "<delegated task>" `
  --timeout 45m
```
