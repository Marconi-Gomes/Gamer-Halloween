import pygame
import sys
import random
import os

# Configuração de diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'sprit')
background_image_path = os.path.join(IMAGES_DIR, 'Mundo.png')
character_image_path = os.path.join(IMAGES_DIR, 'euatualizado.png')
enemy_image_path = os.path.join(IMAGES_DIR, 'fantasma.png')

# Inicializa o Pygame
pygame.init()

# Configurações da tela
largura, altura = 1050, 600
screen = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Mundo Estranho de Marconi")

# Cores
branco = (255, 255, 255)
vermelho = (255, 0, 0)
verde = (0, 255, 0)

# Carrega a imagem de fundo
try:
    imagem_fundo = pygame.image.load(background_image_path)
    imagem_fundo = pygame.transform.scale(imagem_fundo, (largura, altura))
except pygame.error as e:
    print(f"Erro ao carregar a imagem de fundo: {e}")
    pygame.quit()
    sys.exit()

# Carrega a imagem do personagem principal
try:
    imagem_personagem = pygame.image.load(character_image_path)
    imagem_personagem = pygame.transform.scale(imagem_personagem, (150, 100))
except pygame.error as e:
    print(f"Erro ao carregar a imagem do personagem: {e}")
    imagem_personagem = None

# Carrega a imagem do inimigo
try:
    imagem_inimigo = pygame.image.load(enemy_image_path)
    imagem_inimigo = pygame.transform.scale(imagem_inimigo, (150, 100))
except pygame.error as e:
    print(f"Erro ao carregar a imagem do inimigo: {e}")
    imagem_inimigo = None

# Classe do projétil
class Projétil:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 5)
        self.velocidade = 15

    def mover(self):
        self.rect.x += self.velocidade

    def desenhar(self, tela):
        pygame.draw.rect(tela, vermelho, self.rect)

# Classe do jogador
class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, altura - 100, 60, 80)
        self.velocidade = 10
        self.velocidade_salto = 30
        self.saltando = False
        self.gravidade = 3
        self.vel_y = 0
        self.pulos = 0
        self.tempo_ultimo_pulo = 0
        self.movendo = False
        self.hp = 100
        self.projetéis = []
        self.pontos = 0
        self.tempo_ultimo_tiro = 0
        self.municao = 10  # Quantidade inicial de munição

    def mover(self, direcao):
        if direcao == 'direita' and self.rect.x < largura - self.rect.width:
            self.rect.x += self.velocidade
        elif direcao == 'esquerda' and self.rect.x > 0:
            self.rect.x -= self.velocidade

    def pular(self):
        if not self.saltando:
            self.saltando = True
            self.vel_y = -self.velocidade_salto

    def atualizar(self):
        # Atualiza a posição vertical durante o salto
        self.rect.y += self.vel_y
        if self.saltando:
            self.vel_y += self.gravidade
            # Checa se o personagem atingiu o chão
            if self.rect.bottom >= altura - 20:
                self.rect.bottom = altura - 20
                self.saltando = False
                self.vel_y = 0
                self.pulos = 0

        # Atualiza projéteis
        for projétil in self.projetéis[:]:
            projétil.mover()
            if projétil.rect.x > largura:  # Remove projéteis que saem da tela
                self.projetéis.remove(projétil)

    def atirar(self, tempo_atual):
        if self.municao > 0 and tempo_atual - self.tempo_ultimo_tiro >= 1000:
            self.projetéis.append(Projétil(self.rect.centerx + 10, self.rect.centery - 1))
            self.tempo_ultimo_tiro = tempo_atual
            self.municao -= 1  # Reduz a munição ao atirar

    def recarregar(self):
        self.municao = 10  # Recarrega a munição para 10

    def desenhar_barra_municao(self, tela):
        barra_largura = 100
        barra_altura = 10
        largura_atual = barra_largura * (self.municao / 10)  # Supondo que a munição máxima seja 10

        # Desenha a barra de fundo
        pygame.draw.rect(tela, (255, 0, 0), (10, 30, barra_largura, barra_altura))  # Barra de fundo em vermelho
        # Desenha a barra de munição
        pygame.draw.rect(tela, (0, 255, 0), (10, 30, largura_atual, barra_altura))  # Barra de munição em verde

    def desenhar(self, tela):
        if imagem_personagem:
            tela.blit(imagem_personagem, (self.rect.x, self.rect.y))
        pygame.draw.rect(tela, verde, (self.rect.x, self.rect.y - 10, 80, 10))
        # Desenha a quantidade de munição
        font = pygame.font.SysFont(None, 30)
        texto_municao = font.render(f'Munição: {self.municao}', True, branco)
        tela.blit(texto_municao, (10, 10))
        
        # Desenha a barra de munição
        self.desenhar_barra_municao(tela)

# Classe do inimigo
class Inimigo:
    
    def __init__(self, x_pos):
        self.rect = pygame.Rect(x_pos, altura - 100, 150, 100)  # Ajuste para a mesma altura da imagem
        self.velocidade = 9
        self.movendo_direita = True
        self.hp = 100

    def atualizar(self):
        if self.movendo_direita:
            self.rect.x += self.velocidade
            if self.rect.x >= largura - self.rect.width:  # Checa se alcançou a borda direita
                self.movendo_direita = False
        else:
            self.rect.x -= self.velocidade
            if self.rect.x <= 0:  # Checa se alcançou a borda esquerda
                self.movendo_direita = True   

    def receber_dano(self, dano):
        self.hp -= dano  # Diminui o HP do inimigo
        if self.hp <= 0:
            return True  # Retorna True se o inimigo foi derrotado
        return False          

    def desenhar(self, tela):
        if imagem_inimigo:
            tela.blit(imagem_inimigo, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(tela, vermelho, self.rect)

        # Desenha a barra de vida
        self.desenhar_barra_vida(tela)

    def desenhar_barra_vida(self, tela):
        barra_largura = 30
        barra_altura = 5
        largura_atual = barra_largura * (self.hp / 100)

        # Desenha a barra de fundo
        pygame.draw.rect(tela, (255, 0, 0), (self.rect.x, self.rect.y - 10, barra_largura, barra_altura))
        # Desenha a barra de vida
        pygame.draw.rect(tela, (0, 255, 0), (self.rect.x, self.rect.y - 10, largura_atual, barra_altura))

# Função para reiniciar o jogo
def reiniciar_jogo():
    global jogador, inimigos
    jogador = Player()
    inimigos = [Inimigo(random.randint(0, largura - 150))]

# Inicialização do jogo
jogador = Player()
inimigos = [Inimigo(random.randint(0, largura - 150))]

# Adicionando a variável para o tempo do último inimigo
tempo_ultimo_inimigo = pygame.time.get_ticks()  # Tempo do último inimigo adicionado

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(imagem_fundo, (0, 0))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        jogador.mover('esquerda')
    if keys[pygame.K_d]:
        jogador.mover('direita')
    if keys[pygame.K_w] and not jogador.saltando:
        jogador.pular()

    if keys[pygame.K_SPACE]:
        tempo_atual = pygame.time.get_ticks()
        jogador.atirar(tempo_atual)

    if keys[pygame.K_r]:  # Recarrega a munição
        jogador.recarregar()

    jogador.atualizar()

    for inimigo in inimigos:
        inimigo.atualizar()

    # Verifica se é hora de adicionar um novo inimigo
    tempo_atual = pygame.time.get_ticks()
    if tempo_atual - tempo_ultimo_inimigo >= 10000:  # A cada 10 segundos
        inimigos.append(Inimigo(random.randint(0, largura - 150)))
        tempo_ultimo_inimigo = tempo_atual  # Atualiza o tempo do último inimigo adicionado

    # Atualiza e desenha projéteis
    for projétil in jogador.projetéis[:]:
        projétil.desenhar(screen)

        # Verifica colisão com inimigos
        for inimigo in inimigos[:]:
            if projétil.rect.colliderect(inimigo.rect):
                if inimigo.receber_dano(20):  # Supondo que 20 seja o dano do projétil
                    inimigos.remove(inimigo)  # Remove o inimigo se for derrotado
                jogador.projetéis.remove(projétil)  # Remove o projétil após a colisão
                break  # Não verifique mais colisões para este projétil

    jogador.desenhar(screen)
    
    for inimigo in inimigos:
        inimigo.desenhar(screen)

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
