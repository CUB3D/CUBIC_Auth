def get_app_base_url(app):
    return f"{app.config['SERVER_PROTOCOL']}://{app.config['SERVER_HOST']}:{app.config['SERVER_PORT']}/".rstrip(":80/")
