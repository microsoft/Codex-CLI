#!/bin/bash

### Bash setup script

printf "*** Starting NL-CLI bash setup ***\n"

updateBashrc() 
{
    local bashfile=$HOME/.bashrc
    echo "export BSH_CUSTOM=${USER_PATH}" >> $bashfile ##testfile
    echo 'source $BSH_CUSTOM/NL-CLI/scripts/nl_cli.plugin.sh' >> $bashfile testfile
    ## unbind all related to key first then bind to ctrl+x 
    bind -r "\C-x"
    echo 'bind -x "\C-x":create_completion' >> $bashfile #testfile
    source $bashfile 

}

help() 
{
    # Display Help
   echo "Help for NL-CLI Bash Setup Options"
   echo
   echo "Syntax: nl_bash_setup [-p|h|s|o|k]"
   echo "options:"
   echo "p     Set the path for NL-CLI. If path not provided default path ~/nl_cli is used"
   echo "h     Print this Help."
   echo "s     Set the Shell Type."
   echo "o     Set the OpenAI organization ID"
   echo "k     Set the OpenAI secret key"
   echo
}

function getOptions 
{
  local OPTIND
  unset USER_PATH
  unset key
  echo "In options function"
  while getopts ":p:s:h" opt ; do
      case "$opt" in
          p  )   # set custom User Path
              USER_PATH="$OPTARG"
              echo $USER_PATH
              ;;
          s  )   # Script type (for future use)
              SHELL_TYPE="$OPTARG"
              echo $SHELL_TYPE
              ;;
          o  ) 
              ORG_ID="$OPTARG"
              echo $ORG_ID
              ;;
          k  )
             SECRET_KEY="$OPTARG"
             echo $SECRET_KEY
             ;;
          h  )
              # echo the help file
              key="h"   
              help
              return 1
              ;;
          \? )
              key="e"
              echo "Invalid option: -$OPTARG" >&2
              return 1
              ;;
      esac
  done
  shift $((OPTIND-1))

  # set defaults if command not supplied
  echo "user $USER_PATH"
  if [ -z "$USER_PATH" ] ; then USER_PATH="$HOME/nl_cli" ; fi
  # if [ -z "$SHELL_TYPE" ] ; then SHELL_TYPE="bash" ; fi
}

## menu
getOptions "$@"
if [ "$key" = "h" ] || [ "$key" = "e" ]; then
    return 1
fi

echo $USER_PATH
if [ ! -d "$USER_PATH" ]; then
    echo "$USER_PATH is not a directory."
    mkdir -p "$USER_PATH"
fi

# Remove existing NL-CLI folder if exists
rm -rf "$USER_PATH/NL-CLI"

# 1. Download this project to `~/your/custom/path/`.
# ```
#     $ git clone https://github.com/microsoft/NL-CLI.git ~/your/custom/path/
# ```
git clone https://github.com/microsoft/NL-CLI.git "$USER_PATH"

# 2. Add the following to your `~/.bashrc` file.
#     # in your/custom/path you need to clone the repository
#     export ZSH_CUSTOM="your/custom/path" 
#     source "$ZSH_CUSTOM/NL-CLI/scripts/nl_cli.plugin.zsh"
#     bindkey '^X' create_completion

## updateBashrc


# 3. Create a file called `openaiapirc` in `~/.config` with your SECRET_KEY.
## Put this in a function - TEW
mkdir -p $HOME/.config
touch $HOME/.config/openaiapirc
file=$HOME/.config/openaiapirc 

echo '[openai]' >> $file
echo "organization_id=$ORG_ID" >> $file
echo "secret_key=$SECRET_KEY" >> $file
echo "engine=..." >> $file
