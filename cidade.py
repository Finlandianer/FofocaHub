import pygame
import random

# ───────── CONFIG ─────────
WIDTH = 1000
HEIGHT = 600
WORLD_WIDTH = 5000

lightning_alpha = 0
lightning_timer = 3


# ───────── GERAR PRÉDIOS ─────────
def gerar_predios(qtd, espacamento, altura_min, altura_max, escala):

    lista = []

    for i in range(qtd):

        altura = random.randint(altura_min, altura_max)
        largura = int(100 * escala)

        # padrão FIXO de janelas
        janelas = []
        linhas = altura // 30

        for _ in range(linhas):
            linha = []
            for _ in range(3):
                linha.append(random.random() < 0.6)
            janelas.append(linha)

        lista.append({
            "x": i * espacamento,
            "altura": altura,
            "largura": largura,
            "cor": (
                random.randint(20, 40),
                random.randint(20, 40),
                random.randint(35, 60)
            ),
            "janelas": janelas
        })

    return lista


# ───────── CAMADAS PARALLAX ─────────
camadas = [

    # LONGE
    {
        "vel": 0.2,
        "predios": gerar_predios(25, 220, 80, 180, 0.6)
    },

    # MÉDIO
    {
        "vel": 0.5,
        "predios": gerar_predios(30, 170, 120, 260, 0.8)
    },

    # PERTO
    {
        "vel": 1.0,
        "predios": gerar_predios(35, 130, 200, 420, 1.0)
    }
]


# ───────── RELÂMPAGO UPDATE ─────────
def update_lightning(dt):

    global lightning_alpha, lightning_timer

    lightning_timer -= dt

    # chance de raio
    if lightning_timer <= 0 and random.random() < 0.002:
        lightning_alpha = random.randint(200, 255)
        lightning_timer = random.uniform(4, 8)

    # fade rápido
    lightning_alpha = max(0, lightning_alpha - 700 * dt)


# ───────── DESENHAR RELÂMPAGO ─────────
def draw_lightning(surface):

    if lightning_alpha <= 0:
        return

    flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    flash.fill((220, 230, 255, int(lightning_alpha)))

    surface.blit(flash, (0, 0))


# ───────── DESENHAR CIDADE ─────────
def draw_cidade(surface, camera_x):

    for camada in camadas:

        offset = (camera_x * camada["vel"]) % WORLD_WIDTH

        for b in camada["predios"]:

            # desenha duas cópias → loop infinito
            for i in range(2):

                x_pos = b["x"] - offset + i * WORLD_WIDTH

                rect = pygame.Rect(
                    x_pos,
                    HEIGHT - b["altura"],
                    b["largura"],
                    b["altura"]
                )

                # iluminação do relâmpago
                cor = list(b["cor"])

                if lightning_alpha > 0:
                    cor[0] += 80
                    cor[1] += 80
                    cor[2] += 100
                    cor = [min(255, c) for c in cor]

                # ───── CORPO DO PRÉDIO ─────
                pygame.draw.rect(surface, cor, rect)

                # ───── SOMBRA ESQUERDA ─────
                pygame.draw.rect(
                    surface,
                    (10, 10, 15),
                    (rect.x, rect.y, 6, rect.height)
                )

                # ───── BORDA DIREITA CLARA ─────
                pygame.draw.rect(
                    surface,
                    (
                        min(255, cor[0] + 25),
                        min(255, cor[1] + 25),
                        min(255, cor[2] + 25)
                    ),
                    (rect.right - 4, rect.y, 4, rect.height)
                )

                # ───── TOPO DO PRÉDIO ─────
                pygame.draw.rect(
                    surface,
                    (15, 15, 20),
                    (rect.x, rect.y, rect.width, 5)
                )

                # ───── DIVISÕES VERTICAIS ─────
                for linha in range(rect.x + 20, rect.right, 40):
                    pygame.draw.line(
                        surface,
                        (25, 25, 30),
                        (linha, rect.y),
                        (linha, rect.bottom),
                        1
                    )

                # ───── JANELAS ─────
                for row_i, row in enumerate(b["janelas"]):
                    for col_i, acesa in enumerate(row):

                        if acesa:

                            x = rect.x + 15 + col_i * 25
                            y = rect.y + 20 + row_i * 30

                            cor_janela = (160, 140, 70)

                            if lightning_alpha > 0:
                                cor_janela = (210, 210, 160)

                            pygame.draw.rect(
                                surface,
                                cor_janela,
                                (x, y, 8, 12)
                            )