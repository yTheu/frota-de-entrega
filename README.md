# 🚚 IF Express - Sistema de Gerenciamento de Frota

## 📝 Descrição

Aplicação web em Django para gerenciamento de frotas de entrega, com planejamento de rotas via Google Maps e simulação/rastreio em tempo real de veículos usando threads.

## ✨ Funcionalidades

* **Admin:** Dashboard, CRUD de Veículos/Motoristas, Planejamento de Rotas (manual/automático), Supervisão de Entregas, Rastreio em Mapa, Gestão de Manutenções.
* **Cliente:** Cadastro/Login, Solicitação de Entrega (com auto-preenchimento de CEP), Acompanhamento de Pedidos, Histórico de Rastreamento.
* **Motorista:** Login, Visualização de Rotas, Iniciar Rota (ativa simulação), Registrar Abastecimento/Manutenção, Atualizar Status de Entrega, Encerrar Rota Manualmente.
* **Sistema:** Planejamento automático de rotas (agrupamento, API Google), Simulação concorrente de rotas (threads, polyline, checkpoints dinâmicos).

## 🛠️ Tecnologias

* **Back-end:** Python, Django, SQLite3
* **Front-end:** HTML5, CSS3, JavaScript, Bootstrap 5
* **APIs:** Google Maps (Geocoding, Directions, Maps JavaScript), ViaCEP
* **Bibliotecas:** `googlemaps`, `python-dotenv`
* **Concorrência:** `threading` (Python)

## 🚀 Como Executar

1.  Clone o repositório.
2.  Crie e ative um ambiente virtual (`venv`).
3.  Instale as dependências
4.  Crie um arquivo `.env` na raiz e adicione sua(s) chave(s) da API do Google Maps (ex: `Maps_API_KEY="SUA_CHAVE"`).
5.  Aplique as migrações: `python manage.py makemigrations && python manage.py migrate`.
6.  Crie um superusuário: `python manage.py createsuperuser`.
7.  Rode o servidor: `python manage.py runserver`.
8.  Acesse: `http://127.0.0.1:8000/`.
   
---
