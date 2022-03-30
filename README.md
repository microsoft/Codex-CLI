# NL-CLI - Natural Language Command Line Interface

Type in a natural language command, hit Ctrl+X and watch Codex turn it into scripting code.

With the added functionality for loading developing 'modes', it makes the experience of working in the terminal seamless.

Inspired by the [zsh_codex](https://github.com/tom-doerr/zsh_codex) project, it expands the functionality to multiple shells and adds the ability to load modes.

## Installation


Make sure you have python installed. Then install needed python packages.

```
pip3 install openai
pip3 install psutil
```

Follow the steps for which shell you are using. Generally, Mac OS has zsh, Linux has bash, Windows has powershell.

### Zsh instructions


1. Download this project to `~/your/custom/path/`.

```
    $ git clone https://github.com/microsoft/NL-CLI.git ~/your/custom/path/
```

2. Add the following to your `~/.zshrc` file.

```
    # in your/custom/path you need to clone the repository
    export ZSH_CUSTOM="your/custom/path"
    source "$ZSH_CUSTOM/NL-CLI/nl_cli.plugin.zsh"
    bindkey '^X' create_completion
```

3. Create a file called `openaiapirc` in `~/.config` with your SECRET_KEY.

```
[openai]
secret_key = ...
```

4. Run `zsh`, start typing and complete it using `^X`!


### Powershell instructions

1. Download this project to wherever you want `C:\your\custom\path\`.

```
    $ git clone https://github.com/microsoft/NL-CLI.git C:\your\custom\path\
```

2. Open PowerShell as Administrator and run the following command.

```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```


3. In the same Powershell window, go to `C:\your\custom\path\` (the folder contains NL-CLI code), then run the following command to setup your PowerShell environment.

```
.\powershell_setup.ps1
```

4. Open a new powershell session, type in `#` followed by your natural language command and hit Ctrl+X!

#### Clean up
Once you are done, go to `C:\your\custom\path\` (the folder contains NL-CLI code), then run the following command to clean up.
```
.\powershell_cleanup.ps1
```

If you want to revert the execution policy, run this command
```
Set-ExecutionPolicy Undefined -Scope CurrentUser
```

### Bash instructions


1. Download this project to `~/your/custom/path/`.

```
    $ git clone https://github.com/microsoft/NL-CLI.git ~/your/custom/path/
```

2. Add the following to your `~/.bashrc` file.

```
    # in your/custom/path you need to clone the repository
    export NL_CLI_PATH="your/custom/path/NL-CLI"
    source "$NL_CLI_PATH/nl_cli.plugin.sh"
    bind -x '"\C-x":"create_completion"'
```

3. Create a file called `openaiapirc` in `~/.config` with your SECRET_KEY.

```
[openai]
secret_key = ...
```

4. Run `bash`, start typing and complete it using `^X`!



## Context file format

This is what a typical context file looks like.

```
## engine: davinci-codex-msft
## temperature: 0.5
## max_tokens: 50
## shell: powershell
## token_count: 87

...Codex queries and output...
```

The lines starting with `##` are the configuration options and are ignored by Codex. The rest of the file is the actual context that is used by Codex to generate the script. The file is called `openai_completion_input.txt`.


## Usage

When an input is provided to the CLI, we first check if it is a command. If it is, we execute the command and exit. If it is not, we prefix the input with the shell name and context history and pass it to Codex (which is configured according to the configurations at the beginning of the context file). Codex then returns the script that should be executed. That script is printed to the CLI. In the background, we add the input-output to the context file and save it to allow multi-turn scenarios.

Feel free to use `edit context` to edit the context file via a text editor instead of the CLI.
## Commands

### Unlearning commands

- `unlearn`

Deletes the last exchange with Codex (last 2 lines for now).

- `unlearn all` or `clear context`

Starts the current thread/context with Codex afresh. Temporarily saves the current context to `deleted` directory.

### Context file commands

If `.txt` is not appended to the filename, it will be appended automatically.

- `show context <n>`

Shows what the context for your queries look like currently for last `n` lines. If no `n` is given, it shows the entire context.

- `edit context`

Opens up the context in a text editor. It helps you to 'prime' Codex to better respond for some queries.

- `save context <filename>`

Allows you to save your context if you want to load it in later, saves it to `saved` and if name is not specified, it will be saved with the current date-time as name.

- `load context <filename>`

Loads a previously saved context from the `saved` directory. 

### Configuration commands

If any configuration values are out of range, we revert to the defaults (see below).

- `show config`

Shows the current configuration with codex engine, temperature, max_tokens, shell and token_count for the current context.

- `set engine <engine>`

Sets the engine to use for the current context. The current default is `davinci-codex-msft`.

- `set temperature <temp>`

Sets the temperature for the current context. Specify between 0 and 1. The current default is 0.5.

- `set max_tokens <max_tokens>`

Sets the maximum number of tokens for the current context. Try to keep this under 100 tokens. The current default is 50.

- `set shell <shell>`

Sets the shell for the current context. There is no default here since we need the shell for the right outputs.

## Troubleshooting

Use `DEBUG_MODE` to use a terminal input instead of the stdin and debug the code. This is useful when adding new commands.

Sometimes `openai` will throws errors that aren't caught by the tool, you can add a catch block at the end of `codex_query.py` for that exception and print a custom error message.