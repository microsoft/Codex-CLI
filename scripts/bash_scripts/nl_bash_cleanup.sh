#!/bin/bash

## *** Cleanup Script *** ##

## Remove the openairc folder
rmdir -rf $HOME/.config

## Remove the env variables 
unset BSH_USER_PATH
unset SHELL_TYPE

## Restore the original user bashrc file
# Verify backup bashrc exists BEFORE removing and replacing
bkupBash=$HOME/.bashrc_
currBash=$HOME/.bashrc
if [ -f "$bkupBash" ]; then
    rm -f $currBash
    mv $bkupBash $currBash
fi
