"""The `soccer` module implements the `SportMonks soccer HTTP API v2.0.
<https://www.sportmonks.com/sports/soccer/documentation>`__
"""


from os.path import join
from logging import getLogger
from typing import Dict, List, Iterable, Union, Any, Optional
from datetime import date
from requests import get
from sportmonks import _base
from sportmonks._types import Response, Includes


log = getLogger(__name__)


class SoccerApiV2(_base.BaseApiV2):
    """The ``SoccerApiV2`` class provides SportMonks soccer API client."""

    def __init__(self, api_token: str) -> None:
        """Parameter ``api_token`` is the API token from the SportMonks profile web page."""
        log.info('Initialize soccer API client')
        super().__init__(base_url='https://soccer.sportmonks.com/api/v2.0', api_token=api_token)
        log.info('Client initialized, metadata=%s', self.meta())

    def meta(self) -> Dict[str, Any]:
        """Return meta data that includes your SportMonks plan, subscription, and available sports."""
        # Meta data does not have a dedicated endpoint. Use a data endpoint with fast response and extract meta from its
        # response.
        url = join(self.base_url, 'continents')
        log.info('Fetch metadata')
        raw_response = get(url=url, params=self._base_params, headers=self._base_headers)
        response = raw_response.json()
        return response['meta']

    def bookmaker(self, bookmaker_id: int) -> Response:
        """Return a bookmaker."""
        log.info('Fetch bookmaker (id=%s)', bookmaker_id)
        return self._http_get(endpoint=join('bookmakers', str(bookmaker_id)))

    def bookmakers(self) -> Response:
        """Return all bookmakers."""
        log.info('Fetch all bookmakers')
        bookmakers = self._http_get(endpoint='bookmakers')
        log.info('Fetched %s bookmakers', len(bookmakers))
        return bookmakers

    def continent(self, continent_id: int, includes: Includes = None) -> Response:
        """Return a continent.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `countries`.
        """
        log.info('Fetch continent (id=%s), includes=%s', continent_id, includes)
        return self._http_get(endpoint=join('continents', str(continent_id)), includes=includes)

    def continents(self, includes: Includes = None) -> Response:
        """Return all continents.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `countries`.
        """
        log.info('Fetch all continents, includes=%s', includes)
        continents = self._http_get(endpoint='continents', includes=includes)
        log.info('Fetched %s continents', len(continents))
        return continents

    def country(self, country_id: int, includes: Includes = None) -> Response:
        """Return a country.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `continent`, `leagues`.
        """
        log.info('Fetch country (id=%s), includes=%s', country_id, includes)
        return self._http_get(endpoint=join('countries', str(country_id)), includes=includes)

    def countries(self, includes: Includes = None) -> Response:
        """Return all countries.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `continent`, `leagues`.
        """
        log.info('Fetch all countries, includes=%s', includes)
        countries = self._http_get(endpoint='countries', includes=includes)
        log.info('Fetched %s countries', len(countries))
        return countries

    def league(self, league_id: int, includes: Includes = None) -> Response:
        """Return a league.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `country`, `season`, `seasons`. The `season` include Return current season of the
        league. The `seasons` include Return all seasons of the league, including the current season.
        """
        log.info('Fetch league (id=%s), includes=%s', league_id, includes)
        return self._http_get(endpoint=join('leagues', str(league_id)), includes=includes)

    def leagues(self, includes: Includes = None) -> Response:
        """Return all leagues.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `country`, `season`, `seasons`. The `season` include Return current season of the
        league. The `seasons` include Return all seasons of the league, including the current season.
        """
        log.info('Fetch all leagues, includes=%s', includes)
        leagues = self._http_get(endpoint='leagues', includes=includes)
        log.info('Fetched %s leagues', len(leagues))
        return leagues

    def season(self, season_id: int, includes: Includes = None) -> Response:
        """Return a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `league`, `stages`, `rounds`, `fixtures`, `upcoming`, `results`, `groups`.
        """
        log.info('Fetch season (id=%s), includes=%s', season_id, includes)
        return self._http_get(endpoint=join('seasons', str(season_id)), includes=includes)

    def seasons(self, includes: Includes = None) -> Response:
        """Return all seasons.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `league`, `stages`, `rounds`, `fixtures`, `upcoming`, `results`, `groups`.
        """
        log.info('Fetch all seasons, includes=%s', includes)
        seasons = self._http_get(endpoint='seasons', includes=includes)
        log.info('Fetched %s seasons', len(seasons))
        return seasons

    def season_results(self, season_id: int, includes: Includes = None) -> Response:
        """Return completed fixtures of a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 1.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """
        includes = ['results'] + ['results.' + inc for inc in includes or []]
        log.info('Fetch results of a season (id=%s), includes=%s', season_id, includes)

        season_results = self.season(season_id=season_id, includes=includes)

        if isinstance(season_results, dict):
            season_results = season_results['results']
        else:
            raise TypeError('Expected `dict`, got `%s`' % type(season_results))

        log.info('Fetched %s results', len(season_results))
        return season_results

    def fixtures(self, start_date: date, end_date: date, league_ids: Optional[List[int]] = None,
                 includes: Includes = None) -> Response:
        """Return fixtures between ``start_date`` and ``end_date``. The dates are inclusive.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """
        endpoint = join('fixtures', 'between', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        log.info('Fetch fixtures, from=%s, until=%s, league ids=%s, includes=%s', start_date, end_date,
                 league_ids or 'all leagues', includes)
        fixtures = self._http_get(endpoint=endpoint, params={'leagues': league_ids or []}, includes=includes)
        log.info('Fetched %s fixtures', len(fixtures))
        return fixtures

    def fixture(self, fixture_id: int, includes: Includes = None) -> Response:
        """Return a fixture.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """
        log.info('Fetch fixture (id=%s), includes=%s', fixture_id, includes)
        return self._http_get(endpoint=join('fixtures', str(fixture_id)), includes=includes)

    def team_fixtures(self, start_date: date, end_date: date, team_id: int, includes: Includes = None) -> Response:
        """Return fixtures between ``start_date`` and ``end_date`` for a team specified by ``team_id``.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """
        endpoint = join('fixtures', 'between', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                        str(team_id))
        log.info('Fetch fixtures of a team (id=%s), from=%s, until=%s, includes=%s', start_date, end_date, team_id,
                 includes)
        team_fixtures = self._http_get(endpoint=endpoint, includes=includes)
        log.info('Fetched %s team fixtures', len(team_fixtures))
        return team_fixtures

    def fixtures_today(self, league_ids: Optional[List[int]] = None, includes: Includes = None) -> Response:
        """Return today's fixtures, played and to be played.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """
        log.info('Fetch today\'s fixtures, league ids=%s, includes=%s', league_ids or 'all leagues', includes)
        fixtures_today = self._http_get(endpoint='livescores', params={'leagues': league_ids or []}, includes=includes)
        log.info('Fetched %s fixtures', len(fixtures_today))
        return fixtures_today

    def fixtures_in_play(self, includes: Includes = None) -> Response:
        """Return in-play fixtures.

        Note that in-play is defined by SportMonks as fixtures currently played, plus fixtures that will begin within
        45 minutes, and fixtures that ended less than 30 minutes ago.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """
        log.info('Fetch fixtures in play, includes=%s', (includes,))
        fixtures_in_play = self._http_get(endpoint=join('livescores', 'now'), includes=includes)
        log.info('Fetched %s fixtures in play', len(fixtures_in_play))
        return fixtures_in_play

    def head_to_head_fixtures(self, team_ids: Iterable[int], includes: Includes = None) -> Response:
        """Return all head-to-head fixtures of two teams specified by ``team_ids``.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are:	`localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `lineup`, `bench`,
        `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`, `stage`, `referee`, `events`,
        `venue`, `trends`.
        """
        team_ids = list(team_ids)
        endpoint = join('head2head', str(team_ids[0]), str(team_ids[1]))
        log.info('Fetch head-to-head fixtures of two teams (ids=%s), includes=%s', team_ids, includes)
        head_to_head_fixtures = self._http_get(endpoint=endpoint, includes=includes)
        log.info('Fetched %s head-to-head fixtures', len(head_to_head_fixtures))
        return head_to_head_fixtures

    def commentaries(self, fixture_id: int) -> Response:
        """Return commentaries of a fixture.

        Not all fixtures have commentaries. If a fixture has no commentaries then an empty list is returned.
        """
        log.info('Fetch commentaries of a fixture (id=%s)', fixture_id)
        commentaries = self._http_get(endpoint=join('commentaries', 'fixture', str(fixture_id)))
        log.info('Fetched %s commentaries', len(commentaries))
        return commentaries

    def video_highlights(self, fixture_id: Optional[int] = None, includes: Includes = None) -> Response:
        """Return links to video highlights of all fixtures or of a fixture specified by ``fixture_id``.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixture`.
        """
        endpoint = 'highlights'

        if fixture_id:
            endpoint = join('highlights', 'fixture', str(fixture_id))
            log.info('Fetch video highlights of a fixture (id=%s), includes=%s', fixture_id, includes)
        else:
            log.info('Fetch video highlights of all fixtures, includes=%s', includes)

        video_highlights = self._http_get(endpoint=endpoint, includes=includes)
        log.info('Fetched %s video highlights', len(video_highlights))
        return video_highlights

    def standings(self, season_id: int, live: bool = False, group_id: Optional[int] = None,
                  includes: Includes = None) -> Response:
        """Return standings of a season.

        Parameter ``live`` specifies whether standings should also take into account in-play fixtures.

        Parameter ``group_id`` specifies for which group to return the standings. Groups are found in tournaments like
        the FIFA World Cup (e.g. Group A has group ID 185).

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `team`, `league`, `season`, `round`, `stage`.
        """
        endpoint = join('standings', 'season', str(season_id))

        if live:
            endpoint = join('standings', 'season', 'live', str(season_id))

        log.info('Fetch standings, season id=%s, live=%s, group id=%s, includes=%s', season_id, live,
                 group_id or 'all groups', includes)
        standings = self._http_get(endpoint=endpoint, includes=includes, params={'group_id': group_id})
        log.info('Fetched %s standings', len(standings))
        return standings

    def teams(self, season_id: int, includes: Includes = None) -> Response:
        """Return all teams that played during a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `country`, `squad`, `coach`, `transfers`, `sidelined`, `stats`, `venue`, `fifaranking`,
        `uefaranking`, `visitorFixtures`, `localFixtures`, `visitorResults`, `localResults`, `latest`, `upcoming`.
        """
        log.info('Fetch teams of a season (id=%s), includes=%s', season_id, includes)
        teams = self._http_get(endpoint=join('teams', 'season', str(season_id)), includes=includes)
        log.info('Fetched %s teams', len(teams))
        return teams

    def team(self, team_id: int, includes: Includes = None) -> Response:
        """Return a team.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `country`, `squad`, `coach`, `transfers`, `sidelined`, `stats`, `venue`, `fifaranking`,
        `uefaranking`, `visitorFixtures`, `localFixtures`, `visitorResults`, `localResults`, `latest`, `upcoming`.
        """
        log.info('Fetch team (id=%s), includes=%s', team_id, includes)
        return self._http_get(endpoint=join('teams', str(team_id)), includes=includes)

    def team_stats(self, team_id: int) -> Response:
        """Return stats of a team."""
        log.info('Fetch stats of a team (id=%s)', team_id)
        team_stats = self._http_get(endpoint=join('teams', str(team_id)), includes=['stats'])
        if isinstance(team_stats, dict):
            return team_stats['stats']
        else:
            raise TypeError('Expected `dict`, got `%s`' % type(team_stats))

    def top_scorers(self, season_id: int, includes: Includes = None) -> Response:
        """Return top scorers of a season.

        Three types of top scorers are returned: most goals, most assists, and most cards.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `goalscorers.player`, `goalscorers.team` `cardscorers.player`, `cardscorers.team`,
        `assistscorers.player`, `assistscorers.team`.
        """
        endpoint = join('topscorers', 'season', str(season_id))
        log.info('Fetch top scorers of a season (id=%s), includes=%s', season_id, includes)
        return self._http_get(endpoint=endpoint, includes=includes)

    def venue(self, venue_id: int) -> Response:
        """Return a venue."""
        log.info('Fetch venue (id=%s)', venue_id)
        return self._http_get(endpoint=join('venues', str(venue_id)))

    def rounds(self, season_id: int, includes: Includes = None) -> Response:
        """Return rounds of a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """
        log.info('Fetch rounds of a season (id=%s), includes=%s', season_id, includes)
        rounds = self._http_get(endpoint=join('rounds', 'season', str(season_id)), includes=includes)
        log.info('Fetched %s rounds', len(rounds))
        return rounds

    def round(self, round_id: int, includes: Includes = None) -> Response:
        """Return a round.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """
        log.info('Fetch round (id=%s), includes=%s', round_id, includes)
        return self._http_get(endpoint=join('rounds', str(round_id)), includes=includes)

    def pre_match_odds(self, fixture_id: int) -> Response:
        """Return pre-match odds of a fixture."""
        log.info('Fetch pre-match, fixture id=%s', fixture_id)
        pre_match_odds = self._http_get(endpoint=join('odds', 'fixture', str(fixture_id)))
        log.info('Fetched %s pre-match odds', len(pre_match_odds))
        return pre_match_odds

    def in_play_odds(self, fixture_id: int) -> Response:
        """Return in-play odds of a fixture."""
        log.info('Fetch in-play odds, fixture id=%s', fixture_id)
        in_play_odds = self._http_get(endpoint=join('odds', 'inplay', 'fixture', str(fixture_id)))
        log.info('Fetched %s in-play odds', len(in_play_odds))
        return in_play_odds

    def player(self, player_id: int) -> Response:
        """Return a player."""
        log.info('Fetch player, id=%s', player_id)
        return self._http_get(endpoint=join('players', str(player_id)))

    def squad(self, season_id: int, team_id: int, includes: Includes = None) -> Response:
        """Return a squad. A squad is a set of players that played for a team during a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `player`, `position`.
        """
        log.info('Fetch squad of a team (id=%s) during a season (id=%s), includes=%s', team_id, season_id, includes)
        squad = self._http_get(endpoint=join('squad', 'season', str(season_id), 'team', str(team_id)),
                               includes=includes)
        log.info('Fetched %s squad players', len(squad))
        return squad

    def stage(self, stage_id: int, includes: Includes = None) -> Response:
        """Return a stage.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """
        log.info('Fetch stage (id=%s), includes=%s', stage_id, includes)
        return self._http_get(endpoint=join('stages', str(stage_id)), includes=includes)

    def season_stages(self, season_id: int, includes: Includes = None) -> Response:
        """Return stages of a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """
        log.info('Fetch stages of a season (id=%s), includes=%s', season_id, includes)
        stages = self._http_get(endpoint=join('stages', 'season', str(season_id)), includes=includes)
        log.info('Fetched %s stages', len(stages))
        return stages

    def fixture_tv_stations(self, fixture_id: int) -> Response:
        """Return tv stations broadcasting specified fixture."""
        log.info('Fetch TV stations boradcasting a fixture (id=%s)', fixture_id)
        fixture_tv_stations = self._http_get(endpoint=join('tvstations', 'fixture', str(fixture_id)))
        log.info('Fetched %s TV stations', len(fixture_tv_stations))
        return fixture_tv_stations

    def season_venues(self, season_id: int) -> Response:
        """Return venues of specified season."""
        log.info('Fetch venues of a season (id=%s)', season_id)
        season_venues = self._http_get(endpoint=join('venues', 'season', str(season_id)))
        log.info('Fetched %s venues of a season', len(season_venues))
        return season_venues

    def markets(self) -> Response:
        """Return all betting markets, e.g. '3Way Result', 'Home/Away'."""
        log.info('Fetch all markets')
        markets = self._http_get(endpoint='markets')
        log.info('Fetched %s markets', len(markets))
        return markets

    def market(self, market_id: int) -> Response:
        """Return a market."""
        log.info('Fetch market (id=%s)', market_id)
        return self._http_get(endpoint=join('markets', str(market_id)))

    def coach(self, coach_id: int) -> Response:
        """Return a coach."""
        log.info('Fetch coach (id=%s)', coach_id)
        return self._http_get(endpoint=join('coaches', str(coach_id)))
