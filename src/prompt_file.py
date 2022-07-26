import os
from pyexpat import model
import time
import configparser
import pickle

from pathlib import Path
from openai import Model
from prompt_engine.code_engine import CodeEngine, PromptEngineConfig, Interaction

API_KEYS_LOCATION = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'openaiapirc')


class ModelConfig:
    """
    Interaction class is used to store the model config to be used in the prompt engine
    """
    def __init__(self, **kwargs):
        self.engine = kwargs['engine'] if kwargs['engine'] else 'code-davinci-002'
        self.temperature = float(kwargs['temperature']) if kwargs['temperature'] else 0
        self.max_tokens = int(kwargs['max_tokens']) if kwargs['max_tokens'] else 300
        self.shell = kwargs['shell'] if kwargs['shell'] else 'powershell'
        self.multi_turn = kwargs['multi_turn'] if kwargs['multi_turn'] else 'on'
        self.token_count = int(kwargs['token_count']) if kwargs['token_count'] else 0

class Prompt:
    default_context_filename = "current_context.yaml"
    default_file_path = os.path.join(os.path.dirname(__file__), "..", default_context_filename)
    default_config_path = os.path.join(os.path.dirname(__file__), "..", "current_context.pickle")

    def __init__(self, shell, engine):
        
        # check if default_config file exists, otherwise create it from the default_context_filename and save it
        if not os.path.exists(self.default_config_path):
            self.prompt_engine = self.create_prompt_engine_from_yaml(self.default_config_path)
            self.save_prompt_engine(self.prompt_engine, self.default_config_path)
        else:
            # TODO: Change this to assignment operator (:=), recieving invalid syntax
            if not os.path.exists(self.default_file_path):
                shell_context_path = Path(os.path.join(os.path.dirname(__file__), "..", "contexts", f"{shell}-context.yaml"))
                self.prompt_engine = self.create_prompt_engine_from_yaml(shell_context_path)
                self.save_prompt_engine(self.prompt_engine, self.default_config_path)
            else:
                temp = self.load_prompt_engine(self.default_config_path)
                if temp != None:
                    self.prompt_engine = temp
                else:
                    self.prompt_engine = self.create_prompt_engine_from_yaml(self.default_config_path)
                    self.save_prompt_engine(self.prompt_engine, self.default_config_path)
    
    def create_prompt_engine_from_yaml(self, yaml_path):
        prompt_engine = CodeEngine()
        prompt_engine.load_yaml(yaml_path)
        return prompt_engine

    def show_config(self):
        print('\n')
        # read the dictionary into a list of # lines
        lines = []
        for key, value in self.prompt_engine.config.model_config.__dict__.items():
            lines.append('# {}: {}\n'.format(key, value))
        print(''.join(lines))
    
    def add_input_output_pair(self, user_query, prompt_response):
        """
        Add an input/output pair to the prompt engine
        """

        self.prompt_engine.add_interaction(user_query, prompt_response)
    
    def clear(self):
        """
        Clear the prompt file, while keeping the config
        Note: saves a copy to the deleted folder
        """
        self.prompt_engine.reset_context()
    
    def clear_last_interaction(self):
        """
        Clear the last interaction from the prompt file
        """
        self.prompt_engine.remove_last_interaction()
    
    def start_multi_turn(self):
        """
        Turn on context mode
        """
        self.prompt_engine.config.model_config.multi_turn = "on"

    
    def stop_multi_turn(self):
        """
        Turn off context mode
        """
        self.prompt_engine.config.model_config.multi_turn = "off"
    
    def default_context(self):
        """
        Go to default context
        """
        self.load_context(self.context_source_filename)
    
    def load_context(self, filename, initialize=False):
        """
        Loads a context file into current_context
        """
        if not filename.endswith('.yaml'):
            filename = filename + '.yaml'
        filepath = Path(os.path.join(os.path.dirname(__file__), "..", "contexts", filename))

        # check if the file exists
        if filepath.exists():
            
            # read in the engine name from openaiapirc
            config = configparser.ConfigParser()
            config.read(API_KEYS_LOCATION)
            engine = config['openai']['engine'].strip('"').strip("'")
            
            self.prompt_engine = self.create_prompt_engine_from_yaml(filepath)
            self.prompt_engine.config.model_config.engine = engine ## Needed?

            self.save_prompt_engine(self.prompt_engine, self.default_config_path)

        else:
            print("\n#   File not found")
            return False

        

    def save_prompt_engine(self, obj, file_path = os.path.join(os.path.dirname(__file__), "..", "current_context.pickle")):
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(obj, f)
        except Exception as e:
            raise Exception("Error saving prompt engine: {}".format(e))
            
    def load_prompt_engine(self, file_path = os.path.join(os.path.dirname(__file__), "..", "current_context.pickle")):
        try:
            with open(file_path, 'rb') as f:
                self.prompt_engine = pickle.load(f)
                return self.prompt_engine
            return None
        except Exception as e:
            print("Error loading prompt engine: {}".format(e))
            return None
