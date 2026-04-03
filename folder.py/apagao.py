import pygame
import sys
import math
import random
import time

# ─── Inicialização ───────────────────────────────────────────────────────────
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass  # Sem áudio disponível — continua sem som

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Apagão")
clock = pygame.time.Clock()

# ─── Paleta de cores ─────────────────────────────────────────────────────────
BLACK      = (10,  10,  12)
DARK_GRAY  = (20,  20,  25)
MID_GRAY   = (45,  45,  55)
LIGHT_GRAY = (160, 150, 140)
CREAM      = (232, 224, 208)
DIM_CREAM  = (100, 95,  88)
RED_DARK   = (90,  20,  20)
RED_MID    = (160, 40,  40)
RED_GLOW   = (200, 60,  60)
AMBER_DIM  = (80,  60,  20)

# ─── Fontes ───────────────────────────────────────────────────────────────────
# Usa fontes do sistema; troque pelos caminhos das suas fontes pixel art se tiver
try:
    font_title  = pygame.font.SysFont("couriernew", 72, bold=True)
    font_body   = pygame.font.SysFont("couriernew", 18)
    font_small  = pygame.font.SysFont("couriernew", 13)
    font_name   = pygame.font.SysFont("couriernew", 28)
    font_prompt = pygame.font.SysFont("couriernew", 14)
except:
    font_title  = pygame.font.Font(None, 72)
    font_body   = pygame.font.Font(None, 24)
    font_small  = pygame.font.Font(None, 18)
    font_name   = pygame.font.Font(None, 32)
    font_prompt = pygame.font.Font(None, 18)

# ─── Estado da cena ───────────────────────────────────────────────────────────
class NewGameScreen:
    def __init__(self):
        self.reset()

    def reset(self):
        self.phase = "intro"          # intro → name_input → confirm → done
        self.timer = 0.0              # tempo em segundos desde início da fase
        self.player_name = ""
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self.flicker_timer = 0.0
        self.flicker_alpha = 255
        self.noise_particles = self._gen_noise()
        self.narrative_lines = [
            "Era uma noite comum.",
            "Você estava em casa quando percebeu...",
            "Seu irmão não voltou da rua.",
        ]
        self.line_idx = 0             # qual linha narrativa está aparecendo
        self.char_idx = 0             # quantos chars da linha atual já aparecem
        self.text_timer = 0.0
        self.char_delay = 0.045       # segundos por caractere (efeito typewriter)
        self.line_pause = 1.2         # pausa entre linhas
        self.pause_timer = 0.0
        self.pausing = False
        self.narrative_done = False
        self.name_prompt_alpha = 0
        self.name_prompt_fade = 0.0
        self.confirm_alpha = 0
        self.scanline_offset = 0
        self.result = None            # nome escolhido quando fase=="done"

    # ── Geração de ruído de fundo ────────────────────────────────────────────
    def _gen_noise(self):
        return [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
                 random.randint(1, 2), random.randint(5, 30))
                for _ in range(120)]

    # ── Update principal ─────────────────────────────────────────────────────
    def update(self, dt):
        self.timer += dt
        self.flicker_timer += dt
        self.scanline_offset = (self.scanline_offset + 60 * dt) % 4

        # Efeito de flicker na tela
        if random.random() < 0.003:
            self.flicker_alpha = random.randint(210, 245)
        else:
            self.flicker_alpha = min(255, self.flicker_alpha + int(400 * dt))

        # Cursor piscando
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

        # Atualiza ruído
        if random.random() < 0.05:
            idx = random.randint(0, len(self.noise_particles) - 1)
            self.noise_particles[idx] = (
                random.randint(0, WIDTH), random.randint(0, HEIGHT),
                random.randint(1, 2), random.randint(5, 30)
            )

        if self.phase == "intro":
            self._update_intro(dt)
        elif self.phase == "name_input":
            self._update_name_input(dt)
        elif self.phase == "confirm":
            self._update_confirm(dt)

    def _update_intro(self, dt):
        if self.narrative_done:
            # Fade in do prompt de nome
            self.name_prompt_fade += dt
            self.name_prompt_alpha = min(255, int(self.name_prompt_fade * 180))
            if self.name_prompt_fade > 1.8:
                self.phase = "name_input"
            return

        if self.pausing:
            self.pause_timer += dt
            if self.pause_timer >= self.line_pause:
                self.pausing = False
                self.pause_timer = 0
                self.line_idx += 1
                self.char_idx = 0
                if self.line_idx >= len(self.narrative_lines):
                    self.narrative_done = True
            return

        self.text_timer += dt
        if self.text_timer >= self.char_delay:
            self.text_timer = 0
            line = self.narrative_lines[self.line_idx]
            if self.char_idx < len(line):
                self.char_idx += 1
            else:
                self.pausing = True

    def _update_name_input(self, dt):
        # Fade in da caixa de nome
        self.name_prompt_fade += dt * 1.5
        self.name_prompt_alpha = min(255, int(self.name_prompt_fade * 255))

    def _update_confirm(self, dt):
        self.confirm_alpha = min(255, self.confirm_alpha + int(300 * dt))

    # ── Eventos ──────────────────────────────────────────────────────────────
    def handle_event(self, event):
        if self.phase == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(self.player_name.strip()) > 0:
                        self.phase = "confirm"
                        self.confirm_alpha = 0
                elif event.key == pygame.K_ESCAPE:
                    return "back"
                else:
                    if len(self.player_name) < 16 and event.unicode.isprintable():
                        self.player_name += event.unicode

        elif self.phase == "confirm":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_y:
                    self.result = self.player_name.strip()
                    self.phase = "done"
                    return "done"
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                    self.phase = "name_input"
                    self.player_name = ""
                    self.confirm_alpha = 0

        return None

    # ── Draw principal ───────────────────────────────────────────────────────
    def draw(self, surface):
        surface.fill(BLACK)
        self._draw_city(surface)
        self._draw_noise(surface)
        self._draw_scanlines(surface)

        if self.phase in ("intro", "name_input") or self.phase == "confirm":
            self._draw_title(surface)

        if self.phase == "intro":
            self._draw_narrative(surface)
            if self.narrative_done:
                self._draw_fade_prompt(surface)

        elif self.phase in ("name_input", "confirm"):
            self._draw_narrative_static(surface)
            self._draw_name_input(surface)

        if self.phase == "confirm":
            self._draw_confirm(surface)

        # Overlay de flicker
        if self.flicker_alpha < 255:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255 - self.flicker_alpha))
            surface.blit(overlay, (0, 0))

    # ── Silhueta da cidade ───────────────────────────────────────────────────
    def _draw_city(self, surface):
        buildings = [
            (0,   220, 50,  380), (60,  240, 40,  360), (110, 180, 30,  420),
            (150, 200, 60,  400), (220, 150, 35,  450), (265, 230, 45,  370),
            (320, 170, 25,  430), (355, 200, 70,  400), (435, 160, 50,  440),
            (495, 190, 30,  410), (535, 140, 55,  460), (600, 210, 40,  390),
            (650, 180, 35,  420), (695, 220, 60,  380), (765, 200, 40,  400),
        ]
        for x, y, w, h in buildings:
            pygame.draw.rect(surface, DARK_GRAY, (x, y, w, HEIGHT - y))
            # Janelas apagadas ocasionais
            for wy in range(y + 15, HEIGHT - 30, 22):
                for wx in range(x + 6, x + w - 6, 14):
                    if random.random() < 0.04:
                        pygame.draw.rect(surface, AMBER_DIM, (wx, wy, 5, 8))

        # Chão
        pygame.draw.rect(surface, (8, 8, 10), (0, HEIGHT - 80, WIDTH, 80))

    # ── Partículas de ruído ───────────────────────────────────────────────────
    def _draw_noise(self, surface):
        for x, y, size, alpha in self.noise_particles:
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((200, 195, 190, alpha))
            surface.blit(s, (x, y))

    # ── Scanlines ────────────────────────────────────────────────────────────
    def _draw_scanlines(self, surface):
        for y in range(0, HEIGHT, 4):
            line = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
            line.fill((0, 0, 0, 40))
            surface.blit(line, (0, y))

    # ── Título APAGÃO ─────────────────────────────────────────────────────────
    def _draw_title(self, surface):
        # Sombra vermelha (deslocada)
        shadow = font_title.render("APAGÃO", True, RED_DARK)
        sr = shadow.get_rect(center=(WIDTH // 2 + 3, 100 + 3))
        surface.blit(shadow, sr)
        # Texto principal
        title = font_title.render("APAGÃO", True, CREAM)
        tr = title.get_rect(center=(WIDTH // 2, 100))
        surface.blit(title, tr)
        # Linha decorativa
        line_w = 80
        pulse = int(math.sin(self.timer * 1.5) * 10)
        pygame.draw.line(surface, RED_DARK,
                         (WIDTH // 2 - line_w // 2 - pulse, 148),
                         (WIDTH // 2 + line_w // 2 + pulse, 148), 1)

    # ── Texto narrativo (typewriter) ──────────────────────────────────────────
    def _draw_narrative(self, surface):
        base_y = 200
        for i, line in enumerate(self.narrative_lines):
            if i < self.line_idx:
                # Linha completa, mais apagada
                rendered = font_body.render(line, True, DIM_CREAM)
                r = rendered.get_rect(center=(WIDTH // 2, base_y + i * 38))
                surface.blit(rendered, r)
            elif i == self.line_idx and not self.pausing:
                # Linha atual com typewriter
                partial = line[:self.char_idx]
                rendered = font_body.render(partial, True, LIGHT_GRAY)
                r = rendered.get_rect(center=(WIDTH // 2, base_y + i * 38))
                surface.blit(rendered, r)
                # Cursor piscante
                if self.cursor_visible:
                    cx = r.right + 3
                    pygame.draw.rect(surface, LIGHT_GRAY, (cx, r.top, 2, r.height))
            elif i == self.line_idx and self.pausing:
                rendered = font_body.render(line, True, LIGHT_GRAY)
                r = rendered.get_rect(center=(WIDTH // 2, base_y + i * 38))
                surface.blit(rendered, r)

    def _draw_narrative_static(self, surface):
        base_y = 200
        for i, line in enumerate(self.narrative_lines):
            col = DIM_CREAM if i < len(self.narrative_lines) - 1 else LIGHT_GRAY
            rendered = font_body.render(line, True, col)
            r = rendered.get_rect(center=(WIDTH // 2, base_y + i * 38))
            surface.blit(rendered, r)

    def _draw_fade_prompt(self, surface):
        if self.name_prompt_alpha <= 0:
            return
        txt = font_small.render("[ pressione qualquer tecla ]", True,
                                 (self.name_prompt_alpha // 2,
                                  self.name_prompt_alpha // 2,
                                  self.name_prompt_alpha // 2))
        r = txt.get_rect(center=(WIDTH // 2, 360))
        surface.blit(txt, r)

    # ── Input de nome ─────────────────────────────────────────────────────────
    def _draw_name_input(self, surface):
        alpha = min(255, self.name_prompt_alpha)

        # Caixa de fundo
        box_w, box_h = 420, 110
        box_x = WIDTH // 2 - box_w // 2
        box_y = 330

        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((15, 15, 18, min(220, alpha)))
        surface.blit(box_surf, (box_x, box_y))

        # Borda vermelha
        brd_color = (RED_DARK[0], RED_DARK[1], RED_DARK[2])
        pygame.draw.rect(surface, brd_color, (box_x, box_y, box_w, box_h), 1)

        # Label
        label = font_small.render("COMO VOCÊ SE CHAMA?", True,
                                   (min(255, MID_GRAY[0] + alpha // 2),
                                    MID_GRAY[1], MID_GRAY[2]))
        lr = label.get_rect(center=(WIDTH // 2, box_y + 22))
        surface.blit(label, lr)

        # Linha separadora
        pygame.draw.line(surface, RED_DARK,
                         (box_x + 20, box_y + 38), (box_x + box_w - 20, box_y + 38), 1)

        # Nome digitado
        display = self.player_name
        if self.cursor_visible and self.phase == "name_input":
            display += "_"
        name_surf = font_name.render(display, True, CREAM)
        nr = name_surf.get_rect(center=(WIDTH // 2, box_y + 72))
        surface.blit(name_surf, nr)

        # Hint
        hint = font_prompt.render("ENTER para confirmar  •  ESC para voltar", True,
                                   (40, 38, 36))
        hr = hint.get_rect(center=(WIDTH // 2, box_y + box_h + 18))
        surface.blit(hint, hr)

    # ── Confirmação ───────────────────────────────────────────────────────────
    def _draw_confirm(self, surface):
        alpha = self.confirm_alpha
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(180, alpha)))
        surface.blit(overlay, (0, 0))

        if alpha < 60:
            return

        box_w, box_h = 480, 160
        bx = WIDTH // 2 - box_w // 2
        by = HEIGHT // 2 - box_h // 2

        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((12, 10, 10, min(240, alpha)))
        surface.blit(box, (bx, by))
        pygame.draw.rect(surface, RED_MID, (bx, by, box_w, box_h), 1)
        pygame.draw.rect(surface, RED_DARK, (bx + 2, by + 2, box_w - 4, box_h - 4), 1)

        name = self.player_name.strip().upper()
        line1 = font_body.render(f'"{name}"', True, CREAM)
        l1r = line1.get_rect(center=(WIDTH // 2, by + 42))
        surface.blit(line1, l1r)

        line2 = font_small.render("Essa é sua história. Não tem volta.", True, DIM_CREAM)
        l2r = line2.get_rect(center=(WIDTH // 2, by + 78))
        surface.blit(line2, l2r)

        pygame.draw.line(surface, RED_DARK,
                         (bx + 40, by + 95), (bx + box_w - 40, by + 95), 1)

        confirm_txt = font_prompt.render(
            "[ ENTER / S ] Começar     [ ESC / N ] Voltar", True, MID_GRAY)
        cr = confirm_txt.get_rect(center=(WIDTH // 2, by + 124))
        surface.blit(confirm_txt, cr)


# ─── Loop principal ───────────────────────────────────────────────────────────
def main():
    scene = NewGameScreen()

    # Simulação de "qualquer tecla avança o intro"
    intro_advanced = False

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Avança a intro na primeira tecla
            if scene.phase == "intro" and scene.narrative_done and not intro_advanced:
                if event.type == pygame.KEYDOWN:
                    intro_advanced = True
                    scene.phase = "name_input"
                    scene.name_prompt_fade = 0.0
                    scene.name_prompt_alpha = 0

            result = scene.handle_event(event)
            if result == "done":
                print(f"\n[Novo Jogo iniciado] Protagonista: {scene.result}")
                # Aqui você conecta com o seu game loop principal
                # Ex: game_loop(player_name=scene.result)
                running = False
            elif result == "back":
                running = False

        scene.update(dt)
        scene.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()