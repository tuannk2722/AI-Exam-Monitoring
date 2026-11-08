param(
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$DeleteBy,
    [string]$Artifacts,
    [switch]$ConfirmSourceRights,
    [switch]$NotTestOrHoldout
)
$ErrorActionPreference = 'Stop'
if (-not $ConfirmSourceRights -or -not $NotTestOrHoldout) {
    throw 'Confirm local source rights and non-holdout scope before starting.'
}
$taskPython = (Resolve-Path -LiteralPath $Python).Path
$taskSource = (Resolve-Path -LiteralPath $Source).Path
$taskArtifacts = if ($Artifacts) { (Resolve-Path -LiteralPath $Artifacts).Path } else { $null }
$taskLocation = (Get-Location).Path
$taskPath = [Environment]::GetEnvironmentVariable('PYTHONPATH', 'Process')
$taskBytecode = [Environment]::GetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', 'Process')
try {
    Set-Location -LiteralPath $PSScriptRoot
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'src'
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $taskRestoreArgs = @('--workspace', '.')
    if ($taskArtifacts) { $taskRestoreArgs += @('--archive', $taskArtifacts) }
    & $taskPython -B -m ai_exam_monitoring.web.bundle restore @taskRestoreArgs
    if ($LASTEXITCODE -ne 0) { throw 'Model inputs missing or changed; use -Artifacts with video-web.zip.' }
    & $taskPython -B -m ai_exam_monitoring.web.bundle check --workspace .
    if ($LASTEXITCODE -ne 0) { throw 'GPU/package preflight failed; do not replace Torch.' }
    & $taskPython -B -m ai_exam_monitoring.web.bundle deps --workspace .
    if ($LASTEXITCODE -ne 0) {
        & $taskPython -B -m pip install --disable-pip-version-check --no-deps `
            -r requirements/video-web.txt
        if ($LASTEXITCODE -ne 0) { throw 'Web dependencies failed to install.' }
    }
    & $taskPython -B -m ai_exam_monitoring.web.bundle check --workspace . --web
    if ($LASTEXITCODE -ne 0) { throw 'Web preflight failed.' }
    & $taskPython -B -m ai_exam_monitoring.web.bundle receipt --workspace . `
        --source $taskSource --delete-by $DeleteBy --rights-confirmed --not-test-or-holdout
    if ($LASTEXITCODE -ne 0) { throw 'Source receipt failed; preserve the original deadline.' }
    Write-Host 'Open http://127.0.0.1:8765 and upload the MP4 plus the printed receipt JSON.'
    & $taskPython -B -m ai_exam_monitoring.web --workspace .
    if ($LASTEXITCODE -ne 0) { throw 'Video web server stopped with an error.' }
} finally {
    [Environment]::SetEnvironmentVariable('PYTHONPATH', $taskPath, 'Process')
    [Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', $taskBytecode, 'Process')
    Set-Location -LiteralPath $taskLocation
}
