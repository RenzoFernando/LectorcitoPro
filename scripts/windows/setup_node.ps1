[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EnvironmentFile
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$NodeVersion = "24.19.0"
$NodeArchiveName = "node-v$NodeVersion-win-x64.zip"
$NodeDirectoryName = "node-v$NodeVersion-win-x64"
$NodeArchiveHash = "57f71ab3652e797d84acddc79c81cc9ff1c6ddb2a1974cdb83f00fee9bff4c73"
$NodeUrl = "https://nodejs.org/dist/v$NodeVersion/$NodeArchiveName"
$ToolsRoot = Join-Path $ProjectRoot ".tools"
$DownloadRoot = Join-Path $ToolsRoot "downloads"
$PortableNodeRoot = Join-Path $ToolsRoot $NodeDirectoryName
$ArchivePath = Join-Path $DownloadRoot $NodeArchiveName

function Test-NodeCandidate {
    param([string]$NodePath)

    if (-not $NodePath -or -not (Test-Path $NodePath -PathType Leaf)) {
        return $false
    }

    try {
        $Version = (& $NodePath --version 2>$null | Select-Object -First 1).ToString().Trim()
        return $Version -eq "v$NodeVersion"
    } catch {
        return $false
    }
}

function Resolve-NpmPath {
    param([string]$NodePath)

    $AdjacentNpm = Join-Path (Split-Path -Parent $NodePath) "npm.cmd"
    if (Test-Path $AdjacentNpm -PathType Leaf) {
        return (Resolve-Path $AdjacentNpm).Path
    }

    $NpmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($NpmCommand) {
        return $NpmCommand.Source
    }

    return ""
}

$NodePath = ""
$NpmPath = ""
$SystemNode = Get-Command node.exe -ErrorAction SilentlyContinue
if ($SystemNode -and (Test-NodeCandidate $SystemNode.Source)) {
    $NodePath = $SystemNode.Source
    $NpmPath = Resolve-NpmPath $NodePath
}

if (-not $NodePath -or -not $NpmPath) {
    New-Item -ItemType Directory -Path $DownloadRoot -Force | Out-Null

    $PortableNodeExe = Join-Path $PortableNodeRoot "node.exe"
    $PortableNpmCmd = Join-Path $PortableNodeRoot "npm.cmd"

    if (-not (Test-NodeCandidate $PortableNodeExe) -or -not (Test-Path $PortableNpmCmd -PathType Leaf)) {
        if (Test-Path $PortableNodeRoot) {
            Remove-Item -Path $PortableNodeRoot -Recurse -Force
        }

        $DownloadRequired = $true
        if (Test-Path $ArchivePath -PathType Leaf) {
            $ExistingHash = (Get-FileHash -Algorithm SHA256 -Path $ArchivePath).Hash.ToLowerInvariant()
            $DownloadRequired = $ExistingHash -ne $NodeArchiveHash
            if ($DownloadRequired) {
                Remove-Item -Path $ArchivePath -Force
            }
        }

        if ($DownloadRequired) {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $NodeUrl -OutFile $ArchivePath -UseBasicParsing
        }

        $DownloadedHash = (Get-FileHash -Algorithm SHA256 -Path $ArchivePath).Hash.ToLowerInvariant()
        if ($DownloadedHash -ne $NodeArchiveHash) {
            Remove-Item -Path $ArchivePath -Force -ErrorAction SilentlyContinue
            throw "El SHA-256 de Node.js no coincide con el valor esperado."
        }

        Expand-Archive -Path $ArchivePath -DestinationPath $ToolsRoot -Force
    }

    if (-not (Test-NodeCandidate $PortableNodeExe)) {
        throw "Node.js portable no quedo disponible en la version requerida."
    }
    if (-not (Test-Path $PortableNpmCmd -PathType Leaf)) {
        throw "npm.cmd no quedo disponible junto a Node.js portable."
    }

    $NodePath = (Resolve-Path $PortableNodeExe).Path
    $NpmPath = (Resolve-Path $PortableNpmCmd).Path
}

$EnvironmentDirectory = Split-Path -Parent $EnvironmentFile
if ($EnvironmentDirectory) {
    New-Item -ItemType Directory -Path $EnvironmentDirectory -Force | Out-Null
}

$EnvironmentLines = @(
    "@set `"LECTORCITO_NODE_EXE=$NodePath`"",
    "@set `"LECTORCITO_NPM_CMD=$NpmPath`""
)
[System.IO.File]::WriteAllLines(
    $EnvironmentFile,
    $EnvironmentLines,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "Node.js: $(& $NodePath --version)"
Write-Host "npm: $(& $NpmPath --version)"
