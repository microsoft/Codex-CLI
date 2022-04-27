#!/bin/zsh
#
# A shell script to setup NL-CLI for zsh
#
# You can pass the following arguments to the script:
#   --OpenAIOrganizationId: Required. Your OpenAI organization id.
#   --OpenAIEngineId: Required. The OpenAI engine id that provides access to a model.
#   --RepoRoot: Optional. Default to the current folder. The value should be the path of NL-CLI folder.
# For example:
# ./zsh_setup.sh --OpenAIOrganizationId <YOUR_ORG_ID> --OpenAIEngineId <ENGINE_ID> --RepoRoot /Code/NL-CLI
# 
set -e

# Use zparseopts to parse parameters
zmodload zsh/zutil
zparseopts -E -D -- \
           -OpenAIOrganizationId:=o_orgId \
           -OpenAIEngineId:=o_engineId \
           -RepoRoot:=o_repoRoot

echo "${o_orgId[2]}, ${o_engineId[2]}, ${o_repoRoot[2]}"

orgId=""
if (( ${+o_orgId[2]} )); then
    orgId=${o_orgId[2]}
else
    echo "Error: --OpenAIOrganizationId is required."
    exit 1
fi

engineId=""
if (( ${+o_engineId[2]} )); then
    engineId=${o_engineId[2]}
else
    echo "Error: --OpenAIEngineId is required."
    exit 1
fi

repoRoot=""
if (( ${+o_repoRoot[2]} )); then
    repoRoot=${o_repoRoot[2]}
else
    repoRoot=$PWD
fi
echo "RepoRoot is $repoRoot"

# Prompt user for OpenAI access key
read -rs 'secret?OpenAI access key:'

openAIConfigPath="$HOME/.config/openaiapirc"
zshrcPath="$HOME/.zshrc"

# 1. Append settings in .zshrc
# Remove previous settings
sed -i '' '/### NL-CLI setup - start/,/### NL-CLI setup - end/d' $zshrcPath
echo "Removed previous settings in $zshrcPath if present"

# Update the latest settings
echo "### NL-CLI setup - start
export ZSH_CUSTOM=$repoRoot
source \"\$ZSH_CUSTOM/scripts/nl_cli.plugin.zsh\"
bindkey '^G' create_completion
### NL-CLI setup - end" >> $zshrcPath   
echo "Added settings in $zshrcPath"

# 2. Create opanaiapirc in /.config for secrects
echo "[openai]
organization_id=$orgId
secret_key=$secret
engine=$engineId" > $openAIConfigPath
echo "Updated OpenAI configuration file ($openAIConfigPath) with secrets"

# Change file mode of codex_query.py to allow execution
chmod +x "$repoRoot/src/codex_query.py"
echo "Allow execution of $repoRoot/src/codex_query.py"

echo "zsh setup completed. Please open a new zsh to use NL-CLI."