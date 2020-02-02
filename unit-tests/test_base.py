"""Unit tests of the `base` module."""

import unittest

from unittest.mock import Mock, patch

import pytz
import tzlocal

from sportmonks import __version__
from sportmonks._base import BaseApiV2, SportMonksAPIError, BaseUrlMissingError, ApiKeyMissingError


class TestBaseApiV20(unittest.TestCase):
    """Class with unit tests of `BaseApiV2` methods."""

    def setUp(self):
        """Set up tests."""
        pass

    def test_init_raises_exceptions(self):
        """Test that `__init__` raises excepions when base url or API key are missing."""
        self.assertRaises(BaseUrlMissingError, BaseApiV2, base_url=None, api_token="foo")
        self.assertRaises(ApiKeyMissingError, BaseApiV2, base_url="foo", api_token=None)

    def test_init_sets_timezone(self):
        """Test that `__init__` sets timezone."""
        api = BaseApiV2(base_url="http://www.foo.com", api_token="foo", tz_name="Europe/Amsterdam")
        self.assertEqual(pytz.timezone("Europe/Amsterdam"), api.timezone)

        api = BaseApiV2(base_url="http://www.foo.com", api_token="foo")
        self.assertEqual(tzlocal.get_localzone(), api.timezone)

    def test_init_sets_base_params(self):
        """Test that `__init__` sets base params."""
        api = BaseApiV2(base_url="foo", api_token="bar", tz_name="Australia/Sydney")
        self.assertEqual({"api_token": "bar", "tz": "Australia/Sydney"}, api._base_params)

    @patch("requests.get")
    def test_http_get_args_building(self, mocked_get):
        """Test that `_http_get` builds the arguments."""
        api = BaseApiV2(base_url="bar", api_token="foo", tz_name="UTC")

        mocked_response = Mock()
        mocked_response.json.return_value = {"response": "foo"}
        mocked_get.return_value = mocked_response

        response = api._http_get(endpoint="some_endpoint", params={"param": [1, 2]}, includes=["foo", "bar"])
        self.assertEqual({"response": "foo"}, response)
        mocked_get.assert_called_once_with(
            url="bar/some_endpoint",
            params={"api_token": "foo", "tz": "UTC", "param": "1,2", "include": "bar,foo", "page": 1},
            headers={
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": "https://github.com/Dmitrii-I/sportmonks {version}".format(version=__version__),
            },
        )
        self.assertEqual(1, api.http_requests_made)

    @patch("requests.get")
    def test_http_get_works_wtih_includes_being_any_iterable(self, mocked_get):
        """Test that `_http_get` works with `includes` parameters being any iterable."""
        api = BaseApiV2(base_url="bar", api_token="foo", tz_name="UTC")

        includes_iterables = [("foo", "bar"), {"foo", "bar"}, ["foo", "bar"], "foobar"]

        for includes in includes_iterables:

            if isinstance(includes, str):
                includes = [includes]

            mocked_response = Mock()
            mocked_response.json.return_value = {"response": "foo"}
            mocked_get.return_value = mocked_response

            response = api._http_get(endpoint="some_endpoint", params={"param": [1, 2]}, includes=includes)
            self.assertEqual({"response": "foo"}, response)
            mocked_get.assert_called_with(
                url="bar/some_endpoint",
                params={
                    "api_token": "foo",
                    "tz": "UTC",
                    "param": "1,2",
                    "include": ",".join(sorted([i for i in includes])),
                    "page": 1,
                },
                headers={
                    "Accept-Encoding": "gzip, deflate",
                    "User-Agent": "https://github.com/Dmitrii-I/sportmonks {version}".format(version=__version__),
                },
            )

        self.assertEqual(len(includes_iterables), api.http_requests_made)

    @patch("requests.get", new=lambda: "response")
    def test_http_get_raises_type_error(self):
        """Test that `_http_get` raises TypeError."""
        api = BaseApiV2(base_url="foo", api_token="bar")
        self.assertRaises(TypeError, BaseApiV2._http_get, api, endpoint="foo")

    @patch("sportmonks._base.log", new=Mock())
    @patch("requests.get")
    def test_http_get_raises_sportmonks_api_error(self, mocked_get):
        """Test that `_http_get` raises SportMonksAPIError."""
        mocked_response = Mock()
        mocked_response.json.return_value = {"error": {"message": "foo"}}
        mocked_get.return_value = mocked_response

        api = BaseApiV2(base_url="foo", api_token="bar")
        self.assertRaises(SportMonksAPIError, api._http_get, endpoint="foo")

    @patch("requests.get")
    def test_http_get_unnests_data(self, mocked_get):
        """Test that `_http_get unnests data."""
        mocked_response = Mock()
        mocked_response.json.return_value = {"data": {"foo": "bar"}}
        mocked_get.return_value = mocked_response

        api = BaseApiV2(base_url="foo", api_token="bar")
        self.assertEqual({"foo": "bar"}, api._http_get(endpoint="foo"))

    @patch("requests.get")
    def test_http_get_requests_all_pages(self, mocked_requests_get):
        """Test that `_http_get` requests all pages."""

        def mocked_response(url, params, headers):
            response = Mock()
            response.request = Mock()
            response.json.return_value = {
                "data": [{"foo": "page_" + str(params["page"])}],
                "meta": {"pagination": {"current_page": params["page"], "total_pages": 3}},
            }

            return response

        mocked_requests_get.side_effect = mocked_response

        api = BaseApiV2(base_url="gg", api_token="foo")
        combined_response = api._http_get(endpoint="foo")
        self.assertEqual([{"foo": "page_1"}, {"foo": "page_2"}, {"foo": "page_3"}], combined_response)

    def test_unnested_simple(self):
        """Test `_unnest` with a simple case."""
        nested = {"a": 1, "b": [1, 2, 3], "c": "foo", "d": {"data": [1, 2, 3]}}

        expected = {"a": 1, "b": [1, 2, 3], "c": "foo", "d": [1, 2, 3]}

        api = BaseApiV2(base_url="foo", api_token="bar")
        self.assertEqual(api._unnested(nested), expected)

    def test_unnested_complex(self):
        """Test `_unnest` with a complex case."""
        inner = {"p": 1, "q": [1, 2, 3], "r": "foo", "s": {"data": {"x": 1, "z": "foo"}}}

        outer = {"a": 1, "b": [1, 2, 3], "c": "foo", "d": {"data": inner}}

        expected = {
            "a": 1,
            "b": [1, 2, 3],
            "c": "foo",
            "d": {"p": 1, "q": [1, 2, 3], "r": "foo", "s": {"x": 1, "z": "foo"}},
        }

        api = BaseApiV2(base_url="foo", api_token="bar")
        self.assertEqual(api._unnested(outer), expected)

    def test_unnested_super_complex(self):
        """Test `_unnest` with a super complex case."""
        inner_inner = [
            {"a": 1, "b": {"data": {"c": "foo"}}},
            {"a": 2, "b": {"data": {"c": "bar"}}},
            {"a": 3, "b": {"data": {"c": "foobar"}}},
        ]

        inner = {"p": 1, "q": [1, 2, 3], "r": "foo", "s": {"data": {"x": 1, "z": "foo", "y": {"data": inner_inner}}}}

        outer = {"a": 1, "b": [1, 2, 3], "c": "foo", "d": {"data": inner}}

        expected = {
            "a": 1,
            "b": [1, 2, 3],
            "c": "foo",
            "d": {
                "p": 1,
                "q": [1, 2, 3],
                "r": "foo",
                "s": {
                    "x": 1,
                    "z": "foo",
                    "y": [{"a": 1, "b": {"c": "foo"}}, {"a": 2, "b": {"c": "bar"}}, {"a": 3, "b": {"c": "foobar"}}],
                },
            },
        }
        api = BaseApiV2(base_url="foo", api_token="bar")
        self.assertEqual(api._unnested(outer), expected)

    def test_full_url(self):
        api = BaseApiV2(base_url="https://foo", api_token="bar")

        self.assertEqual(api._full_url(url_parts=["a", "b", "c"]), "https://foo/a/b/c")
        self.assertEqual(api._full_url(url_parts=["a/", "b/", "c/"]), "https://foo/a/b/c")
        self.assertEqual(api._full_url(url_parts=["a/", 1, 2]), "https://foo/a/1/2")
        self.assertEqual(api._full_url(url_parts="bar"), "https://foo/bar")
