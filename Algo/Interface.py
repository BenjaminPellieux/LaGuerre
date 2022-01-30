from pygame.locals import *
from random import randint, choice, seed
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
import pygame, sys, socket

# JEU
NBJOUEUR = 2
NBCASES = 6
BASE_UNITE_SIZE = 12

# AFFICHAGE
HEIGHT = 1000
WIDTH = HEIGHT+400

SIZE_LIEN = (0.35 * (HEIGHT - 40)) / NBCASES - 1
SIZE_CASE = (0.65 * (HEIGHT - 40)) / NBCASES
TOTAL_SIZE_LEN = SIZE_LIEN + SIZE_CASE

# COULEURS
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

Pos = tuple[int, int]

@dataclass(eq = True, frozen = True)
class Lien:
    from_case: Pos
    to_case: Pos

    @property
    def direction(self) -> Pos:
        return (self.to_case[0] - self.from_case[0], self.to_case[1] - self.from_case[1])

    @property
    def width(self) -> tuple[float, float]:
        return (1, 0.35) if self.direction[0] else (0.35, 1)

@dataclass
class Case:
    posx: int
    posy: int
    liens: set[Lien] = field(default_factory=set)
    case_function: Optional[str] = None

    def __post_init__(self) -> None:
        voisins = [(self.posx + x, self.posy + y) for x, y in [(-1, 0), (0, -1), (1, 0), (0, 1)]]
        for vx, vy in voisins:
            if 0 <= vx < NBCASES and 0 <= vy < NBCASES:
                self.liens.add(Lien(self.pos, (vx, vy)))

    @property
    def pos(self) -> Pos:
        return (self.posx, self.posy)

@dataclass
class Unite:
    unite_id: int
    pos: tuple[int, int]
    size: int

    @property
    def posx(self) -> int:
        return self.pos[0]

    @property
    def posy(self) -> int:
        return self.pos[1]

class Joueur:
    def __init__(self, joueur_id: int, nom: str, default_pos: Pos, color: tuple[int, int, int], nb_case: int) -> None:
        self.id = joueur_id
        self.nom = nom
        self.color = color
        self.nb_unite = 0
        self.nb_army = BASE_UNITE_SIZE
        self.list_unite: dict[int, Unite] = {0: Unite(self.nb_unite, default_pos, BASE_UNITE_SIZE)}
        self.can_play = True

    def get_unite_by_id(self, idUnite: int) -> Unite:
        if (res := self.list_unite.get(idUnite)):
            return res

        print("[ERROR] Aucune unitée avec l'id {idUnite} pour le joueur {self.id}")
        exit()

    def get_unite_at(self, pos: Pos) -> Optional[Unite]:
        for unite in self.list_unite.values():
            if unite.pos == pos:
                return unite
        return None

    def get_all_unite_pos(self) -> list[Pos]:
        return [unite.pos for unite in self.list_unite.values()]

    def __repr__(self) -> str:
        return f"{self.nom} : {self.nb_army}"

class Game:
    def __init__(self) -> None:
        self.positionJoueur = [(0, 0), (NBCASES - 1, NBCASES - 1), (NBCASES - 1, 0), (0, NBCASES - 1)]
        
        #DEFINE: Style
        self.colorJoueur = [(0, 255, 0), (255, 160, 122), (240, 15, 220), (0, 0, 0)]

        #DEFINE: Reseau
        self.serveur: Serveur = Serveur()
        self.serveur.getJoueurs()

        #DEFINE: Joueurs
        self.listJoueurs = [Joueur(i, self.serveur.team_name[i], self.positionJoueur[i], self.colorJoueur[i], NBCASES) for i in range(len(self.serveur.players))]

        #DEFINE: jeu
        self.list_cases = [[Case(i, j) for j in range(NBCASES)] for i in range(NBCASES)]
        self.proba_case_function = 5 #proba de 0.03 au debut 
        self.listFonctionCase: list[str] = ["DIVIDE", "MULT", "NULL", "PASS", "ENNEMIPASS"]
        
    def moveUnite(self, idJoueur: int, params: list[str]) -> None:
        idUniteStr, parsizeStr, direction = params
        idUnite, parsize = int(idUniteStr), int(parsizeStr)
        joueur = self.listJoueurs[idJoueur]
        unite = joueur.get_unite_by_id(idUnite)

        if not unite:
            print(f"Aucune unite avec l'id {idUnite} pour le joueur {idJoueur}")
            exit()

        if not joueur.can_play:
            joueur.can_play = True
            return

        ##MOUVEMENT
        posfrom = (unite.posx, unite.posy)
        newpos = self.getNewPos(posfrom, direction)

        if parsize < unite.size:
            newpos_unite = joueur.get_unite_at(newpos)
            unite.size -= parsize
            if newpos_unite:
                newpos_unite.size += parsize
            else: 
                joueur.nb_unite += 1
                joueur.list_unite[joueur.nb_unite] = Unite(joueur.nb_unite, newpos, parsize)
        elif parsize == unite.size:
            unite.pos = newpos
        else: 
            print(f"{idJoueur} ERROR: PAS ASSEZ DE SOLDAT")

    def divide(self, joueur: Joueur, case: Case, unite: Unite) -> None:
        unite.size //= 2
        case.case_function = None

    def mult(self, joueur: Joueur, case: Case, unite: Unite) -> None:
        unite.size *= 2
        case.case_function = None

    def null(self, joueur: Joueur, case: Case, unite: Unite) -> None:
        unite.size = 0
        # baisser de 1 tour la case

    def pass_turn(self, joueur: Joueur, case: Case, unite: Unite) -> None:
        joueur.can_play = False

    def ennemie_pass(self, joueur: Joueur, case: Case, unite: Unite) -> None:
        for j2 in self.listJoueurs:
            if j2 != joueur:
                j2.can_play = False

    def actualise(self) -> None:
        unites_to_del = []
        for joueur in self.listJoueurs:
            joueur.nb_army = 0
            for unite_id, unite in joueur.list_unite.items():
                x,y = unite.pos

                #TODO : teleporteur ???
                case = self.list_cases[x][y]
                if case and case.case_function and unite.size > 1:
                    case_functions = {
                            "DIVIDE": self.divide,
                            "MULT": self.mult,
                            "NULL": self.null,
                            "PASS": self.pass_turn,
                            "ENNEMIPASS": self.ennemie_pass
                    }
                    if (fct := case_functions.get(case.case_function)):
                        fct(joueur, case, unite)
                    
                ##ATTAQUE 
                uniteEnnemie = self.verifierEnnemie(unite, (unite.posx, unite.posy))
                if uniteEnnemie:
                    if uniteEnnemie.size>unite.size:
                        uniteEnnemie.size -= unite.size
                        unite.size = 0
                    
                    elif uniteEnnemie.size<unite.size:
                        unite.size -= uniteEnnemie.size
                        uniteEnnemie.size = 0 

                    else:
                        unite.size, uniteEnnemie.size = 0, 0
                joueur.nb_army += unite.size

                if unite.size == 0:
                    unites_to_del.append((joueur, unite_id))

        for joueur, unite_id in unites_to_del:
            del joueur.list_unite[unite_id]
        
    def actualiseCases(self) -> None:
        casesOccupes = []
        for joueur in self.listJoueurs:
            casesOccupes.extend(joueur.get_all_unite_pos())
            
        casesVides = []
        for i in range(NBCASES):
            for j in range(NBCASES):
                case = self.list_cases[i][j]
                if not (i, j) in casesOccupes and not case.case_function:
                    casesVides.append(case)

        if randint(0, 100) < self.proba_case_function:
            choice(casesVides).case_function = choice(self.listFonctionCase)

    def verifierEnnemie(self, parUnite: Unite, pos: Pos) -> Optional[Unite]:
        for joueur in self.listJoueurs:
            for unite_id, unite in joueur.list_unite.items():
                if unite != parUnite and unite.pos == pos:
                    return unite
        return None

    def getNewPos(self, depart: Pos, direction: str) -> Pos:
        if direction == "N":
            if depart[1]>0:
                return (depart[0], depart[1] - 1)
        elif direction == "S":
            if depart[1]<NBCASES-1:
                return (depart[0], depart[1] + 1)
        elif direction == "E":
            if depart[0]<NBCASES-1:
                return (depart[0] + 1, depart[1])
        elif direction == "W":
            if depart[0]>0:
                return (depart[0] - 1, depart[1])
        else:
            print("ERROR")

        return (depart[0], depart[1])

                    
    def handle_command(self, player_id: int, command: str, params: list[str]) -> None:
        commands: dict[str, Callable[[int, list[str]], None]]
        commands = {'MOVE': self.moveUnite}
        command_to_call = commands.get(command)
        if command_to_call:
            command_to_call(player_id, params)

class Interface(Game):
    def __init__(self) -> None:
        super().__init__()
        pygame.init()        
        self.pause = False 
        self.run()

    def run(self) -> None:
        nb_tour = 0
        self.display = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
        self.sprite_soldier = pygame.image.load("sprite/one_soldier.png").convert()
        self.dicoSpriteCaseFunction = {
            "MULT": pygame.image.load("sprite/mult.png").convert(), 
            "DIVIDE": pygame.image.load("sprite/devide.png").convert(), 
            "NULL": pygame.image.load("sprite/null.png").convert(), 
            "PASS": pygame.image.load("sprite/pass.png").convert(), 
            "ENNEMIPASS": pygame.image.load("sprite/ennemiepass.png").convert()
        }

        self.font = pygame.font.Font(None, int(SIZE_CASE/2))
        self.font_unite = pygame.font.Font(None, int(SIZE_CASE*0.8))
        while True:
            if not self.pause:
                self.affichageDamier()
                self.affichageJoueur()

            ##########TEST#################
            #self.TEST.test(nb_tour)
            ##########TEST#################
            command_joueurs = self.serveur.communication(nb_tour)
            for joueur in command_joueurs:
                command, *params = command_joueurs.get(joueur, ("",))
                self.handle_command(int(joueur), command, *params)

            self.actualise()
            self.actualiseCases()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:    
                        self.pause = not self.pause

            pygame.time.wait(1000)
            pygame.display.update()
            nb_tour += 1

    def affichageJoueur(self) -> None:
        for joueur in self.listJoueurs:
            for i in range(NBCASES):
                for unite_id, unite in joueur.list_unite.items():
                    x = 20 + unite.posx * TOTAL_SIZE_LEN
                    y = 20 + unite.posy * TOTAL_SIZE_LEN
                    size = unite.size // 4 + 1
                    for i in range(size):
                        self.display.blit(pygame.transform.scale(self.sprite_soldier, (SIZE_CASE / size, SIZE_CASE)), (x + i * SIZE_CASE/size, y))
                    
                    self.display.blit(self.font_unite.render(str(unite.size), True, BLACK), (x+(SIZE_CASE/3) , (y+(SIZE_CASE/2))))


            self.display.blit(self.font.render(f"{joueur!r}", True, joueur.color), ((WIDTH-300), 200*(joueur.id+1)))

    def affichageDamier(self) -> None:
        self.display.fill(WHITE)
        for i in range(NBCASES):
            for case in self.list_cases[i]:
                if not case:
                    continue

                x = 20 + case.posx * TOTAL_SIZE_LEN
                y = 20 + case.posy * TOTAL_SIZE_LEN

                for lien in case.liens:
                    draw_x, draw_y = (x, y)
                    idx = 1 - (lien.direction[0] != 0)

                    add = [SIZE_LIEN * lien.direction[idx], (SIZE_CASE / 2) - (SIZE_LIEN * lien.width[1 - idx] / 2)]
                    draw_x += add[idx]
                    draw_y += add[1 - idx]

                    pygame.draw.rect(self.display, RED, list(map(int, (draw_x, draw_y, SIZE_LIEN * lien.width[0], SIZE_LIEN * lien.width[1]))))

                if not case.case_function:
                    pygame.draw.rect(self.display, BLUE, list(map(int, (x, y, SIZE_CASE, SIZE_CASE))))
                else:
                    self.display.blit(pygame.transform.scale(self.dicoSpriteCaseFunction[case.case_function], (SIZE_CASE, SIZE_CASE)), (x, y))


class Serveur:
    def __init__(self) -> None:
        print("DEBUG: SERVEUR STARUP")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 5002))
        self.team_name: list[str] = []
        # Attente de la connexion des joueurs
        self.players: list[socket.socket] = []

    def getJoueurs(self) -> None:
        print("[INFO] WAITING FOR PLAYER")
        while len(self.players) < NBJOUEUR:
            self.socket.listen(5)
            client, address = self.socket.accept()
            print(f"[INFO] {address} connected")

            if not (response := client.recv(255).decode()):
                client.send(self.build_message("ERROR", ["Erreur dans la reception du message"]))
                continue

            command, *params = self.parse_message(response)
            if command != 'JOIN' or len(params) != 1:
                client.send(self.build_message("ERROR", ["Vous devez en premier JOIN avec un nom d'équipe"]))
                continue

            print(f"[INFO] Nouveau client accepté avec le nom {params[0]}")
            self.players.append(client)
            self.team_name.append(params[0])


            # Annonce du début de la partie
        print("[INFO] Tous les joueurs ont rejoins, début de la partie")
        for i, player in enumerate(self.players):
            player.send(self.build_message("NEWGAME", [5, NBJOUEUR, i, 0, 0]))

    def communication(self, nbtour: int) -> dict[int, tuple[str, list[str]]]:
        print("DEBUG: WAITING FOR PLAYER MOVE ")
        # Tant que la game tourne
        commande_joueur = {} 
        for player_id, player in enumerate(self.players):
            player.send(self.build_message("NEWTURN", [nbtour]))

            if not (move := player.recv(255).decode()):
                self.error(f"Erreur dans la reception du joueur {player_id}")
                exit()

            # On execute la commande envoyée par le joueur
            command, *params = self.parse_message(move)
            commande_joueur[player_id] = (command, params)
            print(f"[LOG:RECV] {command} {params=}")

        return commande_joueur

    def error(self, msg: str) -> None:
        print(f"[ERROR] {msg}")
        exit()

    def build_message(self, key: str, params: list[Any]) -> bytes:
        msg = f"{key}|{'|'.join(map(str, params))}".encode()
        print(f"[LOG] {msg!r}")
        return msg

    def parse_message(self, msg: str) -> list[str]:
        return [s.upper() for s in msg.split("|")]

if __name__ ==  "__main__":
    seed(10)
    Interface()
