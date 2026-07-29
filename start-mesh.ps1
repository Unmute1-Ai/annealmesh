$ErrorActionPreference = "Stop"

$project = "C:\Users\cindy\builds\hermes-nemotron-mesh"
$envFile = Join-Path $project ".env"

if (-not (Test-Path -LiteralPath $envFile)) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(
        "Configuration is missing.`n`nOpen PowerShell in:`n$project`n`nThen create .env from .env.example and add your NVIDIA API key.",
        "Mesh setup required",
        "OK",
        "Information"
    ) | Out-Null
    exit 1
}

$existing = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
    Start-Process `
        -FilePath "hermes-web" `
        -WorkingDirectory $project `
        -WindowStyle Hidden
}

$ready = $false
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -TimeoutSec 1
        if ($health.status -eq "ok") {
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Milliseconds 250
    }
}

if (-not $ready) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(
        "The app did not start. Run 'hermes-web' in PowerShell to view the error.",
        "Mesh could not start",
        "OK",
        "Error"
    ) | Out-Null
    exit 1
}

Start-Process "http://127.0.0.1:8080"
