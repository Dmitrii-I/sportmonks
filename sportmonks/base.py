
import requests
import abc
import functools
import pytz
import tzlocal
from os.path import join
from logging import getLogger
from urllib.parse import urlsplit, parse_qs
from typing import Dict, List
from sportmonks import __version__

log = getLogger(__name__)


class BaseApiV2(metaclass=abc.ABCMeta):
    def __init__(self, base_url: str, api_token: str, tz_name: str=None) -> None:

        self.base_url = base_url
        if not self.base_url:
            raise BaseUrlMissingError('Base URL must be provided!')

        self.api_token = api_token
        if not self.api_token:
            raise ApiKeyMissingError('API key must be provided!')

        if tz_name:
            self.timezone = pytz.timezone(tz_name)
        else:
            self.timezone = tzlocal.get_localzone()

        self.http_requests_made = 0
        self.base_params = {'api_token': self.api_token, 'tz': str(self.timezone)}
        self.base_headers = {
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'https://github.com/Dmitrii-I/sportmonks {version}'.format(version=__version__)
        }

    def _unnested(self, dictionary: dict) -> Dict:
        """ Returns dictionary with unnested data.

        SportMonks API responses contain data in the arguably redundant key `data`. This method walks through the
        dictionary and unnests all data keys, recursively. For example, `{'country_ids': {'data': [1, 2, 3]}}` is
        unnested into `{'country_ids': [1, 2, 3]}`.

        :param dictionary: Dictionary.
        :returns: Unnested dictionary.
        :raises: IncompatibleDictionarySchema
        """

        log.debug('Unnest dictionary')
        unnested = dict()

        for k in dictionary:
            if isinstance(dictionary[k], dict) and 'data' in dictionary[k]:

                if len(dictionary[k]) > 1:
                    raise IncompatibleDictionarySchema('Cannot flatten a dictionary having keys other than `data`.')

                data = dictionary[k]['data']

                if isinstance(data, list):
                    for i in range(len(data)):
                        if isinstance(data[i], dict):
                            data[i] = self._unnested(data[i])
                elif isinstance(data, dict):
                    data = self._unnested(data)

                unnested[k] = data
            else:
                unnested[k] = dictionary[k]

        return unnested

    def _http_get(self, endpoint: str, params: dict = None, includes: tuple = None) -> Dict or List[Dict]:
        """ Returns parsed response of an HTTP GET request. If the response is paginated, then all pages are returned.

        :param endpoint: Endpoint where to send the GET request to.
        :param params: Query string parameters of the GET request.
        :param includes: Additional objects to include, e.g. results, odds, seasons, etc.
        :returns: Parsed response to a HTTP GET request.
        """

        url = join(self.base_url, endpoint)
        params = {**self.base_params, **(params or {}), **{'include': ','.join(includes or [])}}

        if 'page' not in params:
            params['page'] = 1

        # Lists must be serialized to a comma-separated string
        for k in params:
            if isinstance(params[k], list):
                params[k] = ','.join(str(el) for el in params[k])

        log.debug('GET %s, params: %s' %
                 (url, {k: v if k != 'api_token' else 'API_TOKEN_REDACTED' for k, v in params.items()}))
        self.http_requests_made += 1
        raw_response = requests.get(url=url, params=params, headers=self.base_headers)
        log.debug('GET succeeded of the complete url: %s' %
                 raw_response.request.url.replace(self.api_token, 'API_TOKEN_REDACTED'))
        response = raw_response.json()

        if 'error' in response:
            log.error('Error: %s' % response['error']['message'])
            raise SportMonksAPIError(response['error']['message'])

        if ('meta' in response
                and 'pagination' in response['meta']
                and response['meta']['pagination']['current_page'] < response['meta']['pagination']['total_pages']
                and response['meta']['pagination']['current_page'] == 1):
            log.debug('Response is paginated: %s pages' % response['meta']['pagination']['total_pages'])
            log.debug('Request pages 2 through %s' % response['meta']['pagination']['total_pages'])

            for page_number in range(2, response['meta']['pagination']['total_pages'] + 1):
                params['page'] = page_number
                response_single_page = self._http_get(endpoint=endpoint, params=params, includes=includes)
                response['data'] += response_single_page

        if 'data' in response:
            response = response['data']

        if isinstance(response, dict):
            response = self._unnested(response)
        elif isinstance(response, list):
            response = [self._unnested(pr) for pr in response]
        else:
            msg = 'Unable to flatten data of type `%s`. Type must me a list or dict.' % type(response)
            log.error(msg)
            raise TypeError(msg)

        return response


class ApiKeyMissingError(Exception):
    pass


class BaseUrlMissingError(Exception):
    pass


class SportMonksAPIError(Exception):
    pass


class IncompatibleDictionarySchema(Exception):
    pass


class UnknownSportMonksObject(Exception):
    pass
