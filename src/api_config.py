"""Resolve explicit model settings before provider defaults."""


MINIMAX_BASE_URLS = ('https://api.minimax.io/v1', 'https://api.minimaxi.com/v1')

def get_setting(settings, key, fallback=''):
    value = settings.get(key, fallback)
    return value.strip().strip('"').strip("'")


def get_model(settings):
    model = get_setting(settings, 'model') or get_setting(settings, 'engine')
    if model:
        return model
    if get_setting(settings, 'base_url').rstrip('/') in MINIMAX_BASE_URLS:
        return 'MiniMax-M3.1-Flash'
    return ''


def get_default_max_tokens(settings, fallback):
    # The generation budget includes thinking as well as the final command.
    if (get_setting(settings, 'base_url').rstrip('/') in MINIMAX_BASE_URLS and
            get_model(settings) in ('MiniMax-M3.1-Flash', 'MiniMax-M3')):
        return 32768
    return fallback
