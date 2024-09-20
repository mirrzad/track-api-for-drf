from django.db import models
from django.conf import settings


class BaseApiRequestLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    username_persistent = models.CharField(
        max_length=getattr(settings, 'DRF_TRACKING_USERNAME_LENGTH', 200),
        null=True,
        blank=True
    )
    requested_at = models.DateTimeField(db_index=True)
    response_ms = models.PositiveIntegerField(default=0)
    path = models.CharField(
        max_length=getattr(settings, 'DRF_TRACKING_PATH_LENGTH', 200),
        db_index=True,
        help_text='api url path'
    )
    view = models.CharField(
        max_length=getattr(settings, 'DRF_TRACKING_VIEW_LENGTH', 200),
        db_index=True,
        null=True,
        blank=True,
        help_text='view called by this endpoint'
    )
    view_method = models.CharField(
        max_length=getattr(settings, 'DRF_TRACKING_VIEW_METHOD_LENGTH', 200),
        db_index=True,
        null=True,
        blank=True
    )

    remote_addr = models.GenericIPAddressField()
    host = models.URLField()
    method = models.CharField(max_length=10)
    query_params = models.TextField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    errors = models.TextField(null=True, blank=True)
    status_code = models.PositiveIntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return '{} - {}'.format(self.method, self.path)





