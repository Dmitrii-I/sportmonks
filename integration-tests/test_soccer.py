"""Integration tests of the `soccer` module.

The dictionaries returned by the SportMonks endpoints contain two types of keys: non-includes keys and includes keys. In
our tests we assume that non-includes keys are always present. The includes-keys may be missing, even after explicitly
requesting them. SportMonks does not return `None` for requested includes if they are not available, these includes are
simply missing in the response.

When testing, we request includes from endpoints that have them available. We do not test nested includes because then
the number of requested includes increases quickly and consequently the request processing becomes noticeably slow.
"""

from sys import stdout
from datetime import date
import logging
import sportmonks_v2._base


logging.basicConfig(stream=stdout, level=logging.INFO)


def test_includes_param_can_be_any_iterable(soccer_api):
    """Test that parameter `includes` can be any iterable."""
    iterables = [['countries'], {'countries'}, ('countries',), 'countries']
    assert all(map(lambda x: soccer_api.continent_by_id(1, iterables[0]) == soccer_api.continent_by_id(1, x),
                   iterables[1:]))


def test_all_continents(soccer_api):
    """Test `all_continents` method."""
    for continent in soccer_api.all_continents(includes=('countries',)):
        assert {'name', 'id', 'countries'} == set(continent.keys())


def test_continent_by_id(soccer_api):
    """Test `continent_by_id` method."""
    europe = soccer_api.continent_by_id(continent_id=1, includes=('countries',))
    assert {'name', 'id', 'countries'} == set(europe.keys())


def test_all_countries(soccer_api):
    """Test `all_countries` method.

    SportMonks returns some countries without any continent. Adjust the test for this.
    """
    for country in soccer_api.all_countries(includes=('continent', 'leagues')):

        # Following countries have no continent associated with them:
        countries_without_continent = {99474, 190324, 1442002, 1884978, 3499960, 8151924, 11311331,
                                       12444275, 14534056, 14566098, 14566636, 15288356, 15629849, 25293454, 32396817,
                                       32533155, 34319255}

        expected = {'name', 'id', 'extra', 'continent', 'leagues'}

        if country['id'] in countries_without_continent:
            assert expected - {'continent'} == set(country.keys())
        else:
            assert expected == set(country.keys())


def test_country_by_id(soccer_api):
    """Test `country_by_id` method."""
    poland = soccer_api.country_by_id(country_id=2, includes=('continent', 'leagues'))

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


def test_all_leagues(soccer_api):
    """Test `all_leagues` method."""
    leagues = soccer_api.all_leagues(includes=('country', 'season', 'seasons'))
    expected = {'country_id', 'coverage', 'current_round_id', 'current_season_id', 'current_stage_id', 'id',
                'is_cup', 'legacy_id', 'live_standings', 'name', 'country', 'season', 'seasons', 'logo_path'}

    for league in leagues:
        assert expected == set(league.keys())


def test_league_by_id(soccer_api):
    """Test `league_by_id` method."""
    includes = {'country', 'season', 'seasons'}
    premiership = soccer_api.league_by_id(league_id=501, includes=tuple(includes))

    expected = {'country_id', 'coverage', 'current_round_id', 'current_season_id', 'current_stage_id', 'id',
                'is_cup', 'legacy_id', 'live_standings', 'name', 'logo_path'}

    assert expected | includes == set(premiership.keys())


def test_all_seasons(soccer_api):
    """Test `all_seasons` method."""
    includes = ('league', 'stages', 'rounds', 'fixtures', 'upcoming', 'results', 'groups')
    seasons = soccer_api.all_seasons(includes=includes)

    for season in seasons:
        assert set(includes) - {'fixtures'} <= set(season.keys())


def test_season_by_id(soccer_api):
    """Test `season_by_id` method."""
    includes = ('league', 'stages', 'rounds', 'fixtures', 'upcoming', 'results', 'groups')
    season = soccer_api.season_by_id(season_id=12919, includes=includes)

    assert season['name'] == '2018/2019'
    assert season['league_id'] == 271
    assert set(includes) <= set(season.keys())


def test_season_results(soccer_api):
    """Test `season_results` method."""
    includes = ['localTeam', 'visitorTeam', 'substitutions', 'goals', 'cards', 'other', 'corners', 'lineup', 'bench',
                'sidelined', 'stats', 'comments', 'tvstations', 'highlights', 'league', 'season', 'round', 'stage',
                'referee', 'events', 'venue', 'odds', 'flatOdds', 'inplay', 'localCoach', 'visitorCoach', 'group',
                'trends']

    expected = {'id', 'league_id', 'season_id', 'stage_id', 'round_id', 'group_id', 'aggregate_id', 'venue_id',
                'referee_id', 'localteam_id', 'visitorteam_id', 'winner_team_id', 'weather_report', 'commentaries',
                'attendance', 'pitch', 'winning_odds_calculated', 'formations', 'scores', 'time', 'coaches',
                'standings',
                'assistants', 'leg', 'colors', 'deleted', 'localTeam', 'visitorTeam', 'substitutions', 'goals', 'cards',
                'other', 'corners', 'lineup', 'bench', 'sidelined', 'stats', 'comments', 'tvstations', 'highlights',
                'league', 'season', 'events', 'odds', 'inplay', 'flatOdds', 'trends'}

    season_results = soccer_api.season_results(season_id=759, includes=includes)
    for result in season_results:
        assert expected <= set(result.keys())


def test_fixtures_between(soccer_api):
    """Test `fixtures_between` method."""
    fixtures_1 = soccer_api.fixtures_between(date(2018, 1, 10), date(2018, 2, 10), league_ids=[501, 271])
    fixtures_2 = soccer_api.fixtures_between(date(2018, 1, 10), date(2018, 2, 10), league_ids=[])
    fixtures_3 = soccer_api.fixtures_between(date(2018, 1, 10), date(2018, 2, 10))
    assert len(fixtures_1) == 25
    assert len(fixtures_2) == 25
    assert len(fixtures_3) == 25

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
    fixtures = soccer_api.fixtures_between(date(2018, 1, 10), date(2018, 2, 10), includes, [271])

    for fixture in fixtures:
        assert set(includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())


def test_fixtures_between_by_team_id(soccer_api):
    """Test `fixtures_between_by_team_id` method."""
    expected = {'id', 'league_id', 'season_id', 'stage_id', 'round_id', 'group_id', 'aggregate_id', 'venue_id',
                'referee_id', 'localteam_id', 'visitorteam_id', 'winner_team_id', 'weather_report', 'commentaries',
                'attendance', 'pitch', 'winning_odds_calculated', 'formations', 'scores', 'time', 'coaches',
                'standings', 'assistants', 'leg', 'colors', 'deleted', 'localTeam', 'visitorTeam', 'substitutions',
                'goals', 'cards', 'other', 'corners', 'lineup', 'bench', 'sidelined', 'stats', 'comments', 'tvstations',
                'highlights', 'league', 'season', 'stage', 'referee', 'events', 'venue', 'odds', 'flatOdds',
                'localCoach', 'visitorCoach'}

    # Omit includes `inplay` and `trends` because they are not available for fixtures from 2018-01-01 through
    # 2018-04-01 for team with ID 85.
    includes = ('localTeam', 'visitorTeam', 'substitutions', 'goals', 'cards', 'other', 'corners', 'lineup', 'bench',
                'sidelined', 'stats', 'comments', 'tvstations', 'highlights', 'league', 'season', 'round', 'stage',
                'referee', 'events', 'venue', 'flatOdds', 'localCoach', 'visitorCoach', 'odds')

    fixtures = soccer_api.fixtures_between_by_team_id(start_date=date(2018, 1, 1), end_date=date(2018, 4, 1),
                                                      team_id=85, includes=includes)

    assert len(fixtures) == 7

    for fixture in fixtures:
        assert set(includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())


def test_fixtures_today(soccer_api):
    """Test `fixtures_today` method.

    The fixtures returned by `fixtures_today` depend on the time of running this test. Therefore, we cannot
    know which fixtures will be returned or whether any fixture at all will be returned. This non-deterministic
    return value means we cannot know what includes will be attached to each returned fixture if we request all of
    them. Therefore we request a limited set of includes, one which we assume is available for any fixture.
    """
    essential_includes = ('localTeam', 'visitorTeam', 'league', 'season', 'stage')
    fixtures = soccer_api.fixtures_today(includes=essential_includes)
    assert isinstance(fixtures, list)

    expected = {'id', 'league_id', 'season_id', 'stage_id', 'round_id', 'group_id', 'aggregate_id', 'venue_id',
                'referee_id', 'localteam_id', 'visitorteam_id', 'winner_team_id', 'weather_report', 'commentaries',
                'attendance', 'pitch', 'winning_odds_calculated', 'formations', 'scores', 'time', 'coaches',
                'standings', 'assistants', 'leg', 'colors', 'deleted', 'localTeam', 'visitorTeam', 'league', 'season',
                'stage'}

    for fixture in fixtures:
        assert set(essential_includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())


def test_fixtures_in_play(soccer_api):
    """Test `fixtures_in_play` method.

    The fixtures returned by `fixtures_in_play` depend on the time of running this test. Therefore, we cannot
    know which fixtures will be returned or whether any fixture at all will be returned. This non-deterministic
    return value means we cannot know what includes will be attached to each returned fixture if we request all of
    them. Therefore we request a limited set of includes, one which we assume is available for any fixture.
    """
    essential_includes = ('localTeam', 'visitorTeam', 'league', 'season', 'stage')
    fixtures = soccer_api.fixtures_in_play(includes=essential_includes)
    assert isinstance(fixtures, list)

    expected = {'id', 'league_id', 'season_id', 'stage_id', 'round_id', 'group_id', 'aggregate_id', 'venue_id',
                'referee_id', 'localteam_id', 'visitorteam_id', 'winner_team_id', 'weather_report', 'commentaries',
                'attendance', 'pitch', 'winning_odds_calculated', 'formations', 'scores', 'time', 'coaches',
                'standings', 'assistants', 'leg', 'colors', 'deleted', 'localTeam', 'visitorTeam', 'league', 'season',
                'stage'}

    for fixture in fixtures:
        assert set(essential_includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())


def test_fixture_by_id(soccer_api):
    """Test `fixture_by_id` method."""
    # `inplay` and `trends` includes not available for fixture ID 1625164
    includes = ('localTeam', 'visitorTeam', 'substitutions', 'goals', 'cards', 'other', 'corners', 'lineup', 'bench',
                'sidelined', 'stats', 'comments', 'tvstations', 'highlights', 'league', 'season', 'round', 'stage',
                'referee', 'events', 'venue', 'flatOdds', 'localCoach', 'visitorCoach', 'odds')

    expected = {
        'aggregate_id', 'attendance', 'coaches', 'commentaries', 'deleted', 'formations', 'group_id', 'id',
        'league_id', 'localteam_id', 'pitch', 'referee_id', 'round_id', 'scores', 'season_id', 'stage_id',
        'standings', 'time', 'venue_id', 'visitorteam_id', 'weather_report', 'winning_odds_calculated'
    }

    fixture = soccer_api.fixture_by_id(fixture_id=1625164, includes=includes)

    assert set(includes) <= set(fixture.keys())
    assert expected <= set(fixture.keys())


def test_commentaries_by_fixture_id(soccer_api):
    """Test `commentaries_by_fixture_id` method."""
    expected = {'comment', 'extra_minute', 'fixture_id', 'goal', 'important', 'minute', 'order'}
    commentaries = soccer_api.commentaries_by_fixture_id(1871916)

    for comment in commentaries:
        assert expected == set(comment.keys())


def test_all_video_highlights(soccer_api):
    """Test `all_video_highlights` method."""
    highlights = soccer_api.all_video_highlights(includes=('fixture',))
    expected = {'created_at', 'fixture_id', 'fixture', 'location'}
    highlights_without_fixture_include = {10324789, 10324789, 10324402}

    for hl in highlights:
        assert set(hl.keys()) == expected or set(hl.keys()) == expected - {'fixture'}


def test_video_highlights_by_fixture_id(soccer_api):
    """Test `video_highlights_by_fixture_id` method."""
    fixture_highlights = soccer_api.video_highlights_by_fixture_id(fixture_id=218832)
    expected = {'created_at', 'fixture_id', 'fixture', 'location'}

    for hl in fixture_highlights:
        assert set(hl.keys()) == expected or set(hl.keys()) == expected - {'fixture'}


def test_head_to_head_by_team_ids(soccer_api):
    """Test `head_to_head_by_team_ids` method.

    The fixtures returned by `head_to_head_fixtures` depend on the time of running this test. Therefore, we
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

    essential_includes = ('localTeam', 'visitorTeam', 'league', 'season', 'round', 'stage')

    fixtures = soccer_api.head_to_head_by_team_ids(team_ids={85, 86}, includes=essential_includes)

    for fixture in fixtures:
        assert set(essential_includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())


def test_standings(soccer_api):
    """Test `standings` method."""
    includes = ('team', 'league', 'season', 'round', 'stage')
    standings = soccer_api.standings_by_season_id(season_id=12919, includes=includes)

    assert len(standings) == 3

    expected = {'away', 'group_id', 'group_name', 'home', 'overall', 'points', 'position', 'recent_form', 'result',
                'status', 'team_id', 'team_name', 'total', 'round_name', 'round_id'}

    missing_includes = {'round'}

    for standings_season_stage in standings:
        for standing_entry in standings_season_stage['standings']:
            assert expected - missing_includes <= set(standing_entry.keys()) or expected <= set(standing_entry.keys())


def test_live_standings_by_season_id(soccer_api):
    includes = ('team', 'league', 'season', 'round', 'stage')
    try:
        standings = soccer_api.live_standings_by_season_id(season_id=12919, includes=includes)
    except sportmonks_v2._base.SportMonksAPIError as e:
        if str(e) == "Not authorized. Indicates you're attempting to request data which is not accessible " \
                     "from your plan.":
            return
        raise

    expected = {'away', 'group_id', 'group_name', 'home', 'overall', 'points', 'position', 'recent_form', 'result',
                'status', 'team_id', 'team_name', 'total', 'round_name', 'round_id'}

    missing_includes = {'round'}

    for standings_season_stage in standings:
        for standing_entry in standings_season_stage['standings']:
            assert expected - missing_includes <= set(standing_entry.keys()) or expected <= set(standing_entry.keys())


def test_teams_by_season_id(soccer_api):
    """Test `teams_by_season_id` method."""
    includes = {'country', 'squad', 'coach', 'transfers', 'sidelined', 'stats', 'venue', 'fifaranking', 'uefaranking',
                'visitorFixtures', 'localFixtures', 'visitorResults', 'localResults', 'latest', 'upcoming'}

    # includes `fifaranking` and `uefaranking` are not available for some of the teams of season 6361
    missing_includes = {'fifaranking', 'uefaranking'}
    expected = {'name', 'twitter', 'logo_path', 'country_id', 'legacy_id', 'venue_id', 'founded', 'id',
                'national_team', 'country'}
    teams = soccer_api.teams_by_season_id(season_id=12919, includes=tuple(includes))

    assert len(teams) == 14
    assert teams[0]['country']['name'] == 'Denmark'

    for team in teams:
        assert expected | includes - missing_includes <= set(team.keys())


def test_team_by_id(soccer_api):
    """Test `team_by_id` method."""
    includes = {
        'country', 'squad', 'coach', 'transfers', 'sidelined', 'stats', 'venue', 'fifaranking', 'uefaranking',
        'visitorFixtures', 'localFixtures', 'visitorResults', 'localResults', 'latest', 'upcoming'
    }

    # includes `fifaranking` is not available for team with ID 85
    known_missing_includes = {'fifaranking'}
    expected = {'name', 'twitter', 'logo_path', 'country_id', 'legacy_id', 'venue_id', 'founded', 'id',
                'national_team', 'country'}
    team = soccer_api.team_by_id(team_id=85, includes=includes)

    missing = (expected | includes) - set(team.keys()) - known_missing_includes
    assert missing == set()


def test_team_by_legacy_id(soccer_api):
    """Test `team_by_legacy_id` method."""
    includes = {
        'country', 'squad', 'coach', 'transfers', 'sidelined', 'stats', 'venue', 'fifaranking', 'uefaranking',
        'visitorFixtures', 'localFixtures', 'visitorResults', 'localResults', 'latest', 'upcoming'
    }

    # includes `fifaranking` is not available for team with ID 146
    known_missing_includes = {'fifaranking'}
    expected = {'name', 'twitter', 'logo_path', 'country_id', 'legacy_id', 'venue_id', 'founded', 'id',
                'national_team', 'country'}
    legacy_team = soccer_api.team_by_legacy_id(legacy_team_id=146, includes=includes)

    missing = (expected | includes) - set(legacy_team.keys()) - known_missing_includes
    assert missing == set()


def test_team_stats(soccer_api):
    """Test `team_stats` method."""
    expected = {
        'avg_first_goal_conceded', 'avg_fouls_per_game', 'win', 'avg_ball_possession_percentage',
        'avg_shots_off_target_per_game', 'lost', 'avg_goals_per_game_conceded', 'offsides', 'dangerous_attacks',
        'clean_sheet', 'attacks', 'avg_shots_on_target_per_game', 'shots_on_target', 'stage_id', 'draw', 'season_id',
        'team_id', 'shots_off_target', 'yellowcards', 'fouls', 'goals_against', 'failed_to_score',
        'avg_goals_per_game_scored', 'redcards', 'goals_for', 'scoring_minutes', 'shots_blocked',
        'avg_first_goal_scored'
    }

    team_stats = soccer_api.team_stats(team_id=85)
    for season_stats in team_stats:
        assert expected == set(season_stats.keys())


def test_season_stats(soccer_api):
    """Test `season_stats` method."""
    expected = {'current_round_id', 'current_stage_id', 'stats', 'id', 'league_id', 'name', 'is_current_season'}
    expected_stats = {'league_id', 'season_assist_topscorer_id', 'team_with_most_goals_per_match_id',
                      'number_of_yellowcards', 'number_of_redcards', 'number_of_goals', 'avg_goals_per_match',
                      'team_with_most_conceded_goals_id', 'season_id', 'goals_scored_minutes',
                      'goalkeeper_most_cleansheets_number', 'goalkeeper_most_cleansheets_id', 'goal_line',
                      'season_topscorer_id', 'updated_at', 'avg_yellowredcards_per_match', 'number_of_matches',
                      'btts', 'team_most_cleansheets_id', 'avg_redcards_per_match', 'team_with_most_goals_id',
                      'matches_both_teams_scored', 'avg_yellowcards_per_match', 'number_of_clubs', 'id',
                      'team_most_cleansheets_number', 'number_of_yellowredcards', 'goal_scored_every_minutes',
                      'number_of_matches_played'}

    season_stats = soccer_api.season_stats(season_id=12919)

    assert expected == set(season_stats.keys())
    assert expected_stats == set(season_stats['stats'].keys())


def test_topscorers_by_season_id(soccer_api):
    """Test `topscorers_by_season_id` method."""
    includes = {'player', 'team'}

    top_scorers = soccer_api.topscorers_by_season_id(season_id=12919, includes=tuple(includes))
    expected = {'assistscorers', 'cardscorers', 'current_round_id', 'current_stage_id', 'goalscorers', 'id',
                'is_current_season', 'league_id', 'name'}

    assert expected == set(top_scorers.keys())

    for cardscorer in top_scorers['cardscorers']:
        assert {'player', 'team', 'team_id', 'player_id'} <= set(cardscorer.keys())

    for goalscorer in top_scorers['goalscorers']:
        assert {'player', 'team', 'team_id', 'player_id'} <= set(goalscorer.keys())

    for assistscorer in top_scorers['assistscorers']:
        assert {'player', 'team', 'team_id', 'player_id'} <= set(assistscorer.keys())


def test_venue_by_id(soccer_api):
    """Test `venue_by_id` method."""
    expected = {'address', 'capacity', 'city', 'id', 'image_path', 'name', 'surface', 'coordinates'}
    assert expected == set(soccer_api.venue_by_id(venue_id=206).keys())


def test_rounds_by_season_id(soccer_api):
    """Test `rounds_by_season_id` method."""
    includes = {'fixtures', 'results', 'season', 'league'}
    expected = {'name', 'league_id', 'end', 'season_id', 'stage_id', 'id', 'start'}

    for rnd in soccer_api.rounds_by_season_id(season_id=12919, includes=tuple(includes)):
        assert expected | includes == set(rnd.keys())


def test_round_by_id(soccer_api):
    """Test `round_by_id` method."""
    includes = {'fixtures', 'results', 'season', 'league'}
    expected = {'name', 'league_id', 'end', 'season_id', 'stage_id', 'id', 'start'}

    rnd = soccer_api.round_by_id(round_id=127985, includes=tuple(includes))
    assert expected | includes == set(rnd.keys())


def test_pre_match_odds(soccer_api):
    """Test `pre_match_odds` method."""
    odds = soccer_api.pre_match_odds(fixture_id=1625164)

    for odd in odds:
        assert set(odd.keys()) == {'id', 'bookmaker', 'name', 'suspended'}
        for bookmaker in odd['bookmaker']:
            assert set(bookmaker.keys()) == {'id', 'odds', 'name'}


def test_in_play_odds(soccer_api):
    """Test `in_play_odds` method."""
    try:
        odds = soccer_api.in_play_odds(fixture_id=1625164)
    except sportmonks_v2._base.SportMonksAPIError as e:
        if str(e) == "Not authorized. Indicates you're attempting to request data which is not accessible " \
                     "from your plan.":
            return
        raise

    for odd in odds:
        assert set(odd.keys()) == {'id', 'bookmaker', 'name'}
        for bookmaker in odd['bookmaker']:
            assert set(bookmaker.keys()) == {'id', 'odds', 'name'}


def test_player_by_id(soccer_api):
    """Test `player_by_id` method."""
    expected_keys = {
        'birthcountry', 'birthdate', 'birthplace', 'common_name', 'country_id', 'firstname', 'fullname', 'height',
        'image_path', 'lastname', 'nationality', 'player_id', 'position_id', 'team_id', 'weight'
    }
    assert set(soccer_api.player_by_id(player_id=579).keys()) == expected_keys


def test_all_bookmakers(soccer_api):
    """Test `all_bookmakers` method."""
    expected_keys = {'id', 'logo', 'name'}
    for bookmaker in soccer_api.all_bookmakers():
        assert set(bookmaker.keys()) == expected_keys


def test_bookmaker_by_id(soccer_api):
    """Test `bookmaker` method."""
    expected = {'id': 5, 'logo': None, 'name': '5 Dimes'}
    assert soccer_api.bookmaker_by_id(bookmaker_id=5) == expected


def test_squad_by_season_and_team_id(soccer_api):
    """Test `squad_by_season_and_team_id` method."""
    expected_keys = {
        'appearences', 'assists', 'goals', 'injured', 'lineups', 'minutes', 'number', 'player_id', 'position_id',
        'redcards', 'substitute_in', 'substitute_out', 'substitutes_on_bench', 'yellowcards', 'yellowred'
    }

    squad = soccer_api.squad_by_season_and_team_id(season_id=12919, team_id=85)
    for squad_member in squad:
        assert expected_keys <= set(squad_member.keys())


def test_meta(soccer_api):
    """Test `meta` method."""
    meta = soccer_api.meta()
    assert {'subscription', 'plan', 'sports'} == set(meta.keys())


def test_stages_by_season_id(soccer_api):
    """Test `stages_by_season_id` method."""
    # The includes league, season, and results do not work, despite what SportMonks documents.
    season_stages = soccer_api.stages_by_season_id(season_id=12919, includes=('fixtures',))
    expected_keys = {'id', 'name', 'league_id', 'season_id', 'type', 'fixtures'}

    for stage in season_stages:
        assert expected_keys == set(stage.keys())


def test_stage_by_id(soccer_api):
    """Test `stage_by_id` method."""
    # The includes league, season, and results do not work, despite what SportMonks documents.
    stage = soccer_api.stage_by_id(stage_id=48048, includes=('fixtures',))
    expected_keys = {'id', 'name', 'league_id', 'season_id', 'type', 'fixtures'}
    assert expected_keys == set(stage.keys())


def test_tv_stations_by_fixture_id(soccer_api):
    """Test `tv_stations_by_fixture_id` method."""
    tv_stations = soccer_api.tv_stations_by_fixture_id(fixture_id=218832)
    expected = [
        {'fixture_id': 218832, 'tvstation': 'TV3 Sport (Swe)'},
        {'fixture_id': 218832, 'tvstation': 'TV3+'},
        {'fixture_id': 218832, 'tvstation': 'ViaPlay (Den)'}
    ]

    assert expected == tv_stations


def test_venues_by_season_id(soccer_api):
    """Test `venues_by_season_id` method."""
    venues = soccer_api.venues_by_season_id(season_id=6361)
    expected_keys = {'address', 'capacity', 'city', 'id', 'image_path', 'name', 'surface', 'coordinates'}

    for venue in venues:
        assert expected_keys == set(venue.keys())


def test_all_markets(soccer_api):
    """Test `all_markets` method."""
    assert {'id', 'name'} == {el for m in soccer_api.all_markets() for el in m.keys()}


def test_market_by_id(soccer_api):
    """Test `market_by_id` method."""
    assert {'id': 1, 'name': '3Way Result'} == soccer_api.market_by_id(market_id=1)


def test_coach_by_id(soccer_api):
    """Test `coach_by_id` method."""
    try:
        coach = soccer_api.coach_by_id(coach_id=523962)
    except sportmonks_v2._base.SportMonksAPIError as e:
        if str(e) == "Not authorized. Indicates you're attempting to request data which is not accessible " \
                     "from your plan.":
            return
        raise

    assert coach['coach_id'] == 523962


