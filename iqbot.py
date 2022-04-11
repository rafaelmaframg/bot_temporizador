from main import dados_export
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import time
from openpyxl import load_workbook
import sys

class BotIqoption(IQ_Option):
    def __init__(self, email, password):
        #definindo variaveis
        super().__init__(email, password)
        self.OPERACAO = 1 if dados_export['OPERACAO'] == '1' else 2  # 1 - Digital\n  2 - Binaria
        self.PAR = dados_export['PAR'].upper()
        self.TENTATIVAS = int(dados_export['TENTATIVAS'])
        self.MULTIPLICADOR = float(dados_export['multiplicador'])  # valor da multiplicacao
        self.VALOR_ENTRADA = float(dados_export['valor_entrada'])  # valor entrada
        self.valor_operacao = float(dados_export['valor_entrada']) #valor operacao
        self.stop_loss = float(dados_export['stop_loss']) #limite de stop
        self.STOP_GAIN = float(dados_export['stop_gain']) #limite de win
        self.win = 0 #quantidade de operacoes vencedoras
        self.loss = 0 #quantidade de operacoes perdedoras
        self.lucro = 0 #lucro real
        self.win_cons = 0 # contador vitorias consecutivas (para relatorio)
        self.loss_cons = 0 # contador loss consecutivos (para relatorio)
        self.maior_loss = 0  #maior numero de loss registrado (relatorio)
        self.maior_win = 0 #maior numero de win registrado (relatorio)
        self.conectar()

    #função para inverter a direção da operação
    def muda_dir(self, dir):
        return 'call' if dir == 'put' else 'put'

    #registra em relatorio xlsx as operacoes realizadas durante a execucao do bot,
    #foi criada como extra para melhorar a analise das estrategias aplicadas
    def encerramento(self, stop):
        wb = load_workbook(filename='relatorio.xlsx')
        ws = wb.active
        hoje = datetime.today()
        data = hoje.strftime('%d/%m/%Y')
        hora = hoje.strftime('%H:%M')
        op = self.win + self.loss
        ws.append([data, self.inicio, hora ,op, self.win, self.loss,self.maior_loss,self.maior_win,self.PAR.upper(), self.lucro, stop.upper()])

        print('total operações: ',op)
        print('maior loss: ',self.maior_loss)
        print('maior_win: ',self.maior_win)
        wb.save("relatorio.xlsx")
        sys.exit()

    #realiza verificacao se os stops definidos foram atingidos
    def stop(self, lucro, gain):
        if self.stop_loss <= 0:
            print('Stop Loss batido!')
            print('loss:', self.loss, 'ganhou:', self.win)
            self.encerramento('loss')

        if lucro >= float(abs(gain)):
            print('Stop Gain Batido!')
            print('loss:', self.loss, 'ganhou:', self.win)
            self.encerramento('win')

    #realiza conexão com a plataforma
    def conectar(self):
        self.connect()
        print(dados_export['TIPO_CONTA'])
        self.change_balance("REAL" if dados_export['TIPO_CONTA'].upper() == "REAL" else "PRACTICE")  # PRACTICE / REAL
        if self.check_connect():
            print(' Conectado com sucesso!')
            self.operacao()
        else:
            print(' Erro ao conectar')
            input('\n\n Aperte enter para sair')
            sys.exit()


    def analiza_vela(self):
        vela = self.get_candles(self.PAR, 60, 1, time.time())
        if vela[0]['open'] < vela[0]['close']:
            return 'call'
        elif vela[0]['open'] > vela[0]['close']:
            return 'putt'
        else:
            return False

    def operacao(self):
        self.inicio = datetime.today().strftime("%H:%M") #definindo variavel global para usar como registro do relatorio
        while True:
            minutos = float(((datetime.now()).strftime('%S')))
            entrar = True if minutos >= 58 and minutos <= 59 else False
            print('Hora de entrar?', entrar, '/ Minutos:', minutos)
            if entrar:
                self.inicio = datetime.today().strftime("%H:%M")
                self.dir = self.analiza_vela()
                while self.dir:
                    print('\n\nIniciando operação!', self.dir)
                    status, id = self.buy_digital_spot(self.PAR, self.valor_operacao, self.dir, 1) if self.OPERACAO == 1 else self.buy(
                        self.valor_operacao, self.PAR, self.dir, 1)
                    if status:
                        while True:
                            try:
                                status, valor = self.check_win_digital_v2(id) if self.OPERACAO == 1 else self.check_win_v3(id)

                            except:
                                status = True
                                valor = 0
                            if status:
                                valor = valor if valor > 0 else float('-' + str(abs(self.valor_operacao)))
                                self.lucro += round(valor, 2)
                                print('Resultado operação: ', end='')
                                print('WIN /' if valor > 0 else 'LOSS /', round(valor, 2), '/', round(self.lucro, 2))
                                if valor < 0:
                                    self.win_cons = 0
                                    self.loss_cons += 1
                                    self.dir = self.muda_dir(self.dir)
                                    self.valor_operacao *= self.MULTIPLICADOR
                                    self.stop_loss += round(valor, 2)
                                    self.loss += 1
                                    print('win: ', self.win, 'loss: ', self.loss)

                                else:
                                    self.valor_operacao = self.VALOR_ENTRADA
                                    self.dir = self.dir
                                    self.win_cons += 1
                                    self.loss_cons = 0
                                    self.win += 1
                                    print('win: ', self.win, 'loss: ', self.loss)
                                if self.win_cons > self.maior_win:
                                    self.maior_win = self.win_cons
                                elif self.loss_cons > self.maior_loss:
                                    self.maior_loss = self.loss_cons
                                self.stop(self.lucro, self.STOP_GAIN)
                                break

                    else:
                        print('\nERRO AO REALIZAR OPERAÇÃO\n\n')

            time.sleep(0.5)

print(dados_export)
bot = BotIqoption(dados_export['user'], dados_export['password'])
