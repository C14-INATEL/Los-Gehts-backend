# Los Geht's — Backend

## Indice

- Pre-requisitos
- Configuracao Inicial
- Banco de Dados
- Rodando o Servidor
- Resolucao de Problemas
- Jenkins Pipeline
- Documentacao da API
- Creditos e IA

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (necessário para o PostgreSQL)
- Python 3.x

---

## Configuração inicial

> Realize esses passos apenas na **primeira vez** que for usar o projeto.

1. **Inicie o Docker Desktop** e aguarde até que ele esteja completamente em execução.
2. Execute o script de instalação:

```bash
installDependencies.bat
```

Esse script irá:
- Baixar e configurar o container do **PostgreSQL** via Docker
- Criar um **ambiente virtual Python** local
- Instalar todas as **dependências do projeto**

Após a conclusão, o ambiente estará pronto para uso.

---

## Banco de Dados

### Subindo o PostgreSQL

Para rodar o banco de dados localmente:

cd database
docker-compose up -d
cd ..

Isso ira:
- Iniciar um container PostgreSQL com as configuracoes:
  - Usuario: c14
  - Senha: senhamuitosegura
  - Banco: mydb2
  - Porta: 5432

### Resetando o banco

wipeDB.bat

---

## Rodando o servidor

Com o projeto já configurado, execute:

```bash
RunServer.bat
```

Esse script irá:
1. Ativar o ambiente virtual Python
2. Sincronizar o **Prisma** com o banco de dados
3. Iniciar o servidor

> Certifique-se de que o **Docker Desktop está aberto** antes de rodar o servidor.

---

## Resolução de problemas

### Resetar o banco de dados

Caso precise limpar todos os dados do banco e começar do zero:

```bash
wipeDB.bat
```

---

## Jenkins Pipeline

### O que e necessario?

O pipeline automatiza:
- Build da aplicacao
- Execucao de testes
- Linter (flake8)
- Build da imagem Docker
- Push para o Docker Hub
- Deploy
- Notificacoes por email

### Passo 1: Subir o Jenkins

Na raiz do projeto, execute:

docker-compose up -d

Isso ira:
- Construir a imagem do Jenkins com todos os plugins necessarios
- Iniciar o container na porta 8080
- Montar o volume persistente para dados do Jenkins
- Conectar o Docker socket (para builds de imagens)

### Passo 2: Acessar o Jenkins

1. Abra o navegador em http://localhost:8080

### Passo 3: Configurar Credenciais

No Jenkins, va em Manage Jenkins > Credentials > Global > Add Credentials:

ID: jenkins-email-recipients
Tipo: Secret text
Valor: email1@gmail.com,email2@gmail.com

ID: docker-hub-credentials
Tipo: Username with password
Valor: Seu usuario/senha do access token gerado em Docker Hub > account settings > personal access token

### Passo 4: Configurar SMTP (Email)

Va em Manage Jenkins > System > E-mail Notification:

SMTP Server: smtp.gmail.com
Use SMTP Authentication: Sim
User Name: seu-email@gmail.com
Password: App password do Gmail
Use TLS: Sim
SMTP Port: 587

Para Gmail, gere um App Password em: Conta Google > Inicio
Pesquise por "Senhas de app"

Opcional: Para testar se esta funcionando, habilite a opcao "Test configuration..." e digite um endereco para receber um email de test

Clique em Save

### Passo 5: Rodar container do Banco de Dados (necessario para testes)

O pipeline executa testes que exigem o PostgreSQL:

cd database
docker-compose up -d
cd ..

### Passo 6: Criar o Pipeline no Jenkins

1. Clique em New Item
2. Nome: los-gehts-backend
3. Tipo: Pipeline
4. Na secao Pipeline:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: https://github.com/C14-INATEL/Los-Gehts-backend
   - Branch: */main
   - Script Path: Jenkinsfile
5. Clique em Save

### Passo 7: Executar o Pipeline

Clique em Build Now e acompanhe a execucao.

O pipeline ira:
1. Instalar dependencias
2. Rodar testes com pytest
3. Executar flake8
4. Buildar imagem Docker
5. Fazer push para o Docker Hub (apenas na branch main)
6. Enviar notificacao de sucesso/fracasso

---

## Documentação da API

<details>
<summary>🔐 Rotas de Autenticação (<code>/auth</code>)</summary>

<br>

### POST `/auth/register`
Registra um novo usuário na plataforma.

**Body (JSON):**
```json
{
  "username": "string",
  "password": "string"
}
```

**Regras de negócio:**
- O `username` deve ser único — se já existir, retorna erro
- Ao registrar com sucesso, um token JWT é gerado automaticamente

**Retorna (201 Created):**
```json
{
  "JWT": "eyJ..."
}
```

**Erros:**
| Código | Motivo |
|---|---|
| 400 | Username já cadastrado |

---

### POST `/auth/login`
Autentica um usuário existente.

**Body (JSON):**
```json
{
  "username": "string",
  "password": "string"
}
```

**Regras de negócio:**
- O username deve existir no banco
- A senha deve ser idêntica à cadastrada
- Qualquer divergência retorna o mesmo erro genérico (sem revelar qual campo está errado)

**Retorna (200 OK):**
```json
{
  "JWT": "eyJ..."
}
```

**Erros:**
| Código | Motivo |
|---|---|
| 401 | Credenciais inválidas (usuário não encontrado ou senha errada) |

</details>

---

<details>
<summary>Rotas de Tarefas (<code>/tasks</code>)</summary>

<br>

> Todas as rotas de tarefas exigem autenticação via **Bearer Token** no header:
> ```
> Authorization: Bearer <token>
> ```
> O `user_id` é extraído automaticamente do token — não é necessário enviá-lo no body.

---

### POST `/tasks/`
Cria uma nova tarefa para o usuário autenticado.

**Body (JSON):**
```json
{
  "title": "string",
  "description": "string",
  "priority": "LOW | MEDIUM | HIGH",
  "due_date": "2025-12-31T00:00:00"
}
```

**Regras de negócio:**
- A tarefa é criada com `completed: false` por padrão
- O `userId` é vinculado automaticamente ao usuário do token
- `due_date` é opcional

**Retorna (201 Created):** objeto da tarefa criada

**Erros:**
| Código | Motivo |
|---|---|
| 401 | Token inválido ou ausente |
| 500 | Erro interno ao salvar no banco |

---

### GET `/tasks/pending`
Retorna todas as tarefas **não concluídas** do usuário autenticado.

**Recebe:** apenas o Bearer Token no header

**Regras de negócio:**
- Filtra por `userId` do token e `completed: false`
- Ordenadas por data de criação (mais recentes primeiro)

**Retorna (200 OK):** lista de tarefas pendentes

**Erros:**
| Código | Motivo |
|---|---|
| 401 | Token inválido ou ausente |
| 500 | Erro interno ao consultar o banco |

---

### GET `/tasks/completed`
Retorna todas as tarefas **concluídas** do usuário autenticado.

**Recebe:** apenas o Bearer Token no header

**Regras de negócio:**
- Filtra por `userId` do token e `completed: true`
- Ordenadas por data de atualização (mais recentes primeiro)

**Retorna (200 OK):** lista de tarefas concluídas

**Erros:**
| Código | Motivo |
|---|---|
| 401 | Token inválido ou ausente |
| 500 | Erro interno ao consultar o banco |

---

### PUT `/tasks/{task_id}`
Atualiza os dados de uma tarefa existente.

**Recebe:**
- `task_id` na URL
- Bearer Token no header
- Body JSON com os campos a atualizar (todos opcionais):

```json
{
  "title": "string",
  "priority": "LOW | MEDIUM | HIGH",
  "due_date": "2025-12-31T00:00:00"
}
```

**Regras de negócio:**
- Apenas o dono da tarefa pode atualizá-la (verifica `userId` + `task_id`)
- Somente os campos enviados são atualizados
- `due_date` é renomeado internamente para `dueDate` antes de salvar no banco

**Retorna (200 OK):** objeto da tarefa atualizada

**Erros:**
| Código | Motivo |
|---|---|
| 401 | Token inválido ou ausente |
| 404 | Tarefa não encontrada ou não pertence ao usuário |
| 500 | Erro interno ao atualizar no banco |

---

### POST `/tasks/{task_id}/complete`
Marca uma tarefa como concluída.

**Recebe:**
- `task_id` na URL
- Bearer Token no header

**Regras de negócio:**
- Apenas o dono da tarefa pode completá-la
- Define `completed: true` na tarefa

**Retorna (200 OK):** objeto da tarefa com `completed: true`

**Erros:**
| Código | Motivo |
|---|---|
| 401 | Token inválido ou ausente |
| 404 | Tarefa não encontrada ou não pertence ao usuário |
| 500 | Erro interno ao atualizar no banco |

---

### DELETE `/tasks/{task_id}`
Remove permanentemente uma tarefa.

**Recebe:**
- `task_id` na URL
- Bearer Token no header

**Regras de negócio:**
- Apenas o dono da tarefa pode deletá-la
- A operação é irreversível

**Retorna (204 No Content):** sem body

**Erros:**
| Código | Motivo |
|---|---|
| 401 | Token inválido ou ausente |
| 404 | Tarefa não encontrada ou não pertence ao usuário |
| 500 | Erro interno ao deletar no banco |

</details>

---

## Créditos e IA

Este projeto utilizou **DeepSeek** como assistente de IA para:

- Criação e refinamento deste README
- Geração dos Dockerfiles
- Criação da documentação completa das rotas da API (autenticação e tarefas)
- Correção de problemas no pipeline (plugins, credenciais, rede)
- Ajuda com sintaxe do Jenkinsfile
- Debug de erros de container e network

### Exemplos de prompts utilizados:

**Docker:**
- *"Preciso de um Dockerfile para Jenkins com Docker CLI e plugins"*
- *"Preciso de um Dockerfile para meu aplicativo python com prisma"*

**Documentação da API:**
- *"Documente as rotas de autenticação do meu projeto de acordo com esses arquivos"*
- *"Crie documentação para as rotas de tarefas com exemplos de requisição e resposta"*
- *"Adicione tabelas de erros para cada rota"*

**Jenkins Pipeline:**
- *"Atualize o README com as etapas do Jenkins pipeline"*
- *"Como configurar credenciais e SMTP no Jenkins?"*

### Como utilizamos as respostas

Todo o conteúdo gerado pelo DeepSeek foi:
- **Revisado manualmente**
- **Adaptado ao contexto do projeto** (ajustando paths, variáveis de ambiente e comandos específicos)
- **Formatado e padronizado** conforme as preferências da equipe (remoção de emojis, ajuste de linguagem e formatação, organização de seções)
- **Testado na prática** antes de ser incorporado à documentação final

A ferramenta foi utilizada como ponto de partida e assistente de aceleração, mas todas as soluções foram validadas e adaptadas às necessidades específicas do projeto.

---

**DeepSeek** demonstrou ser uma ferramenta valiosa para:
- Acelerar a escrita de documentação técnica
- Gerar boilerplate de configuração
- Debugar erros comuns de infraestrutura
- Sugerir boas práticas de DevOps
