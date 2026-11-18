# Monitor de Disponibilidade de Serviços (Projeto 6)

**Disciplina:** PSI129A - Conectividade em Sistemas Ciberfísicos  
**Curso:** Bacharelado em Ciência da Computação — Escola Politécnica / PUCPR (Curitiba)  
**Turma:** CCCO - 2U - N - 2026/02  
**Professor:** Prof. MSc. Luis Gonzaga de Paulo  

---

## 1. Identificação da Equipe

* **Integrante 1:** [Nome Completo] — Matrícula: [00000000]
* **Integrante 2:** [Nome Completo] — Matrícula: [00000000]
* **Integrante 3:** [Nome Completo] — Matrícula: [00000000]
* **Integrante 4:** [Nome Completo] — Matrícula: [00000000]


---

## 2. Objetivo e Cenário de Uso Real

### Problema Atendido
Pequenas empresas e equipes de suporte de TI frequentemente enfrentam dificuldades para identificar rapidamente quando um serviço crítico (como o site institucional, servidor de resolução de nomes ou porta de banco de dados/aplicação) sai do ar, descobrindo a falha apenas quando clientes ou colaboradores reclamam.

### Solução Proposta
Este projeto implementa um **Monitor de Disponibilidade de Serviços** leve e automatizado. A aplicação realiza verificações periódicas em segundo plano na pilha TCP/IP, exibe o estado em tempo real (`ONLINE` ou `OFFLINE`) em um painel web protegido por autenticação e permite o envio sob demanda de relatórios de status via e-mail (protocolo SMTP) para os responsáveis técnicos.

---

## 3. Arquitetura, Infraestrutura e Plano de Rede

A solução foi estruturada para operar em ambiente Linux virtualizado/conteinerizado com comunicação via rede IP entre múltiplos nós, atendendo aos requisitos de infraestrutura distribuída e diagnóstico de rede.

### Plano de Endereçamento e Portas

| Nó / Componente | Sistema Operacional / Imagem | Endereço IP (Exemplo Rede Docker/VM) | Máscara / Gateway | Portas e Protocolos | Função |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nó 1: Servidor de Monitoramento** | Ubuntu Linux / Python 3.11 | `172.20.0.10` | `255.255.0.0` / `172.20.0.1` | `5000/TCP` (HTTP) | Executa o script Python/Flask, threads de checagem e painel web. |
| **Nó 2: Alvo Interno / Serviço Simulado** | Alpine / Nginx ou Serviço TCP | `172.20.0.20` | `255.255.0.0` / `172.20.0.1` | `80/TCP` (HTTP) | Serviço local utilizado para simular quedas controladas durante os testes. |
| **Alvos Externos (Internet)** | Serviços Públicos (Google / DNS) | `8.8.8.8` / `google.com` | Roteamento Externo | `443/TCP` (HTTPS), `53/UDP-TCP` (DNS) | Validação de conectividade externa e resolução de nomes. |
| **Servidor de E-mail (SMTP)** | Gmail SMTP (`smtp.gmail.com`) | Dinâmico (via DNS) | Roteamento Externo | `587/TCP` (SMTP + STARTTLS) | Envio autenticado dos relatórios de disponibilidade. |

---

## 4. Bibliotecas Python e Justificativa Técnica

| Biblioteca | Tipo | Função e Justificativa de Uso |
| :--- | :--- | :--- |
| `socket` | Nativa (Standard Library) | Utilizada para testar conexões diretas na camada de transporte (`create_connection` via TCP na porta 53) e realizar resolução de nomes (`gethostbyname` via DNS). |
| `urllib.request` | Nativa (Standard Library) | Empregada (`urlopen`) para validar a disponibilidade de aplicações web na camada de aplicação (HTTP/HTTPS) com controle de `timeout`. |
| `threading` | Nativa (Standard Library) | Garante a concorrência da aplicação: executa o loop contínuo de monitoramento em uma *daemon thread* em paralelo ao servidor web, além de disparar o envio de e-mails de forma assíncrona sem travar a interface do usuário. Também utiliza `threading.Lock()` para evitar condições de corrida (*race conditions*) na leitura/escrita dos resultados. |
| `smtplib` e `email.mime` | Nativas (Standard Library) | Implementam o cliente de protocolo SMTP com criptografia TLS (`starttls()`) e formatação padrão MIME para envio de relatórios por e-mail. |
| `flask` | Externa (Framework Web) | Fornece o servidor HTTP, gerenciamento de rotas (`/`, `/login`, `/logout`, `/enviar-relatorio`), renderização dinâmica da interface e controle de sessão (`session`) para autenticação. |

---

## 5. Segurança Básica e Robustez

* **Autenticação Simples:** O painel web restringe o acesso às informações de monitoramento e ao disparo de relatórios por meio de tela de login protegida por sessão criptografada (`app.secret_key`).
* **Tratamento de Exceções e Timeouts:** Todas as requisições de rede (HTTP, DNS, TCP e SMTP) possuem parâmetros explícitos de `timeout` (5 segundos) e blocos `try/except`, impedindo que a indisponibilidade de um alvo trave a thread de monitoramento.
* **Comunicação Segura (TLS):** O envio de relatórios via SMTP utiliza `STARTTLS` na porta `587` e autenticação via Senha de Aplicativo.

---

## 6. Estrutura do Repositório

```text
├── app.py                  # Código-fonte principal (Flask + Monitoramento + SMTP)
├── requirements.txt        # Dependências externas do projeto (Flask)
├── Dockerfile              # Receita para construção da imagem do contêiner Python
├── docker-compose.yml      # Orquestração dos nós de rede (Monitor + Serviços alvo)
└── README.md               # Documentação técnica e instruções de reprodutibilidade

```

---

## 7. Como Instalar e Executar (Reprodutibilidade)

### Pré-requisitos

* Python 3.10 ou superior instalado (ou Docker / Docker Compose).
* Conta de e-mail com acesso SMTP habilitado (para Gmail, gerar uma **Senha de App** nas configurações de segurança da Conta Google).

### Passo 1: Clonar o repositório

```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DA_PASTA]

```

### Passo 2: Configurar as variáveis no código (`app.py`)

Edite as constantes no início do arquivo `app.py` com suas credenciais de envio e acesso:

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_REMETENTE = "seu_email@gmail.com"
SENHA_REMETENTE = "sua_senha_de_app_de_16_digitos"

USUARIO_ADMIN = "admin"
SENHA_ADMIN = "1234"

```

### Passo 3: Execução via Python Local (ou VM Linux)

```bash
# Instalar dependências
pip install flask

# Iniciar a aplicação
python3 app.py

```

### Passo 4: Execução via Docker Compose (Ambiente Multi-Nó)

```bash
docker-compose up --build -d

```

### Passo 5: Acessar o Painel

Abra o navegador e acesse `http://localhost:5000` (ou o IP da VM/Contêiner na porta `5000`).

Faça login com usuário `admin` e senha `1234`, visualize o status dos serviços e informe um e-mail válido para testar o envio do relatório.

---

## 8. Ferramentas de Diagnóstico e Monitoramento Utilizadas (Linux)

Para validação da infraestrutura e coleta de evidências do projeto, foram utilizados os seguintes comandos no ambiente Linux:

* `ip addr` e `ip route`: Verificação das interfaces de rede e rotas entre os nós.
* `ss -tulnp`: Confirmação de que o servidor Flask está escutando na porta `5000/TCP`.
* `dig google.com`: Validação manual da resolução DNS testada pelo script.
* `tcpdump` / `Wireshark`: Captura de pacotes TCP (porta 53 e porta 587) para evidenciar o handshake TCP e a troca de mensagens SMTP.
* `htop` / `ps -eLf`: Monitoramento do consumo de memória e das threads ativas do processo Python.

---

## 9. Declaração de Uso de Inteligência Artificial Generativa

Conforme a Resolução nº 274/2024 CONSUN da PUCPR:

> "Durante a preparação deste projeto e sua documentação, os autores usaram o IA generativa para apoio em pesquisa eidentificação de erros no projeto, comentar o codigo fonte e para formatar e corrigir este documento. Após usar essa ferramenta, os autores revisaram, testaram e editaram o conteúdo conforme necessário e assumem total responsabilidade pelo conteúdo."

```

```