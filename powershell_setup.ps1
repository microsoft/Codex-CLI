### 
# PowerShell script to setup NL-CLI for PowerShell
###
param
(
    # TODO: Add a swtich for init/clean-up
    [Parameter(Mandatory = $true)]
    [System.IO.FileInfo]
    [ValidateScript( {
            if (-Not ($_ | Test-Path) ) {
                throw "Folder does not exist. Did you clone the NL-CLI repo?" 
            }
            return $true
        })]
    [string]$RepoRoot,

    [Parameter(Mandatory = $true)]
    [SecureString]
    $OpenAIOrgId,

    [Parameter(Mandatory = $true)]
    [SecureString]
    $OpenAIApiKey,

    [Parameter()]
    [bool]
    $CleanUp = $false
)

$plugInScriptPath = Join-Path $RepoRoot -ChildPath "powershell_plugin.ps1"
$codexQueryPath = Join-Path $RepoRoot -ChildPath "codex_query.py"
$openAIConfigPath = Join-Path $env:USERPROFILE -ChildPath ".config\openaiapirc"

function CleanUpProfile() {
    if (Test-Path -Path $PROFILE)
    {
        CleanUpProfileContent
        New-Item -Type File -Path $PROFILE -Force 
    }
}

function CleanUpProfileContent() {
# RegEx match start and end pattern, replace with empty string.
# if the file length is 0. delete the file
# if the folder childItem count is 0, delete the folder
}

function CleanUpOpenAiConfig() {
    if (Test-Path -Path $openAIConfigPath)
    {
        Remove-Item $openAIConfigPath
        Write-Host "Removed $openAIConfigPath"
    }
}

# Create new PowerShell profile if doesn't exist. The profile type is for current user and current host.
# To learn more about PowerShell profile, please refer to 
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles
if (!(Test-Path -Path $PROFILE))
{
    New-Item -Type File -Path $PROFILE -Force 
} else {
    # TODO: Clean up the content before append new one
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

Set-Content -Path $openAIConfigPath "[openai]
organization_id=$OpenAIOrgId
secret_key=$OpenAIApiKey"
Write-Host "Updated OpenAI configuration file with secrets"