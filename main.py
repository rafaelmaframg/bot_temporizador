import cryptocode

dados = {}
legenda = """

#LEGENDA 
#===================
#OPERACAO =  1 - (Digital)  2 - (Binaria)
#TIPO_MHI =  DEMO - REAL
#PAR = PARIDADE para operar ex: EURUSD-OTC
#dir = CVC ou VCV
#multiplicador = #valor da multiplicacao
#valor_entrada = #valor entrada
#stop_loss = #valor stop loss
#stop_gain = #valor stop gain
#====================="""

with open('config.txt','r') as cf:
    fields = cf.readlines()
    for i in fields:
        if i.startswith('(') or i.startswith('\n') or i.startswith('LEGENDA') or i.startswith('#'):
            continue
        if i.startswith('password'):
            passe = (i[10:].strip())
            if not cryptocode.decrypt(passe, 'mafra'):
                pass_decp = passe
                pass_enc = cryptocode.encrypt(passe,'mafra')
            else:
                pass_decp = cryptocode.decrypt(passe, 'mafra')
                pass_enc = passe
            dados[i[:i.index('=')].strip()] = pass_decp.strip()
            continue
        dados[i[:i.index('=')].strip()] = i[i.index('=')+1:].strip()
dados_export = dados.copy()
dados['password'] = pass_enc
with open('config.txt','w') as wr:
    for k,v in dados.items():
        dado = k +' = '+v+'\n'
        wr.write(dado)
    wr.write(legenda)


