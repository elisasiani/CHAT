#Flask-SocketIO: Essa extensão permite a comunicação bidirecional em tempo real, essencial para um chat.
#ele é um framework, o que exige que siga algumas regras para utiliza-lo, coisas já pré-definidas.
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import random
from string import ascii_uppercase

app = Flask(__name__) #instância um objeto de flask
app.config["SECRET_KEY"] = "123456" #a chave aqui serve para proteger a aplicação
socket = SocketIO(app) #habilita a comunicação em tempo real da biblioteca, passando o app como valor

rooms = {} #crie um tipo de dicionário "temporário" 
#para armazenar as chaves das salas

#gera códigos aleatório para salas cada vez que ela é instanciada
def generate_unique_code(Length):
    while True:
        code = ""
        for _ in range(Length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    return code

#1ª página do site
#route -> qual link vai ficar a página, qual o caminho que vem depois do domínio = chat.com/caminho
#def função -> o que você quer exibir naquela página
#return render_template -> "nomedaaba.html"

#vai abrir o caminho com a barra, que dá na página principal do site = chat.com, nesse caso vai abrir a homepage direto
#essa linha de cima é um decorator, que é uma linha sempre antes da definição de uma função, que vai atribuir uma nova funcionalidade para alinha de código que vem logo abaixo dela
@app.route("/", methods=["POST", "GET"])
def home():
    session.clear() #exclui tudo o que estiver dentro da sessão quando voltarem para ela
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Por favor insira um nome!", code=code, name=name) #a parte depois do erro devolve a eles tudo o que eles digitaram anteriormente, sem isso ela é apagada
        
        if join != False and not code:
            return render_template("home.html", error="Por favor insira um code para sala!", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []} #sempre que criarmos uma sala, ela vai ser adcionado ao dicionário de room
        elif code not in room:
            return render_template("home.html", error="Essa sala não existe!", code=code, name=name)
        
        session["name"] = name
        session["room"] = room # ao invés de usarmos autenticação em banco de dados, criamos uma sessão, que armazena os dados temporariamente
        return redirect(url_for("chat"))
        

    return render_template("home.html")


@app.route("/chat.html")
def chat():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    
    return render_template("chat.html", code=room, messages=rooms[room]["messages"])
    
@socket.on("message")
def message (data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }

    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get("name")} disse: {data['data']}")

@socket.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return

    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "Você entrou na sala!"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socket.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room] #caso todo mundo saia da sala, ela vai ser apagada

    send({"name": name, "message": "deixou a sala"}, to=room)
    print(f"{name} has left the room {room}")
#caso tenha apenas uma pessoa na sala, e vc recarregue a página a mesma vai te 
#tirar da sala e levar de volta a homepage, o que não acontece se tiver mais pessoas na sala
#colocar site no ar 

if __name__ == '__main__': #significa que só vai executar se a de cima estiver em execução
    socket.run(app, debug=True) #isso faz com que o site debug sem precisar ficar fazendo isso manualmente


