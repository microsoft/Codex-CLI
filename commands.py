import os
import time

from pathlib import Path
from prompt_file import *

def get_command_result(input, prompt_file):
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
    if prompt_file == None:
        return "", None
    
    config = prompt_file.config
    # configuration setting commands
    if input.__contains__("set"):
        # set temperature <temperature>
        if input.__contains__("temperature"):
            input = input.split()
            if len(input) == 3:
                config['temperature'] = float(input[2])
                prompt_file.set_headers(config)
                return "config set", prompt_file
            else:
                return "", prompt_file
        # set max_tokens <max_tokens>
        elif input.__contains__("max_tokens"):
            input = input.split()
            if len(input) == 3:
                config['max_tokens'] = int(input[2])
                prompt_file.set_headers(config)
                return "config set", prompt_file
            else:
                return "", prompt_file
        elif input.__contains__("shell"):
            input = input.split()
            if len(input) == 3:
                config['shell'] = input[2]
                prompt_file.set_headers(config)
                return "config set", prompt_file
            else:
                return "", prompt_file
        elif input.__contains__("engine"):
            input = input.split()
            if len(input) == 3:
                config['engine'] = input[2]
                prompt_file.set_headers(config)
                return "config set", prompt_file
            else:
                return "", prompt_file

    if input.__contains__("show config"):
        print('\n')
        config = prompt_file.read_headers()
        # read the dictionary into a list of # lines
        lines = []
        for key, value in config.items():
            lines.append('\n# {}: {}'.format(key, value))
        print(''.join(lines))
        return "config shown", prompt_file

    # interaction deletion commands
    if input.__contains__("unlearn"):
        # if input is "unlearn all", then delete all the lines of the prompt file
        if input.__contains__("all"):
            # TODO maybe add a confirmation prompt or temporary file save before deleting file
            prompt_file.clear()
            return "unlearned interaction", prompt_file
        else:
        # otherwise remove the last two lines assuming single line prompt and responses
        # TODO Codex sometimes responds with multiple lines, so some kind of metadata tagging is needed
            prompt_file.clear_last_interaction()
        return "unlearned interaction", prompt_file

    # context commands
    if input.__contains__("context"):
        # show context <n>
        if input.__contains__("show"):
            # print the prompt file to the command line
            print('\n')
            with open(prompt_file.file_name, 'r') as f:
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
            return "context shown", prompt_file
        
        # edit context
        if input.__contains__("edit"):
            # open the prompt file in text editor
            if config['shell'] != 'powershell':
                os.system('open {}'.format(prompt_file.file_name))
            else:
                os.system('start {}'.format(prompt_file.file_name))
            return "context shown", prompt_file

        # save context <filename>
        if input.__contains__("save"):
            # save the current prompt file to a new file
            # if filename not specified use the current time (to avoid name conflicts)

            filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
            if len(input.split()) == 4:
                filename = input.split()[3]
            
            prompt_file.save_to(filename)
            
            print('\n#\tContext saved to {}'.format(filename))
            return "context saved", prompt_file
        
        # clear context
        if input.__contains__("clear"):
            # temporary saving deleted prompt file
            prompt_file.clear()
            return "unlearned interaction", prompt_file
        
        # load context <filename>
        if input.__contains__("load"):
            # the input looks like # load context <filename>
            # write everything from the file to the prompt file
            if len(input.split()) == 4:
                filename = input.split()[3]

                # read from saved directory
                if not filename.endswith('.txt'):
                    filename = filename + '.txt'
                filename = os.path.join(os.path.dirname(prompt_file.file_name), "saved", filename)

                # check if the file exists
                if os.path.isfile(filename):
                    with Path(filename).open('r') as f:
                        lines = f.readlines()
                else:
                    print("\n#\tFile not found")
                    return "context loaded", prompt_file
                
                # write to the current prompt file
                with open(prompt_file.file_name, 'w') as f:
                    f.writelines(lines)
                
                print('\n#\tContext loaded from {}'.format(filename))
                return "context loaded", prompt_file
            print('\n#\tInvalid command format, did you specify which file to load?')
            return "context loaded", prompt_file
    
    return "", prompt_file