from email.mime import image

import pygame
import os
import random
import math

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Didstein - Cidade Sombria")
clock = pygame.time.Clock()

# ─── Carrega o background ─────────────────────────────────────────────────────
img_path = os.path.join(os.path.dirname(__file__), "imagens", "capoturei-1.png.png")
cidadesombria_img = pygame.image.load(img_path).convert()
cidadesombria_img = pygame.transform.scale(cidadesombria_img, (WIDTH, HEIGHT))

# ─── Sistema de chuva ─────────────────────────────────────────────────────────
class Gota:
    def __init__(self):
        self.reset(nascendo=True)

    def reset(self, nascendo=False):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(-HEIGHT, 0) if nascendo else random.uniform(-60, -5)
        self.vel_y = random.uniform(280, 420)
        self.vel_x = random.uniform(30, 60)
        self.comprimento = random.uniform(8, 18)
        self.alpha = random.randint(40, 100)
        self.espessura = 1 if random.random() < 0.7 else 2

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        if self.y > HEIGHT + 20:
            self.reset()

TOTAL_GOTAS = 220
gotas = [Gota() for _ in range(TOTAL_GOTAS)]
chuva_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# ─── Sistema de névoa ─────────────────────────────────────────────────────────
class CamadaNevoa:
    def __init__(self, velocidade, alpha, y_base, altura, cor):
        self.x = 0.0
        self.velocidade = velocidade
        self.alpha = alpha
        self.y_base = y_base
        self.altura = altura
        self.cor = cor
        self.surf = self._criar_surf()

    def _criar_surf(self):
        s = pygame.Surface((WIDTH * 2, self.altura), pygame.SRCALPHA)
        for x in range(WIDTH * 2):
            fator = (math.sin(x * 0.008) * 0.3 + 0.7)
            a = int(self.alpha * fator)
            pygame.draw.line(s, (*self.cor, a), (x, 0), (x, self.altura))
        return s

    def update(self, dt):
        self.x -= self.velocidade * dt
        if self.x <= -WIDTH:
            self.x += WIDTH

    def draw(self, surface):
        x = int(self.x)
        surface.blit(self.surf, (x, self.y_base))
        surface.blit(self.surf, (x + WIDTH, self.y_base))

camadas_nevoa = [
    CamadaNevoa(velocidade=8,  alpha=28, y_base=160, altura=80, cor=(30, 35, 50)),
    CamadaNevoa(velocidade=14, alpha=20, y_base=260, altura=60, cor=(25, 30, 45)),
    CamadaNevoa(velocidade=22, alpha=15, y_base=340, altura=50, cor=(20, 25, 40)),
]

# ─── Efeito de flicker ────────────────────────────────────────────────────────
class Flicker:
    def __init__(self):
        self.alpha = 0
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt
        if random.random() < 0.004:
            self.alpha = random.randint(15, 45)
        else:
            self.alpha = max(0, self.alpha - int(600 * dt))

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, self.alpha))
            surface.blit(s, (0, 0))

flicker = Flicker()

# ─── Scanlines ────────────────────────────────────────────────────────────────
scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 3):
    pygame.draw.line(scanline_surf, (0, 0, 0, 22), (0, y), (WIDTH, y))

# ─── Vinheta ──────────────────────────────────────────────────────────────────
vinheta_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
cx, cy = WIDTH // 2, HEIGHT // 2
for y in range(HEIGHT):
    for x in range(WIDTH):
        dist = math.sqrt(((x - cx) / (WIDTH * 0.6)) ** 2 +
                         ((y - cy) / (HEIGHT * 0.6)) ** 2)
        a = int(min(255, max(0, (dist - 0.5) * 300)))
        if a > 0:
            vinheta_surf.set_at((x, y), (0, 0, 0, a))

# ─── Sombra lateral esquerda ──────────────────────────────────────────────────
sombra_esquerda = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
shadow_width = 350
for x in range(shadow_width):
    alpha = int((1 - x / shadow_width) ** 1.3 * 255)
    pygame.draw.line(sombra_esquerda, (0, 10, 30, alpha), (x, 0), (x, HEIGHT))

# ─── Tinte ────────────────────────────────────────────────────────────────────
tinte_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
tinte_surf.fill((5, 8, 25, 50))

# ─── Sombra inferior ──────────────────────────────────────────────────────────
sombra_inferior = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
shadow_height = 400
for y in range(shadow_height):
    fator = (y / shadow_height) ** 1.5
    alpha = int(fator * 255)
    pygame.draw.line(sombra_inferior, (0, 0, 10, alpha),
                     (0, HEIGHT - shadow_height + y), (WIDTH, HEIGHT - shadow_height + y))

# ─── Função de desenho dos efeitos ────────────────────────────────────────────
def draw_efeitossombrios():
    screen.blit(cidadesombria_img, (0, 0))
    screen.blit(tinte_surf, (0, 0))
    for camada in camadas_nevoa:
        camada.draw(screen)
    chuva_surf.fill((0, 0, 0, 0))
    for gota in gotas:
        x2 = int(gota.x + gota.vel_x * 0.04)
        y2 = int(gota.y + gota.comprimento)
        pygame.draw.line(chuva_surf, (180, 200, 220, gota.alpha),
                         (int(gota.x), int(gota.y)), (x2, y2), gota.espessura)
    screen.blit(chuva_surf, (0, 0))
    screen.blit(vinheta_surf, (0, 0))
    screen.blit(sombra_esquerda, (0, 0))
    screen.blit(scanline_surf, (0, 0))
    flicker.draw(screen)

# ─── Classe Botao com hover ───────────────────────────────────────────────────
class Botao:
    def __init__(self, imagem_normal, imagem_hover, x, y, scale=0.8):
        largura= imagem_normal.get_width()
        altura= imagem_normal.get_height()
        self.imagem_normal = pygame.transform.scale(imagem_normal, (int(largura * scale), int(altura * scale)))
        self.imagem_hover  = pygame.transform.scale(imagem_hover, (int(largura * scale), int(altura * scale)))
        self.rect = self.imagem_normal.get_rect(topleft=(x, y))
        self.hovered = False

    def atualizar(self, pos_mouse):
        self.hovered = self.rect.collidepoint(pos_mouse)

    def draw(self, surface, x, y):
        imagem_atual = self.imagem_hover if self.hovered else self.imagem_normal
        surface.blit(imagem_atual, (x, y))

    def foi_clicado(self, evento): # Só vai servir se o mouse estiver sobre o botão / E mais tarde vou colocar um som de clique
        return (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.hovered
        )

# ─── Carrega sprites dos botões ───────────────────────────────────────────────
start_img_idle = pygame.image.load("imagens/botao-idle.png").convert_alpha()
start_img_hover  = pygame.image.load("imagens/botao-hovered.png").convert_alpha()       

start_button = Botao(start_img_idle, start_img_hover, x=240, y=120, scale=0.7) #Posição da região clicável do botão

# ─── Loop principal ───────────────────────────────────────────────────────────
running = True
while running:
    dt = clock.tick(60) / 1000
    pos_mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if start_button.foi_clicado(event):
            print("Start clicado!") # Aqui você pode iniciar o jogo ou mudar para a próxima tela

    start_button.atualizar(pos_mouse)

    draw_efeitossombrios()
    screen.blit(sombra_inferior, (0, 10))

    start_button.draw(screen, x=240, y=120) #Posição do botão

    for gota in gotas:
        gota.update(dt)
    for camada in camadas_nevoa:
        camada.update(dt)
    flicker.update(dt)

    pygame.display.flip()

pygame.quit()
