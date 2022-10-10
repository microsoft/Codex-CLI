function create_completion
    set text (commandline -b)
    set completion (bash -c "echo -n '$text' | '$CODEX_CLI_PATH/src/codex_query.py'")
    commandline -a $completion
    # note: add move cursor to end
end
bind \cg 'create_completion'
# run the bash setup, then source this file or add it to fish config