#from distutils import command
#from msilib.schema import Error
from pygame.locals import *
from random import randint, choice, seed
import pygame, sys, string, socket


NBJOUEUR=2
NBCASES=10
HEIGHT=1000
BASE_UNITE_SIZE=12
WIDTH=HEIGHT+400
WHITE=(255,255,255)
BLUE=(0,100,255)
RED=(255,0,0)
BLACK=(0,0,0)


class Case():
 
    def __init__(self,parid:int,x:int,y:int):        
        self.id=parid
        self.posx=x
        self.posy=y
        self.liens=set()
        self.case_function=None 

        

class Lien():
    def __init__(self,parfrom,parto):
        self.fromCase=parfrom
        self.toCase=parto
        self.direction=[(self.toCase.posx-self.fromCase.posx),(self.toCase.posy-self.fromCase.posy)]
        self.enable=True
        if self.direction[0]:
            #E & W 
            self.width=(1,0.35)
        else:
            # UP & DPWN 
            self.width=(0.35,1)
        
        #self.fromCase.liens.add(self)

#Groupe



class Joueur():
    def __init__(self,parid,parnom,parpos,parcolor,parcase):
        self.nbcase=parcase
        self.id=parid
        self.nom=parnom
        self.color=parcolor
        #self.pos=parpos
        self.nbUnite=0
        self.nbArmy=BASE_UNITE_SIZE
        self.listUnite=[[None for j in range(self.nbcase)] for i in range(self.nbcase)]
        self.listUnite[parpos[0]][parpos[1]]=Unite(self,self.nbUnite,parpos,self.nbArmy)


    def getUniteById(self,idUnite:int):
        for i in range(self.nbcase):
            for unite in self.listUnite[i]:
                if unite and  unite.id==idUnite:
                    return unite
        return None 

class Unite(Joueur):
    def __init__(self,joueur,parid,parpos:tuple,parsize:int):
        self.joueur=joueur
        self.size=parsize
        self.posx,self.posy=parpos
        self.id=parid

class Game():
    def __init__(self):

        #DEFINE: Element
        self.nbcases=NBCASES
        self.nbjoueur=NBJOUEUR
        self.positionJoueur=[(0,0),(self.nbcases-1,self.nbcases-1),(self.nbcases-1,0),(0,self.nbcases-1)]
        

        #DEFINE: Style
        self.colorJoueur=[(0,255,0),(255, 160, 122),(240, 15, 220),(0,0,0)]
        self.nblien=self.nbcases-1
        self.size_lien=(0.35*(HEIGHT-40))/self.nblien
        self.size_case=(0.65*(HEIGHT-40))/self.nbcases
        

        #DEFINE: Reseau
        self.serveur=Serveur()
        self.serveur.getJoueurs()
        

        #DEFINE: Joueurs
        self.joueurs=[Joueur(i,self.serveur.teamName[i],self.positionJoueur[i],self.colorJoueur[i],self.nbcases) for i in range(len(self.serveur.players))]


        #DEFINE: jeu
        self.listCases=[[None for j in range(self.nbcases)] for i in range(self.nbcases)]
        self.createCases()
        self.proba_case_function=3 #proba de 0.03 au debut 
        self.listFonctionCase=["DIVIDE","MULT","NULL"]
        self.casesVide=[]
        self.nbcase_with_function=0
        # case function 
        #self.listCases[1][0].case_function ="DEVIDE"
        #self.listCases[self.nbcases-1][self.nbcases-2].case_function ="MULT"
        #########################


        self.createLiens()
 
    def createCases(self):
        for i in range(self.nbcases*self.nbcases):
            self.listCases[i%self.nbcases][i//self.nbcases]=Case(i,i%self.nbcases,i//self.nbcases)



    
    def createLiens(self):
        for ligne in range(self.nbcases):
            for thecase in self.listCases[ligne]:                
                voisins=([(thecase.posx+k[0],thecase.posy+k[1])  for k in [(-1,0),(0,-1),(1,0),(0,1)]])
                for voisin in voisins:
                    if -1<voisin[0]<self.nbcases and -1<voisin[1]<self.nbcases:
                        if self.listCases[voisin[0]][voisin[1]]:
                            thecase.liens.add(Lien(thecase,self.listCases[voisin[0]][voisin[1]]))
        
    def moveUnite(self,idJoueur:int,params:list):
        #unite=self.joueurs[idJoueur].listUnite[posfrom[0]][posfrom[1]]
        idUnite,parsize,direction=params
        idUnite,parsize=int(idUnite),int(parsize)
        unite=self.joueurs[idJoueur].getUniteById(idUnite)

        #getUniteByPos(posfrom)
        if unite and direction!="M" and self.listCases[unite.posx][unite.posy].case_function!="NULL" :   
            ##MOUVEMENT
            posfrom=(unite.posx,unite.posy)
            newpos=self.getNewPos(posfrom,direction)
            if self.verifierLien(posfrom,newpos):   
                if parsize<unite.size or not (unite.size-parsize): 
                    newpos_unite=self.joueurs[idJoueur].listUnite[newpos[0]][newpos[1]]
                    #getUniteByPos(newpos)
                    unite.size-=parsize
                    if newpos_unite:
                        newpos_unite.size+=parsize
                    else: 
                        self.joueurs[idJoueur].nbUnite+=1
                        newUnite=Unite(self.joueurs[idJoueur],self.joueurs[idJoueur].nbUnite,newpos,parsize)
                        self.joueurs[idJoueur].listUnite[newpos[0]][newpos[1]]=newUnite
                elif parsize==unite.size:
                    self.joueurs[idJoueur].listUnite[unite.posx][unite.posy]=None
                    self.joueurs[idJoueur].listUnite[newpos[0]][newpos[1]]=unite
                    unite.posx,unite.posy=newpos

                else: print(f"{idJoueur} ERROR: PAS ASSEZ DE SOLDAT")
            else: print(f" {idJoueur} ERROR: LIEN INUTILISABLE") 
        else: print(f"{idJoueur} ERROR: PAS D'UNITE A CETTE POSITION")


    def actualise(self):
        for joueur in self.joueurs:
            joueur.nbArmy=0
            for i in range(self.nbcases):
                for j in range(self.nbcases):
                    unite=joueur.listUnite[j][i]
                    
                    if not unite:
                        self.casesVide.append(self.listCases[j][i])
                        continue

                    #TODO : ajout fonction de la case : /2 unite \ *2 unite \ Passe sont prochain tour \ passe le tour de l'adversaire \ case detruite
                    case=self.listCases[unite.posx][unite.posy]
                    if case.case_function and unite.size>1:
                        if case.case_function =="DEVIDE":
                            unite.size//=2
                            case.case_function=None
                        elif case.case_function =="MULT":
                            unite.size*=2
                            case.case_function=None
                        
                    ##ATTAQUE 
                    
                    uniteEnnemie= self.verifierEnnemie(unite,(unite.posx,unite.posy))
                    if uniteEnnemie:
                        if uniteEnnemie.size>unite.size:
                            uniteEnnemie.size-=unite.size
                            unite.size=0
                        
                        elif uniteEnnemie.size<unite.size:
                            unite.size-=uniteEnnemie.size
                            uniteEnnemie.size=0 

                        else:
                            unite.size,uniteEnnemie=0,0
                    joueur.nbArmy+=unite.size

                    if unite.size==0:
                        joueur.listUnite[unite.posx][unite.posy]=None
        
    def actualiseCases(self):
        for case in self.casesVide:
            if case.case_function or self.nbcase_with_function > self.nbcases :
                continue
            if randint(0, 100)<self.proba_case_function:
                self.nbcase_with_function+=1
                case.case_function=choice(self.listFonctionCase)
        self.proba_case_function+=1
        self.casesVide=[]




    def verifierEnnemie(self,parUnite,pos:tuple):
        for joueur in self.joueurs:
            for i in range(self.nbcases):
                for unite in joueur.listUnite[i]:
                    if not unite:
                        continue
                    if unite!=parUnite and (unite.posx,unite.posy)==pos:
                        return unite
        return None

    def getNewPos(self,depart:tuple,direction:string)->tuple:
        if direction=="N":
            if depart[1]>0:
                return (depart[0],depart[1]-1)
        elif direction=="S":
            if depart[1]<self.nbcase-1:
                return (depart[0],depart[1]+1)
        elif direction=="E":
            if depart[0]<self.nbcases-1:
                return (depart[0]+1,depart[1])
        elif direction=="W":
            if depart[0]>0:
                return (depart[0]-1,depart[1])
        else:
            print("ERROR")
        return (depart[0],depart[1])

                    
    def verifierLien(self,depart:tuple,newpos:tuple)->bool:
        for lien in self.listCases[depart[0]][depart[1]].liens:
            if (lien.toCase.posx,lien.toCase.posy)==newpos:
                return lien.enable
        return None 

class Interface(Game):
    def __init__(self):
        super().__init__()


        
        pygame.init()        
        self.pause=False 

        self.run()


    def run(self):

        nb_tour=0
        self.display=pygame.display.set_mode((WIDTH,HEIGHT),0,32)
        self.sprite_soldier=[pygame.image.load( "sprite/one_soldier.png").convert(),pygame.image.load( "sprite/two_soldier.png").convert() ,pygame.image.load( "sprite/three_soldier.png").convert()]

        self.font=pygame.font.Font(None, 50)
        self.font_unite=pygame.font.Font(None, int(self.size_case*0.8))
        while True:
            if not self.pause:
                self.affchageDamier()
                self.affichageJoueur()

            ##########TEST#################
            #self.TEST.test(nb_tour)
            ##########TEST#################
            try:
                    
                commandJoueur=self.serveur.communication(nb_tour)
                for key in commandJoueur:
                    if commandJoueur[key][0]=="MOVE":
                        self.moveUnite(key,commandJoueur[key][1])
            except Exception as e:
                print(f"ERROR: {e} ")    

            self.actualise()
            self.actualiseCases()




            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_SPACE:    
                        if not self.pause:
                            print("DEBUG: PAUSE!!!!!!")
                            self.pause=True
                        else:
                            self.pause=False
            pygame.time.wait(1000)
            pygame.display.update()
            nb_tour+=1


    def affichageJoueur(self):
        for joueur in self.joueurs:
            for i in range(self.nbcases):
                for unite in joueur.listUnite[i]:
                    if not unite:
                        continue
                    print(f"DEBUG: {unite.id=} {unite.size=}")
                    #  WITHOUT SPRITE ###########
                    #x=(20+unite.posx*(self.size_case+self.size_lien))+self.size_case/2
                    #y=(20+unite.posy*(self.size_case+self.size_lien))+self.size_case/2
                    #pygame.draw.circle(self.display, joueur.color, (x, y), (self.size_case)*0.5,int(self.size_case*0.5)) 
                    #self.display.blit(self.font_unite.render(str(unite.size),1,BLACK), (x-(self.size_case/3) , (y-(self.size_case/4))))
                    #########################
                    x=(20+unite.posx*(self.size_case+self.size_lien))
                    y=(20+unite.posy*(self.size_case+self.size_lien))
                    self.display.blit(pygame.transform.scale(self.sprite_soldier[((unite.size-1)//4)], (self.size_case, self.size_case)),(x , y))
                    self.display.blit(self.font_unite.render(str(unite.size),1,BLACK), (x+(self.size_case/3) , (y+(self.size_case/2))))


            self.display.blit(self.font.render(str(joueur.nom)+" :  "+str(joueur.nbArmy),1,joueur.color), ((WIDTH-300), 200*(joueur.id+1)))

    def affchageDamier(self):
        self.display.fill(WHITE)
        for i in range(self.nbcases):
            for case in self.listCases[i]:
                if not case:
                    continue

                x=(20+case.posx*(self.size_case+self.size_lien))
                y=(20+case.posy*(self.size_case+self.size_lien))
                if not case.case_function:
                    pygame.draw.rect(self.display,BLUE,(x,y,self.size_case,self.size_case))
                else:
                    pygame.draw.rect(self.display,(0,0,0),(x,y,self.size_case,self.size_case))
                #for lien in case.listLien:
                tmp=(x,y)
                for lien in case.liens:
                    x,y=tmp
                    #W
                    if lien.direction==[-1,0]:
                        x-=self.size_lien
                        y+=((self.size_case/2)-(self.size_lien*lien.width[1]/2))
                    #E
                    elif lien.direction==[1,0]:
                        x+=self.size_case
                        y+=((self.size_case/2)-(self.size_lien*lien.width[1]/2))
                    #UP
                    elif lien.direction==[0,-1]:
                        x+=((self.size_case/2)-(self.size_lien*lien.width[0]/2))
                        y-=self.size_lien
                    #DOWN
                    elif lien.direction==[0,+1]:
                        x+=((self.size_case/2)-(self.size_lien*lien.width[0]/2))
                        y+=self.size_case

                    pygame.draw.rect(self.display,RED,(x,y,self.size_lien*lien.width[0],self.size_lien*lien.width[1]))

#ZONE TEST




class Serveur():
    def __init__(self):
        print("DEBUG: SERVEUR STARUP")
        self.maxPlayer = NBJOUEUR

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 5000))
        self.teamName=[]
        # Attente de la connexion des joueurs
        self.players = []

    def getJoueurs(self):
        print("[INFO] WAITING FOR PLAYER")
        while len(self.players) < self.maxPlayer:
            self.socket.listen(5)
            client, address = self.socket.accept()
            print(f"[INFO] {address} connected")

            response = client.recv(255).decode()
            if not response:
                client.send(self.build_message("ERROR", ["Erreur dans la reception du message"]))
                continue

            command, *params = self.parse_message(response)
            if command != 'JOIN' or len(params) != 1:
                client.send(self.build_message("ERROR", ["Vous devez en premier JOIN avec un nom d'équipe"]))
                continue

            print(f"[INFO] Nouveau client accepté avec le nom {params[0]}")
            self.players.append(client)
            self.teamName.append(params[0])


            # Annonce du début de la partie
        print("[INFO] Tous les joueurs ont rejoins, début de la partie")
        for i, player in enumerate(self.players):
            player.send(self.build_message("NEWGAME", [5, self.maxPlayer, i, 0, 0]))

    def communication(self,nbtour):
        print("DEBUG: WAITING FOR PLAYER MOVE ")
        # Tant que la game tourne
        commandeJoueur={} 
        for player_id, player in enumerate(self.players):
            player.send(self.build_message("NEWTURN", [nbtour]))
            # Envoie de tous les nouveaux événements
            move = player.recv(255).decode()

            # Si cela arrive, c'est qu'un
            if not move:
                self.error(f"Erreur dans la reception du joueur {player_id}")
                exit()

            # On execute la commande envoyée par le joueur
            command, *params = self.parse_message(move)
            err = self.handle_command(player_id, command, params)
            commandeJoueur[player_id]=(command,params)
            # Si une erreur a eu lieu, on quite directement le programme 
            # (cela signifie que le code du client n'est pas bon)
            if err:
                self.error("ERROR: COMMANDE INTROUVABLE")

        return commandeJoueur

    def error(self,msg):
        print(f"[ERROR] {msg}")
        exit()

    def build_message(self,key, params):
        msg = f"{key}|{'|'.join(map(str, params))}".encode()
        print(f"[LOG] {msg}")
        return msg

    def parse_message(self,msg):
        return [s.upper() for s in msg.split("|")]

    def move_player(self,player_id, params):
        direction = params[0]
        return (0, "")

    def handle_command(self,player_id, command, params):
        commands = {'MOVE',"STAY"}
        return not command in commands











if __name__== "__main__":
    seed(10)
    Interface()
