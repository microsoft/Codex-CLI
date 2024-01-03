###
# PowerShell script to setup Codex CLI for PowerShell
###
param
(
    [Parameter()]
    [System.IO.FileInfo]
    [ValidateScript( {
            if (-Not ($_ | Test-Path) ) {
                throw "Folder does not exist. Did you clone the Codex CLI repo?" 
            }
            return $true
        })]
    [string]$RepoRoot = (Get-Location),

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [SecureString]
    $OpenAIApiKey,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    $OpenAIOrganizationId,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    $OpenAIModelID
)

$plugInScriptPath = Join-Path $RepoRoot -ChildPath "scripts\powershell_plugin.ps1"
$codexQueryPath = Join-Path $RepoRoot -ChildPath "src\codex_query.py"
$openAIConfigPath = Join-Path $RepoRoot -ChildPath "src\openaiapirc"

# The major version of PowerShell
$PSMajorVersion = $PSVersionTable.PSVersion.Major

# Convert secure string to plain text
if ($PSMajorVersion -lt 7) {
    $binaryString = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($OpenAIApiKey);
    $openAIApiKeyPlainText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($binaryString);
} else {
    $openAIApiKeyPlainText = ConvertFrom-SecureString -SecureString $OpenAIApiKey -AsPlainText
}

# Check the access with OpenAI API
# API call to https://api.openai.com/v1/engines is a potential risk in the future because the route is deprecated
Write-Host "Checking OpenAI access..."
$testApiUri = "https://api.openai.com/v1/engines"
$response = $null
try {
    if ($PSMajorVersion -lt 7) {
        $response = (Invoke-WebRequest -Uri $testApiUri -Headers @{"Authorization" = "Bearer $openAIApiKeyPlainText"; "OpenAI-Organization" = "$OpenAIOrganizationId"})
    } else {
        $response = (Invoke-WebRequest -Uri $testApiUri -Authentication Bearer -Token $OpenAIApiKey -Headers @{"OpenAI-Organization" = "$OpenAIOrganizationId"})
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Error "Failed to access OpenAI api [$statusCode]. Please check your OpenAI API key (https://beta.openai.com/account/api-keys) and Organization ID (https://beta.openai.com/account/org-settings)."
    exit 1
}

# Check if target model is available to the user
if ($null -eq (($response.Content | ConvertFrom-Json).data | Where-Object {$_.id -eq $OpenAIModelID})) {
    Write-Error "Cannot find OpenAI model: $OpenAIModelID. Please check the OpenAI model id (https://platform.openai.com/docs/models/gpt-4) and your Organization ID (https://beta.openai.com/account/org-settings)."
    exit 1
}

# Create new PowerShell profile if doesn't exist. The profile type is for current user and current host.
# To learn more about PowerShell profile, please refer to 
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles
if (!(Test-Path -Path $PROFILE)) {
    New-Item -Type File -Path $PROFILE -Force 
} else {
    # Clean up the content before append new one. This allow users to setup multiple times without running cleanup script
    (Get-Content -Path $PROFILE -Raw) -replace "(?ms)### Codex CLI setup - start.*?### Codex CLI setup - end", "" | Set-Content -Path $PROFILE
    Write-Host "Removed previous setup script from $PROFILE."
}

# Add our plugin script into PowerShell profile. It involves three steps:
# 1. Read the plugin script content,
# 2. Replace hardcode variable with the actual path to codex_query.py, 
# 3. Add the plugin script to the content of PowerShell profile.
(Get-Content -Path $plugInScriptPath) -replace "{{codex_query_path}}", $codexQueryPath | Add-Content -Path $PROFILE
Write-Host "Added plugin setup to $PROFILE."

# Create OpenAI configuration file to store secrets
if (!(Test-Path -Path $openAIConfigPath)) {
    New-Item -Type File -Path $openAIConfigPath -Force 
}

Set-Content -Path $openAIConfigPath "[openai]
organization_id=$OpenAIOrganizationId
secret_key=$openAIApiKeyPlainText
model=$OpenAIModelID"
Write-Host "Updated OpenAI configuration file with secrets."

Write-Host -ForegroundColor Blue "Codex CLI PowerShell (v$PSMajorVersion) setup completed. Please open a new PowerShell session, type in # followed by your natural language command and hit Ctrl+G!"
