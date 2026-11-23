import socket
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.request import urlopen
from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)

# Configurações de E-mail (Substitua pelos dados reais para testes)
# Dica: Se usar o Gmail, utilize uma "Senha de App" (App Password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_REMETENTE = "ciberfisicatrabalho@gmail.com"
SENHA_REMETENTE = "wnws mosm jaca wrni"

# Credenciais de Login simples para o painel
USUARIO_ADMIN = "admin"
SENHA_ADMIN = "1234"

# Serviços que queremos monitorar
servicos = [
    {"nome": "Google", "tipo": "http", "endereco": "https://google.com"},
    {"nome": "DNS Google", "tipo": "dns", "endereco": "google.com"},
    {"nome": "Servidor DNS", "tipo": "tcp", "endereco": "8.8.8.8", "porta": 53}
]

resultados = {}
lock = threading.Lock()

def enviar_email(destinatario, assunto, corpo):
    """Função responsável por disparar o e-mail via SMTP."""
    if not destinatario:
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = destinatario
        msg['Subject'] = assunto
        
        msg.attach(MIMEText(corpo, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, SENHA_REMETENTE)
            servidor.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())
        print(f"[E-MAIL] Relatório enviado com sucesso para {destinatario}")
    except Exception as e:
        print(f"[ERRO E-MAIL] Falha ao enviar e-mail: {e}")

def verificar(servico):
    try:
        if servico["tipo"] == "http":
            urlopen(servico["endereco"], timeout=5)
        elif servico["tipo"] == "dns":
            socket.gethostbyname(servico["endereco"])
        elif servico["tipo"] == "tcp":
            conexao = socket.create_connection(
                (servico["endereco"], servico["porta"]), timeout=5
            )
            conexao.close()
        return "ONLINE"
    except Exception:
        return "OFFLINE"

def monitorar():
    while True:
        with lock:
            for servico in servicos:
                nome = servico["nome"]
                status = verificar(servico)
                resultados[nome] = status
                print(f"{nome}: {status}")

        time.sleep(30)

# Template HTML com o botão para envio sob demanda do relatório por e-mail
TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Monitor de Disponibilidade</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #333; }
        .online { color: green; font-weight: bold; }
        .offline { color: red; font-weight: bold; }
        .form-group { margin-bottom: 15px; }
        input[type="text"], input[type="password"], input[type="email"] { width: 100%%; padding: 8px; margin-top: 5px; box-sizing: border-box; }
        button { background-color: #007BFF; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 4px; }
        button:hover { background-color: #0056b3; }
        .logout { background-color: #dc3545; float: right; }
        .logout:hover { background-color: #c82333; }
        hr { margin: 20px 0; border: 0; border-top: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="container">
        {% if not session.get('logado') %}
            <h2>Login do Sistema</h2>
            {% with messages = get_flashed_messages() %}
              {% if messages %}
                <p style="color: red;">{{ messages[0] }}</p>
              {% endif %}
            {% endwith %}
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Usuário:</label>
                    <input type="text" name="usuario" required>
                </div>
                <div class="form-group">
                    <label>Senha:</label>
                    <input type="password" name="senha" required>
                </div>
                <button type="submit">Entrar</button>
            </form>
        {% else %}
            <form action="/logout" method="POST" style="display:inline;">
                <button type="submit" class="logout">Sair</button>
            </form>
            <h1>Monitor de Disponibilidade</h1>
            <hr>
            <h2>Status Atual dos Serviços</h2>
            <ul>
                {% for nome, status in resultados.items() %}
                    <li>{{ nome }}: <span class="{{ 'online' if status == 'ONLINE' else 'offline' }}">{{ status }}</span></li>
                {% endfor %}
            </ul>
            <hr>
            <h2>Enviar Relatório por E-mail</h2>
            <form method="POST" action="/enviar-relatorio">
                <div class="form-group">
                    <label>Digite o e-mail para receber o relatório:</label>
                    <input type="email" name="email_destino" placeholder="seu_email@dominio.com" required>
                </div>
                <button type="submit">Enviar Relatório Agora</button>
            </form>
            {% with messages = get_flashed_messages() %}
              {% if messages %}
                <p style="color: green; margin-top: 10px;">{{ messages[0] }}</p>
              {% endif %}
            {% endwith %}
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/")
def painel():
    return render_template_string(TEMPLATE_HTML, resultados=resultados)

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    if usuario == USUARIO_ADMIN and senha == SENHA_ADMIN:
        session['logado'] = True
        return redirect(url_for('painel'))
    else:
        flash("Usuário ou senha inválidos!")
        return redirect(url_for('painel'))

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('logado', None)
    return redirect(url_for('painel'))

@app.route("/enviar-relatorio", methods=["POST"])
def rota_enviar_relatorio():
    if not session.get('logado'):
        return redirect(url_for('painel'))
    
    email_destino = request.form.get("email_destino")
    
    # Monta o corpo do relatório com os resultados atuais em tempo real
    with lock:
        corpo_relatorio = "=== RELATÓRIO DE DISPONIBILIDADE DE SERVIÇOS ===\n\n"
        corpo_relatorio += f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for nome, status in resultados.items():
            corpo_relatorio += f"- {nome}: {status}\n"
        corpo_relatorio += "\n-----------------------------------------\nGerado automaticamente pelo Monitor de Sistemas."

    # Dispara em uma thread separada para não travar a página web
    threading.Thread(
        target=enviar_email, 
        args=(email_destino, "Relatório de Disponibilidade - Serviços", corpo_relatorio)
    ).start()
    
    flash(f"Relatório enviado com sucesso para {email_destino}!")
    return redirect(url_for('painel'))

if __name__ == "__main__":
    # Inicia a thread de monitoramento em segundo plano
    threading.Thread(target=monitorar, daemon=True).start()
    # Executa a aplicação web Flask
    app.run(host="0.0.0.0", port=5000, debug=True)