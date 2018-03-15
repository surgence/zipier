import json

from django.test import TestCase
from unittest import mock

from action.utils import (
    build_dict,
    handle_response,
    logger,
    search_dict)


class BuildDictTest(TestCase):

    def test_build_dict_no_list(self):
        items = 'test'
        result = build_dict(items)
        self.assertIsNone(result)

        items = {}
        result = build_dict(items)
        self.assertIsNone(result)

    def test_build_dict_unexpected_list(self):
        items = ['test1', 'test2']
        expected_result = {
            'test1': 'test1',
            'test2': 'test2'
        }
        result = build_dict(items)

        self.assertEquals(result, expected_result)

    def test_build_dict(self):
        items = [{
            'key': 'key1',
            'value': 'value1'
        }, {
            'key': 'key2',
            'value': 'value2'
        }]
        expected_result = {
            'key1': 'value1',
            'key2': 'value2'
        }
        result = build_dict(items)

        self.assertEquals(result, expected_result)


class SearchDictTest(TestCase):

    def test_search_dict_flat(self):
        search_key = 'test_key'
        payload = {
            'test_key': 'this is the value',
            'key_test': 'no',
            'foo': 'never',
            'bar': 'negative'
        }
        result = search_dict(search_key, payload)
        self.assertEqual(list(result)[0], (search_key, 'this is the value'))

    def test_search_dict_found_nothing(self):
        search_key = 'test_key'
        payload = {
            'testKey': 'there is nothing to find',
            'key_test': 'no',
            'foo': 'never',
            'bar': 'negative'
        }
        result = search_dict(search_key, payload)
        self.assertEqual(list(result), [])

    def test_search_dict_send_nothing(self):
        search_key = 'test_key'
        payload = 'test_string'
        result = search_dict(search_key, payload)
        self.assertEqual(list(result), [])

    def test_search_dict_flat_list_key(self):
        search_key = ['test_key', 'testKey']
        payload = {
            'testKey': 'this is the value',
            'key_test': 'no',
            'foo': 'never',
            'bar': 'negative'
        }
        result = search_dict(search_key, payload)
        self.assertEqual(list(result)[0], ('testKey', 'this is the value'))

    def test_search_dict_nested(self):
        search_key = 'test_key'
        payload = {
            'testKey': 'nope',
            'key_test': 'no',
            'foo': 'never',
            'bar': {
                'test_key': 'this is the value',
            }
        }
        result = search_dict(search_key, payload)
        self.assertEqual(list(result)[0], ('test_key', 'this is the value'))

    def test_search_dict_nested_list_key(self):
        search_key = ['test_key', 'keyTest']
        payload = {
            'testKey': 'nope',
            'key_test': 'no',
            'foo': 'never',
            'bar': {
                'test_key': 'this is the value',
            }
        }
        result = search_dict(search_key, payload)
        self.assertEqual(list(result)[0], ('test_key', 'this is the value'))

    def test_search_dict_nested_key_in_list(self):
        search_key = 'test_key'
        payload = {
            'testKey': 'nope',
            'key_test': 'no',
            'foo': 'never',
            'bar': {
                'keyTest': [
                    {'test_key': 'this is the value'},
                    {'other value': 'something else'}
                ]
            }
        }
        result = search_dict(search_key, payload)
        self.assertEqual(list(result)[0], ('test_key', 'this is the value'))

    def test_search_dict_single_input_key_nested_key_part_of_parent(self):
        search_key = 'first_option'
        payload = {
            'first_option': 'This is the one I want',
            'key_test': 'no',
            'foo': 'never',
            'bar': {
                'keyTest': [
                    {'first': 'I do not want this'},
                    {'other value': 'something else'}
                ]
            }
        }
        result = search_dict(search_key, payload)
        result = list(result)
        self.assertEqual(
            result[0], ('first_option', 'This is the one I want'))
        self.assertEqual(len(result), 1)


class HandleResponseTest(TestCase):
    def test_handle_response_no_json(self):
        response = mock.MagicMock()
        response.json = mock.MagicMock()
        response.json.side_effect = ValueError(mock.Mock(), 'error')
        response.status_code = 200

        with mock.patch.object(logger, 'error') as test_logger:
            result = handle_response(response)

        test_logger.assert_called_with(response.json.side_effect,
                                       extra=response)
        self.assertEquals(result, response.content)

    def test_handle_response_bad_response(self):
        expected_result = json.dumps({'key1': 'value1'})
        response = mock.MagicMock()
        response.json.return_value = expected_result
        response.content = 'this is a sample response'
        response.status_code = 401

        with self.assertRaises(Exception) as context:
            handle_response(response)

        self.assertTrue('this is a sample response' in context.exception.args)

    def test_handle_response(self):
        expected_result = json.dumps({'key1': 'value1'})
        response = mock.MagicMock()
        response.json.return_value = expected_result
        response.status_code = 200

        result = handle_response(response)

        self.assertEquals(result, response.json())
