#!/bin/zsh

# This ZSH plugin reads the text from the current buffer 
# and uses a Python script to complete the text.

# accept an argument to specify a boolean
create_completion() {
    # Get the text typed until now.
    text=${BUFFER}
    completion=$(echo -n "$text" | $ZSH_CUSTOM/codex_query.py -c)
    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}

create_completion_without_context() {
    # Get the text typed until now.
    text=${BUFFER}
    completion=$(echo -n "$text" | $ZSH_CUSTOM/codex_query.py)
    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}

# Bind the create_completion function to a key.
zle -N create_completion
zle -N create_completion_without_context