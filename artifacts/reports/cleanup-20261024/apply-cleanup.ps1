# One-time exact-manifest cleanup, authorized by owner on 2026-10-24.
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$cleanupRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$manifestPath = Join-Path $PSScriptRoot 'cleanup-manifest.json'
$receiptPath = Join-Path $PSScriptRoot 'cleanup-result.json'
if (Test-Path -LiteralPath $receiptPath) { throw 'Receipt exists; do not apply twice' }
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$targets = @()
foreach ($row in $manifest.delete) {
    $target = [IO.Path]::GetFullPath((Join-Path $cleanupRoot $row.path))
    if (-not $target.StartsWith($cleanupRoot + [IO.Path]::DirectorySeparatorChar,
            [StringComparison]::OrdinalIgnoreCase)) { throw "Outside workspace: $target" }
    $item = Get-Item -LiteralPath $target -Force
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Not a regular file: $target"
    }
    if ($item.Length -ne $row.bytes -or
        (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256) {
        throw "Changed target: $target"
    }
    if ($row.restore_from) {
        $restore = [IO.Path]::GetFullPath((Join-Path $cleanupRoot $row.restore_from))
        if (-not $restore.StartsWith($cleanupRoot + [IO.Path]::DirectorySeparatorChar,
                [StringComparison]::OrdinalIgnoreCase)) { throw 'Outside restore path' }
        if ((Get-FileHash -LiteralPath $restore -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256) {
            throw "Restore source changed: $restore"
        }
    }
    $targets += $target
}
Write-Output "Verified $($targets.Count) exact files; logical bytes $($manifest.logical_bytes)"
if (-not $Apply) { exit 0 }
$diskBefore = (Get-PSDrive -Name D).Free
$deleted = 0
try {
    foreach ($target in $targets) {
        Remove-Item -LiteralPath $target -Force
        $deleted++
    }
} finally {
    $receipt = [ordered]@{
        status = $(if ($deleted -eq $targets.Count) { 'complete' } else { 'partial' })
        deleted_files = $deleted
        planned_files = $targets.Count
        logical_bytes = $manifest.logical_bytes
        free_disk_before = $diskBefore
        free_disk_after = (Get-PSDrive -Name D).Free
        manifest_sha256 = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $encoding = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($receiptPath, ($receipt | ConvertTo-Json) + "`n", $encoding)
}
