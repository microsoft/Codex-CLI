#!/bin/bash

## *** Cleanup Script *** ##

## Remove the openaiapirc file ##
rmdir -f $HOME/.config/openaiapirc

## Remove the env variables ##
unset BSH_USER_PATH
unset SHELL_TYPE

## Restore the original user bashrc file ##
# Verify backup bashrc exists BEFORE removing and replacing bashrc
bkupBash=$HOME/.bashrc_
currBash=$HOME/.bashrc
if [ -f "$bkupBash" ]; then
    rm -f $currBash
    mv $bkupBash $currBash
fi
