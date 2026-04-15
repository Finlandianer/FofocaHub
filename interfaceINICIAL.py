import pygame
import math
import random
import os


# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
tamanho_hover=(230, 53)
tamanho_normal=(210, 47)
WIDTH= 1000
HEIGHT= 600
centroX= WIDTH // 2
centroY= HEIGHT // 2



def init(screen, WIDTH, HEIGHT, audio_available):
    global _screen, _WIDTH, _HEIGHT, _has_audio
    _screen = screen
    _WIDTH = WIDTH
    _HEIGHT = HEIGHT
    _has_audio = audio_available

    _carregar_background()
    _criar_chuva()

    global camadas_nevoa, flicker
    camadas_nevoa = [
        CamadaNevoa(velocidade=8,  alpha=28, y_base=160, altura=80, cor=(30, 35, 50)),
        CamadaNevoa(velocidade=14, alpha=20, y_base=260, altura=60, cor=(25, 30, 45)),
        CamadaNevoa(velocidade=22, alpha=15, y_base=340, altura=50, cor=(20, 25, 40)),
    ]
    flicker = Flicker()

    _criar_scanlines()
    _criar_vinheta()
    _criar_sombras()
    _criar_tinte()
    _criar_som_clique()
    _criar_botoes()
    _criar_fontes()
    _carregar_musica()


def parar_musica():
    pygame.mixer.music.stop()


# ─── Música de fundo ──────────────────────────────────────────────────────────
def _carregar_musica():
    if _has_audio:
        try:
            pygame.mixer.music.load(os.path.join(BASE_DIR, "sons-interface", "TrilhaSonora.mp3"))
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)
        except Exception:
            pass


# ─── Background ───────────────────────────────────────────────────────────────
def _carregar_background():
    global cidadesombria_img
    img_path = os.path.join(BASE_DIR, "imagens-da-interface", "background.png")
    if os.path.exists(img_path):
        cidadesombria_img = pygame.image.load(img_path).convert_alpha()
        cidadesombria_img = pygame.transform.scale(cidadesombria_img, (_WIDTH, _HEIGHT))
    else:
        # Cria um background escuro se a imagem não existir
        cidadesombria_img = pygame.Surface((_WIDTH, _HEIGHT))
        cidadesombria_img.fill((15, 18, 30))


# ─── Chuva ────────────────────────────────────────────────────────────────────
class Gota:
    def __init__(self):
        self.reset(nascendo=True)

    def reset(self, nascendo=False):
        self.x = random.uniform(0, _WIDTH)
        self.y = random.uniform(-_HEIGHT, 0) if nascendo else random.uniform(-60, -5)
        self.vel_y = random.uniform(280, 420)
        self.vel_x = random.uniform(30, 60)
        self.comprimento = random.uniform(8, 18)
        self.alpha = random.randint(40, 100)
        self.espessura = 1 if random.random() < 0.7 else 2

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        if self.y > _HEIGHT + 20:
            self.reset()


def _criar_chuva():
    global gotas, chuva_surf
    gotas = [Gota() for _ in range(220)]
    chuva_surf = pygame.Surface((_WIDTH, _HEIGHT), pygame.SRCALPHA)


# ─── Névoa ────────────────────────────────────────────────────────────────────
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
        s = pygame.Surface((_WIDTH * 2, self.altura), pygame.SRCALPHA)
        for x in range(_WIDTH * 2):
            fator = (math.sin(x * 0.008) * 0.3 + 0.7)
            a = int(self.alpha * fator)
            pygame.draw.line(s, (*self.cor, a), (x, 0), (x, self.altura))
        return s

    def update(self, dt):
        self.x -= self.velocidade * dt
        if self.x <= -_WIDTH:
            self.x += _WIDTH

    def draw(self, surface):
        x = int(self.x)
        surface.blit(self.surf, (x, self.y_base))
        surface.blit(self.surf, (x + _WIDTH, self.y_base))


# ─── Flicker ──────────────────────────────────────────────────────────────────
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
            s = pygame.Surface((_WIDTH, _HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, self.alpha))
            surface.blit(s, (0, 0))


# ─── Scanlines ────────────────────────────────────────────────────────────────
def _criar_scanlines():
    global scanline_surf
    scanline_surf = pygame.Surface((_WIDTH, _HEIGHT), pygame.SRCALPHA)
    for y in range(0, _HEIGHT, 3):
        pygame.draw.line(scanline_surf, (0, 0, 0, 22), (0, y), (_WIDTH, y))


# ─── Vinheta ──────────────────────────────────────────────────────────────────
def _criar_vinheta():
    global vinheta_surf
    w, h = 200, 150
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    for y in range(h):
        dy = (y - cy) / (h * 0.6)
        for x in range(w):
            dist = math.sqrt(((x - cx) / (w * 0.6)) ** 2 + dy ** 2)
            a = int(min(255, max(0, (dist - 0.5) * 300)))
            if a > 0:
                surf.set_at((x, y), (0, 0, 0, a))
    vinheta_surf = pygame.transform.scale(surf, (_WIDTH, _HEIGHT))


# ─── Sombras ──────────────────────────────────────────────────────────────────
def _criar_sombras():
    global sombra_esquerda, sombra_inferior

    sombra_esquerda = pygame.Surface((_WIDTH, _HEIGHT), pygame.SRCALPHA)
    shadow_width = 350
    for x in range(shadow_width):
        alpha = int((1 - x / shadow_width) ** 1.3 * 255)
        pygame.draw.line(sombra_esquerda, (0, 10, 30, alpha), (x, 0), (x, _HEIGHT))

    sombra_inferior = pygame.Surface((_WIDTH, _HEIGHT), pygame.SRCALPHA)
    shadow_height = 400
    for y in range(shadow_height):
        fator = (y / shadow_height) ** 1.5
        alpha = int(fator * 255)
        pygame.draw.line(sombra_inferior, (0, 0, 10, alpha),
                         (0, _HEIGHT - shadow_height + y), (_WIDTH, _HEIGHT - shadow_height + y))


# ─── Tinte ────────────────────────────────────────────────────────────────────
def _criar_tinte():
    global tinte_surf
    tinte_surf = pygame.Surface((_WIDTH, _HEIGHT), pygame.SRCALPHA)
    tinte_surf.fill((5, 8, 25, 50))


# ─── Desenho dos efeitos ──────────────────────────────────────────────────────
def draw_efeitossombrios(surface=None):
    if surface is None:
        surface = _screen
    surface.blit(tinte_surf, (0, 0))
    for camada in camadas_nevoa:
        camada.draw(surface)
    chuva_surf.fill((0, 0, 0, 0))
    for gota in gotas:
        x2 = int(gota.x + gota.vel_x * 0.04)
        y2 = int(gota.y + gota.comprimento)
        pygame.draw.line(chuva_surf, (180, 200, 220, gota.alpha),
                         (int(gota.x), int(gota.y)), (x2, y2), gota.espessura)
    surface.blit(chuva_surf, (0, 0))
    surface.blit(vinheta_surf, (0, 0))
    surface.blit(sombra_esquerda, (0, 0))
    surface.blit(scanline_surf, (0, 0))
    flicker.draw(surface)


def draw_sombra_inferior(surface=None):
    if surface is None:
        surface = _screen
    surface.blit(sombra_inferior, (0, 10))


def update_chuva(dt):
    for gota in gotas:
        gota.update(dt)


def update_nevoa(dt):
    for camada in camadas_nevoa:
        camada.update(dt)


# ─── Som de clique ─────────────────────────────────────────────────
def _criar_som_clique():
    global click_sound
    click_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sons-interface", "buttonSound.wav"))
    pygame.mixer.Sound.set_volume(click_sound, 0.7)
    return click_sound


# ─── Classe Botoes ─────────────────────────────────────────────────
class Botao:
    COR_TEXTO = (255, 255, 255)
    FONTE_CARREGADA = None

    @classmethod
    def _carregar_fonte(cls):
        if cls.FONTE_CARREGADA is None:
            cls.FONTE_CARREGADA = pygame.font.Font(
                os.path.join(BASE_DIR, "fontes", "Silkscreen-Regular.ttf"),
                16
            )
        return cls.FONTE_CARREGADA

    def __init__(
        self,
        texto,
        centro,
        cor_normal,
        cor_hover,
        tamanho_normal,
        tamanho_hover,
        velocidade=0.15
    ):
        self.texto = texto
        self.centro = pygame.Vector2(centro)
        self.base_centro = pygame.Vector2(centro)

        self.cor_normal = cor_normal
        self.cor_hover = cor_hover

        self.tamanho_normal = tamanho_normal
        self.tamanho_hover = tamanho_hover
        self.velocidade = velocidade

        self.fonte = Botao._carregar_fonte()

        self.tamanho_atual = list(tamanho_normal)
        self._hover = False

        # clique visual
        self.pressed = False
        self.press_timer = 0

        # COOLDOWN
        self.cooldown = 800
        self.last_click = -self.cooldown

        # SHAKE
        self.shake_timer = 0

    # ─────────────────────────────
    def atualizar(self, pos_mouse):

        agora = pygame.time.get_ticks()

        area = pygame.Rect(
            self.base_centro.x - self.tamanho_hover[0] // 2,
            self.base_centro.y - self.tamanho_hover[1] // 2,
            self.tamanho_hover[0],
            self.tamanho_hover[1],
        )

        self._hover = area.collidepoint(pos_mouse)

        alvo = self.tamanho_hover if self._hover else self.tamanho_normal

        # animação suave
        self.tamanho_atual[0] += (alvo[0] - self.tamanho_atual[0]) * self.velocidade
        self.tamanho_atual[1] += (alvo[1] - self.tamanho_atual[1]) * self.velocidade

        # tremida
        if self.shake_timer > agora:
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            self.centro = pygame.Vector2(
                self.base_centro.x + offset_x,
                self.base_centro.y + offset_y
            )
        else:
            self.centro = self.base_centro

        # animação clique
        if self.pressed:
            self.press_timer -= 1
            if self.press_timer <= 0:
                self.pressed = False

    # ─────────────────────────────
    def draw(self, surface):

        agora = pygame.time.get_ticks()

        w, h = self.tamanho_atual
        x = self.centro.x - w // 2
        y = self.centro.y - h // 2
        rect = pygame.Rect(x, y, w, h)

        # cor normal / hover
        cor = self.cor_hover if self._hover else self.cor_normal

        # feedback cooldown
        if agora - self.last_click < self.cooldown:
            cor = (90, 90, 90)

        esp_linha = 2 if self._hover else 1

        pygame.draw.rect(surface, cor, rect, width=esp_linha, border_radius=6)

        texto_surf = self.fonte.render(self.texto, False, self.COR_TEXTO)
        surface.blit(texto_surf, texto_surf.get_rect(center=rect.center))

    # ─────────────────────────────
    def foi_clicado(self, evento):

        if (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self._hover
        ):

            agora = pygame.time.get_ticks()

            # ❌ em cooldown
            if agora - self.last_click < self.cooldown:
                self.shake_timer = agora + 300
                return False

            # ✅ clique válido
            self.last_click = agora

            self.pressed = True
            self.press_timer = 6

            if click_sound:
                click_sound.play()

            return True

        return False

def _criar_botoes():
    global start_button, sair_button, Continuar_button, creditos_button

    start_button = Botao(
        texto="Novo Jogo",
        centro=(centroX, 190),
        cor_normal=(120, 130, 150),
        cor_hover=(200, 215, 240),
        tamanho_normal=tamanho_normal,
        tamanho_hover=tamanho_hover,
    )
    Continuar_button = Botao(
        texto="Continuar",
        centro=(centroX, 260),
        cor_normal=(120, 130, 150),
        cor_hover=(200, 215, 240),
        tamanho_normal=tamanho_normal,
        tamanho_hover=tamanho_hover,
    )
    creditos_button = Botao(
        texto="Créditos",
        centro=(centroX, 330),
        cor_normal=(120, 130, 150),
        cor_hover=(200, 215, 240),
        tamanho_normal=tamanho_normal,
        tamanho_hover=tamanho_hover,
    )
    sair_button = Botao(
        texto="Sair",
        centro=(centroX, 400),
        cor_normal=(120, 130, 150),
        cor_hover=(200, 215, 240),
        tamanho_normal=tamanho_normal,
        tamanho_hover=tamanho_hover,
    )
    
# ─── Fontes ───────────────────────────────────────────────────────────────────
def melhor_fonte_titulo(tamanho):
    for nome in ("cinzel", "playfair display", "georgia"):
        if nome in [f.lower() for f in pygame.font.get_fonts()]:
            return pygame.font.SysFont(nome, tamanho)
    return pygame.font.Font(None, tamanho)


def melhor_fonte_texto(tamanho):
    for nome in ("georgia", "times new roman", "dejavu serif"):
        if nome in [f.lower() for f in pygame.font.get_fonts()]:
            return pygame.font.SysFont(nome, tamanho)
    return pygame.font.Font(None, tamanho)


def _criar_fontes():
    global fonte_titulo, fonte_subtitulo, fonte_creditos
    fonte_titulo = melhor_fonte_titulo(54)
    fonte_subtitulo = melhor_fonte_texto(16)
    fonte_creditos = melhor_fonte_texto(16)


def draw_textos(surface=None):
    if surface is None:
        surface = _screen

    start_button.draw(surface)
    Continuar_button.draw(surface)
    sair_button.draw(surface)
    creditos_button.draw(surface)

    titulo = fonte_titulo.render("Blackout", True, (78, 88, 97))
    titulo_rect = titulo.get_rect(centerx=_WIDTH // 2, top=20)
    surface.blit(titulo, titulo_rect)

    sub = fonte_subtitulo.render("Parte 1. ", True, (120, 130, 150))
    surface.blit(sub, sub.get_rect(centerx=_WIDTH // 2, top=titulo_rect.bottom + 2))

    credits = fonte_creditos.render("Projeto de pygame à escola.", True, (120, 130, 150))
    surface.blit(credits, credits.get_rect(centerx=_WIDTH // 2, bottom=_HEIGHT - 10))