# NL-CLI - Natural Language Command Line Interface

Type in a natural language command, hit Ctrl+X and watch Codex turn it into scripting code.

With the added functionality for loading developing 'modes', it makes the experience of working in the terminal seamless.

## Installation

MacOS users can go for the zsh instructions, Linux for bash instructions and Windows users for powershell instructions.

First install needed python packages.
```
pip3 install openai
pip3 install psutil
```

### Zsh instructions


1. Download the ZSH plugin.

```
    $ git clone https://github.com/tom-doerr/zsh_codex.git ~/.oh-my-zsh/custom/plugins/ 
```

2. Add the following to your `~/.zshrc` file.

Using oh-my-zsh:
```
    plugins=(zsh_codex)
    bindkey '^X' create_completion
```
Without oh-my-zsh:
```
    # in your/custom/path you need to have a "plugins" folder and in there you clone the repository as zsh_codex
    export ZSH_CUSTOM="your/custom/path"
    source "$ZSH_CUSTOM/plugins/zsh_codex/zsh_codex.plugin.zsh"
    bindkey '^X' create_completion
```

3. Create a file called `openaiapirc` in `~/.config` with your ORGANIZATION_ID and SECRET_KEY.

```
[openai]
organization_id = ...
secret_key = ...
```

4. Run `zsh`, start typing and complete it using `^X`!


### Powershell instructions

TBD


### Bash instructions

TBD

## Commands

- `unlearn`
Deletes the last exchange with Codex

- `unlearn all` or `clear context`
Starts the current thread/context with Codex afresh

- `show context`
Shows what the context for your queries look like currently

- `edit context`
Allows you to go back and edit the context to 'prime' Codex to better respond for some queries

- `save context`
Allows you to save your context if you want to load it in later

## Troubleshooting

TBD