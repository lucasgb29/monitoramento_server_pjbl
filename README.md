# Monitor de Disponibilidade de Serviços (Projeto 6)

**Disciplina:** PSI129A - Conectividade em Sistemas Ciberfísicos  
**Curso:** Bacharelado em Ciência da Computação — Escola Politécnica / PUCPR (Curitiba)  
**Turma:** CCCO - 2U - N - 2026/02  
**Professor:** Prof. MSc. Luis Gonzaga de Paulo  

---

## 1. Identificação da Equipe

- **Integrante 1:** [Nome Completo] — Matrícula: [00000000]
- **Integrante 2:** [Nome Completo] — Matrícula: [00000000]
- **Integrante 3:** [Nome Completo] — Matrícula: [00000000]
- **Integrante 4:** [Nome Completo] — Matrícula: [00000000]

---

## 2. Objetivo e Cenário de Uso Real

### Problema Atendido
Pequenas empresas e equipes de suporte de TI frequentemente enfrentam dificuldades para identificar rapidamente quando um serviço crítico (como o site institucional, servidor de resolução de nomes ou porta de serviço/aplicação) sai do ar, descobrindo a falha apenas quando clientes ou colaboradores relatam o problema.

### Solução Proposta
Este projeto implementa um **Monitor de Disponibilidade de Serviços** leve e automatizado. A aplicação realiza verificações periódicas em segundo plano na pilha TCP/IP, exibe o estado em tempo real (`ONLINE` ou `OFFLINE`) em um painel web protegido por autenticação e permite o envio sob demanda de relatórios de status via e-mail (protocolo SMTP) para os responsáveis técnicos.

---

## 3. Arquitetura, Infraestrutura e Plano de Rede

A solução foi estruturada para operar em ambiente Linux virtualizado/conteinerizado com comunicação via rede IP entre múltiplos nós, atendendo aos requisitos de infraestrutura distribuída e diagnóstico de rede.

### Plano de Endereçamento e Portas

| Nó / Componente | Sistema Operacional / Imagem | Endereço IP (Rede Docker/VM) | Máscara / Gateway | Portas e Protocolos | Função |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nó 1: Servidor de Monitoramento** (`monitor-web`) | Python 3.12-slim (Linux) | Dinâmico na rede `rede-scf` (ex.: `172.x.x.x`) | Sub-rede Docker / Gateway da rede | `5000/TCP` (HTTP) | Executa `app.py`, thread de checagem periódica (30s), painel Flask e envio SMTP. |
| **Nós 2 e 3: Clientes de Teste** (`cliente-teste-1`, `cliente-teste-2`) | Python 3.12-slim (Linux) | Dinâmico na rede `rede-scf` | Sub-rede Docker / Gateway da rede | Cliente HTTP/TCP | Nós auxiliares na mesma rede para testes de conectividade e diagnóstico. |
| **Alvos Externos Monitorados** | Google / DNS Público | `https://google.com`, `google.com`, `8.8.8.8` | Roteamento Externo | `443/TCP` (HTTPS), `53/UDP-TCP` (DNS) | Verificação de disponibilidade HTTP, resolução DNS e conexão TCP. |
| **Servidor de E-mail (SMTP)** | Gmail SMTP (`smtp.gmail.com`) | Dinâmico (via DNS) | Roteamento Externo | `587/TCP` (SMTP + STARTTLS) | Envio dos relatórios de disponibilidade sob demanda. |

---

## 4. Bibliotecas Python e Justificativa Técnica

| Biblioteca | Tipo | Função e Justificativa de Uso |
| :--- | :--- | :--- |
| `socket` | Nativa (Standard Library) | Utilizada para testar conexões diretas na camada de transporte (`create_connection` via TCP na porta 53 com timeout de 5s) e realizar resolução de nomes (`gethostbyname` via DNS). |
| `urllib.request` | Nativa (Standard Library) | Empregada (`urlopen` com timeout de 5s) para validar a disponibilidade de aplicações web na camada de aplicação (HTTP/HTTPS). |
| `threading` | Nativa (Standard Library) | Garante a concorrência da aplicação: executa o loop contínuo de monitoramento (a cada 30s) em uma *daemon thread* em paralelo ao servidor web e dispara o envio de e-mails em outra thread, usando `threading.Lock()` para proteger o acesso ao dicionário `resultados`. |
| `smtplib` e `email.mime` | Nativas (Standard Library) | Implementam o cliente SMTP com criptografia TLS (`starttls()`) e formatação MIME para envio de relatórios por e-mail. |
| `flask` | Externa (Framework Web) | Fornece o servidor HTTP, rotas (`/`, `/login`, `/logout`, `/enviar-relatorio`), renderização HTML e controle de sessão (`session`) para autenticação. |

---

## 5. Segurança Básica e Robustez

- **Autenticação Simples:** O painel web restringe o acesso ao status dos serviços e ao envio de relatórios por meio de tela de login protegida por sessão (`app.secret_key`).
- **Tratamento de Exceções e Timeouts:** As verificações HTTP, DNS e TCP utilizam `timeout=5` e blocos `try/except`, retornando `OFFLINE` em caso de falha sem derrubar a thread de monitoramento nem o servidor Flask.
- **Comunicação Segura (TLS):** O envio de relatórios via SMTP utiliza `STARTTLS` na porta `587` e autenticação via Senha de Aplicativo.

---

## 6. Estrutura do Repositório

```text
├── app.py                  # Código-fonte principal (Flask + Monitoramento + SMTP)
├── requirements.txt        # Dependências externas do projeto (Flask)
├── Dockerfile              # Receita para construção da imagem do contêiner Python
├── docker-compose.yml      # Orquestração dos nós de rede (monitor-web e clientes de teste)
└── README.md               # Documentação técnica e instruções de reprodutibilidade