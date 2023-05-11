#!/bin/zsh
#
# A shell script to setup Codex CLI for zsh
#
# You can pass the following arguments to the script:
#   -o: Your OpenAI organization id.
#   -k: Your OpenAI API key.
#   -e: The OpenAI engine id that provides access to a model.
#   -a: The API type (openapi/azure).
#   -m: The Azure model deployment.
#   -p: The Azure API endpoint.
#   -v: The Azure API version.
#
# For example:
# ./zsh_setup.sh -o <YOUR_ORG_ID> -k <YOUR_API_KEY> -e <ENGINE_ID> -a <API_TYPE> -m <MODEL_DEPLOYMENT> -p <API_ENDPOINT> -v <API_VERSION>
# 
set -e

# Call OpenAI API with the given settings to verify everythin is in order
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
    local ENGINE_FOUND=$(echo "$TEST"|grep '"id"'|grep "\"$engineId\"")
    if [ -z "$ENGINE_FOUND" ]; then
        echo "ERROR"
        echo "Cannot find OpenAI engine: $engineId" 
        echo "Please check the OpenAI engine id (https://beta.openai.com/docs/engines/codex-series-private-beta)."
        echo "*************"

        exit 1
    fi
    echo "OK ***"
}

# Call Azure OpenAI API with the given settings to verify everythin is in order
validateAzureSettings()
{
    echo -n "*** Testing Open AI access... "
    local TEST=$(curl -s $apiBase"openai/deployments/$engineId/completions?api-version=$apiVersion" \
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
        echo "Please check your Azure OpenAI API key" 
        echo "and Endpoint URL."
        echo "*************"

        exit 1
    fi
    echo "OK ***"
}

# Append settings and 'Ctrl + G' binding in .zshrc
configureZsh()
{
    # Remove previous settings
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' '/### Codex CLI setup - start/,/### Codex CLI setup - end/d' $zshrcPath
    else
        sed -i -e '/### Codex CLI setup - start/,/### Codex CLI setup - end/d' $zshrcPath
    fi
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
    # Azure specific settings
    if [[ "$apiType" == "azure" ]]; then
        echo "api_base=$apiBase" >> $openAIConfigPath
        echo "api_version=$apiVersion" >> $openAIConfigPath
        echo "api_type=$apiType" >> $openAIConfigPath
    else
         echo "organization_id=$orgId" >> $openAIConfigPath
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
          e:=o_engineId \
          k:=o_key \
          a:=o_apiType \
          p:=o_apiBase \
          v:=o_apiVersion

if (( ${+o_apiType[2]} )); then
    apiType=${o_apiType[2]}
else
    echo -n 'API type (openapi/azure):'; read apiType
fi

# Check for Azure API settings if apiType is azure
if [[ "$apiType" == "azure" ]]; then
    if (( ${+o_apiBase[2]} )); then
        apiBase=${o_apiBase[2]}
    else
        echo -n 'Azure API Endpoint: '; read apiBase
    fi
    if (( ${+o_apiVersion[2]} )); then
        apiVersion=${o_apiVersion[2]}
    else
        echo -n 'Azure API Version: '; read apiVersion
    fi
else
    if (( ${+o_orgId[2]} )); then
        orgId=${o_orgId[2]}
    else
        echo -n 'OpenAI Organization Id: '; read orgId
    fi
fi
if (( ${+o_engineId[2]} )); then
        engineId=${o_engineId[2]}
    else
        echo -n 'OpenAI Engine Id or Azure model deployment: '; read engineId
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

if [[ "$apiType" == "azure" ]]; then
    validateAzureSettings
else
    validateSettings
fi

openAIConfigPath="$CODEX_CLI_PATH/src/openaiapirc"
zshrcPath="$HOME/.zshrc"

configureZsh
configureApp

echo -e "*** Setup complete! ***\n";

echo "***********************************************"
echo "Open a new zsh terminal, type '#' followed by"
echo "your natural language command and hit Ctrl + G!"
echo "***********************************************"