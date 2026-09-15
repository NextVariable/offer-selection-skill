# test_installer.ps1 — PowerShell installer safety battery (dev tool, not shipped)
#
# Mirrors tools/test_installer.sh for install.ps1. Intended to run on a real
# Windows runner (GitHub Actions windows-latest job) because this repository's
# development machines have no PowerShell. Exits non-zero if any check fails.
#
# Every installer scenario runs inside its OWN pwsh child process
# (Invoke-InstallerProcess). install.ps1 is invoked with -File, so an expected
# `exit 1` inside the installer terminates only the child process — never this
# test runner — and every assertion reads the child's real ExitCode instead of
# a stale $LASTEXITCODE. Arguments travel through
# System.Diagnostics.ProcessStartInfo.ArgumentList, so paths containing spaces
# are passed verbatim with no manual quoting and no string concatenation.
#
# Usage:  pwsh -File tools/test_installer.ps1
# CI:     .github/workflows/ci.yml runs the windows-latest job.

$ErrorActionPreference = "Stop"
$RepoDir = Split-Path -Parent $PSScriptRoot
Set-Location $RepoDir

$Pass = 0
$Fail = 0
function Ok  { param($m) $script:Pass++; Write-Host "PASS: $m" }
function Bad { param($m) $script:Fail++; Write-Host "FAIL: $m" }

$T = Join-Path ([System.IO.Path]::GetTempPath()) ("oss-ps1-test." + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $T -Force | Out-Null

function Invoke-InstallerProcess {
    param(
        [string[]]$Arguments,
        [hashtable]$Environment = @{}
    )

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = (Get-Command pwsh).Source
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    foreach ($k in $Environment.Keys) { $psi.Environment[$k] = [string]$Environment[$k] }
    $psi.ArgumentList.Add("-NoProfile")
    $psi.ArgumentList.Add("-File")
    $psi.ArgumentList.Add((Join-Path $RepoDir "install.ps1"))
    foreach ($a in $Arguments) { $psi.ArgumentList.Add($a) }

    $proc = [System.Diagnostics.Process]::Start($psi)
    $outTask = $proc.StandardOutput.ReadToEndAsync()
    $errTask = $proc.StandardError.ReadToEndAsync()
    $proc.WaitForExit()

    return [pscustomobject]@{
        ExitCode = $proc.ExitCode
        Stdout   = $outTask.GetAwaiter().GetResult()
        Stderr   = $errTask.GetAwaiter().GetResult()
    }
}

try {
    # 1. Fresh install to a legal (nonexistent) path succeeds.
    $p1 = Join-Path $T "1\offer-selection-skill"
    $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p1)
    if ($r.ExitCode -eq 0 -and
        (Test-Path (Join-Path $p1 "SKILL.md")) -and
        (Test-Path (Join-Path $p1 ".offer-selection-skill-install.json"))) {
        Ok "1. fresh legal path"
    } else { Bad "1. fresh legal path (exit $($r.ExitCode))" }

    # 2. A parent directory containing spaces works when the basename matches.
    $p2 = Join-Path $T "my skills dir\offer-selection-skill"
    $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p2)
    if ($r.ExitCode -eq 0 -and (Test-Path (Join-Path $p2 "SKILL.md"))) {
        Ok "2. parent path with spaces"
    } else { Bad "2. parent path with spaces (exit $($r.ExitCode))" }

    # 3. Bad basename is rejected by the child process and nothing is created.
    $p3 = Join-Path $T "3\not-the-skill"
    $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p3)
    if ($r.ExitCode -ne 0) { Ok "3. basename rejection" } else { Bad "3. basename rejection (exit 0)" }
    if (-not (Test-Path -LiteralPath $p3)) {
        Ok "3. rejected path not created"
    } else { Bad "3. rejected path not created" }

    # 4. Unsafe destinations are rejected (each in its own child process).
    $unsafe = @("/", $env:USERPROFILE, $RepoDir, (Split-Path -Parent $RepoDir))
    foreach ($u in $unsafe) {
        $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $u)
        if ($r.ExitCode -ne 0) { Ok "4. unsafe rejection ($u)" } else { Bad "4. unsafe rejection ($u)" }
    }

    # 5. A stranger directory (no marker, no legacy layout) is refused and its
    #    contents preserved.
    $p5 = Join-Path $T "5\offer-selection-skill"
    New-Item -ItemType Directory -Path $p5 -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $p5 "precious.txt") -Value "sentinel" -Encoding UTF8
    $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p5)
    if ($r.ExitCode -ne 0) { Ok "5. stranger-directory refusal" } else { Bad "5. stranger-directory refusal" }
    if ((Get-Content -LiteralPath (Join-Path $p5 "precious.txt") -Raw).Trim() -eq "sentinel") {
        Ok "5. sentinel preserved"
    } else { Bad "5. sentinel preserved" }

    # 6. Managed marker upgrade (both runs succeed).
    $p6 = Join-Path $T "6\offer-selection-skill"
    $r1 = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p6)
    $r2 = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p6)
    if ($r1.ExitCode -eq 0 -and $r2.ExitCode -eq 0 -and
        (Test-Path (Join-Path $p6 ".offer-selection-skill-install.json"))) {
        Ok "6. managed marker upgrade"
    } else { Bad "6. managed marker upgrade (exits $($r1.ExitCode)/$($r2.ExitCode))" }

    # 7. A junction whose basename IS the skill name is refused by the link
    #    protection (the basename check alone cannot explain the refusal), and
    #    its target is untouched. Creating the junction is REQUIRED: if mklink
    #    fails the battery fails — coverage may never be silently skipped — and
    #    the junction must be confirmed to be a real reparse point before the
    #    installer is run against it.
    $pReal = Join-Path $T "7real"
    $p7 = Join-Path $T "7\offer-selection-skill"
    New-Item -ItemType Directory -Path (Split-Path $p7 -Parent) -Force | Out-Null
    New-Item -ItemType Directory -Path $pReal -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $pReal "data.txt") -Value "data" -Encoding UTF8
    $mk = [System.Diagnostics.ProcessStartInfo]::new()
    $mk.FileName = "cmd.exe"
    $mk.UseShellExecute = $false
    $mk.RedirectStandardOutput = $true
    $mk.RedirectStandardError = $true
    $mk.CreateNoWindow = $true
    $mk.ArgumentList.Add("/c")
    $mk.ArgumentList.Add("mklink")
    $mk.ArgumentList.Add("/J")
    $mk.ArgumentList.Add($p7)
    $mk.ArgumentList.Add($pReal)
    $mkProc = [System.Diagnostics.Process]::Start($mk)
    $mkOutTask = $mkProc.StandardOutput.ReadToEndAsync()
    $mkErrTask = $mkProc.StandardError.ReadToEndAsync()
    $mkProc.WaitForExit()
    if ($mkProc.ExitCode -ne 0) {
        $mkText = $mkOutTask.GetAwaiter().GetResult() + " " + $mkErrTask.GetAwaiter().GetResult()
        Bad "7. junction creation failed (mklink exit $($mkProc.ExitCode)): $mkText"
    } else {
        $item = Get-Item -LiteralPath $p7 -Force
        $isReparsePoint = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
        if (-not $isReparsePoint) {
            Bad "7. created path is not a reparse point (link protection not exercisable)"
        } else {
            $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p7)
            if ($r.ExitCode -ne 0) {
                Ok "7. link destination refused by link protection"
            } else { Bad "7. link destination refused by link protection (exit 0)" }
            if ((Get-Content -LiteralPath (Join-Path $pReal "data.txt") -Raw).Trim() -eq "data" -and
                -not (Test-Path (Join-Path $pReal "SKILL.md")) -and
                -not (Test-Path (Join-Path $pReal ".offer-selection-skill-install.json"))) {
                Ok "7. link target untouched (sentinel intact, no SKILL.md/marker added)"
            } else { Bad "7. link target untouched (sentinel intact, no SKILL.md/marker added)" }
            $itemAfter = Get-Item -LiteralPath $p7 -Force
            $rpAfter = ($itemAfter.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
            if ((Test-Path -LiteralPath $p7) -and $rpAfter) {
                Ok "7. junction still present as a reparse point after refusal"
            } else { Bad "7. junction missing or no longer a reparse point after refusal" }
        }
    }

    # 8. Invalid marker (wrong name) is refused and preserved.
    $p8 = Join-Path $T "8\offer-selection-skill"
    New-Item -ItemType Directory -Path $p8 -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $p8 ".offer-selection-skill-install.json") -Value '{"schema":"offer-selection-skill-install/v1","name":"other-skill","version":"9"}' -Encoding UTF8
    $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p8)
    if ($r.ExitCode -ne 0) { Ok "8. invalid-marker refusal" } else { Bad "8. invalid-marker refusal" }
    if (Test-Path (Join-Path $p8 ".offer-selection-skill-install.json")) {
        Ok "8. invalid marker preserved"
    } else { Bad "8. invalid marker preserved" }

    # 9. Payload: dev docs / dev material / installer scripts are absent.
    $bad = @()
    foreach ($d in @("README.md","CONTRIBUTING.md","SECURITY.md","AGENTS.md","audits","evals","archive","tools",".git",".workbuddy",".DS_Store","install.sh","install.ps1")) {
        if (Test-Path -LiteralPath (Join-Path $p1 $d)) { $bad += $d }
    }
    if ($bad.Count -eq 0) { Ok "9. no dev docs / dev material / installer scripts" }
    else { Bad "9. forbidden entries present: $($bad -join ',')" }

    # 10. Runtime references resolve + marker JSON parses.
    $missing = @()
    foreach ($f in @("SKILL.md","references\core-decision-engine.md","references\path-private-sector.md","references\path-soe-public.md","references\path-local-stay.md","references\path-phd-academic.md","domain\priors-and-calibration.md")) {
        if (-not (Test-Path -LiteralPath (Join-Path $p1 $f))) { $missing += $f }
    }
    if ($missing.Count -eq 0) { Ok "10. runtime references complete" }
    else { Bad "10. missing runtime files: $($missing -join ',')" }
    try {
        $pluginVer = (Get-Content -LiteralPath ".claude-plugin\plugin.json" -Raw -Encoding UTF8 | ConvertFrom-Json).version
        $mk = Get-Content -LiteralPath (Join-Path $p1 ".offer-selection-skill-install.json") -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($mk.schema -eq "offer-selection-skill-install/v1" -and $mk.name -eq "offer-selection-skill" -and $mk.version -eq $pluginVer) {
            Ok "10. marker JSON valid (schema/name/version)"
        } else { Bad "10. marker JSON invalid" }
    } catch {
        Bad "10. marker JSON unreadable: $_"
    }

    # 11. Real rollback fault injection: the test-only hook removes the staged
    #     copy AFTER the old install moved to backup, so the real placement
    #     failure path must restore the previous install and leave no
    #     .previous.*/staging residue.
    $p11 = Join-Path $T "11\offer-selection-skill"
    $r0 = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p11)
    if ($r0.ExitCode -ne 0) {
        Bad "11. rollback setup (initial managed install failed, exit $($r0.ExitCode))"
    } else {
        Set-Content -LiteralPath (Join-Path $p11 "sentinel.txt") -Value "rollback-sentinel" -Encoding UTF8
        $envMap = @{ "OFFER_SELECTION_INSTALLER_TEST_FAIL_AFTER_BACKUP" = "1" }
        $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p11) -Environment $envMap
        if ($r.ExitCode -ne 0) {
            Ok "11. rollback: upgrade failed under injected placement failure"
        } else { Bad "11. rollback: upgrade unexpectedly succeeded" }
        if ((Test-Path (Join-Path $p11 "SKILL.md")) -and
            (Test-Path (Join-Path $p11 ".offer-selection-skill-install.json"))) {
            Ok "11. rollback: previous install restored (SKILL.md + marker)"
        } else { Bad "11. rollback: previous install not restored" }
        if ((Get-Content -LiteralPath (Join-Path $p11 "sentinel.txt") -Raw).Trim() -eq "rollback-sentinel") {
            Ok "11. rollback: sentinel content unchanged"
        } else { Bad "11. rollback: sentinel content changed" }
        $left = @(Get-ChildItem -LiteralPath (Join-Path $T "11") -Force |
                  Where-Object { $_.Name -ne "offer-selection-skill" })
        if ($left.Count -eq 0) {
            Ok "11. rollback: no .previous.* or staging leftover"
        } else { Bad "11. rollback: leftover entries: $(($left | ForEach-Object { $_.Name }) -join ',')" }
    }

    # 12. Restore-failure fault injection: when BOTH placement and the
    #     automatic restore fail (test-only hooks), the installer must keep the
    #     backup (never delete or overwrite it), print its exact path, and must
    #     NOT claim that it restored the previous install.
    $p12 = Join-Path $T "12\offer-selection-skill"
    $r0 = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p12)
    if ($r0.ExitCode -ne 0) {
        Bad "12. restore-failure setup (initial managed install failed, exit $($r0.ExitCode))"
    } else {
        Set-Content -LiteralPath (Join-Path $p12 "sentinel.txt") -Value "restore-fail-sentinel" -Encoding UTF8
        $envMap = @{
            "OFFER_SELECTION_INSTALLER_TEST_FAIL_AFTER_BACKUP" = "1"
            "OFFER_SELECTION_INSTALLER_TEST_FAIL_RESTORE" = "1"
        }
        $r = Invoke-InstallerProcess -Arguments @("-Platform", "universal", "-Path", $p12) -Environment $envMap
        $combined = $r.Stdout + "`n" + $r.Stderr
        if ($r.ExitCode -ne 0) {
            Ok "12. restore-failure: upgrade failed (placement + restore both injected to fail)"
        } else { Bad "12. restore-failure: upgrade unexpectedly succeeded" }
        if ($combined -match "Automatic restoration also failed") {
            Ok "12. restore-failure: output reports the automatic restoration failure"
        } else { Bad "12. restore-failure: output does not report the automatic restoration failure" }
        if ($combined -match "restored successfully") {
            Bad "12. restore-failure: output falsely claims a successful restore"
        } else { Ok "12. restore-failure: output does not falsely claim a restore" }
        $backup = @(Get-ChildItem -LiteralPath (Join-Path $T "12") -Force |
                    Where-Object { $_.Name -like ".offer-selection-skill.previous.*" })
        if ($backup.Count -gt 0) {
            Ok "12. restore-failure: previous install preserved in a backup directory"
        } else { Bad "12. restore-failure: no backup directory found" }
        if ($backup.Count -gt 0) {
            $bkPath = $backup[0].FullName
            if ($combined.Contains($bkPath)) {
                Ok "12. restore-failure: output reports the backup path"
            } else { Bad "12. restore-failure: output does not report the backup path" }
            if ((Test-Path (Join-Path $bkPath "SKILL.md")) -and
                (Test-Path (Join-Path $bkPath ".offer-selection-skill-install.json")) -and
                ((Get-Content -LiteralPath (Join-Path $bkPath "sentinel.txt") -Raw).Trim() -eq "restore-fail-sentinel")) {
                Ok "12. restore-failure: backup intact (SKILL.md + marker + sentinel)"
            } else { Bad "12. restore-failure: backup incomplete or sentinel changed" }
        }
        if (-not (Test-Path (Join-Path $p12 "SKILL.md"))) {
            Ok "12. restore-failure: destination not occupied by a new install"
        } else { Bad "12. restore-failure: destination wrongly occupied by a new install" }
        $stagingLeft = @(Get-ChildItem -LiteralPath (Join-Path $T "12") -Force |
                         Where-Object { $_.Name -like "*.staging.*" })
        if ($stagingLeft.Count -eq 0) {
            Ok "12. restore-failure: no staging leftover"
        } else { Bad "12. restore-failure: staging leftover present" }
    }
} finally {
    Remove-Item -LiteralPath $T -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "----"
Write-Host "installer battery: PASS=$Pass FAIL=$Fail"
if ($Fail -ne 0) { exit 1 }
exit 0
