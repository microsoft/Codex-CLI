### 
# PowerShell script to clean up the Codex CLI settings for PowerShell
#
# File/Content to be removed:
# 1. PowerShell profile (Remove file if the content only has Codex CLI setup; otherwise, wipe the Codex CLI setup content)
# 2. OpenAI configuration file (openaiapirc)
###
$RepoRoot = (Get-Location)

$openAIConfigPath = Join-Path $RepoRoot -ChildPath "src\openaiapirc"

function CleanUpOpenAiConfig() 
{
    if (Test-Path -Path $openAIConfigPath) {
        Remove-Item $openAIConfigPath
        Write-Host "Removed $openAIConfigPath"
    }
}

function CleanUpProfileContent() 
{
    if (Test-Path -Path $PROFILE) {
        # RegEx match setup code, replace with empty string.
        (Get-Content -Path $PROFILE -Raw) -replace "(?ms)### Codex CLI setup - start.*?### Codex CLI setup - end", "" | Set-Content -Path $PROFILE

        # Delete the file if its content is empty
        if ([String]::IsNullOrWhiteSpace((Get-Content -Path $PROFILE))) {
            Remove-Item $PROFILE
            Write-Host "Removed $PROFILE"
        }
    }
}

CleanUpProfileContent
CleanUpOpenAiConfig

Write-Host -ForegroundColor Blue "Codex CLI PowerShell clean up completed. Please close this PowerShell session."