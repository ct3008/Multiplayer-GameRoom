from flask import Flask
from flask import render_template
from flask import Response, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS
import random
import string
from random import choice

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

lobbies = {
    'XYNO9342': {'players': ['player_test1', 'player_test2'],'game': False, 'players_ready': []},
    'BBNE9402': {'players': ['player_test3'],'game': False,'players_ready': []},
}

players = {
    'player_id1': 'XYNO9342',
    'player_id2': 'XYNO9342',
    'player_id3': 'BBNE9402',
}

#Variables for game
player_choices = {}
remaining_replay_players = {}
game_started = {} #Holds lobby_id and players in the lobby that started a game
sockets=[] #Unused


def startGame(lobby_id):
    if len(lobbies[lobby_id]['players']) > 5 and not lobbies[lobby_id]['game']:
        lobbies[lobby_id]['game'] = True
        socketio.emit('game_starting', {'message': f'Game starting now in lobby {lobby_id}', 'lobby_id': lobby_id})
        # for player_id in lobbies[lobby_id]['players']:
        #     socketio.emit('redirect_to_game', {'lobby_id': lobby_id})


# ROUTES
@app.route('/')
def lobby():
    return render_template('lobby.html', lobbies=lobbies, players=players, io=socketio)
    
@app.route('/room/<lobby_id>')
def room(lobby_id=None):
    player_id = session.get('player_id', None)
    return render_template('room.html', lobbies=lobbies, lobby_id=lobby_id, player_id=player_id, io=socketio)

@app.route('/game/<lobby_id>')
def game(lobby_id):
    player_list = [player for player, lobby in players.items() if lobby == lobby_id]
    return render_template('game.html', lobby_id=lobby_id, players=player_list)

#Handles when a client connects
@socketio.on('connect')
def handle_connect():
	# print('Client connected: ', socketio)
	sockets.append(socketio)
    
#Handles logic for joining a lobby
@socketio.on('join_lobby')
def handle_join_lobby(data):
    player_id = data['player_id']
    session['player_id'] = player_id
    if player_id not in players or players[player_id] == "":
        lobby_id = data['lobby_id']
        join_room(lobby_id)
        lobbies[lobby_id]['players'].append(player_id)
        players[player_id] = lobby_id
        
        #Emits information to player they joined the room and alerts others in the room about this and updates their views
        emit('room_joined', {'lobby_id': lobby_id})
        socketio.emit('room_alert', {'message': f'{player_id} has joined lobby {lobby_id}'})
        socketio.emit('room_update', {'lobby_id': lobby_id, 'lobbies': lobbies})
        
        #Checks for startGame conditions (3 players in a room)
        startGame(lobby_id)
    elif players[player_id] == data['lobby_id']: 
        emit('in_correct_room',{'lobby_id': data['lobby_id']})
    else:
        emit('already_in_room', {'message': f'You are already in room {players[player_id]}!'})

#Handles logic for a player leaving a room and removing them from the datastructures and emitting information
@socketio.on('leave_room')
def handle_leave_room(data):
    player_id = data['player_id']
    lobby_id = players.get(player_id)
    if lobby_id:
        if player_id in lobbies[lobby_id]['players']:
            lobbies[lobby_id]['players'].remove(player_id)
        del players[player_id]

        socketio.emit('room_alert', {'message': f'{player_id} has left lobby {lobby_id}'})
        socketio.emit('room_update', {'lobby_id': lobby_id, 'lobbies': lobbies})
        leave_room(lobby_id)
        if len(lobbies[lobby_id]['players']) == 0:
            del lobbies[lobby_id]
            # print(f"Lobby {lobby_id} deleted")
            socketio.emit('room_update', {'lobby_id': lobby_id, 'lobbies': lobbies})


#Handles logic to delete a lobby
@socketio.on('delete_lobby')
def handle_delete_lobby(data):
    # print("ENTERED DELETE LOBBY")
    # print(lobbies)
    lobby_id = data['lobby_id']
    if lobby_id in lobbies:
        del lobbies[lobby_id]
        # print(f"Lobby {lobby_id} deleted.")
    
#Handles logic for a player checking if they are ready to start the game
@socketio.on('check_start')
def handle_check_start(data):
    player_id = data['player_id']
    lobby_id = players.get(player_id)
    if lobby_id:
        if player_id in lobbies[lobby_id]['players']:
            lobbies[lobby_id]['players_ready'].append(player_id)
            socketio.emit('room_remaining_players', {'remaining': len(lobbies[lobby_id]['players']) - len(lobbies[lobby_id]['players_ready'])})
            if len(lobbies[lobby_id]['players_ready']) == len(lobbies[lobby_id]['players']):
                #All players are ready, start the game
                lobbies[lobby_id]['game'] = True
                socketio.emit('game_starting', {'message': f'Game starting now in lobby {lobby_id}', 'lobby_id': lobby_id})

def generate_lobby_id():
    #For security, combines 4 random letters and 4 numbers to make random lobby ID
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    digits = ''.join(random.choices(string.digits, k=4))
    return letters + digits
     
#Handles logic of creating a new lobby room
@socketio.on('create_lobby')
def handle_create_lobby(player_id):
    if player_id not in players or players[player_id] == "":
        lobby_id = generate_lobby_id()
        # print("LOBBY ID", lobby_id)
        lobbies[lobby_id] = {'players': [player_id],'game': False, 'players_ready': []}
        players[player_id] = lobby_id
        
        socketio.emit('lobby_update', {'lobby_id': lobby_id, 'lobbies': lobbies})
        # emit('lobby_created', [lobbies[lobby_id], lobby_id])
    else:
        socketio.emit('already_in_room', {'message': f'You are already in room {players[player_id]}!'})

#Handles logic upon a player clicking a choice button in the game to keep track of what the player chose
@socketio.on('player_choice')
def handle_player_choice(data):
    player_id = data['player_id']
    button_id = data['button_id']
    # print("ENTER PLAYER CHOICE FOR PLAYER ", player_id, " ON BUTTON ", button_id)
    lobby_id = players[player_id]
    player_choices.setdefault(lobby_id, {})[player_id] = button_id
    # print("player choices: ", player_choices)
    
    #COunts number of players yet to choose
    remaining_players = len(lobbies[lobby_id]['players']) - len(player_choices[lobby_id])
    socketio.emit('remaining_players', {'remaining': remaining_players})
    if remaining_players == 0:
        #Checks if all answers are unique
        choices = list(player_choices[lobby_id].values())
        unique_choices = len(set(choices))
        if unique_choices == len(choices):
            # print("unique")
            socketio.emit('game_result', {'message': 'You win! All players chose different buttons.'})
        else:
            # print("not unique")
            socketio.emit('game_result', {'message': 'You lose! Some players chose the same button.'})

#Handles logic upon receiving play again signal from players in a room if they want to play again
@socketio.on('play_again')
def handle_play_again(data):
    player_id = data['player_id']
    lobby_id = players[player_id]

    if lobby_id not in remaining_replay_players:
        remaining_replay_players[lobby_id] = len(lobbies[lobby_id]['players']) - 1
    else:
        remaining_replay_players[lobby_id] -= 1
    
    print(remaining_replay_players[lobby_id])

    #Check if all players have pressed the replay button
    if remaining_replay_players[lobby_id] <= 0:
        #Reset the game if all players have pressed the replay button
        remaining_replay_players[lobby_id] = len(lobbies[lobby_id]['players']) - 1
        player_choices[lobby_id] = {}
        socketio.emit('replay', {'lobby_id': lobby_id})

    #Emit the remaining players count to update clients in real-time
    socketio.emit('remaining_replay_players', {'remaining': remaining_replay_players[lobby_id]})


@socketio.on('new_user')
def handle_new_user(data):
    player_id = data['player_id']
    players[player_id] = '' 
    #New user indicated without a room
    # print('New user connected with player ID:', player_id)

    

if __name__ == '__main__':
    socketio.run(app)
#    app.run(debug = True)
