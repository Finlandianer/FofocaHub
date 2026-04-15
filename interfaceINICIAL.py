import pygame
import math
import random
import os


# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
tamanho_hover = (230, 53)
tamanho_normal = (210, 47)
WIDTH = 1000
HEIGHT = 600
centroX = WIDTH // 2
centroY = HEIGHT // 2


def init(screen, WIDTH, HEIGHT, audio_available):
    global _screen, _WIDTH, _HEIGHT, _has_audio
    _screen = screen
    _WIDTH = WIDTH
    _HEIGHT = HEIGHT
    _has_audio = audio_available

    _carregar_background()
    _criar_chuva()
    _criar_splash()
    _criar_brasas()

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

    # cinematic state
    global cinematic_phase, cinematic_timer, curtain_open, curtain_y
    cinematic_phase = 0  # 0=dark, 1=city_reveal, 2=dark_again, 3=hands_open, 4=menu
    cinematic_timer = 0.0
    curtain_open = 0.0
    curtain_y = HEIGHT / 2

    # button entrance animation
    global button_slide_in
    button_slide_in = 0.0


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


# ─── Splash da chuva (quando atinge o chão) ──────────────────────────────────
class Splash:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 1.0
        self.decay = random.uniform(3, 6)
        self.particles = []
        for _ in range(random.randint(2, 4)):
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(20, 60)
            self.particles.append({
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "ox": 0,
                "oy": 0,
            })

    def update(self, dt):
        self.life -= self.decay * dt
        for p in self.particles:
            p["ox"] += p["vx"] * dt
            p["oy"] += p["vy"] * dt
            p["vy"] += 200 * dt  # gravidade nas gotinhas

    def draw(self, surface):
        if self.life <= 0:
            return
        a = int(self.life * 120)
        for p in self.particles:
            px = int(self.x + p["ox"])
            py = int(self.y + p["oy"])
            pygame.draw.circle(surface, (180, 200, 220, a), (px, py), 1)


splashes = []


def _criar_splash():
    global splashes
    splashes = []


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


# ─── Brasas (partículas atmosféricas) ─────────────────────────────────────────
class Brasa:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, _WIDTH)
        self.y = random.uniform(0, _HEIGHT)
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-20, -5)
        self.life = random.uniform(2, 6)
        self.max_life = self.life
        self.size = random.uniform(1, 3)
        self.cor = random.choice([
            (200, 100, 30), (180, 80, 20), (220, 120, 40),
            (255, 150, 50), (190, 90, 30),
        ])

    def update(self, dt):
        self.x += self.vx * dt + math.sin(self.y * 0.02) * 5 * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0 or self.y < -10:
            self.reset()
            self.y = _HEIGHT + 10  # renasce de baixo

    def draw(self, surface):
        a = int(max(0, min(255, (self.life / self.max_life) * 150)))
        r, g, b = self.cor
        pygame.draw.circle(surface, (r, g, b, a), (int(self.x), int(self.y)), int(self.size))


def _criar_brasas():
    global brasas
    brasas = [Brasa() for _ in range(35)]


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

    # chuva + splash
    chuva_surf.fill((0, 0, 0, 0))
    for gota in gotas:
        x2 = int(gota.x + gota.vel_x * 0.04)
        y2 = int(gota.y + gota.comprimento)
        pygame.draw.line(chuva_surf, (180, 200, 220, gota.alpha),
                         (int(gota.x), int(gota.y)), (x2, y2), gota.espessura)

        # chance de splash quando a gota chega perto do chão
        if gota.y > _HEIGHT - 20 and random.random() < 0.15:
            splashes.append(Splash(gota.x, _HEIGHT - 2))

    surface.blit(chuva_surf, (0, 0))

    # splashes
    for sp in splashes:
        sp.draw(surface)

    # brasas
    for brasa in brasas:
        brasa.draw(surface)

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

    # atualiza e limpa splashes mortos
    for sp in splashes:
        sp.update(dt)
    splashes[:] = [sp for sp in splashes if sp.life > 0]


def update_nevoa(dt):
    for camada in camadas_nevoa:
        camada.update(dt)

    for brasa in brasas:
        brasa.update(dt)


def update_brasas(dt):
    for brasa in brasas:
        brasa.update(dt)


# ─── Som de clique ─────────────────────────────────────────────────
def _criar_som_clique():
    global click_sound
    try:
        click_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sons-interface", "buttonSound.wav"))
        pygame.mixer.Sound.set_volume(click_sound, 0.7)
    except Exception:
        click_sound = None


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
        self.pressed = False
        self.press_timer = 0
        self.cooldown = 800
        self.last_click = -self.cooldown
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
        self.tamanho_atual[0] += (alvo[0] - self.tamanho_atual[0]) * self.velocidade
        self.tamanho_atual[1] += (alvo[1] - self.tamanho_atual[1]) * self.velocidade

        if self.shake_timer > agora:
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            self.centro = pygame.Vector2(
                self.base_centro.x + offset_x,
                self.base_centro.y + offset_y
            )
        else:
            self.centro = self.base_centro

        if self.pressed:
            self.press_timer -= 1
            if self.press_timer <= 0:
                self.pressed = False

    # ─────────────────────────────
    def draw(self, surface, slide_offset=0):
        agora = pygame.time.get_ticks()

        w, h = self.tamanho_atual
        x = self.centro.x - w // 2
        y = self.centro.y - h // 2 + slide_offset
        rect = pygame.Rect(x, y, w, h)

        cor = self.cor_hover if self._hover else self.cor_normal
        if agora - self.last_click < self.cooldown:
            cor = (90, 90, 90)

        esp_linha = 2 if self._hover else 1

        # glow sutil no hover
        if self._hover:
            glow_surf = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
            glow_surf.fill((100, 140, 200, 15))
            surface.blit(glow_surf, (x - 5, y - 5))

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
            if agora - self.last_click < self.cooldown:
                self.shake_timer = agora + 300
                return False
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

    start_button.draw(surface, button_slide_in)
    Continuar_button.draw(surface, button_slide_in)
    sair_button.draw(surface, button_slide_in)
    creditos_button.draw(surface, button_slide_in)

    titulo = fonte_titulo.render("Blackout", True, (78, 88, 97))
    titulo_rect = titulo.get_rect(centerx=_WIDTH // 2, top=20 + button_slide_in)
    surface.blit(titulo, titulo_rect)

    sub = fonte_subtitulo.render("Parte 1. ", True, (120, 130, 150))
    surface.blit(sub, sub.get_rect(centerx=_WIDTH // 2, top=titulo_rect.bottom + 2))


# ─── Cinemática de abertura ───────────────────────────────────────────────────
def update_cinematic(dt):
    global cinematic_phase, cinematic_timer, curtain_open, button_slide_in

    cinematic_timer += dt

    if cinematic_phase == 0:
        # Escuridão total por 2s
        if cinematic_timer > 2.0:
            cinematic_phase = 1
            cinematic_timer = 0.0

    elif cinematic_phase == 1:
        # Cidade aparece (fade in de 2.5s)
        if cinematic_timer > 2.5:
            cinematic_phase = 2
            cinematic_timer = 0.0

    elif cinematic_phase == 2:
        # Volta para escuridão por 1.5s
        if cinematic_timer > 1.5:
            cinematic_phase = 3
            cinematic_timer = 0.0

    elif cinematic_phase == 3:
        # Mãos abrindo (cortina se separa por 1.2s)
        curtain_open = min(1.0, cinematic_timer / 1.2)
        if curtain_open >= 1.0:
            cinematic_phase = 4
            cinematic_timer = 0.0

    elif cinematic_phase == 4:
        # Botões entram com slide
        button_slide_in = max(0, button_slide_in - 300 * dt)


def get_cinematic_darkness():
    """Retorna 0.0 (totalmente visível) a 1.0 (tela preta)."""
    if cinematic_phase == 0:
        return 1.0
    elif cinematic_phase == 1:
        return max(0, 1.0 - cinematic_timer / 2.5)
    elif cinematic_phase == 2:
        return min(1.0, cinematic_timer / 1.5)
    elif cinematic_phase == 3:
        return 1.0  # ainda escuro, cortina que revela
    else:
        return 0.0


def draw_curtain(surface):
    """Desenha as metades da cortina de escuridão + silhuetas das mãos."""
    if cinematic_phase >= 4:
        return

    darkness = get_cinematic_darkness()
    if darkness <= 0:
        return

    if cinematic_phase == 3:
        # Cortina abrindo com "mãos" no meio
        half_w = int(_WIDTH / 2 * (1.0 - curtain_open))

        # Escuridão nas laterais
        surface.fill((0, 0, 0), (0, 0, half_w, _HEIGHT))
        surface.fill((0, 0, 0), (_WIDTH - half_w, 0, half_w, _HEIGHT))

        # Desenha silhuetas de mãos na borda da cortina
        if curtain_open > 0.05:
            for lado in [-1, 1]:
                base_x = half_w if lado == -1 else _WIDTH - half_w
                _desenho_mao(surface, base_x, _HEIGHT // 2, lado)

    else:
        # Tela preta total
        overlay = pygame.Surface((_WIDTH, _HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(int(darkness * 255))
        surface.blit(overlay, (0, 0))


def _desenho_mao(surface, x, y, lado):
    """Desenha uma silhueta estilizada de mão agarrando a cortina."""
    cor = (15, 10, 8)

    # palma
    if lado == -1:
        palma_rect = pygame.Rect(x - 35, y - 30, 35, 60)
    else:
        palma_rect = pygame.Rect(x, y - 30, 35, 60)
    pygame.draw.ellipse(surface, cor, palma_rect)

    # dedos
    for i in range(5):
        ang = -0.6 + i * 0.3
        dx = lado * (15 + abs(math.sin(ang)) * 10)
        dy = -30 + i * 8 + math.sin(ang * 2) * 5
        px = int(x + dx)
        py = int(y + dy)
        pygame.draw.rect(surface, cor, (px - 4, py - 3, 8, 14), border_radius=4)
