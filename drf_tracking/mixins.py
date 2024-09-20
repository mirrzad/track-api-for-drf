from .base_mixins import BaseLoggingMixin
from .models import ApiRequestLog


class LoggingMixin(BaseLoggingMixin):
    def handle_log(self):
        ApiRequestLog(**self.log).save()
