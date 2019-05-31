"""Unit tests of `soccer` module."""

import unittest

from unittest.mock import patch, MagicMock
from datetime import date

from sportmonks_v2.soccer import SoccerApiV2


class TestSoccerApiV2(unittest.TestCase):
    """Class with unit tests of `SoccerApiV2` methods."""

    def setUp(self):
        """Set up unit tests."""
        pass

    @patch('sportmonks_v2.soccer.get')
    def test_init(self, mocked_get):
        """Test `__init__` method."""
        mocked_response = MagicMock()
        mocked_response.json.return_value = {'meta': 'foo'}
        mocked_get.return_value = mocked_response

        api = SoccerApiV2(api_token='foo')
        self.assertEqual('foo', api.api_token)

    def test_continent_by_id(self):
        """Test `continent_by_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.continent_by_id(api, continent_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='continents/1', includes=['foo', 'bar'])

    def test_all_countries(self):
        """Test `all_countries` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.all_countries(api, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='countries', includes=['foo', 'bar'])

    def test_country_by_id(self):
        """Test `country_by_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.country_by_id(api, country_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='countries/1', includes=['foo', 'bar'])

    def test_all_leagues(self):
        """Test `all_leagues` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.all_leagues(api, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='leagues', includes=['foo', 'bar'])

    def test_league_by_id(self):
        """Test `league_by_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.league_by_id(api, league_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='leagues/1', includes=['foo', 'bar'])

    def test_all_seasons(self):
        """Test `all_seasons` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.all_seasons(api, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='seasons', includes=['foo', 'bar'])

    def test_season_by_id(self):
        """Test `season_by_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.season_by_id(api, season_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='seasons/1', includes=['foo', 'bar'])

    def test_season_results(self):
        """Test `season_results` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.season_results(api, season_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='seasons/results/1',
                                              includes=['results', 'results.foo', 'results.bar'])

        # Test without any includes
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.season_results(api, season_id=1)
        api._http_get.assert_called_once_with(endpoint='seasons/results/1',
                                              includes=['results'])

    def test_fixtures_between(self):
        """Test `fixtures_between` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixtures_between(api, start_date=date(2000, 1, 1), end_date=date(2001, 1, 1), league_ids=[1],
                                     includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='fixtures/between/2000-01-01/2001-01-01',
                                              includes=['foo', 'bar'], params={'leagues': [1], 'markets': [],
                                                                               'bookmakers': []})

    def test_fixture_by_id(self):
        """Test `fixture_by_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixture_by_id(api, fixture_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='fixtures/1', includes=['foo', 'bar'],
                                              params={'markets': [], 'bookmakers': []})

    def test_fixtures_between_by_team_id(self):
        """Test `fixtures_between_by_team_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixtures_between_by_team_id(api, start_date=date(2000, 1, 1), end_date=date(2001, 1, 1), team_id=1,
                                                includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='fixtures/between/2000-01-01/2001-01-01/1',
                                              includes=['foo', 'bar'], params={'leagues': [], 'markets': [],
                                                                               'bookmakers': []})

    def test_fixtures_today(self):
        """Test `fixtures_today` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixtures_today(api, league_ids=[1], includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='livescores', includes=['foo', 'bar'],
                                              params={'leagues': [1], 'markets': [], 'bookmakers': []})

    def test_fixtures_in_play(self):
        """Test `fixtures_in_play` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.fixtures_in_play(api, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='livescores/now', includes=['foo', 'bar'],
                                              params={'leagues': [], 'markets': [], 'bookmakers': []})

    def test_head_to_head_by_team_ids(self):
        """Test `head_to_head_by_team_ids` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.head_to_head_by_team_ids(api, team_ids={1, 2}, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='head2head/1/2', includes=['foo', 'bar'])

    def test_commentaries_by_fixture_id(self):
        """Test `commentaries_by_fixture_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.commentaries_by_fixture_id(api, fixture_id=1)
        api._http_get.assert_called_once_with(endpoint='commentaries/fixture/1')

    def test_all_video_highlights(self):
        """Test `all_video_highlights` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.all_video_highlights(api, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='highlights', includes=['foo', 'bar'])

    def test_video_highlights_by_fixture_id(self):
        """Test `video_highlights_by_fixture_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.video_highlights_by_fixture_id(api, fixture_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='highlights/fixture/1', includes=['foo', 'bar'])

    def test_standings_by_season_id(self):
        """Test `standings_by_season_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.standings_by_season_id(api, season_id=1, group_id=123, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='standings/season/1', params={'group_id': 123},
                                              includes=['standings.foo', 'standings.bar'])

    def test_live_standings_by_season_id(self):
        """Test `live_standings_by_season_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.live_standings_by_season_id(api, season_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='standings/season/live/1', params={'group_id': None},
                                              includes=['standings.foo', 'standings.bar'])

    def test_teams_by_season_id(self):
        """Test `teams_by_season_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.teams_by_season_id(api, season_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='teams/season/1', includes=['foo', 'bar'])

    def test_team_by_id(self):
        """Test `team_by_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.team_by_id(api, team_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='teams/1', includes=['foo', 'bar'])

    def test_team_stats(self):
        """Test `team_stats` method."""
        api = MagicMock()()
        api._http_get.return_value = {'stats': 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual('foo', SoccerApiV2.team_stats(api, team_id=1))
        api._http_get.assert_called_once_with(endpoint='teams/1', includes=['stats'])

    def test_season_stats(self):
        """Test `season_stats` method."""
        api = MagicMock()()
        api._http_get.return_value = {'stats': 'foo'}
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual(api._http_get.return_value, SoccerApiV2.season_stats(api, season_id=1))
        api._http_get.assert_called_once_with(endpoint='seasons/1', includes=['stats'])

    def test_topscorers_by_season_id(self):
        """Test `topscorers_by_season_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.topscorers_by_season_id(api, season_id=1, includes=['foo', 'bar'])
        expected_includes = ['goalscorers.foo', 'goalscorers.bar', 'cardscorers.foo', 'cardscorers.bar',
                             'assistscorers.foo', 'assistscorers.bar']
        api._http_get.assert_called_once_with(endpoint='topscorers/season/1', includes=expected_includes)

    def test_venue_by_id(self):
        """Test `venue_by_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.venue_by_id(api, venue_id=1)
        api._http_get.assert_called_once_with(endpoint='venues/1')

    def test_rounds_by_season_id(self):
        """Test `rounds_by_season_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.rounds_by_season_id(api, season_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='rounds/season/1', includes=['foo', 'bar'])

    def test_round_by_id(self):
        """Test `round_by_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.round_by_id(api, round_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='rounds/1', includes=['foo', 'bar'])

    def test_pre_match_odds(self):
        """Test `pre_match_odds` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.pre_match_odds(api, fixture_id=1)
        api._http_get.assert_called_once_with(endpoint='odds/fixture/1')

    def test_in_play_odds(self):
        """Test `in_play_odds` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.in_play_odds(api, fixture_id=1)
        api._http_get.assert_called_once_with(endpoint='odds/inplay/fixture/1')

    def test_player_by_id(self):
        """Test `player_by_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.player_by_id(api, player_id=1)
        api._http_get.assert_called_once_with(endpoint='players/1', includes=None)

    def test_all_bookmakers(self):
        """Test `all_bookmakers` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.all_bookmakers(api)
        api._http_get.assert_called_once_with(endpoint='bookmakers')

    def test_bookmaker_by_id(self):
        """Test `bookmaker_by_id` method."""
        api = MagicMock()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.bookmaker_by_id(api, bookmaker_id=1)
        api._http_get.assert_called_once_with(endpoint='bookmakers/1')

    def test_squad_by_season_and_team_id(self):
        """Test `squad_by_season_and_team_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.squad_by_season_and_team_id(api, season_id=1, team_id=2, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='squad/season/1/team/2', includes=['foo', 'bar'])

    @patch('sportmonks_v2.soccer.get')
    def test_meta(self, mocked_requests_get):
        """Test `meta` method."""
        api = MagicMock()()
        api.base_url = 'http://foo.bar'
        api._base_params = 'params'
        api._base_headers = 'headers'

        mocked_response = MagicMock()()
        mocked_response.json.return_value = {'meta': 'foo'}

        mocked_requests_get.return_value = mocked_response
        # noinspection PyCallByClass, PyTypeChecker
        self.assertEqual(SoccerApiV2.meta(api), 'foo')

        mocked_requests_get.assert_called_once_with(url='http://foo.bar/continents', params='params', headers='headers')

    def test_stage_by_id(self):
        """Test `stage_by_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.stage_by_id(api, stage_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='stages/1', includes=['foo', 'bar'])

    def test_stages_by_season_id(self):
        """Test `stages_by_season_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.stages_by_season_id(api, season_id=1, includes=['foo', 'bar'])
        api._http_get.assert_called_once_with(endpoint='stages/season/1', includes=['foo', 'bar'])

    def test_tv_stations_by_fixture_id(self):
        """Test `tv_stations_by_fixture_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.tv_stations_by_fixture_id(api, fixture_id=1)
        api._http_get.assert_called_once_with(endpoint='tvstations/fixture/1')

    def test_venues_by_season_id(self):
        """Test `venues_by_season_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.venues_by_season_id(api, season_id=1)
        api._http_get.assert_called_once_with(endpoint='venues/season/1')

    def test_all_markets(self):
        """Test `all_markets` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.all_markets(api)
        api._http_get.assert_called_once_with(endpoint='markets')

    def test_market_by_id(self):
        """Test `market_by_id` method."""
        api = MagicMock()()
        # noinspection PyCallByClass, PyTypeChecker
        SoccerApiV2.market_by_id(api, market_id=1)
        api._http_get.assert_called_once_with(endpoint='markets/1')
