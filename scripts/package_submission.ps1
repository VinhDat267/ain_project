<#
.SYNOPSIS
    Package the Final Submission archive (<PREFIX>.zip) per AIN_Submission_Guide.pdf.
.DESCRIPTION
    Creates <PREFIX>.zip with a single root directory <PREFIX>/ containing:
      - slides/<PREFIX>_midterm_slides.pdf
      - code/  (clean git archive export from HEAD)
      - report/<PREFIX>_report.docx
    Uses POSIX forward-slash zip entries so the archive extracts cleanly on Windows,
    macOS, and Linux, and checks for forbidden artifacts and the 50 MB size guideline.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\package_submission.ps1 -ClassCode 61FIT3AIN-TUT02 -Group 07
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "61FIT3AIN-TUT01", "61FIT3AIN-TUT02",
        "66FIT3AIN-TT02", "66FIT3AIN-TT03",
        "62FIT4ATI-CLC02", "62FIT4ATI-CLC03"
    )]
    [string]$ClassCode,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^\d{2}$")]
    [string]$Group,

    [string]$Project = "P12",
    [string]$GitRef = "HEAD",
    [string]$OutputZip = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Prefix = "${ClassCode}_G${Group}_${Project}"
if (-not $OutputZip) {
    $OutputZip = Join-Path $RepoRoot "${Prefix}.zip"
}

$SlidesSrc = Join-Path $RepoRoot "presentation\presentation_en.pdf"
$ReportSrc = Join-Path $RepoRoot "report\${Prefix}_report.docx"

if (-not (Test-Path $SlidesSrc)) {
    throw "Missing English midterm slides PDF: $SlidesSrc"
}
if (-not (Test-Path $ReportSrc)) {
    throw "Missing final Word report: $ReportSrc (run python report/build_final_report.py --class-code $ClassCode --group $Group and report/finalize_report.ps1 first)"
}

$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$StageParent = Join-Path $env:TEMP ("ain_pkg_" + [guid]::NewGuid().ToString("N"))
$StageRoot = Join-Path $StageParent $Prefix
$CodeArchive = Join-Path $StageParent "code.zip"

try {
    New-Item -ItemType Directory -Path (Join-Path $StageRoot "slides") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $StageRoot "code") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $StageRoot "report") -Force | Out-Null

    Copy-Item -Path $SlidesSrc -Destination (Join-Path $StageRoot "slides\${Prefix}_midterm_slides.pdf") -Force
    Copy-Item -Path $ReportSrc -Destination (Join-Path $StageRoot "report\${Prefix}_report.docx") -Force

    Push-Location $RepoRoot
    try {
        git archive --format=zip --output="$CodeArchive" $GitRef
        if ($LASTEXITCODE -ne 0) { throw "git archive failed for ref $GitRef" }
    }
    finally {
        Pop-Location
    }

    $PackScript = Join-Path $StageParent "pack_submission.py"
    $PyCode = @'
import os
import sys
import zipfile
from pathlib import Path

code_zip = Path(sys.argv[1])
code_dir = Path(sys.argv[2])
stage_parent = Path(sys.argv[3])
prefix = sys.argv[4]
out_zip = Path(sys.argv[5])

with zipfile.ZipFile(code_zip, "r") as zf:
    zf.extractall(code_dir)

forbidden_parts = {
    ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    ".ipynb_checkpoints", ".git", ".idea", ".vscode", "node_modules", "__MACOSX",
}
forbidden_files = {".DS_Store", ".env"}
forbidden_suffixes = {".pyc", ".pyo", ".h5", ".pt", ".pkl", ".ckpt"}

stage_root = stage_parent / prefix
if out_zip.exists():
    out_zip.unlink()

entries = []
with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
    # Write explicit root directory entry first so unzip -l shows <PREFIX>/ on line 1.
    out.writestr(f"{prefix}/", "")
    for root, dirs, files in os.walk(stage_root):
        dirs.sort()
        files.sort()
        rel_dir = Path(root).relative_to(stage_parent)
        if rel_dir != Path(prefix):
            out.writestr(rel_dir.as_posix() + "/", "")
        for name in files:
            full = Path(root) / name
            rel = full.relative_to(stage_parent)
            parts = set(rel.parts)
            if parts & forbidden_parts or name in forbidden_files or full.suffix.lower() in forbidden_suffixes:
                raise SystemExit(f"Forbidden artifact detected in package: {rel.as_posix()}")
            if "DRAFT" in name:
                raise SystemExit(f"Draft artifact detected in package: {rel.as_posix()}")
            arcname = rel.as_posix()
            out.write(full, arcname)
            entries.append(arcname)

size_mb = out_zip.stat().st_size / (1024 * 1024)
print(f"Created: {out_zip}")
print(f"Files packaged: {len(entries)} | Size: {size_mb:.2f} MB")
if size_mb >= 50.0:
    raise SystemExit(f"Archive exceeds 50 MB guideline ({size_mb:.2f} MB)")
'@
    Set-Content -Path $PackScript -Value $PyCode -Encoding UTF8
    & $PythonExe $PackScript $CodeArchive (Join-Path $StageRoot "code") $StageParent $Prefix $OutputZip

    if ($LASTEXITCODE -ne 0) { throw "Packaging verification failed" }
}
finally {
    if (Test-Path $StageParent) {
        Remove-Item -Path $StageParent -Recurse -Force -ErrorAction SilentlyContinue
    }
}
