# A.R.A. Frontend - Redesign Base

Esta entrega transforma o frontend atual em um shell de produto A.R.A. preservando as rotas de backend ja existentes para autenticacao, conversas, chat e tarefas.

## O que esta implementado

- Identidade visual A.R.A. (dark/light)
- Login redesenhado
- Main shell responsivo
- Sidebar recolhivel
- Command Center (Ctrl+K)
- Home / Hoje com resumo de tarefas reais
- Chat reestilizado sem alterar o contrato `/chat`
- Tarefas preservadas e reestilizadas
- Rotas preparadas para Agenda, Memoria, Arquivos, Projetos, Automacoes e Integracoes
- Pagina de configuracoes com tema persistente

## Rotas

- `/hoje`
- `/chat`
- `/tarefas`
- `/agenda`
- `/memoria`
- `/arquivos`
- `/projetos`
- `/automacoes`
- `/integracoes`
- `/configuracoes`

## Integracoes mantidas

- `POST /auth/login`
- `GET/POST/PATCH/DELETE /conversas...`
- `GET /mensagens/conversa/{id}`
- `POST /chat`
- `GET/POST/PATCH/DELETE /tarefas...`

## Observacao

Os modulos novos que ainda nao possuem endpoints no backend aparecem como superficies preparadas para integracao, sem inventar dados ou simular persistencia inexistente.
