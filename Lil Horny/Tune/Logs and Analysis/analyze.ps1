# Analyze a 3D whoop blackbox log end-to-end.
# usage:  .\analyze.ps1 "Pass 2.BBL" "Pass 2"
#         .\analyze.ps1 "Pass 2.BBL#5" "Pass 2 log5"   (pick one log of a multi-log file;
#         run tools\list_logs.py first to see them)
param([Parameter(Mandatory)][string]$Log, [string]$Label = "")
$ErrorActionPreference = "Continue"
$root = $PSScriptRoot
$py = Join-Path $root ".venv\Scripts\python.exe"
$env:PYTHONPATH = "C:\Users\Admin\Documents\Tuning\orangebox-0.5.0;$root\tools"
if (-not $Label) { $Label = [IO.Path]::GetFileNameWithoutExtension($Log) }
$tag = ($Label -replace '[^\w\-]', '_')
New-Item -ItemType Directory -Force (Join-Path $root "reports") | Out-Null

& $py "$root\tools\bbl_headers.py" $Log > "$root\reports\${tag}_headers.txt"
& $py "$root\tools\poles_check.py" $Log
& $py "$root\tools\reversals.py" $Log --plot "$root\reports\${tag}_worst_reversals.png"
& $py "$root\tools\noise_step.py" $Log "$root\reports\$tag"
& $py "$root\tools\scorecard.py" $Log $Label
