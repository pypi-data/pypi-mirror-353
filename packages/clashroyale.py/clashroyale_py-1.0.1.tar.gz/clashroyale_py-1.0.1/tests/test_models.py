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


# pylint: skip-file

import unittest
from clashroyale.models import (
    ClashRoyaleObject, ClanLog, ClanMemberList, ClanList, BattleLog, TournamentList, ChallengeList
)

def fresh_clanlog():
    return ClanLog({
        'items': [
            {'createdDate': '20250101T120000.000Z', 'foo': 'bar', 'num': 1},
            {'createdDate': '20250102T130000.000Z', 'baz': 'qux', 'num': 2}
        ]
    })

def fresh_clanmemberlist():
    return ClanMemberList([
        {'lastSeen': '20250101T120000.000Z', 'name': 'Alice', 'role': 'leader'},
        {'lastSeen': '20250102T130000.000Z', 'name': 'Bob', 'role': 'member'}
    ])

def fresh_clanlist():
    return ClanList({
        'items': [
            {'memberList': [{'lastSeen': '20250101T120000.000Z', 'name': 'Alice', 'role': 'leader'}], 'foo': 'bar'},
            {'memberList': [{'lastSeen': '20250102T130000.000Z', 'name': 'Bob', 'role': 'member'}], 'baz': 'qux'}
        ]
    })

def fresh_battlelog():
    return BattleLog([
        {'battleTime': '20250101T120000.000Z', 'foo': 'bar', 'result': 'win'},
        {'battleTime': '20250102T130000.000Z', 'baz': 'qux', 'result': 'lose'}
    ])

def fresh_tournamentlist():
    return TournamentList({
        'items': [
            {'createdTime': '20250101T120000.000Z', 'foo': 'bar', 'id': 1},
            {'createdTime': '20250102T130000.000Z', 'baz': 'qux', 'id': 2}
        ]
    })

def fresh_challengelist():
    return ChallengeList([
        {'startTime': '20250101T120000.000Z', 'endTime': '20250101T130000.000Z', 'foo': 'bar', 'id': 1},
        {'startTime': '20250102T120000.000Z', 'endTime': '20250102T130000.000Z', 'baz': 'qux', 'id': 2}
    ])

class TestClashRoyaleObject(unittest.TestCase):
    def test_attribute_access_and_nested(self):
        data = {'fooBar': 123, 'nestedList': [{'a': 1}, {'b': 2}], 'nestedDict': {'c': 3}}
        obj = ClashRoyaleObject(data)
        self.assertEqual(obj.foo_bar, 123)
        self.assertIsInstance(obj.nested_list[0], ClashRoyaleObject)
        self.assertEqual(obj.nested_list[0].a, 1)
        self.assertIsInstance(obj.nested_dict, ClashRoyaleObject)
        self.assertEqual(obj.nested_dict.c, 3)

    def test_eq(self):
        obj1 = ClashRoyaleObject({'fooBar': 1})
        obj2 = ClashRoyaleObject({'fooBar': 1})
        obj3 = ClashRoyaleObject({'fooBar': 2})
        self.assertEqual(obj1, obj2)
        self.assertNotEqual(obj1, obj3)

class TestClanLog(unittest.TestCase):
    def test_getitem_and_types(self):
        log = fresh_clanlog()
        item = log[0]
        self.assertIsInstance(item, ClashRoyaleObject)
        self.assertEqual(item.foo, 'bar')
        self.assertEqual(item.num, 1)
        item2 = log[1]
        self.assertEqual(item2.baz, 'qux')
        self.assertEqual(item2.num, 2)

    def test_iter_and_len(self):
        log = fresh_clanlog()
        items = list(log)
        self.assertEqual(len(items), 2)
        self.assertEqual(len(log), 2)

class TestClanMemberList(unittest.TestCase):
    def test_getitem_and_types(self):
        members = fresh_clanmemberlist()
        member = members[0]
        self.assertIsInstance(member, ClashRoyaleObject)
        self.assertEqual(member.name, 'Alice')
        self.assertEqual(member.role, 'leader')
        member2 = members[1]
        self.assertEqual(member2.name, 'Bob')
        self.assertEqual(member2.role, 'member')

    def test_iter_and_len(self):
        members = fresh_clanmemberlist()
        items = list(members)
        self.assertEqual(len(items), 2)
        self.assertEqual(len(members), 2)

class TestClanList(unittest.TestCase):
    def test_getitem_and_types(self):
        clans = fresh_clanlist()
        clan = clans[0]
        self.assertIsInstance(clan, ClashRoyaleObject)
        self.assertIsInstance(clan.member_list, ClanMemberList)
        self.assertEqual(clan.foo, 'bar')
        clan2 = clans[1]
        self.assertEqual(clan2.baz, 'qux')

    def test_iter_and_len(self):
        clans = fresh_clanlist()
        items = list(clans)
        self.assertEqual(len(items), 2)
        self.assertEqual(len(clans), 2)

class TestBattleLog(unittest.TestCase):
    def test_getitem_and_types(self):
        log = fresh_battlelog()
        battle = log[0]
        self.assertIsInstance(battle, ClashRoyaleObject)
        self.assertEqual(battle.foo, 'bar')
        self.assertEqual(battle.result, 'win')
        battle2 = log[1]
        self.assertEqual(battle2.baz, 'qux')
        self.assertEqual(battle2.result, 'lose')

    def test_iter_and_len(self):
        log = fresh_battlelog()
        items = list(log)
        self.assertEqual(len(items), 2)
        self.assertEqual(len(log), 2)

class TestTournamentList(unittest.TestCase):
    def test_getitem_and_types(self):
        tournaments = fresh_tournamentlist()
        tournament = tournaments[0]
        self.assertIsInstance(tournament, ClashRoyaleObject)
        self.assertEqual(tournament.foo, 'bar')
        self.assertEqual(tournament.id, 1)
        tournament2 = tournaments[1]
        self.assertEqual(tournament2.baz, 'qux')
        self.assertEqual(tournament2.id, 2)

    def test_iter_and_len(self):
        tournaments = fresh_tournamentlist()
        items = list(tournaments)
        self.assertEqual(len(items), 2)
        self.assertEqual(len(tournaments), 2)

class TestChallengeList(unittest.TestCase):
    def test_getitem_and_types(self):
        challenges = fresh_challengelist()
        challenge = challenges[0]
        self.assertIsInstance(challenge, ClashRoyaleObject)
        self.assertEqual(challenge.foo, 'bar')
        self.assertEqual(challenge.id, 1)
        challenge2 = challenges[1]
        self.assertEqual(challenge2.baz, 'qux')
        self.assertEqual(challenge2.id, 2)

    def test_iter_and_len(self):
        challenges = fresh_challengelist()
        items = list(challenges)
        self.assertEqual(len(items), 2)
        self.assertEqual(len(challenges), 2)

if __name__ == '__main__':
    unittest.main()
