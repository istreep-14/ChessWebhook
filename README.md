
# Chess Bot Webhook

A Script that notifies you through a Discord Webhook when a game of chess has been played  on [Chess.com](https://chess.com).
## Requirements

* `Python 3.6` or above
* Permission to create a `Discord Webhook` in the Server
* A hosting service e.g. `AWS` (optional)
## Installation

Python libraries:
```bash
  pip install discord-webhook
  pip install DateTime
  pip install pytz
  pip install requests
```
## Usage

Create a txt file with the Webhook's URL named `webhook.txt` or replace the contents of the variable `webhook_url` in `line 6` to your Webhook's url.
Replace the contents of the variable `player` in `line 14` to your [Chess.com](https://chess.com) username.
Create a txt file named `last-game.txt`.
## Embed demo

![Demo](https://github.com/AnanasHerz/Chess-Bot-Webhook/blob/main/demo.png?raw=true)