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

O projeto esta funcional com as seguintes apps implementadas:

- `users` - Autenticacao baseada em email com registro e login
- `profiles` - Perfis de usuario com dados pessoais
- `accounts` - CRUD completo de contas bancarias (corrente, poupanca, carteira, investimentos)
- `categories` - Categorias de receitas e despesas com categorias padrao
- `transactions` - CRUD completo de transacoes financeiras com filtros e dashboard analitico

## Links Uteis

- [PRD.md](../PRD.md) - Documento de requisitos completo do produto
