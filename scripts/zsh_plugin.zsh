#!/bin/zsh

# This ZSH plugin reads the text from the current buffer 
# and uses a Python script to complete the text.

create_completion() {
    # Get the text typed until now.
    text=${BUFFER}
    completion=$(echo -n "$text" | $CODEX_CLI_PATH/src/codex_query.py)


    # add # to the beginning of $text if it doesnt start with #
    # get the first non whitespace char
    # first_char=$(echo $line | sed -e 's/^[[:space:]]*//')
    # get the first char of the line
    first_char=$(echo $text | cut -c 1)
    if [ "$first_char" != "#" ]; then
       text="# $text"
    fi
    # note: add multiline fix

    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}

# Bind the create_completion function to a key.
zle -N create_completion

setopt interactivecomments