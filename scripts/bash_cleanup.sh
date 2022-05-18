#!/usr/bin/env bash

uninstall()
{
    # Path to Codex CLI source
    local CODEX_CLI_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
    # Path to OpenAI API settings
    local OPENAI_RC_FILE="$CODEX_CLI_PATH/src/openaiapirc"
    # Path to Bash settings loaded when a Bash session starts
    local BASH_RC_FILE="$HOME/.codexclirc"
    # Remove the plugin loaded by .bashrc
    rm -f $BASH_RC_FILE
    # Remove credentials and other personal settings
    rm -f $OPENAI_RC_FILE
    # Remove key binding (works only for sourced script calls)
    if [ $SOURCED -eq 1 ]; then
        bind -r "\C-g"
    fi

    echo "Codex CLI has been removed."
}

# Detect if the script is sourced
(return 0 2>/dev/null) && SOURCED=1 || SOURCED=0

uninstall

unset SOURCED
