import pygame
import os

pygame.init()
screen = pygame.display.set_mode((800, 600))
img_path = os.path.join(os.path.dirname(__file__), "imagens", "capoturei-1.png (1).png")
cidadesombria_img = pygame.image.load(img_path).convert()
clock = pygame.time.Clock()
x = 0
running = True
while running:
    clock.tick(60)
    screen.blit(cidadesombria_img, (x, 30))
    x += 1
       # x = (x - 1) % 800 Move para a esquerda e reinicia quando sair da tela, use caso queira um loop infinito igual terraria
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.display.flip()
           
pygame.quit()

