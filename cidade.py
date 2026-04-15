import pygame
import random

WIDTH = 1000
HEIGHT = 600

camera_x = 0

buildings = []

for i in range(40):
    x = i * 120
    altura = random.randint(150, 400)

    buildings.append({
        "x": x,
        "altura": altura
    })


camadas=[
    {"vel": 0.3, "cor": (15, 15, 25)}, #longe
    {"vel": 0.6, "cor": (25, 25, 35)}, #medio
    {"vel": 1, "cor": (40, 40, 60)}    #perto
]
def draw_cidade(surface, camera_x):

    for camada in camadas:

        offset = camera_x * camada["vel"]

        for b in buildings:

            rect = pygame.Rect(
                b["x"] - offset,
                HEIGHT - b["altura"],
                100,
                b["altura"]
            )

            pygame.draw.rect(surface, camada["cor"], rect)