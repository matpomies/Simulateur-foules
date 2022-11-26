import sys, pygame
from random import randrange

#Print a refaire correctement
print("Mode emploi (touches) :\n(p) : Mode edition\n(o) : Ajout obstacle\n(s) : Ajout sortie\n(f): Ajout foule\n(n): Sauvegarde")


########Mise en forme globale de l'application###########
pygame.init()
size = width, hight = 800, 500
screen = pygame.display.set_mode(size)
cellules_hauteur = 25 #Nombre de cellules en hauteur
cellules_largeur = 40 #Nombre de cellules en largeur
dico_carte = {} #Ce dictionnaire contient les informations de toutes les cellules et de leur état
#slot = "Slot_modification.txt" #Permet de charger des cellules deja predefinies
slot = "Slot2.txt"

#Couleurs
#https://web-color.aliasdmc.fr/couleur-web-red-rgb-hsl-hexa.html  #Site utilisé pour les couleurs de rouge
couleur_obstacle = (80, 80, 80) #Gris
couleur_sortie = (52, 201, 36) #Vert
couleur_foule1 = (240,128,128) #rouge très clair
couleur_foule2 = (205,92,92) #rouge clair
couleur_foule3 = (220,20,60) #rouge moyen
couleur_foule4 = (255,0,0) #rouge vif
couleur_foule5 = (139,0,0) #rouge sombre

#Parametres foules
portee_ajout_foule = 4
##############################


#Mode edition, ce dictionnaire contient tous les etats actuels du mode edition
bool_edition = {
    'edition': False,
    'obstacle': False,
    'sortie': False,
    'foule': False
}

def valeur_absolu(k):
    if k>=0:
        return k
    return -k

def str_to_tuple(str):
    """Permet de convertir un tuple sous forme de string en reel tuple"""
    mont = str[1:len(str) - 1] # on enleve les ()
    return tuple(map(int, mont.split(', '))) #On separe les deux nombres et on les convertis en int, puis en tuple

def ajout_foule(i, j):
    """Cette fonction s'occupe de repartir la foule sur le point mentionné lors du mode edition"""
    for k in range(-portee_ajout_foule + 1 ,portee_ajout_foule):
        for l in range(-portee_ajout_foule + 1 ,portee_ajout_foule):
            if (i+k, j+l) not in dico_carte:
                if randrange(0,valeur_absolu(k)+1) == 0:
                    dico_carte[(i+k, j+l)] = "F"
            elif dico_carte[(i+k, j+l)] == "F":
                print("", end='') # Pour l'instant rien, on va rajouter les niveaux de foule après

def enregistrer_carte(dico):
    """Enregistre l'etat de toutes les cellules de la carte dans un fichier temporaire"""
    fichier = open("Slot_modification.txt", 'w')
    fichier.write(f"Size_window={width};{hight}")
    fichier.write(f"\nSize_tiles={cellules_largeur};{cellules_hauteur}")
    for key,item in dico.items():
        fichier.write(f"\n{key};{item}")
    fichier.close()


def ouvrir_carte():
    """Charge le dictionnaire en charge des cellules depuis un fichier slot.txt"""
    fichier = open(f"{slot}", 'r')
    for ligne in fichier:
        ligne = ligne.rstrip('\n')
        ##On verifie la dimension de la carte/cellules
        if ligne[5] == "w":
            ligne = ligne.split("=")[1].split(";")
            if int(ligne[0]) != width or int(ligne[1]) != hight:
                print("Mauvaise dimension de carte")
        elif ligne[5] == "t":
            ligne = ligne.split("=")[1].split(";")
            if int(ligne[0]) != cellules_largeur or int(ligne[1]) != cellules_hauteur:
                print("Mauvaise dimension des cellules")
        #######
        else:
            ligne = ligne.split(";")
            dico_carte[str_to_tuple(ligne[0])] = str(ligne[1])
    fichier.close()


def modifier_carreau(x, y):
    "Cette fonction sert a éditer les cellules de la carte pendant le mode edition"
    j = (cellules_largeur*x)//width # Colonne de la carte
    i = (cellules_hauteur*y)//hight # Ligne de la carte
    if bool_edition['obstacle'] is True:
        dico_carte[(i, j)] = 'O'
    elif bool_edition['sortie'] is True:
        dico_carte[(i, j)] = 'S'
    elif bool_edition['foule'] is True:
        ajout_foule(i,j)
    else:
        if (i, j) in dico_carte:
            del(dico_carte[(i, j)])
        else:
            print("Erreur, il n'y a rien a faire sur cette cases")

def edition(lettre):
    "Cette fonction edition permet de gérer l'activation du mode edition et modes d'ajouts comme les obstacles/sorties sans conflits entre eux"
    #112:p, 115:s, 111:o
    numero_lettre = {
        111: 'obstacle', #lettre o
        112: 'edition', #lettre p
        115: 'sortie', #lettre s
        102: 'foule' #lettre f
        }

    if lettre == 112: #Cette partie permet d'activer ou de desactiver le mode edition
        if bool_edition['edition'] is False:
            bool_edition['edition'] = True
            print("Mode edition active")
        else:
            for key in bool_edition.keys(): #Si on desactive le mode edition, on desactive tous les modes d'ajouts
                bool_edition[key] = False
            print("Mode edition desactive")
    else: #Cette partie permet de verifier si un autre mode d'ajout n'est déjà activer pour éviter un conflit
        if bool_edition['edition'] is True:
            autorisation = True
            for key in bool_edition.keys():
                if key != 'edition' and key != numero_lettre[lettre] and bool_edition[key] is True:
                    print(f"Desactivez le mode ajout {key} avant")
                    autorisation = False

            if autorisation is True: #Aucun autre mode n'est activé, on peut donc l'activer ou le désactiver
                if bool_edition[numero_lettre[lettre]] is True:
                    bool_edition[numero_lettre[lettre]] = False
                    print(f"Mode ajout {numero_lettre[lettre]} desactive")
                else:
                    bool_edition[numero_lettre[lettre]] = True
                    print(f"Mode ajout {numero_lettre[lettre]} active")
        else: #Un autre mode est activé, on previent l'utilisateur
            print("Activez le mode edition avant!")

ouvrir_carte() #On charge le dictionnaire qui contient les informations des cases de la carte

while 1:
    for event in pygame.event.get():
        #print(event)
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            if bool_edition['edition'] == True:
                modifier_carreau(x, y)
        if event.type == pygame.KEYDOWN:
            #print(event)
            if event.key == 27:
                sys.exit()
            if event.key == 112 or event.key == 115 or event.key == 111 or event.key == 102:
                edition(event.key)
            if event.key == 110:
                print("Sauvegarde!")
                enregistrer_carte(dico_carte)
        if event.type == pygame.QUIT:
            enregistrer_carte(dico_carte)
            sys.exit()


    #############Quadrillage###########
    taille_largeur = size[0]/cellules_largeur
    taille_hauteur = size[1]/cellules_hauteur

    #Affichage des cellules sur l'application avec leur couleur respective
    for i in range(0, cellules_largeur):
        for j in range(0, cellules_hauteur):
            if (j, i) in dico_carte: #Regarde si c'est une cellule vide ou si son état est connu
                if dico_carte[(j,i)] == 'S':
                    couleur = couleur_sortie
                elif dico_carte[(j,i)] == 'O':
                    couleur = couleur_obstacle
                elif dico_carte[(j,i)] == 'F':
                    couleur = couleur_foule4
                else:
                    print("Probleme de couleur dans le dictionnaire de la carte")
                pygame.draw.rect(screen, couleur, pygame.Rect(i * taille_largeur, j * taille_hauteur, taille_largeur, taille_hauteur))
            else:
                pygame.draw.rect(screen, (255,255,255), pygame.Rect(i*taille_largeur, j*taille_hauteur, taille_largeur, taille_hauteur), 1)
    ##################################



    pygame.display.flip()