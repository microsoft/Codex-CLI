### 
# PowerShell script to setup NL-CLI for PowerShell
###
param
(
    [Parameter()]
    [System.IO.FileInfo]
    [ValidateScript( {
            if (-Not ($_ | Test-Path) ) {
                throw "Folder does not exist. Did you clone the NL-CLI repo?" 
            }
            return $true
        })]
    [string]$RepoRoot = (Get-Location),

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [SecureString]
    $OpenAIApiKey
)

$plugInScriptPath = Join-Path $RepoRoot -ChildPath "powershell_plugin.ps1"
$codexQueryPath = Join-Path $RepoRoot -ChildPath "codex_query.py"
$openAIConfigPath = Join-Path $env:USERPROFILE -ChildPath ".config\openaiapirc"

# Create new PowerShell profile if doesn't exist. The profile type is for current user and current host.
# To learn more about PowerShell profile, please refer to 
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles
if (!(Test-Path -Path $PROFILE))
{
    New-Item -Type File -Path $PROFILE -Force 
} else {
    # Clean up the content before append new one. This allow users to setup multiple times without running cleanup script
    (Get-Content -Path $PROFILE -Raw) -replace "(?ms)### NL-CLI setup - start.*?### NL-CLI setup - end", "" | Set-Content -Path $PROFILE
    Write-Host "Removed previous setup script from $PROFILE."
}

# Add our plugin script into PowerShell profile. It involves three steps:
# 1. Read the plugin script content,
# 2. Replace hardcode variable with the actual path to codex_query.py, 
# 3. Add the plugin script to the content of PowerShell profile.
(Get-Content -Path $plugInScriptPath) -replace "{{codex_query_path}}", $codexQueryPath | Add-Content -Path $PROFILE
Write-Host "Added plugin setup to $PROFILE."

# Create OpenAI configuration file to store secrets
if (!(Test-Path -Path $openAIConfigPath))
{
    New-Item -Type File -Path $openAIConfigPath -Force 
}

$openAIApiKeyPlainText = ConvertFrom-SecureString -SecureString $OpenAIApiKey -AsPlainText

Set-Content -Path $openAIConfigPath "[openai]
secret_key=$openAIApiKeyPlainText"
Write-Host "Updated OpenAI configuration file with secrets"