# Chat relay for PyPlanet
## Plugin for Trackmania and Maniaplanet server controller Pyplanet to forward chat messages from players to a specified URL

Exposed settings:

| Setting key                | Label                     | Type   | Default                 | Description                                   |
|----------------------------|----------------------------|--------|--------------------------|-----------------------------------------------|
| chat_relay_webhook_url     | ChatRelay webhook URL      | string | http://localhost:3000    | Endpoint URL to receive player chat messages. |
| chat_relay_http_timeout    | ChatRelay request timeout  | float  | 1.0                      | How long to wait for delivery to webhook.     |
