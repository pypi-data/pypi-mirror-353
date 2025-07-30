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
from clashroyale.client import Client
from clashroyale.models import ClashRoyaleObject, ClanLog, ClanList, ClanMemberList, BattleLog, TournamentList, ChallengeList

class DummySession:
    def __init__(self):
        self.headers = {}
        self.last_url = None
        self.last_params = None
        self.response = None
    def get(self, url, headers=None, params=None):
        self.last_url = url
        self.last_params = params
        class DummyResponse:
            def __init__(self, json_data):
                self._json = json_data
                self.status_code = 200
            def json(self):
                return self._json
        return DummyResponse(self.response)

def make_client_with_response(response):
    session = DummySession()
    session.response = response
    return Client('token', session=session)

class TestClient(unittest.TestCase):
    def test_get_war_log(self):
        response = {'items': [{'createdDate': '20250101T120000.000Z', 'foo': 'bar'}]}
        client = make_client_with_response(response)
        log = client.get_war_log('tag')
        self.assertIsInstance(log, ClanLog)
        self.assertEqual(log[0].foo, 'bar')

    def test_search_clans(self):
        response = {'items': [{'foo': 'bar', 'memberList': []}]}
        client = make_client_with_response(response)
        clans = client.search_clans(name='test')
        self.assertIsInstance(clans, ClanList)
        self.assertEqual(clans[0].foo, 'bar')

    def test_get_river_race_log(self):
        response = {'items': [{'createdDate': '20250101T120000.000Z', 'foo': 'bar'}]}
        client = make_client_with_response(response)
        log = client.get_river_race_log('tag')
        self.assertIsInstance(log, ClanLog)
        self.assertEqual(log[0].foo, 'bar')

    def test_get_clan(self):
        response = {'foo': 'bar', 'memberList': []}
        client = make_client_with_response(response)
        clan = client.get_clan('tag')
        self.assertIsInstance(clan, ClashRoyaleObject)
        self.assertEqual(clan.foo, 'bar')
        self.assertIsInstance(clan.member_list, ClanMemberList)

    def test_get_clan_members(self):
        response = [{'name': 'Alice', 'lastSeen': '20250101T120000.000Z'}]
        client = make_client_with_response(response)
        members = client.get_clan_members('tag')
        self.assertIsInstance(members, ClanMemberList)
        self.assertEqual(members[0].name, 'Alice')

    def test_get_current_river_race(self):
        response = {'foo': 'bar'}
        client = make_client_with_response(response)
        race = client.get_current_river_race('tag')
        self.assertIsInstance(race, ClashRoyaleObject)
        self.assertEqual(race.foo, 'bar')

    def test_get_player(self):
        response = {'foo': 'bar'}
        client = make_client_with_response(response)
        player = client.get_player('tag')
        self.assertIsInstance(player, ClashRoyaleObject)
        self.assertEqual(player.foo, 'bar')

    def test_get_upcoming_chests(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        chests = client.get_upcoming_chests('tag')
        self.assertIsInstance(chests, list)
        self.assertIsInstance(chests[0], ClashRoyaleObject)
        self.assertEqual(chests[0].foo, 'bar')

    def test_get_player_battlelog(self):
        response = [{'battleTime': '20250101T120000.000Z', 'foo': 'bar'}]
        client = make_client_with_response(response)
        log = client.get_player_battlelog('tag')
        self.assertIsInstance(log, BattleLog)
        self.assertEqual(log[0].foo, 'bar')

    def test_get_cards(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        cards = client.get_cards()
        self.assertIsInstance(cards, list)
        self.assertIsInstance(cards[0], ClashRoyaleObject)
        self.assertEqual(cards[0].foo, 'bar')

    def test_search_tournaments(self):
        response = {'items': [{'createdTime': '20250101T120000.000Z', 'foo': 'bar'}]}
        client = make_client_with_response(response)
        tournaments = client.search_tournaments(name='test')
        self.assertIsInstance(tournaments, TournamentList)
        self.assertEqual(tournaments[0].foo, 'bar')

    def test_get_tournament(self):
        response = {'createdTime': '20250101T120000.000Z', 'foo': 'bar'}
        client = make_client_with_response(response)
        tournament = client.get_tournament('tag')
        self.assertIsInstance(tournament, ClashRoyaleObject)
        self.assertEqual(tournament.foo, 'bar')

    def test_get_clan_rankings(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        rankings = client.get_clan_rankings('global')
        self.assertIsInstance(rankings, list)
        self.assertIsInstance(rankings[0], ClashRoyaleObject)
        self.assertEqual(rankings[0].foo, 'bar')

    def test_get_player_rankings(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        rankings = client.get_player_rankings(1)
        self.assertIsInstance(rankings, list)
        self.assertIsInstance(rankings[0], ClashRoyaleObject)
        self.assertEqual(rankings[0].foo, 'bar')

    def test_get_clan_war_rankings(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        rankings = client.get_clan_war_rankings('global')
        self.assertIsInstance(rankings, list)
        self.assertIsInstance(rankings[0], ClashRoyaleObject)
        self.assertEqual(rankings[0].foo, 'bar')

    def test_get_path_of_legends_rankings(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        rankings = client.get_path_of_legends_rankings(season_id='1', location_id=None)
        self.assertIsInstance(rankings, list)
        self.assertIsInstance(rankings[0], ClashRoyaleObject)
        self.assertEqual(rankings[0].foo, 'bar')

    def test_get_season(self):
        response = {'endTime': '20250101T120000.000Z', 'foo': 'bar'}
        client = make_client_with_response(response)
        season = client.get_season('1')
        self.assertIsInstance(season, ClashRoyaleObject)
        self.assertEqual(season.foo, 'bar')

    def test_get_season_rankings(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        rankings = client.get_season_rankings('2025-01')
        self.assertIsInstance(rankings, list)
        self.assertIsInstance(rankings[0], ClashRoyaleObject)
        self.assertEqual(rankings[0].foo, 'bar')

    def test_get_all_season_months(self):
        response = {'items': [{'id': 1}, {'id': 2}]}
        client = make_client_with_response(response)
        months = client.get_all_season_months()
        self.assertEqual(months, [1, 2])

    def test_get_all_locations(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        locations = client.get_all_locations()
        self.assertIsInstance(locations, list)
        self.assertIsInstance(locations[0], ClashRoyaleObject)
        self.assertEqual(locations[0].foo, 'bar')

    def test_get_location(self):
        response = {'foo': 'bar'}
        client = make_client_with_response(response)
        location = client.get_location('1')
        self.assertIsInstance(location, ClashRoyaleObject)
        self.assertEqual(location.foo, 'bar')

    def test_get_tournament_rankings(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        rankings = client.get_tournament_rankings('tag')
        self.assertIsInstance(rankings, list)
        self.assertIsInstance(rankings[0], ClashRoyaleObject)
        self.assertEqual(rankings[0].foo, 'bar')

    def test_get_challenges(self):
        response = [
            {'startTime': '20250101T120000.000Z', 'endTime': '20250101T130000.000Z', 'foo': 'bar'}
        ]
        client = make_client_with_response(response)
        challenges = client.get_challenges()
        self.assertIsInstance(challenges, ChallengeList)
        self.assertEqual(challenges[0].foo, 'bar')

    def test_get_leaderboard(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        leaderboard = client.get_leaderboard(1)
        self.assertIsInstance(leaderboard, list)
        self.assertIsInstance(leaderboard[0], ClashRoyaleObject)
        self.assertEqual(leaderboard[0].foo, 'bar')

    def test_get_all_leaderboards(self):
        response = {'items': [{'foo': 'bar'}]}
        client = make_client_with_response(response)
        leaderboards = client.get_all_leaderboards()
        self.assertIsInstance(leaderboards, list)
        self.assertIsInstance(leaderboards[0], ClashRoyaleObject)
        self.assertEqual(leaderboards[0].foo, 'bar')

    def test_get_all_global_tournaments(self):
        response = {'items': [{'createdTime': '20250101T120000.000Z', 'foo': 'bar'}]}
        client = make_client_with_response(response)
        tournaments = client.get_all_global_tournaments()
        self.assertIsInstance(tournaments, TournamentList)
        self.assertEqual(tournaments[0].foo, 'bar')

if __name__ == '__main__':
    unittest.main()
