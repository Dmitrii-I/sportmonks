
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

        # Lists must be serialized to a comma-separated string
        for k in params:
            if isinstance(params[k], list):
                params[k] = ','.join(str(el) for el in params[k])

        log.info('GET %s, params: %s' %
                 (url, {k: v if k != 'api_token' else 'API_TOKEN_REDACTED' for k, v in params.items()}))
        self.http_requests_made += 1
        raw_response = requests.get(url=url, params=params, headers=self.base_headers)
        log.info('GET succeeded of the complete url: %s' %
                 raw_response.request.url.replace(self.api_token, 'API_TOKEN_REDACTED'))
        response = raw_response.json()

        if 'error' in response:
            log.error('Error: %s' % response['error']['message'])
            log.error(raw_response.request)
            raise SportMonksAPIError(response['error']['message'])

        if ('meta' in response
                and 'pagination' in response['meta']
                and 'next' in response['meta']['pagination']['links']):
            query = urlsplit(response['meta']['pagination']['links']['next']).query
            params = parse_qs(query)
            page = {'page': params['page'][0]}
            response_single_page = self._http_get(endpoint=endpoint, params={**(params or {}), **page},
                                                  includes=includes)
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

    @property
    @abc.abstractmethod
    def _callables_cached_objects(self) -> Dict:
        pass

    @functools.lru_cache(maxsize=128)
    def _lookup_table(self, sportmonks_object: str, **kwargs) -> Dict:
        """ Returns a lookup table for specified soccer object.

        This function returns a lookup table for specified soccer object (e.g. season, league, team). This function is
        cached: calling it with same arguments again and again returns the lookup table from cache. This avoids needless
        HTTP requests to SportMonks.

        Note: caching could lead to stale lookup tables if your script is running for days and the underlying SportMonks
        data has changed in the meantime. Data could change because you upgraded your SportMonks plan or because
        SportMonks added new data.

        :param sportmonks_object: Soccer object recognized by the SportMonks API, like 'season', 'continent', 'team'.
        :param includes: Soccer objects to include.
        :raises: UnknownSportMonksObject exception.
        :returns: A lookup object.
        """

        try:
            return {obj['id']: obj for obj in self._callables_cached_objects[sportmonks_object](**kwargs)}
        except KeyError:
            message = "Unable to lookup unknown soccer object `%s`" % sportmonks_object
            log.error(message)
            raise UnknownSportMonksObject(message)


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
