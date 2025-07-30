"""
MIT License

Copyright (c) 2025 Omkaar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import annotations

from datetime import datetime
from time import sleep
from typing import Callable, Optional, List
from threading import Thread

from requests import Session

from .endpoints import BASE_URL
from .exceptions import UncallableError
from .models import ClashRoyaleObject, ClanLog, ClanList, ClanMemberList, BattleLog, TournamentList, ChallengeList
from .utils import _fetch, _difference


class Client:

    """
    A class that represents a client.

    :param token: The Clash Royale API token.
    :type token: :class:`str`
    :param session: The session to use.
    :type session: Optional[:class:`requests.Session`]
    """

    def __init__(self, token: str, *, session: Optional[Session] = None) -> None:
        self.session = session if session else Session()
        self.session.headers = {"Authorization": f"Bearer {token}"}

    def get_war_log(self, tag: str, *, limit: Optional[int] = None, after: Optional[str] = None, before: Optional[str] = None) -> ClanLog:
        """
        .. warn::

            This API endpoint has been temporarily disabled, possibilities to bring it back are being investigated.

        Gets the clan's war log.

        :param tag: The tag of the clan.
        :type tag: :class:`str`
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}clans/{tag}/warlog", self, {"limit": limit, "after": after, "before": before})
        return ClanLog(data)

    def search_clans(self, *, name: Optional[str] = None, location_id: Optional[str] = None, min_members: Optional[int] = None, max_members: Optional[int] = None, min_score: Optional[int] = None, max_score: Optional[int] = None, limit: Optional[int] = None, after: Optional[str] = None, before: Optional[str] = None) -> ClanList:
        """
        Searches for clans based on various criteria.

        :param name: The name of the clan.
        :type name: Optional[:class:`str`]
        :param location_id: The ID of the location.
        :type location_id: Optional[:class:`str`]
        :param min_members: The minimum number of members in the clan.
        :type min_members: Optional[:class:`int`]
        :param max_members: The maximum number of members in the clan.
        :type max_members: Optional[:class:`int`]
        :param min_score: The minimum score of the clan.
        :type min_score: Optional[:class:`int`]
        :param max_score: The maximum score of the clan.
        :type max_score: Optional[:class:`int`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.

        .. note::

            At least one filtering parameter must be provided.
        """
        if not any([name, location_id, min_members, max_members, min_score, max_score, limit, after, before]):
            raise ValueError("at least one filtering parameter must be provided.")
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}clans", self, {
            "name": name,
            "locationId": location_id,
            "minMembers": min_members,
            "maxMembers": max_members,
            "minScore": min_score,
            "maxScore": max_score,
            "limit": limit,
            "after": after,
            "before": before
        })
        return ClanList(data)

    def get_river_race_log(self, tag: str, *, before: Optional[str] = None, after: Optional[str] = None, limit: Optional[int] = None) -> ClanLog:
        """
        Gets the clan's river race log.

        :param tag: The tag of the clan.
        :type tag: :class:`str`
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}clans/{tag}/riverracelog", self, {"limit": limit, "after": after, "before": before})
        return ClanLog(data)

    def get_clan(self, tag: str) -> ClashRoyaleObject:
        """
        Gets information about a single clan.

        :param tag: The tag of the clan.
        :type tag: :class:`str`
        """
        data = _fetch(f"{BASE_URL}clans/{tag}", self)
        clan = ClashRoyaleObject(data)
        clan.member_list = ClanMemberList(data.pop("memberList", []))
        return clan

    def get_clan_members(self, tag: str, *, limit: Optional[int] = None, after: Optional[str] = None, before: Optional[str] = None) -> ClanMemberList:
        """
        Gets the members of a clan.

        :param tag: The tag of the clan.
        :type tag: :class:`str`
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}clans/{tag}/members", self, {"limit": limit, "after": after, "before": before})
        return ClanMemberList(data)

    def get_current_river_race(self, tag: str) -> ClashRoyaleObject:
        """
        Gets the current river race for a clan.
        :param tag: The tag of the clan.
        """
        data = _fetch(f"{BASE_URL}clans/{tag}/currentriverrace", self)
        return ClashRoyaleObject(data)

    def get_player(self, tag: str) -> ClashRoyaleObject:
        """
        Gets information about a single player.

        :param tag: The tag of the player.
        :type tag: :class:`str`
        """
        data = _fetch(f"{BASE_URL}players/{tag}", self)
        return ClashRoyaleObject(data)

    def get_upcoming_chests(self, tag: str) -> List[ClashRoyaleObject]:
        """
        Gets the upcoming chests for a player.

        :param tag: The tag of the player.
        :type tag: :class:`str`
        """
        data = _fetch(f"{BASE_URL}players/{tag}/upcomingchests", self)
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_player_battlelog(self, tag: str) -> BattleLog:
        """
        Gets the recent battles of a player.

        :param tag: The tag of the player.
        :type tag: :class:`str`
        """
        data = _fetch(f"{BASE_URL}players/{tag}/battlelog", self)
        return BattleLog(data)

    def get_cards(self, *, limit: Optional[int] = None, after: Optional[str] = None, before: Optional[str] = None) -> List[ClashRoyaleObject]:
        """
        Gets a list of cards.

        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}cards", self, {"limit": limit, "after": after, "before": before})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def search_tournaments(self, *, name: Optional[str] = None, limit: Optional[int] = None, after: Optional[str] = None, before: Optional[str] = None) -> TournamentList:
        """
        Searches for tournaments based on various criteria.

        :param name: The name of the tournament.
        :type name: Optional[:class:`str`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.

        .. note::

            At least one filtering parameter must be provided.
        """
        if not any([name, limit, after, before]):
            raise ValueError("at least one filtering parameter must be provided.")
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}tournaments", self, {
            "name": name,
            "limit": limit,
            "after": after,
            "before": before
        })
        return TournamentList(data)

    def get_tournament(self, tag: str) -> ClashRoyaleObject:
        """
        Gets information about a single tournament.

        :param tag: The tag of the tournament.
        :type tag: :class:`str`
        """
        data = _fetch(f"{BASE_URL}tournaments/{tag}", self)
        tournament = ClashRoyaleObject(data)
        tournament.created_time = data.pop("createdTime")
        return tournament

    def get_clan_rankings(self, location_id: str, *, before: Optional[str] = None, after: Optional[str] = None, limit: Optional[int] = None) -> List[ClashRoyaleObject]:
        """
        Gets global clan rankings or those for a specific location.

        :param location_id: The location identifier, or 'global' for global rankings.
        :type location_id: :class:`str`
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}locations/{location_id}/rankings/clans", self, {"before": before, "after": after, "limit": limit})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_player_rankings(self, location_id: int, *, before: Optional[str] = None, after: Optional[str] = None, limit: Optional[int] = None) -> List[ClashRoyaleObject]:
        """
        Gets global player rankings or those for a specific location.

        :param location_id: The location identifier, or 'global' for global rankings.
        :type location_id: :class:`int`
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}locations/{location_id}/rankings/players", self, {"before": before, "after": after, "limit": limit})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_clan_war_rankings(self, location_id: str, *, before: Optional[str] = None, after: Optional[str] = None, limit: Optional[int] = None) -> List[ClashRoyaleObject]:
        """
        Gets global clan war rankings or those for a specific location.

        :param location_id: The location identifier, or 'global' for global rankings.
        :type location_id: :class:`str`
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}locations/{location_id}/rankings/clanwars", self, {"before": before, "after": after, "limit": limit})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_path_of_legends_rankings(self, *, season_id: str, location_id: str, before: Optional[str] = None, after: Optional[str] = None, limit: Optional[int] = None) -> List[ClashRoyaleObject]:
        """
        Gets global Path of Legends rankings.

        :param season_id: The identifier of the season.
        :type season_id: :class:`str`
        :param location_id: The location identifier, or 'global' for global rankings.
        :type location_id: :class:`str`

        .. note::

            Exactly one of ``location_id`` or ``season_id`` must be provided.

        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if (not season_id and not location_id) or (season_id and location_id):
            raise ValueError("exactly one of 'season_id' or 'location_id' must be provided.")
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        if season_id:
            data = _fetch(f"{BASE_URL}locations/global/pathoflegend/{season_id}/rankings/players", self, {"before": before, "after": after, "limit": limit})
            return [ClashRoyaleObject(item) for item in data["items"]]
        data = _fetch(f"{BASE_URL}locations/{location_id}/pathoflegend/players", self, {"before": before, "after": after, "limit": limit})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_season(self, season_id: str) -> ClashRoyaleObject:
        """
        Gets information about a specific season.

        :param season_id: The identifier of the season.
        :type season_id: :class:`str`
        """
        data = _fetch(f"{BASE_URL}locations/global/seasons/{season_id}", self)
        if "id" in data.keys():
            raise ValueError("the season with the given ID does not exist.")
        season = ClashRoyaleObject(data)
        season.end_time = datetime.strptime(data.pop("endTime"), "%Y%m%dT%H%M%S.%fZ")
        return season

    def get_season_rankings(self, month: str, *, before: Optional[str] = None, after: Optional[str] = None, limit: Optional[int] = None) -> List[ClashRoyaleObject]:
        """
        Gets the rankings for a specific season.

        :param month: The month of the season.
        :type month: :class:`str`

        .. note::
            The month is in the format 'YYYY-MM', e.g., '2018-05'.

        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}locations/global/seasons/{month}/rankings/players", self, {"before": before, "after": after, "limit": limit})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_all_season_months(self) -> List[int]:
        """
        Gets a list of all available season months.
        """
        data = _fetch(f"{BASE_URL}locations/global/seasons", self)
        return [item["id"] for item in data["items"]]

    def get_all_locations(self, *, limit: Optional[int] = None, after: Optional[str] = None, before: Optional[str] = None) -> List[ClashRoyaleObject]:
        """
        Gets a list of all locations.

        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}locations", self, {"limit": limit, "after": after, "before": before})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_location(self, location_id: str) -> ClashRoyaleObject:
        """
        Gets information about a specific location.

        :param location_id: The identifier of the location.
        :type location_id: :class:`str`
        """
        data = _fetch(f"{BASE_URL}locations/{location_id}", self)
        return ClashRoyaleObject(data)

    def get_tournament_rankings(self, tag: str, *, before: Optional[str] = None, after: Optional[str] = None, limit: Optional[int] = None) -> List[ClashRoyaleObject]:
        """
        Gets the rankings for a specific tournament.

        :param tag: The tag of the tournament.
        :type tag: :class:`str`
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}tournaments/{tag}/rankings", self, {"before": before, "after": after, "limit": limit})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_challenges(self) -> ChallengeList:
        """
        Gets a list of current and upcoming challenges.
        """
        data = _fetch(f"{BASE_URL}challenges", self)
        return ChallengeList(data)

    def get_leaderboard(self, leaderboard_id: int, *, before: Optional[str] = None, after: Optional[str] = None, limit: Optional[int] = None) -> List[ClashRoyaleObject]:
        """
        Gets the leaderboard for a specific leaderboard ID.

        :param leaderboard_id: The ID of the leaderboard.
        :type leaderboard_id: :class:`int`
        :param before: The marker to return items before.
        :type before: Optional[:class:`str`]
        :param after: The marker to return items after.
        :type after: Optional[:class:`str`]
        :param limit: The maximum number of items to be returned.
        :type limit: Optional[:class:`int`]

        .. note::

            If both ``before`` and ``after`` are provided, a ``ValueError`` is raised.
        """
        if before and after:
            raise ValueError("both 'before' and 'after' cannot be provided.")
        data = _fetch(f"{BASE_URL}leaderboard/{leaderboard_id}", self, {"before": before, "after": after, "limit": limit})
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_all_leaderboards(self) -> List[ClashRoyaleObject]:
        """
        Gets a list of all available leaderboards.
        """
        data = _fetch(f"{BASE_URL}leaderboards", self)
        return [ClashRoyaleObject(item) for item in data["items"]]

    def get_all_global_tournaments(self) -> TournamentList:
        """
        Gets a list of all global tournaments.
        """
        data = _fetch(f"{BASE_URL}globaltournaments", self)
        return TournamentList(data)

    def on_member_join(self, tag: str, *, repeat_duration: Optional[float] = 60):
        """
        Event that is called when a member joins a clan.

        :param tag: The tag of the clan.
        :type tag: :class:`str`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_clan_members(tag))
                    sleep(repeat_duration)
                    current = list(self.get_clan_members(tag))
                    difference = _difference(current, cache)
                    if len(difference) >= 1:
                        function(members = difference)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_member_leave(self, tag: str, repeat_duration: Optional[float] = 60):
        """
        Event that is called when a member leaves a club.

        :param tag: The tag of the club.
        :type tag: :class:`str`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_clan_members(tag))
                    sleep(repeat_duration)
                    current = list(self.get_clan_members(tag))
                    difference = _difference(cache, current)
                    if len(difference) >= 1:
                        function(members = difference)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_battlelog_update(self, tag: str, repeat_duration: Optional[float] = 60):
        """
        Event that is called when a player's battlelog is updated.

        :param tag: The tag of the player.
        :type tag: :class:`str`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_player_battlelog(tag))
                    sleep(repeat_duration)
                    current = list(self.get_player_battlelog(tag))
                    difference = _difference(current, cache)
                    if len(difference) >= 1:
                        function(battles = difference)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_war_log_update(self, tag: str, repeat_duration: Optional[float] = 60):
        """
        Event that is called when a clan's war log is updated.

        .. warn::

            The ``get_war_log`` endpoint has been temporarily disabled, possibilities to bring it back are being investigated.

        :param tag: The tag of the clan.
        :type tag: :class:`str`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_war_log(tag))
                    sleep(repeat_duration)
                    current = list(self.get_war_log(tag))
                    difference = _difference(current, cache)
                    if len(difference) >= 1:
                        function(wars = difference)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_river_race_log_update(self, tag: str, repeat_duration: Optional[float] = 60):
        """
        Event that is called when a clan's river race log is updated.

        :param tag: The tag of the clan.
        :type tag: :class:`str`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_river_race_log(tag))
                    sleep(repeat_duration)
                    current = list(self.get_river_race_log(tag))
                    difference = _difference(current, cache)
                    if len(difference) >= 1:
                        function(river_races = difference)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_clan_rankings_update(self, location_id: str, repeat_duration: Optional[float] = 60):
        """
        Event that is called when the clan rankings for a specific location are updated.

        :param location_id: The ID of the location.
        :type location_id: :class:`str`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_clan_rankings(location_id))
                    sleep(repeat_duration)
                    current = list(self.get_clan_rankings(location_id))
                    difference_1 = _difference(current, cache)
                    difference_2 = _difference(cache, current)
                    if len(difference_1) >= 1 or len(difference_2) >= 1:
                        function(added_clans = difference_1, removed_clans = difference_2)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_player_rankings_update(self, location_id: int, repeat_duration: Optional[float] = 60):
        """
        Event that is called when the player rankings for a specific location are updated.

        :param location_id: The ID of the location.
        :type location_id: :class:`int`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_player_rankings(location_id))
                    sleep(repeat_duration)
                    current = list(self.get_player_rankings(location_id))
                    difference_1 = _difference(current, cache)
                    difference_2 = _difference(cache, current)
                    if len(difference_1) >= 1 or len(difference_2) >= 1:
                        function(added_players = difference_1, removed_players = difference_2)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_clan_war_rankings_update(self, location_id: str, repeat_duration: Optional[float] = 60):
        """
        Event that is called when the clan war rankings for a specific location are updated.

        :param location_id: The ID of the location.
        :type location_id: :class:`str`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_clan_war_rankings(location_id))
                    sleep(repeat_duration)
                    current = list(self.get_clan_war_rankings(location_id))
                    difference_1 = _difference(current, cache)
                    difference_2 = _difference(cache, current)
                    if len(difference_1) >= 1 or len(difference_2) >= 1:
                        function(added_clans = difference_1, removed_clans = difference_2)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_path_of_legends_rankings_update(self, repeat_duration: Optional[float] = 60, *, season_id: Optional[str] = None, location_id: Optional[str] = None):
        """
        Event that is called when the Path of Legends rankings are updated.

        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        :param season_id: The ID of the season.
        :type season_id: Optional[:class:`str`]
        :param location_id: The ID of the location.
        :type location_id: Optional[:class:`str`]

        .. note::

            Exactly one of ``season_id`` or ``location_id`` must be provided.
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_path_of_legends_rankings(season_id = season_id, location_id = location_id))
                    sleep(repeat_duration)
                    current = list(self.get_path_of_legends_rankings(season_id = season_id, location_id = location_id))
                    difference_1 = _difference(current, cache)
                    difference_2 = _difference(cache, current)
                    if len(difference_1) >= 1 or len(difference_2) >= 1:
                        function(added_players = difference_1, removed_players = difference_2)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_season_rankings_update(self, month: str, repeat_duration: Optional[float] = 60):
        """
        Event that is called when the season rankings are updated.

        :param month: The month of the season.
        :type month: :class:`str`

        .. note::
            The month is in the format 'YYYY-MM', e.g., '2018-05'.

        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_season_rankings(month))
                    sleep(repeat_duration)
                    current = list(self.get_season_rankings(month))
                    difference_1 = _difference(current, cache)
                    difference_2 = _difference(cache, current)
                    if len(difference_1) >= 1 or len(difference_2) >= 1:
                        function(added_players = difference_1, removed_players = difference_2)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_tournament_rankings_update(self, tag: str, repeat_duration: Optional[float] = 60):
        """
        Event that is called when the tournament rankings are updated.

        :param tag: The tag of the tournament.
        :type tag: :class:`str`
        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_tournament_rankings(tag))
                    sleep(repeat_duration)
                    current = list(self.get_tournament_rankings(tag))
                    difference_1 = _difference(current, cache)
                    difference_2 = _difference(cache, current)
                    if len(difference_1) >= 1 or len(difference_2) >= 1:
                        function(added_players = difference_1, removed_players = difference_2)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator

    def on_challenges_update(self, repeat_duration: Optional[float] = 60):
        """
        Event that is called when the challenges are updated.

        :param repeat_duration: The time to sleep for between every check.
        :type repeat_duration: Optional[:class:`float`]
        """
        def decorator(function: Callable):

            def process():
                while True:
                    cache = list(self.get_challenges())
                    sleep(repeat_duration)
                    current = list(self.get_challenges())
                    difference_1 = _difference(current, cache)
                    difference_2 = _difference(cache, current)
                    if len(difference_1) >= 1 or len(difference_2) >= 1:
                        function(added_challenges = difference_1, removed_challenges = difference_2)

            thread = Thread(target = process)
            thread.start()

            def error():
                raise UncallableError("functions used for events are not callable.")

            return error

        return decorator
