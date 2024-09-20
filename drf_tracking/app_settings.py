class AppSettings:
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, default):
        from django.conf import settings
        return getattr(settings, self.prefix + name, default)

    @property
    def path_length(self):
        return self._setting('PATH_LENGTH', 200)

    @property
    def decode_request_body(self):
        return self._setting('DECODE_REQUEST_BODY', True)


app_settings = AppSettings('DRF_TRACKING_')
