#!/bin/bash

### Bash setup script

printf "*** Starting NL-CLI bash setup ***\n"

createOpenAIrc()
{
    mkdir -p $HOME/.config
    touch $HOME/.config/openaiapirc
    file=$HOME/.config/openaiapirc 

    echo '[openai]' >> $file
    echo "organization_id=$ORG_ID" >> $file
    echo "secret_key=$SECRET_KEY" >> $file
    echo "engine=..." >> $file

    unset SECRET_KEY
    unset ORG_ID
    unset file
}

updateBashrc() 
{
    local bashfile=$HOME/.bashrc
    ## backup the user's bashrc file 
    cp $HOME/.bashrc $HOME/.bashrc_

    ## Add NL-CLI features to bashrc file
    echo "export BSH_CUSTOM=${BSH_USER_PATH}" >> $bashfile ##testfile
    echo 'source $BSH_CUSTOM/NL-CLI/scripts/nl_cli.plugin.sh' >> $bashfile testfile

    ## unbind all related to ctrl+x key first then bind to ctrl+x 
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
  unset BSH_USER_PATH
  echo "In options function"
  while getopts ":p:s:h" opt ; do
      case "$opt" in
          p  )  # set custom User Path
              BSH_USER_PATH="$OPTARG"
              echo $BSH_USER_PATH
              ;;
          s  )  # script type (for future use)
              SHELL_TYPE="$OPTARG"
              echo $SHELL_TYPE
              ;;
          o  )  # organization ID 
              ORG_ID="$OPTARG"
              echo $ORG_ID
              ;;
          k  )  # secret key
             SECRET_KEY="$OPTARG"
             echo $SECRET_KEY
             ;;
          h  )  # echo the help file
              key="h"   
              help
              return 1
              ;;
          \? ) # 
              key="e"
              echo "Invalid option: -$OPTARG" >&2
              return 1
              ;;
      esac
  done
  shift $((OPTIND-1))

  # set defaults if a User Path not supplied
  echo "user $BSH_USER_PATH"
  if [ -z "$BSH_USER_PATH" ] ; then BSH_USER_PATH="$HOME/nl_cli" ; fi
  # if [ -z "$SHELL_TYPE" ] ; then SHELL_TYPE="bash" ; fi
}

##################
## *** Main *** ##
##################

## Script Menu Options ##
getOptions "$@"
# Tracking & return for help or wrong option selected
if [ "$key" = "h" ] || [ "$key" = "e" ]; then
    unset key
    return 1
fi

## Verifying and creating User defined Path ##
echo "Installing NL-CLI in directory: "
echo $BSH_USER_PATH
if [ ! -d "$BSH_USER_PATH" ]; then
    echo "$BSH_USER_PATH is not a valid directory; Creating directory..."
    mkdir -p "$BSH_USER_PATH"
fi

## "Installing NL-CLI" Cloning NL-CL repo ##

# 1. Download this project to `~/your/custom/path/`.
# Remove existing NL-CLI folder if exists
rm -rf "$BSH_USER_PATH/NL-CLI"
# $ git clone https://github.com/microsoft/NL-CLI.git ~/your/custom/path/
git clone https://github.com/microsoft/NL-CLI.git "$BSH_USER_PATH"

# 2. Add the custom lines in `~/.bashrc` file.
# Call update Bash function
updateBashrc

# 3. Create a file called `openaiapirc` in `~/.config` with your SECRET_KEY.
# Call create OpenAI function
createOpenAI 

return 0