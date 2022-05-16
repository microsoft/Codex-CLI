#!/usr/bin/env bash

#############################################
## *** NL-CLI plugin function for Bash *** ##
#############################################

create_completion() {
    # Check settings in case the CLI has just been uninstalled in another session
    local SETTINGS="$NL_CLI_PATH/src/openaiapirc"
    local SIZE=$(wc -c $SETTINGS | awk '{print $1}')
    if [ ! -f "$SETTINGS" ]; then
        echo "OpenAI NL-CLI configuration is missing. Try reinstalling NL CLI."
        return
    fi
    if (( $SIZE < 10 )); then
        echo "OpenAI NL-CLI configuration is missing. Try reinstalling NL CLI."
        return
    fi
    # Get the text typed until now
    text=${READLINE_LINE}
    completion=$(echo -n "$text" | $NL_CLI_PATH/src/codex_query.py)
    # Add completion to the current buffer
    READLINE_LINE="${text}${completion}"
    # Put the cursor at the end of the line
    READLINE_POINT=${#READLINE_LINE}
}
