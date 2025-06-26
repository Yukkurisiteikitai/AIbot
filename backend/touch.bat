function touch([string] $filePath) {
    # if exists, make it update
    # if not exists, make it create
    
    if (Test-Path $filePath) {
        (Get-Item $filePath).LastWriteTime = Get-Date
    }
    else {
        New-Item -ItemType File -Path $filePath | Out-Null
    }
}
