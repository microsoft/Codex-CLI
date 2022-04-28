#!/bin/bash

printf "*** Starting NL-CLI bash setup ***\n"

## Set path to NL-CLI repo ##
BASH_NL_PATH=$(git rev-parse --show-toplevel)

#############################
## *** Setup Functions *** ##
#############################

help() 
{
    # Display Help
   echo "Help for NL-CLI Bash Setup Options"
   echo
   echo "Syntax: nl_bash_setup [-h|o|k]"
   echo "options:"
   echo "h     Print this Help."
   echo "o     Set the OpenAI organization ID (required)"
   echo "k     Set the OpenAI API key (required)"
   echo
}

function getOptions 
{
    local OPTIND 
    showhelp=0
    #echo "path: $BASH_NL_PATH"

    ##echo "In options function"
    while getopts ":o:k:h" opt ; do
        case "$opt" in
            o  )  # organization ID 
                ORG_ID="$OPTARG"
                ;;
            k  )  # secret key
                SECRET_KEY="$OPTARG"
                #[ -z "$SECRET_KEY" ] && showhelp=1
                ;;
            h  )  # echo the help file
                key="h"   
                help
                return 1
                ;;
            \? ) # Invalid option
                key="e"
                echo "Invalid option: -$OPTARG" >&2
                return 1
                ;;
        esac
    done
 
    if ((OPTIND == 1)) 
    then
        echo "ERROR: Required options were not specified"
        showhelp=1 
    fi
    
    if [ -z "$ORG_ID" ]; then 
        showhelp=1
        echo "ERROR: **Organization ID is required**"
    fi

    if [ -z "$SECRET_KEY" ]; then 
        showhelp=1 
        echo "ERROR: **OpenAI API Key is required**"
    fi        

    shift $((OPTIND-1))

}

resetOpenAI()
{
    unset ORG_ID
    unset SECRET_KEY

    read -p 'Organization ID: ' ORG_ID
    read -p 'OpenAI key: ' SECRET_KEY

    echo $ORG_ID
    echo $SECRET_KEY
}

createOpenAI()
{
    openAIfile=$HOME/.config/openaiapirc 
    if [ -f "$openAIfile" ]; then
        rm -f $openAIfile
    fi

    mkdir -p $HOME/.config
    touch $HOME/.config/openaiapirc
   

    echo '[openai]' >> $openAIfile
    echo "organization_id=$ORG_ID" >> $openAIfile
    echo "secret_key=$SECRET_KEY" >> $openAIfile
    echo "engine= " >> $openAIfile

    unset SECRET_KEY
    unset ORG_ID
    unset openAIfile
}

updateBashrc() 
{
    local bashfile=$HOME/.bashrc

    if grep -Fq "BSH_CUSTOM" $bashfile; then 
        #echo "what? "
        return 0
    fi

    #echo "U passed?"
    ## backup the user's bashrc file 
    cp $HOME/.bashrc $HOME/.bashrc_

    ## Add NL-CLI features to bashrc file
    echo "export BSH_CUSTOM=${BASH_NL_PATH}" >> $bashfile
    echo 'source $BSH_CUSTOM/scripts/bash_plugin.sh' >> $bashfile
    
    ## unbind all related to ctrl+x key first then bind to ctrl+x 
    # TODO: test effect of removing since handling signal 
    echo 'bind -x '"\C-g"':create_completion' >> $bashfile
    source $bashfile 

}

# testpath()
# {
#     echo "testing"
#     echo "$BASH_NL_PATH"
# }

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

#echo $showhelp
[ showhelp ] && help
#Testing function calls 
#testpath

# Add the custom lines in `~/.bashrc` file.
# Call update Bash function
updateBashrc


# Create a file called `openaiapirc` in `~/.config` with your SECRET_KEY.
# Call create OpenAI function
createOpenAI 