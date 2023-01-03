#!/bin/zsh

# This ZSH plugin reads the text from the current buffer
# and uses a Python script to complete the text.

if [[ -z "$CODEX_CLI_PATH" ]];then
export CODEX_CLI_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../"
fi

create_completion() {
    # Get the text typed until now.
    text=${BUFFER}
    completion=$(echo -n "$text" | $CODEX_CLI_PATH/src/codex_query.py)
    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}

# Bind the create_completion function to a key.
zle -N create_completion

setopt interactivecomments
