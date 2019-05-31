"""Unit tests of the `base` module."""

import unittest

from unittest.mock import Mock, patch

import pytz
import tzlocal

from sportmonks_v2._base import BaseApiV2, SportMonksAPIError, BaseUrlMissingError, ApiKeyMissingError


class TestBaseApiV20(unittest.TestCase):
    """Class with unit tests of `BaseApiV2` methods."""

    def setUp(self):
        """Set up tests."""
        pass

    def test_init_raises_exceptions(self):
        """Test that `__init__` raises exceptions when base url or API key are missing."""
        self.assertRaises(BaseUrlMissingError, BaseApiV2, base_url=None, api_token='foo')
        self.assertRaises(ApiKeyMissingError, BaseApiV2, base_url='foo', api_token=None)

    def test_init_sets_timezone(self):
        """Test that `__init__` sets timezone."""
        api = BaseApiV2(base_url='http://www.foo.com', api_token='foo', tz_name='Europe/Amsterdam')
        self.assertEqual(pytz.timezone('Europe/Amsterdam'), api.timezone)

        api = BaseApiV2(base_url='http://www.foo.com', api_token='foo')
        self.assertEqual(tzlocal.get_localzone(), api.timezone)

    def test_init_sets_base_params(self):
        """Test that `__init__` sets base params."""
        api = BaseApiV2(base_url='foo', api_token='bar', tz_name='Australia/Sydney')
        self.assertEqual({'api_token': 'bar', 'tz': 'Australia/Sydney'}, api._base_params)

    @patch('requests.get', new=lambda: 'response')
    def test_http_get_raises_type_error(self):
        """Test that `_http_get` raises TypeError."""
        api = BaseApiV2(base_url='foo', api_token='bar')
        self.assertRaises(TypeError, BaseApiV2._http_get, api, endpoint='foo')

    @patch('sportmonks_v2._base.log', new=Mock())
    @patch('requests.get')
    def test_http_get_raises_sportmonks_api_error(self, mocked_get):
        """Test that `_http_get` raises SportMonksAPIError."""

        api = BaseApiV2(base_url='foo', api_token='bar')
        self.assertRaises(SportMonksAPIError, api._http_get, endpoint='foo')

    def test_unnested_simple(self):
        """Test `_unnest` with a simple case."""
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

        api = BaseApiV2(base_url='foo', api_token='bar')
        self.assertEqual(api._unnested(nested), expected)

    def test_unnested_complex(self):
        """Test `_unnest` with a complex case."""
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

        api = BaseApiV2(base_url='foo', api_token='bar')
        self.assertEqual(api._unnested(outer), expected)

    def test_unnested_super_complex(self):
        """Test `_unnest` with a super complex case."""
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
        api = BaseApiV2(base_url='foo', api_token='bar')
        self.assertEqual(api._unnested(outer), expected)
