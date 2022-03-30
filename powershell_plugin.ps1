### NL-CLI setup - start
$nl_cli_script = "{{codex_query_path}}"


# this function takes the input from the buffer and passes it to codex_query.py
function create_completion() {
    param (
        # accept $buffer and $context parameters
        [string] $buffer,
        [bool] $context
    )
    
    if ($nl_cli_script -eq "") {
        Write-Output "# Please update the nl_cli_script path in $profile"
        return "`nnotepad $profile"
    }

    if ($context) {
    	$output = echo -n $buffer | python $nl_cli_script -c
    }
    else {
	    $output = echo -n $buffer | python $nl_cli_script
    }


    return $output
}

Set-PSReadLineKeyHandler -Key Ctrl+x `
                         -BriefDescription NLCLI1 `
                         -LongDescription "Calls NL-CLI tool on the current buffer with context" `
                         -ScriptBlock {
    param($key, $arg)
    
    $line = $null
    $cursor = $null

    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)

    $output = create_completion($line, $true)
    
    if ($output -ne $null) {
        foreach ($str in $output) {
            if ($str -ne $null -and $str -ne "") {
                [Microsoft.PowerShell.PSConsoleReadLine]::AddLine()
                [Microsoft.PowerShell.PSConsoleReadLine]::Insert($str)
            }
        }
    }
}


Set-PSReadLineKeyHandler -Key Ctrl+g `
                         -BriefDescription NLCLI2 `
                         -LongDescription "Calls NL-CLI tool on the current buffer without context" `
                         -ScriptBlock {
    param($key, $arg)
    
    $line = $null
    $cursor = $null

    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)

    $output = create_completion($line, $false)
    
    if ($output -ne $null) {
        foreach ($str in $output) {
            if ($str -ne $null -and $str -ne "") {
                [Microsoft.PowerShell.PSConsoleReadLine]::AddLine()
                [Microsoft.PowerShell.PSConsoleReadLine]::Insert($str)
            }
        }
    }
}
### NL-CLI setup - end