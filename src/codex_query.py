#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openai
import sys
import os
import configparser
import re
import psutil

from pathlib import Path
from prompt_file import ModelConfig, Prompt
from commands import get_command_result

MULTI_TURN = "off"
SHELL = ""

ENGINE = ''
TEMPERATURE = 0
MAX_TOKENS = 300

DEBUG_MODE = False

# api keys located in the same directory as this file
API_KEYS_LOCATION = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'openaiapirc')

# Read the secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization=<organization-id>
# secret_key=<your secret key>
# engine=<engine-name>
def create_template_ini_file():
    """
    If the ini file does not exist create it and add secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        print('# Please create a file at {} and add your secret key'.format(API_KEYS_LOCATION))
        print('# The format is:\n')
        print('# [openai]')
        print('# organization_id=<organization-id>')
        print('# secret_key=<your secret key>\n')
        print('# engine=<engine-id>')
        sys.exit(1)

def initialize(shell: str):
    """
    Initialize openAI and shell mode
    """

    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")
    openai.organization = config['openai']['organization_id'].strip('"').strip("'")
    engine = config['openai']['engine'].strip('"').strip("'")
    
    return Prompt(shell, engine)

def is_sensitive_content(content):
    """
    Check if the content contains sensitive content
    Refer to https://beta.openai.com/docs/engines/content-filter for explanation
    """

    if len(content) == 0:
        return False
    
    response = openai.Completion.create(
        engine="content-filter-alpha",
        prompt = "<|endoftext|>"+content+"\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=0,
        logprobs=10
        )
    
    output_label = response["choices"][0]["text"]

    # This is the probability at which we evaluate that a "2" is likely real
    # vs. should be discarded as a false positive
    toxic_threshold = -0.355

    if output_label == "2":
        # If the model returns "2", return its confidence in 2 or other output-labels
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        # If the model is not sufficiently confident in "2",
        # choose the most probable of "0" or "1"
        # Guaranteed to have a confidence for 2 since this was the selected token.
        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            # If both "0" and "1" have probabilities, set the output label
            # to whichever is most probable
            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            # If only one of them is found, set output label to that one
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

            # If neither "0" or "1" are available, stick with "2"
            # by leaving output_label unchanged.

        # if the most probable token is none of "0", "1", or "2"
        # this should be set as unsafe
        if output_label not in ["0", "1", "2"]:
            output_label = "2"

    return (output_label != "0")

def get_query(prompt_generator):
    """
    uses the stdin to get user input
    input is either treated as a command or as a Codex query

    Returns: command result or context + input from stdin
    """

    # get input from terminal or stdin
    if DEBUG_MODE:
        entry = input("prompt: ")
    else:
        # Remove extreaneous newlines and hashtag from the input string
        entry = sys.stdin.read().strip("\n").strip("#").strip(" ") 
    # first we check if the input is a command
    try:
        command_result, prompt_generator = get_command_result(entry, prompt_generator)
    except Exception as e:
        print (str(e))

    # if input is not a command, then query Codex, otherwise exit command has been run successfully
    if command_result == "":
        return entry, prompt_generator
    else:
        sys.exit(0)


def get_shell_prefix(shell: str):
    # prime codex for the corresponding shell type
    if shell == "zsh":
        return '#!/bin/zsh\n\n'
    elif shell == "bash":
        return '#!/bin/bash\n\n'
    elif shell == "powershell":
        return '<# powershell #>\n\n'
    elif shell == "unknown":
        print("\n#\tUnsupported shell type, please use # set shell <shell>")
        return ""
    else:
        return '#' + shell + '\n\n'

def detect_shell():
    parent_process_name = psutil.Process(os.getppid()).name()
    POWERSHELL_MODE = bool(re.fullmatch('pwsh|pwsh.exe|powershell.exe', parent_process_name))
    BASH_MODE = bool(re.fullmatch('bash|bash.exe', parent_process_name))
    ZSH_MODE = bool(re.fullmatch('zsh|zsh.exe', parent_process_name))

    shell = "powershell" if POWERSHELL_MODE else "bash" if BASH_MODE else "zsh" if ZSH_MODE else "unknown"

    prefix = get_shell_prefix(shell)

    return shell, prefix

if __name__ == '__main__':
    shell, prefix = detect_shell()
    prompt_generator: Prompt = initialize(shell)

    try:
        user_query, prompt_generator = get_query(prompt_generator)
        codex_query = prefix + prompt_generator.prompt_engine.build_prompt(user_query, prompt_generator.prompt_engine.config.model_config.multi_turn)
        # get the response from codex
        response = openai.Completion.create(engine=prompt_generator.prompt_engine.config.model_config.engine, 
                                            prompt=codex_query, 
                                            temperature=prompt_generator.prompt_engine.config.model_config.temperature, 
                                            max_tokens=prompt_generator.prompt_engine.config.model_config.max_tokens, 
                                            stop=prompt_generator.prompt_engine.config.input_prefix)

        completion_all = response['choices'][0]['text']

        if is_sensitive_content(user_query + '\n' + completion_all):
            print("\n#   Sensitive content detected, response has been redacted")
        else:
            print(completion_all)

            # append output to prompt context file
            if prompt_generator.prompt_engine.config.model_config.multi_turn == "on":
                if completion_all != "" or len(completion_all) > 0:
                    prompt_generator.prompt_engine.add_interaction(user_query, completion_all)
                    prompt_generator.save_prompt_engine()
        
    except FileNotFoundError:
        print('\n\n# Codex CLI error: Prompt file not found, try again')
    except openai.error.RateLimitError:
        print('\n\n# Codex CLI error: Rate limit exceeded, try later')
    except openai.error.APIConnectionError:
        print('\n\n# Codex CLI error: API connection error, are you connected to the internet?')
    except openai.error.InvalidRequestError as e:
        print('\n\n# Codex CLI error: Invalid request - ' + str(e))
    except Exception as e:
        print('\n\n# Codex CLI error: Unexpected exception - ' + str(e))
