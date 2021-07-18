# Seeker-API

Webservice providing REST API for SeekerBot

## TODO
- [ ] Data migration
- [ ] Users and authentication
- [ ] Undo commands
- [ ] Time filter for leaderboard/stats
    - Time conversions done by SeekerBot, time filtering will be done using GMT as stored in the database

## API Request JSON

```json
{
    "reports": [
        {
            "user": {
                "id": 0,
                "name": "str",
            },
            "deck": "str",
            "games": 0
        },
        {
            "user": {
                "id": 0,
                "name": "str",
            },
            "deck": "str",
            "games": 0
        }],
    "guild": {
        "guild_id": 0,
        "name": "str"
    },
    "channel_id": 0,
    "format": "str",
    "notes": "str"
}
```
