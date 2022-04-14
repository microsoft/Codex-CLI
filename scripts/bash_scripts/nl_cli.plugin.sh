#!/bin/bash

create_completion() 
{
    local codex_path=$NL_CLI_PATH/src
    # Get the text typed until now.
    ## read -e BUFFER <TODO: update from other branch fix this add sigint trap>
    # text=${BUFFER}
    
    completion=$(echo -n "$text" | $codex_path/codex_query.py)
    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER} #TODO: update this from other branch -TEW
}