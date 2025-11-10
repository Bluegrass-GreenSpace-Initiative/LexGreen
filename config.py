# config.py (centralized config only; no Flask app side-effects)

class Config:
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # Map defaults (UK campus)
    DEFAULT_LAT = 38.0406
    DEFAULT_LNG = -84.5037
    DEFAULT_ZOOM = 15


class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    DEBUG = False
