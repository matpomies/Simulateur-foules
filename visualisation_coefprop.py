# Ce fichier sert à visualiser les différents coefficients de proportionnalité pour la densité des foules

import matplotlib.pyplot as plt


############################################################

## Modification du comportement du programme ##

# coef_debut : Coefficient le plus petit que vous voulez simuler
coef_debut = 0.0005

# coef_fin : Coefficient le plus grand que vous voulez simuler
coef_fin = 0.0014

# nombre_courbes : Le nombre de coefficients que vous voulez simuler entre le plus petit coefficient et le plus grand
nombre_courbes = 8

############################################################


nombre_courbes -=1
tab_densite = [i*10 for i in range(80)]
pas = (coef_fin - coef_debut)/nombre_courbes
tab_coef = [pas*n + coef_debut for n in range(0, nombre_courbes+1)]


for coef in tab_coef:
    tab_coef_calcul = []
    coef = round(coef,4)
    # On calcul l'impact sur les densités pour chaque coefficient et on l'affiche comme une droite
    for densite in tab_densite:
        calcul = (810 - densite) * coef
        if calcul > 1:
            tab_coef_calcul.append(1)
        elif calcul < 0:
            tab_coef_calcul.append(0)
        else:
            tab_coef_calcul.append(calcul)
    plt.plot(tab_densite, tab_coef_calcul, label=f"{coef}" )


if __name__ == "__main__":
    plt.legend()
    plt.xlabel("Somme de la densité voisine")
    plt.ylabel("Densité autorisé à se déplacer")
    plt.title("Densité autorisé à se déplacer en fonction de la densité voisine")
    plt.show()
