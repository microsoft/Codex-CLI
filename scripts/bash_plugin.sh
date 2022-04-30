#!/bin/bash

#############################################
## *** NL-CLI plugin Function for Bash *** ##
#############################################

create_completion() {
    # Get the text typed until now.
    text=${READLINE_LINE}
    completion=$(echo -n "$text" | $NL_CLI_PATH/src/codex_query.py)
    # Add completion to the current buffer.
    READLINE_LINE="${text}${completion}"
    # Put the cursor at the end of the line.
    READLINE_POINT=${#READLINE_LINE}
}