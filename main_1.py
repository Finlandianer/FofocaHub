import pygame
import interfaceINICIAL
import cidade

pygame.init()

try:
    pygame.mixer.init()
    has_audio = True
except pygame.error:
    has_audio = False

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackout")

clock = pygame.time.Clock()

interfaceINICIAL.init(screen, WIDTH, HEIGHT, has_audio)

camera_x = 0
stop_point = 600

running = True

# ================= LOOP PRINCIPAL =================
while running:

    deltatime = clock.tick(60) / 1000
    mouse_pos = pygame.mouse.get_pos()

    # -------- EVENTOS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if interfaceINICIAL.start_button.foi_clicado(event):
            pass

        if interfaceINICIAL.Continuar_button.foi_clicado(event):
            pass

        if interfaceINICIAL.creditos_button.foi_clicado(event):
            pass

        if interfaceINICIAL.sair_button.foi_clicado(event):
            running = False


    # -------- MOVIMENTO DA CÂMERA
    if camera_x < stop_point:
        camera_x += 60 * deltatime


    # -------- ATUALIZAÇÕES
    interfaceINICIAL.start_button.atualizar(mouse_pos)
    interfaceINICIAL.Continuar_button.atualizar(mouse_pos)
    interfaceINICIAL.creditos_button.atualizar(mouse_pos)
    interfaceINICIAL.sair_button.atualizar(mouse_pos)

    interfaceINICIAL.update_chuva(deltatime)
    interfaceINICIAL.update_nevoa(deltatime)
    interfaceINICIAL.flicker.update(deltatime)


    # -------- DESENHO (ORDEM IMPORTA MUITO)
    screen.fill((10,10,60))

    cidade.draw_cidade(screen, camera_x)

    interfaceINICIAL.draw_efeitossombrios(screen)
    interfaceINICIAL.draw_sombra_inferior(screen)
    interfaceINICIAL.draw_textos(screen)

    pygame.display.flip()

pygame.quit()