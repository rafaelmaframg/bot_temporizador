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
        try:
            self.OPERACAO = 1 if dados_export['OPERACAO'] == '1' else 2  # 1 - Digital\n  2 - Binaria
            self.PAR = dados_export['PAR'].upper()
            self.tentativas = int(dados_export['TENTATIVAS'])  #numero de tentativas
            self.MULTIPLICADOR = float(dados_export['multiplicador'])  # valor da multiplicacao
            self.VALOR_ENTRADA = float(dados_export['valor_entrada'])  # valor entrada
            self.valor_operacao = float(dados_export['valor_entrada']) #valor operacao
            self.stop_loss = float(dados_export['stop_loss']) #limite de stop
            self.STOP_GAIN = float(dados_export['stop_gain']) #limite de win
            self.TEMPORIZADOR = int(dados_export['temporizador'])*60 #recebe valor de tempo para aguardar a proxima
            # operacao em minutos
            self.TIMEFRAME = int(dados_export['timeframe'])
            self.win = 0 #quantidade de operacoes vencedoras
            self.loss = 0 #quantidade de operacoes perdedoras
            self.lucro = 0 #lucro real
            self.win_cons = 0 # contador vitorias consecutivas (para relatorio)
            self.loss_cons = 0 # contador loss consecutivos (para relatorio)
            self.maior_loss = 0  #maior numero de loss registrado (relatorio)
            self.maior_win = 0 #maior numero de win registrado (relatorio)
            print('\n\nDados Carregados com Sucesso!!\n')
        except:
            print('Erro ao importar os DADOS! certifique de que os dados inseridos estão corretos!')
            input('\n\n Aperte enter para sair')
            sys.exit()
        finally:
            # realiza conexão com a plataforma
            self.connect()
            print(f'Você esta operando em conta: {dados_export["TIPO_CONTA"]}\n')
            print('Valor atual da sua banca: R$', self.get_balance()) #issue #4 by: KairosGG

            #define o tipo de operação DEMO/REAL
            if dados_export['TIPO_CONTA'].upper() == "REAL":
                self.change_balance('REAL')
            else:
                self.change_balance('PRACTICE')

            if self.check_connect():
                print(' Conectado com sucesso!\n\n')
                self.operacao()
            else:
                print(' Erro ao conectar')
                input('\n\n Aperte enter para sair')
                sys.exit()

    #função para inverter a direção da operação sempre que acionada
    def muda_dir(self, dir):
        return 'call' if dir == 'put' else 'put'

    #realiza verificacao se os stops definidos foram atingidos
    def stop(self, lucro, gain):
        if self.stop_loss <= 0:
            print('Stop Loss batido!')
            print('loss:', self.loss, 'ganhou:', self.win)
            print('Valor atual da sua banca: R$', self.get_balance()) #issue #4 by: KairosGG
            self.encerramento('loss')

        if lucro >= float(abs(gain)):
            print('Stop Gain Batido!')
            print('loss:', self.loss, 'ganhou:', self.win)
            print('Valor atual da sua banca: R$', self.get_balance()) #issue #4 by: KairosGG
            self.encerramento('win')

    #analiza o ultimo candle antes da entrada para definir a direcao
    def analiza_vela(self):
        vela = self.get_candles(self.PAR, 60, 1, time.time())
        if vela[0]['open'] < vela[0]['close']:
            return 'call'
        elif vela[0]['open'] > vela[0]['close']:
            return 'put'
        else:
            print('DOJI')
            return False

    #função criada para indicar o tempo correto para entrada na vela de acordo com o timeframe especificado na
    # configuração as condicioais variam de 1 5 e 15 para que sejam captados os segundos finais davela para entrada
    def check_entrar(self, timeframe):

        if timeframe == 1:
            self.minutos = float(((datetime.now()).strftime('%S')))
            return True if self.minutos >= 58 else False

        elif timeframe == 5:
            self.minutos = float(((datetime.now()).strftime('%M.%S')[1:]))
            return True if (self.minutos >= 4.58 and self.minutos <= 4.59 or
                            self.minutos >= 9.58 and self.minutos <= 9.59) else False
        else:
            self.minutos = float(((datetime.now()).strftime('%M.%S')))
            return True if (self.minutos >= 14.58 and self.minutos <= 14.59 or
                            self.minutos >= 29.58 and self.minutos <= 29.59
                            or self.minutos >= 59.58 and self.minutos <= 59.59) else False

    #realiza a operaçã de entrada checkando o tempo correto para entrar e verificando a vela anterior como analize
    def operacao(self):
        while True:
            entrar = self.check_entrar(self.TIMEFRAME)
            print(f'Hora de entrar? {entrar} Minuto: {self.minutos}')
            if entrar:
                self.inicio = datetime.today().strftime("%H:%M") #definindo variavel para usar como registro do relatorio
                self.dir = self.analiza_vela() #define direção da operação [call, put ou False para doji]
                while self.dir:
                    print('\nIniciando operação! ', self.dir.upper())
                    #realiza compra da operação de acordo com o tipo da operacao (binaria ou digital)
                    status, id = self.buy_digital_spot(self.PAR, self.valor_operacao, self.dir, self.TIMEFRAME) \
                        if self.OPERACAO == 1 else self.buy(self.valor_operacao, self.PAR, self.dir, self.TIMEFRAME)

                   #realiza verificação se a compra foi feita com sucesso = TRUE, então inicia o processo para
                    if status:
                        while True:
                            #loop para verificação do resultado, a forma de checkar o win varia de acordo com a operação
                            try:
                                #verifica o win caso seja operação digital
                                if self.OPERACAO == 1:
                                    status, valor = self.check_win_digital_v2(id)
                                else:
                                    #realiza verificação caso operação seja binaria
                                    valor = self.check_win_v3(id)

                            except:
                                status = True
                                valor = 0
                            if status:
                                #valor recebe a variavel retornada da verificação apenas se a foi win
                                #caso contrario recebe o valor da operação (entrada)
                                valor = valor if valor > 0 else float('-' + str(abs(self.valor_operacao)))
                                self.lucro += round(valor, 2)
                                print('Resultado operação: ', end='')
                                print('WIN ||' if valor > 0 else 'LOSS ||', f'{round(valor, 2)} || {round(self.lucro, 2)}')

                                #caso resultado seja loss realiza estrategia definida mudando o dir
                                if valor < 0:
                                    self.win_cons = 0
                                    self.loss_cons += 1
                                    self.loss += 1
                                    print('Win: ', self.win, 'Loss: ', self.loss)
                                    if self.tentativas == 0:
                                        self.dir = self.muda_dir(self.dir)
                                        self.tentativas = int(dados_export['TENTATIVAS'])
                                        if self.TEMPORIZADOR > 0:
                                            print(f'Aguardando {self.TEMPORIZADOR / 60} MINUTOS')
                                            time.sleep(self.TEMPORIZADOR)
                                            self.dir = False

                                    else:
                                        self.tentativas -= 1
                                    self.valor_operacao *= self.MULTIPLICADOR
                                    self.stop_loss += round(valor, 2)


                                else:
                                    self.valor_operacao = self.VALOR_ENTRADA
                                    self.win_cons += 1
                                    self.loss_cons = 0
                                    self.win += 1
                                    print('Win: ', self.win, 'Loss: ', self.loss)
                                if self.win_cons > self.maior_win:
                                    self.maior_win = self.win_cons
                                elif self.loss_cons > self.maior_loss:
                                    self.maior_loss = self.loss_cons
                                self.stop(self.lucro, self.STOP_GAIN)
                                break

                    else:
                        print('\nERRO AO REALIZAR OPERAÇÃO\n\n')

            time.sleep(0.5)

    #registra em relatorio xlsx as operacoes realizadas durante a execucao do bot,
    #foi criada como extra para melhorar a analise das estrategias aplicadas
    def encerramento(self, stop):
        wb = load_workbook(filename='relatorio.xlsx')
        ws = wb.active
        hoje = datetime.today()
        ws.append([datetime.today().strftime('%d/%m/%Y'), self.inicio, (hoje.strftime('%H:%M')), (self.win + self.loss),
                   self.win, self.loss,self.maior_loss,self.maior_win,self.PAR.upper(),
                   self.lucro, stop.upper()])

        print('Total Operações: ', (self.win + self.loss))
        print('Maior seq. Loss: ',self.maior_loss)
        print('Maior seq.Win: ',self.maior_win)
        wb.save("relatorio.xlsx")
        input('\n\n Aperte enter para sair')
        sys.exit()

bot = BotIqoption(dados_export['user'], dados_export['password'])
