import contextlib
import io
import json
import runpy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
import openai


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'src'))

import prompt_file
from api_config import get_model
from prompt_file import PromptFile


class SerializedRequestTests(unittest.TestCase):
    def run_cli(self, endpoint, settings='', saved=None, context=None, context_name='custom'):
        requests = []
        clients = []
        real_client = openai.OpenAI

        def respond(request):
            requests.append(request)
            return httpx.Response(200, json={
                'id': 'offline-completion', 'object': 'chat.completion',
                'created': 0, 'model': json.loads(request.content)['model'],
                'choices': [{'index': 0, 'finish_reason': 'stop',
                             'message': {'role': 'assistant', 'content': 'pwd'}}],
            })

        def create_client(**options):
            client = real_client(
                **options, max_retries=0,
                http_client=httpx.Client(transport=httpx.MockTransport(respond)),
            )
            clients.append(client)
            return client

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'src').mkdir()
            script = root / 'src' / 'codex_query.py'
            shutil.copyfile(REPO_ROOT / 'src' / 'codex_query.py', script)
            shutil.copytree(REPO_ROOT / 'contexts', root / 'contexts')
            api_config = root / 'src' / 'openaiapirc'
            api_config.write_text(
                '[openai]\nsecret_key=test-key\nbase_url=' + endpoint + '\n' + settings,
                encoding='utf-8',
            )
            active_config = root / 'current_context.config'
            active_prompt = root / 'current_context.txt'
            if saved:
                active_config.write_text(self.context_config(saved), encoding='utf-8')
                active_prompt.write_text('# previous question\nprintf previous\n', encoding='utf-8')
            if context:
                (root / 'contexts' / (context_name + '.txt')).write_text(
                    ''.join('## ' + line + '\n' for line in self.context_config(context).splitlines())
                    + '# saved question\nprintf saved\n', encoding='utf-8',
                )

            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(PromptFile, 'default_file_path', str(active_prompt)))
                stack.enter_context(patch.object(PromptFile, 'default_config_path', str(active_config)))
                stack.enter_context(patch.object(prompt_file, '__file__', str(root / 'src' / 'prompt_file.py')))
                stack.enter_context(patch.object(prompt_file, 'API_KEYS_LOCATION', str(api_config)))
                stack.enter_context(patch('openai.OpenAI', side_effect=create_client))
                process = stack.enter_context(patch('psutil.Process'))
                process.return_value.name.return_value = 'bash'
                output = stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                try:
                    if context:
                        with patch('sys.stdin', io.StringIO('# load context ' + context_name + '\n')):
                            with self.assertRaises(SystemExit) as stopped:
                                runpy.run_path(str(script), run_name='__main__')
                            self.assertEqual(stopped.exception.code, 0)
                    with patch('sys.stdin', io.StringIO('# show directory\n')):
                        runpy.run_path(str(script), run_name='__main__')
                finally:
                    for client in clients:
                        client.close()
            self.assertNotIn('Codex CLI error', output.getvalue())
            self.assertIn('pwd', output.getvalue())
            self.assertEqual(len(requests), 1)
            history = active_prompt.read_text(encoding='utf-8')
        request = requests[0]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(str(request.url), endpoint.rstrip('/') + '/chat/completions')
        body = json.loads(request.content)
        self.assertEqual(set(body), {'model', 'messages', 'temperature', 'max_tokens'})
        self.assertEqual(body['messages'][0]['role'], 'system')
        self.assertIn('# show directory', body['messages'][1]['content'])
        return body, history

    @staticmethod
    def context_config(model_line):
        return (model_line + '\ntemperature: 0\nmax_tokens: 300\nshell: bash\n'
                'multi_turn: on\ntoken_count: 5\n')

    def test_direct_regional_defaults_and_explicit_models(self):
        cases = (
            ('', 'MiniMax-M3.1-Flash'),
            ('model=\n', 'MiniMax-M3.1-Flash'),
            ('model=MiniMax-M3.1-Flash\n', 'MiniMax-M3.1-Flash'),
            ('model=MiniMax-M3\n', 'MiniMax-M3'),
            ('model=MiniMax-M2.7\n', 'MiniMax-M2.7'),
            ('engine=MiniMax-M2.7\n', 'MiniMax-M2.7'),
            ('model=\nengine=custom:model\n', 'custom:model'),
            ('model=custom:model\nengine=MiniMax-M3\n', 'custom:model'),
        )
        for endpoint in ('https://api.minimax.io/v1', 'https://api.minimaxi.com/v1/'):
            for settings, expected in cases:
                with self.subTest(endpoint=endpoint, settings=settings):
                    body, _ = self.run_cli(endpoint, settings)
                    self.assertEqual(body['model'], expected)
                    self.assertEqual(body['max_tokens'], 32768 if expected in (
                        'MiniMax-M3.1-Flash', 'MiniMax-M3') else 300)

    def test_saved_active_model_and_history_survive_default(self):
        for model_line in ('model: MiniMax-M3.1-Flash', 'model: MiniMax-M2.7', 'engine: custom:model'):
            with self.subTest(model_line=model_line):
                body, history = self.run_cli('https://api.minimax.io/v1', saved=model_line)
                self.assertEqual(body['model'], model_line.split(': ', 1)[1])
                self.assertEqual(body['max_tokens'], 300)
                self.assertIn('printf previous', body['messages'][1]['content'])
                self.assertIn('printf previous', history)
                self.assertIn('pwd', history)

    def test_loading_saved_context_preserves_model_and_history(self):
        for model_line in ('model: MiniMax-M3.1-Flash', 'model: MiniMax-M2.7', 'engine: custom:model'):
            with self.subTest(model_line=model_line):
                body, history = self.run_cli('https://api.minimax.io/v1', context=model_line)
                self.assertEqual(body['model'], model_line.split(': ', 1)[1])
                self.assertEqual(body['max_tokens'], 300)
                self.assertIn('printf saved', body['messages'][1]['content'])
                self.assertIn('printf saved', history)

    def test_saved_context_replacing_bundled_example_keeps_budget(self):
        body, _ = self.run_cli(
            'https://api.minimax.io/v1', context='model: custom:model',
            context_name='bash-context',
        )
        self.assertEqual(body['model'], 'custom:model')
        self.assertEqual(body['max_tokens'], 300)

    def test_custom_endpoint_keeps_explicit_model(self):
        body, _ = self.run_cli('https://gateway.example/v1', 'model=custom:model\n')
        self.assertEqual(body['model'], 'custom:model')

    def test_unverified_endpoints_have_no_minimax_default(self):
        for endpoint in ('', 'https://gateway.example/v1',
                         'https://api.minimax.io/v1/proxy',
                         'https://api.minimax.io.example/v1'):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(get_model({'base_url': endpoint}), '')


if __name__ == '__main__':
    unittest.main()
