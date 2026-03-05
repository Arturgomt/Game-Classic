import pygame
import math
import random

# Inicializa a fonte do Pygame
pygame.font.init()
fonte = pygame.font.SysFont("Arial", 36)

pontuacao = 0
game_over = False # Controla se o jogo acabou ou não
numero_asteroides = 5 # <-- NOVA VARIÁVEL

# Configurações da tela
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mini Asteroids")
relogio = pygame.time.Clock()

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

class Nave:
    def __init__(self):
        self.posicao = pygame.math.Vector2(LARGURA / 2, ALTURA / 2)
        self.velocidade = pygame.math.Vector2(0, 0)
        self.angulo = 0  
        self.aceleracao = 0.2
        self.atrito = 0.98 
        self.acelerando = False # <-- NOVA VARIÁVEL para saber se estamos acelerando

    def atualizar(self, teclas):
        if teclas[pygame.K_LEFT]:
            self.angulo -= 5
        if teclas[pygame.K_RIGHT]:
            self.angulo += 5

        # Verifica se estamos apertando para cima
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

        # --- NOVO: DESENHA O FOGO SE ESTIVER ACELERANDO ---
        if self.acelerando:
            # Pega o ângulo oposto (radianos + Pi, que equivale a 180 graus)
            # O random faz o tamanho do fogo variar para parecer que está piscando
            tamanho_fogo = random.randint(20, 35)
            fogo_vetor = pygame.math.Vector2(math.cos(rad + math.pi), math.sin(rad + math.pi)) * tamanho_fogo
            
            ponto_fogo = (self.posicao.x + fogo_vetor.x, self.posicao.y + fogo_vetor.y)
            
            # Desenha duas linhas laranjas saindo da traseira da nave até o ponto do fogo
            COR_FOGO = (120, 81, 169) # Laranja
            pygame.draw.line(superficie, COR_FOGO, pontos[1], ponto_fogo, 2)
            pygame.draw.line(superficie, COR_FOGO, pontos[2], ponto_fogo, 2)
        # --------------------------------------------------
        
        pygame.draw.polygon(superficie, BRANCO, pontos, 2)
class Tiro:
    def __init__(self, x, y, angulo):
        # O tiro nasce exatamente na posição (ponto) onde a nave está
        self.posicao = pygame.math.Vector2(x, y)
        
        # Calculamos a direção para onde a nave está apontando
        radianos = math.radians(angulo)
        direcao = pygame.math.Vector2(math.cos(radianos), math.sin(radianos))
        
        # Multiplicamos por 10 porque o tiro precisa ser muito mais rápido que a nave
        self.velocidade = direcao * 10

    def atualizar(self):
        # O tiro apenas avança, não sofre atrito nem precisa de aceleração
        self.posicao += self.velocidade

    def desenhar(self, superficie):
        # Desenhamos uma bolinha (círculo) branca pequena
        pygame.draw.circle(superficie, BRANCO, (int(self.posicao.x), int(self.posicao.y)), 3)

class Asteroide:
    def __init__(self, x=None, y=None, raio=None):
        # 1. POSIÇÃO (Nascimento com Área Segura)
        if x is not None and y is not None:
            # Se passamos o X e Y (quando o asteroide grande se divide), nasce ali mesmo
            self.posicao = pygame.math.Vector2(x, y)
        else:
            # NOVO: Criação de novos asteroides com Zona Segura
            zona_segura = 150 # Distância mínima em pixels (ajuste se quiser maior)
            centro_tela = pygame.math.Vector2(LARGURA / 2, ALTURA / 2)
            
            # Fica sorteando posições até achar uma que fique longe do centro
            while True:
                pos_x = random.randint(0, LARGURA)
                pos_y = random.randint(0, ALTURA)
                pos_teste = pygame.math.Vector2(pos_x, pos_y)
                
                # Se a distância entre o ponto sorteado e o centro for maior que 150...
                if pos_teste.distance_to(centro_tela) > zona_segura:
                    self.posicao = pos_teste
                    break # ... sai do loop e aprova a posição!
        
        # 2. TAMANHO
        if raio is not None:
            self.raio = raio
        else:
            self.raio = random.randint(30, 50)

        # 3. VETOR DE MOVIMENTO
        angulo_vel = random.uniform(0, 360)
        radianos_vel = math.radians(angulo_vel)
        direcao = pygame.math.Vector2(math.cos(radianos_vel), math.sin(radianos_vel))
        self.velocidade = direcao * random.uniform(1, 3)

        # --- NOVO: GERANDO O FORMATO IRREGULAR DA ROCHA ---
        self.offsets_pontos = [] # Guarda a distância de cada ponta em relação ao centro
        num_pontos = random.randint(8, 12) # O asteroide terá entre 8 e 12 lados
        
        for i in range(num_pontos):
            # Divide um círculo (360 graus) pelo número de pontas
            angulo_ponto = math.radians((360 / num_pontos) * i)
            
            # A Mágica: O raio de cada ponta varia entre 70% e 130% do raio original.
            # Isso é o que deixa a pedra "torta" e esburacada!
            distancia_ponta = self.raio * random.uniform(0.7, 1.3)
            
            # Transforma o ângulo e a distância em uma coordenada X e Y (Vetor)
            x_offset = math.cos(angulo_ponto) * distancia_ponta
            y_offset = math.sin(angulo_ponto) * distancia_ponta
            
            self.offsets_pontos.append(pygame.math.Vector2(x_offset, y_offset))
        # --------------------------------------------------

    def atualizar(self):
        self.posicao += self.velocidade
        
        if self.posicao.x > LARGURA + self.raio: self.posicao.x = -self.raio
        elif self.posicao.x < -self.raio: self.posicao.x = LARGURA + self.raio
        if self.posicao.y > ALTURA + self.raio: self.posicao.y = -self.raio
        elif self.posicao.y < -self.raio: self.posicao.y = ALTURA + self.raio

    def desenhar(self, superficie):
        # --- NOVO: DESENHANDO O POLÍGONO ---
        pontos_reais = []
        
        # Pegamos os pontos que sorteamos no nascimento e somamos com a posição 
        # atual do asteroide para saber onde desenhar na tela agora
        for offset in self.offsets_pontos:
            pontos_reais.append((self.posicao.x + offset.x, self.posicao.y + offset.y))
        
        # Desenha as linhas conectando todos os pontos gerados (espessura 2)
        pygame.draw.polygon(superficie, BRANCO, pontos_reais, 2)
        # -----------------------------------
# Instancia os objetos do jogo
jogador = Nave()
tiros = []
asteroides = []
for _ in range(5):
    asteroides.append(Asteroide())

  
# Loop principal do jogo
rodando = True
while rodando:
    relogio.tick(60)
    
    # 1. EVENTOS
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            # Só atira se NÃO estiver em Game Over
            if evento.key == pygame.K_SPACE and not game_over:
                novo_tiro = Tiro(jogador.posicao.x, jogador.posicao.y, jogador.angulo)
                tiros.append(novo_tiro)
            # Reinicia o jogo se apertar 'R'
            elif evento.key == pygame.K_r and game_over:
                jogador = Nave()
                tiros = []
                asteroides = []
                numero_asteroides = 5 # <-- RESETA A DIFICULDADE AQUI
                for _ in range(numero_asteroides):
                    asteroides.append(Asteroide())
                pontuacao = 0
                game_over = False

    # 2. LÓGICA E ATUALIZAÇÕES (Só rodam se o jogo não acabou)
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
                
                # Distância entre os dois asteroides
                distancia = ast1.posicao.distance_to(ast2.posicao)
                soma_raios = ast1.raio + ast2.raio
                
                if distancia < soma_raios:
                    # 1. Física de "Quicar": Trocam as velocidades (vetores)
                    ast1.velocidade, ast2.velocidade = ast2.velocidade, ast1.velocidade
                    
                    # 2. Prevenir que fiquem colados: Empurra os dois para direções opostas
                    if distancia > 0: # Evita erro de divisão por zero
                        # Descobre quantos pixels eles entraram um no outro
                        sobreposicao = soma_raios - distancia 
                        
                        # Cria um vetor normalizado (tamanho 1) apontando do ast2 para o ast1
                        direcao_afastamento = (ast1.posicao - ast2.posicao).normalize()
                        
                        # Afasta eles metade da sobreposicao para cada lado
                        ast1.posicao += direcao_afastamento * (sobreposicao / 2)
                        ast2.posicao -= direcao_afastamento * (sobreposicao / 2)
        # Colisão TIRO x ASTEROIDE
        tiros_destruidos = []
        asteroides_destruidos = []
        novos_asteroides = []

        for tiro in tiros:
            for asteroide in asteroides:
                distancia = tiro.posicao.distance_to(asteroide.posicao)
                if distancia < asteroide.raio:
                    tiros_destruidos.append(tiro)
                    asteroides_destruidos.append(asteroide)
                    
                    # GANHA PONTOS! 100 por asteroide grande, 50 por pequeno
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

        # Colisão NAVE x ASTEROIDE
        raio_colisao_nave = 15
        for asteroide in asteroides:
            distancia = jogador.posicao.distance_to(asteroide.posicao)
            if distancia < asteroide.raio + raio_colisao_nave:
                game_over = True # Em vez de fechar, ativamos o Game Over!

    if len(asteroides) == 0:
            numero_asteroides += 1 # Aumenta a dificuldade (+1 asteroide)
            
            for _ in range(numero_asteroides):
                asteroides.append(Asteroide())
    # 3. RENDERIZAÇÃO (DESENHO)
    tela.fill(PRETO)
    
    # Só desenha a nave se não for Game Over
    if not game_over:
        jogador.desenhar(tela)
    
    for tiro in tiros:
        tiro.desenhar(tela)
    for asteroide in asteroides:
        asteroide.desenhar(tela)
        
    # Desenha a Pontuação na tela (canto superior esquerdo)
    texto_pontos = fonte.render(f"Pontos: {pontuacao}", True, BRANCO)
    tela.blit(texto_pontos, (10, 10))

    # Desenha a mensagem de Game Over no centro da tela
    if game_over:
        texto_go = fonte.render("GAME OVER - Aperte 'R' para reiniciar", True, BRANCO)
        # Calcula o centro da tela para o texto
        rect_texto = texto_go.get_rect(center=(LARGURA/2, ALTURA/2))
        tela.blit(texto_go, rect_texto)
    
    pygame.display.flip()

pygame.quit()