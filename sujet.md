---
header-includes:
  - \hypersetup{colorlinks=false,
            allbordercolors={0 0 0},
            pdfborderstyle={/S/U/W 1}}

title: "A la guerre comme à la guerre"
author: [Evann Berthou, Benjamin Pellieux]
date: "2022-00-00"
fontsize: 11pt
geometry: margin=0.75in

---


# Sujet: A la guerre comme à la guerre

## Contexte
**Ecrire une histoire bidon**

## Règles du jeu
Le jeu se déroule sous forme de jeu tour par tour. Le plateau est constitué d'une grille carré de taille qui est donné par le serveur au lancement de la partie.
Chaque équipe commence avec un groupe de 10 unités. A chaque tour, le joueur peut effectuer une action. (__[Voir API](#API)__)

La subtilité du jeu se trouve dans le système de "combat" entre groupe d'unités. Lorsqu'une équipe déplace son groupe sur un unité adversaire, alors il ne reste sur la
case que la soustraction du nombre des deux unités. 

Ex: L'équipe A déplace son groupe de 8 unités sur une case où 5 unités de l'équipe B sont présents. Il ne reste alors que 3 unités de l'équipe A sur la case (et l'équipe B
perd ses unités). Si égalité, les deux groupes disparaissent.

La partie se termine quand il ne reste plus qu'une seule équipe sur la plateau ou que le nombre de tour maximum est atteint.
De plus, à chaque tour, des évènements aléatoires peuvent avoir lieu (__[Voir Events](#Events)__). Ces évènements peuvent être des bonus ou des malus.

## Objectif
Ce jeu n'est pas à jouer en tant réel. L'objectif est de coder une IA afin que le jeu puisse jouer tout seul.
Le client échange avec le serveur mais jamais le serveur renvoie son état. C'est-à-dire que c'est au client
de garder une trace des déplacements de ses adversaires, d'où ont eu lieu les événements, etc...

Il faut donc coder une IA plus intelligente que son adversaire afin de gagner la partie.
Bien entendu, lorsque l'on parle d'IA, on ne parle pas de machine learning ou de technique avancée. Il s'agit simplement d'analyse simple de l'état de la partie
afin de pouvoir prendre une décision.

Le serveur est fournis, vous devez uniquement coder le client (pas d'interface graphique, juste des échanges d'informations à travers de l'API).

# Echange entre le serveur et le client
Le serveur est celui qui s'occupe de relier toutes les équipes entre elles, ainsi que d'être le maitre de la partie. Il possède toute l'autorité et vérifie que les 
actions faites ne sont pas illégales d'après les règles du jeu. Tout passage des règle signifie la défaite de l'équipe.

Afin de pouvoir échanger des informations avec le serveur, il faut utiliser des **Socket** (indication importante). Les échanges se font à travers des commandes
définies dans la section API

\pagebreak

## API {#API}
Toutes les commandes se présentent sous la forme suivante : **COMMANDE|PARAM1|PARAM2|...** que ça soit pour les messages à envoyer ou les messages reçu.

### Vers serveur

| Commande   | Arguments           | Description                                                            |
|------------|---------------------|------------------------------------------------------------------------|
| JOIN       | NOM                 | Rejoins la partie avec ce nom d'équipe                                 |
| MOVE       | GROUPE, NOMBRE, DIR | Déplace NOMBRE unités du groupe GROUPE dans la direction DIR (N,S,E,W) |

### Depuis serveur

| Commande    | Arguments         | Description                                                                               |
|-------------|-------------------|-------------------------------------------------------------------------------------------|
| NEWGAME     | N,K,I,X,Y         | Indique qu'une nouvelle partie avec un tableau de taille n\*n et k équipes va commencer.  | 
|             |                   | L'équipe commence sur la case (x,y) et possède l'id i                                     |
| NEWTURN     | N                 | Indique à l'équipe que c'est à son tour de jouer.                                         |
|             |                   | De plus, indique que N nouveaux événemnets sont à traiter                                 |
| EVENT       | X,Y, TYPE, PARAMS | Description d'un nouveau événement qui a lieu sur la case (x,y).                          |
|             |                   | Voir la section Event pour plus de détails sur les types.                                 |
| ERROR       | MSG               | Une erreur a eu lieu, avec sa raison                                                      |


### Les types d'event {#Events}

| ID | Arguments               | Description                                                                               |
|----|-------------------------|-------------------------------------------------------------------------------------------|
| 0  | ID, GROUPE, NOMBRE, DIR | L'équpe ID a déplacé NOMBRE unité de son groupe GROUPE dans la direction DIR (N, S, E, W) |
| 1  | /                       | Une case qui double le nombre d'unité qui lui marche dessus en premier                    |
| 2  | A,B                     | Crée un téléporteur qui téléporte relie la case (X,Y) et (A,B)                            |
| 3  | TEMPS                   | Cette case devient inaccessible pendant TEMPS tours                                       |

\pagebreak

## Déroulement d'une partie
```
Connexion par socket
Envoyer le nom d'équipe
Recevoir le numéro joueur, et de la position de départ
TANT QUE la partie n'est pas terminée
    Attendre NEWTURN
    Traiter les nouveaux événements
    Préparer son coup 
    Envoyer son coup (Un seul coup chaque tour)
FIN TANT QUE
```


## Partie hacking
**A FAIRE**
