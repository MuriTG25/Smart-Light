import socket
import machine
from machine import Pin
import config

#---usuario/senha do wifi---#
ssid=config.SSID
senha= config.SENHA
#---os leds que irao ser conectados no wifi---#
Luz_sala=Pin(1, Pin.OUT)
Luz_cozinha=Pin(2, Pin.OUT)
Luz_banheiro=Pin(4, Pin.OUT)

#---funcao que conecta com  o wifi---#
def conectarComWifi(ssid, senha=None, timeout_seconds=30):
  import network, utime
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(ssid, senha)
  while wlan.isconnected() == False:
    print('Esperando conexão...')
    utime.sleep(1)
  if wlan.isconnected() == True:
    print('Conectado')
    ip = wlan.ifconfig()[0]
    print('Ip: ', ip)
    return ip

#---funcao que mostra a mensagem se a aluz esta ligada ou nao---#
def luzEstaLigada(led):
    if led.value==1:
        return "Desligar "
    else:
        return "Ligar "

#---cria a página web para ligar/desligar os leds---#
def paginaDaWeb(luz1,luz2,luz3):
    html=f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
</head>
<body>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <br/>
    <form action="./liga-desliga1">
        <input type="submit" style="width: 400px;max-width: 95%;margin-left: 10px;margin-right: 10px;" value="Luz 1" />
    </form>
    <br/>
    <form action="./liga-desliga2">
        <input type="submit" style="width: 400px;max-width: 95%;margin-left: 10px;margin-right: 10px;" value="Luz 2" />
    </form>
    <br/>
    <form action="./liga-desliga3">
        <input type="submit" style="width: 400px;max-width: 95%;margin-left: 10px;margin-right: 10px;" value="Luz 3" />
    </form>
</body>
</html>
            """
    return html

#---verifica os resultados que retornaram da web e emite a luz---#
def verificacaoDeLuzes(request,luz1,luz2,luz3):
    if request == '/liga-desliga1?':
        luz1.toggle()
        print("Liga luz 1")
    if request == '/liga-desliga2?':
        luz2.toggle()
        print("Liga luz 2")
    if request == '/liga-desliga3?':
        luz3.toggle()
        print("Liga luz 3")

#---faz a verificacao de conexão---#
def servidor(conexao):
    while True:
        client = conexao.accept()[0]
        requisicao = client.recv(1024)
        requisicao = str(requisicao)
        try:
            requisicao = requisicao.split()[1]
        except IndexError:
            pass
        print(requisicao)
#---verifica os resultados que retornaram da web e emite a luz---#
        verificacaoDeLuzes(requisicao,Luz_sala,Luz_cozinha,Luz_banheiro)
        html=paginaDaWeb(Luz_sala,Luz_cozinha,Luz_banheiro)
        client.send(html)
        client.close()

#---inicia o socket para abrir o site ---#
def abre_socket(ip):
    endereco= (ip,80)
    conexao= socket.socket()
    conexao.bind(endereco)
    conexao.listen(1)
    print(conexao)
    return(conexao)

#---primeiramente conecta com o wifi ---#
ip = conectarComWifi(ssid,senha)
try:
    # ---apenas ao ter o ip, que ele vai abrir o socket---#
    if ip is not None :
        #---abre o socket com os botoes para as luzes---#
        conexao=abre_socket(ip)
        #---abre o servidor---#
        servidor(conexao)
except KeyboardInterrupt:
    #---dando excecao, reseta o pico---#
    machine.reset()
        
