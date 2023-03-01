# https://github.com/sauvajohnz
import sys
import pygame
from random import randrange
import time

# To do:
# -Mode edition maintenant par clic continu
# -Remettre en fonction l'affichage du chemin de la foule
# -Vérification de la carte avant le lancement d'une simulation

########################### CONSTANTES MODIFIABLES ########################################

##Modification de la carte ##

# width : largeur de la fenêtre en pixel
# height : hauteur de la fenêtre en pixel
size = width, height = 800, 500

# cellules_hauteur : nombre de cellules sur une colonne
# cellules_largeur : nombre de cellules sur une ligne
cellules_hauteur = 25
cellules_largeur = 40

## Modification du comportement du programme ##

# portee_ajout_foule : portée en case de l'ajout de foule (pour ajouter beaucoup de cases foule rapidement)
portee_ajout_foule = 4

# slot : fichier text à charger pour charger la carte de simulation
slot = "Slot_lucien.txt"

# seconde_par_deplacement : temps en seconde à attendre au minimum entre chaque tour
seconde_par_deplacement = 1

# distance_maximale_effort : cercle maximal de déplacement d'une case foule (sur un seul tour)
distance_maximale_effort = 9
###########################################################################################


# Constantes a ne pas toucher
pygame.init()
dico_carte = {}  # Ce dictionnaire contient les informations de toutes les cellules et de leur état
dico_distance_euclidienne = {}
dico_pchs = {}
screen = pygame.display.set_mode(size)
horloge = time.process_time()
sorties = []
dico_chemin = {}  # Dictionnaire contenant les cases qui représentent le chemin que les cases foules vont prendre
temps_ancien_deplacement = 0  # Constante interne a l'horloge
nombre_tours_simulation = 0
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
    """Affiche le menu pour modifier le programme pendant son fonctionnement"""
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


def fusion(gauche, droite):
    """Fonction complémentaire pour tri foule en fusion"""
    resultat = []
    index_gauche, index_droite = 0, 0
    while index_gauche < len(gauche) and index_droite < len(droite):
        if gauche[index_gauche][1] <= droite[index_droite][1]:
            resultat.append(gauche[index_gauche])
            index_gauche += 1
        else:
            resultat.append(droite[index_droite])
            index_droite += 1
    if gauche:
        resultat.extend(gauche[index_gauche:])
    if droite:
        resultat.extend(droite[index_droite:])
    return resultat


def tri_foule(tableau):
    """Trie par fusion les élements dans l'ordre croissant d'un tableau de tableau en fonction de son deuxième element
    exemple : [[element1, 33], [element2, 28]] devient [[element2, 28], [element1, 33]]
    """
    if len(tableau) <= 1:
        return tableau
    milieu = len(tableau) // 2
    gauche = tableau[:milieu]
    droite = tableau[milieu:]
    gauche = tri_foule(gauche)
    droite = tri_foule(droite)
    return list(fusion(gauche, droite))


def distance_euclidienne(i, j, chemin):
    """Calcul la longueur d'un chemin en mètres (1 case = 1 mètre)"""
    chemin.reverse()  # Car le chemin commence au dernier indice

    if len(chemin) == 0:
        return 0
    longueur_chemin = 0
    case_precedente = (i, j)  # On initialise
    for k in range(0, len(chemin)):
        if chemin[k][0] != case_precedente[0] and chemin[k][1] != case_precedente[1]:  # Longueur d'une diagonale
            longueur_chemin += 1.41  # Racine carrée de 2
        elif chemin[k][0] != case_precedente[0] or chemin[k][1] != case_precedente[1]:  # Longueur d'un côté
            longueur_chemin += 1
        elif chemin[k][0] == case_precedente[0] and chemin[k][1] == case_precedente[1]:  # Elle se déplace sur elle même
            return 0
        else:
            print("Problème dans le calcul de la distance euclidienne")
        case_precedente = chemin[k]
    chemin.reverse()
    return longueur_chemin


def affichage(cases_changement, tout=False):
    "Permet de gérer l'affichage de l'application"
    taille_largeur = int(size[0] / cellules_largeur)
    taille_hauteur = int(size[1] / cellules_hauteur)

    if tout is True:  # Activé quand on ouvre le programme, permet de charger toute la carte
        cases_changement = []
        for i in range(0, cellules_hauteur):
            for j in range(0, cellules_largeur):
                cases_changement.append((i, j))

    # Affichage des cellules sur l'application avec leur couleur respective
    for case in cases_changement:
        j, i = case[0], case[1]
        if (j, i) in dico_carte:  # Regarde si c'est une cellule vide ou si son état est connu
            if dico_carte[(j, i)][0] == 'S':
                couleur = couleur_sortie
            elif dico_carte[(j, i)][0] == 'O':
                couleur = couleur_obstacle
            elif dico_carte[(j, i)][0] == 'C':
                couleur = (255, 255, 0)
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


def verification_carte():  # Pas implémentée
    """Vérifie avant chaque simulation que toutes les zones sont accessibles et chaque sortie également, en laissant
    la possibilité à l'utilisateur de lancer quand même"""

    # Erreur trouvée
    input("Continuer quand même? (O/N)\n>")


def check_sortie():
    """Actualise la variable globale "sorties" """
    sorties.clear()
    for key, item in dico_carte.items():
        if item[0] == 'S':
            sorties.append(key)


def determiner_dico_distance_euclidienne():
    dico_distance_euclidienne.clear()
    for sortie in sorties:
        dico_distance_euclidienne[(sortie[0], sortie[1])] = 0
        liste_attente = [(sortie[0], sortie[1])]
        deja_vu = [()]
        fin = False
        while fin is False:
            case = (liste_attente[0][0], liste_attente[0][1])
            deja_vu.append(case)

            voisins = check_entourage(case[0], case[1], [], distance_non_euclidienne=True)[1]
            for voisin in voisins:
                distance_sortie = 0
                # On regarde si c'est un voisin diagonal ou un voisin direct
                if case[0] != voisin[0] and case[1] != voisin[1]:  # Voisin diagonal
                    distance_sortie = dico_distance_euclidienne[case] + 1.41
                elif case[0] != voisin[0] or case[1] != voisin[1]:  # Voisin direct
                    distance_sortie = dico_distance_euclidienne[case] + 1
                else:
                    distance_sortie = 99999

                if voisin in dico_distance_euclidienne:
                    if dico_distance_euclidienne[voisin] > distance_sortie:
                        dico_distance_euclidienne[voisin] = distance_sortie
                else:
                    dico_distance_euclidienne[voisin] = distance_sortie

                if voisin not in deja_vu and voisin not in liste_attente:
                    liste_attente.append(voisin)
            liste_attente.pop(0)
            if len(liste_attente) == 0:
                fin = True


def determiner_dico_pchs():
    """Determine le plus court chemin en distance euclidienne vers la sortie pour chaque case en ne prenant pas en
    compte la foule comme obstacle """
    dico_pchs.clear()
    for i in range(0, cellules_hauteur):
        for j in range(0, cellules_largeur):
            calcul_autorise = False
            if (i, j) in dico_carte:
                if dico_carte[(i, j)][0] == "F":
                    calcul_autorise = True
            else:
                calcul_autorise = True

            if calcul_autorise is True:
                sortie_trouve, _ = check_entourage(i, j, sorties)  # Le check_entourage renvoie l'entourage dans
                # l'ordre du plus court vers la sortie en distance euclidienne
                chemin = [(i, j)]
                while sortie_trouve[0] is False:
                    sortie_trouve, prochain_chemin = check_entourage(chemin[len(chemin) - 1][0],
                                                                     chemin[len(chemin) - 1][1], sorties)
                    if sortie_trouve[0] is False:
                        while prochain_chemin[0] in chemin:
                            prochain_chemin.pop(0)
                        chemin.append(prochain_chemin[0])
                chemin.append(sortie_trouve[1])
                chemin.pop(0)
                chemin.reverse()
                dico_pchs[(i, j)] = chemin


def trier_entourage_distance_euclidienne(voisins, case_depart):
    """Prend la liste des voisins proches pour les trier selon leur distance à la sortie la plus proche"""
    liste_triee = []
    for voisin in voisins:
        if voisin[0] != case_depart[0] and voisin[1] != case_depart[1]:
            liste_triee.append([voisin, dico_distance_euclidienne[voisin] + 1.41])
        elif voisin[0] != case_depart[0] or voisin[1] != case_depart[1]:
            liste_triee.append([voisin, dico_distance_euclidienne[voisin] + 1])
        else:
            liste_triee.append([voisin, dico_distance_euclidienne[voisin]])
    liste_triee = tri_foule(liste_triee)
    return [voisin[0] for voisin in liste_triee]


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


def determiner_cercle_maximal_effort(i, j, rayon):
    "Determine le cercle voisin d'un cellule d'un certain rayon donné"
    liste_attente_future = [(i, j)]
    deja_vu = []
    for _ in range(0, rayon + 1):
        liste_attente_actuelle = [case for case in liste_attente_future]
        liste_attente_future.clear()
        for case in liste_attente_actuelle:
            deja_vu.append(case)
            voisins = check_entourage(case[0], case[1], [], distance_non_euclidienne=False)[1]
            for voisin in voisins:
                if (voisin not in deja_vu) and (voisin not in liste_attente_actuelle) and (
                        voisin not in liste_attente_future):
                    if abs(voisin[0] - i) + abs(voisin[1] - j) < 2 * rayon:
                        if voisin not in dico_carte:
                            liste_attente_future.append(voisin)

    for case in liste_attente_future:
        deja_vu.append(case)
    return deja_vu


def check_entourage(i, j, tableau_sortie, foule=False, distance_non_euclidienne=False):
    """Cette fonction renvoie la liste de l'entourage vide de la case demandée, ou si la sortie est à proximité"""
    voisins_vides = []
    is_sortie = [False, ()]
    for k in range(-1, 2):
        for l in range(-1, 2):
            coin_licite = True
            if l == 0 and k == 0:  # La case elle-même ne peut pas être son entourage
                print('', end='')  # rien
            elif (l != 0) and (k != 0):  # Si c'est un coin, on vérifie qu'on puisse y accéder
                if (i + k, j) in dico_carte:
                    if dico_carte[(i + k, j)][0] == 'O':
                        coin_licite = False  # Coin inaccessible
                if (i, j + l) in dico_carte:
                    if dico_carte[(i, j + l)][0] == 'O':
                        coin_licite = False  # Coin inaccessible
            if (i + k) < 0 or (j + l) < 0:
                coin_licite = False  # Hors de la carte
            if coin_licite is True:
                if (i + k, j + l) in tableau_sortie:
                    is_sortie = [True, (i + k, j + l)]
                    return is_sortie, trier_entourage(voisins_vides, (i, j))
                if (i + k, j + l) not in dico_carte:
                    voisins_vides.append((i + k, j + l))
                elif dico_carte[(i + k, j + l)][
                    0] == 'F' and foule is False:  # On ne compte pas la foule comme un obstacle
                    voisins_vides.append((i + k, j + l))
    if distance_non_euclidienne is False:
        return is_sortie, trier_entourage_distance_euclidienne(voisins_vides, (i, j))  # très instable
    return is_sortie, trier_entourage(voisins_vides, (i, j))


def pchs(i, j, tab_sortie, foule_as_obstacle=False):  # (Plus Court Chemin vers Sortie)
    """Calcul pour chaque foule le plus court chemin en utilisant un parcours en largeur"""
    file_attente = [(i, j)]
    deja_vu = []
    peres = []  # [(fils), (pere)]
    sortie = False
    coord_sortie = []
    # Pour ne pas recalculer inutilement plusieurs fois le même chemin, on regarde si le chemin à déjà été calculer
    # pour une case, puis on vérifie qu'il marche toujours.

    chemin_libre = True
    if (i, j) in dico_memoisation_chemin and foule_as_obstacle is False and tab_sortie == sorties:
        for case in dico_memoisation_chemin[(i, j)]:
            if case in dico_carte:
                if dico_carte[(case[0], case[1])][0] != "F" and dico_carte[(case[0], case[1])][0] != "S":
                    del dico_memoisation_chemin[(i, j)]
                    chemin_libre = False
        if chemin_libre == True:
            return dico_memoisation_chemin[(i, j)]

    # Début de l'algorithme de parcours en largeur
    while sortie is False:

        if len(file_attente) == 0:  # Dans le cas ou on a déjà parcourue toute la carte
            if foule_as_obstacle is True:
                return deja_vu, False
            print("Problème dans le calcul du chemin de la foule, sortie introuvable")
            return [(i, j)]
        else:
            deja_vu.append(file_attente[0])

        is_sortie, voisins = check_entourage(file_attente[0][0], file_attente[0][1], tab_sortie,
                                             foule=foule_as_obstacle)
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
    if foule_as_obstacle is False and len(tab_sortie) == 0:
        for i in range(0, len(chemin_sortie)):
            dico_memoisation_chemin[(chemin_sortie[i][0], chemin_sortie[i][1])] = chemin_sortie[:i]
    if foule_as_obstacle is True:
        return chemin_sortie, True
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
    liste_foule_ajoutee = []  # Tableau contenant toutes les cases de foule générées pour la fonction affichage
    for k in range(-portee_ajout_foule + 1, portee_ajout_foule):
        for l in range(-portee_ajout_foule + 1, portee_ajout_foule):
            if (i + k, j + l) not in dico_carte:
                if randrange(0, valeur_absolu(k) + 1) == 0:
                    dico_carte[(i + k, j + l)] = ["F", 1]
                    liste_foule_ajoutee.append([i + k, j + l])
            # FONCTIONNALITEE A REMETTRE
            """elif dico_carte[(i + k, j + l)][0] == "F" and randrange(0, valeur_absolu(k) + 1) == 0:
                if dico_carte[(i + k, j + l)][1] != 4:
                    dico_carte[(i + k, j + l)][1] += 1
                    liste_foule_ajoutee.append([i + k, j + l])"""
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
        else:  # C'est les bonnes dimensions, on charge la carte
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
            dico_carte.pop((i, j))
        else:
            print("Erreur, il n'y a rien a faire sur cette cases")
    affichage([[i, j]])


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
            check_sortie()
            determiner_dico_distance_euclidienne()
            determiner_dico_pchs()
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
                    print(f"Mode ajout {numero_lettre[lettre]} désactivé")
                else:
                    bool_edition[numero_lettre[lettre]] = True
                    print(f"Mode ajout {numero_lettre[lettre]} active")
        else:  # Un autre mode est activé, on prévient l'utilisateur
            print("Activez le mode edition avant!")


def deplacement_foule(i, j, distance_sortie):
    """Déplace d'une case la foule vers la sortie"""
    chemin_sortie = pchs(i, j, sorties)
    cercle_effort = determiner_cercle_maximal_effort(i, j, distance_maximale_effort)

    chemin_inverse = pchs(chemin_sortie[0][0], chemin_sortie[0][1], cercle_effort)
    chemin_sans_sortie, est_sortie = pchs(i, j, [(chemin_inverse[0][0], chemin_inverse[0][1])], foule_as_obstacle=True)
    est_sortie, _ = check_entourage(i, j, sorties)

    if est_sortie[0] is True:  # Si la sortie est dans l'entourage, la future case est donc la sortie
        chemin = [est_sortie[1]]
    else:  # Sinon,
        chemin = []
        for case in chemin_sans_sortie:
            chemin.append(case)

    if len(chemin) != 0:
        future_case = chemin[len(chemin) - 1]
        if future_case not in dico_carte:
            dico_carte[future_case] = dico_carte[(i, j)]
            del dico_carte[(i, j)]
        elif dico_carte[future_case][0] == 'S':  # Quand il atteint la sortie on le supprime
            del dico_carte[(i, j)]
        elif dico_carte[future_case][0] == 'F':
            print('', end='')  # A fixer, c'est quand deux foules s'emboitent
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
check_sortie()
determiner_dico_distance_euclidienne()
determiner_dico_pchs()
affichage_console()  # Affichage du menu
affichage([[0, 0]], tout=True)  # On affiche toute la carte pour la charger
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
                    if bool_edition['edition'] is False:
                        # verification_carte()
                        demarrer_simulation = True
                        print("Simulation démarrée!")
                        nombre_tours_simulation = 0
                    else:
                        print("Désactivez le mode édition avant de démarrer la simulation!")
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
        liste_foule_a_deplacer = []  # Liste chacun des 'carrés' foule à faire bouger, boucle imbriquée pour obtenir les
        # cordonnées de toutes les cases foule
        for i in range(0, cellules_hauteur):
            for j in range(0, cellules_largeur):
                if (i, j) in dico_carte:
                    if dico_carte[(i, j)][0] == 'F':
                        liste_foule_a_deplacer.append((i, j))
        if len(liste_foule_a_deplacer) == 0:
            print(f"Nombre de tours : {nombre_tours_simulation}")
            print("Simulation terminée!")
            demarrer_simulation = False
        nombre_tours_simulation += 1

        # On calcule la distance de chaque case foule avec la sortie, puis on le range par ordre croissant
        # On peut se permettre de faire un parcours en largeur de chaque foule juste pour connaître la distance
        # avec la sortie, car ce calcul a déjà été fait, il est mémoîsé.
        for k in range(0, len(liste_foule_a_deplacer)):
            case = liste_foule_a_deplacer[k]
            liste_foule_a_deplacer[k] = [(case[0], case[1]),
                                         distance_euclidienne(case[0], case[1], dico_pchs[(case[0], case[1])])]
        # On trie selon les cases foule les plus proches de la sortie
        liste_foule_a_deplacer = tri_foule(liste_foule_a_deplacer)
        # Puis on les déplace
        for case in liste_foule_a_deplacer:
            deplacement_foule(case[0][0], case[0][1], case[1])

    pygame.display.flip()
