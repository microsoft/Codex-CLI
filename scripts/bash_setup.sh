#!/usr/bin/env bash

set -e
trap 'exitScript' ERR

help()
{
    cat <<- _EOF_
Help for Codex CLI Bash setup script

Usage: source bash_setup.sh [optional parameters]

    -o orgId     Set the OpenAI organization id.
    -k apiKey    Set the OpenAI API key.
    -e engineId  Set the OpenAI engine id.
    -d           Print some system information for debugging.
    -h           Print this help content.

To uninstall Codex CLI use bash_cleanup.sh.
For more information visit https://github.com/microsoft/Codex-CLI
_EOF_
}

# Read command line parameters
readParameters()
{
    while [ "$1" != "" ]; do
        case $1 in
            -o ) shift; ORG_ID=$1 ;;
            -k ) shift; SECRET_KEY=$1 ;;
            -e ) shift; ENGINE_ID=$1 ;;
            -d ) systemInfo
                 exitScript
                ;;
            * ) help
                exitScript
                ;;
        esac
        shift
    done
}

# Prompt user for OpenAI settings
askSettings()
{
    echo "*** Starting Codex CLI bash setup ***"
    if [ -z "$ORG_ID" ]; then
        echo -n 'OpenAI Organization Id: '; read ORG_ID
    fi
    if [ -z "$SECRET_KEY" ]; then
        echo -n 'OpenAI API key: '; read -s SECRET_KEY; echo
    fi
    if [ -z "$ENGINE_ID" ]; then
        echo -n 'OpenAI Engine Id: '; read ENGINE_ID
    fi
}

# Call OpenAI API with the given settings to verify everythin is in order
validateSettings()
{
    echo -n "*** Testing Open AI access... "
    local TEST=$(curl -s 'https://api.openai.com/v1/engines' -H "Authorization: Bearer $SECRET_KEY" -H "OpenAI-Organization: $ORG_ID" -w '%{http_code}')
    local STATUS_CODE=$(echo "$TEST"|tail -n 1)
    if [ $STATUS_CODE -ne 200 ]; then
        echo "ERROR [$STATUS_CODE]"
        echo "Failed to access OpenAI API, result: $STATUS_CODE"
        echo "Please check your OpenAI API key (https://beta.openai.com/account/api-keys)" 
        echo "and Organization ID (https://beta.openai.com/account/org-settings)."
        echo "*************"
        exitScript
        return
    fi
    local ENGINE_FOUND=$(echo "$TEST"|grep '"id"'|grep "\"$ENGINE_ID\"")
    if [ -z "$ENGINE_FOUND" ]; then
        echo "ERROR"
        echo "Cannot find OpenAI engine: $ENGINE_ID" 
        echo "Please check the OpenAI engine id (https://beta.openai.com/docs/engines/codex-series-private-beta)."
        echo "*************"
        exitScript
        return
    fi
    echo "OK ***"
}

# Store API key and other settings in `openaiapirc`
configureApp()
{
    local BASH_NL_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )/"
    echo "*** Configuring application [$BASH_NL_PATH/src/openaiapirc] ***"
    chmod +x "$BASH_NL_PATH/src/codex_query.py"
    echo -n > $BASH_NL_PATH/src/openaiapirc
    echo '[openai]' >> $BASH_NL_PATH/src/openaiapirc
    echo "organization_id=$ORG_ID" >> $BASH_NL_PATH/src/openaiapirc
    echo "secret_key=$SECRET_KEY" >> $BASH_NL_PATH/src/openaiapirc
    echo "engine=$ENGINE_ID" >> $BASH_NL_PATH/src/openaiapirc
}

# Create and load ~/.openairc to setup bash CTRL-g binding
configureBash()
{
    echo "*** Configuring bash [$HOME/.openairc] ***"
    local BASH_NL_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )/"
    echo -n > $HOME/.openairc
    echo "export NL_CLI_PATH=\"${BASH_NL_PATH}\"" >> $HOME/.openairc
    echo 'source "$NL_CLI_PATH/scripts/bash_plugin.sh"' >> $HOME/.openairc
    echo "bind -x '\"\C-g\":\"create_completion\"'" >> $HOME/.openairc
    if [ $SOURCED -eq 1 ]; then
        echo "*** Testing bash settings [$HOME/.openairc] ***"
        source "$HOME/.openairc"
    fi
}

# Add call to .openairc into .bashrc
enableApp()
{
    echo "*** Activating application [$HOME/.bashrc] ***"
    # Check if already installed
    if grep -Fq ".openairc" $HOME/.bashrc; then 
        return 0
    fi
    echo -e "\n# Initialize Codex CLI" >> $HOME/.bashrc
    echo 'if [ -f "$HOME/.openairc" ]; then' >> $HOME/.bashrc
    echo '    . "$HOME/.openairc"' >> $HOME/.bashrc
    echo 'fi' >> $HOME/.bashrc
}

# Print some system details useful to debug the script in case it's not working
systemInfo()
{
    echo "*** system ***"
    uname -smpr
    echo "*** shell ***"
    echo $SHELL
    echo "*** bash interpreter ***"
    echo $BASH_VERSION
    echo "*** python ***"
    if command -v python &> /dev/null; then
        which python
        python --version
    else
        echo "python not found"
    fi
    echo "*** curl ***"
    if command -v curl &> /dev/null; then
        which curl
        curl --version
    else
        echo "curl not found"
    fi
}

# Remove variables and functions from the environment, in case the script was sourced
cleanupEnv()
{
    unset ORG_ID SECRET_KEY ENGINE_ID SOURCED
    unset -f askSettings validateSettings configureApp configureBash enableApp readParameters
}

# Clean exit for sourced scripts
exitScript()
{
    cleanupEnv
    kill -SIGINT $$
}

# Detect if the script is sourced
(return 0 2>/dev/null) && SOURCED=1 || SOURCED=0

readParameters $*
askSettings
validateSettings
configureApp
configureBash
enableApp
cleanupEnv

echo -e "*** Setup complete! ***\n";

echo "**********************************************"
echo "Open a new Bash terminal, type '#' followed by"
echo "your natural language command and hit Ctrl+g!"
echo "**********************************************"
