""" This module contains unit tests for the `base` module. """

import unittest
from unittest.mock import Mock, patch
from sportmonks import __version__
import pytz
import tzlocal
import sportmonks.base as base


class TestBaseApiV20(unittest.TestCase):

    def setUp(self):

        class BaseApiV2WithoutAbstractMethods(base.BaseApiV2):
            """ A subclass of `base.BaseApiV20` with overridden abstract methods allowing instantiation. """
            @property
            def _callables_cached_objects(self):
                raise NotImplementedError()

        self.api_v20_base_class = BaseApiV2WithoutAbstractMethods

    def test_init_raises_exceptions(self):
        self.assertRaises(base.BaseUrlMissingError, self.api_v20_base_class, base_url=None, api_token='foo')
        self.assertRaises(base.ApiKeyMissingError, self.api_v20_base_class, base_url='foo', api_token=None)

    def test_init_sets_timezone_correctly(self):

        api = self.api_v20_base_class(base_url='http://www.foo.com', api_token='foo',tz_name='Europe/Amsterdam')
        self.assertEqual(pytz.timezone('Europe/Amsterdam'), api.timezone)

        api = self.api_v20_base_class(base_url='http://www.foo.com', api_token='foo')
        self.assertEqual(tzlocal.get_localzone(), api.timezone)

    def test_init_sets_base_params(self):
        api = self.api_v20_base_class(base_url='foo', api_token='bar', tz_name='Australia/Sydney')
        self.assertEqual({'api_token': 'bar', 'tz': 'Australia/Sydney'}, api.base_params)

    @patch('requests.get')
    def test_http_get_args_building(self, mocked_get):
        api = self.api_v20_base_class(base_url='bar', api_token='foo', tz_name='UTC')

        mocked_response = Mock()
        mocked_response.json.return_value = {'response': 'foo'}
        mocked_get.return_value = mocked_response

        response = api._http_get(endpoint='some_endpoint', params={'param': [1, 2]}, includes=['foo', 'bar'])
        self.assertEqual({'response': 'foo'}, response)
        mocked_get.assert_called_once_with(
            url='bar/some_endpoint',
            params={'api_token': 'foo', 'tz': 'UTC', 'param': '1,2', 'include': 'foo,bar', 'page': 1},
            headers={
                'Accept-Encoding': 'gzip, deflate',
                'User-Agent': 'https://github.com/Dmitrii-I/sportmonks {version}'.format(version=__version__)
            }
        )
        self.assertEqual(1, api.http_requests_made)

    @patch('requests.get', new=lambda: 'response')
    def test_http_get_raises_type_error(self):
        api = self.api_v20_base_class(base_url='foo', api_token='bar')
        self.assertRaises(TypeError, base.BaseApiV2._http_get, api, endpoint='foo')

    @patch('sportmonks.base.log', new=Mock())
    @patch('requests.get')
    def test_http_get_raises_sportmonks_api_error(self, mocked_get):
        mocked_response = Mock()
        mocked_response.json.return_value = {'error': {'message': 'foo'}}
        mocked_get.return_value = mocked_response

        api = self.api_v20_base_class(base_url='foo', api_token='bar')
        self.assertRaises(base.SportMonksAPIError, api._http_get, endpoint='foo')

    @patch('requests.get')
    def test_http_get_unnests_data(self, mocked_get):
        mocked_response = Mock()
        mocked_response.json.return_value = {'data': {'foo': 'bar'}}
        mocked_get.return_value = mocked_response

        api = self.api_v20_base_class(base_url='foo', api_token='bar')
        self.assertEqual({'foo': 'bar'}, api._http_get(endpoint='foo'))

    @patch('requests.get')
    def test_http_get_requests_all_pages(self, mocked_requests_get):

        def mocked_response(url, params, headers):
            response = Mock()
            response.request = Mock()
            response.json.return_value = {
                'data': [{'foo': 'page_' + str(params['page'])}],
                'meta': {'pagination': {'current_page': params['page'], 'total_pages': 3}}
            }

            return response

        mocked_requests_get.side_effect = mocked_response

        api = self.api_v20_base_class(base_url='gg', api_token='foo')
        combined_response = api._http_get(endpoint='foo')
        self.assertEqual([{'foo': 'page_1'}, {'foo': 'page_2'}, {'foo': 'page_3'}], combined_response)

    def test_unnested_simple(self):

        nested = {
            'a': 1,
            'b': [1, 2, 3],
            'c': 'foo',
            'd': {'data': [1, 2, 3]}
        }

        expected = {
            'a': 1,
            'b': [1, 2, 3],
            'c': 'foo',
            'd': [1, 2, 3]
        }

        api = self.api_v20_base_class(base_url='foo', api_token='bar')
        self.assertEqual(api._unnested(nested), expected)

    def test_unnested_complex(self):

        inner = {
            'p': 1,
            'q': [1, 2, 3],
            'r': 'foo',
            's': {'data': {'x': 1, 'z': 'foo'}}
        }

        outer = {
            'a': 1,
            'b': [1, 2, 3],
            'c': 'foo',
            'd': {'data': inner}
        }

        expected = {
            'a': 1,
            'b': [1, 2, 3],
            'c': 'foo',
            'd': {
                'p': 1,
                'q': [1, 2, 3],
                'r': 'foo',
                's': {'x': 1, 'z': 'foo'}
            }
        }

        api = self.api_v20_base_class(base_url='foo', api_token='bar')
        self.assertEqual(api._unnested(outer), expected)

    def test_unnested_super_complex(self):

        inner_inner = [
            {'a': 1, 'b': {'data': {'c': 'foo'}}},
            {'a': 2, 'b': {'data': {'c': 'bar'}}},
            {'a': 3, 'b': {'data': {'c': 'foobar'}}}
        ]

        inner = {
            'p': 1,
            'q': [1, 2, 3],
            'r': 'foo',
            's': {'data': {'x': 1, 'z': 'foo', 'y': {'data': inner_inner}}}
        }

        outer = {
            'a': 1,
            'b': [1, 2, 3],
            'c': 'foo',
            'd': {'data': inner}
        }

        expected = {
            'a': 1,
            'b': [1, 2, 3],
            'c': 'foo',
            'd': {
                'p': 1,
                'q': [1, 2, 3],
                'r': 'foo',
                's': {
                    'x': 1,
                    'z': 'foo',
                    'y': [{'a': 1, 'b': {'c': 'foo'}}, {'a': 2, 'b': {'c': 'bar'}}, {'a': 3, 'b': {'c': 'foobar'}}]
                }
            }
        }
        api = self.api_v20_base_class(base_url='foo', api_token='bar')
        self.assertEqual(api._unnested(outer), expected)
