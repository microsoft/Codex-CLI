import openai
openai.api_type = "azure"
openai.api_base = "https://gavsgpt-openai.openai.azure.com/"
openai.api_version = "2022-12-01"
openai.api_key = "<your token>"
engine = "test-code"
print(engine, openai.api_type, openai.api_key, openai.api_base, openai.api_version, openai.organization)
codex_query="What is OpenAI?"
response = openai.Completion.create(engine=engine, prompt=codex_query, stop="#")
print (response)
print (response['choices'][0]['text'])
