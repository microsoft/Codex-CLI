#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import re
import sys
from pathlib import Path

import openai
import psutil

from api_config import get_default_max_tokens, get_model, get_setting
from prompt_file import PromptFile
from commands import get_command_result

MULTI_TURN = "off"
SHELL = ""

MODEL = ''
CLIENT = None
TEMPERATURE = 0
MAX_TOKENS = 300

DEBUG_MODE = False

# api keys located in the same directory as this file
API_KEYS_LOCATION = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'openaiapirc')

PROMPT_CONTEXT = Path(__file__).with_name('current_context.txt')


# Read the secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization_id=<optional-organization-id>
# secret_key=<your secret key>
# base_url=<api-base-url>
# model=<model-id>
def create_template_ini_file():
    """
    If the ini file does not exist create it and add secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        print('# Please create a file at {} and add your secret key'.format(API_KEYS_LOCATION))
        print('# The format is:\n')
        print('# [openai]')
        print('# organization_id=<optional-organization-id>')
        print('# secret_key=<your secret key>\n')
        print('# base_url=<api-base-url>')
        print('# model=<model-id>')
        sys.exit(1)


def initialize():
    """
    Initialize openAI and shell mode
    """
    global CLIENT
    global MODEL

    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    settings = config['openai']
    api_key = get_setting(settings, 'secret_key')
    base_url = get_setting(settings, 'base_url')
    organization_id = get_setting(settings, 'organization_id')
    MODEL = get_model(settings)

    if not api_key or not MODEL:
        raise ValueError('secret_key and model are required in openaiapirc')

    client_options = {'api_key': api_key}
    if base_url:
        client_options['base_url'] = base_url.rstrip('/')
    if organization_id:
        client_options['organization'] = organization_id
    CLIENT = openai.OpenAI(**client_options)

    prompt_config = {
        'model': MODEL,
        'temperature': TEMPERATURE,
        'max_tokens': get_default_max_tokens(settings, MAX_TOKENS),
        'shell': SHELL,
        'multi_turn': MULTI_TURN,
        'token_count': 0
    }
    
    return PromptFile(PROMPT_CONTEXT.name, prompt_config)


def create_chat_completion(client, config, prompt):
    response = client.chat.completions.create(
        model=config['model'],
        messages=[
            {
                'role': 'system',
                'content': (
                    "Return a valid {} command for the user's request. "
                    "Prefix any textual explanation with the shell's comment syntax."
                ).format(config['shell'])
            },
            {'role': 'user', 'content': prompt}
        ],
        temperature=config['temperature'],
        max_tokens=config['max_tokens']
    )
    return response.choices[0].message.content or ''


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

    shell_prompt_file = Path(os.path.join(os.path.dirname(__file__), "..", "contexts", "{}-context.txt".format(SHELL)))

    if shell_prompt_file.is_file():
        PROMPT_CONTEXT = shell_prompt_file


if __name__ == '__main__':
    detect_shell()
    prompt_file = initialize()

    try:
        user_query, prompt_file = get_query(prompt_file)
        
        config = prompt_file.config if prompt_file else {
            'model': MODEL,
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

        completion_all = create_chat_completion(CLIENT, config, codex_query)
        print(completion_all)

        # append output to prompt context file
        if config['multi_turn'] == "on":
            if completion_all != "" or len(completion_all) > 0:
                prompt_file.add_input_output_pair(user_query, completion_all)
        
    except FileNotFoundError:
        print('\n\n# Codex CLI error: Prompt file not found, try again')
    except openai.RateLimitError:
        print('\n\n# Codex CLI error: Rate limit exceeded, try later')
    except openai.APIConnectionError:
        print('\n\n# Codex CLI error: API connection error, are you connected to the internet?')
    except openai.BadRequestError as e:
        print('\n\n# Codex CLI error: Invalid request - ' + str(e))
    except Exception as e:
        print('\n\n# Codex CLI error: Unexpected exception - ' + str(e))
