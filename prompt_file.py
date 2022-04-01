from email.policy import default
import os
import time

from pathlib import Path


class PromptFile:
    default_file_name = "openai_completion_input.txt"

    def __init__(self, file_name, config):
        if file_name != self.default_file_name:
            file_full_path = os.path.join(os.path.dirname(__file__), "contexts", file_name)

            # if we don't have a previous context, use the specified one
            if os.path.isfile(file_full_path):
                context = "off"

                if os.path.isfile(self.default_file_name):
                    with open(self.default_file_name, 'r') as f:
                        lines = f.readlines()
                        engine = lines[0].split(':')[1].strip()
                        temperature = lines[1].split(':')[1].strip()
                        max_tokens = lines[2].split(':')[1].strip()
                        shell = lines[3].split(':')[1].strip()
                        context = lines[4].split(':')[1].strip()
                        token_count = lines[5].split(':')[1].strip()
                    
                    # use previously set configs
                    config = {
                        'engine': engine,
                        'temperature': float(temperature),
                        'max_tokens': int(max_tokens),
                        'shell': shell,
                        'context': context,
                        'token_count': int(token_count)
                    }

                if context == "off":
                    with open(file_full_path, 'r') as f:
                        lines = f.readlines()
                        with open(self.default_file_name, 'w') as f:
                            f.writelines(lines)
        
        self.file_name = self.default_file_name
        self.config = config
        
        if self.has_headers() == False:
            self.set_headers(self.config)
        
        if config['context'] == 'on':
            self.config['token_count'] = self.get_token_count()

    def has_headers(self):
        """
        Check if the prompt file has headers
        """
        if os.path.isfile(self.file_name) == False:
            return False
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            # this is not a strict check, but it should be enough
            if lines[0].__contains__('## engine:'):
                return True
            else:
                return False
    
    def read_headers(self):
        """
        Read the prompt headers and return a dictionary
        """
        if self.has_headers() == False:
            self.config = {
                'engine': 'davinci_codex_msft',
                'temperature': 0,
                'max_tokens': 300,
                'shell': '',
                'context': 'off',
                'token_count': 0
            }
            return self.config
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            engine = lines[0].split(':')[1].strip()
            temperature = lines[1].split(':')[1].strip()
            max_tokens = lines[2].split(':')[1].strip()
            shell = lines[3].split(':')[1].strip()
            context = lines[4].split(':')[1].strip()    
            token_count = lines[5].split(':')[1].strip()
        
        self.config = {
            'engine': engine,
            'temperature': float(temperature),
            'max_tokens': int(max_tokens),
            'shell': shell,
            'context': context,
            'token_count': int(token_count)
        }

        return self.config 
    
    def set_headers(self, config):
        """
        Set the prompt headers with the new config
        """
        if self.file_name != self.default_file_name:
            # we don't want to edit saved contexts
            return
        
        self.config = config
        lines = []
        if os.path.isfile(self.file_name):
            lines = open(self.file_name, 'r').readlines() # read old content

        newf = []
        # add headers at the beginning
        newf.append('## engine: {}\n'.format(config['engine']))
        newf.append('## temperature: {}\n'.format(config['temperature']))
        newf.append('## max_tokens: {}\n'.format(config['max_tokens']))
        newf.append('## shell: {}\n'.format(config['shell']))
        newf.append('## context_mode: {}\n'.format(config['context']))
        newf.append('## token_count: {}\n'.format(config['token_count']))

        if self.has_headers():
            lines = lines[6:] # drop old headers
        
        # add lines to newf
        newf.extend(lines)
        
        with open(self.file_name, 'w') as f:
            f.writelines(newf)
    
    def add_input_output_pair(self, user_query, prompt_response):
        """
        Add lines to file_name and update the token_count
        """

        with open(self.file_name, 'a') as f:
            f.write(user_query)
            f.write(prompt_response)
        
        if self.config['context'] == 'on':
            self.config['token_count'] += len(user_query.split()) + len(prompt_response.split())
            self.set_headers(self.config)
    
    def read_prompt_file(self, input):
        """
        Get the updated prompt file
        Checks for token overflow and appends the current input

        Returns: the prompt file after appending the input
        """

        input_tokens_count = len(input.split())
        need_to_refresh = (self.config['token_count'] + input_tokens_count > 2048)

        if need_to_refresh:
            # TODO use multi-line metadata and dependency metadata to track this
            # delete first 2 lines of prompt context file
            with open(self.file_name, 'r') as f:
                lines = f.readlines()
                headers = lines[:6]
                prompt = lines[8:] # drop first 2 lines of prompt
            with open(self.file_name, 'w') as f:
                f.writelines(headers)
                f.writelines(prompt)

        prompt = ""
        # get input from prompt file
        # skip the header lines
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            lines = lines[6:] # skip headers
            prompt = ''.join(lines)

        return prompt
    
    def get_token_count(self):
        """
        Get the actual token count
        """
        token_count = 0
        if self.has_headers():
            with open(self.file_name, 'r') as f:
                lines = f.readlines()
                token_count = int(lines[5].split(':')[1].strip())
        
        true_token_count = 0
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            # count the number of words in the prompt file
            for line in lines[6:]:
                true_token_count += len(line.split())
        
        if true_token_count != token_count:
            self.config['token_count'] = true_token_count
            self.set_headers(self.config)
        
        return true_token_count
    
    def clear(self):
        """
        Clear the prompt file, while keeping the headers
        Note: saves a copy to the deleted folder
        """
        config = self.read_headers()
        filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            filename = os.path.join(os.path.dirname(self.file_name), "deleted", filename)
            with Path(filename).open('w') as f:
                f.writelines(lines)
        
        # delete the prompt file
        with open(self.file_name, 'w') as f:
            f.write('')
            print("\n#\tContext has been cleared, temporarily saved to {}".format(filename))
        self.set_headers(config)
    
    def clear_last_interaction(self):
        """
        Clear the last interaction from the prompt file
        """
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                lines.pop()
                lines.pop()
                with open(self.file_name, 'w') as f:
                    f.writelines(lines)
            print("\n#   Unlearned interaction")
    
    def save_to(self, save_name):
        """
        Save the prompt file to a new location
        """
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            if not save_name.endswith('.txt'):
                save_name = save_name + '.txt'
            save_name = os.path.join(os.path.dirname(self.file_name), "contexts", save_name)
            with Path(save_name).open('w') as f:
                f.writelines(lines)
    
    def turn_on_context(self):
        """
        Turn on context mode
        """
        self.config['context'] = 'on'
        self.set_headers(self.config)
        print("\n#   Context mode is now on")

    
    def turn_off_context(self):
        """
        Turn off context mode
        """
        self.config['context'] = 'off'
        self.set_headers(self.config)
        print("\n#   Context mode is now off")
    
    def default_context(self):
        """
        Go to default context
        """

        default_context_path = os.path.join(os.path.dirname(self.file_name), "contexts", "{}_context.txt".format(self.config['shell']))
        if os.path.exists(default_context_path):
            # write the default context to the prompt file
            with open(default_context_path, 'r') as f:
                lines = f.readlines()
                lines[4] = '## context_mode: {}\n'.format(self.config['context'])
                with open(self.file_name, 'w') as f:
                    f.writelines(lines)
            print("\n#   Context has been set to shell default")
        else:
            print("\n#   No default shell context found")
    
    def load_context(self, filename):
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
        filename = os.path.join(os.path.dirname(self.file_name), "contexts", filename)

        # check if the file exists
        if os.path.isfile(filename):
            with Path(filename).open('r') as f:
                lines = f.readlines()
            
            # preserve old headers
            lines[0] = '## engine: {}\n'.format(self.config['engine'])
            lines[1] = '## temperature: {}\n'.format(self.config['temperature'])
            lines[2] = '## max_tokens: {}\n'.format(self.config['max_tokens'])
            lines[3] = '## shell: {}\n'.format(self.config['shell'])
            lines[4] = '## context_mode: {}\n'.format(self.config['context'])

            # write to the current prompt file
            with open(self.file_name, 'w') as f:
                f.writelines(lines)
            print('\n#\tContext loaded from {}'.format(filename))
        else:
            print("\n#\tFile not found")
            return False