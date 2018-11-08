""" This module contains unit tests of `soccer` module. """

import unittest
from sportmonks.soccer import SoccerApiV2
from unittest.mock import patch, MagicMock
from datetime import date


class TestSoccerApiV20(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        api = SoccerApiV2(api_token='foo')
        self.assertEqual('foo', api.api_token)

    def test_callables_cached_objects(self):

        api = SoccerApiV2('foo')
        expected_cached_objects = {'continent', 'country', 'league', 'bookmaker'}

        self.assertEqual(expected_cached_objects, set(api._callables_cached_objects.keys()))

        self.assertEqual(api.continents, api._callables_cached_objects['continent'])
        self.assertEqual(api.countries, api._callables_cached_objects['country'])
        self.assertEqual(api.leagues, api._callables_cached_objects['league'])
        self.assertEqual(api.bookmakers, api._callables_cached_objects['bookmaker'])

    def test_continents(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.continents(api, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='continents', includes=('foo', 'bar'))

    def test_continent(self):
        api = MagicMock()
        api._lookup_table.return_value = {1: 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual('foo', SoccerApiV2.continent(api, continent_id=1, includes=('foo', 'bar')))
        api._lookup_table.assert_called_once_with(sportmonks_object='continent', includes=('foo', 'bar'))

    def test_countries(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.countries(api, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='countries', includes=('foo', 'bar'))

    def test_country(self):
        api = MagicMock()
        api._lookup_table.return_value = {1: 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual('foo', SoccerApiV2.country(api, country_id=1, includes=('foo', 'bar')))
        api._lookup_table.assert_called_once_with(sportmonks_object='country', includes=('foo', 'bar'))

    def test_leagues(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.leagues(api, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='leagues', includes=('foo', 'bar'))

    def test_league(self):
        api = MagicMock()
        api._lookup_table.return_value = {1: 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual('foo', SoccerApiV2.league(api, league_id=1, includes=('foo', 'bar')))
        api._lookup_table.assert_called_once_with(sportmonks_object='league', includes=('foo', 'bar'))

    def test_seasons(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.seasons(api, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='seasons', includes=('foo', 'bar'))

    def test_season(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.season(api, season_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='seasons/1', includes=('foo', 'bar'))

    def test_season_results(self):
        api = MagicMock()
        api.season.return_value = {'results': 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual('foo', SoccerApiV2.season_results(api, season_id=1, includes=('foo', 'bar')))
        api.season.assert_called_once_with(season_id=1, includes=('results', 'results.foo', 'results.bar'))

        # Test without any includes
        api = MagicMock()
        api.season.return_value = {'results': 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual('foo', SoccerApiV2.season_results(api, season_id=1))
        api.season.assert_called_once_with(season_id=1, includes=('results',))

    def test_fixtures(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixtures(api, start_date=date(2000, 1, 1), end_date=date(2001, 1, 1), league_ids=[1],
                             includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='fixtures/between/2000-01-01/2001-01-01',
                                              params={'leagues': [1]}, includes=('foo', 'bar'))

    def test_fixture(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixture(api, fixture_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='fixtures/1', includes=('foo', 'bar'))

    def test_team_fixtures(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.team_fixtures(api, start_date=date(2000, 1, 1), end_date=date(2001, 1, 1), team_id=1,
                                  includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='fixtures/between/2000-01-01/2001-01-01/1',
                                              includes=('foo', 'bar'))

    def test_fixtures_today(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixtures_today(api, league_ids=[1], includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='livescores', params={'leagues': [1]}, includes=('foo', 'bar'))

    def test_fixtures_in_play(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixtures_in_play(api, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='livescores/now', includes=('foo', 'bar'))

    def test_head_to_head_fixtures(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.head_to_head_fixtures(api, team_ids={1, 2}, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='head2head/1/2', includes=('foo', 'bar'))

    def test_commentaries(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.commentaries(api, fixture_id=1)
        api._http_get.assert_called_once_with(endpoint='commentaries/fixture/1')

    def test_video_commentaries(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.video_highlights(api, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='highlights', includes=('foo', 'bar'))

        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.video_highlights(api, fixture_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='highlights/fixture/1', includes=('foo', 'bar'))

    def test_standings(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.standings(api, season_id=1, live=False, group_id=123, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='standings/season/1', includes=('foo', 'bar'),
                                              params={'group_id': 123})

        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.standings(api, season_id=1, live=True, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='standings/season/live/1', params={'group_id': None},
                                              includes=('foo', 'bar'))

    def test_teams(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.teams(api, season_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='teams/season/1', includes=('foo', 'bar'))

    def test_team(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.team(api, team_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='teams/1', includes=('foo', 'bar'))

    def test_team_stats(self):
        api = MagicMock()()
        api._http_get.return_value = {'stats': 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual('foo', SoccerApiV2.team_stats(api, team_id=1))
        api._http_get.assert_called_once_with(endpoint='teams/1', includes=('stats',))

    def test_top_scorers(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.top_scorers(api, season_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='topscorers/season/1', includes=('foo', 'bar'))

    def test_venue(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.venue(api, venue_id=1)
        api._http_get.assert_called_once_with(endpoint='venues/1')

    def test_rounds(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.rounds(api, season_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='rounds/season/1', includes=('foo', 'bar'))

    def test_round(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.round(api, round_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='rounds/1', includes=('foo', 'bar'))

    def test_pre_match_odds(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.pre_match_odds(api, fixture_id=1)
        api._http_get.assert_called_once_with(endpoint='odds/fixture/1')

    def test_in_play_odds(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.in_play_odds(api, fixture_id=1)
        api._http_get.assert_called_once_with(endpoint='odds/inplay/fixture/1')

    def test_player(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.player(api, player_id=1)
        api._http_get.assert_called_once_with(endpoint='players/1')

    def test_bookmakers(self):
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.bookmakers(api)
        api._http_get.assert_called_once_with(endpoint='bookmakers')

    def test_bookmaker(self):
        api = MagicMock()
        api._lookup_table.return_value = {1: 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual('foo', SoccerApiV2.bookmaker(api, bookmaker_id=1))
        api._lookup_table.assert_called_once_with(sportmonks_object='bookmaker')

    def test_squad(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.squad(api, season_id=1, team_id=2, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='squad/season/1/team/2', includes=('foo', 'bar'))

    @patch('sportmonks.soccer.get')
    def test_meta(self, mocked_requests_get):
        api = MagicMock()()
        api.base_url = 'http://foo.bar'
        api.base_params = 'params'
        api.base_headers = 'headers'

        mocked_response = MagicMock()()
        mocked_response.json.return_value = {'meta': 'foo'}

        mocked_requests_get.return_value = mocked_response
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual(SoccerApiV2.meta(api), 'foo')

        mocked_requests_get.assert_called_once_with(url='http://foo.bar/continents', params='params', headers='headers')

    def test_stage(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.stage(api, stage_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='stages/1', includes=('foo', 'bar'))

    def test_season_stages(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.season_stages(api, season_id=1, includes=('foo', 'bar'))
        api._http_get.assert_called_once_with(endpoint='stages/season/1', includes=('foo', 'bar'))

    def test_fixture_tv_stations(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixture_tv_stations(api, fixture_id=1)
        api._http_get.assert_called_once_with(endpoint='tvstations/fixture/1')

    def test_season_venues(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.season_venues(api, season_id=1)
        api._http_get.assert_called_once_with(endpoint='venues/season/1')

    def test_markets(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.markets(api)
        api._http_get.assert_called_once_with(endpoint='markets')

    def test_market(self):
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.market(api, market_id=1)
        api._http_get.assert_called_once_with(endpoint='markets/1')



