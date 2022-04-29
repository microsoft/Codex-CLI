#!/bin/bash

## Allow bash script to get last input from command line
set -o history -o histexpand

## Allow for trap of Ctrl-g


#####################################
## *** NL-CLI plugin Function *** ##
#####################################

create_completion() {
    # Get the text typed until now.
    cmd_line=$(history | tail -2 | head -1 | cut -c8-999)

    # Fire off to Codex
    completion_test=$(echo -n "$cmd_line" | $NL_CLI_PATH/src/codex_query.py)
    
    # Add completion to the current buffer.
    BUFFER="${cmdline}${completion}"

    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}


