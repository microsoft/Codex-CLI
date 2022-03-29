create_completion() {
    # Get the text typed until now.
    text=${BUFFER}
    completion=$(echo -n "$text" | $NL_CLI_PATH/codex_query.py -c)
    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}

create_completion_without_context() {
    # Get the text typed until now.
    text=${BUFFER}
    completion=$(echo -n "$text" | $NL_CLI_PATH/codex_query.py)
    # Add completion to the current buffer.
    BUFFER="${text}${completion}"
    # Put the cursor at the end of the line.
    CURSOR=${#BUFFER}
}