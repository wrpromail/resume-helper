if ([string]::IsNullOrEmpty($env:GOOGLE_APPLICATION_CREDENTIALS) -or
    [string]::IsNullOrEmpty($env:OPENAI_API_KEY) -or
    [string]::IsNullOrEmpty($env:MISTRAL_API_KEY)) {
    Write-Host "Please set the required environment variables and try again."
    Exit 1
}
else {
    python3.exe -m modal deploy main.py
}

# if occur following error
#  + CategoryInfo          : SecurityError: (:) []，PSSecurityException
#  + FullyQualifiedErrorId : UnauthorizedAccess
# typing: Set-ExecutionPolicy Unrestricted
# or running powershell as administrator