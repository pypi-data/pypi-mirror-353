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
from re import sub
from typing import Iterator, Union


class ClashRoyaleObject:

    """
    A class that represents a custom object for the library.
    """

    def __init__(self, _data: Union[dict, list, tuple]):
        self._data = _data
        if isinstance(self._data, dict):
            for key, value in self._data.items():
                _key = type(key)(sub(r"(?<!^)(?=[A-Z])", "_", str(key)).lower())
                if isinstance(value, (list, tuple)):
                    self.__setattr__(_key, [ClashRoyaleObject(index) if isinstance(index, (dict, list, tuple)) else index for index in value])
                elif isinstance(value, dict):
                    self.__setattr__(_key, ClashRoyaleObject(value))
                else:
                    self.__setattr__(_key, value)
        else:
            self.__getitem__ = lambda index: [ClashRoyaleObject(index) if isinstance(index, (dict, list, tuple)) else index for index in value][index]

    def __eq__(self, __o: object) -> bool:
        for attribute in dir(self):
            if attribute.startswith("_"):
                continue
            if getattr(self, attribute, None) != getattr(__o, attribute, None):
                return False
        return True


class ClanLog:

    """
    A class that represents a clan's log.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> ClashRoyaleObject:
        item = self._data["items"][index]
        battle = ClashRoyaleObject(item)
        battle.created_date = datetime.strptime(item.pop("createdDate"), "%Y%m%dT%H%M%S.%fZ")
        return battle

    def __iter__(self) -> Iterator:
        for index in range(len(self)):
            yield self[index]

    def __len__(self) -> int:
        return len(self._data["items"])

    def __eq__(self, __o: object) -> bool:
        return list(self) == list(__o)


class ClanMemberList:

    """
    A class that represents a list of clan members.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> ClashRoyaleObject:
        item = self._data[index]
        member = ClashRoyaleObject(item)
        member.last_seen = datetime.strptime(item.pop("lastSeen"), "%Y%m%dT%H%M%S.%fZ")
        return member

    def __iter__(self) -> Iterator:
        for index in range(len(self)):
            yield self[index]

    def __len__(self) -> int:
        return len(self._data)

    def __eq__(self, __o: object) -> bool:
        return list(self) == list(__o)


class ClanList:

    """
    A class that represents a list of clans.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> ClashRoyaleObject:
        item = self._data["items"][index]
        clan = ClashRoyaleObject(item)
        clan.member_list = ClanMemberList(item.pop("memberList", []))
        return clan

    def __iter__(self) -> Iterator:
        for index in range(len(self)):
            yield self[index]

    def __len__(self) -> int:
        return len(self._data["items"])

    def __eq__(self, __o: object) -> bool:
        return list(self) == list(__o)


class BattleLog:

    """
    A class that represents a battle log.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> ClashRoyaleObject:
        item = self._data[index]
        battle = ClashRoyaleObject(item)
        battle.battle_time = datetime.strptime(item.pop("battleTime"), "%Y%m%dT%H%M%S.%fZ")
        return battle

    def __iter__(self) -> Iterator:
        for index in range(len(self)):
            yield self[index]

    def __len__(self) -> int:
        return len(self._data)

    def __eq__(self, __o: object) -> bool:
        return list(self) == list(__o)


class TournamentList:

    """
    A class that represents a list of tournaments.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> ClashRoyaleObject:
        item = self._data["items"][index]
        tournament = ClashRoyaleObject(item)
        tournament.created_time = datetime.strptime(item.pop("createdTime"), "%Y%m%dT%H%M%S.%fZ")
        return tournament

    def __iter__(self) -> Iterator:
        for index in range(len(self)):
            yield self[index]

    def __len__(self) -> int:
        return len(self._data["items"])

    def __eq__(self, __o: object) -> bool:
        return list(self) == list(__o)


class ChallengeList:

    """
    A class that represents a list of challenges.
    """

    def __init__(self, _data: dict) -> None:
        self._data = _data

    def __getitem__(self, index: int) -> ClashRoyaleObject:
        item = self._data[index]
        challenge = ClashRoyaleObject(item)
        challenge.start_time = datetime.strptime(item.pop("startTime"), "%Y%m%dT%H%M%S.%fZ")
        challenge.end_time = datetime.strptime(item.pop("endTime"), "%Y%m%dT%H%M%S.%fZ")
        return challenge

    def __iter__(self) -> Iterator:
        for index in range(len(self)):
            yield self[index]

    def __len__(self) -> int:
        return len(self._data["items"])

    def __eq__(self, __o: object) -> bool:
        return list(self) == list(__o)
