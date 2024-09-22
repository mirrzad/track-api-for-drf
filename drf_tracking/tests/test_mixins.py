from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from django.test import override_settings
from drf_tracking.models import ApiRequestLog
from drf_tracking.base_mixins import BaseLoggingMixin
from drf_tracking.tests.views import MockLoggingView
from django.contrib.auth.models import User
from unittest import mock
import ast
import datetime


@override_settings(ROOT_URLCONF='drf_tracking.tests.urls')
class TestLoggingMixins(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_nologging_no_log_created(self):
        self.client.get('/no-logging/')
        self.assertEqual(ApiRequestLog.objects.all().count(), 0)

    def test_logging_log_created(self):
        self.client.get('/logging/')
        self.assertEqual(ApiRequestLog.objects.all().count(), 1)

    def test_log_path(self):
        self.client.get('/logging/')
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.path, '/logging/')

    def test_log_ip_remote(self):
        request = APIRequestFactory().get('/logging/')
        request.META['REMOTE_ADDR'] = '127.0.0.6'
        MockLoggingView.as_view()(request)
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '127.0.0.6')

    def test_log_ip_remote_list(self):
        request = APIRequestFactory().get('/loging/')
        request.META['REMOTE_ADDR'] = '127.0.0.6, 127.0.0.100'
        MockLoggingView.as_view()(request)
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '127.0.0.6')

    def test_log_ip_v4_with_port(self):
        request = APIRequestFactory().get('/loging/')
        request.META['REMOTE_ADDR'] = '127.0.0.6:8080'
        MockLoggingView.as_view()(request)
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '127.0.0.6')

    def test_log_ip_v6(self):
        request = APIRequestFactory().get('/loging/')
        request.META['REMOTE_ADDR'] = '2001:08db:78b3:0000:00000:45ea:4774:0365'
        MockLoggingView.as_view()(request)
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '2001:08db:78b3:0000:00000:45ea:4774:0365')

    def test_log_ip_v6_loopback(self):
        request = APIRequestFactory().get('/loging/')
        request.META['REMOTE_ADDR'] = '::1'
        MockLoggingView.as_view()(request)
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '::1')

    def test_log_ip_v6_with_port(self):
        request = APIRequestFactory().get('/loging/')
        request.META['REMOTE_ADDR'] = '[::1]:1234'
        MockLoggingView.as_view()(request)
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '::1')

    def test_log_ip_x_forwarded(self):
        request = APIRequestFactory().get('/loging/')
        request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.6'
        MockLoggingView.as_view()(request)
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '127.0.0.6')

    def test_log_ip_x_forwarded_list(self):
        request = APIRequestFactory().get('/loging/')
        request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.6, 128.0.0.1'
        MockLoggingView.as_view()(request)
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '127.0.0.6')

    def test_log_host(self):
        self.client.get('/logging/')
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.host, 'testserver')

    def test_log_method(self):
        self.client.get('/logging/')
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.method, 'GET')

    def test_log_status_code(self):
        self.client.get('/logging/')
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.status_code, 200)

    def test_explicit_logging(self):
        self.client.get('/explicit_logging/')
        self.client.post('/explicit_logging/')
        self.assertEqual(ApiRequestLog.objects.all().count(), 1)

    def test_custom_check_logging(self):
        self.client.get('/custom_check_logging/')
        self.client.post('/custom_check_logging/')
        self.assertEqual(ApiRequestLog.objects.all().count(), 1)

    def test_anon_user(self):
        self.client.get('/logging/')
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.user, None)

    def test_log_auth_user(self):
        User.objects.create_user(username='test', password='123')
        user = User.objects.get(username='test')
        self.client.login(username='test', password='123')
        self.client.get('/session_auth_logging/')
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.user, user)

    def test_log_params(self):
        self.client.get('/logging/', {'p1': 'test', 'p2': '15'})
        log = ApiRequestLog.objects.first()
        self.assertEqual(ast.literal_eval(log.query_params), {'p1': 'test', 'p2': '15'})

    def test_log_params_cleaned(self):
        self.client.get('/sensitive_fields_logging/', {'api': 'test', 'name': 'test', 'my_field': '123456'})
        log = ApiRequestLog.objects.first()
        self.assertEqual(
            ast.literal_eval(log.query_params),
            {'api': BaseLoggingMixin.CLEAN_SUBSTITUTE,
             'name': 'test',
             'my_field': BaseLoggingMixin.CLEAN_SUBSTITUTE,
             }
        )

    def test_invalid_clean_substitute(self):
        with self.assertRaises(AssertionError):
            self.client.get('/invalid_clean_substitute_logging/')

    @mock.patch('drf_tracking.models.ApiRequestLog.save')
    def test_log_save_fails_not_prevent_api_call(self, mock_save):
        mock_save.side_effect = Exception('save failure')
        response = self.client.get('/logging/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ApiRequestLog.objects.all().count(), 0)

    @override_settings(USE_TZ=False)
    @mock.patch('drf_tracking.base_mixins.now')
    def test_log_no_fails_negative_response_ms(self, mock_now):
        mock_now.side_effect = [
            datetime.datetime(2023, 10, 10, 10, 0, 10),
            datetime.datetime(2023, 10, 10, 10, 0, 0),
        ]

        self.client.get('/logging/')
        log = ApiRequestLog.objects.first()
        self.assertEqual(log.response_ms, 0)


