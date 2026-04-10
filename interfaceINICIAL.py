import pygame
import math
import random
import struct
import wave
import io
import os


# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def init(screen, WIDTH, HEIGHT, audio_available):
    """Inicializa todos os elementos da interface. Deve ser chamado após pygame.init()."""
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
    _criar_botaoContinuar()


def parar_musica():
    """Para a música quando o jogador sai da tela de interface."""
    pygame.mixer.music.stop()


# ─── Música de fundo ─────────────────────────────────────────────────────────
def _carregar_musica():
    if _has_audio:
        try:
            pygame.mixer.music.load(os.path.join(BASE_DIR, "sons-interface", "música-interface.wav"))
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except Exception:
            pass


# ─── Background ───────────────────────────────────────────────────────────────
def _carregar_background():
    global cidadesombria_img
    img_path = os.path.join(BASE_DIR, "imagens-da-interface", "background.png")
    cidadesombria_img = pygame.image.load(img_path).convert_alpha()
    cidadesombria_img = pygame.transform.scale(cidadesombria_img, (_WIDTH, _HEIGHT))


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


# ─── Sombra lateral esquerda ──────────────────────────────────────────────────
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
    surface.blit(cidadesombria_img, (0, 0))
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


# ─── Som de clique procedural ─────────────────────────────────────────────────
def _gerar_som_clique():
    sr = 22050
    dur = 0.08
    n = int(sr * dur)
    buf = io.BytesIO()
    wf = wave.open(buf, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    for i in range(n):
        t = i / sr
        env = max(0, 1 - i / n)
        sample = int(math.sin(2 * math.pi * 800 * t) * env * 6000)
        wf.writeframes(struct.pack("<h", sample))
    wf.close()
    buf.seek(0)
    return pygame.mixer.Sound(buf)


def _criar_som_clique():
    global click_sound
    if _has_audio:
        try:
            click_sound = _gerar_som_clique()
        except Exception:
            click_sound = None
    else:
        click_sound = None


# ─── Classe Botao ─────────────────────────────────────────────────────────────
class Botao:
    def __init__(self, imagem_normal, imagem_hover, x, y, scale=0.8):
        largura = imagem_normal.get_width()
        altura = imagem_normal.get_height()
        self.imagem_normal = pygame.transform.scale(imagem_normal, (int(largura * scale), int(altura * scale)))
        self.imagem_hover  = pygame.transform.scale(imagem_hover,   (int(largura * scale), int(altura * scale)))
        self.x, self.y = x, y
        self.rect = self.imagem_normal.get_rect(topleft=(x, y))
        self.hovered = False
        self.pressed = False
        self.press_timer = 0

    def atualizar(self, pos_mouse):
        self.hovered = self.rect.collidepoint(pos_mouse)
        if self.pressed:
            self.press_timer -= 1
            if self.press_timer <= 0:
                self.pressed = False

    def draw(self, surface):
        if self.pressed:
            surface.blit(self.imagem_normal, (self.x, self.y))
        elif self.hovered:
            surface.blit(self.imagem_hover, (self.x, self.y))
        else:
            surface.blit(self.imagem_normal, (self.x, self.y))

    def foi_clicado(self, evento):
        if (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.hovered
        ):
            self.pressed = True
            self.press_timer = 6
            if click_sound:
                click_sound.play()
            return True
        return False


def _criar_botoes():
    global start_button
    start_img_idle  = pygame.image.load(os.path.join(BASE_DIR, "imagens-da-interface", "botao-idle.png")).convert_alpha()
    start_img_hover = pygame.image.load(os.path.join(BASE_DIR, "imagens-da-interface", "botao-hovered.png")).convert_alpha()
    start_button = Botao(start_img_idle, start_img_hover, x=260, y=180)

# ─── Botão Continuar (procedural, sem sprites) ────────────────────────────────
class BotaoContinuar:
    def __init__(self, x, y):
        self.base_x = x
        self.base_y = y
        texto_surf = fonte_titulo.render("Continuar", True, (180, 190, 210))
        pad_x, pad_y = 20, 8
        self._botoes_w = texto_surf.get_width() + pad_x * 2
        self._botoes_h = texto_surf.get_height() + pad_y * 2
        self.texto_base = texto_surf
        self.hover_scale = 1.22
        self.hovered = False
        self.pressed = False
        self.press_timer = 0
        self.texto_hover = pygame.transform.scale(
            texto_surf,
            (int(texto_surf.get_width() * self.hover_scale), int(texto_surf.get_height() * self.hover_scale)),
        )
        self.x = x
        self.y = y
        self._build_rects()

    def _build_rects(self):
        self.rect = pygame.Rect(self.x, self.y, self._botoes_w, self._botoes_h)
        self.hover_rect = pygame.Rect(
            self.x - (self._botoes_w * (self.hover_scale - 1)) // 2,
            self.y - (self._botoes_h * (self.hover_scale - 1)) // 2,
            int(self._botoes_w * self.hover_scale),
            int(self._botoes_h * self.hover_scale),
        )

    def atualizar(self, pos_mouse):
        active = self.hover_rect if self.hovered else self.rect
        self.hovered = active.collidepoint(pos_mouse)
        if self.hovered:
            self.rect = self.hover_rect
            self.x = self.rect.x
            self.y = self.rect.y
        else:
            self.x = self.base_x
            self.y = self.base_y
            self._build_rects()
        if self.pressed:
            self.press_timer -= 1
            if self.press_timer <= 0:
                self.pressed = False

    def draw(self, surface):
        w, h = self.rect.w, self.rect.h
        x, y = self.rect.x, self.rect.y
        cor_borda = (200, 215, 240) if self.hovered else (120, 130, 150)
        esp_linha = 2 if self.hovered else 1
        pygame.draw.rect(surface, cor_borda, (x, y, w, h), esp_linha, border_radius=6)
        txt = self.texto_hover if self.hovered else self.texto_base
        surface.blit(txt, txt.get_rect(center=(x + w // 2, y + h // 2)))

    def foi_clicado(self, evento):
        if (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.rect.collidepoint(evento.pos)
        ):
            self.pressed = True
            self.press_timer = 6
            if click_sound:
                click_sound.play()
            return True
        return False


def _criar_botaoContinuar():
    global Continuar_button
    Continuar_button = BotaoContinuar(x=280, y=245)    



    


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

    titulo = fonte_titulo.render("Apagão", True, (78, 88, 97))
    titulo_rect = titulo.get_rect(centerx=_WIDTH // 2, top=20)
    surface.blit(titulo, titulo_rect)

    sub = fonte_subtitulo.render(" Aqui não há luz. ", True, (120, 130, 150))
    surface.blit(sub, sub.get_rect(centerx=_WIDTH // 2, top=titulo_rect.bottom + 2))

    credits = fonte_creditos.render("Projeto de pygame à escola.", True, (20, 85, 100))
    surface.blit(credits, credits.get_rect(centerx=_WIDTH // 2, bottom=_HEIGHT - 10))
