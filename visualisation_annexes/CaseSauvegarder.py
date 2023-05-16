import pygame
#import visualisation
#x=640 premiere colonne
class CaseSauvegarder(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, screen):
        super().__init__()
        self.color = (0, 255, 0)
        self.y = pos_y
        self.x = pos_x
        self.wide = 320
        self.length = 50
        self.font_text = pygame.font.Font('freesansbold.ttf', 15)
        self.rect = pygame.Rect(self.x, self.y, self.wide, self.length)
        self.draw(screen)
        self.triggered = False


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Si l'utilisateur à cliquer sur le bouton.
            if self.rect.collidepoint(event.pos):
                self.triggered = True


    def istriggered(self):
        if self.triggered is True:
            self.triggered = False
            return True
        return False


    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # -- nom affiché au dessus du carré --
        text = self.font_text.render("SAUVEGARDER", True, (255, 255, 255), self.color)
        textRect = text.get_rect()
        textRect.center = (self.x + self.wide/2, self.y + self.length/2)
        screen.blit(text, textRect)
