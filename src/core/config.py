import os


def get_config(app, key, default=None):
    return os.environ[key] or app.config[key] or default


def get_app_base_url(app):
    return f"{get_config(app, 'SERVER_PROTOCOL')}://{get_config(app, 'SERVER_HOST')}:{get_config(app, 'SERVER_PORT')}/".rstrip(":80/")
