import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'src'))

import codex_query
from commands import get_command_result
from prompt_file import PromptFile


class InitializeTests(unittest.TestCase):
    def initialize_with(self, base_url, model):
        config_text = (
            '[openai]\n'
            'organization_id=\n'
            'secret_key=test-key\n'
            'base_url={}\n'
            'model={}\n'
        ).format(base_url, model)

        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / 'openaiapirc'
            config_path.write_text(config_text, encoding='utf-8')
            with patch.object(codex_query, 'API_KEYS_LOCATION', str(config_path)):
                with patch.object(codex_query, 'PromptFile') as prompt_file:
                    with patch.object(codex_query.openai, 'OpenAI') as client:
                        codex_query.initialize()

        return client, prompt_file

    def test_initialize_configures_global_endpoint(self):
        client, prompt_file = self.initialize_with(
            'https://api.minimax.io/v1/',
            'MiniMax-M3'
        )

        client.assert_called_once_with(
            api_key='test-key',
            base_url='https://api.minimax.io/v1'
        )
        self.assertEqual(prompt_file.call_args.args[1]['model'], 'MiniMax-M3')

    def test_initialize_configures_china_endpoint(self):
        client, prompt_file = self.initialize_with(
            'https://api.minimaxi.com/v1',
            'MiniMax-M2.7'
        )

        client.assert_called_once_with(
            api_key='test-key',
            base_url='https://api.minimaxi.com/v1'
        )
        self.assertEqual(prompt_file.call_args.args[1]['model'], 'MiniMax-M2.7')


class ChatCompletionTests(unittest.TestCase):
    def test_client_exposes_chat_completions(self):
        client = codex_query.openai.OpenAI(
            api_key='test-key',
            base_url='https://api.minimax.io/v1'
        )
        try:
            self.assertTrue(callable(client.chat.completions.create))
        finally:
            client.close()

    def test_create_chat_completion_uses_configured_model(self):
        client = MagicMock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='ls -la'))]
        )
        config = {
            'model': 'MiniMax-M3',
            'shell': 'bash',
            'temperature': 0,
            'max_tokens': 300
        }

        result = codex_query.create_chat_completion(client, config, '# list files')

        self.assertEqual(result, 'ls -la')
        request = client.chat.completions.create.call_args.kwargs
        self.assertEqual(request['model'], 'MiniMax-M3')
        self.assertEqual(request['messages'][1], {
            'role': 'user',
            'content': '# list files'
        })
        self.assertNotIn('stop', request)


class ConfigurationTests(unittest.TestCase):
    def test_prompt_file_persists_model(self):
        config = {
            'model': 'MiniMax-M3',
            'temperature': 0,
            'max_tokens': 300,
            'shell': 'bash',
            'multi_turn': 'off',
            'token_count': 0
        }

        with tempfile.TemporaryDirectory() as directory:
            prompt_file = PromptFile.__new__(PromptFile)
            prompt_file.config_path = Path(directory) / 'context.config'
            prompt_file.set_config(config)

            self.assertEqual(prompt_file.read_config(), config)

    def test_set_model_command_updates_config(self):
        prompt_file = MagicMock()
        prompt_file.config = {
            'model': 'MiniMax-M3',
            'temperature': 0,
            'max_tokens': 300,
            'shell': 'bash',
            'multi_turn': 'off',
            'token_count': 0
        }

        with patch('builtins.print'):
            result, returned_prompt_file = get_command_result(
                '# set model MiniMax-M2.7',
                prompt_file
            )

        self.assertEqual(result, 'config set')
        self.assertIs(returned_prompt_file, prompt_file)
        self.assertEqual(prompt_file.config['model'], 'MiniMax-M2.7')
        prompt_file.set_config.assert_called_once_with(prompt_file.config)


if __name__ == '__main__':
    unittest.main()
