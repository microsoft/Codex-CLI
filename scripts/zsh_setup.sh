#!/bin/zsh
#
# A shell script to setup Codex CLI for zsh
#
# You can pass the following arguments to the script:
#   -o: Your OpenAI organization id.
#   -k: Your OpenAI API key.
#   -b: The API base URL.
#   -m: The model id.
#   -e: Legacy alias for -m.
#
# For example:
# ./zsh_setup.sh -o <YOUR_ORG_ID> -k <YOUR_API_KEY> -b <BASE_URL> -m <MODEL_ID>
# 
set -e

# Validate the settings before writing the configuration file
validateSettings()
{
    echo -n "*** Validating API settings... "
    if [ -z "$secret" ] || [ -z "$baseUrl" ] || [ -z "$modelId" ]; then
        echo "ERROR"
        echo "API key, base URL, and model id are required."
        echo "*************"
        exit 1
    fi
    case "$baseUrl" in
        http://* | https://* ) ;;
        * )
            echo "ERROR"
            echo "API base URL must start with http:// or https://."
            echo "*************"
            exit 1
            ;;
    esac
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
    echo "base_url=$baseUrl" >> $openAIConfigPath
    echo "model=$modelId" >> $openAIConfigPath
    
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
          b:=o_baseUrl \
          m:=o_modelId \
          e:=o_engineId \
          k:=o_key

if (( ${+o_orgId[2]} )); then
    orgId=${o_orgId[2]}
else
    echo -n 'OpenAI Organization Id: '; read orgId
fi

if (( ${+o_baseUrl[2]} )); then
    baseUrl=${o_baseUrl[2]}
else
    echo -n 'API base URL: '; read baseUrl
fi

if (( ${+o_modelId[2]} )); then
    modelId=${o_modelId[2]}
elif (( ${+o_engineId[2]} )); then
    modelId=${o_engineId[2]}
else
    echo -n 'Model Id: '; read modelId
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
