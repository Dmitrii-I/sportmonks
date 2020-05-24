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
from collections import defaultdict
import logging
import sportmonks._base


logging.basicConfig(stream=stdout, level=logging.INFO)


def test_includes_param_can_be_any_iterable(soccer_api):
    """Test that parameter `includes` can be any iterable."""
    iterables = [["countries"], {"countries"}, ("countries",), "countries"]
    assert all(map(lambda x: soccer_api.continent(1, iterables[0]) == soccer_api.continent(1, x), iterables[1:]))


def test_continents(soccer_api):
    """Test `continents` method."""
    for continent in soccer_api.continents(includes=("countries",)):
        assert {"name", "id", "countries"} == set(continent.keys())


def test_continent(soccer_api):
    """Test `continent` method."""
    europe = soccer_api.continent(continent_id=1, includes=("countries",))
    assert {"name", "id", "countries"} == set(europe.keys())


def test_countries(soccer_api):
    """Test `countries` method.

    SportMonks returns some countries without any continent. Adjust the test for this.
    """
    logging.info("Integration test `countries` method")
    countries = soccer_api.countries(includes=("continent", "leagues"))
    for country in countries:

        expected = {"name", "id", "extra", "continent", "leagues", "image_path"}
        actual = set(country.keys())

        logging.info(
            "country %s, extra keys: %s, missing keys: %s", country["id"], actual - expected, expected - actual
        )
        assert expected == actual


def test_country(soccer_api):
    """Test `country` method."""
    poland = soccer_api.country(country_id=2, includes=("continent", "leagues"))

    assert poland["name"] == "Poland"
    assert poland["id"] == 2
    assert poland["extra"]["continent"] == "Europe"
    assert poland["extra"]["flag"][0:10] == "<svg xmlns"
    assert poland["extra"]["iso"] == "POL"
    assert poland["extra"]["latitude"] == "52.147850036621094"
    assert poland["extra"]["longitude"] == "19.37775993347168"
    assert poland["extra"]["sub_region"] == "Eastern Europe"
    assert poland["extra"]["world_region"] == "EMEA"

    assert {"continent", "leagues"} <= set(poland.keys())


def test_leagues(soccer_api):
    """Test `leagues` method."""
    leagues = soccer_api.leagues(includes=("country", "season", "seasons"))
    expected = {
        "country_id",
        "coverage",
        "current_round_id",
        "current_season_id",
        "current_stage_id",
        "id",
        "is_cup",
        "legacy_id",
        "live_standings",
        "name",
        "country",
        "season",
        "seasons",
        "logo_path",
        "active",
        "type",
    }

    for league in leagues:
        actual = set(league.keys())

        if league["id"] in {513, 1659}:
            # This league is missing seasons include. Probably because of 'rona.
            assert (expected - {"season"}) == set(league.keys())
        else:
            logging.info(
                "League %s, extra keys: %s, missing keys: %s", league["id"], actual - expected, expected - actual
            )
            assert expected == set(league.keys())


def test_league(soccer_api):
    """Test `league` method."""
    includes = {"country", "season", "seasons"}
    premiership = soccer_api.league(league_id=501, includes=tuple(includes))

    expected = {
        "country_id",
        "coverage",
        "current_round_id",
        "current_season_id",
        "current_stage_id",
        "id",
        "is_cup",
        "legacy_id",
        "live_standings",
        "name",
        "logo_path",
        "active",
        "type",
    } | includes
    actual = set(premiership.keys())

    logging.info("extra keys: %s, missing keys: %s", actual - expected, expected - actual)
    assert expected == actual


def test_seasons(soccer_api):
    """Test `seasons` method."""
    includes = ("league", "stages", "rounds", "fixtures", "upcoming", "results", "groups")
    seasons = soccer_api.seasons(includes=includes)

    for season in seasons:
        assert set(includes) <= set(season.keys())


def test_season(soccer_api):
    """Test `season` method."""
    includes = ("league", "stages", "rounds", "fixtures", "upcoming", "results", "groups")
    season = soccer_api.season(season_id=6361, includes=includes)

    assert season["name"] == "2017/2018"
    assert season["league_id"] == 271
    assert set(includes) <= set(season.keys())


def test_season_results(soccer_api):
    """Test `season_results` method.

    As per [1], the valid includes for a fixture are: localTeam, visitorTeam, substitutions, goals, cards,
    other, corners, lineup, bench, sidelined, stats, comments, tvstations, highlights, league, season, round, stage,
    referee, events, venue, odds, flatOdds, inplay, localCoach, visitorCoach,group, trends. However, requesting all
    these includes at once results in an API error, therefore we break down this set into subsets, and test each
    subset.

    [1] https://www.sportmonks.com/products/soccer/docs/2.0/fixtures/18
    """
    # The `group` include is not applicable for season with ID 6361 because it is not a tournament-type season,
    # so it is omitted in this test.
    includes_tuples = [
        ("localTeam", "visitorTeam", "substitutions", "goals", "cards", "other", "corners", "lineup", "bench"),
        ("sidelined", "stats", "comments", "tvstations", "highlights", "league", "season", "round", "stage"),
        ("referee", "events", "venue", "flatOdds", "inplay", "localCoach", "visitorCoach", "trends"),
        ("odds",),
    ]

    expected_non_includes = {
        "aggregate_id",
        "attendance",
        "coaches",
        "commentaries",
        "deleted",
        "formations",
        "group_id",
        "id",
        "league_id",
        "localteam_id",
        "pitch",
        "referee_id",
        "round_id",
        "scores",
        "season_id",
        "stage_id",
        "standings",
        "time",
        "venue_id",
        "visitorteam_id",
        "weather_report",
        "winning_odds_calculated",
    }

    known_missing_includes = defaultdict(set)
    known_missing_includes.update(
        {
            1140241: {"round"},
            1140251: {"round"},
            1140270: {"round"},
            1140284: {"round"},
            1241158: {"round"},
            1241159: {"round"},
            1492895: {"round"},
            1281339: {"round", "stage", "venue"},
            1281341: {"round", "stage", "venue"},
            1281343: {"round", "stage", "venue"},
            1281346: {"round", "stage", "venue"},
            220294: {"referee", "localCoach", "visitorCoach"},
            220345: {"referee", "localCoach", "visitorCoach"},
            220386: {"referee", "localCoach", "visitorCoach"},
            220428: {"referee", "localCoach", "visitorCoach"},
            220481: {"referee", "localCoach", "visitorCoach"},
            220510: {"referee", "localCoach", "visitorCoach"},
            220547: {"referee", "localCoach", "visitorCoach"},
            220586: {"referee", "localCoach", "visitorCoach"},
            220624: {"referee", "localCoach", "visitorCoach"},
            220665: {"localCoach", "visitorCoach"},
            220702: {"localCoach", "visitorCoach"},
            220741: {"localCoach", "visitorCoach"},
            220774: {"localCoach", "visitorCoach"},
            220792: {"localCoach", "visitorCoach"},
            220802: {"localCoach", "visitorCoach"},
            220812: {"localCoach", "visitorCoach"},
            220822: {"localCoach", "visitorCoach"},
            220832: {"localCoach", "visitorCoach"},
            220842: {"localCoach", "visitorCoach"},
            220853: {"localCoach", "visitorCoach"},
            225987: {"visitorCoach"},
        }
    )

    for includes_tuple in includes_tuples:
        season_results = soccer_api.season_results(season_id=759, includes=includes_tuple)
        for result in season_results:

            missing_includes = (set(includes_tuple) - known_missing_includes[result["id"]]) - set(result.keys())
            assert missing_includes == set()

            assert expected_non_includes <= set(result.keys())


def test_fixtures(soccer_api):
    """Test `fixtures` method."""
    fixtures_1 = soccer_api.fixtures(date(2018, 1, 10), date(2018, 2, 10), [501, 271])
    fixtures_2 = soccer_api.fixtures(date(2018, 1, 10), date(2018, 2, 10), [])
    fixtures_3 = soccer_api.fixtures(date(2018, 1, 10), date(2018, 2, 10))
    assert len(fixtures_1) == 25
    assert len(fixtures_2) == 25
    assert len(fixtures_3) == 25

    expected = {
        "aggregate_id",
        "attendance",
        "coaches",
        "commentaries",
        "deleted",
        "formations",
        "group_id",
        "id",
        "league_id",
        "localteam_id",
        "pitch",
        "referee_id",
        "round_id",
        "scores",
        "season_id",
        "stage_id",
        "standings",
        "time",
        "venue_id",
        "visitorteam_id",
        "weather_report",
        "winning_odds_calculated",
    }

    # includes `odds`, `inplay`, and `trends` are not available for fixtures from 2018-01-10 through 2018-02-10 for
    # league with ID 271.
    includes = (
        "localTeam",
        "visitorTeam",
        "substitutions",
        "goals",
        "cards",
        "other",
        "corners",
        "lineup",
        "bench",
        "sidelined",
        "stats",
        "comments",
        "tvstations",
        "highlights",
        "league",
        "season",
        "round",
        "stage",
        "referee",
        "events",
        "venue",
        "flatOdds",
        "localCoach",
        "visitorCoach",
    )
    fixtures = soccer_api.fixtures(date(2018, 1, 10), date(2018, 2, 10), [271], includes=includes)

    for fixture in fixtures:
        assert set(includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())


def test_team_fixtures(soccer_api):
    """Test `team_fixtures` method."""
    expected = {
        "aggregate_id",
        "attendance",
        "coaches",
        "commentaries",
        "deleted",
        "formations",
        "group_id",
        "id",
        "league_id",
        "localteam_id",
        "pitch",
        "referee_id",
        "round_id",
        "scores",
        "season_id",
        "stage_id",
        "standings",
        "time",
        "venue_id",
        "visitorteam_id",
        "weather_report",
        "winning_odds_calculated",
    }

    # Omit includes `inplay` and `trends` because they are not available for fixtures from 2018-01-01 through
    # 2018-04-01 for team with ID 85.
    includes = (
        "localTeam",
        "visitorTeam",
        "substitutions",
        "goals",
        "cards",
        "other",
        "corners",
        "lineup",
        "bench",
        "sidelined",
        "stats",
        "comments",
        "tvstations",
        "highlights",
        "league",
        "season",
        "round",
        "stage",
        "referee",
        "events",
        "venue",
        "flatOdds",
        "localCoach",
        "visitorCoach",
        "odds",
    )

    fixtures = soccer_api.team_fixtures(
        start_date=date(2018, 1, 1), end_date=date(2018, 4, 1), team_id=85, includes=includes
    )

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
    essential_includes = ("localTeam", "visitorTeam", "league", "season", "round", "stage", "venue")
    fixtures = soccer_api.fixtures_today(includes=essential_includes)
    assert isinstance(fixtures, list)

    expected = {
        "aggregate_id",
        "attendance",
        "coaches",
        "commentaries",
        "deleted",
        "formations",
        "group_id",
        "id",
        "league_id",
        "localteam_id",
        "pitch",
        "referee_id",
        "round_id",
        "scores",
        "season_id",
        "stage_id",
        "standings",
        "time",
        "venue_id",
        "visitorteam_id",
        "weather_report",
        "winning_odds_calculated",
    }

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
    essential_includes = ("localTeam", "visitorTeam", "league", "season", "round", "stage", "venue")
    fixtures = soccer_api.fixtures_in_play(includes=essential_includes)
    assert isinstance(fixtures, list)

    expected = {
        "aggregate_id",
        "attendance",
        "coaches",
        "commentaries",
        "deleted",
        "formations",
        "group_id",
        "id",
        "league_id",
        "localteam_id",
        "pitch",
        "referee_id",
        "round_id",
        "scores",
        "season_id",
        "stage_id",
        "standings",
        "time",
        "venue_id",
        "visitorteam_id",
        "weather_report",
        "winning_odds_calculated",
    }

    for fixture in fixtures:
        assert set(essential_includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())


def test_fixture(soccer_api):
    """Test `fixture` method."""
    # `inplay` and `trends` includes not available for fixture ID 1625164
    includes = (
        "localTeam",
        "visitorTeam",
        "substitutions",
        "goals",
        "cards",
        "other",
        "corners",
        "lineup",
        "bench",
        "sidelined",
        "stats",
        "comments",
        "tvstations",
        "highlights",
        "league",
        "season",
        "round",
        "stage",
        "referee",
        "events",
        "venue",
        "flatOdds",
        "localCoach",
        "visitorCoach",
        "odds",
    )

    expected = {
        "aggregate_id",
        "attendance",
        "coaches",
        "commentaries",
        "deleted",
        "formations",
        "group_id",
        "id",
        "league_id",
        "localteam_id",
        "pitch",
        "referee_id",
        "round_id",
        "scores",
        "season_id",
        "stage_id",
        "standings",
        "time",
        "venue_id",
        "visitorteam_id",
        "weather_report",
        "winning_odds_calculated",
    }

    fixture = soccer_api.fixture(fixture_id=1625164, includes=includes)

    assert set(includes) <= set(fixture.keys())
    assert expected <= set(fixture.keys())


def test_commentaries(soccer_api):
    """Test `commentaries` method."""
    expected = {"comment", "extra_minute", "fixture_id", "goal", "important", "minute", "order"}
    commentaries = soccer_api.commentaries(1871916)

    for comment in commentaries:
        assert expected == set(comment.keys())


def test_video_highlights(soccer_api):
    """Test `video_highlights` method."""
    highlights = soccer_api.video_highlights(includes=("fixture",))
    highlights_without_fixture_include = {10324789, 10324789, 10324402, 1281343}

    for hl in highlights:
        expected = {"created_at", "fixture_id", "fixture", "location", "event_id", "type"}
        if hl["fixture_id"] in highlights_without_fixture_include:
            expected = expected - {"fixture"}

        actual = set(hl.keys())
        if actual != expected:
            logging.error(
                "Fixture ID %s, extra keys: %s, missing keys: %s",
                hl["fixture_id"],
                actual - expected,
                expected - actual,
            )
        assert expected == actual

    fixture_highlights = soccer_api.video_highlights(fixture_id=218832)
    for hl in fixture_highlights:
        expected = {"created_at", "fixture_id", "location", "event_id", "type"}
        actual = set(hl.keys())
        logging.info("highlights fixture 218832 extra keys: %s, missing keys: %s", actual - expected, expected - actual)
        assert expected == actual


def test_head_to_head_fixtures(soccer_api):
    """Test `head_to_head_fixtures` method.

    The fixtures returned by `head_to_head_fixtures` depend on the time of running this test. Therefore, we
    cannot know which fixtures will be returned or whether any fixture at all will be returned. This
    non-deterministic return value means we cannot know what includes will be attached to each returned fixture if
    we request all of them. Therefore we request a limited set of includes, one which we assume is available for
    any fixture.
    """
    expected = {
        "aggregate_id",
        "attendance",
        "coaches",
        "commentaries",
        "deleted",
        "formations",
        "group_id",
        "id",
        "league_id",
        "localteam_id",
        "pitch",
        "referee_id",
        "round_id",
        "scores",
        "season_id",
        "stage_id",
        "standings",
        "time",
        "venue_id",
        "visitorteam_id",
        "weather_report",
        "winning_odds_calculated",
    }

    essential_includes = ("localTeam", "visitorTeam", "league", "season", "round", "stage")

    fixtures = soccer_api.head_to_head_fixtures(team_ids={85, 86}, includes=essential_includes)

    for fixture in fixtures:
        assert set(essential_includes) <= set(fixture.keys())
        assert expected <= set(fixture.keys())


def test_standings(soccer_api):
    """Test `standings` method."""
    includes = ("team", "league", "season", "round", "stage")
    standings = soccer_api.standings(season_id=6361, includes=includes)

    expected = {
        "away",
        "group_id",
        "group_name",
        "home",
        "overall",
        "points",
        "position",
        "recent_form",
        "result",
        "status",
        "team_id",
        "team_name",
        "total",
        "round_name",
        "round_id",
    }

    for standings_season_stage in standings:
        for standing_entry in standings_season_stage["standings"]:
            actual = set(standing_entry.keys())
            logging.info("evaluate a standing entry")
            logging.info("extra keys: %s, missing keys: %s", actual - expected, expected - actual)
            assert expected == actual

    try:
        standings = soccer_api.standings(season_id=6361, live=True, includes=includes)
    except sportmonks._base.SportMonksAPIError as e:
        if str(e) == "Insufficient Privileges! Your current plan doesn't allow access to this section!":
            return
        raise

    for standings_season_stage in standings:
        for standing_entry in standings_season_stage["standings"]:
            assert expected == set(standing_entry.keys())


def test_teams(soccer_api):
    """Test `teams` method."""
    includes = {
        "country",
        "squad",
        "coach",
        "transfers",
        "sidelined",
        "stats",
        "venue",
        "fifaranking",
        "uefaranking",
        "visitorFixtures",
        "localFixtures",
        "visitorResults",
        "localResults",
        "latest",
        "upcoming",
    }

    # includes `fifaranking` and `uefaranking` are not available for some of the teams of season 6361
    missing_includes = {"fifaranking", "uefaranking"}
    expected = {
        "name",
        "twitter",
        "logo_path",
        "country_id",
        "legacy_id",
        "venue_id",
        "founded",
        "id",
        "national_team",
        "country",
    }
    teams = soccer_api.teams(season_id=6361, includes=tuple(includes))

    assert len(teams) == 14
    assert teams[0]["country"]["name"] == "Denmark"

    for team in teams:
        assert expected | includes - missing_includes <= set(team.keys())


def test_team(soccer_api):
    """Test `team` method."""
    includes = {
        "country",
        "squad",
        "coach",
        "transfers",
        "sidelined",
        "stats",
        "venue",
        "fifaranking",
        "uefaranking",
        "visitorFixtures",
        "localFixtures",
        "visitorResults",
        "localResults",
        "latest",
        "upcoming",
    }

    # includes `fifaranking` is not available for team with ID 85
    known_missing_includes = {"fifaranking"}
    expected = {
        "name",
        "twitter",
        "logo_path",
        "country_id",
        "legacy_id",
        "venue_id",
        "founded",
        "id",
        "national_team",
        "country",
    }
    team = soccer_api.team(team_id=85, includes=includes)

    missing = (expected | includes) - set(team.keys()) - known_missing_includes
    assert missing == set()


def test_team_stats(soccer_api):
    """Test `team_stats` method."""
    expected = {
        "offsides",
        "lost",
        "dangerous_attacks",
        "goals_for",
        "shots_blocked",
        "avg_shots_off_target_per_game",
        "avg_ball_possession_percentage",
        "clean_sheet",
        "stage_id",
        "team_id",
        "avg_shots_on_target_per_game",
        "redcards",
        "scoring_minutes",
        "avg_fouls_per_game",
        "avg_first_goal_scored",
        "avg_goals_per_game_conceded",
        "season_id",
        "failed_to_score",
        "yellowcards",
        "shots_on_target",
        "fouls",
        "goals_against",
        "avg_first_goal_conceded",
        "shots_off_target",
        "draw",
        "avg_goals_per_game_scored",
        "attacks",
        "win",
        "btts",
        "goal_line",
        "goals_conceded_minutes",
        "avg_corners",
        "total_corners",
    }

    team_stats = soccer_api.team_stats(team_id=85)
    for season_stats in team_stats:
        actual = set(season_stats.keys())
        logging.info("test season stats entry")
        logging.info("extra keys: %s, missing keys: %s", actual - expected, expected - actual)
        assert expected == actual


def test_top_scorers(soccer_api):
    """Test `top_scorers` method."""
    includes = {
        "goalscorers.player",
        "goalscorers.team",
        "assistscorers.player",
        "assistscorers.team",
        "cardscorers.player",
        "cardscorers.team",
    }

    top_scorers = soccer_api.top_scorers(season_id=6361, includes=tuple(includes))
    expected = {
        "assistscorers",
        "cardscorers",
        "current_round_id",
        "current_stage_id",
        "goalscorers",
        "id",
        "is_current_season",
        "league_id",
        "name",
    }

    assert expected == set(top_scorers.keys())

    for cardscorer in top_scorers["cardscorers"]:
        assert {"player", "team", "team_id", "player_id"} <= set(cardscorer.keys())

    for goalscorer in top_scorers["goalscorers"]:
        assert {"player", "team", "team_id", "player_id"} <= set(goalscorer.keys())

    for assistscorer in top_scorers["assistscorers"]:
        assert {"player", "team", "team_id", "player_id"} <= set(assistscorer.keys())


def test_aggregated_top_scorers(soccer_api):
    """Test `aggregated_top_scorers` method."""
    includes = {
        "aggregatedGoalscorers.player",
        "aggregatedGoalscorers.team",
        "aggregatedAssistscorers.player",
        "aggregatedAssistscorers.team",
        "aggregatedCardscorers.player",
        "aggregatedCardscorers.team",
    }

    aggregated_top_scorers = soccer_api.aggregated_top_scorers(season_id=6361, includes=tuple(includes))
    expected = {
        "aggregatedAssistscorers",
        "aggregatedCardscorers",
        "current_round_id",
        "current_stage_id",
        "aggregatedGoalscorers",
        "id",
        "is_current_season",
        "league_id",
        "name",
    }

    assert expected == set(aggregated_top_scorers.keys())

    for cardscorer in aggregated_top_scorers["aggregatedCardscorers"]:
        assert {"player", "team", "team_id", "player_id"} <= set(cardscorer.keys())

    for goalscorer in aggregated_top_scorers["aggregatedGoalscorers"]:
        assert {"player", "team", "team_id", "player_id"} <= set(goalscorer.keys())

    for assistscorer in aggregated_top_scorers["aggregatedAssistscorers"]:
        assert {"player", "team", "team_id", "player_id"} <= set(assistscorer.keys())


def test_venue(soccer_api):
    """Test `venue` method."""
    expected = {"address", "capacity", "city", "id", "image_path", "name", "surface", "coordinates"}
    assert expected == set(soccer_api.venue(venue_id=206).keys())


def test_rounds(soccer_api):
    """Test `rounds` method."""
    includes = {"fixtures", "results", "season", "league"}
    expected = {"name", "league_id", "end", "season_id", "stage_id", "id", "start"}

    for rnd in soccer_api.rounds(season_id=6361, includes=tuple(includes)):
        assert expected | includes == set(rnd.keys())


def test_round(soccer_api):
    """Test `round` method."""
    includes = {"fixtures", "results", "season", "league"}
    expected = {"name", "league_id", "end", "season_id", "stage_id", "id", "start"}

    rnd = soccer_api.round(round_id=127985, includes=tuple(includes))
    assert expected | includes == set(rnd.keys())


def test_pre_match_odds(soccer_api):
    """Test `pre_match_odds` method."""
    odds = soccer_api.pre_match_odds(fixture_id=1625164)

    for odd in odds:
        assert set(odd.keys()) == {"id", "bookmaker", "name", "suspended"}
        for bookmaker in odd["bookmaker"]:
            assert set(bookmaker.keys()) == {"id", "odds", "name"}


def test_in_play_odds(soccer_api):
    """Test `in_play_odds` method."""
    try:
        odds = soccer_api.in_play_odds(fixture_id=1625164)
    except sportmonks._base.SportMonksAPIError as e:
        if str(e) == "Insufficient Privileges! Your current plan doesn't allow access to this section!":
            return
        raise

    for odd in odds:
        assert set(odd.keys()) == {"id", "bookmaker", "name"}
        for bookmaker in odd["bookmaker"]:
            assert set(bookmaker.keys()) == {"id", "odds", "name"}


def test_player(soccer_api):
    """Test `player` method."""
    expected = {
        "birthcountry",
        "birthdate",
        "birthplace",
        "common_name",
        "country_id",
        "firstname",
        "fullname",
        "height",
        "image_path",
        "lastname",
        "nationality",
        "player_id",
        "position_id",
        "team_id",
        "weight",
        "team",
        "position",
        "stats",
        "trophies",
        "display_name",
    }

    actual = set(soccer_api.player(player_id=579, includes=["team", "position", "stats", "trophies"]).keys())
    logging.info("extra keys: %s, missing keys: %s", actual - expected, expected - actual)
    assert expected == actual


def test_bookmakers(soccer_api):
    """Test `bookmakers` method."""
    expected_keys = {"id", "logo", "name"}
    for bookmaker in soccer_api.bookmakers():
        assert set(bookmaker.keys()) == expected_keys


def test_bookmaker(soccer_api):
    """Test `bookmaker` method."""
    expected = {"id": 5, "logo": None, "name": "5 Dimes"}
    assert soccer_api.bookmaker(bookmaker_id=5) == expected


def test_squad(soccer_api):
    """Test `squad` method."""
    expected_keys = {
        "appearences",
        "assists",
        "goals",
        "injured",
        "lineups",
        "minutes",
        "number",
        "player_id",
        "position_id",
        "redcards",
        "substitute_in",
        "substitute_out",
        "substitutes_on_bench",
        "yellowcards",
        "yellowred",
    }

    squad = soccer_api.squad(season_id=6361, team_id=85)
    for squad_member in squad:
        assert expected_keys <= set(squad_member.keys())


def test_meta(soccer_api):
    """Test `meta` method."""
    meta = soccer_api.meta()
    assert {"subscription", "plan", "sports"} == set(meta.keys())


def test_season_stages(soccer_api):
    """Test `season_stages` method."""
    # The includes league, season, and results do not work, despite what SportMonks documents.
    season_stages = soccer_api.season_stages(season_id=6361, includes=("fixtures",))
    expected = {"id", "name", "league_id", "season_id", "type", "fixtures", "sort_order", "has_standings"}

    for stage in season_stages:
        actual = set(stage.keys())
        logging.info("stage %s, extra keys: %s, missing keys: %s", stage["id"], actual - expected, expected - actual)
        assert expected == actual


def test_stage(soccer_api):
    """Test `stage` method."""
    # The includes league, season, and results do not work, despite what SportMonks documents.
    stage = soccer_api.stage(stage_id=48048, includes=("fixtures",))
    expected = {"id", "name", "league_id", "season_id", "type", "fixtures", "sort_order", "has_standings"}
    actual = set(stage.keys())
    logging.info("stage 48048, extra keys: %s, missing keys %s", actual - expected, expected - actual)
    assert expected == actual


def test_fixture_tv_stations(soccer_api):
    """Test `fixture_tv_stations` method."""
    tv_stations = soccer_api.fixture_tv_stations(fixture_id=218832)
    expected = [
        {"fixture_id": 218832, "tvstation": "TV3 Sport (Swe)"},
        {"fixture_id": 218832, "tvstation": "TV3+"},
        {"fixture_id": 218832, "tvstation": "ViaPlay (Den)"},
    ]

    assert expected == tv_stations


def test_season_venues(soccer_api):
    """Test `season_venues` method."""
    venues = soccer_api.season_venues(season_id=6361)
    expected_keys = {"address", "capacity", "city", "id", "image_path", "name", "surface", "coordinates"}

    for venue in venues:
        assert expected_keys == set(venue.keys())


def test_markets(soccer_api):
    """Test `markets` method."""
    assert {"id", "name"} == {el for m in soccer_api.markets() for el in m.keys()}


def test_market(soccer_api):
    """Test `market` method."""
    assert {"id": 1, "name": "3Way Result"} == soccer_api.market(market_id=1)


def test_coach(soccer_api):
    """Test `coach` method."""
    try:
        coach = soccer_api.coach(coach_id=523962)
    except sportmonks._base.SportMonksAPIError as e:
        if str(e) == "Insufficient Privileges! Your current plan doesn't allow access to this section!":
            return
        raise

    assert coach["coach_id"] == 523962
