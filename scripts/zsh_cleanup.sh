#!/bin/zsh
#
# A shell script to clean up the setup of NL-CLI for zsh
# 
set -e

openAIConfigPath="$HOME/.config/openaiapirc"
zshrcPath="$HOME/.zshrc"

# 1. Remove settings in .zshrc
sed -i '' '/### NL-CLI setup - start/,/### NL-CLI setup - end/d' $zshrcPath
echo "Removed settings in $zshrcPath if present"

# 2. Remove opanaiapirc in /.config
rm -f $openAIConfigPath
echo "Removed $openAIConfigPath"

echo "NL-CLI clean up completed. Please open a new zsh to continune."