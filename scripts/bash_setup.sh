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
    #local status="test OpenAI call"
    #echo "stat code: $status"
    echo $status
}

resetAIOptions()
{
    #echo "testing"
    unset ORG_ID
    unset SECRET_KEY

    read -p 'Organization ID: ' ORG_ID
    read -p 'OpenAI key: ' SECRET_KEY

    #echo $ORG_ID
    #echo $SECRET_KEY
}

help() 
{
    # Display Help
   echo "Help for NL-CLI Bash Setup Options"
   echo
   echo "Syntax: nl_bash_setup [-h|o|k|s]"
   echo "options:"
   echo "h     Print this Help."
   echo "o     Set the OpenAI organization ID (required)"
   echo "k     Set the OpenAI API key (required)"
   echo "s     Reset OpenAI options ex. Org ID & API key"
   echo
}

function getOptions 
{
    local OPTIND 
    showhelp=0
    echo "path: $BASH_NL_PATH"

    while getopts ":so:k:h" opt ; do
        case $opt in
            s  )  # script type (for future use)
                key="s"
                resetAIOptions
                ;;
            o  )  # organization ID 
                ORG_ID="$OPTARG"
                #echo $ORG_ID
                ;;
            k  )  # secret key
                SECRET_KEY="$OPTARG"
                #echo $SECRET_KEY
                ;;
            h  )  # echo the help file
                key="h"   
                help
                return 1
                ;;
            \? ) # 
                key="e"
                echo "Invalid option: -$OPTARG" >&2
                echo "Please see help (-h) for options"
                echo 
                return 1
                ;;
        esac
    done

    if ((OPTIND == 1)) 
    then
        echo "ERROR: No options were not specified"
        echo "Please provide required options. See help (-h) for info"
        echo
        showhelp=1 
        return
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
    #echo $showhelp
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
    cp $HOME/.bashrc $HOME/.bashrc__

    ## Add NL-CLI features to bashrc file
    echo "export BSH_CUSTOM=${BASH_NL_PATH}" >> $bashfile
    echo 'source $BSH_CUSTOM/scripts/bash_plugin.sh' >> $bashfile
    
    ## unbind all related to ctrl+x key first then bind to ctrl+x 
    # TODO: test effect of removing since handling signal 
    echo 'bind -x '"\C-g"':create_completion' >> $bashfile
    source $bashfile 

}


##################
## *** Main *** ##
##################

## Script Menu Options ##
getOptions "$@"

## Track option selected and respond accordingly
## If error show help to user
case $key in
    e|h )
        unset key
        return 1;;
    s ) 
        unset key;;
esac

[[ $showhelp -eq 1 ]] && help && return 1

#Testing function calls 
#testpath

# Add the custom lines in `~/.bashrc` file.
# Call update Bash function
# updateBashrc

#Test valid access to OpenAI Access with Organization & API Key
result=$(hasOpenAIaccess)
echo "OpenAI: $result"

if [ $result != 200 ]; then 
    echo "*** ERROR ***"
    echo "Failed to access OpenAI api w/result: [$result]."
    echo "Please check your OpenAI API key (https://beta.openai.com/account/api-keys)" 
    echo "and Organization ID (https://beta.openai.com/account/org-settings)."
    echo "*************"
    return 1
fi

echo "*** Validated OpenAI Access ***"
echo 
echo "Creating OpenAI config file.........."

# Create a file called `openaiapirc` in `~/.config` with your SECRET_KEY.
# Call create OpenAI function
createOpenAI
echo "*** OpenAI config successfully created"
echo
echo "*******************************************************"
echo "**** NL-CL Bash Setup completed ****"
echo "Please open a new Bash terminal, type in # followed by"
echo "your natural language command and hit Ctrl+g!"
echo "********************************************************"