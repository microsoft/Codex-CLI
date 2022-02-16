# NL-CLI - Natural Language Command Line Interface

Type in a natural language command, hit Ctrl+X and watch Codex turn it into scripting code.

With the added functionality for loading developing 'modes', it makes the experience of working in the terminal seamless.

## Installation

MacOS and Linux users can go for the zsh instructions and Windows users for powershell instructions.

0. Install needed python packages.
```
pip3 install openai
pip3 install psutil
```

### Zsh instructions

Bash doesn't have native support for plugins. Zsh is a shell that extends bash with a lot more functionality one of which is plugin support. 

Most macOS versions ship zsh natively. Run `zsh --version` to confirm. In case you don't use zsh, consider [these installation instructions](https://github.com/ohmyzsh/ohmyzsh/wiki/Installing-ZSH).


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


## Troubleshooting

