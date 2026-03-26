param(
    [switch]$WithMcp,
    [switch]$DryRun,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [int]$McpPort = 8001
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
$backendSrc = Join-Path $root "backend\src"
$frontendDir = Join-Path $root "frontend"
$mcpPyPath = Join-Path $root "backend\src\mcp_server\arxiv-mcp-server\src"

function Resolve-PythonExe {
    if ($env:CONDA_PREFIX) {
        $condaPython = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path $condaPython) {
            return $condaPython
        }
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd -and $pythonCmd.Source) {
        return $pythonCmd.Source
    }

    throw "Cannot find python executable in current shell."
}

$pythonExe = Resolve-PythonExe

Write-Host "[start] root: $root"
Write-Host "[start] python: $pythonExe"
Write-Host "[start] backend: http://localhost:$BackendPort"
Write-Host "[start] frontend: http://localhost:$FrontendPort"

if ($WithMcp) {
    Write-Host "[start] mcp sse: http://localhost:$McpPort/sse"
}

$backendCmd = @"
Set-Location '$backendSrc'
`$env:PYTHONPATH = '$backendSrc'
`$env:PORT = '$BackendPort'
"@

if ($WithMcp) {
    $mcpCmd = @"
Set-Location '$root'
`$env:PYTHONPATH = '$mcpPyPath'
& '$pythonExe' -m arxiv_mcp_server.__init__ --transport sse --port $McpPort
"@

    $backendCmd += @"

`$env:ENABLE_MCP = 'true'
`$env:ARXIV_MCP_TRANSPORT = 'sse'
`$env:ARXIV_MCP_URL = 'http://localhost:$McpPort/sse'
"@
} else {
    $backendCmd += "`n`$env:ENABLE_MCP = 'false'"
}

$backendCmd += @"

& '$pythonExe' main.py
"@

$frontendCmd = "Set-Location '$frontendDir'; npm run dev -- --port $FrontendPort"

if ($DryRun) {
    if ($WithMcp) {
        Write-Host "`n[dry-run] MCP command:" -ForegroundColor Yellow
        Write-Host $mcpCmd
    }
    Write-Host "`n[dry-run] Backend command:" -ForegroundColor Yellow
    Write-Host $backendCmd
    Write-Host "`n[dry-run] Frontend command:" -ForegroundColor Yellow
    Write-Host $frontendCmd
    return
}

if ($WithMcp) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $mcpCmd | Out-Null
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd | Out-Null
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd | Out-Null

Write-Host "[done] all requested services started in new terminals."


