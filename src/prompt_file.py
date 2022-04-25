import os
import time

from pathlib import Path


class PromptFile:
    context_source_filename = ""
    default_context_filename = "current_context.txt"
    default_file_path = os.path.join(os.path.dirname(__file__), "..", default_context_filename)
    default_config_path = os.path.join(os.path.dirname(__file__), "..", "current_context.config")

    def __init__(self, file_name, config):
        self.context_source_filename = "{}-context.txt".format(config['shell']) #  feel free to set your own default context path here
        
        self.file_path = self.default_file_path
        self.config_path = self.default_config_path

        # loading in one of the saved contexts
        if file_name != self.default_context_filename:
            self.load_context(file_name, True)

    def has_config(self):
        """
        Check if the prompt file has a corresponding config file
        """
        return os.path.isfile(self.config_path)
    
    def read_config(self):
        """
        Read the prompt config and return a dictionary
        """

        if self.has_config() == False:
            self.set_config(self.config)
            return self.config
        
        with open(self.config_path, 'r') as f:
            lines = f.readlines()

        config = {
            'engine': lines[0].split(':')[1].strip(),
            'temperature': float(lines[1].split(':')[1].strip()),
            'max_tokens': int(lines[2].split(':')[1].strip()),
            'shell': lines[3].split(':')[1].strip(),
            'multi_turn': lines[4].split(':')[1].strip(),
            'token_count': int(lines[5].split(':')[1].strip())
        }

        self.config = config
        return self.config 
    
    def set_config(self, config):
        """
        Set the prompt headers with the new config
        """
        self.config = config
        
        with open(self.config_path, 'w') as f:
            f.write('engine: {}\n'.format(self.config['engine']))
            f.write('temperature: {}\n'.format(self.config['temperature']))
            f.write('max_tokens: {}\n'.format(self.config['max_tokens']))
            f.write('shell: {}\n'.format(self.config['shell']))
            f.write('multi_turn: {}\n'.format(self.config['multi_turn']))
            f.write('token_count: {}\n'.format(self.config['token_count']))
    
    def show_config(self):
        print('\n')
        # read the dictionary into a list of # lines
        lines = []
        for key, value in self.config.items():
            lines.append('# {}: {}\n'.format(key, value))
        print(''.join(lines))
    
    def add_input_output_pair(self, user_query, prompt_response):
        """
        Add lines to file_name and update the token_count
        """

        with open(self.file_path, 'a') as f:
            f.write(user_query)
            f.write(prompt_response)
        
        if self.config['multi_turn'] == 'on':
            self.config['token_count'] += len(user_query.split()) + len(prompt_response.split())
            self.set_config(self.config)
    
    def read_prompt_file(self, input):
        """
        Get the updated prompt file
        Checks for token overflow and appends the current input

        Returns: the prompt file after appending the input
        """

        input_tokens_count = len(input.split())
        need_to_refresh = (self.config['token_count'] + input_tokens_count > 2048)

        if need_to_refresh:
            # delete first 2 lines of prompt context file
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
                prompt = lines[2:] # drop first 2 lines of prompt
            with open(self.file_path, 'w') as f:
                f.writelines(prompt)

        # get input from prompt file
        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        return ''.join(lines)
    
    def get_token_count(self):
        """
        Get the actual token count
        """
        token_count = 0
        if self.has_config():
            with open(self.config_path, 'r') as f:
                lines = f.readlines()
                token_count = int(lines[5].split(':')[1].strip())
        
        true_token_count = 0
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
            # count the number of words in the prompt file
            for line in lines:
                true_token_count += len(line.split())
        
        if true_token_count != token_count:
            self.config['token_count'] = true_token_count
            self.set_config(self.config)
        
        return true_token_count
    
    def clear(self):
        """
        Clear the prompt file, while keeping the config
        Note: saves a copy to the deleted folder
        """
        config = self.read_config()
        filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
            filename = os.path.join(os.path.dirname(__file__), "..", "deleted", filename)
            with Path(filename).open('w') as f:
                f.writelines(lines)
        
        # delete the prompt file
        with open(self.file_path, 'w') as f:
            f.write('')
        
        print("\n#   Context has been cleared, temporarily saved to {}".format(filename))
        self.set_config(config)
    
    def clear_last_interaction(self):
        """
        Clear the last interaction from the prompt file
        """
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                lines.pop()
                lines.pop()
                with open(self.file_path, 'w') as f:
                    f.writelines(lines)
            print("\n#   Unlearned interaction")
    
    def save_to(self, save_name):
        """
        Save the prompt file to a new location
        """
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
            if not save_name.endswith('.txt'):
                save_name = save_name + '.txt'
            save_path = os.path.join(os.path.dirname(__file__), "..", "contexts", save_name)
            with Path(save_path).open('w') as f:
                f.writelines(lines)
        
        print('\n#   Context saved to {}'.format(save_name))
    
    def start_multi_turn(self):
        """
        Turn on context mode
        """
        self.config['multi_turn'] = 'on'
        self.set_config(self.config)
        print("\n#   Multi turn mode is on")

    
    def stop_multi_turn(self):
        """
        Turn off context mode
        """
        self.config['multi_turn'] = 'off'
        self.set_config(self.config)
        print("\n#   Multi turn mode is off")
    
    def default_context(self):
        """
        Go to default context
        """
        self.load_context(self.context_source_filename)
    
    def load_context(self, filename, initialize=False):
        """
        Loads a context file into current_context

        """
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        filepath = Path(os.path.join(os.path.dirname(__file__), "..", "contexts", filename))

        # check if the file exists
        if filepath.exists():
            with filepath.open('r') as f:
                lines = f.readlines()
            
            config = {
                'engine': lines[0].split(':')[1].strip(),
                'temperature': float(lines[1].split(':')[1].strip()),
                'max_tokens': int(lines[2].split(':')[1].strip()),
                'shell': lines[3].split(':')[1].strip(),
                'multi_turn': lines[4].split(':')[1].strip(),
                'token_count': int(lines[5].split(':')[1].strip())
            }

            # use new config if old config doesn't exist
            if initialize == False or self.has_config() == False:
                self.set_config(config)
            else:
                self.config = self.read_config()

            lines = lines[6:]

            # write to the current prompt file if we are in multi-turn mode
            if initialize == False or self.config['multi_turn'] == "off":
                with open(self.file_path, 'w') as f:
                    f.writelines(lines)
                
                if initialize == False:
                    print('\n#   Context loaded from {}'.format(filename))
        else:
            print("\n#   File not found")
            return False