import os
import time

from pathlib import Path


class PromptFile:
    def __init__(self, file_name, config):
        self.file_name = file_name
        self.config = config

        # create the file if it doesn't exist
        if not os.path.isfile(self.file_name):
            with open(self.file_name, 'w') as f:
                f.write('## engine: {}\n'.format(config['engine']))
                f.write('## temperature: {}\n'.format(config['temperature']))
                f.write('## max_tokens: {}\n'.format(config['max_tokens']))
                f.write('## shell: {}\n'.format(config['shell']))
                f.write('## token_count: {}\n'.format(0))
        self.config['token_count'] = self.get_token_count()
        
        if self.has_headers() == False:
            self.set_headers(self.config)

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
        if self.has_prompt_headers() == False:
            self.config = {
                'engine': 'davinci_codex_msft',
                'temperature': 0,
                'max_tokens': 300,
                'shell': '',
                'token_count': 0
            }
            return self.config
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            engine = lines[0].split(':')[1].strip()
            temperature = lines[1].split(':')[1].strip()
            max_tokens = lines[2].split(':')[1].strip()
            shell = lines[3].split(':')[1].strip()
            token_count = lines[4].split(':')[1].strip()
        
        self.config = {
            'engine': engine,
            'temperature': float(temperature),
            'max_tokens': int(max_tokens),
            'shell': shell,
            'token_count': int(token_count)
        }

        return self.config 
    
    def set_headers(self, config):
        """
        Set the prompt headers with the new config
        """
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
        newf.append('## token_count: {}\n'.format(config['token_count']))

        if self.has_headers():
            lines = lines[5:] # drop old headers
        
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
                headers = lines[:5]
                prompt = lines[7:] # drop first 2 lines of prompt
            with open(self.file_name, 'w') as f:
                f.writelines(headers)
                f.writelines(prompt)

        prompt = ""
        # get input from prompt file
        # skip the header lines
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            lines = lines[5:] # skip headers
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
                token_count = int(lines[4].split(':')[1].strip())
        
        true_token_count = 0
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
            # count the number of words in the prompt file
            for line in lines[5:]:
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
            save_name = os.path.join(os.path.dirname(self.file_name), "saved", save_name)
            with Path(save_name).open('w') as f:
                f.writelines(lines)