#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openai
import sys
import os
import configparser
import time
import re
import psutil

from pathlib import Path

CONTEXT_MODE = "off"
SHELL = ""

ENGINE = 'davinci-codex-msft'
TEMPERATURE = 0
MAX_TOKENS = 100

DEBUG_MODE = False

# Get config dir from environment or default to ~/.config or ~\.config depending on OS
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser(os.path.join('~','.config')))
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
        print('Please create a file called openaiapirc at {} and add your organization ID and secret key'.format(CONFIG_DIR))
        print('The format is:\n')
        print('[openai]')
        print('organization_id=<your organization ID>')
        print('secret_key=<your secret key>\n')
        print('If you do not yet have an organization ID and secret key, you\n'
        'need to register for OpenAI Codex: \n'
        'https://openai.com/blog/openai-codex/')
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
    
    prompt_config = {}
    
    if has_prompt_headers(PROMPT_CONTEXT) == False:
        prompt_config = {
            'engine': ENGINE,
            'temperature': TEMPERATURE,
            'max_tokens': MAX_TOKENS,
            'shell': SHELL,
            'context': CONTEXT_MODE,
            'token_count': get_token_count(PROMPT_CONTEXT)
        }
        stamp_prompt_headers(PROMPT_CONTEXT, prompt_config)
    else:
        prompt_config = read_prompt_headers(PROMPT_CONTEXT)
    
    return prompt_config

def has_prompt_headers(prompt_file):
    """
    Check if the prompt context file has headers
    """
    if os.path.isfile(prompt_file) == False:
        return False
    
    with prompt_file.open('r') as f:
        lines = f.readlines()
        # this is not a strict check, but it should be enough
        if lines[0].__contains__('## engine:'):
            return True
        else:
            return False

def read_prompt_headers(prompt_file):
    """
    Read the prompt headers and return a dictionary
    """
    if has_prompt_headers(prompt_file) == False:
        return {
            'engine': ENGINE,
            'temperature': TEMPERATURE,
            'max_tokens': MAX_TOKENS,
            'shell': SHELL,
            'context': CONTEXT_MODE,
            'token_count': get_token_count(prompt_file)
        }
    with prompt_file.open('r') as f:
        lines = f.readlines()
        engine = lines[0].split(':')[1].strip()
        temperature = lines[1].split(':')[1].strip()
        max_tokens = lines[2].split(':')[1].strip()
        shell = lines[3].split(':')[1].strip()
        context = lines[4].split(':')[1].strip()
        token_count = lines[5].split(':')[1].strip()
    return {
        'engine': engine,
        'temperature': float(temperature),
        'max_tokens': int(max_tokens),
        'shell': shell,
        'context': context,
        'token_count': int(token_count)
    }

def stamp_prompt_headers(prompt_file, config):
    """
    Stamp the prompt headers with the config
    """
    lines = []
    if os.path.isfile(PROMPT_CONTEXT):
        lines = prompt_file.open('r').readlines() # read old content
    
    newf = open('temp.txt','w')
    # add headers at the beginning
    newf.write('## engine: {}\n'.format(config['engine']))
    newf.write('## temperature: {}\n'.format(config['temperature']))
    newf.write('## max_tokens: {}\n'.format(config['max_tokens']))
    newf.write('## shell: {}\n'.format(config['shell']))
    newf.write('## context_mode: {}\n'.format(config['context']))
    newf.write('## token_count: {}\n'.format(config['token_count']))

    if has_prompt_headers(prompt_file):
        lines = lines[6:] # drop old headers
    
    for line in lines: # write old content after new
        newf.write(line)
    
    newf.close()
    newf = open('temp.txt','r')
    with prompt_file.open('w') as f:
        # write everything from newf to f
        f.write(newf.read())
    newf.close()
    os.remove('temp.txt')

def get_token_count(prompt_file):
    """
    Get the token count from the prompt context file
    """
    token_count = 0
    if os.path.isfile(prompt_file):
        with prompt_file.open('r') as f:
            lines = f.readlines()
        # count number of tokens
        token_count = 0
        if has_prompt_headers(prompt_file):
            lines = lines[6:] # drop headers
        for line in lines:
            token_count += len(line.split())
    return token_count

def get_updated_prompt_file(input, config):
    """
    Get the updated prompt file
    Checks for token overflow and appends the current input

    Returns: the prompt file after appending the input
    """

    input_tokens_count = len(input.split())
    need_to_refresh = (config['token_count'] + input_tokens_count > 2048)

    if need_to_refresh:
        # TODO use multi-line metadata and dependency metadata to track this
        # delete first 2 lines of prompt context file
        with PROMPT_CONTEXT.open('r') as f:
            lines = f.readlines()
            headers = lines[:6]
            prompt = lines[8:] # drop first 2 lines of prompt
        with PROMPT_CONTEXT.open('w') as f:
            f.writelines(headers)
            f.writelines(prompt)

    # append input to prompt context file
    if config['context'] == 'on':
        with PROMPT_CONTEXT.open('a') as f:
            f.write(input)
            f.close()

    prompt = ""
    # get input from prompt file
    # skip the header lines
    with PROMPT_CONTEXT.open('r') as f:
        lines = f.readlines()
        lines = lines[6:] # skip headers
        prompt = ''.join(lines)

    return prompt + input, config

def get_command_result(input, config):
    """
    Checks if the input is a command and if so, executes it
    Currently supported commands:
    - unlearn
    - unlearn all
    - show context <n>
    - edit context
    - save context
    - clear context
    - load context <filename>
    - set engine <engine>
    - set temperature <temperature>
    - set max_tokens <max_tokens>
    - set shell <shell>

    Returns: command result or "" if no command matched
    """

    # configuration setting commands
    if input.__contains__("set"):
        # set temperature <temperature>
        if input.__contains__("temperature"):
            input = input.split()
            if len(input) == 3:
                config['temperature'] = float(input[2])
                return "config set", config
            else:
                return "", config
        # set max_tokens <max_tokens>
        elif input.__contains__("max_tokens"):
            input = input.split()
            if len(input) == 3:
                config['max_tokens'] = int(input[2])
                return "config set", config
            else:
                return "", config
        elif input.__contains__("shell"):
            input = input.split()
            if len(input) == 3:
                config['shell'] = input[2]
                return "config set", config
            else:
                return "", config
        elif input.__contains__("engine"):
            input = input.split()
            if len(input) == 3:
                config['engine'] = input[2]
                return "config set", config
            else:
                return "", config

    if input.__contains__("show config"):
        print('\n')
        with open(PROMPT_CONTEXT, 'r') as f:
            lines = f.readlines()
            lines = lines[:6] # keep headers
        # the input looks like "show context <number of lines>"
        print('\n# '.join(lines))
        return "config shown", config

    # interaction deletion commands
    if input.__contains__("unlearn"):
        # if input is "unlearn all", then delete all the lines of the prompt file
        if input.__contains__("all"):
            # TODO maybe add a confirmation prompt or temporary file save before deleting file
            with open(PROMPT_CONTEXT, 'w') as f:
                f.write('')
                print("\n#\tContext has been cleared")
            return "unlearned interaction", config
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
                print("\n#   Unlearned interaction")
        return "unlearned interaction", config

    # context commands
    if input.__contains__("context"):
        # show context <n>
        if input.__contains__("show"):
            # print the prompt file to the command line
            print('\n')
            with open(PROMPT_CONTEXT, 'r') as f:
                lines = f.readlines()
                lines = lines[6:] # skip headers
            # the input looks like "show context <number of lines>"
            line_numbers = 0
            if len(input.split()) > 3:
                line_numbers = int(input.split()[3])
            # print the last line_numbers lines
            if line_numbers != 0:
                for line in lines[-line_numbers:]:
                    print('\n# '+line, end='')
            else:
                print('\n# '.join(lines))
            return "context shown", config
        
        # edit context
        if input.__contains__("edit"):
            # open the prompt file in text editor
            if config['shell'] != 'powershell':
                os.system('open {}'.format(PROMPT_CONTEXT))
            else:
                os.system('start {}'.format(PROMPT_CONTEXT))
            return "context shown", config

        # save context <filename>
        if input.__contains__("save"):
            # save the current prompt file to a new file
            # if filename not specified use the current time (to avoid name conflicts)

            filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
            if len(input.split()) == 4:
                filename = input.split()[3]
            
            with open(PROMPT_CONTEXT, 'r') as f:
                lines = f.readlines()
                if not filename.endswith('.txt'):
                    filename = filename + '.txt'
                filename = os.path.join(os.path.dirname(PROMPT_CONTEXT), "saved", filename)
                with Path(filename).open('w') as f:
                    f.writelines(lines)
            
            print('\n#\tContext saved to {}'.format(filename))
            return "context saved", config
        
        # clear context
        if input.__contains__("clear"):
            # temporary saving deleted prompt file
            filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
            with open(PROMPT_CONTEXT, 'r') as f:
                lines = f.readlines()
                filename = os.path.join(os.path.dirname(PROMPT_CONTEXT), "deleted", filename)
                with Path(filename).open('w') as f:
                    f.writelines(lines)
            
            # delete the prompt file
            with open(PROMPT_CONTEXT, 'w') as f:
                f.write('')
                print("\n#\tContext has been cleared, temporarily saved to {}".format(filename))
            return "unlearned interaction", config
        
        # load context <filename>
        if input.__contains__("load"):
            # the input looks like # load context <filename>
            # write everything from the file to the prompt file
            if len(input.split()) == 4:
                filename = input.split()[3]

                # read from saved directory
                if not filename.endswith('.txt'):
                    filename = filename + '.txt'
                filename = os.path.join(os.path.dirname(PROMPT_CONTEXT), "saved", filename)

                # check if the file exists
                if os.path.isfile(filename):
                    with Path(filename).open('r') as f:
                        lines = f.readlines()
                else:
                    print("\n#\tFile not found")
                    return "context loaded", config
                
                # write to the current prompt file
                with open(PROMPT_CONTEXT, 'w') as f:
                    f.writelines(lines)
                
                print('\n#\tContext loaded from {}'.format(filename))
                return "context loaded", config
            print('\n#\tInvalid command format, did you specify which file to load?')
            return "context loaded", config
    
    return "", config

def get_prompt(config):
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
    command_result, config = get_command_result(entry, config)

    # if input is not a command, then update the prompt file and get the prompt
    if command_result == "":
        return get_updated_prompt_file(entry, config)
    elif command_result == "config set":
        # successful command no codex query needed
        stamp_prompt_headers(PROMPT_CONTEXT, config)
        sys.exit(0)
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

    # set the prompt context file to contexts/powershell_context.txt
    if SHELL == "powershell":
        PROMPT_CONTEXT = Path(os.path.join(os.path.dirname(__file__), "contexts", "powershell_context.txt"))

if __name__ == '__main__':
    detect_shell()
    config = initialize()
    try:
        prompt, config = get_prompt(config)

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

        codex_query = prefix + prompt

        # write codex_query to a temporary file
        with open("codex_query.txt", 'w') as f:
            f.write(codex_query)

        # get the response from codex
        response = openai.Completion.create(engine=config['engine'], prompt=codex_query, temperature=config['temperature'], max_tokens=config['max_tokens'], stop="#")

        completion_all = response['choices'][0]['text']

        print('\n')
        print(completion_all)

        # append output to prompt context file
        if config['context'] == "on":
            with PROMPT_CONTEXT.open('a') as f:
                f.write(completion_all)
                f.close()
            
            config['token_count'] = get_token_count(PROMPT_CONTEXT)
            stamp_prompt_headers(PROMPT_CONTEXT, config)
    except FileNotFoundError:
        print('\n\n# Codex CLI error: Prompt file not found')
    except openai.error.RateLimitError:
        print('\n\n# Codex CLI error: Rate limit exceeded')
    except openai.error.APIConnectionError:
        print('\n\n# Codex CLI error: API connection error, are you connected to the internet?')
