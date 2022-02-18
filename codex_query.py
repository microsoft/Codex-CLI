#!/usr/bin/env python3

import openai
import sys
import os
import configparser
import time
import re
import psutil

from pathlib import Path

SHELL = ""

ENGINE = 'davinci-codex-msft'
TEMPERATURE = 0.5
MAX_TOKENS = 50

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

    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")

    if os.path.isfile(PROMPT_CONTEXT) == False:
        with PROMPT_CONTEXT.open('w') as f:
            f.write('## engine: {}\n'.format(ENGINE))
            f.write('## temperature: {}\n'.format(TEMPERATURE))
            f.write('## max_tokens: {}\n'.format(MAX_TOKENS))
            f.write('## shell: {}\n'.format(SHELL))
            f.write('## token_count: {}\n'.format(0))
            f.write('\n')
    elif has_prompt_headers(PROMPT_CONTEXT) == False:
        with PROMPT_CONTEXT.open('r') as f:
            lines = f.readlines()
        # count number of tokens
        token_count = 0
        for line in lines:
            token_count += len(line.split())
        newf = open('temp.txt','w')
        lines = PROMPT_CONTEXT.open('r').readlines() # read old content
        # add headers at the beginning
        newf.write('## engine: {}\n'.format(ENGINE))
        newf.write('## temperature: {}\n'.format(TEMPERATURE))
        newf.write('## max_tokens: {}\n'.format(MAX_TOKENS))
        newf.write('## shell: {}\n'.format(SHELL))
        newf.write('## token_count: {}\n'.format(token_count))
        newf.write('\n')
        for line in lines: # write old content after new
            newf.write(line)
        newf.close()
        newf = open('temp.txt','r')
        with PROMPT_CONTEXT.open('w') as f:
            # write everything from newf to f
            f.write(newf.read())
    
    return read_prompt_headers(PROMPT_CONTEXT)

def has_prompt_headers(prompt_file):
    """
    Check if the prompt context file has headers
    """
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
            'token_count': 0
        }
    with prompt_file.open('r') as f:
        lines = f.readlines()
        engine = lines[0].split(':')[1].strip()
        temperature = lines[1].split(':')[1].strip()
        max_tokens = lines[2].split(':')[1].strip()
        shell = lines[3].split(':')[1].strip()
        token_count = lines[4].split(':')[1].strip()
    return {
        'engine': engine,
        'temperature': float(temperature),
        'max_tokens': int(max_tokens),
        'shell': shell,
        'token_count': int(token_count)
    }

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
            headers = lines[:5]
            prompt = lines[7:] # drop first 2 lines of prompt
        with PROMPT_CONTEXT.open('w') as f:
            f.writelines(headers)
            f.writelines(prompt)

    # append input to prompt context file
    with PROMPT_CONTEXT.open('a') as f:
        f.write(input)
        f.close()

    prompt = ""
    # get input from prompt file
    # skip the header lines
    with PROMPT_CONTEXT.open('r') as f:
        lines = f.readlines()
        lines = lines[5:] # skip headers
        prompt = ''.join(lines)

    return prompt, config

def get_command_result(input, config):
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

    if input.__contains__("set"):
        # if the input is "set temperature 0.5", update TEMPERATURE
        # and return the prompt
        if input.__contains__("temperature"):
            input = input.split()
            if len(input) == 3:
                config['temperature'] = float(input[2])
                return "temperature set", config
            else:
                return "", config
        # if the input is "set max_tokens 50", update MAX_TOKENS
        # and return the
        elif input.__contains__("max_tokens"):
            input = input.split()
            if len(input) == 3:
                config['max_tokens'] = int(input[2])
                return "max_tokens set", config
            else:
                return "", config

    # if input contains "unlearn", then delete the last exchange in the prompt file
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
                print("\n#\tUnlearned interaction")
        return "unlearned interaction", config

    # TODO add an input for how many lines to show after "show context"
    # context commands
    if input.__contains__("context"):
        # show context
        if input.__contains__("show"):
            # print the prompt file to the command line
            print('\n')
            with open(PROMPT_CONTEXT, 'r') as f:
                lines = f.readlines()
                lines = lines[5:] # skip headers
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
            os.system('open {}'.format(PROMPT_CONTEXT))
            return "context shown", config

        # save context <filename>
        if input.__contains__("save"):
            # save the current prompt file to a new file
            # the input looks like "save context <filename>"
            # save the prompt file to the filename
            # set filename to current time and date
            filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
            if len(input.split()) == 3:
                filename = input.split()[3]
            with open(PROMPT_CONTEXT, 'r') as f:
                lines = f.readlines()
                # create a new file name with the current time in this file's directory
                if not filename.endswith('.txt'):
                    filename = filename + '.txt'
                if config['shell'] == "powershell":
                    filename = "saved\\" + filename
                else:
                    filename = "saved/" + filename
                with Path(__file__).with_name(filename).open('w') as f:
                    f.writelines(lines)
            print('\n#\tContext saved to {}'.format(filename))
            return "context saved", config
        
        if input.__contains__("clear"):
            # TODO maybe add a confirmation prompt or temporary file save before deleting file
            with open(PROMPT_CONTEXT, 'w') as f:
                f.write('')
                print("\n#\tContext has been cleared")
            return "unlearned interaction", config
    
    return "", config

def get_prompt(config):
    """
    uses the stdin to get user input
    input is either treated as a command or as a Codex query

    Returns: command result or context + input from stdin
    """

    # get input from terminal
    #sys.stdin.read() + '\n'
    entry = input("prompt: ") + '\n'
    # first we check if the input is a command
    command_result, config = get_command_result(entry, config)

    # if input is not a command, then update the prompt file and get the prompt
    if command_result == "":
        return get_updated_prompt_file(entry, config)
    else:
        return command_result, config

def detect_shell():
    global SHELL

    parent_process_name = psutil.Process(os.getppid()).name()
    POWERSHELL_MODE = bool(re.fullmatch('pwsh|pwsh.exe|powershell.exe', parent_process_name))
    BASH_MODE = bool(re.fullmatch('bash|bash.exe', parent_process_name))
    ZSH_MODE = bool(re.fullmatch('zsh|zsh.exe', parent_process_name))

    SHELL = "powershell" if POWERSHELL_MODE else "bash" if BASH_MODE else "zsh" if ZSH_MODE else "unknown"

    print(SHELL)

if __name__ == '__main__':
    detect_shell()
    config = initialize()

    try:
        prompt, config = get_prompt(config)

        # check if the prompt is a command result, otherwise run the query
        if prompt == "unlearned interaction" or prompt == "context shown" or prompt == "context saved":
            sys.exit(0)

        prefix = ""
        # prime codex for the corresponding shell type
        if config['shell'] == "zsh":
            prefix = '#!/bin/zsh\n\n'
        elif config['shell'] == "bash":
            prefix = '#!/bin/bash\n\n'
        elif config['shell'] == "powershell":
            prefix = '<# powershell #>'
        else:
            prefix = '#' + config['shell'] + '\n\n'
            print("\n#\tUnsupported shell type, please use # set shell <shell type>")

        codex_query = prefix + prompt

        # get the response from codex
        # keeping max_tokens at 50 to avoid multi-line responses
        # keeping temperature high
        response = openai.Completion.create(engine=config['engine'], prompt=codex_query, temperature=config['temperature'], max_tokens=config['max_tokens'])

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
