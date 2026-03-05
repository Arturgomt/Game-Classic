import pygame
import math
import random

# Inicializa a fonte do Pygame
pygame.font.init()
fonte = pygame.font.SysFont("Arial", 36)

pontuacao = 0
game_over = False # Controla se o jogo acabou ou não
numero_asteroides = 5 # <-- NOVA VARIÁVEL

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mini Asteroids")
relogio = pygame.time.Clock()

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

#Função NAVE 
class Nave:
    def __init__(self):
        self.posicao = pygame.math.Vector2(LARGURA / 2, ALTURA / 2)
        self.velocidade = pygame.math.Vector2(0, 0)
        self.angulo = 0  
        self.aceleracao = 0.2
        self.atrito = 0.98 
        self.acelerando = False

    def atualizar(self, teclas):
        if teclas[pygame.K_LEFT]:
            self.angulo -= 5
        if teclas[pygame.K_RIGHT]:
            self.angulo += 5

        self.acelerando = teclas[pygame.K_UP]
        
        if self.acelerando:
            radianos = math.radians(self.angulo)
            direcao = pygame.math.Vector2(math.cos(radianos), math.sin(radianos))
            self.velocidade += direcao * self.aceleracao

        self.velocidade *= self.atrito
        self.posicao += self.velocidade

        if self.posicao.x > LARGURA: self.posicao.x = 0
        elif self.posicao.x < 0: self.posicao.x = LARGURA
        if self.posicao.y > ALTURA: self.posicao.y = 0
        elif self.posicao.y < 0: self.posicao.y = ALTURA

    def desenhar(self, superficie):
        rad = math.radians(self.angulo)
        
        ponta = pygame.math.Vector2(math.cos(rad), math.sin(rad)) * 20
        esq = pygame.math.Vector2(math.cos(rad - 2.5), math.sin(rad - 2.5)) * 15
        dir_p = pygame.math.Vector2(math.cos(rad + 2.5), math.sin(rad + 2.5)) * 15

        pontos = [
            (self.posicao.x + ponta.x, self.posicao.y + ponta.y),
            (self.posicao.x + esq.x, self.posicao.y + esq.y),
            (self.posicao.x + dir_p.x, self.posicao.y + dir_p.y)
        ]
        
        pygame.draw.polygon(superficie, BRANCO, pontos, 2)

        if self.acelerando:
            tamanho_fogo = random.randint(20, 35)
            fogo_vetor = pygame.math.Vector2(math.cos(rad + math.pi), math.sin(rad + math.pi)) * tamanho_fogo
            
            ponto_fogo = (self.posicao.x + fogo_vetor.x, self.posicao.y + fogo_vetor.y)
            
            COR_FOGO = (120, 81, 169) # Laranja
            pygame.draw.line(superficie, COR_FOGO, pontos[1], ponto_fogo, 2)
            pygame.draw.line(superficie, COR_FOGO, pontos[2], ponto_fogo, 2)
        
        pygame.draw.polygon(superficie, BRANCO, pontos, 2)

#Função de tiro da nave
class Tiro:
    def __init__(self, x, y, angulo):
        self.posicao = pygame.math.Vector2(x, y)
        radianos = math.radians(angulo)
        direcao = pygame.math.Vector2(math.cos(radianos), math.sin(radianos))
        
        self.velocidade = direcao * 10

    def atualizar(self):
        self.posicao += self.velocidade

    def desenhar(self, superficie):
        pygame.draw.circle(superficie, BRANCO, (int(self.posicao.x), int(self.posicao.y)), 3)
        
#Função do Asteriod
class Asteroide:
    def __init__(self, x=None, y=None, raio=None):
        if x is not None and y is not None:
            self.posicao = pygame.math.Vector2(x, y)
        else:
            zona_segura = 150 
            centro_tela = pygame.math.Vector2(LARGURA / 2, ALTURA / 2)
            
            while True:
                pos_x = random.randint(0, LARGURA)
                pos_y = random.randint(0, ALTURA)
                pos_teste = pygame.math.Vector2(pos_x, pos_y)
                
                if pos_teste.distance_to(centro_tela) > zona_segura:
                    self.posicao = pos_teste
                    break # ... sai do loop e aprova a posição!
        
        if raio is not None:
            self.raio = raio
        else:
            self.raio = random.randint(30, 50)

        # 3. Vetor de Movimento do Asteriod
        angulo_vel = random.uniform(0, 360)
        radianos_vel = math.radians(angulo_vel)
        direcao = pygame.math.Vector2(math.cos(radianos_vel), math.sin(radianos_vel))
        self.velocidade = direcao * random.uniform(1, 3)
        
        self.offsets_pontos = [] # Guarda a distância de cada ponta em relação ao centro
        num_pontos = random.randint(8, 12) # O asteroide terá entre 8 e 12 lados
        
        for i in range(num_pontos):
            angulo_ponto = math.radians((360 / num_pontos) * i)
            
            distancia_ponta = self.raio * random.uniform(0.7, 1.3)
            
            x_offset = math.cos(angulo_ponto) * distancia_ponta
            y_offset = math.sin(angulo_ponto) * distancia_ponta
            
            self.offsets_pontos.append(pygame.math.Vector2(x_offset, y_offset))

    def atualizar(self):
        self.posicao += self.velocidade
        
        if self.posicao.x > LARGURA + self.raio: self.posicao.x = -self.raio
        elif self.posicao.x < -self.raio: self.posicao.x = LARGURA + self.raio
        if self.posicao.y > ALTURA + self.raio: self.posicao.y = -self.raio
        elif self.posicao.y < -self.raio: self.posicao.y = ALTURA + self.raio

    def desenhar(self, superficie):
        pontos_reais = []
        
        for offset in self.offsets_pontos:
            pontos_reais.append((self.posicao.x + offset.x, self.posicao.y + offset.y))
        
        pygame.draw.polygon(superficie, BRANCO, pontos_reais, 2)
        
# Instancia os objetos
jogador = Nave()
tiros = []
asteroides = []
for _ in range(5):
    asteroides.append(Asteroide())

  
# Loop principal do jogo
rodando = True
while rodando:
    relogio.tick(60)
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_SPACE and not game_over:
                novo_tiro = Tiro(jogador.posicao.x, jogador.posicao.y, jogador.angulo)
                tiros.append(novo_tiro)

            elif evento.key == pygame.K_r and game_over:
                jogador = Nave()
                tiros = []
                asteroides = []
                numero_asteroides = 5 
                for _ in range(numero_asteroides):
                    asteroides.append(Asteroide())
                pontuacao = 0
                game_over = False

    if not game_over:
        teclas = pygame.key.get_pressed()
        jogador.atualizar(teclas)

        for tiro in tiros:
            tiro.atualizar()
        for asteroide in asteroides:
            asteroide.atualizar()
        for i in range(len(asteroides)):
            for j in range(i + 1, len(asteroides)):
                ast1 = asteroides[i]
                ast2 = asteroides[j]
                
                distancia = ast1.posicao.distance_to(ast2.posicao)
                soma_raios = ast1.raio + ast2.raio
                
                if distancia < soma_raios:
                    ast1.velocidade, ast2.velocidade = ast2.velocidade, ast1.velocidade
                    
                    if distancia > 0: # Evita erro de divisão por zero
                        sobreposicao = soma_raios - distancia 
                        
                        direcao_afastamento = (ast1.posicao - ast2.posicao).normalize()
                        
                        ast1.posicao += direcao_afastamento * (sobreposicao / 2)
                        ast2.posicao -= direcao_afastamento * (sobreposicao / 2)
        tiros_destruidos = []
        asteroides_destruidos = []
        novos_asteroides = []

        for tiro in tiros:
            for asteroide in asteroides:
                distancia = tiro.posicao.distance_to(asteroide.posicao)
                if distancia < asteroide.raio:
                    tiros_destruidos.append(tiro)
                    asteroides_destruidos.append(asteroide)
                    
                    if asteroide.raio > 20:
                        pontuacao += 100
                        novo_raio = asteroide.raio // 2
                        novos_asteroides.append(Asteroide(asteroide.posicao.x, asteroide.posicao.y, novo_raio))
                        novos_asteroides.append(Asteroide(asteroide.posicao.x, asteroide.posicao.y, novo_raio))
                    else:
                        pontuacao += 50
                    break 

        for tiro in tiros_destruidos:
            if tiro in tiros: tiros.remove(tiro)
        for asteroide in asteroides_destruidos:
            if asteroide in asteroides: asteroides.remove(asteroide)
        asteroides.extend(novos_asteroides)

        raio_colisao_nave = 15
        for asteroide in asteroides:
            distancia = jogador.posicao.distance_to(asteroide.posicao)
            if distancia < asteroide.raio + raio_colisao_nave:
                game_over = True

    if len(asteroides) == 0:
            numero_asteroides += 3 # Aumenta a dificuldade (+1 asteroide)
            
            for _ in range(numero_asteroides):
                asteroides.append(Asteroide())

    tela.fill(PRETO)

    if not game_over:
        jogador.desenhar(tela)
    
    for tiro in tiros:
        tiro.desenhar(tela)
    for asteroide in asteroides:
        asteroide.desenhar(tela)
        
    texto_pontos = fonte.render(f"Pontos: {pontuacao}", True, BRANCO)
    tela.blit(texto_pontos, (10, 10))

    if game_over:
        texto_go = fonte.render("GAME OVER - Aperte 'R' para reiniciar", True, BRANCO)
        # Calcula o centro da tela para o texto
        rect_texto = texto_go.get_rect(center=(LARGURA/2, ALTURA/2))
        tela.blit(texto_go, rect_texto)
    
    pygame.display.flip()


pygame.quit()
