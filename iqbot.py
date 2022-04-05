from main import dados_export
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
from openpyxl import load_workbook
import sys


#definindo variaveis
OPERACAO = 1 if dados_export['OPERACAO'] == '1' else 2  # 1 - Digital\n  2 - Binaria
PAR = dados_export['PAR'].upper()
TENTATIVAS = int(dados_export['TENTATIVAS'])
MULTIPLICADOR = float(dados_export['multiplicador'])  # valor da multiplicacao
VALOR_ENTRADA = float(dados_export['valor_entrada'])  # valor entrada
valor_operacao = float(dados_export['valor_entrada']) #valor operacao
stop_loss = float(dados_export['stop_loss']) #limite de stop
STOP_GAIN = float(dados_export['stop_gain']) #limite de win
win = 0 #quantidade de operacoes vencedoras
loss = 0 #quantidade de operacoes perdedoras
lucro = 0 #lucro real
win_cons = 0 # contador vitorias consecutivas (para relatorio)
loss_cons = 0 # contador loss consecutivos (para relatorio)
maior_loss = 0  #maior numero de loss registrado (relatorio)
maior_win = 0 #maior numero de win registrado (relatorio)

#função para inverter a direção da operação
def muda_dir(dir):
    return 'call' if dir == 'put' else 'put'

#registra em relatorio xlsx as operacoes realizadas durante a execucao do bot,
#foi criada como extra para melhorar a analise das estrategias aplicadas
def encerramento(stop):
    wb = load_workbook(filename='relatorio.xlsx')
    ws = wb.active
    hoje = datetime.today()
    data = hoje.strftime('%d/%m/%Y')
    hora = hoje.strftime('%H:%M')
    op = win + loss
    ws.append([data, inicio, hora ,op, win, loss,maior_loss,maior_win,PAR.upper(), lucro, stop.upper()])

    print('total operações: ',op)
    print('maior loss: ',maior_loss)
    print('maior_win: ',maior_win)
    wb.save("relatorio.xlsx")
    sys.exit()

#realiza verificacao se os stops definidos foram atingidos
def stop(lucro, gain):
    if stop_loss <= 0:
        print('Stop Loss batido!')
        print('loss:', loss, 'ganhou:', win)
        encerramento('loss')

    if lucro >= float(abs(gain)):
        print('Stop Gain Batido!')
        print('loss:', loss, 'ganhou:', win)
        encerramento('win')

#realiza conexão com a plataforma
def conectar():
    BOT = IQ_Option(dados_export['user'], dados_export['password'])
    BOT.connect()
    print('ok')
    print(dados_export['TIPO_CONTA'])
    BOT.change_balance("REAL" if dados_export['TIPO_CONTA'].upper() == "REAL" else "PRACTICE")  # PRACTICE / REAL
    if BOT.check_connect():
        print(' Conectado com sucesso!')
    else:
        print(' Erro ao conectar')
        input('\n\n Aperte enter para sair')
        sys.exit()



print(dados_export)
conectar()