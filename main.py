import sys
import pygame
from random import randrange
import time


# To do:
# -Ameliorer algorithm de mouvement de foule (Si sortie bloquée par foule, partir de la sortie et
# trouver par cercle concentrique le premier point accessible par la foule)
# -Mode edition maintenant par clic continu
# -Remettre en fonction l'affichage du chemin de la foule


# Constantes modifiables
size = width, height = 800, 500
cellules_hauteur = 25
cellules_largeur = 40
portee_ajout_foule = 4  # Portée pour l'ajout de foule
slot = "Slot2.txt"  # Fichier à charger pour la carte
seconde_par_deplacement = 1  # Pas de temps entre chaque déplacement de foule


# Constantes a ne pas toucher
pygame.init()
dico_carte = {}  # Ce dictionnaire contient les informations de toutes les cellules et de leur état
screen = pygame.display.set_mode(size)
horloge = time.process_time()
dico_chemin = {}  # Dictionnaire contenant les cases qui représentent le chemin que les cases foules vont prendre
temps_ancien_deplacement = 0  # Constante interne a l'horloge
dico_memoisation_chemin = {}
couleur_obstacle = (80, 80, 80)  # Gris
couleur_sortie = (52, 201, 36)  # Vert
couleur_foule1 = (240, 128, 128)  # rouge très clair
couleur_foule2 = (205, 92, 92)  # rouge clair
couleur_foule3 = (220, 20, 60)  # rouge moyen
couleur_foule4 = (178, 34, 34)  # rouge vif
couleur_foule5 = (139, 0, 0)  # rouge sombre
# Mode edition, ce dictionnaire contient tous les états actuels du mode edition
bool_edition = {
    'edition': False,
    'obstacle': False,
    'sortie': False,
    'foule': False,
}
demarrer_simulation = False
affichage_chemin = False
##############################


def affichage_console():
    menu = {
        'Mode edition': '(p)',
        'Sauvegarde': '(n)',
        'Afficher/Masquer chemin': '(c)',
        'Démarrer/Arrêter simulation': '(entrer)'
    }
    sous_menu = {
        'Mode edition': [['Ajout obstacle', '(o)'], ['Ajout sortie', '(s)'], ['Ajout foule', '(f)']]
    }
    print("Mode emploi (touches)")
    for key in menu.keys():
        print(f"{menu[key]} : {key}")
        if key in sous_menu.keys():
            for item in sous_menu[key]:
                print(f"    {item[1]} : {item[0]}")

def affichage(cases_changement, tout=False):
    #print(f"affichage de {len(cases_changement)} cases")
    "Permet de gérer l'affichage de l'application"
    taille_largeur = int(size[0] / cellules_largeur)
    taille_hauteur = int(size[1] / cellules_hauteur)

    if tout is True: #Activé quand on ouvre le programme, permet de charger toute la carte
        cases_changement = []
        for i in range(0, cellules_hauteur):
            for j in range(0, cellules_largeur):
                cases_changement.append((i,j))

    # Affichage des cellules sur l'application avec leur couleur respective
    for case in cases_changement:
        j , i = case[0], case[1]
        if (j, i) in dico_carte:  # Regarde si c'est une cellule vide ou si son état est connu
            if dico_carte[(j, i)][0] == 'S':
                couleur = couleur_sortie
            elif dico_carte[(j, i)][0] == 'O':
                couleur = couleur_obstacle
            elif dico_carte[(j, i)][0] == 'F':
                niveau_rouge = dico_carte[(j, i)][1]
                if affichage_chemin is True:  # Affiche en jaune le chemin de chaque case foule
                    afficher_chemin(j, i)
                if niveau_rouge == 1:  # Attribution de la couleur de la foule en fonction de son intensité
                    couleur = couleur_foule1
                elif niveau_rouge == 2:
                    couleur = couleur_foule2
                elif niveau_rouge == 3:
                    couleur = couleur_foule3
                elif niveau_rouge == 4:
                    couleur = couleur_foule4
                else:
                    couleur = couleur_foule5
            else:
                print("Problème de couleur dans le dictionnaire de la carte")
            pygame.draw.rect(screen, couleur,
                             pygame.Rect(i * taille_largeur, j * taille_hauteur, taille_largeur, taille_hauteur))
        elif (j, i) in dico_chemin:  # Si c'est un chemin jaune
            couleur = (255, 255, 0)
            pygame.draw.rect(screen, couleur,
                             pygame.Rect(i * taille_largeur, j * taille_hauteur, taille_largeur, taille_hauteur))
        else:
            # On appelle 2 fois pygame.draw.rect pour 'nettoyer' le fond du carré
            pygame.draw.rect(screen, (0, 0, 0),
                             pygame.Rect(i * taille_largeur, j * taille_hauteur, taille_largeur, taille_hauteur))
            pygame.draw.rect(screen, (255, 255, 255),
                             pygame.Rect(i * taille_largeur, j * taille_hauteur, taille_largeur, taille_hauteur), 1)


def trier_entourage(voisins, case_depart):
    """Prend la liste des voisins proches pour les trier sur les voisins directement proches en priorité plutôt que
    ceux sur les coins"""
    liste_triee = []
    liste_attente = []
    for voisin in voisins:  # On ajoute en premier les voisins direct
        if voisin[0] == case_depart[0] or voisin[1] == case_depart[1]:
            liste_triee.append(voisin)
        else:
            liste_attente.append(voisin)
    for voisin in liste_attente:  # On ajoute à la fin les voisins dans les coins
        liste_triee.append(voisin)
    return liste_triee


def check_entourage(i, j):
    """Cette fonction renvoie la liste de l'entourage vide de la case demandée, ou si la sortie est à proximité"""
    voisins_vides = []
    is_sortie = [False, ()]
    for k in range(-1, 2):
        for l in range(-1, 2):
            coin_licite = True
            if l == 0 and k == 0:  # La case elle-même ne peut pas être son entourage
                print('', end='')  # rien
            elif (l != 0) and (k != 0):  # Si c'est un coin, on vérifie qu'on puisse y accéder
                if (i+k, j) in dico_carte:
                    if dico_carte[(i+k, j)][0] == 'O':
                        coin_licite = False  # Coin inaccessible
                if (i, j+l) in dico_carte:
                    if dico_carte[(i, j+l)][0] == 'O':
                        coin_licite = False  # Coin inaccessible
            if coin_licite is True:
                if (i + k, j + l) not in dico_carte:
                    voisins_vides.append((i + k, j + l))
                elif dico_carte[(i + k, j + l)][0] == 'S':  # Est-ce que la sortie est à proximité ?
                    is_sortie = [True, (i + k, j + l)]
                elif dico_carte[(i + k, j + l)][0] == 'F':  # On ne compte pas la foule comme un obstacle
                    voisins_vides.append((i + k, j + l))
    return is_sortie, trier_entourage(voisins_vides, (i, j))


def pchs(i, j):  # (Plus Court Chemin vers Sortie)
    """Calcul pour chaque foule le plus court chemin en utilisant un parcours en largeur"""
    file_attente = [(i, j)]
    deja_vu = []
    peres = []  # [(fils), (pere)]
    sortie = False
    coord_sortie = []

    chemin_libre = True # On regarde si le chemin est libre
    if (i,j) in dico_memoisation_chemin:
        for case in dico_memoisation_chemin[(i,j)]:
            if case in dico_carte:
                if dico_carte[(case[0], case[1])][0] != "F" and dico_carte[(case[0], case[1])][0] != "S":
                    chemin_libre = False
        if chemin_libre == True:
            return dico_memoisation_chemin[(i,j)]

    while sortie is False:
        if len(file_attente) == 0:
            print("Problème dans le calcul du chemin de la foule, sortie introuvable")
            return [(i, j)]
        else:
            deja_vu.append(file_attente[0])
        is_sortie, voisins = check_entourage(file_attente[0][0], file_attente[0][1])
        if is_sortie[0] is True:  # Est-ce qu'on a trouvé la sortie ?
            sortie = True
            coord_sortie = is_sortie[1]
            peres.append([is_sortie[1], file_attente[0]])
        # Sinon on continue de chercher
        for voisin in voisins:
            if voisin not in deja_vu:
                deja_vu.append(voisin)
                file_attente.append(voisin)
                peres.append([voisin, file_attente[0]])
        file_attente.pop(0)
    chemin_sortie = remonter_peres(peres, coord_sortie, (i, j))
    for i in range(0, len(chemin_sortie)):
        dico_memoisation_chemin[(chemin_sortie[i][0], chemin_sortie[i][1])] = chemin_sortie[:i]
    return chemin_sortie


def remonter_peres(peres, coord_sortie, coord_entree):
    """Fonction complémentaire a la fonction de recherche du plus court chemin, permet de remonter le dictionnaire des
    peres pour afficher la sortie"""
    fin = False  # Tant qu'on n'a pas tout remonté
    chemin = [coord_sortie]
    chemin_actuel = coord_sortie
    while fin is False:
        for lien in peres:
            if lien[0] == chemin_actuel:
                if lien[1] == coord_entree:
                    fin = True
                else:
                    chemin_actuel = lien[1]
                    chemin.append(lien[1])
    return chemin


def valeur_absolu(k):
    if k >= 0:
        return k
    return -k


def str_to_tuple(ligne, type):
    """Permet de convertir un tuple sous forme de string en reel tuple"""
    mont = ligne[1:len(ligne) - 1]  # on enlève les ()
    if type == "int":
        return tuple(map(int, mont.split(', ')))  # On sépare les deux nombres et on les convertit en int, puis en tuple
    return [mont[1], int(mont[5])]


def ajout_foule(i, j):
    """Cette fonction s'occupe de repartir la foule sur le point mentionné lors du mode edition"""
    liste_foule_ajoutee = [] # Tableau contenant toutes les cases de foule générées pour la fonction affichage
    for k in range(-portee_ajout_foule + 1, portee_ajout_foule):
        for l in range(-portee_ajout_foule + 1, portee_ajout_foule):
            if (i + k, j + l) not in dico_carte:
                if randrange(0, valeur_absolu(k) + 1) == 0:
                    dico_carte[(i + k, j + l)] = ["F", 1]
                    liste_foule_ajoutee.append([i+k, j+ l])
            elif dico_carte[(i + k, j + l)][0] == "F" and randrange(0, valeur_absolu(k) + 1) == 0:
                if dico_carte[(i + k, j + l)][1] != 4:
                    dico_carte[(i + k, j + l)][1] += 1
                    liste_foule_ajoutee.append([i + k, j + l])
    affichage(liste_foule_ajoutee)


def enregistrer_carte(dico):
    """Enregistre l'état de toutes les cellules de la carte dans un fichier temporaire"""
    fichier = open("Slot_modification.txt", 'w')
    fichier.write(f"Size_window={width};{height}")
    fichier.write(f"\nSize_tiles={cellules_largeur};{cellules_hauteur}")
    for key, item in dico.items():
        fichier.write(f"\n{key};{item}")
    fichier.close()


def ouvrir_carte():
    """Charge le dictionnaire en charge des cellules depuis un fichier slot.txt"""
    fichier = open(f"{slot}", 'r')
    for ligne in fichier:
        ligne = ligne.rstrip('\n')
        # On vérifie la dimension de la carte/cellules
        if ligne[5] == "w":
            ligne = ligne.split("=")[1].split(";")
            if int(ligne[0]) != width or int(ligne[1]) != height:
                print("Mauvaise dimension de carte")
        elif ligne[5] == "t":
            ligne = ligne.split("=")[1].split(";")
            if int(ligne[0]) != cellules_largeur or int(ligne[1]) != cellules_hauteur:
                print("Mauvaise dimension des cellules")
        #######
        else: # C'est les bonnes dimensions, on charge la carte
            ligne = ligne.split(";")
            dico_carte[str_to_tuple(ligne[0], 'int')] = str_to_tuple(ligne[1], str)
    fichier.close()

def modifier_carreau(x, y):
    """Cette fonction sert à éditer les cellules de la carte pendant le mode edition"""
    j = (cellules_largeur * x) // width  # Colonne de la carte
    i = (cellules_hauteur * y) // height  # Ligne de la carte
    dico_chemin.clear()
    dico_memoisation_chemin.clear()
    if bool_edition['obstacle'] is True:
        dico_carte[(i, j)] = ['O', 0]
    elif bool_edition['sortie'] is True:
        dico_carte[(i, j)] = ['S', 0]
    elif bool_edition['foule'] is True:
        ajout_foule(i, j)
    else:
        if (i, j) in dico_carte:
            del (dico_carte[(i, j)])
        else:
            print("Erreur, il n'y a rien a faire sur cette cases")
    affichage([[i,j]])


def edition(lettre):
    """Cette fonction edition permet de gérer l'activation du mode edition et modes d'ajouts comme les obstacles/sorties
    sans conflits entre eux"""
    # 112:p, 115:s, 111:o
    numero_lettre = {
        111: 'obstacle',  # lettre o
        112: 'edition',  # lettre p
        115: 'sortie',  # lettre s
        102: 'foule',  # lettre f
        13: 'demarrer_simu'  # lettre entrer
    }
    if lettre == 112:  # Cette partie permet d'activer ou de desactiver le mode edition
        if bool_edition['edition'] is False:
            bool_edition['edition'] = True
            print("Mode edition active")
        else:
            for key in bool_edition.keys():  # Si on désactive le mode edition, on désactive tous les modes d'ajouts
                bool_edition[key] = False
            print("Mode edition désactive")
    else:  # Cette partie permet de verifier si un autre mode d'ajout n'est pas déjà activé pour éviter un conflit
        if bool_edition['edition'] is True:
            autorisation = True
            for key in bool_edition.keys():
                if key != 'edition' and key != numero_lettre[lettre] and bool_edition[key] is True:
                    print(f"Désactivez le mode ajout {key} avant")
                    autorisation = False
            if autorisation is True:  # Aucun autre mode n'est activé, on peut donc l'activer ou le désactiver
                if bool_edition[numero_lettre[lettre]] is True:
                    bool_edition[numero_lettre[lettre]] = False
                    print(f"Mode ajout {numero_lettre[lettre]} desactivé")
                else:
                    bool_edition[numero_lettre[lettre]] = True
                    print(f"Mode ajout {numero_lettre[lettre]} active")
        else:  # Un autre mode est activé, on prévient l'utilisateur
            print("Activez le mode edition avant!")


def deplacement_foule(i, j):
    """Déplace d'une case la foule vers la sortie"""
    chemin = pchs(i, j)
    if (i, j) == chemin[len(chemin) - 1]:
        print("Erreur, une case foule essaye d'aller sur elle même")
    elif len(chemin) != 0:
        future_case = chemin[len(chemin) - 1]
        if future_case not in dico_carte:
            dico_carte[future_case] = dico_carte[(i, j)]
            del dico_carte[(i, j)]
        elif dico_carte[future_case][0] == 'F':
            if dico_carte[future_case][1] + dico_carte[(i, j)][1] <= 5:  # Quand deux foules peuvent se combiner
                dico_carte[future_case][1] = dico_carte[future_case][1] + dico_carte[(i, j)][1]
                del dico_carte[(i, j)]
            elif dico_carte[future_case][1] != 5:  # Quand seulement une partie de la foule peut se combiner
                dico_carte[(i, j)][1] -= 5 - dico_carte[future_case][1]
                dico_carte[future_case][1] = 5
        elif dico_carte[future_case][0] == 'S':  # Quand il atteint la sortie on le supprime
            #print(f"La foule numéro {coord_to_identite(i,j)} a trouvé la sortie !")
            del dico_carte[(i, j)]
        else:
            print("Problème dans le déplacement d'une case foule")
    affichage([[i, j], future_case])


def afficher_chemin(i, j):
    """Permet d'afficher le chemin en jaune qu'un 'carré' foule va poursuivre"""
    chemin_sortie = pchs(i, j)
    for case in chemin_sortie:
        dico_chemin[(case[0], case[1])] = 'J'
    affichage(dico_chemin)



ouvrir_carte()  # On charge le dictionnaire qui contient les informations des cases de la carte
affichage_console()  # Affichage du menu
affichage([[0,0]],tout=True) # On affiche toute la carte pour la charger
while 1:
    for event in pygame.event.get():
        # print(event)
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            if bool_edition['edition'] is True:
                modifier_carreau(x, y)
        if event.type == pygame.KEYDOWN:
            # print(event)
            if event.key == 27:
                sys.exit()
            if event.key == 112 or event.key == 115 or event.key == 111 or event.key == 102:
                edition(event.key)
            if event.key == 110:
                print("Sauvegarde!")
                enregistrer_carte(dico_carte)
            if event.key == 13:  # entrer
                if demarrer_simulation is False:
                    demarrer_simulation = True
                    print("Simulation démarrée!")
                else:
                    demarrer_simulation = False
                    print("Simulation stoppée!")
            if event.key == 99:  # c
                print("Fonctionnalité désactivée")
                """if affichage_chemin is False:
                    affichage_chemin = True
                    print("Chemin affiché!")
                else:
                    affichage_chemin = False
                    print("Chemin masqué!")
                    dico_chemin.clear()"""
        if event.type == pygame.QUIT:
            enregistrer_carte(dico_carte)
            sys.exit()

    # Déplacement de la foule
    horloge = time.perf_counter()
    if horloge >= temps_ancien_deplacement + seconde_par_deplacement and (
            demarrer_simulation is True):  # Pour afficher un déplacement par pas de temps
        temps_ancien_deplacement = horloge
        dico_chemin.clear()
        liste_foule_a_deplacer = []# Liste chacun des 'carrés' foule à faire bouger
        for i in range(0, cellules_hauteur):
            for j in range(0, cellules_largeur):
                if (i,j) in dico_carte:
                    if dico_carte[(i, j)][0] == 'F':
                        liste_foule_a_deplacer.append((i,j))
        for case in liste_foule_a_deplacer:
            deplacement_foule(case[0], case[1])


    ##################################
    pygame.display.flip()
