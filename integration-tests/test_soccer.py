""" This module contains integration tests of `soccer` module.

The dictionaries returned by the SportMonks endpoints contain two types of keys: non-includes keys and includes keys. In
our tests we assume that non-includes keys are always present. The includes-keys may be missing, even after explicitly
requesting them. SportMonks does not return `None` for requested includes if they are not available, these includes are
simply missing in the response.

When testing, we request includes from endpoints that have them available. We do not test nested includes because then
the number of requested includes increases quickly and consequently the request processing becomes noticeably slow.
"""

import logging
import sportmonks.base
from sys import stdout
from datetime import date
from collections import defaultdict


logging.basicConfig(stream=stdout, level=logging.INFO)


class TestSoccerApiV20:

    def test_continents(self, soccer_api):
        for continent in soccer_api.continents(includes=('countries',)):
            assert {'name', 'id', 'countries'} == set(continent.keys())

    def test_continent(self, soccer_api):
        europe = soccer_api.continent(continent_id=1, includes=('countries',))
        assert {'name', 'id', 'countries'} == set(europe.keys())

    def test_countries(self, soccer_api):
        for country in soccer_api.countries(includes=('continent', 'leagues')):

            # Following countries have no continent associated with them:
            countries_without_continent = {99474, 190324, 1442002, 1884978, 3499960, 8151924, 9374632, 11311331,
                                           12444275, 14534056, 14566098, 14566636, 15288356, 15629849, 25293454}

            expected = {'name', 'id', 'extra', 'continent', 'leagues'}

            if country['id'] in countries_without_continent:
                assert expected - {'continent'} == set(country.keys())
            else:
                assert expected == set(country.keys())

    def test_country(self, soccer_api):
        poland = soccer_api.country(country_id=2, includes=('continent', 'leagues'))

        assert poland['name'] == 'Poland'
        assert poland['id'] == 2
        assert poland['extra']['continent'] == 'Europe'
        assert poland['extra']['flag'][0:10] == '<svg xmlns'
        assert poland['extra']['iso'] == 'POL'
        assert poland['extra']['latitude'] == '52.147850036621094'
        assert poland['extra']['longitude'] == '19.37775993347168'
        assert poland['extra']['sub_region'] == 'Eastern Europe'
        assert poland['extra']['world_region'] == 'EMEA'

        assert {'continent', 'leagues'} <= set(poland.keys())

    def test_leagues(self, soccer_api):
        leagues = soccer_api.leagues(includes=('country', 'season', 'seasons'))
        expected = {'country_id', 'coverage', 'current_round_id', 'current_season_id', 'current_stage_id', 'id',
                    'is_cup', 'legacy_id', 'live_standings', 'name', 'country', 'season', 'seasons'}

        for league in leagues:
            assert expected == set(league.keys())

    def test_league(self, soccer_api):
        includes = {'country', 'season', 'seasons'}
        premiership = soccer_api.league(league_id=501, includes=tuple(includes))

        expected = {'country_id', 'coverage', 'current_round_id', 'current_season_id', 'current_stage_id', 'id',
                    'is_cup', 'legacy_id', 'live_standings', 'name'}

        assert expected | includes == set(premiership.keys())

    def test_seasons(self, soccer_api):
        includes = ('league', 'stages', 'rounds', 'fixtures', 'upcoming', 'results', 'groups')
        seasons = soccer_api.seasons(includes=includes)

        for season in seasons:

            # fixtures includes is always missing even though SportMonks documentation says it is available
            if 'fixtures' in season:
                raise KeyError('Found `fixtures` includes! The test needs to be adjusted to test for this')

            assert set(includes) - {'fixtures'} <= set(season.keys())

    def test_season(self, soccer_api):
        includes = ('league', 'stages', 'rounds', 'fixtures', 'upcoming', 'results', 'groups')
        season = soccer_api.season(season_id=6361, includes=includes)

        assert season['name'] == '2017/2018'
        assert season['league_id'] == 271
        assert set(includes) <= set(season.keys())

    def test_season_results(self, soccer_api):
        """ As per [1], the valid includes for a fixture are: localTeam, visitorTeam, substitutions, goals, cards,
        other, corners, lineup, bench, sidelined, stats, comments, tvstations, highlights, league, season, round, stage,
        referee, events, venue, odds, flatOdds, inplay, localCoach, visitorCoach,group, trends. However, requesting all
        these includes at once results in an API error, therefore we break down this set into subsets, and test each
        subset.

        [1] https://www.sportmonks.com/products/soccer/docs/2.0/fixtures/18
        """

        # The `group` include is not applicable for season with ID 6361 because it is not a tournament-type season,
        # so it is omitted in this test.
        includes_tuples = [
            ('localTeam', 'visitorTeam', 'substitutions', 'goals', 'cards', 'other', 'corners', 'lineup', 'bench'),
            ('sidelined', 'stats', 'comments', 'tvstations', 'highlights', 'league', 'season', 'round', 'stage'),
            ('referee', 'events', 'venue', 'flatOdds', 'inplay', 'localCoach', 'visitorCoach', 'trends'),
            ('odds',)
        ]

        expected_non_includes = {
            'aggregate_id', 'attendance', 'coaches', 'commentaries', 'deleted', 'formations', 'group_id', 'id',
            'league_id', 'localteam_id', 'pitch', 'referee_id', 'round_id', 'scores', 'season_id', 'stage_id',
            'standings', 'time', 'venue_id', 'visitorteam_id', 'weather_report', 'winning_odds_calculated'
        }

        known_missing_includes = defaultdict(set)
        known_missing_includes.update(
            {
                1140241: {'round'},
                1140251: {'round'},
                1140270: {'round'},
                1140284: {'round'},
                1241158: {'round'},
                1241159: {'round'},
                1492895: {'round'},
                1281339: {'round', 'stage'},
                1281341: {'round', 'stage'},
                1281343: {'round', 'stage'},
                1281346: {'round', 'stage'},
                220294: {'referee', 'localCoach', 'visitorCoach'},
                220345: {'referee', 'localCoach', 'visitorCoach'},
                220386: {'referee', 'localCoach', 'visitorCoach'},
                220428: {'referee', 'localCoach', 'visitorCoach'},
                220481: {'referee', 'localCoach', 'visitorCoach'},
                220510: {'referee', 'localCoach', 'visitorCoach'},
                220547: {'referee', 'localCoach', 'visitorCoach'},
                220586: {'referee', 'localCoach', 'visitorCoach'},
                220624: {'referee', 'localCoach', 'visitorCoach'},
                220665: {'localCoach', 'visitorCoach'},
                220702: {'localCoach', 'visitorCoach'},
                220741: {'localCoach', 'visitorCoach'},
                220774: {'localCoach', 'visitorCoach'},
                220792: {'localCoach', 'visitorCoach'},
                220802: {'localCoach', 'visitorCoach'},
                220812: {'localCoach', 'visitorCoach'},
                220822: {'localCoach', 'visitorCoach'},
                220832: {'localCoach', 'visitorCoach'},
                220842: {'localCoach', 'visitorCoach'},
                220853: {'localCoach', 'visitorCoach'},
                225987: {'visitorCoach'}
            }
        )

        for includes_tuple in includes_tuples:
            season_results = soccer_api.season_results(season_id=759, includes=includes_tuple)
            for result in season_results:

                missing_includes = (set(includes_tuple) - known_missing_includes[result['id']]) - set(result.keys())
                assert missing_includes == set()

                assert expected_non_includes <= set(result.keys())

    def test_fixtures(self, soccer_api):
        fixtures_1 = soccer_api.fixtures(date(2018, 1, 10), date(2018, 2, 10), [501, 271])
        fixtures_2 = soccer_api.fixtures(date(2018, 1, 10), date(2018, 2, 10), [])
        fixtures_3 = soccer_api.fixtures(date(2018, 1, 10), date(2018, 2, 10))
        assert 25 == len(fixtures_1)
        assert 25 == len(fixtures_2)
        assert 25 == len(fixtures_3)

        expected = {
            'aggregate_id', 'attendance', 'coaches', 'commentaries', 'deleted', 'formations', 'group_id', 'id',
            'league_id', 'localteam_id', 'pitch', 'referee_id', 'round_id', 'scores', 'season_id', 'stage_id',
            'standings', 'time', 'venue_id', 'visitorteam_id', 'weather_report', 'winning_odds_calculated'
        }

        # includes `odds`, `inplay`, and `trends` are not available for fixtures from 2018-01-10 through 2018-02-10 for
        # league with ID 271.
        includes = ('localTeam', 'visitorTeam', 'substitutions', 'goals', 'cards', 'other', 'corners', 'lineup', 'bench',
                    'sidelined', 'stats', 'comments', 'tvstations', 'highlights', 'league', 'season', 'round', 'stage',
                    'referee', 'events', 'venue', 'flatOdds', 'localCoach', 'visitorCoach')
        fixtures = soccer_api.fixtures(date(2018, 1, 10), date(2018, 2, 10), [271], includes=includes)

        for fixture in fixtures:
            assert set(includes) <= set(fixture.keys())
            assert expected <= set(fixture.keys())

    def test_team_fixtures(self, soccer_api):
        expected = {
            'aggregate_id', 'attendance', 'coaches', 'commentaries', 'deleted', 'formations', 'group_id', 'id',
            'league_id', 'localteam_id', 'pitch', 'referee_id', 'round_id', 'scores', 'season_id', 'stage_id',
            'standings', 'time', 'venue_id', 'visitorteam_id', 'weather_report', 'winning_odds_calculated'
        }

        # Omit includes `inplay` and `trends` because they are not available for fixtures from 2018-01-01 through
        # 2018-04-01 for team with ID 85.
        includes = ('localTeam', 'visitorTeam', 'substitutions', 'goals', 'cards', 'other', 'corners', 'lineup', 'bench',
                    'sidelined', 'stats', 'comments', 'tvstations', 'highlights', 'league', 'season', 'round', 'stage',
                    'referee', 'events', 'venue', 'flatOdds', 'localCoach', 'visitorCoach', 'odds')

        fixtures = soccer_api.team_fixtures(start_date=date(2018, 1, 1), end_date=date(2018, 4, 1), team_id=85,
                                        includes=includes)

        assert len(fixtures) == 7

        for fixture in fixtures:
            assert set(includes) <= set(fixture.keys())
            assert expected <= set(fixture.keys())

    def test_fixtures_today(self, soccer_api):
        """ The fixtures returned by `fixtures_today` depend on the time of running this test. Therefore, we cannot
        know which fixtures will be returned or whether any fixture at all will be returned. This non-deterministic
        return value means we cannot know what includes will be attached to each returned fixture if we request all of
        them. Therefore we request a limited set of includes, one which we assume is available for any fixture.
        """

        essential_includes = ('localTeam', 'visitorTeam', 'league', 'season', 'round', 'stage', 'venue')
        fixtures = soccer_api.fixtures_today(includes=essential_includes)
        assert isinstance(fixtures, list)

        expected = {
            'aggregate_id', 'attendance', 'coaches', 'commentaries', 'deleted', 'formations', 'group_id', 'id',
            'league_id', 'localteam_id', 'pitch', 'referee_id', 'round_id', 'scores', 'season_id', 'stage_id',
            'standings', 'time', 'venue_id', 'visitorteam_id', 'weather_report', 'winning_odds_calculated'
        }

        for fixture in fixtures:
            assert set(essential_includes) <= set(fixture.keys())
            assert expected <= set(fixture.keys())

    def test_fixtures_in_play(self, soccer_api):
        """ The fixtures returned by `fixtures_in_play` depend on the time of running this test. Therefore, we cannot
        know which fixtures will be returned or whether any fixture at all will be returned. This non-deterministic
        return value means we cannot know what includes will be attached to each returned fixture if we request all of
        them. Therefore we request a limited set of includes, one which we assume is available for any fixture.
        """

        essential_includes = ('localTeam', 'visitorTeam', 'league', 'season', 'round', 'stage', 'venue')
        fixtures = soccer_api.fixtures_in_play(includes=essential_includes)
        assert isinstance(fixtures, list)

        expected = {
            'aggregate_id', 'attendance', 'coaches', 'commentaries', 'deleted', 'formations', 'group_id', 'id',
            'league_id', 'localteam_id', 'pitch', 'referee_id', 'round_id', 'scores', 'season_id', 'stage_id',
            'standings', 'time', 'venue_id', 'visitorteam_id', 'weather_report', 'winning_odds_calculated'
        }

        for fixture in fixtures:
            assert set(essential_includes) <= set(fixture.keys())
            assert expected <= set(fixture.keys())

    def test_fixture(self, soccer_api):

        # `inplay` and `trends` includes not available for fixture ID 1625164
        includes = ('localTeam', 'visitorTeam', 'substitutions', 'goals', 'cards', 'other', 'corners', 'lineup', 'bench',
                    'sidelined', 'stats', 'comments', 'tvstations', 'highlights', 'league', 'season', 'round', 'stage',
                    'referee', 'events', 'venue', 'flatOdds', 'localCoach', 'visitorCoach', 'odds')

        expected = {
            'aggregate_id', 'attendance', 'coaches', 'commentaries', 'deleted', 'formations', 'group_id', 'id',
            'league_id', 'localteam_id', 'pitch', 'referee_id', 'round_id', 'scores', 'season_id', 'stage_id',
            'standings', 'time', 'venue_id', 'visitorteam_id', 'weather_report', 'winning_odds_calculated'
        }

        fixture = soccer_api.fixture(fixture_id=1625164, includes=includes)

        assert set(includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())

    def test_commentaries(self, soccer_api):
        expected = {'comment', 'extra_minute', 'fixture_id', 'goal', 'important', 'minute', 'order'}
        commentaries = soccer_api.commentaries(1871916)

        for comment in commentaries:
            assert expected == set(comment.keys())

    def test_video_highlights(self, soccer_api):
        highlights = soccer_api.video_highlights(includes=('fixture',))
        expected = {'created_at', 'fixture_id', 'fixture', 'location'}

        for hl in highlights:
            assert set(hl.keys()) == expected

        fixture_highlights = soccer_api.video_highlights(fixture_id=218832)
        for hl in fixture_highlights:
            assert set(hl.keys()) == expected - {'fixture'}

    def test_head_to_head_fixtures(self, soccer_api):
        """ The fixtures returned by `head_to_head_fixtures` depend on the time of running this test. Therefore, we
        cannot know which fixtures will be returned or whether any fixture at all will be returned. This
        non-deterministic return value means we cannot know what includes will be attached to each returned fixture if
        we request all of them. Therefore we request a limited set of includes, one which we assume is available for
        any fixture.
        """

        expected = {
            'aggregate_id', 'attendance', 'coaches', 'commentaries', 'deleted', 'formations', 'group_id', 'id',
            'league_id', 'localteam_id', 'pitch', 'referee_id', 'round_id', 'scores', 'season_id', 'stage_id',
            'standings', 'time', 'venue_id', 'visitorteam_id', 'weather_report', 'winning_odds_calculated'
        }

        essential_includes = ('localTeam', 'visitorTeam', 'league', 'season', 'round', 'stage', 'venue')

        fixtures = soccer_api.head_to_head_fixtures(team_ids={85, 86}, includes=essential_includes)

        for fixture in fixtures:
            assert set(essential_includes) <= set(fixture.keys())
            assert expected <= set(fixture.keys())

    def test_standings(self, soccer_api):
        includes = ('team', 'league', 'season', 'round', 'stage')
        standings = soccer_api.standings(season_id=6361, includes=includes)

        # because of a bug in SportMonks API, none of the includes are returned
        assert standings == soccer_api.standings(season_id=6361)

        expected = {'away', 'group_id', 'group_name', 'home', 'overall', 'points', 'position', 'recent_form', 'result',
                    'status', 'team_id', 'team_name', 'total', 'round_name', 'round_id'}

        for standings_season_stage in standings:
            for standing_entry in standings_season_stage['standings']:
                assert expected == set(standing_entry.keys())

        try:
            standings = soccer_api.standings(season_id=6361, live=True, includes=includes)
        except sportmonks.base.SportMonksAPIError as e:
            if str(e) == "Insufficient Privileges! Your current plan doesn't allow access to this section!":
                return
            else:
                raise

        for standings_season_stage in standings:
            for standing_entry in standings_season_stage['standings']:
                assert expected == set(standing_entry.keys())

    def test_teams(self, soccer_api):
        includes = {'country', 'squad', 'coach', 'transfers', 'sidelined', 'stats', 'venue', 'fifaranking', 'uefaranking',
                    'visitorFixtures', 'localFixtures', 'visitorResults', 'localResults', 'latest', 'upcoming'}

        # includes `fifaranking` and `uefaranking` are not available for some of the teams of season 6361
        missing_includes = {'fifaranking', 'uefaranking'}
        expected = {'name', 'twitter', 'logo_path', 'country_id', 'legacy_id', 'venue_id', 'founded', 'id',
                    'national_team', 'country'}
        teams = soccer_api.teams(season_id=6361, includes=tuple(includes))

        assert len(teams) == 16
        assert teams[0]['country']['name'] == 'Denmark'

        for team in teams:
            assert expected | includes - missing_includes <= set(team.keys())

    def test_team(self, soccer_api):
        includes = {
            'country', 'squad', 'coach', 'transfers', 'sidelined', 'stats', 'venue', 'fifaranking', 'uefaranking',
            'visitorFixtures', 'localFixtures', 'visitorResults', 'localResults', 'latest', 'upcoming'
        }

        # includes `fifaranking` is not available for team with ID 85
        known_missing_includes = {'fifaranking'}
        expected = {'name', 'twitter', 'logo_path', 'country_id', 'legacy_id', 'venue_id', 'founded', 'id',
                    'national_team', 'country'}
        team = soccer_api.team(team_id=85, includes=tuple(includes))

        missing = (expected | includes) - set(team.keys()) - known_missing_includes
        assert missing == set()

    def test_team_stats(self, soccer_api):
        expected = {
            'avg_first_goal_conceded', 'avg_first_goal_scored', 'avg_goals_per_game_conceded',
            'avg_goals_per_game_scored', 'clean_sheet', 'draw', 'failed_to_score', 'goals_against',
            'goals_for', 'lost', 'scoring_minutes', 'season_id', 'team_id', 'win',
            'stage_id'
        }

        team_stats = soccer_api.team_stats(team_id=85)
        for season_stats in team_stats:
            assert expected == set(season_stats.keys())

    def test_top_scorers(self, soccer_api):
        includes = {'goalscorers.player', 'goalscorers.team', 'assistscorers.player', 'assistscorers.team',
                    'cardscorers.player', 'cardscorers.team'}

        top_scorers = soccer_api.top_scorers(season_id=6361, includes=tuple(includes))
        expected = {'assistscorers', 'cardscorers', 'current_round_id', 'current_stage_id', 'goalscorers', 'id',
                    'is_current_season', 'league_id', 'name'}

        assert expected == set(top_scorers.keys())

        for cardscorer in top_scorers['cardscorers']:
            assert {'player', 'team', 'team_id', 'player_id'} <= set(cardscorer.keys())

        for goalscorer in top_scorers['goalscorers']:
            assert {'player', 'team', 'team_id', 'player_id'} <= set(goalscorer.keys())

        for assistscorer in top_scorers['assistscorers']:
            assert {'player', 'team', 'team_id', 'player_id'} <= set(assistscorer.keys())

    def test_venue(self, soccer_api):
        expected = {'address', 'capacity', 'city', 'id', 'image_path', 'name', 'surface', 'coordinates'}
        assert expected == set(soccer_api.venue(venue_id=206).keys())

    def test_rounds(self, soccer_api):
        includes = {'fixtures', 'results', 'season', 'league'}
        expected = {'name', 'league_id', 'end', 'season_id', 'stage_id', 'id', 'start'}

        for rnd in soccer_api.rounds(season_id=6361, includes=tuple(includes)):
            assert expected | includes == set(rnd.keys())

    def test_round(self, soccer_api):
        includes = {'fixtures', 'results', 'season', 'league'}
        expected = {'name', 'league_id', 'end', 'season_id', 'stage_id', 'id', 'start'}

        rnd = soccer_api.round(round_id=127985, includes=tuple(includes))
        assert expected | includes == set(rnd.keys())

    def test_pre_match_odds(self, soccer_api):
        odds = soccer_api.pre_match_odds(fixture_id=1625164)

        for odd in odds:
            assert set(odd.keys()) == {'id', 'bookmaker', 'name'}
            for bookmaker in odd['bookmaker']:
                assert set(bookmaker.keys()) == {'id', 'odds', 'name'}

    def test_in_play_odds(self, soccer_api):
        try:
            odds = soccer_api.in_play_odds(fixture_id=1625164)
        except sportmonks.base.SportMonksAPIError as e:
            if str(e) == "Insufficient Privileges! Your current plan doesn't allow access to this section!":
                return
            else:
                raise

        for odd in odds:
            assert set(odd.keys()) == {'id', 'bookmaker', 'name'}
            for bookmaker in odd['bookmaker']:
                assert set(bookmaker.keys()) == {'id', 'odds', 'name'}

    def test_player(self, soccer_api):
        expected_keys = {
            'birthcountry', 'birthdate', 'birthplace', 'common_name', 'country_id', 'firstname', 'fullname', 'height',
            'image_path', 'lastname', 'nationality', 'player_id', 'position_id', 'team_id', 'weight'
        }
        assert set(soccer_api.player(player_id=579).keys()) == expected_keys

    def test_bookmakers(self, soccer_api):
        expected_keys = {'id', 'logo', 'name'}
        for bookmaker in soccer_api.bookmakers():
            assert set(bookmaker.keys()) == expected_keys

    def test_bookmaker(self, soccer_api):
        expected = {'id': 5, 'logo': None, 'name': '5 Dimes'}
        assert soccer_api.bookmaker(bookmaker_id=5) == expected

    def test_squad(self, soccer_api):
        expected_keys = {
            'appearences', 'assists', 'goals', 'injured', 'lineups', 'minutes', 'number', 'player_id', 'position_id',
            'redcards', 'substitute_in', 'substitute_out', 'substitutes_on_bench', 'yellowcards', 'yellowred'
        }

        squad = soccer_api.squad(season_id=6361, team_id=85)
        for squad_member in squad:
            assert expected_keys <= set(squad_member.keys())

    def test_meta(self, soccer_api):
        meta = soccer_api.meta()
        assert {'subscription', 'plan', 'sports'} == set(meta.keys())

    def test_season_stages(self, soccer_api):
        # The includes league, season, and results do not work, despite what SportMonks documents.
        season_stages = soccer_api.season_stages(season_id=6361, includes=('fixtures',))
        expected_keys = {'id', 'name', 'league_id', 'season_id', 'type', 'fixtures'}

        for stage in season_stages:
            assert expected_keys == set(stage.keys())

    def test_stage(self, soccer_api):
        # The includes league, season, and results do not work, despite what SportMonks documents.
        stage = soccer_api.stage(stage_id=48048, includes=('fixtures',))
        expected_keys = {'id', 'name', 'league_id', 'season_id', 'type', 'fixtures'}
        assert expected_keys == set(stage.keys())

    def test_fixture_tv_stations(self, soccer_api):
        tv_stations = soccer_api.fixture_tv_stations(fixture_id=218832)
        expected = [
            {'fixture_id': 218832, 'tvstation': 'TV3 Sport (Swe)'},
            {'fixture_id': 218832, 'tvstation': 'TV3+'},
            {'fixture_id': 218832, 'tvstation': 'ViaPlay (Den)'}
        ]

        assert expected == tv_stations

    def test_season_venues(self, soccer_api):
        venues = soccer_api.season_venues(season_id=6361)
        expected_keys = {'address', 'capacity', 'city', 'id', 'image_path', 'name', 'surface', 'coordinates'}

        for venue in venues:
            assert expected_keys == set(venue.keys())

    def test_markets(self, soccer_api):
        assert {'id', 'name'} == set([el for m in soccer_api.markets() for el in m.keys()])

    def test_market(self, soccer_api):
        assert {'id': 1, 'name': '3Way Result'} == soccer_api.market(market_id=1)

    def test_coach(self, soccer_api):

        # No access allowed while on Free Plan
        try:
            coach = soccer_api.coach(coach_id=523962)
        except sportmonks.base.SportMonksAPIError as e:
            if str(e) == "Insufficient Privileges! Your current plan doesn't allow access to this section!":
                return
            else:
                raise
