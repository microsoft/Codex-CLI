#!/bin/bash

#############################################
## *** NL-CLI Cleanup Script for Bash *** ##
#############################################

## Remove the openaiapirc file ##
rm -f $NL_CLI_PATH/src/openaiapirc

## Remove the env variables ##
unset NL_CLI_PATH
unset BASH_NL_PATH


## Restore the original user bashrc file ##
# Verify backup bashrc exists BEFORE removing and replacing bashrc
bkupBash=$HOME/.bashrc__
currBash=$HOME/.bashrc
if [ -f "$bkupBash" ]; then
    rm -f $currBash
    mv $bkupBash $currBash
fi
