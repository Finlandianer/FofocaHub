<<<<<<< Updated upstream

=======
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
cidadesombria_img = pygame.image.load("darktheme.png").convert()
x = 0
running = True
while running:
    screen.blit(cidadesombria_img, (x, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

           
pygame.quit()
>>>>>>> Stashed changes
