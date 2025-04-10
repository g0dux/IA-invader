# IA invader

![Banner](https://via.placeholder.com/800x200?text=IA+invader)

Bem-vindo ao **IA invader**, seu assistente de segurança local alimentado por inteligência artificial! Esta ferramenta foi desenvolvida para interpretar comandos em linguagem natural e convertê-los automaticamente em comandos de shell válidos, auxiliando você na execução de varreduras de segurança e análises de vulnerabilidades com facilidade.

---

## Sumário

- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Pré-requisitos e Dependências](#pré-requisitos-e-dependências)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
  - [Exemplos de Comandos](#exemplos-de-comandos)
- [Llama Pull Mistral e Ollama](#llama-pull-mistral-e-ollama)
- [Feedback e Auto-Correção](#feedback-e-auto-correção)
- [Logs e Histórico](#logs-e-histórico)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato](#contato)

---

## Sobre

O **IA invader** é uma ferramenta de linha de comando que utiliza a API do Ollama com o modelo **Mistral** para gerar comandos de shell a partir de requisições feitas em linguagem natural. A ferramenta suporta comandos direcionados a sistemas Linux e Windows e oferece recursos como:

- **Geração Automática de Comandos:** Transforma a requisição do usuário em um comando de shell apropriado.
- **Interpretação do Comando:** Exibe uma breve explicação do que o comando fará.
- **Auto-Correção:** Sugere alternativas em caso de erro na execução.
- **Interface Multilíngue:** Suporte para Inglês e Português.
- **Spinner e Feedback Visual:** Exibe uma animação enquanto o comando é processado.
- **Dicas de Instalação:** Caso uma ferramenta necessária não esteja instalada, são fornecidas instruções e links para o download.

---

## Funcionalidades

- **Geração Inteligente:** Converte requisições em comandos de shell com base em inteligência artificial.
- **Execução Interativa:** Pede confirmação antes de executar comandos sensíveis.
- **Feedback Visual:** Inclui um spinner animado para indicar que o comando está sendo processado.
- **Sugestões de Correção:** Em caso de erro, a ferramenta interage para sugerir um comando alternativo.
- **Multilíngue:** Interface disponível em Inglês e Português.
- **Customização:** Permite selecionar o sistema operacional alvo (Linux ou Windows).

---

## Pré-requisitos e Dependências

Antes de utilizar o IA invader, certifique-se de ter os seguintes itens instalados:

- **Python 3.7+**  
  A ferramenta foi desenvolvida em Python e utiliza os seguintes módulos:
  - `os`, `time`, `subprocess`, `requests`, `sys`, `threading`, `itertools`

  Caso não possua o módulo *requests*, instale-o com:
  ```bash
  pip install requests
API do Ollama com o Modelo Mistral
A ferramenta utiliza a API do Ollama para gerar comandos. A URL padrão é:
http://localhost:11434/api/generate
Certifique-se de que o serviço está ativo.

Llama Pull Mistral com Ollama
Para utilizar o modelo Mistral, é necessário baixar e configurar o Llama Pull Mistral. Veja mais detalhes na sessão Llama Pull Mistral e Ollama abaixo.

Ferramentas de Segurança
Dependendo dos comandos gerados, você poderá precisar de ferramentas como:

Nmap:

Download para Windows
ou, em Linux:

bash
Copiar
Editar
sudo apt install nmap
Nikto:

Download para Windows
ou siga as instruções para instalação em Linux.

Permissões de Execução:
Em sistemas Windows ou quando comandos exigirem privilégios de root em Linux, execute o script com as permissões apropriadas.

Instalação
Clone o repositório:

bash
Copiar
Editar
git clone https://github.com/seu-usuario/ia-invader.git
cd ia-invader
Crie um ambiente virtual (opcional, mas recomendado):

bash
Copiar
Editar
python3 -m venv venv
source venv/bin/activate  # Em Linux/macOS
venv\Scripts\activate     # Em Windows
Instale as dependências:

bash
Copiar
Editar
pip install -r requirements.txt
Configure a API do Ollama:
Certifique-se de que a API está rodando na URL especificada. Caso necessário, atualize a variável OLLAMA_API_URL no código.

Configure o Llama Pull Mistral com Ollama:
Veja os passos na sessão Llama Pull Mistral e Ollama.

Configuração
Idioma:
Ao iniciar, escolha entre Inglês e Português para a interface da ferramenta.

Sistema Operacional Alvo:
Selecione se os comandos gerados serão para um sistema Linux ou Windows.

Personalização:
Os textos e mensagens estão definidos no dicionário LANGUAGES do código e podem ser editados conforme necessário.

Ferramentas Suportadas:
O dicionário DOWNLOAD_LINKS contém links e instruções de instalação para ferramentas essenciais (como Nmap e Nikto). Expanda essa lista conforme necessário.

Uso
Para iniciar o IA invader, execute:

bash
Copiar
Editar
python ia_invader.py
Siga as etapas a seguir:

Seleção de Idioma:
Escolha entre Inglês ou Português para a interface.

Seleção do Sistema Operacional:
Defina se o alvo é Linux ou Windows.

Interface Interativa:

Apresentação de banner e mensagens de boas-vindas.

Exibição de opções e instruções de uso.

Input para a sua requisição, por exemplo:

scss
Copiar
Editar
O que você deseja fazer? (ex.: varrer google.com com nmap):
Processamento e Execução:

O comando gerado será exibido juntamente com uma breve explicação.

Após a confirmação, o comando será executado. Se houver erro, a ferramenta pode sugerir uma correção automaticamente.

Exemplos de Comandos
Escanear um site com Nmap:

csharp
Copiar
Editar
scan google.com with nmap
Realizar uma varredura com Nikto:

csharp
Copiar
Editar
scan example.com with nikto
Llama Pull Mistral e Ollama
Para utilizar o modelo Mistral no IA invader, é necessário configurar o Llama Pull Mistral via Ollama:

Instale o Ollama:

Baixe o instalador apropriado para o seu sistema operacional no site oficial do Ollama.

Siga as instruções de instalação específicas para o seu sistema.

Verifique a instalação do Ollama:

Abra o terminal e execute:

bash
Copiar
Editar
ollama --version
Esse comando deve exibir a versão do Ollama instalada, confirmando que a instalação foi bem-sucedida.

Baixe o modelo Mistral:

No terminal, execute:

bash
Copiar
Editar
ollama pull mistral
Isso fará o download do modelo Mistral e o preparará para uso.

Execute o modelo Mistral:

Após o download, inicie o modelo com:

bash
Copiar
Editar
ollama run mistral
Isso iniciará uma sessão interativa, permitindo que a API utilize o modelo para gerar comandos conforme requisitado pelo IA invader.

Integração com o IA invader:

Certifique-se de que o serviço do Ollama com o modelo Mistral esteja em execução e configurado corretamente, para que a comunicação via API (na variável OLLAMA_API_URL) ocorra sem problemas.

Feedback e Auto-Correção
Confirmação Interativa:
Antes da execução, a ferramenta exibe a interpretação da IA e pede confirmação do usuário.

Auto-Correção:
Caso um comando resulte em erro, o IA invader permite tentar uma solução sugerida pela IA, enviando o erro para a API para uma nova geração de comando.

Logs e Histórico
Registro de Comandos:
Recomenda-se manter um sistema de logs registrando os comandos executados, seus resultados e erros, para facilitar a depuração e auditoria.

Histórico de Execuções:
Uma funcionalidade para visualizar o histórico dos comandos pode ajudar na automação e repetição de tarefas.

Contribuição
Se você deseja contribuir para o projeto:

Faça um fork deste repositório.

Crie uma branch para sua nova funcionalidade ou correção:

bash
Copiar
Editar
git checkout -b feature/nova-funcionalidade
Faça commit das alterações:

bash
Copiar
Editar
git commit -am 'Adiciona nova funcionalidade'
Envie para o repositório remoto:

bash
Copiar
Editar
git push origin feature/nova-funcionalidade
Abra um Pull Request com suas alterações.

Sua contribuição é muito bem-vinda!

Licença
Distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.

Contato
Autor: Seu Nome

Email: seu.email@exemplo.com

GitHub: seu-perfil

Dica Interativa:
Se encontrar algum problema ou tiver sugestões para melhorias, abra uma issue no repositório ou entre em contato via email. Estamos sempre em busca de aprimorar o IA invader para proporcionar a melhor experiência de segurança possível!

Aproveite e contribua para um ambiente de segurança mais inteligente e automatizado!
