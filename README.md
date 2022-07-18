# Codex CLI - Natural Language Command Line Interface

This project uses [GPT-3 Codex](https://openai.com/blog/openai-codex/) to convert natural language commands into commands in PowerShell, Z shell and Bash.

![Codex Cli GIF](codex_cli.gif)


The Command Line Interface (CLI) was the first major User Interface we used to interact with machines. It's incredibly powerful, you can do almost anything with a CLI, but it requires the user to express their intent extremely precisely. The user needs to _know the language of the computer_. 

With the advent of Large Language Models (LLMs), particularly those that have been trained on code, it's possible to interact with a CLI using Natural Language (NL). In effect, these models understand natural language _and_ code well enough that they can translate from one to another. 

This project aims to offer a cross-shell NL->Code experience to allow users to interact with their favorite CLI using NL. The user enters a command, like "what's my IP address", hits `Ctrl + G` and gets a suggestion for a command idiomatic to the shell they're using. The project uses the GPT-3 Codex model off-the-shelf, meaning the model has not been explicitly trained for the task. Instead we rely on a discipline called prompt engineering (see [section](#prompt-engineering-and-context-files) below) to coax the right commands from Codex. 

**Note: The model can still make mistakes! Don't run a command if you don't understand it. If you're not sure what a command does, hit `Ctrl + C` to cancel it**.

This project took technical inspiration from the [zsh_codex](https://github.com/tom-doerr/zsh_codex) project, extending its functionality to span multiple shells and to customize the prompts passed to the model (see prompt engineering section below).

## Statement of Purpose
This repository aims to grow the understanding of using Codex in applications by providing an example of implementation and references to support the [Microsoft Build conference in 2022](https://mybuild.microsoft.com/). It is not intended to be a released product. Therefore, this repository is not for discussing OpenAI API or requesting new features.

## Requirements
* [Python 3.7.1+](https://www.python.org/downloads/)
    * \[Windows\]: Python is added to PATH.
* An [OpenAI account](https://openai.com/api/)
    * [OpenAI API Key](https://beta.openai.com/account/api-keys).
    * [OpenAI Organization Id](https://beta.openai.com/account/org-settings). If you have multiple organizations, please update your [default organization](https://beta.openai.com/account/api-keys) to the one that has access to codex engines before getting the organization Id.
    * [OpenAI Engine Id](https://beta.openai.com/docs/engines/codex-series-private-beta). It provides access to a model. For example, `code-davinci-002` or `code-cushman-001`. See [here](#what-openai-engines-are-available-to-me) for checking available engines.

## Installation

Please follow the installation instructions for PowerShell, bash or zsh from [here](./Installation.md).

## Usage

Once configured for your shell of preference, you can use the Codex CLI by writing a comment (starting with `#`) into your shell, and then hitting `Ctrl + G`.

The Codex CLI supports two primary modes: single-turn and multi-turn.

By default, multi-turn mode is off. It can be toggled on and off using the `# start multi-turn` and `# stop multi-turn` commands.

If the multi-turn mode is on, the Codex CLI will "remember" past interactions with the model, allowing you to refer back to previous actions and entities. If, for example, you asked the Codex CLI to change your time zone to mountain, and then said "change it back to pacific", the model would have the context from the previous interaction to know that "it" is the user's timezone:

```powershell
# change my timezone to mountain
tzutil /s "Mountain Standard Time"

# change it back to pacific
tzutil /s "Pacific Standard Time"
```

The tool creates a `current_context.txt` file that keeps track of past interactions, and passes them to the model on each subsequent command. 

When multi-turn mode is off, this tool will not keep track of interaction history. There are tradeoffs to using multi-turn mode - though it enables compelling context resolution, it also increases overhead. If, for example, the model produces the wrong script for the job, the user will want to remove that from the context, otherwise future conversation turns will be more likely to produce the wrong script again. With multi-turn mode off, the model will behave completely deterministically - the same command will always produce the same output. 

Any time the model seems to output consistently incorrect commands, you can use the `# stop multi-turn` command to stop the model from remembering past interactions and load in your default context. Alternatively, the `# default context` command does the same while preserving the multi-turn mode as on.

## Commands

| Command | Description |
|--|--|
| `start multi-turn` | Starts a multi-turn experience |
| `stop multi-turn` | Stops a multi-turn experience and loads default context |
| `load context <filename>` | Loads the context file from `contexts` folder |
| `default context` | Loads default shell context |
| `view context` | Opens the context file in a text editor |
| `save context <filename>` | Saves the context file to `contexts` folder, if name not specified, uses current date-time |
| `show config` | Shows the current configuration of your interaction with the model |
| `set <config-key> <config-value>` | Sets the configuration of your interaction with the model |


Feel free to improve your experience by changing the token limit, engine id and temperature using the set command. For example, `# set engine cushman-codex`, `# set temperature 0.5`, `# set max_tokens 50`.

## Prompt Engineering and Context Files

This project uses a discipline called _prompt engineering_ to coax GPT-3 Codex to generate commands from natural language. Specifically, we pass the model a series of examples of NL->Commands, to give it a sense of the kind of code it should be writing, and also to nudge it towards generating commands idiomatic to the shell you're using. These examples live in the `contexts` directory. See snippet from the PowerShell context below:

```powershell
# what's the weather in New York?
(Invoke-WebRequest -uri "wttr.in/NewYork").Content

# make a git ignore with node modules and src in it
"node_modules
src" | Out-File .gitignore

# open it in notepad
notepad .gitignore
```

Note that this project models natural language commands as comments, and provide examples of the kind of PowerShell scripts we expect the model to write. These examples include single line completions, multi-line completions, and multi-turn completions (the "open it in notepad" example refers to the `.gitignore` file generated on the previous turn). 

When a user enters a new command (say "what's my IP address"), we simple append that command onto the context (as a comment) and ask Codex to generate the code that should follow it. Having seen the examples above, Codex will know that it should write a short PowerShell script that satisfies the comment. 

## Building your own Contexts

This project comes pre-loaded with contexts for each shell, along with some bonus contexts with other capabilities. Beyond these, you can build your own contexts to coax other behaviors out of the model. For example, if you want the Codex CLI to produce Kubernetes scripts, you can create a new context with examples of commands and the `kubectl` script the model might produce:

```bash
# make a K8s cluster IP called my-cs running on 5678:8080
kubectl create service clusterip my-cs --tcp=5678:8080
```

Add your context to the `contexts` folder and run `load context <filename>` to load it. You can also change the default context from to your context file inside `src\prompt_file.py`.

Note that Codex will often produce correct scripts without any examples. Having been trained on a large corpus of code, it frequently knows how to produce specific commands. That said, building your own contexts helps coax the specific kind of script you're looking for - whether it's long or short, whether it declares variables or not, whether it refers back to previous commands, etc. You can also provide examples of your own CLI commands and scripts, to show Codex other tools it should consider using.

One important thing to consider is that if you add a new context, keep the multi-turn mode on to avoid our automatic defaulting (which was added to keep faulty contexts from breaking your experience).

We have added a [cognitive services context](./contexts/CognitiveServiceContext.md) which uses the cognitive services API to provide text to speech type responses as an example.

## Troubleshooting

Use `DEBUG_MODE` to use a terminal input instead of the stdin and debug the code. This is useful when adding new commands and understanding why the tool is unresponsive.

Sometimes the `openai` package will throws errors that aren't caught by the tool, you can add a catch block at the end of `codex_query.py` for that exception and print a custom error message.

## FAQ
### What OpenAI engines are available to me?
You might have access to different [OpenAI engines](https://beta.openai.com/docs/api-reference/engines) per OpenAI organization. To check what engines are available to you, one can query the [List engines API](https://beta.openai.com/docs/api-reference/engines/list) for available engines. See the following commands:

* Shell
    ```
    curl https://api.openai.com/v1/engines \
      -H 'Authorization: Bearer YOUR_API_KEY' \
      -H 'OpenAI-Organization: YOUR_ORG_ID'
    ```

* PowerShell

    PowerShell v5 (The default one comes with Windows)
    ```powershell
    (Invoke-WebRequest -Uri https://api.openai.com/v1/engines -Headers @{"Authorization" = "Bearer YOUR_API_KEY"; "OpenAI-Organization" = "YOUR_ORG_ID"}).Content
    ```

    PowerShell v7
    ```powershell
    (Invoke-WebRequest -Uri https://api.openai.com/v1/engines -Authentication Bearer -Token (ConvertTo-SecureString "YOUR_API_KEY" -AsPlainText -Force) -Headers @{"OpenAI-Organization" = "YOUR_ORG_ID"}).Content
    ```

### Can I run the sample on Azure?
The sample code can be currently be used with Codex on OpenAI’s API. In the coming months, the sample will be updated so you can also use it with the [Azure OpenAI Service](https://aka.ms/azure-openai). 
