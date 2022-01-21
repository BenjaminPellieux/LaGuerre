import socket

def error(msg):
    print(f"[ERROR] {msg}")
    exit()

def build_message(key, params):
    msg = f"{key}|{'|'.join(map(str, params))}".encode()
    print(f"[LOG] {msg}")
    return msg

def parse_message(msg):
    return [s.upper() for s in msg.split("|")]

def move_player(player_id, params):
    direction = params[0]
    return (0, "")

def handle_command(player_id, command, params):
    print(f"{command=}{params=}")
    commands = {'MOVE': "Bonjour"}
    if not command in commands:
        return (1, "Commande inexistante")

    #return commands[command](player_id, params)

MAX_PLAYERS = 1

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', 5000))

# Attente de la connexion des joueurs
players = []
while len(players) < MAX_PLAYERS:
    socket.listen(5)
    client, address = socket.accept()
    print(f"[INFO] {address} connected")

    response = client.recv(255).decode()
    if not response:
        client.send(build_message("ERROR", ["Erreur dans la reception du message"]))
        continue

    command, *params = parse_message(response)
    if command != 'JOIN' or len(params) != 1:
        client.send(build_message("ERROR", ["Vous devez en premier JOIN avec un nom d'équipe"]))
        continue

    print(f"[INFO] Nouveau client accepté avec le nom {params[0]}")
    players.append(client)

# Annonce du début de la partie
print("[INFO] Tous les joueurs ont rejoins, début de la partie")
for i, player in enumerate(players):
    player.send(build_message("NEWGAME", [5, MAX_PLAYERS, i, 0, 0]))

# Tant que la game tourne
while True:
    for player_id, player in enumerate(players):
        player.send(build_message("NEWTURN", [0]))
        # Envoie de tous les nouveaux événements
        move = player.recv(255).decode()

        # Si cela arrive, c'est qu'un
        if not move:
            error("Erreur dans la reception du joueur {player_id}")
            exit()

        # On execute la commande envoyée par le joueur
        command, *params = parse_message(move)
        handle_command(player_id, command, params)
        #err, response = handle_command(player_id, command, params)
        #print(f"{err=}  {response=}")
        # Si une erreur a eu lieu, on quite directement le programme 
        # (cela signifie que le code du client n'est pas bon)
        #if err:
        #    error(response)
