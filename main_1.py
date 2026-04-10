import pygame as pygame
import interfaceINICIAL

pygame.init()
try:
    pygame.mixer.init()
    has_audio = True
except pygame.error:
    has_audio = False

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Apagão")
clock = pygame.time.Clock()

interfaceINICIAL.init(screen, WIDTH, HEIGHT, has_audio)

running = True
while running:
    deltatime = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if interfaceINICIAL.start_button.foi_clicado(event):
            interfaceINICIAL.parar_musica()
            # TODO: transição para próxima tela do jogo

    interfaceINICIAL.start_button.atualizar(pygame.mouse.get_pos())
    interfaceINICIAL.Continuar_button.atualizar(pygame.mouse.get_pos())
    interfaceINICIAL.draw_efeitossombrios()
    interfaceINICIAL.draw_sombra_inferior()
    interfaceINICIAL.draw_textos()
    interfaceINICIAL.update_chuva(deltatime)
    interfaceINICIAL.update_nevoa(deltatime)
    interfaceINICIAL.flicker.update(deltatime)
    pygame.display.flip()

pygame.quit()
