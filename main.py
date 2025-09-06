from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
import time

w = open("webhook.txt", "r")
webhook_url = w.read()

print('Running...') #Debug message on ready

def parse_pgn(pgn_text):
    tags = {}
    if not pgn_text:
        return tags, ''
    lines = pgn_text.splitlines()
    index = 0
    while index < len(lines) and lines[index].strip().startswith('['):
        line = lines[index].strip()
        if line.startswith('[') and line.endswith(']'):
            try:
                inner = line[1:-1]
                space_position = inner.find(' ')
                if space_position != -1:
                    tag = inner[:space_position]
                    value_part = inner[space_position + 1:].strip()
                    if value_part.startswith('"') and value_part.endswith('"'):
                        value = value_part[1:-1]
                    else:
                        value = value_part.strip('"')
                    tags[tag] = value
            except Exception:
                pass
        index += 1
    while index < len(lines) and lines[index].strip() == '':
        index += 1
    movetext = ' '.join(lines[index:]).strip()
    return tags, movetext

def loop():
    #Webhook
    webhook = DiscordWebhook(url=webhook_url)
    #Player
    player = 'ananasherz1' #Players username
    check = requests.get(f'https://api.chess.com/pub/player/{player}')
    #Empty variables
    rated = ''
    time_class = ''
    result = ''
    reason = ''
    side = ''
    color = ''
    opponent = ''
    endboard = ''
    global restart
    restart = False
    if check.status_code == 200:
        archive = requests.get(f'https://api.chess.com/pub/player/{player}/games/archives').json()
        newest_arc = int(len(archive['archives']))-1
        most_recent_archive = archive['archives'][newest_arc]
        response = requests.get(most_recent_archive).json()
        if requests.get(most_recent_archive).status_code == 200 and archive != '[]':
            f = open("last-game.txt", "r")
            last_game = f.read()
            #Def the most recent game
            newest = int(len(response['games']))-1
            suspected_last_game = response['games'][newest]['url']
            #Def the suspected last game
            if suspected_last_game != last_game:
                f.close()
                f = open("last-game.txt", "w")
                f.write(suspected_last_game)
                f.close()
                print('Url changed')
                #Url var
                url = response['games'][newest]['url']
                #Rated or unrated
                if response['games'][newest]['rated'] is True:
                    rated = 'a rated'
                if response['games'][newest]['rated'] is False:
                    rated = 'an unrated'
                else:
                    pass
                #Time class of game (Blitz, Bullet...) and url friendly endboard image adress
                time_class = response['games'][newest]['time_class']
                fen = response['games'][newest]['fen'].replace(" ", "%20")
                #Defines the sides
                if response['games'][newest]['white']['username'] == player:
                    side = response['games'][newest]['white']
                    color = 'white'
                    opponent = response['games'][newest]['black']
                if response['games'][newest]['black']['username'] == player:
                    side = response['games'][newest]['black']
                    color = 'black'
                    opponent = response['games'][newest]['white']
                if response['games'][newest]['white']['username'] != player and response['games'][newest]['black']['username'] != player:
                    side = 'invalid colors'
                    opponent = 'invalid colors'
                    print('Invalid color')
                else:
                    pass
                #Result codes
                if side['result'] == 'win':
                    result = 'won'
                if opponent['result'] == 'win':
                    result = 'lost'
                if side['result'] == 'agreed' or side['result'] == 'repetition' or side['result'] == 'stalemate' or side['result'] == 'insufficient' or side['result'] == '50move' or side['result'] == 'timevsinsufficient':
                    result = 'drawed'
                else:
                    pass
                #Reason of endpoint
                if side['result'] == 'checkmated' or opponent['result'] == 'checkmated':
                    reason = 'checkmate'
                if side['result'] == 'agreed' or opponent['result'] == 'agreed':
                    reason = 'an agreemend'
                if side['result'] == 'repetition' or opponent['result'] == 'repetition':
                    reason = 'repetition'
                if side['result'] == 'timeout' or opponent['result'] == 'timeout':
                    reason = 'timeout'
                if side['result'] == 'resigned' or opponent['result'] == 'resigned':
                    reason = 'resignation'
                if side['result'] == 'stalemate' or opponent['result'] == 'stalemate':
                    reason = 'a stalemate'
                if side['result'] == 'insufficient' or opponent['result'] == 'insufficient':
                    reason = 'insufficient material'
                if side['result'] == '50move' or opponent['result'] == '50move':
                    reason = 'the 50-move rule'
                if side['result'] == 'abandoned' or opponent['result'] == 'abandoned':
                    reason = 'abandonment'
                if side['result'] == 'kingofthehill' or opponent['result'] == 'kingofthehill':
                    reason = 'the opponent king who reached the hill'
                if side['result'] == 'threecheck' or opponent['result'] == 'threecheck':
                    reason = 'three check'
                if side['result'] == 'timevsinsufficient' or opponent['result'] == 'timevsinsufficient':
                    reason = 'the timeout vs insufficient material rule'
                if side['result'] == 'bughousepartnerlose' or opponent['result'] == 'bughousepartnerlose':
                    reason = 'Bughouse partner lost'
                else:
                    pass
                #Endboard image adress
                endboard = f'https://www.chess.com/dynboard?fen={fen}&board=brown&piece=neo&size=3'
                # PGN details: rating, ECO, opening URL, movetext
                pgn_text = response['games'][newest].get('pgn', '')
                tags, movetext = parse_pgn(pgn_text)
                eco = tags.get('ECO', 'Unknown')
                opening_url = tags.get('ECOUrl') or tags.get('OpeningUrl') or 'Unknown'
                if color == 'white':
                    my_rating = tags.get('WhiteElo', 'Unknown')
                elif color == 'black':
                    my_rating = tags.get('BlackElo', 'Unknown')
                else:
                    my_rating = 'Unknown'
                moves_field = movetext if movetext else 'Unavailable'
                if len(moves_field) > 1000:
                    moves_field = moves_field[:1000] + '…'
                #Alert                
                alert = DiscordEmbed(
                    title = f'{player} just played a game of chess!',
                    description = f'{player} played as {color} {rated} {time_class} game and {result} by {reason}.',
                    color = '769656'
                )
                alert.set_author(name='Chess Bot', icon_url='https://play-lh.googleusercontent.com/a7R5nyeaX8lIEWdBOxjlvbyq9LcFwh3XMvNtBPEKR3LPGgdvgGrec4sJwn8tUaaSkw')
                alert.add_embed_field(name='Url', value=url)
                alert.add_embed_field(name='My rating', value=my_rating)
                alert.add_embed_field(name='ECO', value=eco)
                alert.add_embed_field(name='Opening URL', value=opening_url)
                alert.add_embed_field(name='Moves (PGN)', value=moves_field)
                alert.set_image(url=endboard)
                alert.set_footer(text='Made by AnanasHerz#5480')
                webhook.add_embed(alert)
                #Sending the message or not
                webhook.execute()
                print('Webhook send!')
                time.sleep(30)
                return
            if suspected_last_game == last_game:
                time.sleep(30)
                return
        if requests.get(most_recent_archive).status_code == 200 and archive == '[]':
            print('Empty archive')
            return True
    if check.status_code != 200:
        print('Status code: ', check.status_code)
        exit()
        
while True:
    loop()