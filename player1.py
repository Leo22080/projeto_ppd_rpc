import pygame
import Pyro4
from gekitai import *

# Inicializando módulos de Pygame
pygame.init()

player_1 = Player()

ns = Pyro4.locateNS() # procura o servidor de nomes

# Criando uma janela
janela = pygame.display.set_mode((LARGURAJANELA, ALTURAJANELA))
pygame.display.set_caption('Gekitai - Player 1')


#threading
import threading

def create_thread(target):
    thread = threading.Thread(target=target)
    thread.daemon = True 
    thread.start()


def iniciando_player():
    ''' cria o Daemon que é a parte do Pyro que escuta as chamadas de método remoto, as despacha
     para os objetos reais apropriados e retorna os resultados para o chamador.'''

    daemon = Pyro4.Daemon()
    uri = daemon.register(player_1) # registre a classe Player como objeto Pyro
    ns.register("gekitai.player_1", uri) # registrar o objeto com um nome no servidor de nomes

    print("Pronto.")
    daemon.requestLoop() # iniciar o loop de eventos do servidor para aguardar
    #esperando 


create_thread(iniciando_player)

player_1.turn = False
player_1.connection_established = False

try:
    uri = ns.lookup('gekitai.player_2')
    player_2 = Pyro4.Proxy(uri) #
    player_1.connection_established = True
    player_2.turn = True
except Pyro4.errors.NamingError as error:
    pass

deve_continuar = True
fimdeJogo = False

# Loop do jogo
while deve_continuar:

    # Checando eventos
    for evento in pygame.event.get():
        # Se for um evento QUIT
        if evento.type == pygame.QUIT:
            deve_continuar = False

        # quando o botao esquerdo do mouse é pressionado
        if evento.type == pygame.MOUSEBUTTONDOWN and player_1.connection_established:
            if pygame.mouse.get_pressed()[0]:
                if player_1.turn and not fimdeJogo and not player_1.chatOn:
                    rect = tabuleiro.get_rect().move(TABULEIROORIGEM)
                    if rect.collidepoint(pygame.mouse.get_pos()):

                        x, y = getCoordenadas(evento.pos[0], evento.pos[1])
                        if not player_1.grade.matrizTabuleiro[y][x]:

                            player_1.jogar('1', (x, y))
                            player_1.turn = False

                            player_2.jogar('1', (x, y))
                            player_2.turn = True
                                                        
        if evento.type == pygame.KEYDOWN and player_1.connection_established:
            if evento.key == pygame.K_DELETE:
                deve_continuar = False
            
            if evento.key == pygame.K_ESCAPE and fimdeJogo:
                player_1.iniciarJogo()
                player_2.iniciarJogo()
                fimdeJogo = False
                
            if evento.key == pygame.K_F12:
                player_1.chatOn = not player_1.chatOn
                player_2.chatOn = not player_2.chatOn

            if player_1.chatOn:
                chat = player_1.chat
                if evento.key == pygame.K_BACKSPACE:
                    chat.mensagem = chat.mensagem[:-1]
                elif evento.key == pygame.K_RETURN and not chat.mensagem == '':
                    try:
                        chat.enviar(chat.mensagem, 'esq')
                        player_2.enviarMsg(chat.mensagem, 'dir')
                        chat.limpar()
                    except:
                        pass
                else:
                    if not evento.key == pygame.K_ESCAPE or not evento.key == pygame.K_DELETE:
                        chat.mensagem += evento.unicode

    # Preenchendo o fundo da janela com uma cor
    janela.fill((192, 192, 192))

    # preenchendo o fundo de janela com a sua imagem    
    janela.blit(titulo, ((LARGURAJANELA - LARGURATITULO) / 2, 0))
    janela.blit(tabuleiro, (TABULEIROORIGEM))
    menu(janela)    

    for peca in pecasJogador1:
        janela.blit(peca.imagem, peca.pos)
        peca.atualizar()
    for peca in pecasJogador2:
        janela.blit(peca.imagem, peca.pos)
        peca.atualizar()

    fimdeJogo = player_1.verificarJogada(janela)

    if player_1.chatOn:
        player_1.chat.drawChat(janela)

    if not player_1.connection_established:
        try:
            uri = ns.lookup('gekitai.player_2')
            player_2 = Pyro4.Proxy(uri)
            player_1.connection_established = True
        except Pyro4.errors.NamingError:
            pass
        


    # mostrando na tela tudo o que foi desenhado
    pygame.display.update()

# Encerrando módulos de Pygame
try:
    player_2.turn = False
    player_2.iniciarJogo()
    player_2.chatOn = False
    player_2.connection_established = False
except:
    pass
ns.remove('gekitai.player_1') #apaga a referência do objeto do servidor de nomes
pygame.quit()
