import pygame, sys, string
from pygame.locals import *
from random import randint

NBJOUEUR=2
NBCASES=10
HEIGHT=1000
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
        #self.case_function

    def getLienById(self,parid:int): 
        for lien in self.liens:
            if lien.id==parid:
                return lien          
        return None

    def getLienByPosTo(self,pos:tuple):
        for lien in self.liens:
            if (lien.toCase.posx,lien.toCase.posy)==pos:
                return lien          
        return None
        

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
class Unite():
    def __init__(self,parid,parpos:tuple,parsize:int):
        self.size=parsize
        self.posx,self.posy=parpos
        self.id=parid


class Joueur():
    def __init__(self,parid,parnom,parpos,parcolor,parcase):
        self.nbcase=parcase
        self.id=parid
        self.nom=parnom
        self.color=parcolor
        self.pos=parpos
        self.nbUnite=12
        self.listUnite={Unite(0,parpos,self.nbUnite)}

    def getUniteByPos(self,pos:tuple)->Unite:
        for unite in self.listUnite:
            if (unite.posx,unite.posy) ==pos:
                return unite
        return None


class Game():
    def __init__(self,nbcases:int,nbjoueur:int):
        if nbjoueur>4:
            print("ERROR: TROP DE JOUEURS")

        self.nbcases=nbcases
        self.nbjoueur=nbjoueur
        self.positionJoueur=[(0,0),(self.nbcases-1,self.nbcases-1),(self.nbcases-1,0),(0,self.nbcases-1)]
        self.colorJoueur=[(0,255,0),(255, 160, 122),(240, 15, 220),(0,0,0)]

        self.nblien=nbcases-1
        self.size_lien=(0.35*(HEIGHT-40))/self.nblien
        self.size_case=(0.65*(HEIGHT-40))/self.nbcases
        
        self.joueurs=[Joueur(i,"Player "+str(i+1),self.positionJoueur[i],self.colorJoueur[i],self.nbcases) for i in range(self.nbjoueur)]
        self.cases=set()
        self.createCases()
        self.createLiens()
 
    def createCases(self):
        for i in range(self.nbcases*self.nbcases):
            self.cases.add(Case(i,i%self.nbcases,i//self.nbcases))
    
    def createLiens(self):
        for thecase in self.cases:
            voisin=set([(thecase.posx+k[0],thecase.posy+k[1])  for k in [(-1,0),(0,-1),(1,0),(0,1)]])
            for case in self.cases:
                if (case.posx,case.posy) in voisin:
                    thecase.liens.add(Lien(thecase,case))

    def moveUnite(self,idJoueur:int,parsize:int,posfrom:tuple,direction:string):
        print(f"DEBUG: moveUnite {idJoueur=} {posfrom=} {direction=}")
        unite=self.joueurs[idJoueur].getUniteByPos(posfrom)
        if unite:
            
            newpos=self.getNewPos(posfrom,direction)
            if self.verifierLien(posfrom,newpos):   

                if parsize<=unite.size:
                    newpos_unite=self.joueurs[idJoueur].getUniteByPos(newpos)
                    unite.size-=parsize
                    if newpos_unite:
                        newpos_unite.size+=parsize
                    else: 
                        newUnite=Unite(len(self.joueurs[idJoueur].listUnite),newpos,parsize)
                        self.joueurs[idJoueur].listUnite.add(newUnite)

                    if unite.size==0:
                        self.joueurs[idJoueur].listUnite.remove(unite)

                else: print("ERROR: PAS ASSEZ DE SOLDAT")
            else: print("ERROR: LIEN INUTILISABLE")
        else: print("ERROR: PAS D'UNITE A CETTE POSITION")


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
        for case in self.cases:
            if (case.posx,case.posy)==depart:
                lien=case.getLienByPosTo(newpos)
                if lien:
                    return lien.enable
        return None 

class Interface(Game):
    def __init__(self,nbcases,nbjoueur):
        super().__init__(nbcases,nbjoueur)

        self.TEST=TEST(self)

        pygame.init()        
        self.pause=False 
        self.run()


    def run(self):

        nb_tour=0
        self.display=pygame.display.set_mode((WIDTH,HEIGHT),0,32)
        self.font=pygame.font.Font(None, 50)
        self.font_unite=pygame.font.Font(None, int(self.size_case*0.8))
        while True:
            
            if not self.pause:
                self.affchageDamier()
                self.affichageJoueur()

            ##########TEST#################
            self.TEST.test(nb_tour)
            ##########TEST#################



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
            for unite in joueur.listUnite:
                x=(20+unite.posx*(self.size_case+self.size_lien))+self.size_case/2
                y=(20+unite.posy*(self.size_case+self.size_lien))+self.size_case/2
                pygame.draw.circle(self.display, joueur.color, (x, y), (self.size_case)*0.5,int(self.size_case*0.5)) 
                self.display.blit(self.font_unite.render(str(unite.size),1,BLACK), (x-(self.size_case/3) , (y-(self.size_case/4))))


            self.display.blit(self.font.render(str(joueur.nom)+" :  "+str(joueur.nbUnite),1,joueur.color), ((WIDTH-300), 200*(joueur.id+1)))

    def affchageDamier(self):
        self.display.fill(WHITE)
        for case in self.cases:
            x=(20+case.posx*(self.size_case+self.size_lien))
            y=(20+case.posy*(self.size_case+self.size_lien))
            pygame.draw.rect(self.display,BLUE,(x,y,self.size_case,self.size_case))
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
class TEST():
    def __init__(self,game:Game):
        self.game=game
        self.size_map=NBCASES

    def test(self,nb_tour:int):
        #print("TEST: tour:",nb_tour)
        # N , S ,E, W
        if nb_tour==0:
            self.game.moveUnite(0,5,(0, 0),"E")
            self.game.moveUnite(1,5,(self.size_map-1,self.size_map-1),"E")
        elif nb_tour==1:
            self.game.moveUnite(1,5,(self.size_map-1,self.size_map-1),"W")
            self.game.moveUnite(0,5,(0, 0),"E")
        elif nb_tour==3:
            self.game.moveUnite(0,1,(0, 0),"E")
            self.game.moveUnite(1,3,(self.size_map-1,self.size_map-1),"W")
        elif nb_tour==4:
            self.game.moveUnite(1,4,(self.size_map-1,self.size_map-1),"W")

        elif nb_tour==4:
            self.game.moveUnite(1,4,(self.size_map-1,self.size_map-1),"W")

        #else:self.game.pause=True








if __name__== "__main__":
    Interface(NBCASES,NBJOUEUR)
