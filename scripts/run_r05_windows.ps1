<#
.SYNOPSIS
    R05 full evaluation pipeline for Windows — predict → report → finalize → notebooks.
    Prevents sleep, shows live progress, generates per-fold HTML notebooks sequentially.

.USAGE
    From repo root in PowerShell (as Administrator or with execution policy set):
        powershell -ExecutionPolicy Bypass -File scripts\run_r05_windows.ps1

    Optional: resume an existing run by passing its directory name:
        powershell -ExecutionPolicy Bypass -File scripts\run_r05_windows.ps1 -RunDir artifacts\20261012T134149Z-R05
#>

param(
    [string]$RunDir = ""   # leave blank to start a NEW run
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── paths ──────────────────────────────────────────────────────────────────────
$Root      = Split-Path -Parent $PSScriptRoot          # repo root
$Python    = Join-Path $Root ".venv\Scripts\python.exe"
$EvalScript= Join-Path $Root "scripts\evaluate_replay.py"
$NbDir     = Join-Path $Root "notebooks"

# ── sanity checks ──────────────────────────────────────────────────────────────
if (-not (Test-Path $Python)) {
    Write-Error "Python venv not found at $Python — run setup first (see planning/prompts/windows_setup.md)"
    exit 1
}
if (-not (Test-Path $EvalScript)) {
    Write-Error "evaluate_replay.py not found. Are you in the repo root?"
    exit 1
}

# ── prevent Windows sleep for the duration of the script ──────────────────────
Write-Host "[SETUP] Disabling sleep via powercfg..." -ForegroundColor Cyan
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
# Also keep the process alive using SetThreadExecutionState via a background job
$WakeJob = Start-Job -ScriptBlock {
    Add-Type -TypeDefinition @"
        using System;
        using System.Runtime.InteropServices;
        public class Sleep {
            [DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);
            public const uint ES_CONTINUOUS       = 0x80000000;
            public const uint ES_SYSTEM_REQUIRED  = 0x00000001;
            public const uint ES_DISPLAY_REQUIRED = 0x00000002;
        }
"@
    [Sleep]::SetThreadExecutionState([Sleep]::ES_CONTINUOUS -bor [Sleep]::ES_SYSTEM_REQUIRED) | Out-Null
    while ($true) { Start-Sleep -Seconds 30 }
}
Write-Host "[SETUP] Sleep prevention active (job id $($WakeJob.Id))" -ForegroundColor Green

# ── helper: pretty timestamp ───────────────────────────────────────────────────
function ts { Get-Date -Format "HH:mm:ss" }

# ── helper: run a phase and stream output with progress lines highlighted ──────
function Invoke-Phase {
    param([string]$Phase, [string]$Run, [string]$Label)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor DarkCyan
    Write-Host "  [$(ts)] PHASE: $Label" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor DarkCyan

    $env:VP_RUN_DIR = $Run
    $proc = Start-Process -FilePath $Python `
        -ArgumentList $EvalScript, "--run", $Run, "--phase", $Phase `
        -NoNewWindow -PassThru -RedirectStandardOutput "$Run\phase_$Phase.stdout.log" `
        -RedirectStandardError  "$Run\phase_$Phase.stderr.log"

    # Tail the predict.log (or execution.log) live while the process runs
    $logFile = if ($Phase -eq "predict") { "$Run\predict.log" } else { "$Run\execution.log" }
    $lastPos = 0
    $spinner = @("|", "/", "-", "\")
    $spin    = 0

    while (-not $proc.HasExited) {
        Start-Sleep -Milliseconds 500
        if (Test-Path $logFile) {
            $content = Get-Content $logFile -Raw -Encoding UTF8 2>$null
            if ($content -and $content.Length -gt $lastPos) {
                $newText = $content.Substring($lastPos)
                $lastPos = $content.Length
                foreach ($line in ($newText -split "`n")) {
                    $line = $line.Trim()
                    if (-not $line) { continue }
                    if ($line -match "episode complete") {
                        # Parse episode progress e.g. "F0 episode 5/62 complete"
                        Write-Host "  ✓ $line" -ForegroundColor Green
                    } elseif ($line -match "episode \d+/\d+") {
                        Write-Host "  ► $line" -ForegroundColor Yellow
                    } elseif ($line -match "FAILED|ERROR|error") {
                        Write-Host "  ✗ $line" -ForegroundColor Red
                    } elseif ($line -match "complete|PASS|sealed|usable|USABLE") {
                        Write-Host "  ✓ $line" -ForegroundColor Green
                    } else {
                        Write-Host "    $line" -ForegroundColor Gray
                    }
                }
            }
        }
        $spin = ($spin + 1) % 4
        Write-Host -NoNewline "`r  [$(ts)] $($spinner[$spin]) Running $Label..." -ForegroundColor DarkYellow
    }
    Write-Host ""  # newline after spinner

    if ($proc.ExitCode -ne 0) {
        Write-Host "  [ERROR] Phase '$Phase' exited with code $($proc.ExitCode)" -ForegroundColor Red
        Write-Host "  Check: $Run\phase_$Phase.stderr.log" -ForegroundColor Red
        Get-Content "$Run\phase_$Phase.stderr.log" -Tail 20 | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkRed }
        throw "Phase '$Phase' failed. Aborting."
    }
    Write-Host "  [$(ts)] ✓ Phase '$Label' complete." -ForegroundColor Green
}

# ── helper: execute one notebook with env vars, output executed .ipynb + HTML ──
function Invoke-Notebook {
    param(
        [string]$NotebookPath,
        [string]$OutputBase,
        [hashtable]$EnvVars,
        [string]$Label
    )
    Write-Host ""
    Write-Host "  [$(ts)] 📓 Executing notebook: $Label" -ForegroundColor Cyan

    # Set env vars for child process
    $savedEnv = @{}
    foreach ($kv in $EnvVars.GetEnumerator()) {
        $savedEnv[$kv.Key] = [System.Environment]::GetEnvironmentVariable($kv.Key)
        [System.Environment]::SetEnvironmentVariable($kv.Key, $kv.Value)
    }

    try {
        $nbOut  = "$OutputBase.ipynb"
        $htmlOut= "$OutputBase.html"

        # Execute notebook → .ipynb
        & $Python -m jupyter nbconvert `
            --to notebook `
            --execute `
            --ExecutePreprocessor.timeout=600 `
            --output $nbOut `
            $NotebookPath
        if ($LASTEXITCODE -ne 0) { throw "nbconvert execute failed for $Label" }

        # Convert executed .ipynb → .html
        & $Python -m jupyter nbconvert --to html $nbOut
        if ($LASTEXITCODE -ne 0) { throw "nbconvert html failed for $Label" }

        Write-Host "  [$(ts)] ✓ Notebook done → $htmlOut" -ForegroundColor Green
    } finally {
        # Restore env vars
        foreach ($kv in $savedEnv.GetEnumerator()) {
            [System.Environment]::SetEnvironmentVariable($kv.Key, $kv.Value)
        }
    }
}

# ── MAIN ───────────────────────────────────────────────────────────────────────
try {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         VALID POINT — R05 Windows Evaluation Pipeline               ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "  Repo   : $Root"
    Write-Host "  Python : $Python"
    Write-Host "  Time   : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""

    # ── determine run directory ────────────────────────────────────────────────
    if ($RunDir -ne "") {
        # Resume existing run
        $Run = if ([System.IO.Path]::IsPathRooted($RunDir)) { $RunDir } `
               else { Join-Path $Root $RunDir }
        if (-not (Test-Path $Run)) {
            Write-Error "Run directory not found: $Run"
            exit 1
        }
        Write-Host "[RESUME] Using existing run: $Run" -ForegroundColor Yellow

        # Check what phases are already done
        $predictDone  = (Test-Path "$Run\prediction_seal.json")
        $reportDone   = (Test-Path "$Run\T_R05_metrics.csv")
        $finalizeDone = (Test-Path "$Run\gate.md")
    } else {
        # New run — run intake first, which creates the run directory
        Write-Host "[NEW RUN] Starting fresh R05 run..." -ForegroundColor Cyan
        $Run = $null
        $predictDone  = $false
        $reportDone   = $false
        $finalizeDone = $false
    }

    # ── PHASE: intake (only for new runs) ─────────────────────────────────────
    if ($Run -eq $null) {
        Write-Host ""
        Write-Host "[$(ts)] Running INTAKE phase to initialize run directory..." -ForegroundColor Cyan
        $env:VP_RUN_DIR = ""
        $intakeOut = & $Python $EvalScript --phase intake 2>&1
        # Extract the run directory from output (run_stage returns the path)
        $Run = ($intakeOut | Where-Object { $_ -match "artifacts[\\/]" } | Select-Object -Last 1).Trim()
        if (-not $Run -or -not (Test-Path $Run)) {
            # fallback: find newest R05 dir
            $Run = Get-ChildItem (Join-Path $Root "artifacts") -Directory |
                   Where-Object { $_.Name -match "R05" } |
                   Sort-Object LastWriteTime -Descending |
                   Select-Object -First 1 -ExpandProperty FullName
        }
        Write-Host "[$(ts)] ✓ Run directory: $Run" -ForegroundColor Green
        $predictDone  = $false
        $reportDone   = $false
        $finalizeDone = $false
    }

    Write-Host ""
    Write-Host "[INFO] Run directory: $Run" -ForegroundColor White

    # ── PHASE: predict ────────────────────────────────────────────────────────
    if (-not $predictDone) {
        Write-Host ""
        Write-Host "[$(ts)] Starting PREDICT phase. This takes several hours." -ForegroundColor Yellow
        Write-Host "         Progress is shown live below. Do not close this window." -ForegroundColor Yellow
        Invoke-Phase -Phase "predict" -Run $Run -Label "Predict (all 4 folds × 62 episodes)"
    } else {
        Write-Host "[SKIP] Predict already complete (prediction_seal.json exists)." -ForegroundColor Green
    }

    # ── PHASE: report ─────────────────────────────────────────────────────────
    if (-not $reportDone) {
        Invoke-Phase -Phase "report" -Run $Run -Label "Report (CSVs + figures)"
    } else {
        Write-Host "[SKIP] Report already complete (T_R05_metrics.csv exists)." -ForegroundColor Green
    }

    # ── PHASE: finalize ───────────────────────────────────────────────────────
    if (-not $finalizeDone) {
        Invoke-Phase -Phase "finalize" -Run $Run -Label "Finalize (gate.md + history)"
    } else {
        Write-Host "[SKIP] Finalize already complete (gate.md exists)." -ForegroundColor Green
    }

    # ── install nbconvert if missing ──────────────────────────────────────────
    Write-Host ""
    Write-Host "[$(ts)] Checking nbconvert..." -ForegroundColor Cyan
    $nbCheck = & $Python -c "import nbconvert; print('ok')" 2>&1
    if ($nbCheck -ne "ok") {
        Write-Host "  Installing nbconvert..." -ForegroundColor Yellow
        & $Python -m pip install --quiet nbconvert
        Write-Host "  ✓ nbconvert installed." -ForegroundColor Green
    } else {
        Write-Host "  ✓ nbconvert already installed." -ForegroundColor Green
    }

    # ── NOTEBOOKS: per-segment timelines (one per fold, sequential) ───────────
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor DarkCyan
    Write-Host "  [$(ts)] NOTEBOOKS: Per-segment timelines + grouped evaluation" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor DarkCyan

    $segments = @("C0", "C1", "C2", "C3")
    foreach ($seg in $segments) {
        $outBase = Join-Path $Run "R05_segment_timelines_${seg}_executed"
        if (Test-Path "$outBase.html") {
            Write-Host "  [SKIP] Segment $seg notebook already done." -ForegroundColor DarkGreen
            continue
        }
        Invoke-Notebook `
            -NotebookPath (Join-Path $NbDir "R05_segment_timelines.ipynb") `
            -OutputBase $outBase `
            -EnvVars @{ VP_RUN_DIR = $Run; VP_SEGMENT = $seg } `
            -Label "R05_segment_timelines — $seg"
    }

    # ── NOTEBOOK: grouped evaluation ─────────────────────────────────────────
    $grpBase = Join-Path $Run "R05_grouped_evaluation_executed"
    if (Test-Path "$grpBase.html") {
        Write-Host "  [SKIP] Grouped evaluation notebook already done." -ForegroundColor DarkGreen
    } else {
        Invoke-Notebook `
            -NotebookPath (Join-Path $NbDir "R05_grouped_evaluation.ipynb") `
            -OutputBase $grpBase `
            -EnvVars @{ VP_RUN_DIR = $Run } `
            -Label "R05_grouped_evaluation"
    }

    # ── DONE ──────────────────────────────────────────────────────────────────
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Green
    Write-Host "  [$(ts)] ✓ R05 COMPLETE" -ForegroundColor Green
    Write-Host ("=" * 70) -ForegroundColor Green
    Write-Host ""
    Write-Host "  Outputs in: $Run" -ForegroundColor White
    Write-Host ""
    Write-Host "  Opening results..." -ForegroundColor Cyan
    $htmlFiles = Get-ChildItem $Run -Filter "*.html" | Sort-Object Name
    foreach ($f in $htmlFiles) {
        Write-Host "    → $($f.Name)" -ForegroundColor White
    }
    Write-Host ""
    Start-Process (Join-Path $Run "R05_grouped_evaluation_executed.html")

} finally {
    # ── restore sleep settings ────────────────────────────────────────────────
    Write-Host ""
    Write-Host "[CLEANUP] Restoring sleep settings..." -ForegroundColor DarkGray
    Stop-Job $WakeJob -ErrorAction SilentlyContinue
    Remove-Job $WakeJob -ErrorAction SilentlyContinue
    powercfg /change standby-timeout-ac 30
    powercfg /change monitor-timeout-ac 15
    Write-Host "[CLEANUP] Sleep settings restored." -ForegroundColor DarkGray
}
