import pygame
import random
import os
import sys
import cv2 

pygame.init()

info = pygame.display.Info()
LARGURA = info.current_w
ALTURA = info.current_h
FPS = 60

# Cores
BRANCO = (255, 255, 255)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
PRETO = (0, 0, 0)
# Caminho da fonte 
caminho_fonte = os.path.join('assets', 'PressStart2P.ttf')

# Inicialização da tela
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("Esqueleto vs Valquiria")
clock = pygame.time.Clock()

# Coração (vidas)
caminho_heart = os.path.join('assets', 'heart.png')
heart_image = pygame.image.load(caminho_heart).convert_alpha()
heart_image = pygame.transform.scale(heart_image, (40, 40))
heart_image_small = pygame.transform.scale(heart_image, (15, 15))

# Fundo para os menus (lua.png)
caminho_fundo_menu = os.path.join('assets', 'lua.png')
fundo_menu = pygame.image.load(caminho_fundo_menu).convert()
fundo_menu = pygame.transform.scale(fundo_menu, (LARGURA, ALTURA))

# Sons
som_ataque = pygame.mixer.Sound(os.path.join('sounds', 'attack.wav'))
som_caminhada = pygame.mixer.Sound(os.path.join('sounds', 'walk.wav'))
som_ambiente_fase1 = pygame.mixer.Sound(os.path.join('sounds', 'ambiente.wav'))
som_ambiente_fase2 = pygame.mixer.Sound(os.path.join('sounds', 'wind.wav'))
som_ambiente_fase3 = pygame.mixer.Sound(os.path.join('sounds', 'battle.wav'))

som_ataque.set_volume(0.2)
som_caminhada.set_volume(0.2)
som_ambiente_fase1.set_volume(0.1)
som_ambiente_fase2.set_volume(0.1)
som_ambiente_fase3.set_volume(0.1)

vidas = 3
tempo_invencivel = 1000
fase = 1
avancar_fase = False
mostrar_aviso_avancar = False
tela_loading = False
fim_de_jogo = False


# Função para mostrar o vídeo de introdução

def mostrar_intro():
    # Caminho para o vídeo
    caminho_video = os.path.join('assets', 'intro.mp4')
    
    # Carregar o vídeo com OpenCV
    video = cv2.VideoCapture(caminho_video)

    # Verificar se o vídeo foi aberto corretamente
    if not video.isOpened():
        print("Erro ao abrir o vídeo!")
        return
    
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  # Total de frames do vídeo
    frame_rate = video.get(cv2.CAP_PROP_FPS)  # Taxa de frames por segundo

    while video.isOpened():
        ret, frame = video.read()
        
        if not ret:
            break
        
        # Converter a imagem de BGR (OpenCV) para RGB (Pygame)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Criar uma superfície Pygame com a imagem
        frame_surface = pygame.surfarray.make_surface(frame_rgb)

        # Obter as dimensões do frame do vídeo
        frame_height, frame_width, _ = frame.shape

        # Calcular a escala para preencher a tela sem distorcer
        scale_x = LARGURA / frame_width
        scale_y = ALTURA / frame_height
        scale_factor = max(scale_x, scale_y)  # Usando o fator de escala maior para preencher a tela

        # Redimensionar o vídeo para cobrir toda a tela
        new_width = int(frame_width * scale_factor)
        new_height = int(frame_height * scale_factor)

        # Redimensionar o frame para preencher a tela
        frame_surface = pygame.transform.scale(frame_surface, (new_width, new_height))

        # Calcular a posição para centralizar o vídeo na tela
        offset_x = (new_width - LARGURA) // 2
        offset_y = (new_height - ALTURA) // 2

        # Cortar a parte do vídeo que ultrapassa a tela (caso necessário)
        frame_surface = frame_surface.subsurface(pygame.Rect(offset_x, offset_y, LARGURA, ALTURA))

        # Exibir o vídeo centralizado
        tela.fill(PRETO)  # Preencher com preto antes de exibir o vídeo
        tela.blit(frame_surface, (0, 0))  # Exibir o vídeo centralizado

        # Desenhar o texto "Aperte 'Space' para pular a intro" no canto inferior esquerdo
        fonte = pygame.font.Font(caminho_fonte, 12)  # Usando a fonte personalizada
        texto_pular = fonte.render("Pressione 'Space' para pular . . .", True, BRANCO)
        tela.blit(texto_pular, (LARGURA - 350, ALTURA - 50))  # Texto mais para a esquerda

        # Atualizar a tela
        pygame.display.update()

        # Calcular o tempo restante no vídeo
        current_frame = int(video.get(cv2.CAP_PROP_POS_FRAMES))  # Frame atual do vídeo
        tempo_restante = (total_frames - current_frame) / frame_rate  # Tempo restante até o final

        # Se faltar menos de 0.5 segundos, simula o pressionamento da tecla "Space"
        if tempo_restante <= 0.5:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

        # Esperar um pouco antes de mostrar o próximo frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Se pressionar 'space', pula o vídeo e vai direto para o menu
                if event.key == pygame.K_SPACE:
                    video.release()  # Finaliza o vídeo
                    return  # Sai da função e vai direto para o menu

        clock.tick(FPS)

    # Quando o vídeo acabar, voltar ao menu principal
    menu_principal()



# ===== FUNÇÃO DO MENU PRINCIPAL =====
def menu_principal():
    while True:
        tela.blit(fundo_menu, (0, 0))

        fonte_titulo = pygame.font.Font(caminho_fonte, 40)
        fonte_opcao = pygame.font.Font(caminho_fonte, 30)

        titulo = fonte_titulo.render("Esqueleto vs Valquírias", True, BRANCO)
        titulo_rect = titulo.get_rect(center=(LARGURA // 2, 80))
        tela.blit(titulo, titulo_rect)

        # Lista de opções com suas cores e ações associadas
        opcoes = [
            ("1 - Iniciar Jogo", VERDE, "iniciar"),
            ("2 - Ajuda", VERDE, "ajuda"),
            ("3 - Sair do Jogo", VERMELHO, "sair"),
        ]

        botoes = []  # Lista com (rect, ação)

        for i, (texto, cor, acao) in enumerate(opcoes):
            texto_render = fonte_opcao.render(texto, True, cor)
            texto_rect = texto_render.get_rect(topleft=(50, ALTURA - 200 + i * 60))
            tela.blit(texto_render, texto_rect)
            botoes.append((texto_rect, acao))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # CLIQUE COM O MOUSE → executa diretamente a ação
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for rect, acao in botoes:
                    if rect.collidepoint(mouse_x, mouse_y):
                        if acao == "iniciar":
                            reiniciar_jogo()
                            return
                        elif acao == "ajuda":
                            tela_ajuda()
                        elif acao == "sair":
                            pygame.quit()
                            sys.exit()

            # TECLADO continua funcionando normalmente
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    reiniciar_jogo()
                    return
                elif event.key == pygame.K_2:
                    tela_ajuda()
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()




# Função para reiniciar o jogo
def reiniciar_jogo():
    # Aqui você pode inicializar o jogo, como reiniciar as variáveis e a fase
    print("Iniciando o jogo...")  # Aqui é apenas um exemplo
    fase = 1  # Como exemplo, você pode redefinir a fase aqui.
    # Adicione o código necessário para inicializar a fase do jogo.
    # Você também pode chamar funções para carregar os recursos do jogo, se necessário.


# Chama a função de introdução quando o jogo inicia
mostrar_intro()




# ===== FUNÇÃO DE MODAL ATUALIZADA =====
def desenhar_modal(textos, cor_texto=BRANCO, cor_modal=(30, 30, 30), largura=None, altura=None):
    if largura is None:
        largura = int(LARGURA * 0.8)
    if altura is None:
        altura = int(ALTURA * 0.6)

    modal_surface = pygame.Surface((largura, altura))
    modal_surface.set_alpha(220)
    modal_surface.fill(cor_modal)

    pos_x = (LARGURA - largura) // 2
    pos_y = (ALTURA - altura) // 2

    tela.blit(modal_surface, (pos_x, pos_y))

    fonte = pygame.font.Font(caminho_fonte, 16)
    texto_rects = []  # <- coletar os retângulos clicáveis

    for i, texto in enumerate(textos):
        linha = fonte.render(texto, True, cor_texto)
        texto_rect = linha.get_rect(center=(LARGURA // 2, pos_y + 60 + i * 45))
        tela.blit(linha, texto_rect)

        # Adiciona apenas retângulos de linhas que são opções (excluindo títulos/linhas vazias)
        if texto.strip().startswith("1") or texto.strip().startswith("2") or texto.strip().startswith("3") or texto.strip().startswith("4"):
            texto_rects.append((texto_rect, texto.strip()[0]))  # (rect, número da opção)

    return texto_rects  # <- retorna os retângulos das opções



# ===== FUNÇÃO DE HISTÓRIA POR FASE COM FUNDO REAL DO JOGO =====
def mostrar_historia_fase(fase):
    textos = []

    if fase == 1:
        textos = [
            "O Esqueleto escapou de Helheim.",
            "Agora, persegue sua vinganca contra as Valquirias.",
            "Elas o condenaram injustamente ao submundo.",
            "A jornada pela verdade comeca agora.",
            "",
            "Pressione qualquer tecla para continuar..."
        ]
    elif fase == 2:
        textos = [
            "O caminho se torna mais perigoso.",
            "Valquirias cada vez mais fortes o cacam.",
            "Mas os ecos da verdade surgem entre as sombras.",
            "",
            "Pressione qualquer tecla para continuar..."
        ]
    elif fase == 3:
        textos = [
            "O Esqueleto se aproxima do seu destino final.",
            "A Lider das Valquirias o aguarda.",
            "A verdade esta prestes a ser revelada.",
            "Hora de enfrentar seu passado.",
            "",
            "Pressione qualquer tecla para continuar..."
        ]

    tela.blit(fundo, (0, 0))
    for plataforma in plataformas:
        tela.blit(plataforma.image, plataforma.rect)

    if jogador:
        tela.blit(jogador.image, jogador.rect)

    for inimigo in grupo_inimigos:
        tela.blit(inimigo.image, inimigo.rect)
        if hasattr(inimigo, 'vida_coracoes'):
            for pos in inimigo.vida_coracoes:
                tela.blit(heart_image_small, pos)

    for i in range(vidas):
        tela.blit(heart_image, (10 + i * 45, 10))

    desenhar_modal(textos)
    pygame.display.flip()

    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                esperando = False
def carregar_fundo():
    global fundo
    if fase == 1:
        fundo = pygame.image.load(os.path.join('background', 'primeira_fase', 'fase_1.png')).convert()
    elif fase == 2:
        fundo = pygame.image.load(os.path.join('background', 'segunda_fase', 'fase_2.png')).convert()
    elif fase == 3:
        fundo = pygame.image.load(os.path.join('background', 'terceira_fase', 'fase_3.png')).convert()
    else:
        fundo = pygame.image.load(os.path.join('background', 'primeira_fase', 'fase_1.png')).convert()
    fundo = pygame.transform.scale(fundo, (LARGURA, ALTURA))

def tocar_som_ambiente():
    pygame.mixer.stop()
    if fase == 1:
        som_ambiente_fase1.play(loops=-1)
    elif fase == 2:
        som_ambiente_fase2.play(loops=-1)
    elif fase == 3:
        som_ambiente_fase3.play(loops=-1)


def tela_ajuda():
    tela.blit(fundo_menu, (0, 0))

    # Desenhar o modal de ajuda usando a fonte personalizada
    desenhar_modal([  # Usando a fonte personalizada no modal de ajuda
        "AJUDA - COMANDOS DO JOGO",
        "",
        "← → : Mover personagem",
        "Barra de espaço: Pular",
        "Tecla A: Atacar",
        "ESC: Abrir menu de pausa",
        "Dica: Ao passar de fase, o jogador recupera 1 vida",
        "",
        "Pressione qualquer tecla para voltar"
    ], cor_texto=BRANCO)  # Mantemos a cor branca para o texto

    pygame.display.flip()
    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                esperando = False


def menu_pausa():
    pausado = True
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()

    while pausado:
        tela.blit(fundo_menu, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        tela.blit(overlay, (0, 0))

        texto_opcoes = [
            "PAUSA",
            "",
            "1 - Reiniciar Jogo",
            "2 - Voltar ao Menu Principal",
            "3 - Continuar Jogando",
            "4 - Sair do Jogo"
        ]
        botoes = desenhar_modal(texto_opcoes)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Clique do mouse → aciona ações
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for rect, opcao in botoes:
                    if rect.collidepoint(mouse_pos):
                        if opcao == "1":
                            reiniciar_jogo()
                            pausado = False
                        elif opcao == "2":
                            menu_principal()
                            reiniciar_jogo()
                            pausado = False
                        elif opcao == "3":
                            pygame.mixer.music.unpause()
                            pausado = False
                        elif opcao == "4":
                            pygame.quit()
                            sys.exit()

            # Teclado ainda funcionando
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    reiniciar_jogo()
                    pausado = False
                elif event.key == pygame.K_2:
                    menu_principal()
                    reiniciar_jogo()
                    pausado = False
                elif event.key == pygame.K_3:
                    pygame.mixer.music.unpause()
                    pausado = False
                elif event.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.unpause()
                    pausado = False


def tela_game_over():
    while True:
        tela.blit(fundo_menu, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        tela.blit(overlay, (0, 0))

        texto_opcoes = [
            "GAME OVER",
            "",
            "1 - Tentar Novamente",
            "2 - Voltar ao Menu Principal",
            "3 - Sair do Jogo"
        ]
        botoes = desenhar_modal(texto_opcoes, cor_texto=VERMELHO)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Clique do mouse → aciona ações
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for rect, opcao in botoes:
                    if rect.collidepoint(mouse_pos):
                        if opcao == "1":
                            reiniciar_jogo()
                            return
                        elif opcao == "2":
                            menu_principal()
                            reiniciar_jogo()
                            return
                        elif opcao == "3":
                            pygame.quit()
                            sys.exit()

            # Teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    reiniciar_jogo()
                    return
                elif event.key == pygame.K_2:
                    menu_principal()
                    reiniciar_jogo()
                    return
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()


# ===== CLASSE JOGADOR =====
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames_walking = []
        self.frames_jump_start = []
        self.frames_falling = []
        self.frames_slashing = []
        self.frames_dying = []
        self.estado = "idle"
        self.frame_atual = 0
        self.ataque = False
        self.morrendo = False
        self.carregar_animacoes()
        self.image = self.frames_walking[self.frame_atual]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (100, ALTURA - 30)
        self.vel_y = 0
        self.no_chao = False
        self.andando = False
        self.direcao = 1
        self.tempo_ultimo_frame = pygame.time.get_ticks()
        self.invencivel = False
        self.tempo_dano = 0

    def carregar_animacoes(self):
        pasta = os.path.join('esqueleto', 'walking')
        arquivos = sorted(os.listdir(pasta))
        for i in range(24):
            for arquivo in arquivos:
                if arquivo.startswith(f'0_Skeleton_Crusader_Walking_{i:03}'):
                    imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                    imagem = pygame.transform.scale(imagem, (130, 150))
                    self.frames_walking.append(imagem)
                    break

        pasta = os.path.join('esqueleto', 'jump_start')
        arquivos = sorted(os.listdir(pasta))
        for i in range(6):
            for arquivo in arquivos:
                if arquivo.startswith(f'0_Skeleton_Crusader_Jump Start_{i:03}'):
                    imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                    imagem = pygame.transform.scale(imagem, (130, 150))
                    self.frames_jump_start.append(imagem)
                    break

        pasta = os.path.join('esqueleto', 'falling')
        arquivos = sorted(os.listdir(pasta))
        for i in range(6):
            for arquivo in arquivos:
                if arquivo.startswith(f'0_Skeleton_Crusader_FallingDown_{i:03}'):
                    imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                    imagem = pygame.transform.scale(imagem, (130, 150))
                    self.frames_falling.append(imagem)
                    break

        pasta = os.path.join('esqueleto', 'slashing')
        arquivos = sorted(os.listdir(pasta))
        for arquivo in arquivos:
            if arquivo.startswith('0_Skeleton_Crusader_Slashing_'):
                imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                imagem = pygame.transform.scale(imagem, (130, 150))
                self.frames_slashing.append(imagem)

        pasta = os.path.join('esqueleto', 'dying')
        arquivos = sorted(os.listdir(pasta))
        for i in range(15):
            for arquivo in arquivos:
                if arquivo.startswith(f'0_Skeleton_Crusader_Dying_{i:03}'):
                    imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                    imagem = pygame.transform.scale(imagem, (130, 150))
                    self.frames_dying.append(imagem)
                    break

    def update(self):
        global vidas, game_over, avancar_fase
        agora = pygame.time.get_ticks()

        if self.morrendo and self.frames_dying:
            frames = self.frames_dying
            if agora - self.tempo_ultimo_frame > 120:
                self.tempo_ultimo_frame = agora
                self.frame_atual += 1
                if self.frame_atual >= len(frames):
                    self.frame_atual = len(frames) - 1
                    game_over = True  # Altere essa linha para garantir que o game_over só ocorra aqui
            frame = frames[self.frame_atual % len(frames)]
            if self.direcao == -1:
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame
            return


        keys = pygame.key.get_pressed()
        dx = 0
        self.andando = False

        if keys[pygame.K_LEFT]:
            dx = -5
            self.direcao = -1
            self.andando = True
        if keys[pygame.K_RIGHT]:
            dx = 5
            self.direcao = 1
            self.andando = True

        if self.andando and not som_caminhada.get_num_channels():
            som_caminhada.play(loops=-1)
        elif not self.andando:
            som_caminhada.stop()

        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LARGURA:
            if mostrar_aviso_avancar:
                avancar_fase = True
            else:
                self.rect.right = LARGURA

        self.vel_y += 0.5
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.y += self.vel_y

        self.no_chao = False
        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect) and self.vel_y > 0:
                self.rect.bottom = plataforma.rect.top + 30
                self.vel_y = 0
                self.no_chao = True
                if self.estado in ["jumping", "falling"]:
                    self.estado = "idle"

        if not self.no_chao and self.vel_y > 1:
            self.estado = "falling"

        frames = [self.frames_walking[0]] if self.frames_walking else []

        if self.estado == "jumping" and self.frames_jump_start:
            frames = self.frames_jump_start
            if agora - self.tempo_ultimo_frame > 80:
                self.tempo_ultimo_frame = agora
                self.frame_atual += 1
                if self.frame_atual >= len(frames):
                    self.estado = "falling"
                    self.frame_atual = 0

        elif self.estado == "falling" and self.frames_falling:
            frames = self.frames_falling
            if agora - self.tempo_ultimo_frame > 100:
                self.tempo_ultimo_frame = agora
                self.frame_atual = (self.frame_atual + 1) % len(frames)

        elif self.ataque and self.frames_slashing:
            frames = self.frames_slashing
            if agora - self.tempo_ultimo_frame > 80:
                self.tempo_ultimo_frame = agora
                self.frame_atual += 1
                if self.frame_atual >= len(frames):
                    self.ataque = False
                    self.frame_atual = 0

        elif self.andando and self.frames_walking:
            self.estado = "walking"
            frames = self.frames_walking
            if agora - self.tempo_ultimo_frame > 100:
                self.tempo_ultimo_frame = agora
                self.frame_atual = (self.frame_atual + 1) % len(frames)

        else:
            self.estado = "idle"
            frames = [self.frames_walking[0]] if self.frames_walking else []
            self.frame_atual = 0

        if frames:
            frame = frames[self.frame_atual % len(frames)]
            if self.direcao == -1:
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

        if self.invencivel and agora - self.tempo_dano > tempo_invencivel:
            self.invencivel = False

        if vidas <= 0 and not self.morrendo:
            self.morrendo = True
            self.frame_atual = 0
            self.tempo_ultimo_frame = pygame.time.get_ticks()

    def pular(self):
        if self.no_chao:
            self.vel_y = -10
            self.estado = "jumping"
            self.frame_atual = 0
            self.tempo_ultimo_frame = pygame.time.get_ticks()

    def tomar_dano(self, direcao):
        global vidas
        if not self.invencivel:
            vidas -= 1
            self.invencivel = True
            self.tempo_dano = pygame.time.get_ticks()
            for _ in range(10):
                self.rect.x += 10 * direcao

    def atacar(self):
        if not self.ataque:
            self.ataque = True
            self.frame_atual = 0
            self.tempo_ultimo_frame = pygame.time.get_ticks()
            som_ataque.play()

# ===== CLASSE PLATAFORMA =====
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill((8, 3, 23))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
# ===== CLASSE INIMIGO COMUM =====
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.frames = []
        self.frames_dying = []
        self.carregar_animacao_valkyrie()
        self.carregar_animacao_morte()
        self.frame_atual = 0
        self.image = self.frames[self.frame_atual]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, ALTURA - 30 + 20)
        self.vel = 2
        self.tempo_ultimo_frame = pygame.time.get_ticks()
        self.hitbox = pygame.Rect(0, 0, 40, 80)
        self.hitbox.center = self.rect.center
        self.ataques = 0
        self.foi_atacado = False
        self.morrendo = False
        self.direcao = 1
        self.vida_coracoes = []

    def carregar_animacao_valkyrie(self):
        pasta = os.path.join('valkyrie', 'walking')
        arquivos = sorted(os.listdir(pasta))
        for i in range(24):
            for arquivo in arquivos:
                if arquivo.startswith(f'0_Valkyrie_Walking_{i:03}'):
                    imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                    imagem = pygame.transform.scale(imagem, (115, 135))
                    self.frames.append(imagem)
                    break

    def carregar_animacao_morte(self):
        pasta = os.path.join('valkyrie', 'dying_valq')
        arquivos = sorted(os.listdir(pasta))
        for i in range(15):
            for arquivo in arquivos:
                if arquivo.startswith(f'0_Valkyrie_Dying_{i:03}'):
                    imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                    imagem = pygame.transform.scale(imagem, (115, 135))
                    self.frames_dying.append(imagem)
                    break

    def update(self):
        agora = pygame.time.get_ticks()

        if self.morrendo:
            if agora - self.tempo_ultimo_frame > 100:
                self.tempo_ultimo_frame = agora
                self.frame_atual += 1
                if self.frame_atual >= len(self.frames_dying):
                    self.kill()
                else:
                    frame = self.frames_dying[self.frame_atual]
                    if self.direcao == -1:
                        frame = pygame.transform.flip(frame, True, False)
                    self.image = frame
            return

        self.rect.x += self.vel

        if self.rect.left <= 0 or self.rect.right >= LARGURA:
            self.vel *= -1
            self.direcao *= -1

        if agora - self.tempo_ultimo_frame > 120:
            self.tempo_ultimo_frame = agora
            self.frame_atual = (self.frame_atual + 1) % len(self.frames)
            frame = self.frames[self.frame_atual]
            if self.direcao == -1:
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

        self.hitbox.center = self.rect.center

        if self.ataques >= 2 and not self.morrendo:
            self.morrendo = True
            self.frame_atual = 0
            self.tempo_ultimo_frame = pygame.time.get_ticks()

        if not jogador.ataque:
            self.foi_atacado = False

        self.vida_coracoes = []
        total_coracoes = 2 - self.ataques
        coracoes_largura_total = total_coracoes * heart_image_small.get_width()
        inicio_x = self.rect.centerx - (coracoes_largura_total // 2)

        for i in range(total_coracoes):
            coracao_x = inicio_x + i * heart_image_small.get_width()
            coracao_y = self.rect.top - heart_image_small.get_height() - 5
            self.vida_coracoes.append((coracao_x, coracao_y))

# ===== CLASSE INIMIGO BOSS =====
class InimigoBoss(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.frames = []
        self.frames_dying = []
        self.carregar_animacao_boss()
        self.carregar_animacao_morte()
        self.frame_atual = 0
        self.image = self.frames[self.frame_atual]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, ALTURA - 30 + 20)
        self.vel = 1.5
        self.tempo_ultimo_frame = pygame.time.get_ticks()
        self.hitbox = pygame.Rect(0, 0, 60, 100)
        self.hitbox.center = self.rect.center
        self.ataques = 0
        self.foi_atacado = False
        self.morrendo = False
        self.direcao = 1
        self.vida_coracoes = []

    def carregar_animacao_boss(self):
        pasta = os.path.join('Valkyrie_boss', 'walking')
        arquivos = sorted(os.listdir(pasta))
        for i in range(24):
            for arquivo in arquivos:
                if arquivo.startswith(f'0_Valkyrie_Walking_{i:03}'):
                    imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                    imagem = pygame.transform.scale(imagem, (130, 150))
                    self.frames.append(imagem)
                    break

    def carregar_animacao_morte(self):
        pasta = os.path.join('Valkyrie_boss', 'dying')
        arquivos = sorted(os.listdir(pasta))
        for i in range(15):
            for arquivo in arquivos:
                if arquivo.startswith(f'0_Valkyrie_Dying_{i:03}'):
                    imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                    imagem = pygame.transform.scale(imagem, (130, 150))
                    self.frames_dying.append(imagem)
                    break

    def update(self):
        agora = pygame.time.get_ticks()

        if self.morrendo:
            if agora - self.tempo_ultimo_frame > 100:
                self.tempo_ultimo_frame = agora
                self.frame_atual += 1
                if self.frame_atual >= len(self.frames_dying):
                    self.kill()
                else:
                    frame = self.frames_dying[self.frame_atual]
                    if self.direcao == -1:
                        frame = pygame.transform.flip(frame, True, False)
                    self.image = frame
            return

        # Atualizar a posição com base na direção
        self.rect.x += self.vel * self.direcao

        # Impedir que o boss ultrapasse a borda da tela
        if self.rect.left <= 0:  # Caso o boss ultrapasse a borda esquerda
            self.rect.left = 0
            self.direcao = 1  # Inverter a direção para a direita
        elif self.rect.right >= LARGURA:  # Caso o boss ultrapasse a borda direita
            self.rect.right = LARGURA
            self.direcao = -1  # Inverter a direção para a esquerda

        if agora - self.tempo_ultimo_frame > 120:
            self.tempo_ultimo_frame = agora
            self.frame_atual = (self.frame_atual + 1) % len(self.frames)
            frame = self.frames[self.frame_atual]
            if self.direcao == -1:
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

        self.hitbox.center = self.rect.center

        if self.ataques >= 5 and not self.morrendo:
            self.morrendo = True
            self.frame_atual = 0
            self.tempo_ultimo_frame = pygame.time.get_ticks()

        if not jogador.ataque:
            self.foi_atacado = False

        # Atualizando a vida do boss
        self.vida_coracoes = []
        total_coracoes = 5 - self.ataques
        coracoes_largura_total = total_coracoes * heart_image_small.get_width()
        inicio_x = self.rect.centerx - (coracoes_largura_total // 2)

        for i in range(total_coracoes):
            coracao_x = inicio_x + i * heart_image_small.get_width()
            coracao_y = self.rect.top - heart_image_small.get_height() - 5
            self.vida_coracoes.append((coracao_x, coracao_y))


# ===== TELA DE FIM DO JOGO =====
def tela_fim_jogo():
    while True:
        tela.fill(PRETO)  # Fundo preto

        # Texto de vitória
        fonte = pygame.font.Font(caminho_fonte, 30)
        texto = fonte.render('Parabéns! Você chegou ao fim do jogo!', True, VERDE)
        texto_rect = texto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
        tela.blit(texto, texto_rect)

        # Opção de sair do jogo
        fonte_opcao = pygame.font.Font(caminho_fonte, 30)
        opcao_texto = "1 - Sair do Jogo"
        opcao_render = fonte_opcao.render(opcao_texto, True, VERMELHO)
        opcao_rect = opcao_render.get_rect(center=(LARGURA // 2, ALTURA // 2 + 100))
        tela.blit(opcao_render, opcao_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Clique do mouse → aciona a saída
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if opcao_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

            # Teclado ainda funcionando
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pygame.quit()
                    sys.exit()





# ===== REINICIAR JOGO COMPLETO (Fase 1) =====
def reiniciar_jogo():
    global vidas, todos_sprites, grupo_inimigos, plataformas, jogador, fase, game_over
    vidas = 3
    fase = 1
    game_over = False  # Adiciona esta linha para garantir que o game over seja resetado
    carregar_fundo()
    tocar_som_ambiente()

    todos_sprites.empty()
    grupo_inimigos.empty()
    plataformas.clear()

    jogador = Jogador()
    todos_sprites.add(jogador)

    chao = Plataforma(0, ALTURA - 40, LARGURA, 40)
    plataformas.append(chao)
    todos_sprites.add(chao)

    inimigo = Inimigo(random.randint(100, LARGURA - 100))
    todos_sprites.add(inimigo)
    grupo_inimigos.add(inimigo)

    mostrar_historia_fase(fase)  # Exibe a história da fase



# ===== REINICIAR FASE ATUAL (mantém progresso) =====
def reiniciar_fase():
    global vidas, todos_sprites, grupo_inimigos, plataformas, jogador, fase
    if vidas < 3:
        vidas += 1

    carregar_fundo()
    tocar_som_ambiente()

    todos_sprites.empty()
    grupo_inimigos.empty()
    plataformas.clear()

    jogador = Jogador()
    todos_sprites.add(jogador)

    chao = Plataforma(0, ALTURA - 40, LARGURA, 40)
    plataformas.append(chao)
    todos_sprites.add(chao)

    if fase == 2:
        inimigo1 = Inimigo(random.randint(100, LARGURA - 300))
        inimigo2 = Inimigo(random.randint(300, LARGURA - 100))
        todos_sprites.add(inimigo1, inimigo2)
        grupo_inimigos.add(inimigo1, inimigo2)
    elif fase == 3:
        boss = InimigoBoss(LARGURA // 2)
        todos_sprites.add(boss)
        grupo_inimigos.add(boss)
    elif fase >= 4:
        tela_fim_jogo()

    mostrar_historia_fase(fase)  # Aqui também se assegura que a história da fase atual seja exibida corretamente


# ===== REINICIAR FASE ATUAL (mantem progresso) =====
def reiniciar_fase():
    global vidas, todos_sprites, grupo_inimigos, plataformas, jogador, fase
    if vidas < 3:
        vidas += 1

    carregar_fundo()
    tocar_som_ambiente()

    todos_sprites.empty()
    grupo_inimigos.empty()
    plataformas.clear()

    jogador = Jogador()
    todos_sprites.add(jogador)

    chao = Plataforma(0, ALTURA - 40, LARGURA, 40)
    plataformas.append(chao)
    todos_sprites.add(chao)

    if fase == 2:
        inimigo1 = Inimigo(random.randint(100, LARGURA - 300))
        inimigo2 = Inimigo(random.randint(300, LARGURA - 100))
        todos_sprites.add(inimigo1, inimigo2)
        grupo_inimigos.add(inimigo1, inimigo2)
    elif fase == 3:
        boss = InimigoBoss(LARGURA // 2)
        todos_sprites.add(boss)
        grupo_inimigos.add(boss)
    elif fase >= 4:
        tela_fim_jogo()

    mostrar_historia_fase(fase)

# ===== INICIALIZAÇÃO FINAL =====
vidas = 3
todos_sprites = pygame.sprite.Group()
grupo_inimigos = pygame.sprite.Group()
plataformas = []

menu_principal()
reiniciar_jogo()

jogando = True
game_over = False
# ===== LOOP PRINCIPAL DO JOGO =====

while jogando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jogando = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_pausa()
            if not game_over and not jogador.morrendo and event.key == pygame.K_SPACE:
                 jogador.pular()
            elif not game_over and not jogador.morrendo and event.key == pygame.K_a:
                 jogador.atacar()

    if not game_over:
        todos_sprites.update()

        for inimigo in grupo_inimigos:
            if jogador.rect.colliderect(inimigo.hitbox):
                if jogador.ataque and not inimigo.foi_atacado:
                    inimigo.ataques += 1
                    inimigo.foi_atacado = True
                elif not jogador.ataque and not inimigo.morrendo:
                    direcao = -1 if jogador.rect.centerx < inimigo.rect.centerx else 1
                    jogador.tomar_dano(direcao)
                break

        if not grupo_inimigos and not avancar_fase:
            mostrar_aviso_avancar = True

    # ===== DESENHAR NA TELA =====
    tela.blit(fundo, (0, 0))

    for plataforma in plataformas:
        tela.blit(plataforma.image, plataforma.rect)

    for sprite in todos_sprites:
        if not isinstance(sprite, Plataforma):
            tela.blit(sprite.image, sprite.rect)

    for inimigo in grupo_inimigos:
        if hasattr(inimigo, 'vida_coracoes'):
            for pos in inimigo.vida_coracoes:
                tela.blit(heart_image_small, pos)

    for i in range(vidas):
        tela.blit(heart_image, (10 + i * 45, 10))

    if mostrar_aviso_avancar:
        fonte = pygame.font.SysFont("Arial", 32)
        texto_avancar = fonte.render("", True, BRANCO)
        seta = fonte.render("→", True, BRANCO)
        tela.blit(texto_avancar, (LARGURA - 400, ALTURA - 100))
        tela.blit(seta, (LARGURA - 80, ALTURA - 110))

    if game_over:
        tela_game_over()

    pygame.display.flip()

    # ===== AVANÇAR PARA A PRÓXIMA FASE =====

    if avancar_fase:
        tela.fill(PRETO)  # Preenche a tela com a cor preta
        fonte = pygame.font.Font(caminho_fonte, 25)  # Usando a fonte personalizada
        texto_loading = fonte.render("Carregando...", True, BRANCO)

        # Centralizando o texto no meio da tela
        texto_rect = texto_loading.get_rect(center=(LARGURA // 2, ALTURA // 2))

        # Exibe o texto centralizado na tela
        tela.blit(texto_loading, texto_rect)

        pygame.display.flip()  # Atualiza a tela
        pygame.time.delay(2000)  # Aguarda 2 segundos

        fase += 1
        avancar_fase = False
        mostrar_aviso_avancar = False
        reiniciar_fase()  # Reinicia a fase

pygame.quit()
sys.exit()
