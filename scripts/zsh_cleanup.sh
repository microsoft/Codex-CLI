#!/bin/zsh
#
# A shell script to clean up the setup of Codex CLI for zsh
# 
set -e

openAIConfigPath="$PWD/src/openaiapirc"
zshrcPath="$HOME/.zshrc"

# 1. Remove settings in .zshrc
sed -i '' '/### Codex CLI setup - start/,/### Codex CLI setup - end/d' $zshrcPath
echo "Removed settings in $zshrcPath if present"

# 2. Remove opanaiapirc in /.config
rm -f $openAIConfigPath
echo "Removed $openAIConfigPath"

echo "Codex CLI clean up completed. Please open a new zsh to continue."