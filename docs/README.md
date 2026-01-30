# Documentacao do Finanpy

Sistema de gestao de financas pessoais desenvolvido em Python/Django.

## Indice

1. [Instalacao](instalacao.md) - Como configurar o ambiente de desenvolvimento
2. [Estrutura do Projeto](estrutura.md) - Organizacao de pastas e arquivos
3. [Arquitetura](arquitetura.md) - Stack tecnologica e decisoes arquiteturais
4. [Padroes de Codigo](codigo.md) - Convencoes e estilo de codigo
5. [Design System](design-system.md) - Paleta de cores, tipografia e componentes UI

## Sobre o Projeto

O Finanpy e uma aplicacao web para controle financeiro pessoal com:

- Sistema de autenticacao baseado em email
- Gestao de contas bancarias
- Categorizacao de transacoes
- Controle de receitas e despesas
- Dashboard analitico

## Status Atual

O projeto esta em fase inicial de desenvolvimento. A estrutura base do Django foi criada com as seguintes apps:

- `users` - Gerenciamento de usuarios
- `profiles` - Perfis de usuario
- `accounts` - Contas bancarias
- `categories` - Categorias de transacoes
- `transactions` - Transacoes financeiras

## Links Uteis

- [PRD.md](../PRD.md) - Documento de requisitos completo do produto
