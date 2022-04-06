#!/bin/zsh
#
# A shell script to setup NL-CLI for zsh
#
# You can pass the following arguments to the script:
#   --RepoRoot: Optional. Default to the current folder. The value should be the path of NL-CLI folder.
# For example:
# sh zsh_setup.sh --RepoRoot /Code/NL-CLI
# 
set -e

# Parse parameters
zparseopts -E -D -- \
           -RepoRoot:=o_repoRoot \

# Prompt user for OpenAI access key
read -rs 'secret?OpenAI access key:'

openAIConfigPath="$HOME/.config/openaiapirc"
zshrcPath="$HOME/.zshrc"

repoRoot=""
if [[ -v ${o_repoRoot[2]} ]]; then
    repoRoot=${o_repoRoot[2]}
else
    repoRoot=$PWD
fi

echo "RepoRoot is $repoRoot"

# 1. Append settings in .zshrc
# Remove previous settings
sed -i '' '/### NL-CLI setup - start/,/### NL-CLI setup - end/d' $zshrcPath
echo "Removed previous settings in $zshrcPath if present"

# Update the latest settings
echo "### NL-CLI setup - start
export ZSH_CUSTOM=$repoRoot
source \"\$ZSH_CUSTOM/nl_cli.plugin.zsh\"
bindkey '^X' create_completion
### NL-CLI setup - end" >> $zshrcPath   
echo "Added settings in $zshrcPath"

# 2. Create opanaiapirc in /.config for secrects
echo "[openai]
secret_key=${secret}" > $openAIConfigPath
echo "Updated OpenAI configuration file ($openAIConfigPath) with secrets"

# Change file mode of codex_query.py to allow execution
chmod +x "$repoRoot/codex_query.py"
echo "Allow execution of $repoRoot/codex_query.py"

echo "zsh setup completed. Please open a new zsh to use NL-CLI."