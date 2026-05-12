param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ToolArgs
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "extract_song_clip.py"

if (-not (Test-Path -LiteralPath $PythonScript)) {
    Write-Error "Cannot find $PythonScript"
    exit 1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Cannot find python in PATH."
    exit 1
}

if (($ToolArgs -contains "--help") -or ($ToolArgs -contains "-h")) {
    & python $PythonScript @ToolArgs
    exit $LASTEXITCODE
}

foreach ($Tool in @("ffmpeg", "ffprobe")) {
    if (-not (Get-Command $Tool -ErrorAction SilentlyContinue)) {
        Write-Error "Cannot find $Tool in PATH. Install ffmpeg first, then reopen PowerShell."
        exit 1
    }
}

& python $PythonScript @ToolArgs
exit $LASTEXITCODE
