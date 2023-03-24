#!/bin/zsh
#
# A shell script to setup Codex CLI for zsh
#
# You can pass the following arguments to the script:
#   -o: Your OpenAI organization id.
#   -k: Your OpenAI API key.
#   -e: The OpenAI model id that provides access to a model.
#
# For example:
# ./zsh_setup.sh -o <YOUR_ORG_ID> -k <YOUR_API_KEY> -e <MODEL_ID>
# 
set -e

# Call OpenAI API with the given settings to verify everything is in order
# API call to https://api.openai.com/v1/engines is a potential risk in the future because the route is deprecated
validateSettings()
{
    echo -n "*** Testing Open AI access... "
    local TEST=$(curl -s 'https://api.openai.com/v1/engines' -H "Authorization: Bearer $secret" -H "OpenAI-Organization: $orgId" -w '%{http_code}')
    local STATUS_CODE=$(echo "$TEST"|tail -n 1)
    if [ $STATUS_CODE -ne 200 ]; then
        echo "ERROR [$STATUS_CODE]"
        echo "Failed to access OpenAI API, result: $STATUS_CODE"
        echo "Please check your OpenAI API key (https://beta.openai.com/account/api-keys)" 
        echo "and Organization ID (https://beta.openai.com/account/org-settings)."
        echo "*************"

        exit 1
    fi
    local MODEL_FOUND=$(echo "$TEST"|grep '"id"'|grep "\"$modelID\"")
    if [ -z "$MODEL_FOUND" ]; then
        echo "ERROR"
        echo "Cannot find OpenAI model: $modelID" 
        echo "Please check the OpenAI model id (https://platform.openai.com/docs/models/gpt-4)."
        echo "*************"

        exit 1
    fi
    echo "OK ***"
}

# Append settings and 'Ctrl + G' binding in .zshrc
configureZsh()
{
    # Remove previous settings
    sed -i '' '/### Codex CLI setup - start/,/### Codex CLI setup - end/d' $zshrcPath
    echo "Removed previous settings in $zshrcPath if present"

    # Update the latest settings
    echo "### Codex CLI setup - start" >> $zshrcPath
    echo "export CODEX_CLI_PATH=$CODEX_CLI_PATH" >> $zshrcPath
    echo "source \"\$CODEX_CLI_PATH/scripts/zsh_plugin.zsh\"" >> $zshrcPath
    echo "bindkey '^G' create_completion" >> $zshrcPath
    echo "### Codex CLI setup - end" >> $zshrcPath
    
    echo "Added settings in $zshrcPath"
}

# Store API key and other settings in `openaiapirc`
configureApp()
{
    echo "[openai]" > $openAIConfigPath
    echo "organization_id=$orgId" >> $openAIConfigPath
    echo "secret_key=$secret" >> $openAIConfigPath
    echo "model=$modelID" >> $openAIConfigPath
    
    echo "Updated OpenAI configuration file ($openAIConfigPath) with secrets"

    # Change file mode of codex_query.py to allow execution
    chmod +x "$CODEX_CLI_PATH/src/codex_query.py"
    echo "Allow execution of $CODEX_CLI_PATH/src/codex_query.py"
}

# Start installation
# Use zparseopts to parse parameters
zmodload zsh/zutil
zparseopts -E -D -- \
          o:=o_orgId \
          m:=o_modelId \
          k:=o_key

if (( ${+o_orgId[2]} )); then
    orgId=${o_orgId[2]}
else
    echo -n 'OpenAI Organization Id: '; read orgId
fi

if (( ${+m_modelId[2]} )); then
    modelId=${o_modelId[2]}
else
    echo -n 'OpenAI Model Id: '; read modelId
fi

if (( ${+o_key[2]} )); then
    secret=${o_key[2]}
else
   # Prompt user for OpenAI access key
   read -rs 'secret?OpenAI access key:'
   echo -e "\n"
fi

# Detect Codex CLI folder path
CODEX_CLI_PATH="$( cd "$( dirname "$0" )" && cd .. && pwd )"
echo "CODEX_CLI_PATH is $CODEX_CLI_PATH"

validateSettings

openAIConfigPath="$CODEX_CLI_PATH/src/openaiapirc"
zshrcPath="$HOME/.zshrc"

configureZsh
configureApp

echo -e "*** Setup complete! ***\n";

echo "***********************************************"
echo "Open a new zsh terminal, type '#' followed by"
echo "your natural language command and hit Ctrl + G!"
echo "***********************************************"