#!/bin/bash

printf "*** Starting NL-CLI bash setup ***\n"

## Set path to NL-CLI repo ##
BASH_NL_PATH=$(git rev-parse --show-toplevel)

#############################
## *** Setup Functions *** ##
#############################

hasOpenAIaccess() {
    local url=https://api.openai.com/v1/engines
    
    status=$(curl -w --head "$url" --write-out "%{http_code}" -s -o /dev/null -H 'Authorization: Bearer '$SECRET_KEY'' -H 'OpenAI-Organization: '$ORG_ID'')
}

resetAIOptions()
{
    unset ORG_ID
    unset SECRET_KEY
    unset ENGINE_ID

    read -p 'Organization ID: ' ORG_ID
    read -p 'OpenAI key: ' SECRET_KEY
    read -p 'Engine ID: ' ENGINE_ID
}

help() 
{
    # Display Help
   echo "Help for NL-CLI Bash Setup Options"
   echo
   echo "Syntax: nl_bash_setup [-h|o|k|e|s]"
   echo "options:"
   echo "h     Print this Help."
   echo "o     Set the OpenAI organization ID (required)"
   echo "k     Set the OpenAI API key (required)"
   echo "e     Set the OpenAI engine ID (required)"
   echo "s     Reset OpenAI options ex. Org ID & API key"
   echo
}

function getOptions 
{
    local OPTIND 
    showhelp=0
    echo "path: $BASH_NL_PATH"

    while getopts ":so:k:e:h" opt ; do
        case $opt in
            s  )  # reset OpenAI options
                resetAIOptions
                ;;
            o  )  # organization ID 
                ORG_ID="$OPTARG"
                ;;
            k  )  # secret key
                SECRET_KEY="$OPTARG"
                ;;
            e  )  # engine ID
                ENGINE_ID="$OPTARG"
                ;;
            h  )  # echo the help file
                help
                exit 0
                ;;
            \? ) # invalid options
                echo "Invalid option: -$OPTARG" >&2
                echo "Please see help (-h) for options"
                showhelp=1
                ;;
        esac
    done

    if ((OPTIND == 1)) 
    then
        showhelp=1
        echo "ERROR: No options were not specified"
        echo "Please provide required options. See help (-h) for info"
        return
    fi
    
    if [ -z "$ORG_ID" ]; then 
        showhelp=1
        echo "ERROR: **OpenAI Organization ID is required**"
    fi

    if [ -z "$SECRET_KEY" ]; then 
        showhelp=1 
        echo "ERROR: **OpenAI API Key is required**"
    fi

    if [ -z "$ENGINE_ID" ]; then 
        showhelp=1 
        echo "ERROR: **OpenAI Engine ID is required**"
    fi

    shift $((OPTIND-1))
}


createOpenAI()
{
    openAIfile=$BASH_NL_PATH/src/openaiapirc 
    if [ -f "$openAIfile" ]; then
        rm -f $openAIfile
    fi

    #mkdir -p $HOME/.config
    touch $openAIfile

    echo '[openai]' >> $openAIfile
    echo "organization_id=$ORG_ID" >> $openAIfile
    echo "secret_key=$SECRET_KEY" >> $openAIfile
    echo "engine=$ENGINE_ID" >> $openAIfile

    unset SECRET_KEY
    unset ORG_ID
    unset ENGINE_ID
    unset openAIfile
}

updateBashrc() 
{
    local bashfile=$HOME/.bashrc

    if grep -Fq "NL_CLI_PATH" $bashfile; then 
        # Configuration existed. skip update.
        return 0
    fi

    ## backup the user's bashrc file 
    cp $HOME/.bashrc $HOME/.bashrc__

    ## Add NL-CLI features to bashrc file
    echo "export NL_CLI_PATH=${BASH_NL_PATH}" >> $bashfile
    echo 'source $NL_CLI_PATH/scripts/bash_plugin.sh' >> $bashfile
    
    ## Key binding for ctrl+g
    echo "bind -x '\"\C-g\":\"create_completion\"'" >> $bashfile
    source $bashfile 
}

allowExecution()
{
    chmod +x "$BASH_NL_PATH/src/codex_query.py"
    echo "Allow execution of $BASH_NL_PATH/src/codex_query.py"
}

##################
## *** Main *** ##
##################

## Script Menu Options ##
getOptions "$@"

[[ $showhelp -eq 1 ]] && echo && help && exit 1


# Add the custom lines in `~/.bashrc` file.
# Call update Bash function
updateBashrc

# Test valid access to OpenAI Access with Organization & API Key
result=$(hasOpenAIaccess)


if [ $result -ne 200 ]; then 
    echo "*** ERROR ***"
    echo "Failed to access OpenAI api w/result: [$result]."
    echo "Please check your OpenAI API key (https://beta.openai.com/account/api-keys)" 
    echo "and Organization ID (https://beta.openai.com/account/org-settings)."
    echo "*************"
    exit 1
fi

echo "*** Validated OpenAI Access ***"
echo 
echo "Creating OpenAI config file.........."

# Create a file called `openaiapirc` in `~/.config` with your SECRET_KEY.
# Call create OpenAI function
createOpenAI

# Change file mode of codex_query.py to allow execution
allowExecution

echo "OpenAI config successfully created"
echo
echo "*******************************************************"
echo "**** NL-CL Bash Setup completed ****"
echo "Please open a new Bash terminal, type in # followed by"
echo "your natural language command and hit Ctrl+g!"
echo "********************************************************"