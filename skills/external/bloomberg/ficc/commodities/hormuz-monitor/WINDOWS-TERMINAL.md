# Windows Terminal Setup

This file shows how to run `hormuz-monitor` from Windows Terminal with Git Bash.

## 1. Verify Git Bash

Run this in PowerShell:

```powershell
Test-Path 'C:\Program Files\Git\bin\bash.exe'
```

Expected result:

```text
True
```

## 2. Add a Git Bash profile to Windows Terminal

Open Windows Terminal settings with `Ctrl+,`, then open `settings.json`.

Add this object to `profiles.list`:

```json
{
  "guid": "{b7c9e7d2-7b2f-4d8d-9b2f-1d9e8c4a1001}",
  "name": "Git Bash",
  "commandline": "\"C:\\Program Files\\Git\\bin\\bash.exe\" -li",
  "startingDirectory": "C:\\Users\\Q\\Code\\quinn-awesome-skills",
  "icon": "C:\\Program Files\\Git\\mingw64\\share\\git\\git-for-windows.ico"
}
```

If you already have a Git Bash profile, just update `startingDirectory` to:

```text
C:\Users\Q\Code\quinn-awesome-skills
```

Full copy-paste example:

```json
{
  "$schema": "https://aka.ms/terminal-profiles-schema",
  "defaultProfile": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
  "profiles": {
    "defaults": {},
    "list": [
      {
        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
        "name": "Windows PowerShell",
        "commandline": "powershell.exe"
      },
      {
        "guid": "{b7c9e7d2-7b2f-4d8d-9b2f-1d9e8c4a1001}",
        "name": "Git Bash",
        "commandline": "\"C:\\Program Files\\Git\\bin\\bash.exe\" -li",
        "startingDirectory": "C:\\Users\\Q\\Code\\quinn-awesome-skills",
        "icon": "C:\\Program Files\\Git\\mingw64\\share\\git\\git-for-windows.ico"
      }
    ]
  }
}
```

## 3. Open a Git Bash tab

After saving `settings.json`, open a new `Git Bash` tab in Windows Terminal.

## 4. Run the skill

From the repo root:

```bash
bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --help
```

Common commands:

```bash
bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --all
bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --transit --period 24h
bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --types
bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --queue
bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --cache
bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --raw-cache
python skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-analysis.py --summary
python skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-analysis.py --briefing
python skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-analysis.py --vars
```

## 5. Live API configuration

If you want to call the live MarineTraffic API, set these in Git Bash first:

```bash
export MARINETRAFFIC_API_KEY="your_key"
export MARINETRAFFIC_URL_STYLE="path"
export MARINETRAFFIC_PROTOCOL="json"
export MARINETRAFFIC_MSGTYPE="extended"
```

Then run:

```bash
bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --transit --period 24h
```

Notes:
- `MARINETRAFFIC_URL_STYLE=path` matches common official examples more closely.
- If your API product expects query-style URLs, switch it to `query`.
- Raw provider responses are saved to `~/.cache/hormuz-monitor/latest.raw.json`.
- Normalized downstream cache is saved to `~/.cache/hormuz-monitor/latest.json`.

## 6. PowerShell one-shot alternative

If you do not want to add a Windows Terminal profile, run Git Bash directly from PowerShell:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -lc 'cd /c/Users/Q/Code/quinn-awesome-skills && bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --help'
```

Live API example:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -lc 'export MARINETRAFFIC_API_KEY="your_key"; export MARINETRAFFIC_URL_STYLE="path"; export MARINETRAFFIC_PROTOCOL="json"; export MARINETRAFFIC_MSGTYPE="extended"; cd /c/Users/Q/Code/quinn-awesome-skills && bash skills/external/bloomberg/ficc/commodities/hormuz-monitor/scripts/hormuz-tracker.sh --transit --period 24h'
```

## 7. PowerShell helper script

There is also a ready-to-run helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -Help
```

Examples:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -TrackerArgs '--all'
powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -TrackerArgs '--transit --period 24h'
powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -AnalysisArgs '--summary'
powershell -ExecutionPolicy Bypass -File .\skills\external\bloomberg\ficc\commodities\hormuz-monitor\run-hormuz.ps1 -TrackerArgs '--transit --period 24h' -MarineTrafficApiKey 'your_key'
```
