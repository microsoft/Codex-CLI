#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmd import PROMPT
import openai
import sys
import os
import configparser
import time
import re
import psutil

from pathlib import Path
from prompt_file import PromptFile
from commands import get_command_result

MULTI_TURN = "off"
SHELL = ""

ENGINE = 'cushman-codex-msft'
TEMPERATURE = 0
MAX_TOKENS = 300

DEBUG_MODE = False

# Get config dir from environment or default to ~/.config or ~\.config depending on OS
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser(os.path.join('~','.config')))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')

PROMPT_CONTEXT = Path(__file__).with_name('openai_completion_input.txt')


# Read the secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization=<organization-id>
# secret_key=<your secret key>
def create_template_ini_file():
    """
    If the ini file does not exist create it and add secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        print('Please create a file called openaiapirc at {} and add your secret key'.format(CONFIG_DIR))
        print('The format is:\n')
        print('[openai]')
        print('organization_id=<organization-id>')
        print('secret_key=<your secret key>\n')
        sys.exit(1)

def initialize():
    """
    Initialize openAI and shell mode
    """

    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")
    openai.organization = config['openai']['organization_id'].strip('"').strip("'")

    prompt_config = {
        'engine': ENGINE,
        'temperature': TEMPERATURE,
        'max_tokens': MAX_TOKENS,
        'shell': SHELL,
        'multi_turn': MULTI_TURN,
        'token_count': 0
    }
    
    return PromptFile(PROMPT_CONTEXT.name, prompt_config)

def get_query(prompt_file):
    """
    uses the stdin to get user input
    input is either treated as a command or as a Codex query

    Returns: command result or context + input from stdin
    """

    # get input from terminal or stdin
    if DEBUG_MODE:
        entry = input("prompt: ") + '\n'
    else:
        entry = sys.stdin.read()
    # first we check if the input is a command
    command_result, prompt_file = get_command_result(entry, prompt_file)

    # if input is not a command, then query Codex, otherwise exit command has been run successfully
    if command_result == "":
        return entry, prompt_file
    else:
        sys.exit(0)

def detect_shell():
    global SHELL
    global PROMPT_CONTEXT

    parent_process_name = psutil.Process(os.getppid()).name()
    POWERSHELL_MODE = bool(re.fullmatch('pwsh|pwsh.exe|powershell.exe', parent_process_name))
    BASH_MODE = bool(re.fullmatch('bash|bash.exe', parent_process_name))
    ZSH_MODE = bool(re.fullmatch('zsh|zsh.exe', parent_process_name))

    SHELL = "powershell" if POWERSHELL_MODE else "bash" if BASH_MODE else "zsh" if ZSH_MODE else "unknown"

    shell_prompt_file = Path(os.path.join(os.path.dirname(__file__), "contexts", "{}_context.txt".format(SHELL)))

    if shell_prompt_file.is_file():
        PROMPT_CONTEXT = shell_prompt_file

if __name__ == '__main__':
    detect_shell()
    prompt_file = initialize()

    try:
        user_query, prompt_file = get_query(prompt_file)
        
        config = prompt_file.config if prompt_file else {
            'engine': ENGINE,
            'temperature': TEMPERATURE,
            'max_tokens': MAX_TOKENS,
            'shell': SHELL,
            'multi_turn': MULTI_TURN,
            'token_count': 0
        }

        # use query prefix to prime Codex for correct scripting language
        prefix = ""
        # prime codex for the corresponding shell type
        if config['shell'] == "zsh":
            prefix = '#!/bin/zsh\n\n'
        elif config['shell'] == "bash":
            prefix = '#!/bin/bash\n\n'
        elif config['shell'] == "powershell":
            prefix = '<# powershell #>\n\n'
        elif config['shell'] == "unknown":
            print("\n#\tUnsupported shell type, please use # set shell <shell>")
        else:
            prefix = '#' + config['shell'] + '\n\n'

        codex_query = prefix + prompt_file.read_prompt_file(user_query) + user_query

        # get the response from codex
        response = openai.Completion.create(engine=config['engine'], prompt=codex_query, temperature=config['temperature'], max_tokens=config['max_tokens'], stop="#")

        completion_all = response['choices'][0]['text']

        print(completion_all)

        # append output to prompt context file
        if config['multi_turn'] == "on":
            if completion_all != "" or len(completion_all) > 0:
                prompt_file.add_input_output_pair(user_query, completion_all)
    except FileNotFoundError:
        print('\n\n# Codex CLI error: Prompt file not found, try again')
    except openai.error.RateLimitError:
        print('\n\n# Codex CLI error: Rate limit exceeded, try later')
    except openai.error.APIConnectionError:
        print('\n\n# Codex CLI error: API connection error, are you connected to the internet?')
