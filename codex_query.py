#!/usr/bin/env python3

# TODO consider running this file as a daemon/service so it can be run in the background

import openai
import sys
import os
import configparser
import time
import re
import psutil

from pathlib import Path

# check if parent process is powershell
POWERSHELL_MODE = bool(re.fullmatch('pwsh|pwsh.exe|powershell.exe', psutil.Process(os.getppid()).name()))
BASH_MODE = (POWERSHELL_MODE == False)

# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')

PROMPT_CONTEXT = Path(__file__).with_name('openai_completion_input.txt')

# Read the organization_id and secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization_id=<your organization ID>
# secret_key=<your secret key>

# If you don't see your organization ID in the file you can get it from the
# OpenAI web site: https://openai.com/organizations
def create_template_ini_file():
    """
    If the ini file does not exist create it and add the organization_id and
    secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')

        print('OpenAI API config file created at {}'.format(API_KEYS_LOCATION))
        print('Please edit it and add your organization ID and secret key')
        print('If you do not yet have an organization ID and secret key, you\n'
        'need to register for OpenAI Codex: \n'
        'https://openai.com/blog/openai-codex/')
        sys.exit(1)


def initialize_openai_api():
    """
    Initialize the OpenAI API
    """
    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")

def get_updated_prompt_file(input):
    """
    Get the updated prompt file
    Checks for token overflow and appends the current input

    Returns: the prompt file after appending the input
    """

    input_tokens_number = len(input.split())
    need_to_refresh = False

    # TODO potentially have file cache or header for tracking this count instead of reading the file every time
    # count number of words in temp file
    with PROMPT_CONTEXT.open('r') as f:
        num_words = len(f.read().split())
        if num_words + input_tokens_number > 2048:
            need_to_refresh = True

    if need_to_refresh:
        # TODO use multi-line metadata and dependency metadata to track this
        # delete first 2 lines of prompt context file
        with PROMPT_CONTEXT.open('r') as f:
            lines = f.readlines()
            lines = lines[2:]
        with PROMPT_CONTEXT.open('w') as f:
            f.writelines(lines)

    # append input to prompt context file
    with PROMPT_CONTEXT.open('a') as f:
        f.write(input)
        f.close()

    prompt = ""
    # get input from prompt file
    with PROMPT_CONTEXT.open('r') as f:
        prompt = f.read()

    return prompt

def get_command_result(input):
    """
    Checks if the input is a command and if so, executes it
    Currently supported commands:
    - unlearn
    - unlearn all
    - show context
    - edit context
    - save context
    - clear context

    Returns: command result or "" if no command matched
    """

    # TODO allow user to set max_tokens and temperature from CLI
    
    # if input contains "unlearn", then delete the last exchange in the prompt file
    if input.__contains__("unlearn"):
        # if input is "unlearn all", then delete all the lines of the prompt file
        if input.__contains__("all"):
            # TODO maybe add a confirmation prompt or temporary file save before deleting file
            with open(PROMPT_CONTEXT, 'w') as f:
                f.write('')
                print("\n#\tContext has been cleared")
            return "unlearned interaction"
        else:
        # otherwise remove the last two lines assuming single line prompt and responses
        # TODO Codex sometimes responds with multiple lines, so some kind of metadata tagging is needed
            with open(PROMPT_CONTEXT, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    lines.pop()
                    lines.pop()
                    with open(PROMPT_CONTEXT, 'w') as f:
                        f.writelines(lines)
                print("\n#\tUnlearned interaction")
        return "unlearned interaction"

    # TODO add an input for how many lines to show after "show context"
    # context commands
    if input.__contains__("context"):
        # show context
        if input.__contains__("show"):
            # print the prompt file to the command line
            print('\n')
            with open(PROMPT_CONTEXT, 'r') as f:
                lines = f.readlines()
                print('\n# '.join(lines))
            return "context shown"
        
        # edit context
        if input.__contains__("edit"):
            # open the prompt file in text editor
            os.system('open {}'.format(PROMPT_CONTEXT))
            return "context shown"

        # TODO accept file name after "save context"
        # currently using computer time to avoid name-conflicts
        # save context
        if input.__contains__("save"):
            # save the current prompt file to a new file
            with open(PROMPT_CONTEXT, 'r') as f:
                lines = f.readlines()
                # create a new file name with the current time in this file's directory
                new_file_name = time.strftime("%Y%m%d-%H%M%S") + '.txt'
                with Path(__file__).with_name(new_file_name).open('w') as f:
                    f.writelines(lines)
            print('\n#\tContext saved to {}'.format(new_file_name))
            return "context saved"
        
        if input.__contains__("clear"):
            # TODO maybe add a confirmation prompt or temporary file save before deleting file
            with open(PROMPT_CONTEXT, 'w') as f:
                f.write('')
                print("\n#\tContext has been cleared")
            return "unlearned interaction"
    
    return ""

def get_prompt():
    """
    uses the stdin to get user input
    input is either treated as a command or as a Codex query

    Returns: command result or context + input from stdin
    """

    # get input from sys.stdin.read()
    input = sys.stdin.read() + '\n'

    # first we check if the input is a command
    command_result = get_command_result(input)

    # if input is not a command, then update the prompt file and get the prompt
    if command_result == "":
        return get_updated_prompt_file(input)
    else:
        return command_result

if __name__ == '__main__':
    initialize_openai_api()

    try:
        prompt = get_prompt()

        # check if the prompt is a command result, otherwise run the query
        if prompt == "unlearned interaction" or prompt == "context shown" or prompt == "context saved":
            sys.exit(0)

        # prime codex for the corresponding shell type
        if BASH_MODE:
            codex_query = '#!/bin/zsh\n\n' + prompt
        else:
            codex_query = '<# powershell #>' + prompt

        # get the response from codex
        # keeping max_tokens at 50 to avoid multi-line responses
        # keeping temperature high
        response = openai.Completion.create(engine='davinci-codex-msft', prompt=codex_query, temperature=0.5, max_tokens=50)

        completion_all = response['choices'][0]['text']
        completion_list = completion_all.split('\n')
        output = ""
        if completion_all[:2] == '\n\n':
            output = completion_all
        elif completion_list[0]:
            output = completion_list[0]
        elif len(completion_list) == 1:
            output = ""
        else:
            output = '\n' + completion_list[1]

        # print output to CLI
        print('\n')
        print(output)

        # append output to prompt context file
        with PROMPT_CONTEXT.open('a') as f:
            f.write(output + '\n')
            f.close()
    except FileNotFoundError:
        print('\n\n# Codex CLI error: Prompt file not found')
