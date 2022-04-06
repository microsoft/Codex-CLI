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

2. In zsh, go to `~/your/custom/path/` (the folder contains NL-CLI code), then run the following command to setup your zsh environment. It will prompt you for OpenAI access key.

```
./zsh_setup.sh
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;See [About zsh_setup.sh](#about-zshsetupsh) section to learn script parameters.

3. Run `zsh`, start typing and complete it using `^X`!

#### Clean up
Once you are done, go to `~/your/custom/path/` (the folder contains NL-CLI code), then run the following command to clean up.
```
./zsh_cleanup.sh
```

#### About zsh_setup.sh
`zsh_setup.sh` supports the following parameters:
| Parameter | Description | Example |
|--|--|--|
| `--RepoRoot` | Optional. Default to the current folder.<br>The value should be the path of NL-CLI folder | `./zsh_setup.sh --RepoRoot /Code/NL-CLI`|

### Powershell instructions

1. Download this project to wherever you want `C:\your\custom\path\`.

```
    $ git clone https://github.com/microsoft/NL-CLI.git C:\your\custom\path\
```

2. Open PowerShell as Administrator and run the following command.

```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```


3. In the same Powershell window, go to `C:\your\custom\path\` (the folder contains NL-CLI code), then run the following command to setup your PowerShell environment. It will prompt you for OpenAI access key.

```
.\powershell_setup.ps1
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;See [About powershell_setup.ps1](#about-powershellsetupps1) section to learn script parameters.

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

#### About powershell_setup.ps1
`powershell_setup.ps1` supports the following parameters:
| Parameter | Type | Description | Example |
|--|--|--|--|
| `-RepoRoot` | [FileInfo](https://docs.microsoft.com/en-us/dotnet/api/system.io.fileinfo) | Optional. Default to the current folder.<br>The value should be the path of NL-CLI folder|`.\powershell_setup.ps1 -RepoRoot 'C:\your\custom\path'`|
| `-OpenAIApiKey` | [SecureString](https://docs.microsoft.com/en-us/dotnet/api/system.security.securestring) | Required. If is not supplied, the script will prompt you to input the value. If you would like to provide the value via PowerShell parameter, please refer to the example. | `.\powershell_setup.ps1 -OpenAIApiKey (ConvertTo-SecureString "YOUR_OPENAI_API_KEY" -AsPlainText -Force)` |

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


## Usage

When an input is provided to the CLI, we first check if it is a command. 

If it is, we execute the command and exit. 

If it is not a command, we prefix the input with the shell name, the interactions in `openai_completion_input.txt` and pass it to Codex (which uses the context config). 

Depending on whether context mode is on or off and the interaction was successful, we add the interaction to the current context file, letting you build off on interactions.

## Commands

| Command | Description |
|--|--|
| `start context` | Starts a multi-turn experience |
| `stop context` | Stops a multi-turn experience and loads default context |
| `load context <filename>` | Loads the context file from `contexts` folder |
| `default context` | Loads default shell context |
| `edit context` | Opens the context file in a text editor |
| `save context <filename>` | Saves the context file to `contexts` folder, if name not specified, uses current date-time |
| `show config` | Shows the current configuration of your interaction with the model |
| `set <config-key> <config-value>` | Sets the configuration of your interaction with the model |
| `unlearn` | Unlearns the last two lines of input-output from the model |

## Troubleshooting

Use `DEBUG_MODE` to use a terminal input instead of the stdin and debug the code. This is useful when adding new commands and understanding why the tool is unresponsive.

Sometimes `openai` will throws errors that aren't caught by the tool, you can add a catch block at the end of `codex_query.py` for that exception and print a custom error message.