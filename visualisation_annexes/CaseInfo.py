import pygame
#x=640 premiere colonne
class CaseInfo(pygame.sprite.Sprite):
    def __init__(self, pos_y, valeur_init, nom, screen, limit_carac = 6):
        super().__init__()
        self.color = (0, 0, 0)
        self.couleur_actif = (140,140,240)
        self.couleur_inactif = (0, 0, 0)
        self.limite_carac = limit_carac
        self.y = pos_y
        self.x = 660  # premiere colonne (a modifier plus tard si 2 colonnes)
        self.valeur = str(valeur_init)
        self.wide = 150
        self.length = 20
        self.nom = str(nom)
        self.font_text = pygame.font.Font('freesansbold.ttf', 15)
        self.active = False
        self.rect = pygame.Rect(self.x, self.y, self.wide, self.length)
        self.draw(screen)

    def set_valeur(self, valeur):
        self.valeur = valeur
        self.update()


    def get_valeur(self):
        return float(self.valeur)


    def get_nom(self):
        return self.nom


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.couleur_actif if self.active else self.couleur_inactif
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.valeur = self.valeur[:-1]
                else:
                    if len(self.valeur) < self.limite_carac:
                        self.valeur += event.unicode
                # Re-render the text.
                self.update()


    def update(self):
        self.txt_surface = self.font_text.render(self.valeur, True, (0, 0, 0))


    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        screen.fill((255, 255, 255), self.rect)
        screen.blit(self.font_text.render(self.valeur, True, self.couleur_inactif), (self.rect.x + 2, self.rect.y + 2))
        # -- nom affiché au dessus du carré --
        nom = self.font_text.render(self.nom, True, (255, 255, 255), (96, 96, 96))
        textRect = nom.get_rect()
        textRect.center = (self.x + self.wide/2, self.y - 10)
        screen.blit(nom, textRect)
