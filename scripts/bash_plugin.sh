#!/bin/bash

## Allow bash script to get last input from command line
set -o history -o histexpand

## Allow for trap of Ctrl-g


#####################################
## *** NL-CLI plugin Function *** ##
#####################################

create_completion() {
    # Get the text typed until now.
    text=$(echo !!)
    cmd_line=$(history | tail -2 | head -1 | cut -c8-999)

    completion=$(echo -n "$text" | $NL_CLI_PATH/codex_query.py)
    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}

cmd_line=$(history | tail -2 | head -1 | cut -c8-999)
echo $cmd_line
