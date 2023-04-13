#!/bin/zsh
#
# A shell script to clean up the setup of Codex CLI for zsh
# 
set -e

CODEX_CLI_PATH="$( cd "$( dirname "$0" )" && cd .. && pwd )"
openAIConfigPath="$CODEX_CLI_PATH/src/openaiapirc"
zshrcPath="$HOME/.zshrc"

# 1. Remove settings in .zshrc
# Check if the current system is Darwin (i.e. MacOS)
if [[ "$OSTYPE" == "Darwin" ]]; then
    # Command to execute on MacOS
    sed -i '' '/### Codex CLI setup - start/,/### Codex CLI setup - end/d' $zshrcPath
else
    # Command to execute on Linux
    sed -i '/### Codex CLI setup - start/,/### Codex CLI setup - end/d' $zshrcPath
fi
echo "Removed settings in $zshrcPath if present"

# 2. Remove opanaiapirc in /.config
rm -f $openAIConfigPath
echo "Removed $openAIConfigPath"

echo "Codex CLI clean up completed. Please open a new zsh to continue."
