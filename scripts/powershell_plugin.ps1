### Codex CLI setup - start
$nl_cli_script = "{{codex_query_path}}"

# this function takes the input from the buffer and passes it to codex_query.py
function create_completion() {
    param (
        [Parameter (Mandatory = $true)] [string] $buffer
    )
    
    if ($nl_cli_script -eq "" -or !(Test-Path($nl_cli_script))) {
        Write-Output "# Please update the nl_cli_script path in the profile!"
        return "`nnotepad $profile"
    }

    $output = echo -n $buffer | python $nl_cli_script 
    
    return $output
}

Set-PSReadLineKeyHandler -Key Ctrl+g `
                         -BriefDescription NLCLI `
                         -LongDescription "Calls Codex CLI tool on the current buffer" `
                         -ScriptBlock {
    param($key, $arg)
    
    $line = $null
    $cursor = $null

    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)

    # get response from create_completion function
    $output = create_completion($line)

    # get first char of the response
    # if its not #, add # to the beginning of the response
    if ($output[0] -ne "#") {
        $output = "# $output"
    }
    # note: add multiline fix
    

    
    # check if output is not null
    if ($output -ne $null) {
        foreach ($str in $output) {
            if ($str -ne $null -and $str -ne "") {
                [Microsoft.PowerShell.PSConsoleReadLine]::AddLine()
                [Microsoft.PowerShell.PSConsoleReadLine]::Insert($str)
            }
        }
    }
}
### Codex CLI setup - end