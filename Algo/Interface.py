from pygame.locals import *
from random import randint, choice, seed
from dataclasses import dataclass, field
from typing import Optional
import pygame, sys, socket


NBJOUEUR = 2
NBCASES = 6
HEIGHT = 1000
BASE_UNITE_SIZE = 12
WIDTH = HEIGHT+400
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


@dataclass
class Case:
    case_id: int
    posx: int
    posy: int
    liens: set = field(default_factory=set)
    case_function = None

    @property
    def pos(self):
        return (self.posx, self.posy)

@dataclass(eq = True, frozen = True)
class Lien:
    from_case: tuple[int, int]
    to_case: tuple[int, int]

    @property
    def direction(self):
        return [(self.to_case[0] - self.from_case[0]), (self.to_case[1] - self.from_case[1])]

    @property
    def width(self) -> tuple[float, float]:
        return (1, 0.35) if self.direction[0] else (0.35, 1)

class Joueur:
    def __init__(self, joueur_id, nom, default_pos, color, nb_case):
        self.id = joueur_id
        self.nb_case = nb_case
        self.nom = nom
        self.color = color
        self.nb_unite = 0
        self.nb_army = BASE_UNITE_SIZE
        self.list_unite = {}
        self.list_unite[0] = Unite(self.nb_unite, default_pos, BASE_UNITE_SIZE)
        self.can_play = True

    def get_unite_by_id(self, idUnite: int):
        a = self.list_unite.get(idUnite)
        print(f"[GET] {idUnite=} / {self.list_unite=}")
        return a

    def get_unite_at(self, pos):
        for unite in self.list_unite.values():
            if unite.pos == pos:
                return unite
        return None

    def get_all_unite_pos(self):
        return [unite.pos for unite in self.list_unite.values()]

@dataclass
class Unite:
    unite_id: int
    pos: tuple[int, int]
    size: int

    @property
    def posx(self):
        return self.pos[0]

    @property
    def posy(self):
        return self.pos[1]

class Game:
    def __init__(self) -> None:
        self.nbcases = NBCASES
        self.nbjoueur = NBJOUEUR
        self.positionJoueur = [(0, 0), (self.nbcases-1, self.nbcases-1), (self.nbcases-1, 0), (0, self.nbcases-1)]
        

        #DEFINE: Style
        self.colorJoueur = [(0, 255, 0), (255, 160, 122), (240, 15, 220), (0, 0, 0)]
        self.nblien = self.nbcases-1
        self.size_lien = (0.35*(HEIGHT-40))/self.nblien
        self.size_case = (0.65*(HEIGHT-40))/self.nbcases
        

        #DEFINE: Reseau
        self.serveur = Serveur()
        self.serveur.getJoueurs()
        

        #DEFINE: Joueurs
        self.listJoueurs = [Joueur(i, self.serveur.team_name[i], self.positionJoueur[i], self.colorJoueur[i], self.nbcases) for i in range(len(self.serveur.players))]


        #DEFINE: jeu
        self.listCases = [[None for j in range(self.nbcases)] for i in range(self.nbcases)]
        self.createCases()
        self.proba_case_function = 5 #proba de 0.03 au debut 
        self.listFonctionCase = ["DIVIDE", "MULT", "NULL", "PASS", "ENNEMIPASS"]
        self.nbcase_with_function = 0
        # case function 
        #self.listCases[1][0].case_function  = "DEVIDE"
        #self.listCases[self.nbcases-1][self.nbcases-2].case_function  = "MULT"
        #########################


        self.createLiens()
 
    def createCases(self):
        for i in range(self.nbcases*self.nbcases):
            self.listCases[i%self.nbcases][i//self.nbcases] = Case(i, i%self.nbcases, i//self.nbcases)

    def createLiens(self):
        for ligne in range(self.nbcases):
            for thecase in self.listCases[ligne]:                
                voisins = ([(thecase.posx+k[0], thecase.posy+k[1])  for k in [(-1, 0), (0, -1), (1, 0), (0, 1)]])
                for voisin in voisins:
                    if -1<voisin[0]<self.nbcases and -1<voisin[1]<self.nbcases:
                        if self.listCases[voisin[0]][voisin[1]]:
                            thecase.liens.add(Lien(thecase.pos, self.listCases[voisin[0]][voisin[1]].pos))
        
    def moveUnite(self, idJoueur:int, params:list):
        idUnite, parsize, direction = params
        idUnite, parsize = int(idUnite), int(parsize)
        joueur = self.listJoueurs[idJoueur]
        unite = joueur.get_unite_by_id(idUnite)

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

    def actualise(self):
        unites_to_del = []
        for joueur in self.listJoueurs:
            joueur.nb_army = 0
            for unite_id, unite in joueur.list_unite.items():
                x,y = unite.pos

                #TODO : teleporteur ???
                case = self.listCases[x][y]
                if case.case_function and unite.size > 1:
                    if case.case_function == "DEVIDE":
                        unite.size //= 2
                        case.case_function = None
                    elif case.case_function == "MULT":
                        unite.size *= 2
                        case.case_function = None
                    elif case.case_function == "NULL":
                        unite.size = 0
                    elif case.case_function == "PASS":
                        joueur.can_play = False
                    elif case.case_function == "ENNEMIPASS":
                        for j2 in self.listJoueurs:
                            if j2 != joueur:
                                j2.can_play = False
                    
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
                        unite.size, uniteEnnemie = 0, 0
                joueur.nb_army += unite.size

                if unite.size == 0:
                    unites_to_del.append((joueur, unite_id))

        for joueur, unite_id in unites_to_del:
            del joueur.list_unite[unite_id]
        
    def actualiseCases(self):
        casesOccupes = []
        for joueur in self.listJoueurs:
            casesOccupes.extend(joueur.get_all_unite_pos())
            
        casesVides = []
        for i in range(self.nbcases):
            for j in range(self.nbcases):
                if not (i, j) in casesOccupes and not self.listCases[i][j].case_function:
                    casesVides.append(self.listCases[i][j])

        if randint(0, 100) < self.proba_case_function:
            choice(casesVides).case_function = choice(self.listFonctionCase)

    def verifierEnnemie(self, parUnite, pos:tuple):
        for joueur in self.listJoueurs:
            for unite_id, unite in joueur.list_unite.items():
                if unite != parUnite and unite.pos == pos:
                    return unite
        return None

    def getNewPos(self, depart:tuple, direction:str)->tuple[int, int]:
        if direction == "N":
            if depart[1]>0:
                return (depart[0], depart[1] - 1)
        elif direction == "S":
            if depart[1]<self.nbcases-1:
                return (depart[0], depart[1] + 1)
        elif direction == "E":
            if depart[0]<self.nbcases-1:
                return (depart[0] + 1, depart[1])
        elif direction == "W":
            if depart[0]>0:
                return (depart[0] - 1, depart[1])
        else:
            print("ERROR")

        return (depart[0], depart[1])

                    
    def handle_command(self, player_id, command, params):
        commands = {'MOVE': self.moveUnite, "STAY": lambda x: x}
        commands.get(command)(player_id, params[0])

class Interface(Game):
    def __init__(self):
        super().__init__()

        pygame.init()        
        self.pause = False 
      
        self.run()


    def run(self):
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

        self.font = pygame.font.Font(None, int(self.size_case/2))
        self.font_unite = pygame.font.Font(None, int(self.size_case*0.8))
        while True:
            if not self.pause:
                self.affichageDamier()
                self.affichageJoueur()

            ##########TEST#################
            #self.TEST.test(nb_tour)
            ##########TEST#################
            command_joueurs = self.serveur.communication(nb_tour)
            for joueur in command_joueurs:
                command, *params = command_joueurs.get(joueur)
                self.handle_command(joueur, command, params)

            self.actualise()
            self.actualiseCases()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:    
                        self.pause = not self.pause

            pygame.time.wait(1000)
            pygame.display.update()
            nb_tour += 1

    def affichageJoueur(self):
        for joueur in self.listJoueurs:
            for i in range(self.nbcases):
                for unite_id, unite in joueur.list_unite.items():
                    x = (20+unite.posx*(self.size_case+self.size_lien))
                    y = (20+unite.posy*(self.size_case+self.size_lien))
                    size = (unite.size//4)+1
                    for i in range(size):
                        self.display.blit(pygame.transform.scale(self.sprite_soldier, ((self.size_case/size), self.size_case)), (x+(i*(self.size_case/size)) , y))
                    
                    self.display.blit(self.font_unite.render(str(unite.size), True, BLACK), (x+(self.size_case/3) , (y+(self.size_case/2))))


            self.display.blit(self.font.render(str(joueur.nom)+" :  "+str(joueur.nb_army), True, joueur.color), ((WIDTH-300), 200*(joueur.id+1)))

    def affichageDamier(self):
        self.display.fill(WHITE)
        for i in range(self.nbcases):
            for case in self.listCases[i]:
                if not case:
                    continue

                x = (20+case.posx*(self.size_case+self.size_lien))
                y = (20+case.posy*(self.size_case+self.size_lien))

                for lien in case.liens:
                    draw_x, draw_y = (x, y)
                    idx = 1 - (lien.direction[0] != 0)

                    add = [self.size_lien * lien.direction[idx], (self.size_case / 2) - (self.size_lien * lien.width[1 - idx] / 2)]
                    draw_x += add[idx]
                    draw_y += add[1 - idx]

                    pygame.draw.rect(self.display, RED, (draw_x, draw_y, self.size_lien * lien.width[0], self.size_lien * lien.width[1]))

                if not case.case_function:
                    pygame.draw.rect(self.display, BLUE, (x, y, self.size_case, self.size_case))
                else:
                    self.display.blit(pygame.transform.scale(self.dicoSpriteCaseFunction[case.case_function], (self.size_case, self.size_case)), (x , y))


class Serveur():
    def __init__(self):
        print("DEBUG: SERVEUR STARUP")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 5002))
        self.team_name = []
        # Attente de la connexion des joueurs
        self.players = []

    def getJoueurs(self):
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

    def communication(self, nbtour):
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

    def error(self, msg):
        print(f"[ERROR] {msg}")
        exit()

    def build_message(self, key, params):
        msg = f"{key}|{'|'.join(map(str, params))}".encode()
        print(f"[LOG] {msg}")
        return msg

    def parse_message(self, msg):
        return [s.upper() for s in msg.split("|")]

if __name__ ==  "__main__":
    seed(10)
    Interface()
