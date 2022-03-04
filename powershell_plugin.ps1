
# fill in the path here
# it will look like - C:\Users\<username>\your\custom\path\NL-CLI\codex-query.py
$nl_cli_script = ""

# this function takes the input from the buffer and passes it to codex_query.py
function create_completion() {
    param (
        [Parameter (Mandatory = $true)] [string] $buffer
    )
    
    if ($nl_cli_script -eq "") {
        Write-Output "# Please update the nl_cli_script path in $profile"
        return "`nnotepad $profile"
    }

    $output = echo -n $buffer | python $nl_cli_script 
    
    return $output
}

Set-PSReadLineKeyHandler -Key Ctrl+x `
                         -BriefDescription NLCLI `
                         -LongDescription "Calls NL-CLI tool on the current buffer" `
                         -ScriptBlock {
    param($key, $arg)
    
    $line = $null
    $cursor = $null

    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)

    # get response from create_completion function
    $outpt = create_completion($line)

    # move to the next line
    [Microsoft.PowerShell.PSConsoleReadLine]::AddLine()
    [Microsoft.PowerShell.PSConsoleReadLine]::Insert($outpt)
}
