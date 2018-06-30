""" This module contains unit tests for the `base` module. """

import unittest
from unittest.mock import Mock, patch
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

        response = api._http_get(endpoint='some_endpoint', params={'param': [1, 2]}, includes=('foo', 'bar'))
        self.assertEqual({'response': 'foo'}, response)
        mocked_get.assert_called_once_with(
            url='bar/some_endpoint',
            params={'api_token': 'foo', 'tz': 'UTC', 'param': '1,2', 'include': 'foo,bar'},
            headers={'Accept-Encoding': 'gzip, deflate'}
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
                'data': [{'page': 1}],
                'meta': {'pagination': {'links': {'next': 'http://foo.bar?page=2'}}}
            }

            if 'page' in params:
                response_pages = {
                    '2': {
                        'data': [{'page': 2}],
                        'meta': {'pagination': {'links': {'next': 'http://foo.bar?page=3'}}}
                    },

                    '3': {'data': [{'page': 3}]}
                }

                response.json.return_value = response_pages[params['page']]

            return response

        mocked_requests_get.side_effect = mocked_response

        api = self.api_v20_base_class(base_url='gg', api_token='foo')
        combined_response = api._http_get(endpoint='foo')
        self.assertEqual([{'page': 1}, {'page': 2}, {'page': 3}], combined_response)

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

    def test_lookup_table(self):

        class ApiV2(base.BaseApiV2):

            @property
            def _callables_cached_objects(self):
                return {
                    'foo': lambda **kwargs: [{'id': ','.join(sorted([kwargs[k] for k in kwargs]))}],
                    'bar': lambda **kwargs:  [{'id': '-'.join(sorted([kwargs[k] for k in kwargs]))}]
                }

        api = ApiV2(base_url='http://foo', api_token='bar')
        expected_foo = {'a,b,c': {'id': 'a,b,c'}}
        expected_bar = {'a-b-c': {'id': 'a-b-c'}}

        self.assertEqual(expected_foo, api._lookup_table(sportmonks_object='foo', a='a', c='c', b='b'))
        self.assertEqual(expected_bar, api._lookup_table(sportmonks_object='bar', a='a', c='c', b='b'))

        self.assertRaises(base.UnknownSportMonksObject, api._lookup_table, 'foobar')
