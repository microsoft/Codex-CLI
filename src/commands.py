import os
import time

from pathlib import Path
from prompt_file import *

import re

param_type_mapping = {
    'engine': str,
    'temperature': float,
    'max_tokens': int,
    'shell': str,
}


def get_command_result(input, prompt_generator):
    """
    Checks if the input is a command and if so, executes it
    Currently supported commands:
    - start multi-turn
    - stop multi-turn
    - default context
    - show context <n>
    - view context
    - save context
    - clear context
    - load context <filename>
    - set engine <engine>
    - set temperature <temperature>
    - set max_tokens <max_tokens>
    - set shell <shell>

    Returns: command result or "" if no command matched
    """
    
    config = prompt_generator.prompt_engine.config.model_config
    # configuration setting commands
    if input.__contains__("set"):
        # match the command using regex to one of the 4 above set commands
        match = re.match(r"set (engine|temperature|max_tokens|shell) (.*)", input)
        if match:
            # get the command and the value
            command = match.group(1)
            value = match.group(2)
            # check if the value is of the correct type
            if param_type_mapping[command] == float:
                value = float(value)
            elif param_type_mapping[command] == int:
                value = int(value)
            elif param_type_mapping[command] == str:
                value = str(value)
            # set the value
            setattr(config, command, value)
            print (f"\n#   {command} set to {value}")
            return "Configuration setting updated", prompt_generator

    elif input.__contains__("show config"):
        prompt_generator.show_config()
        return "config shown", prompt_generator

    # multi turn/single turn commands
    elif input.__contains__("multi-turn"):
        # start context
        if input.__contains__("start"):
            if getattr(config, 'multi_turn') == 'off':
                prompt_generator.start_multi_turn()
                print ("\n#   Multi-turn mode started")
                return "multi turn mode on", prompt_generator
            else:
                print ("\n#   Multi-turn mode already started")
                return "multi turn mode already on", prompt_generator
                    
        # stop context
        elif input.__contains__("stop"):
            if getattr(config, 'multi_turn') == 'on':
                prompt_generator.stop_multi_turn()
                print ("\n#   Multi-turn mode stopped")
                return "multi turn mode off", prompt_generator
            else:
                print ("\n#   Multi-turn mode already stopped")
                return "multi turn mode already off", prompt_generator
    
    # context file commands
    elif input.__contains__("context"):
        if input.__contains__("default"):
            prompt_generator.default_context()
            print ("\n#   Default context loaded")
            return "stopped context", prompt_generator
        
        # show context <n>
        if input.__contains__("show"):
            print('\n')
            print ("\n#   ".join(prompt_generator.prompt_engine.build_context().split("\n")))
            return "context shown", prompt_generator
        
        # edit context
        if input.__contains__("view"):
            # open the prompt file in text editor
            prompt_generator.save_to("current-context.yaml")
            if getattr(config, 'shell') != 'powershell':
                os.system('open {}'.format(Path(os.path.join(os.path.dirname(__file__), "..", "contexts", f"current-context.yaml"))))
            else:
                os.system('start {}'.format(Path(os.path.join(os.path.dirname(__file__), "..", "contexts", f"current-context.yaml"))))
            print ("\n#   Context file opened in text editor")
            return "context shown", prompt_generator

        # save context <filename>
        if input.__contains__("save"):
            # save the current prompt file to a new file
            # if filename not specified use the current time (to avoid name conflicts)

            # regex to get the filename
            match = re.match(r"save context (.*)", input)
            if match:
                filename = match.group(1)
            else:
                filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".yaml"
            
            prompt_generator.save_to(filename)
            print(f'\n#   Saved to {filename}')

            return "context saved", prompt_generator
        
        # clear context
        if input.__contains__("clear"):
            # temporary saving deleted prompt file
            prompt_generator.clear_context()
            print ("\n#   Context cleared")
            return "unlearned interaction", prompt_generator
        
        # load context <filename>
        if input.__contains__("load"):

            # regex to get the filename
            match = re.match(r"load context (.*)", input)
            if match:
                filename = match.group(1)
                success = prompt_generator.load_context(filename)
                if success:
                    print (f'\n#   Loaded {filename}')
                else:
                    print (f'\n#   Failed to load {filename}, please check the file')
                return "context loaded", prompt_generator
            print('\n#\tInvalid command format, did you specify which file to load?')
            return "context loaded", prompt_generator
    
    return "", prompt_generator
