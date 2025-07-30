.. image:: https://raw.githubusercontent.com/Ombucha/clashroyale.py/main/banner.png

.. image:: https://img.shields.io/pypi/v/clashroyale.py
    :target: https://pypi.python.org/pypi/clashroyale.py
    :alt: PyPI version
.. image:: https://img.shields.io/pypi/dm/clashroyale.py
    :target: https://pypi.python.org/pypi/clashroyale.py
    :alt: PyPI downloads
.. image:: https://sloc.xyz/github/Ombucha/clashroyale.py
    :target: https://github.com/Ombucha/clashroyale.py/graphs/contributors
    :alt: Lines of code
.. image:: https://img.shields.io/github/repo-size/Ombucha/clashroyale.py
    :target: https://github.com/Ombucha/clashroyale.py
    :alt: Repository size

A modern, easy-to-use, and feature-rich Python wrapper for the Clash Royale API.

Features
--------

- Full support for all Clash Royale API endpoints
- Event-driven architecture (with decorators)
- Pythonic models for all objects (players, clans, tournaments, etc.)
- Built-in error handling and rate limit management
- Type hints for all public interfaces
- Actively maintained and open source

Requirements
------------

- Python 3.8 or higher
- `requests <https://pypi.python.org/pypi/requests>`_

Installation
------------

**Stable version:**

.. code-block:: sh

    # Unix / macOS
    python3 -m pip install "clashroyale.py"

    # Windows
    py -m pip install "clashroyale.py"

**Development version:**

.. code-block:: sh

    git clone https://github.com/Ombucha/clashroyale.py

Getting Started
---------------

.. code-block:: python

    import clashroyale as cr

    client = cr.Client("token")

    # Fetch a player by tag
    player = client.get_player("#URUGP8G0")
    print(f"{player.name}: {player.trophies} trophies")

    # Fetch a clan and its members
    clan = client.get_clan("#Q9LYC0YL")
    print(f"Clan: {clan.name} ({clan.tag})")
    for member in clan.member_list:
        print(f"{member.name} - {member.trophies} trophies")

    # Get top 5 global players
    top_players = client.get_player_rankings("global", limit=5)
    for player in top_players:
        print(f"{player.rank}. {player.name} - {player.trophies} trophies")

Links
-----

- `Clash Royale <https://clashroyale.com/>`_
- `Official API <https://developer.clashroyale.com/>`_
- `Documentation <https://clashroyalepy.readthedocs.io/>`_
- `Examples <https://github.com/Ombucha/clashroyale.py/tree/main/examples>`_

----

**Note:**  
If you encounter issues, please search for duplicates and then create a new issue on GitHub with as much detail as possible (including terminal output, OS details, and Python version).