################################################
## *** Codex CLI plugin function for Bash *** ##
##         loaded by $HOME/.codexclirc        ##
################################################

create_completion()
{
    # Check settings in case the CLI has just been uninstalled
    # Note: CODEX_CLI_PATH is defined in $HOME/.codexclirc
    local SETTINGS="$CODEX_CLI_PATH/src/openaiapirc"
    local SIZE=$(wc -c $SETTINGS | awk '{print $1}')
    if [ ! -f "$SETTINGS" ]; then
        echo "Codex CLI configuration is missing, try reinstalling."
        return
    fi
    if (( $SIZE < 10 )); then
        echo "Codex CLI configuration is missing, try reinstalling."
        return
    fi
    # Get the text typed until now
    text=${READLINE_LINE}
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

    # Add completion to the current buffer
    READLINE_LINE="${text}${completion}"
    # Put the cursor at the end of the line
    READLINE_POINT=${#READLINE_LINE}
}
