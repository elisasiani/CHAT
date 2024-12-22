import socket #provê comunicação entre duas portas, entre servidor/cliente dentro da própria rede ou máquina

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #serve para a comunicação STREAM entre o cliente e o servidor para utilizar o protocolo TCP/IP
servidor.bind(('localhost', 8888))

servidor.listen() #vai ficar ouvindo as conexões que estão acontecendo em volta, abre e começa a conversar com o cliente e servidor 
cliente, end = servidor.accept() #aceitar a conexão 

terminado = False

while not terminado:
    msg = cliente.recv(1024).decode('utf-8') #bits da mensagem
    if msg == 'tt': #se alguém digitar tt a conversa encerra 
        terminado = True
    else: #se não, imprime a mensagem
        print(msg)
    cliente.send(input('Mensagem: ').encode('utf-8')) 

cliente.close()
servidor.close()