from main import dados_export
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import time
import sys

def conectar():
    BOT = IQ_Option(dados_export['user'], dados_export['password'])
    BOT.connect()
    BOT.change_balance('REAL' if dados_export['TIPO_MHI'].upper() == 'REAL' else 'PRACTICE')  # PRACTICE / REAL

def configuracoes():
    OPERACAO = 1 if dados_export['OPERACAO'] == '1' else 2  # 1 - Digital\n  2 - Binaria
    PAR = dados_export['PAR'].upper()
    tentativas = int(dados_export['TENTATIVAS'])
    multiplicador = float(dados_export['multiplicador'])  # valor da multiplicacao
    valor_entrada = float(dados_export['valor_entrada'])  # valor entrada
    valor_operacao = float(dados_export['valor_entrada'])
    stop_loss = float(dados_export['stop_loss'])
    stop_gain = float(dados_export['stop_gain'])
    win = 0
    loss = 0
    lucro = 0
    win_cons = 0
    loss_cons = 0
    maior_loss = 0
    maior_win = 0


print(dados_export)