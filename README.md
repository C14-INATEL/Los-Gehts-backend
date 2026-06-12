# Los Geht's — Backend

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
<summary>✅ Rotas de Tarefas (<code>/tasks</code>)</summary>

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

## Créditos e IA

Este projeto utilizou **DeepSeek** como assistente de IA para:

- Criação e refinamento deste README
- Criação da documentação completa das rotas da API (autenticação e tarefas)
- Desenvolvimento e correção do Jenkinsfile
- Configuração de credenciais e variáveis de ambiente no Jenkins
- Debug de erros do pipeline (permissões, branches, workspace)
- Ajuda com sintaxe do Jenkinsfile (environment, post, agent, credentials)

### Exemplos de prompts utilizados:

**Jenkinsfile e Pipeline:**
- *"Como fazer o Jenkinsfile ler o Jenkinsfile do repositório?"*
- *"Como passar a DATABASE_URL como variável de ambiente para o container nos testes?"*
- *"Como carregar um caminho de projeto como variável no environment?"*
- *"Como usar a variável WORKSPACE para definir caminhos relativos?"*
- *"Qual a diferença entre agent any e agent { docker { ... } }?"*
- *"Como corrigir o erro 'permission denied while trying to connect to the docker API'?"*
- *"Como configurar o post para enviar e-mails com emailext?"*
- *"Onde armazenar uma variável de ambiente que não é um credential no Jenkins?"*
- *"Como limpar o workspace corrompido no Jenkins?"*
- *"Como fazer o Jenkins apontar para uma branch específica em vez da main?"*

**Documentação da API:**
- *"Documente as rotas de autenticação do meu projeto de acordo com esses arquivos"*
- *"Crie documentação para as rotas de tarefas com exemplos de requisição e resposta"*
- *"Adicione tabelas de erros para cada rota"*

### Como utilizamos as respostas

Todo o conteúdo gerado pelo DeepSeek foi:
- **Revisado manualmente** para garantir precisão técnica
- **Adaptado ao contexto do projeto** (ajustando paths, nomes de branches, credenciais e URLs específicas)
- **Formatado e padronizado** conforme as preferências da equipe (remoção de emojis, ajuste de linguagem, organização de seções)
- **Testado na prática** antes de ser incorporado à documentação final

A ferramenta foi utilizada como ponto de partida e assistente de aceleração, mas todas as soluções foram validadas e adaptadas às necessidades específicas do projeto.

---

**DeepSeek** demonstrou ser uma ferramenta valiosa para:
- Acelerar a escrita de documentação técnica
- Debugar erros comuns de pipeline e infraestrutura
- Sugerir boas práticas de CI/CD com Jenkins
- Ajudar na sintaxe correta do Groovy para Jenkinsfile
