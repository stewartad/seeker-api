# Seeker-API

Webservice providing REST API for SeekerBot built on Django and Django REST Framework

## TODO
- [ ] Data migration
- [ ] Users and authentication
    - Discord oauth for website access
- [ ] Undo commands
    - Proper cascading match deletion
- [ ] Per-deck stats
- [x] Time filter for leaderboard/stats
    - Timezone conversions done by SeekerBot, time filtering will be done using GMT as stored in the database

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
