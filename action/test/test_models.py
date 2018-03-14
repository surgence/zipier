import json
import requests

from dicttoxml import dicttoxml
from django.test import TestCase
from model_mommy import mommy
from unittest import mock

from action.models import ActionWebhook
import action.utils

class ActionWebhookTest(TestCase):

    def test_str(self):
        webhook = mommy.make('action.ActionWebhook', title='webhook title')
        self.assertEqual(str(webhook), u'webhook title')

    def test_get_schema_base(self):
        webhook = mommy.make('action.ActionWebhook')
        webhook.BASE_SCHEMA = {'test': 'schema'}

        schema = webhook.get_schema(None)

        self.assertEqual(schema, webhook.BASE_SCHEMA)

    def test_get_schema_get(self):
        webhook = mommy.make('action.ActionWebhook')

        schema = webhook.get_schema(webhook.HOOK_GET)

        self.assertEqual(schema['title'], 'Webhook GET')
        self.assertEqual(schema['description'],
                         'Set up Webhooks by Zipier GET')
        self.assertIsNone(schema.get('payloadType'))
        self.assertEqual(schema['properties']['data']['title'],
                         'Query String Params')
        # I know, I'm being lazy here but time == money
        self.assertTrue('URL-encoded' in (
            schema['properties']['data']['description']))

    def test_get_schema_get_skip_inside_ifs_lazy(self):
        webhook = mommy.make('action.ActionWebhook')
        webhook.BASE_SCHEMA = {
            'title': 'schema',
            'description': 'foobar',
            'properties': {}
        }

        schema = webhook.get_schema(webhook.HOOK_GET)

        self.assertEqual(schema['title'], 'Webhook GET')
        self.assertEqual(schema['description'],
                         'Set up Webhooks by Zipier GET')

    def test_get_schema_post(self):
        webhook = mommy.make('action.ActionWebhook')

        schema = webhook.get_schema(webhook.HOOK_POST)

        self.assertEqual(schema['title'], 'Webhook POST')
        self.assertEqual(schema['description'],
                         'Set up Webhooks by Zipier POST')

    def test_get_schema_put(self):
        webhook = mommy.make('action.ActionWebhook')

        schema = webhook.get_schema(webhook.HOOK_PUT)

        self.assertEqual(schema['title'], 'Webhook PUT')
        self.assertEqual(schema['description'],
                         'Set up Webhooks by Zipier PUT')

    def test_make_it_so_nope(self):
        webhook = mommy.make('action.ActionWebhook', hook_type='Nothing')
        result = webhook.make_it_so()
        self.assertEqual(result, 'Nope')

    @mock.patch.object(ActionWebhook, 'run_get')
    def test_make_it_so_get(self, run_get):
        webhook = mommy.make('action.ActionWebhook', hook_type='get')

        return_get = mock.MagicMock()
        run_get.return_value = return_get

        result = webhook.make_it_so()

        run_get.assert_called_once_with()
        self.assertEqual(return_get, result)

    @mock.patch.object(ActionWebhook, 'run_post')
    def test_make_it_so_post(self, run_post):
        webhook = mommy.make('action.ActionWebhook', hook_type='post')

        return_post = mock.MagicMock()
        run_post.return_value = return_post

        result = webhook.make_it_so()

        run_post.assert_called_once_with()
        self.assertEqual(return_post, result)

    @mock.patch.object(ActionWebhook, 'run_put')
    def test_make_it_so_put(self, run_put):
        webhook = mommy.make('action.ActionWebhook', hook_type='put')

        return_put = mock.MagicMock()
        run_put.return_value = return_put

        result = webhook.make_it_so()

        run_put.assert_called_once_with()
        self.assertEqual(return_put, result)

    # How do you like to test?
    # I can mock everything out.
    @mock.patch.object(ActionWebhook, 'get_headers')
    @mock.patch.object(ActionWebhook, 'get_data')
    @mock.patch.object(requests, 'post')
    @mock.patch('action.utils.handle_response')
    def test_run_post(self, handle_response, post, get_data, get_headers):
        data = {'url': 'url'}
        webhook = mommy.make('action.ActionWebhook', hook_type='post',
                             data=data)

        get_headers.return_value = {}
        get_data.return_value = {}
        post.return_value = 'request_response'
        handle_response.return_value = 'handled_response'

        result = webhook.run_post()

        get_headers.assert_called_once_with(
            {'Content-Type': 'multipart/form-data'})
        get_data.assert_called_once_with()
        post.assert_called_once_with('url', data={}, headers={}, timeout=30)
        handle_response.assert_called_once_with('request_response')

        self.assertEqual(result, handle_response.return_value)

    @mock.patch.object(ActionWebhook, 'get_headers')
    @mock.patch.object(ActionWebhook, 'get_data')
    @mock.patch.object(requests, 'post')
    @mock.patch('action.utils.handle_response')
    def test_run_post_json(self, handle_response, post, get_data, get_headers):
        data = {
            'url': 'url',
            'payloadType': 'json'
        }
        webhook = mommy.make('action.ActionWebhook', hook_type='post',
                             data=data)

        result = webhook.run_post()

        get_headers.assert_called_once_with(
            {'Content-Type': 'application/json'})

    @mock.patch.object(ActionWebhook, 'get_headers')
    @mock.patch.object(ActionWebhook, 'get_data')
    @mock.patch.object(requests, 'post')
    @mock.patch('action.utils.handle_response')
    def test_run_post_xml(self, handle_response, post, get_data, get_headers):
        data = {
            'url': 'url',
            'payloadType': 'xml'
        }
        webhook = mommy.make('action.ActionWebhook', hook_type='post',
                             data=data)

        result = webhook.run_post()

        get_headers.assert_called_once_with(
            {'Content-Type': 'application/xml'})

    # Or let just important things run through (get_data)
    @mock.patch.object(ActionWebhook, 'get_headers')
    @mock.patch.object(requests, 'get')
    @mock.patch('action.utils.handle_response')
    def test_run_get(self, handle_response, get, get_headers):
        data = {
            'url': 'url',
            'payloadType': 'xml',
            'data': [{
                'key': 'key1',
                'value': 'value1'
            }, {
                'key': 'key2',
                'value': 'value2'
            }]
        }

        webhook = mommy.make('action.ActionWebhook', hook_type='get',
                             data=data)

        get_headers.return_value = {}
        get.return_value = 'request_response'
        handle_response.return_value = 'handled_response'

        result = webhook.run_get()

        get_headers.assert_called_once_with()
        get.assert_called_once_with('url?key1=value1&key2=value2', headers={},
                                    timeout=30)
        handle_response.assert_called_once_with('request_response')

        self.assertEqual(result, handle_response.return_value)

    @mock.patch.object(ActionWebhook, 'get_headers')
    @mock.patch.object(ActionWebhook, 'get_data')
    @mock.patch.object(requests, 'put')
    @mock.patch('action.utils.handle_response')
    def test_run_put(self, handle_response, put, get_data, get_headers):
        data = {'url': 'url'}
        webhook = mommy.make('action.ActionWebhook', hook_type='put',
                             data=data)

        get_headers.return_value = {}
        get_data.return_value = {}
        put.return_value = 'request_response'
        handle_response.return_value = 'handled_response'

        result = webhook.run_put()

        get_headers.assert_called_once_with(
            {'Content-Type': 'multipart/form-data'})
        get_data.assert_called_once_with()
        put.assert_called_once_with('url', data={}, headers={}, timeout=30)
        handle_response.assert_called_once_with('request_response')

        self.assertEqual(result, handle_response.return_value)

    @mock.patch.object(ActionWebhook, 'get_headers')
    @mock.patch.object(ActionWebhook, 'get_data')
    @mock.patch.object(requests, 'put')
    @mock.patch('action.utils.handle_response')
    def test_run_put_json(self, handle_response, put, get_data, get_headers):
        data = {
            'url': 'url',
            'payloadType': 'json'
        }
        webhook = mommy.make('action.ActionWebhook', hook_type='put',
                             data=data)

        result = webhook.run_put()

        get_headers.assert_called_once_with(
            {'Content-Type': 'application/json'})

    @mock.patch.object(ActionWebhook, 'get_headers')
    @mock.patch.object(ActionWebhook, 'get_data')
    @mock.patch.object(requests, 'put')
    @mock.patch('action.utils.handle_response')
    def test_run_put_xml(self, handle_response, put, get_data, get_headers):
        data = {
            'url': 'url',
            'payloadType': 'xml'
        }
        webhook = mommy.make('action.ActionWebhook', hook_type='put',
                             data=data)

        result = webhook.run_put()

        get_headers.assert_called_once_with(
            {'Content-Type': 'application/xml'})

    @mock.patch('action.utils.build_dict')
    def test_get_data_no_data(self, build_dict):
        data = {}

        webhook = mommy.make('action.ActionWebhook', data=data)

        build_dict.return_value = None

        result = webhook.get_data()

        self.assertIsNone(result)

    @mock.patch('action.utils.build_dict')
    def test_get_data_empty_list(self, build_dict):
        data = {}
        webhook = mommy.make('action.ActionWebhook', data=data)

        build_dict.return_value = []

        result = webhook.get_data()

        self.assertIsNone(result)

    def test_get_data_get(self):
        data = {
            'data': [{
                'key': 'key1',
                'value': 'value1'
            }, {
                'key': 'key2',
                'value': 'value2'
            }]
        }
        expected_result = '?key1=value1&key2=value2'
        webhook = mommy.make('action.ActionWebhook', data=data,
                             hook_type='get')

        result = webhook.get_data()

        self.assertEqual(result, expected_result)

    @mock.patch('action.utils.build_dict')
    def test_get_data_json(self, build_dict):
        data = {
            'payloadType': 'json',
            'data': [{
                'key': 'key1',
                'value': 'value1'
            }, {
                'key': 'key2',
                'value': 'value2'
            }]
        }
        expected_result = {
            'key1': 'value1',
            'key2': 'value2'
        }
        webhook = mommy.make('action.ActionWebhook', data=data,
                             hook_type='post')

        build_dict.return_value = expected_result
        result = webhook.get_data()

        self.assertEqual(result, json.dumps(expected_result))

    @mock.patch('action.utils.build_dict')
    def test_get_data_xml(self, build_dict):
        data = {
            'payloadType': 'xml',
            'data': [{
                'key': 'key1',
                'value': 'value1'
            }, {
                'key': 'key2',
                'value': 'value2'
            }]
        }
        expected_result = {
            'key1': 'value1',
            'key2': 'value2'
        }
        webhook = mommy.make('action.ActionWebhook', data=data,
                             hook_type='post')

        build_dict.return_value = expected_result
        result = webhook.get_data()

        self.assertEqual(result, dicttoxml(expected_result))

    @mock.patch('action.utils.build_dict')
    def test_get_data(self, build_dict):
        data = {
            'data': [{
                'key': 'key1',
                'value': 'value1'
            }, {
                'key': 'key2',
                'value': 'value2'
            }]
        }
        expected_result = {
            'key1': 'value1',
            'key2': 'value2'
        }
        webhook = mommy.make('action.ActionWebhook', data=data,
                             hook_type='post')

        build_dict.return_value = expected_result
        result = webhook.get_data()

        self.assertEqual(result, expected_result)

    def test_get_headers_empty(self):
        data = {}
        webhook = mommy.make('action.ActionWebhook', data=data)

        result = webhook.get_headers()

        self.assertEquals(result, {})

    def test_get_headers_results_no_header(self):
        data = {'headers': []}
        webhook = mommy.make('action.ActionWebhook', data=data)

        result = webhook.get_headers({})

        self.assertEquals(result, {})

    @mock.patch('action.utils.build_dict')
    def test_get_headers_results(self, build_dict):
        data = {'headers': [{
            'key': 'key1',
            'value': 'value1'
        }, {
            'key': 'key2',
            'value': 'value2'
        }]}
        expected_result = {
            'key1': 'value1',
            'key2': 'value2'
        }
        webhook = mommy.make('action.ActionWebhook', data=data)
        build_dict.return_value = expected_result

        result = webhook.get_headers()

        build_dict.assert_called_once_with(data.get('headers'))

        self.assertEquals(result, expected_result)
