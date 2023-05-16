#----------------------------------------------------------------------
# Auteur: https://github.com/sauvajohnz
# Programme réalisé pour un TIPE sur les mouvements de foule
#----------------------------------------------------------------------

import pygame
import sys
from visualisation_annexes.CaseInfo import *
from visualisation_annexes.CaseSauvegarder import *
from visualisation_annexes.CaseSupprimer import *
import matplotlib.pyplot as plt



# ---------------------------------------------------------------
# TO DO :

#   [ ] Relier au programme principal pour effectuer des simulations automatiques

# ---------------------------------------------------------------


# ---------------------------------------------------------------
# -- Variables du programme (à ne pas toucher) --
couleur_fond_graphique = (0,120,120)
couleur_contour_graphique = (255, 255, 255)
size = width, height = 1000, 500
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(size)
font_graphique = pygame.font.SysFont('freesansbold.ttf', 15)
points_graphique = [(40,40)]


bouton_foule_pourcentage_depart = CaseInfo(60, 10, "foule_pourcentage_depart", screen)
bouton_densite_maximale_supportee = CaseInfo(110, 10, "densite_maximale_supportee", screen)
bouton_densite_sortie = CaseInfo(160, 10, "densite_sortie", screen)
bouton_densite_deplacement_0pourcent = CaseInfo(330, 10, "densité déplacement à 0%", screen)
bouton_densite_deplacement_900pourcent = CaseInfo(370, 10, "densité déplacement à 900%", screen)
bouton_supprimer = CaseSupprimer(130, 430, screen)
bouton_sauvegarder = CaseSauvegarder(650, 430, screen)
liste_valeurs = [bouton_densite_maximale_supportee, bouton_foule_pourcentage_depart, bouton_densite_sortie]
liste_boutons = [bouton_densite_sortie, bouton_densite_maximale_supportee, bouton_foule_pourcentage_depart,
                 bouton_sauvegarder, bouton_supprimer, bouton_densite_deplacement_900pourcent, bouton_densite_deplacement_0pourcent]
# ---------------------------------------------------------------


# --- PROGRAMME PRINCIPAL ---

def conversion_graph_pixel(point):
    """Convertis les coordonnées du graphique en cordonnés pixels"""
    return (point[0]*6/9 + 10, (100 - point[1])*4 + 10)


def conversion_pixel_graph(point):
    """Convertis les coordonnées pixels en cordonnées du graphique"""
    return ((point[0] - 10)*9/6, 100 - (point[1] - 10)/4)


def placer_point(point):
    """Place un point graphiquement à partir de deux coordonnées du graphique"""
    point_pixel = conversion_graph_pixel(point)
    pygame.draw.circle(screen, (255,255,255), point_pixel, 3)


def sauvegarder_graphique():
    """Sauvegarde les points du graphique"""
    with open("visualisation_annexes/points_graphique.txt", "w") as fichier:
        for point in points_graphique:
            fichier.write(f"({int(point[0])},{int(point[1])})\n")


def sauvegarder_parametres():
    """Sauvegarde tous les paramètres du programme"""
    with open("parametres.txt", "w") as fichier:
        # On met en forme le tableau des valeurs dans un string
        tableau_deplacement_foule = calculer_tableau()
        string_tableau_deplacement_foule = ""
        for valeur in tableau_deplacement_foule:
            string_tableau_deplacement_foule += f"{round(valeur/100,3)},"
        string_tableau_deplacement_foule = string_tableau_deplacement_foule[:-1] # On retire la dernière virgule
        string_tableau_deplacement_foule += "\n"
        fichier.write(string_tableau_deplacement_foule)

        # On enregistre ensuite la valeur des variables
        for variable in liste_valeurs:
            fichier.write(f"{variable.get_nom()}:{variable.get_valeur()}\n")


def importer_parametres():
    """Importe les paramètres du programme"""
    with open("parametres.txt", "r") as fichier:
        lignes = fichier.readlines()
        lignes.pop(0)
        for ligne in lignes:
            ligne = ligne.split(':')
            if ligne[0] == "densite_maximale_supportee":
                bouton_densite_maximale_supportee.set_valeur(ligne[1].split("\n")[0])
            elif ligne[0] == "foule_pourcentage_depart":
                bouton_foule_pourcentage_depart.set_valeur(ligne[1].split("\n")[0])
            elif ligne[0] == "densite_sortie":
                bouton_densite_sortie.set_valeur(ligne[1].split("\n")[0])
            else:
                print("Erreur dans l'importation des paramètres : paramètre inconnu")


def importer_graphique():
    """Importe les points du graphique"""
    points = []
    with open("visualisation_annexes/points_graphique.txt", "r") as fichier:
        lignes = fichier.readlines()
        for ligne in lignes:
            points.append((int(ligne.split(',')[0].split('(')[1]), int(ligne.split(',')[1].split(')')[0])))
    for point in points:
        if point[0] == 0:
            bouton_densite_deplacement_0pourcent.set_valeur(str(point[1]))
        elif point[0] == 900:
            bouton_densite_deplacement_900pourcent.set_valeur(str(point[1]))
    return points


def tracer_quadrillage_graphique():
    """Trace le quadrillage du graphique"""
    # -- abscisses --
    for k in range(1, 19):
        pygame.draw.line(screen, (255, 255, 255), (10 + 33.3*k, 10), (10 + 33.3*k, 410))
        abscisse_text = font_graphique.render(f'{k*50}', False, (0, 0, 0))
        screen.blit(abscisse_text, (3 + 33.3*k, 410))

    # -- ordonnees --
    for k in range(0, 11):
        pygame.draw.line(screen, (255, 255, 255), (10, 10 + 40*k), (610, 10 + 40*k))
        ordonnee_text = font_graphique.render(f'{100 - k * 10}', False, (0, 0, 0))
        screen.blit(ordonnee_text, (1, 10 + k*40))


def tri_points():
    """Tri les points du graphique dans le sens croissant par rapport à l'abscisse"""
    # cette fonction est codée de manière aberrante : a ne pas regarder svp pour votre santé mentale
    copie_points_graphique = [point for point in points_graphique]
    points_graphique_tries = []

    def minimum(tab):
        """Cherche le minimum dans un tableau"""
        min = tab[0]
        indice = 0
        for i in range(0,len(tab)):
            if tab[i][0] < min[0]:
                indice = i
                min = tab[i]
        return indice, min

    while len(copie_points_graphique) > 0:
        i, min = minimum(copie_points_graphique)
        points_graphique_tries.append(min)
        copie_points_graphique.pop(i)

    return points_graphique_tries


def tracer_lignes_graphique():
    """Trace les lignes entres les points du graphique"""
    points_graphique = tri_points()
    couleur_ligne = (255,200,255)

    for i in range(0, len(points_graphique)-1):
        point1 = conversion_graph_pixel(points_graphique[i])
        point2 = conversion_graph_pixel(points_graphique[i+1])
        pygame.draw.line(screen, couleur_ligne, point1, point2)


def intersect_line(ligne1, ligne2):
    """Donne l'intersection entre deux lignes"""
    # j'ai copié ce code d'internet
    x1, y1, x2, y2 = ligne1
    x3, y3, x4, y4 = ligne2
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
    if 0 < t < 1 and 0 < u < 1:
        return pygame.Vector2(x1 + t * (x2 - x1),
                              y1 + t * (y2 - y1))


def valeur_tableau(abcisse):
    """Donne la valeur du tableau pour une certaine abscisse"""
    points_graphique = tri_points()

    # Si jamais on calcule la valeur d'un point, on donne directement son ordonnée
    for point in points_graphique:
        if point[0] == abcisse:
            return point[1]

    point_gauche = (0,int(bouton_densite_deplacement_0pourcent.get_valeur()))
    point_droite = (900,int(bouton_densite_deplacement_900pourcent.get_valeur()))

    # On cherche le point le plus proche à gauche et à droite de l'abscisse
    for point in points_graphique:
        if point[0] < abcisse and point[0] > point_gauche[0]:
            point_gauche = point
        if point[0] > abcisse and point[0] < point_droite[0]:
            point_droite = point

    # On convertit les lignes à l'échelle du programme, pas à l'échelle du graphique
    abcisse = conversion_graph_pixel((abcisse, 50))[0]
    point_gauche = conversion_graph_pixel(point_gauche)
    point_droite = conversion_graph_pixel(point_droite)

    # On calcule le point d'intersection des deux droites
    point_intersection = intersect_line( (point_gauche[0], point_gauche[1], point_droite[0], point_droite[1]), (abcisse, 0, abcisse, 450) )

    return conversion_pixel_graph(point_intersection)[1]


def calculer_tableau():
    """Calcul le tableau du graphique"""
    valeurs_graphique = []
    for i in range(0,901):
        valeurs_graphique.append(valeur_tableau(i))
    return valeurs_graphique


points_graphique = importer_graphique()  # On importe les points du graphique
importer_parametres()
def supprimer_point(point_clique):
    """Supprime un point du graphique si on a cliqué proche de lui"""
    for point in points_graphique:
        # on calcule la distance entre le point cliqué, et chaque point du graphique, avec la norme 2
        distance = ((point_clique[0] - point[0])**2 + (point_clique[1] - point[1])**2)**(1/2)
        if distance < 7:
            points_graphique.remove(point)
            return True
    return False


while 1:
    for event in pygame.event.get():
        #print(event)
        if event.type == pygame.KEYDOWN:
            #print(event)
            if event.key == 27:
                sauvegarder_graphique()
                sys.exit()
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            # -- Si on clique sur le graphique --
            if event.pos[0] > 10 and event.pos[0] < 610:
                if event.pos[1] > 10 and event.pos[1] < 410:
                    # Si on clique trop proche d'un point, on le supprime, sinon on en place un
                    if supprimer_point(conversion_pixel_graph(event.pos)) == False:
                        points_graphique.append(conversion_pixel_graph(event.pos))
        for bouton in liste_boutons:
            bouton.handle_event(event)

    # -- Coordonnées --
    #pos = list(pygame.mouse.get_pos())
    #print(conversion_pixel_graph(pos))
    # ----------------

    # Si un des boutons est cliqué, on effectue les actions correspondantes
    if bouton_sauvegarder.istriggered() == True:
        sauvegarder_graphique()
        sauvegarder_parametres()
        print("Sauvegarde!")
    if bouton_supprimer.istriggered() == True:
        points_graphique = [(0,int(bouton_densite_deplacement_0pourcent.get_valeur())),
                            (900,int(bouton_densite_deplacement_900pourcent.get_valeur()))]
        print("Graphique réinitialisé!")

    # -- on charge les elements graphique du programme --
    pygame.draw.rect(screen, (96, 96, 96), pygame.Rect(620, 0, 380, 500))
    pygame.draw.rect(screen, couleur_contour_graphique, pygame.Rect(0, 0, 620, 500))
    pygame.draw.rect(screen, couleur_fond_graphique, pygame.Rect(10, 10, 600, 400))
    for point in points_graphique:
        placer_point(point)
    for bouton in liste_boutons:
        bouton.draw(screen)
    tracer_quadrillage_graphique()
    tracer_lignes_graphique()
    # ---------------------------------------------

    pygame.display.flip()
