param(
    [string]$Python = ".\.venv\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$packagingDir = Join-Path $projectRoot "packaging"
$iconPath = Join-Path $packagingDir "wechat-toast.ico"
$versionFilePath = Join-Path $packagingDir "version_info.txt"
Set-Location $projectRoot

if (-not (Test-Path $Python)) {
    throw "未找到 Python: $Python"
}

if (-not (Test-Path $iconPath)) {
    throw "未找到图标文件: $iconPath"
}

if (-not (Test-Path $versionFilePath)) {
    throw "未找到版本信息文件: $versionFilePath"
}

& $Python -m pip install --upgrade pip
& $Python -m pip install pyinstaller

if (Test-Path .\build) {
    Remove-Item -LiteralPath .\build -Recurse -Force
}

if (Test-Path .\dist) {
    Remove-Item -LiteralPath .\dist -Recurse -Force
}

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name wechat-toast `
    --icon $iconPath `
    --version-file $versionFilePath `
    --add-binary '.\.venv\Lib\site-packages\uiautomation\bin\UIAutomationClient_VC140_X64.dll;uiautomation\bin' `
    --add-binary '.\.venv\Lib\site-packages\uiautomation\bin\UIAutomationClient_VC140_X86.dll;uiautomation\bin' `
    .\wechat-toast.py

Write-Host ""
Write-Host "打包完成: $projectRoot\dist\wechat-toast.exe"
