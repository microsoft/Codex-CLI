### 
# PowerShell script to clean up the NL-CLI settings for PowerShell
#
# File/Content to be removed:
# 1. PowerShell profile (Remove file and/or folder if the content only has NL-CLI setup; otherwise, wipe the NL-CLI setup content)
# 2. OpenAI configuration file (openaiapirc)
###

function CleanUpOpenAiConfig() 
{
    if (Test-Path -Path $openAIConfigPath)
    {
        Remove-Item $openAIConfigPath
        Write-Host "Removed $openAIConfigPath"
    }
}

function CleanUpProfileContent() 
{
    # RegEx match start and end pattern, replace with empty string.
    (Get-Content -Path $PROFILE) -replace "^.*?(?:\b|_)NL-CLI setup - start(?:\b|_).*?(?:\b|_)NL-CLI setup - end", "" | Set-Content $PROFILE

    # if the file length is 0. delete the file
    if (IsNullOrWhiteSpace((Get-Content -Path $PROFILE)))
    {
        Remove-Item $PROFILE
        Write-Host "Removed $PROFILE"

        # if the folder childItem count is 1, delete the folder
        $profileFolderPath = (Get-Item $PROFILE).parent
        if(Test-Path -Path $profileFolderPath)
        {
            if ((Get-ChildItem $profileFolderPath).count == 1)
            {
                # TODO: actually reove the folder
                Write-Host "Removed $profileFolderPath"
            }
        }
    }
}

if (Test-Path -Path $PROFILE) 
{
    CleanUpProfileContent
    #Remove-Item -Type File -Path $PROFILE -Force 
}