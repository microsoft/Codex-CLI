#!/bin/zsh
#
# A shell script to setup Codex CLI for zsh
#
# You can pass the following arguments to the script:
#   -k: Your Azure OpenAI API key.
#   -e: The OpenAI engine id that provides access to a model.
#
# For example:
# ./zsh_setup.sh -k <YOUR_API_KEY> -e <ENGINE_ID>
# 
set -e

# Call OpenAI API with the given settings to verify everythin is in order
validateSettings()
{
    echo -n "*** Testing Open AI access... "
    local TEST=$(curl -s $baseUrl"openai/deployments/$engineId/completions?api-version=$apiVersion" \
        -H "Content-Type: application/json" \
        -H "api-key: $secret" \
        -d '{
        "prompt": "This is a test",
        "max_tokens": 250,
        "temperature": 0.7,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "top_p": 1,
        "best_of": 1,
        "stop": null
        }' -w '%{http_code}')
    local STATUS_CODE=$(echo "$TEST"|tail -n 1)
    if [ $STATUS_CODE -ne 200 ]; then
        echo "ERROR [$STATUS_CODE]"
        echo "Failed to access OpenAI API, result: $STATUS_CODE"
        echo "Please check your OpenAI API key (https://beta.openai.com/account/api-keys)" 
        echo "and Organization ID (https://beta.openai.com/account/org-settings)."
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
    echo "secret_key=$secret" >> $openAIConfigPath
    echo "engine=$engineId" >> $openAIConfigPath
    echo "base_url=$baseUrl" >> $openAIConfigPath
    echo "api_version=$apiVersion" >> $openAIConfigPath
    
    echo "Updated OpenAI configuration file ($openAIConfigPath) with secrets"

    # Change file mode of codex_query.py to allow execution
    chmod +x "$CODEX_CLI_PATH/src/codex_query.py"
    echo "Allow execution of $CODEX_CLI_PATH/src/codex_query.py"
}

# Start installation
# Use zparseopts to parse parameters
zmodload zsh/zutil
zparseopts -E -D -- \
          e:=o_engineId \
          k:=o_key \
          b:=o_baseUrl \
          a:=o_apiVersion 

if (( ${+o_engineId[2]} )); then
    engineId=${o_engineId[2]}
else
    echo -n 'OpenAI Engine Id: '; read engineId
fi

if (( ${+o_key[2]} )); then
    secret=${o_key[2]}
else
   # Prompt user for Azure OpenAI access key
   read -rs 'secret?Azure OpenAI access key:'
   echo -e "\n"
fi

if (( ${+o_baseUrl[2]} )); then
    baseUrl=${o_baseUrl[2]}
else
    echo -n 'API base url: '; read baseUrl
fi

if (( ${+o_apiVersion[2]} )); then
    apiVersion=${o_apiVersion[2]}
else
    echo -n 'API version: '; read apiVersion
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