<#
  Build the CSEYE portable package: a self-contained, no-admin Windows folder
  (embeddable Python + bridge + built viewer + double-click launcher), zipped.

  Prereq: build the viewer first so viewer/dist exists:
      cd ../viewer ; npm run build

  Usage:
      pwsh -File build-portable.ps1 [-PyVersion 3.12.8] [-OutDir C:\Analysis\CSEYE\package]
#>
param(
  [string]$PyVersion = '3.12.8',
  [string]$OutDir    = 'C:\Analysis\CSEYE\package'
)
$ErrorActionPreference = 'Stop'
$src = Split-Path -Parent $PSScriptRoot        # cseye-web
$pkg = Join-Path $OutDir 'CSEYE-Portable'
$dl  = Join-Path $OutDir '_dl'

if (-not (Test-Path "$src\viewer\dist\index.html")) { throw "viewer/dist missing - run 'npm run build' in ../viewer first." }
if (Test-Path $pkg) { Remove-Item $pkg -Recurse -Force }
New-Item -ItemType Directory -Force -Path "$pkg\python", $dl | Out-Null

# 1) embeddable Python
$zip = "$dl\py-embed.zip"
Invoke-WebRequest "https://www.python.org/ftp/python/$PyVersion/python-$PyVersion-embed-amd64.zip" -OutFile $zip
Expand-Archive $zip -DestinationPath "$pkg\python" -Force

# 2) enable site-packages + site import in the ._pth
$pth = Get-ChildItem "$pkg\python\python*._pth" | Select-Object -First 1
@"
$($pth.BaseName).zip
.
Lib\site-packages

import site
"@ | Set-Content -Path $pth.FullName -Encoding ascii

# 3) pip + deps
Invoke-WebRequest 'https://bootstrap.pypa.io/get-pip.py' -OutFile "$dl\get-pip.py"
& "$pkg\python\python.exe" "$dl\get-pip.py" --no-warn-script-location
& "$pkg\python\python.exe" -m pip install --no-warn-script-location `
    "fastapi>=0.110" "uvicorn>=0.29" "comtypes>=1.4" "pydantic>=2.6"

# 4) app tree (mirror cseye-web layout; NO .env / secrets)
New-Item -ItemType Directory -Force -Path "$pkg\app\bridge","$pkg\app\viewer" | Out-Null
robocopy "$src\bridge\cseye_bridge" "$pkg\app\bridge\cseye_bridge" /E /XD __pycache__ /NFL /NDL /NJH /NJS /NP | Out-Null
Copy-Item "$src\bridge\run.py","$src\bridge\launcher.py" "$pkg\app\bridge\"
robocopy "$src\viewer\dist" "$pkg\app\viewer\dist" /E /NFL /NDL /NJH /NJS /NP | Out-Null
Copy-Item "$PSScriptRoot\portable-README.txt" "$pkg\README.txt" -ErrorAction SilentlyContinue
Copy-Item "$PSScriptRoot\portable-Start.bat"  "$pkg\Start CSEYE.bat" -ErrorAction SilentlyContinue

# 5) slim + zip
Get-ChildItem -Recurse -Directory "$pkg" -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$pkg\python\Lib\site-packages\pip","$pkg\python\Lib\site-packages\pip-*","$pkg\python\Scripts" -Recurse -Force -ErrorAction SilentlyContinue
$out = "$OutDir\CSEYE-Portable.zip"
Remove-Item $out -Force -ErrorAction SilentlyContinue
Compress-Archive -Path $pkg -DestinationPath $out -CompressionLevel Optimal
Remove-Item $dl -Recurse -Force -ErrorAction SilentlyContinue
"Built {0}  ({1:N1} MB)" -f $out, ((Get-Item $out).Length/1MB)
