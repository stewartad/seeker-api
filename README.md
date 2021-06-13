# Grand Maximus

A tftcg site for a new era

## TODO
- [ ] Data migration
- [ ] Users and authentication

## API Request JSON

```json
{
    "reports": [
        {
            "user": {
                "id": int,
                "name": "str",
            },
            "deck": "str",
            "games": int
        },
        {
            "user": {
                "id": int,
                "name": "str",
            },
            "deck": "str",
            "games": int
        }],
    "guild": {
        "guild_id": int,
        "name": "str"
    },
    "channel_id": int,
    "format": "str",
    "notes": "str"
}
```

## Community

Keep up to date with the tftcg fan-support scene.

## SeekerBot

Discord bot to report match results.

### Features

- [ ] REST API

## Card Database

Easily reference official and unofficial cards

## Deckbuilder

### Features

- [ ] Inline search of the card database using any card property
- [ ] Visual preview
