import cryptocode

dados = {}
legenda = """
#LEGENDA 
#===================
#OPERACAO =  1 - (Digital)  2 - (Binaria)
#TIPO_CONTA =  DEMO - REAL
#PAR = PARIDADE para operar ex: EURUSD-OTC
#TENTATIVAS = Numero Tentativas
#multiplicador = #valor da multiplicacao
#valor_entrada = #valor entrada
#stop_loss = #valor stop loss
#stop_gain = #valor stop gain
#temporizador = #timer para aguardar nova operacao
#timeframe = #1/5/15 Timeframe para operações
#====================="""

with open('config.txt','r') as cf:
    fields = cf.readlines()
    for line in fields:
        if line.startswith('(') or line.startswith('\n') or line.startswith('LEGENDA') or line.startswith('#'):
            continue
        if line.startswith('password'):
            passe = (line[10:].strip())
            if not cryptocode.decrypt(passe, 'mafra'):
                pass_decp = passe
                pass_enc = cryptocode.encrypt(passe,'mafra')
            else:
                pass_decp = cryptocode.decrypt(passe, 'mafra')
                pass_enc = passe
            dados[line[:line.index('=')].strip()] = pass_decp.strip()
            continue
        dados[line[:line.index('=')].strip()] = line[line.index('=')+1:].strip()

try:
    dados['multiplicador'] = dados['multiplicador'].replace(',','.')
    dados['valor_entrada'] = dados['valor_entrada'].replace(',', '.')
except:
    pass

dados_export = dados.copy()
dados['password'] = pass_enc
with open('config.txt','w') as wr:
    for k,v in dados.items():
        dado = k +' = '+v+'\n'
        wr.write(dado)
    wr.write(legenda)


