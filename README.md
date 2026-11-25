# Monitor de Disponibilidade de Serviços

**Disciplina:** PSI129A - Conectividade em Sistemas Ciberfísicos  
**Curso:** Bacharelado em Ciência da Computação — Escola Politécnica / PUCPR (Curitiba)  
**Turma:** CCCO - 2U - N - 2026/02  
**Professor:** Prof. MSc. Luis Gonzaga de Paulo  

---

## 1. Identificação da Equipe e Links

- **Integrante 1:** Lucas Gomes Bernardino
- **Integrante 2:** Guilherme Filipak Retamero 
- **Integrante 3:** Leticia Souza de Oliveira 
- **Link do Vídeo de Demonstração (até 10 min):** `https://www.youtube.com/watch?v=0_HDkR3rcMo`
- **Link do Repositório (GitHub / GitLab):** `https://github.com/lucasgb29/monitoramento_server_pjbl`

---

## 2. Objetivo e Cenário de Uso Real

### Problema Atendido
Pequenas empresas e equipes de suporte de TI frequentemente enfrentam dificuldades para identificar rapidamente quando um serviço crítico (como o site institucional, servidor de resolução de nomes ou porta de serviço/aplicação) sai do ar, descobrindo a falha apenas quando clientes ou colaboradores relatam o problema.

### Solução Proposta
Este projeto implementa um **Monitor de Disponibilidade de Serviços** leve e automatizado. A aplicação realiza verificações periódicas em segundo plano na pilha TCP/IP, exibe o estado em tempo real (`ONLINE` ou `OFFLINE`) em um painel web protegido por autenticação e permite o envio sob demanda de relatórios de status via e-mail (protocolo SMTP) para os responsáveis técnicos.

---

## 3. Arquitetura, Infraestrutura e Plano de Rede

A solução foi estruturada para operar em ambiente Linux virtualizado/conteinerizado com comunicação via rede IP entre múltiplos nós (`monitor-web`, `cliente-teste-1` e `cliente-teste-2` na rede `rede-scf`), atendendo aos requisitos de infraestrutura distribuída e diagnóstico de rede.

### Plano de Endereçamento e Portas

| Nó / Componente | Sistema Operacional / Imagem | Endereço IP (Rede Docker/VM) | Máscara / Gateway | Portas e Protocolos | Função |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nó 1: Servidor de Monitoramento** (`monitor-web` / `monitor-disponibilidade-scf`) | Python 3.12-slim (Linux) | Dinâmico na rede `rede-scf` (ex.: `172.18.0.2` / `0.0.0.0`) | Sub-rede Docker (`172.18.0.0/16`) / Gateway (`172.18.0.1`) | `5000/TCP` (HTTP) | Executa `app.py`, thread de checagem periódica (30s), painel Flask e envio SMTP. |
| **Nós 2 e 3: Clientes de Teste** (`cliente-teste-1`, `cliente-teste-2`) | Python 3.12-slim (Linux) | Dinâmico na rede `rede-scf` (ex.: `172.18.0.3`) | Sub-rede Docker (`172.18.0.0/16`) / Gateway (`172.18.0.1`) | Cliente HTTP/TCP | Nós auxiliares na mesma rede para testes de conectividade e diagnóstico. |
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
- **Comunicação Segura (TLS) e Boas Práticas de Credenciais:** O envio de relatórios via SMTP utiliza `STARTTLS` na porta `587` e autenticação via Senha de Aplicativo. Para o repositório público, recomenda-se configurar as credenciais via variáveis de ambiente em vez de mantê-las fixas no código.

---

## 6. Estrutura do Repositório e Execução

```text
├── app.py                  # Código-fonte principal (Flask + Monitoramento + SMTP)
├── requirements.txt        # Dependências externas do projeto (Flask)
├── Dockerfile              # Receita para construção da imagem do contêiner Python
├── docker-compose.yml      # Orquestração dos nós de rede (monitor-web e clientes de teste)
└── README.md               # Documentação técnica e instruções de reprodutibilidade
```

### Como Executar com Docker Compose
1. Certifique-se de que `app.py`, `requirements.txt`, `Dockerfile` e `docker-compose.yml` estejam no mesmo diretório.
2. Configure o e-mail remetente e a Senha de App no `app.py` (ou via variáveis de ambiente antes de iniciar).
3. Suba o ambiente com o comando:
   ```bash
   docker compose up --build -d
   ```
4. Acesse `http://localhost:5000` no navegador, autentique-se com usuário `admin` e senha `1234`, acompanhe o status dos serviços e teste o envio do relatório por e-mail.

---

## 7. Ferramentas de Diagnóstico, Testes e Evidências

Para verificar o funcionamento do sistema, da rede e do ambiente Linux/Docker, foram utilizados comandos de diagnóstico (como `ip`, `ss`, `dig`, `tcpdump`/Wireshark, `htop` e logs do Docker) e definidos os seguintes casos de teste:

| ID | Objetivo do teste | Procedimento | Resultado esperado | Resultado obtido | Evidência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T01** | Verificar comunicação entre nós na rede Docker e acesso ao painel | Executar requisição HTTP a partir do `cliente-teste-1` para `http://monitor-web:5000` e acessar via navegador | Resposta HTTP `200` e carregamento do painel/login | Resposta `200` no cliente e acesso `GET /` e `POST /login` registrados nos logs do servidor | `[Inserir Print/Log]` |
| **T02** | Verificar autenticação e envio de relatório via SMTP | Fazer login no painel, informar e-mail de destino e clicar no botão de enviar relatório | Redirecionamento com mensagem de confirmação e recebimento do e-mail com status dos serviços | Relatório montado com data/hora e status e disparado via SMTP (`587/TCP`) | `[Inserir Print/E-mail]` |
| **T03** | Verificar tratamento de falha / indisponibilidade | Simular falha de conexão/timeout ou alvo indisponível durante a checagem | Marcar serviço como `OFFLINE` sem travar o loop de monitoramento nem o Flask | Status atualizado para `OFFLINE` com exceção tratada e servidor estável | `[Inserir Print/Log]` |

---

## 8. Problemas Encontrados, Soluções e Aprendizados

### Problemas Encontrados e Soluções
- **Autenticação SMTP no Gmail:** A senha comum da conta não autenticava no envio via `smtplib`; foi resolvido ativando a verificação em duas etapas e gerando uma Senha de App de 16 dígitos.
- **Acesso ao servidor Flask no contêiner:** Garantir que o Flask escute em `0.0.0.0:5000` e mapeie a porta no `docker-compose.yml` para permitir acesso externo e entre os nós da `rede-scf`.
- **Concorrência entre monitoramento e requisições web:** Uso de `threading` e `threading.Lock()` para evitar condições de corrida na leitura/escrita dos resultados e não bloquear a interface web durante o envio de e-mails.

### Aprendizados e Contribuição dos Integrantes
- A equipe consolidou na prática o uso de threads, sockets/HTTP/SMTP, autenticação web básica e redes em contêineres Linux.
- **Lucas Gomes Bernardino:** `Desenvolvimento do codigo fonte em python e documentaçãodo projeto`.
- **Guilherme Filipak Retamero:** `Desenvolvimento da infrastrutura com Docker`.
- **Leticia Souza de Oliveira:** `Descrição de erros e desafios encontrados no projeto`.

---

## 9. Conclusões e Trabalhos Futuros

O monitor atende ao cenário proposto ao integrar verificações TCP/IP, painel web protegido por login, envio de relatório por e-mail via SMTP e ambiente com múltiplos nós em rede. Como melhorias futuras, destacam-se: carregar credenciais exclusivamente por variáveis de ambiente, utilizar um servidor WSGI de produção (como Gunicorn) no lugar do servidor de desenvolvimento do Flask e persistir o histórico de eventos em arquivo de log ou banco de dados.

---

## 10. Referências (ABNT)

DE PAULO, Luis Gonzaga. **Material da disciplina PSI129A — Conectividade em Sistemas Ciberfísicos**: slides, roteiros e enunciado do Projeto 6. Curitiba: PUCPR, 2026.

PYTHON SOFTWARE FOUNDATION. **Python 3 Documentation**: `socket`, `threading`, `urllib.request`, `smtplib` e `email`. Disponível em: <https://docs.python.org/3/>. Acesso em: 24 nov. 2026.

PALLETS PROJECTS. **Flask Documentation**. Disponível em: <https://flask.palletsprojects.com/>. Acesso em: 24 nov. 2026.

DOCKER INC. **Docker Documentation**: Dockerfile e Docker Compose. Disponível em: <https://docs.docker.com/>. Acesso em: 24 nov. 2026.

---

## 11. Declaração de Uso de Inteligência Artificial Generativa

Conforme a Resolução nº 274/2024 CONSUN da PUCPR:

> "Durante a preparação deste projeto e sua documentação, os autores usaram o Google Gemini (versão 2026) para apoio na estruturação do sistema de autenticação em Flask, implementação do envio de relatórios via protocolo SMTP com concorrência em threads, configuração de ambiente Docker/rede e revisão/complementação da documentação técnica. Após usar essa ferramenta, os autores revisaram, testaram e editaram o conteúdo conforme necessário e assumem total responsabilidade pelo conteúdo."