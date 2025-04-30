import os
import time
import subprocess
import requests
import sys
import shutil  # Usado para verificar a existência do comando
from threading import Thread
from itertools import cycle
from typing import Optional, Dict, Any, Tuple, List
import traceback # Para depuração de erros inesperados

# --- Configuração ---
OLLAMA_MODEL: str = "mistral"  # Modelo a ser usado com Ollama
OLLAMA_API_URL: str = "http://localhost:11434/api/generate" # Endpoint da API Ollama
REQUEST_TIMEOUT: int = 120 # Timeout aumentado para Ollama (análise pode levar mais tempo)

# --- Estado Global ---
spinner_running: bool = False
selected_lang: str = "en" # Idioma padrão
selected_os: str = "linux" # SO padrão
msg: Dict[str, Any] = {} # Dicionário para mensagens específicas do idioma

# --- Constantes ---
# Dicionário com links e instruções de instalação para ferramentas conhecidas.
DOWNLOAD_LINKS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "nmap": {
        "windows": {
            "link": "https://nmap.org/download.html#windows",
            "instructions": {
                "en": "Nmap not found. Download the installer from the official Nmap website.",
                "pt": "Nmap não encontrado. Baixe o instalador no site oficial do Nmap."
            }
        },
        "linux": {
            "link": "https://nmap.org/download.html",
            "instructions": {
                "en": "Nmap not found. Install it using your package manager (e.g., 'sudo apt update && sudo apt install nmap' or 'sudo dnf install nmap').",
                "pt": "Nmap não encontrado. Instale-o usando seu gerenciador de pacotes (ex.: 'sudo apt update && sudo apt install nmap' ou 'sudo dnf install nmap')."
            }
        },
         "macos": {
            "link": "https://nmap.org/download.html",
            "instructions": {
                "en": "Nmap not found. Install it using Homebrew ('brew install nmap') or download from the official site.",
                "pt": "Nmap não encontrado. Instale usando o Homebrew ('brew install nmap') ou baixe do site oficial."
            }
        }
    },
    "nikto": {
        "windows": {
            "link": "https://cirt.net/Nikto2",
            "instructions": {
                "en": "Nikto not found. Download Nikto for Windows (requires Perl). See the official page for setup.",
                "pt": "Nikto não encontrado. Baixe o Nikto para Windows (requer Perl). Veja a página oficial para configuração."
            }
        },
        "linux": {
            "link": "https://github.com/sullo/nikto",
            "instructions": {
                "en": "Nikto not found. Install it using your package manager (e.g., 'sudo apt install nikto' or 'sudo dnf install nikto') or clone from GitHub.",
                "pt": "Nikto não encontrado. Instale usando seu gerenciador de pacotes (ex.: 'sudo apt install nikto' ou 'sudo dnf install nikto') ou clone do GitHub."
            }
        },
         "macos": {
            "link": "https://github.com/sullo/nikto",
            "instructions": {
                "en": "Nikto not found. Install it using Homebrew ('brew install nikto') or clone from GitHub.",
                "pt": "Nikto não encontrado. Instale usando o Homebrew ('brew install nikto') ou clone do GitHub."
            }
        }
    },
    "ip": {
        "linux": {
            "link": "https://wiki.archlinux.org/title/Iproute2",
            "instructions": {
                "en": "'ip' command not found. Ensure 'iproute2' package is installed (usually default, or 'sudo apt install iproute2').",
                "pt": "Comando 'ip' não encontrado. Certifique-se de que o pacote 'iproute2' está instalado (normalmente padrão, ou 'sudo apt install iproute2')."
            }
        }
    },
    "whois": {
        "windows": {
            "link": "https://docs.microsoft.com/en-us/sysinternals/downloads/whois",
            "instructions": {
                "en": "'whois' not found. Download it from Microsoft Sysinternals.",
                "pt": "'whois' não encontrado. Baixe do Microsoft Sysinternals."
            }
        },
        "linux": {
            "link": "",
            "instructions": {
                "en": "'whois' not found. Install it using your package manager (e.g., 'sudo apt install whois' or 'sudo dnf install whois').",
                "pt": "'whois' não encontrado. Instale usando seu gerenciador de pacotes (ex.: 'sudo apt install whois' ou 'sudo dnf install whois')."
            }
        },
        "macos": {
            "link": "",
            "instructions": {
                "en": "'whois' not found. It might be pre-installed. If not, try 'brew install whois'.",
                "pt": "'whois' não encontrado. Pode estar pré-instalado. Se não, tente 'brew install whois'."
            }
        }
    }
}

# Dicionário de mensagens multilíngues
LANGUAGES: Dict[str, Dict[str, Any]] = {
    "en": {
        "header": r"""

▪   ▄▄▄·     ▪   ▐ ▄  ▌ ▐· ▄▄▄· ·▄▄▄▄  ▄▄▄ .▄▄▄  
██ ▐█ ▀█     ██ •█▌▐█▪█·█▌▐█ ▀█ ██▪ ██ ▀▄.▀·▀▄ █·
▐█·▄█▀▀█     ▐█·▐█▐▐▌▐█▐█•▄█▀▀█ ▐█· ▐█▌▐▀▀▪▄▐▀▀▄ 
▐█▌▐█ ▪▐▌    ▐█▌██▐█▌ ███ ▐█ ▪▐▌██. ██ ▐█▄▄▌▐█•█▌
▀▀▀ ▀  ▀     ▀▀▀▀▀ █▪. ▀   ▀  ▀ ▀▀▀▀▀•  ▀▀▀ .▀  ▀
 Invader v2.1
""", # Versão atualizada
        "welcome": "Welcome to IA invader v2.1 - Your AI Security Assistant with Analysis", # Nome e versão atualizados
        "separator": "-----------------------------------------------------------------",
        "usage": "Usage: Enter your security task (e.g., 'scan example.com with nmap -sV')",
        "options": "Options: -h for help | -v for version | -lang to change language | -os to change OS",
        "help": (
            "\nUsage:\n  <Describe your task> (e.g., 'check open ports on 192.168.1.1 with nmap')\n"
            "IA invader will generate a command, execute it (with confirmation),\n"
            "analyze the output, and suggest follow-up actions.\n"
            "Supported tools depend on your system and Ollama's knowledge.\n"
            "Common examples: nmap, nikto, whois, ping, traceroute, dig, etc.\n"
            "Options:\n"
            "  -h : Show this help message\n"
            "  -v : Show version info\n"
            "  -lang : Change interface language\n"
            "  -os : Change target OS for command generation\n"
            "  exit : Quit the application\n"
        ),
        "version": f"IA invader v2.1 - Powered by Ollama ({OLLAMA_MODEL})", # Versão atualizada
        "input": "\nIA invader> ",
        "thinking": "IA invader is thinking... 🤔",
        "interpreting": "IA invader is interpreting the command... 🧐",
        "correcting": "IA invader is attempting to correct the command... 🛠️",
        "analyzing": "IA invader is analyzing the output... 🔬", # Nova mensagem
        "suggesting": "IA invader is suggesting next steps... 👉", # Nova mensagem
        "ai_generated": "\n🤖 AI Generated Command:",
        "ai_interpreted": "🤖 AI Interpretation:",
        "ai_corrected": "\n🤖 AI Corrected Command Suggestion:",
        "ai_analysis": "\n📊 AI Analysis of Output:", # Nova mensagem
        "ai_followup": "\n💡 AI Suggested Follow-up Commands:", # Nova mensagem
        "confirm": "Do you want to execute this command? (y/n): ",
        "execute": "🚀 Executing:",
        "ready": "\n✅ IA invader is ready for your next command! (Type 'exit' to quit)\n",
        "cancel": "❌ Command execution canceled by the user.",
        "error_fetch": "🚫 Failed to generate command via Ollama.",
        "error_interpret": "🚫 Failed to get interpretation from Ollama.",
        "error_correct": "🚫 Failed to get correction from Ollama.",
        "error_analyze": "🚫 Failed to get analysis from Ollama.", # Nova mensagem
        "error_suggest": "🚫 Failed to get suggestions from Ollama.", # Nova mensagem
        "error_ollama_comm": "🚫 Error communicating with Ollama API:",
        "error_ollama_conn": "🚫 Error connecting to Ollama API. Is Ollama running?",
        "error_invalid_req": "🚫 The request doesn't seem to translate into a valid shell command.",
        "error_permission": "🚫 Permission Denied: Cannot execute the command. Try running IA invader with administrator/root privileges if necessary.",
        "error_not_found": "🚫 Command not found:",
        "error_general": "🚫 An error occurred during execution:",
        "goodbye": "\n👋 Goodbye!",
        "os_select": "Select the target operating system for command generation:",
        "os_options": "1. Linux\n2. Windows\n3. macOS\nChoice (1/2/3): ",
        "lang_select": "Select language / Selecione o idioma:",
        "lang_options": "1. English\n2. Português\nChoice / Escolha (1/2): ",
        "auto_correct_q": "The command failed. Would you like to ask the AI for a correction? (y/n): ",
        "no_correction": "🤷 No alternative command suggested by AI.",
        "no_analysis": "🤷 AI could not provide an analysis for this output.", # Nova mensagem
        "no_suggestions": "🤷 AI could not provide follow-up suggestions.", # Nova mensagem
        "tool_hint": "Hint:",
        "tool_hint_generic": "Ensure the required tool is installed and available in your system's PATH.",
        "lang_set_by_arg": "Language set to {lang} by argument.",
        "proceed_q": "Proceed anyway? (y/n): ",
    },
    "pt": {
        "header": r"""

▪   ▄▄▄·     ▪   ▐ ▄  ▌ ▐· ▄▄▄· ·▄▄▄▄  ▄▄▄ .▄▄▄  
██ ▐█ ▀█     ██ •█▌▐█▪█·█▌▐█ ▀█ ██▪ ██ ▀▄.▀·▀▄ █·
▐█·▄█▀▀█     ▐█·▐█▐▐▌▐█▐█•▄█▀▀█ ▐█· ▐█▌▐▀▀▪▄▐▀▀▄ 
▐█▌▐█ ▪▐▌    ▐█▌██▐█▌ ███ ▐█ ▪▐▌██. ██ ▐█▄▄▌▐█•█▌
▀▀▀ ▀  ▀     ▀▀▀▀▀ █▪. ▀   ▀  ▀ ▀▀▀▀▀•  ▀▀▀ .▀  ▀
 Invader v2.1
""", # Versão atualizada
        "welcome": "Bem-vindo ao IA invader v2.1 - Seu Assistente de Segurança IA com Análise", # Nome e versão atualizados
        "separator": "-----------------------------------------------------------------",
        "usage": "Uso: Descreva sua tarefa de segurança (ex: 'escanear example.com com nmap -sV')",
        "options": "Opções: -h para ajuda | -v para versão | -lang para mudar idioma | -os para mudar SO",
        "help": (
            "\nUso:\n  <Descreva sua tarefa> (ex: 'verificar portas abertas em 192.168.1.1 com nmap')\n"
            "O IA invader irá gerar um comando, executá-lo (com confirmação),\n"
            "analisar a saída e sugerir ações de acompanhamento.\n"
            "Ferramentas suportadas dependem do seu sistema e do conhecimento do Ollama.\n"
            "Exemplos comuns: nmap, nikto, whois, ping, traceroute, dig, etc.\n"
            "Opções:\n"
            "  -h : Mostra esta mensagem de ajuda\n"
            "  -v : Mostra informações da versão\n"
            "  -lang : Muda o idioma da interface\n"
            "  -os : Muda o SO alvo para geração de comandos\n"
            "  exit : Sai da aplicação\n"
        ),
        "version": f"IA invader v2.1 - Alimentado por Ollama ({OLLAMA_MODEL})", # Versão atualizada
        "input": "\nIA invader> ",
        "thinking": "IA invader está pensando... 🤔",
        "interpreting": "IA invader está interpretando o comando... 🧐",
        "correcting": "IA invader está tentando corrigir o comando... 🛠️",
        "analyzing": "IA invader está analisando a saída... 🔬", # Nova mensagem
        "suggesting": "IA invader está sugerindo próximos passos... 👉", # Nova mensagem
        "ai_generated": "\n🤖 Comando Gerado pela IA:",
        "ai_interpreted": "🤖 Interpretação da IA:",
        "ai_corrected": "\n🤖 Sugestão de Correção da IA:",
        "ai_analysis": "\n📊 Análise da IA sobre a Saída:", # Nova mensagem
        "ai_followup": "\n💡 Sugestões da IA para Próximos Comandos:", # Nova mensagem
        "confirm": "Deseja executar este comando? (s/n): ",
        "execute": "🚀 Executando:",
        "ready": "\n✅ IA invader está pronto para o próximo comando! (Digite 'exit' para sair)\n",
        "cancel": "❌ Execução do comando cancelada pelo usuário.",
        "error_fetch": "🚫 Falha ao gerar comando via Ollama.",
        "error_interpret": "🚫 Falha ao obter interpretação do Ollama.",
        "error_correct": "🚫 Falha ao obter correção do Ollama.",
        "error_analyze": "🚫 Falha ao obter análise do Ollama.", # Nova mensagem
        "error_suggest": "🚫 Falha ao obter sugestões do Ollama.", # Nova mensagem
        "error_ollama_comm": "🚫 Erro ao comunicar com a API Ollama:",
        "error_ollama_conn": "🚫 Erro ao conectar à API Ollama. O Ollama está rodando?",
        "error_invalid_req": "🚫 A solicitação não parece traduzir-se num comando de shell válido.",
        "error_permission": "🚫 Permissão Negada: Não é possível executar o comando. Tente rodar o IA invader com privilégios de administrador/root se necessário.",
        "error_not_found": "🚫 Comando não encontrado:",
        "error_general": "🚫 Ocorreu um erro durante a execução:",
        "goodbye": "\n👋 Adeus!",
        "os_select": "Selecione o sistema operacional alvo para geração de comandos:",
        "os_options": "1. Linux\n2. Windows\n3. macOS\nEscolha (1/2/3): ",
        "lang_select": "Select language / Selecione o idioma:",
        "lang_options": "1. English\n2. Português\nChoice / Escolha (1/2): ",
        "auto_correct_q": "O comando falhou. Deseja pedir uma correção à IA? (s/n): ",
        "no_correction": "🤷 Nenhuma sugestão de comando alternativo pela IA.",
        "no_analysis": "🤷 A IA não pôde fornecer uma análise para esta saída.", # Nova mensagem
        "no_suggestions": "🤷 A IA não pôde fornecer sugestões de acompanhamento.", # Nova mensagem
        "tool_hint": "Dica:",
        "tool_hint_generic": "Certifique-se de que a ferramenta necessária está instalada e disponível no PATH do seu sistema.",
        "lang_set_by_arg": "Idioma definido para {lang} por argumento.",
        "proceed_q": "Prosseguir mesmo assim? (s/n): ",
    }
}

# --- Funções Auxiliares ---

def print_color(text: str, color_code: str):
    """Imprime texto em uma cor ANSI especificada."""
    print(f"{color_code}{text}\033[0m")

def select_language():
    """Permite ao usuário selecionar o idioma da interface."""
    global selected_lang, msg
    prompt_text = msg.get("lang_select", "Select language / Selecione o idioma:")
    options_text = msg.get("lang_options", "Choice / Escolha (1/2): ")

    print_color(prompt_text, "\033[96m") # Ciano
    print("1. English")
    print("2. Português")
    choice = input(options_text).strip()
    if choice == "2":
        selected_lang = "pt"
    else:
        selected_lang = "en"
    msg = LANGUAGES[selected_lang]
    print_color(f"Language set to {selected_lang.upper()}", "\033[92m") # Verde

def select_os():
    """Permite ao usuário selecionar o SO alvo para geração de comandos."""
    global selected_os
    print_color("\n" + msg["os_select"], "\033[96m") # Ciano
    choice = input(msg["os_options"]).strip()
    if choice == "2":
        selected_os = "windows"
    elif choice == "3":
        selected_os = "macos"
    else:
        selected_os = "linux"
    print_color(f"Target OS set to {selected_os.upper()}", "\033[92m") # Verde

def display_header():
    """Exibe o cabeçalho da aplicação e mensagens iniciais."""
    if not msg:
        print("Error: Message dictionary not initialized.")
        return
    print_color(msg["header"], "\033[95m") # Magenta
    print_color(msg["welcome"], "\033[92m") # Verde
    print(msg["separator"])
    print(msg["usage"])
    print(msg["options"])

def show_help():
    """Exibe a mensagem de ajuda."""
    print(msg["help"])

def show_version():
    """Exibe as informações de versão."""
    print(msg["version"])

def check_command_exists(command_name: str) -> bool:
    """Verifica se um comando existe no PATH do sistema."""
    return shutil.which(command_name) is not None

def get_missing_tool_hint(tool_name: str) -> str:
    """Fornece dicas de instalação para ferramentas conhecidas ausentes."""
    tool_name = tool_name.lower()
    if tool_name in DOWNLOAD_LINKS:
        os_data = DOWNLOAD_LINKS[tool_name].get(selected_os)
        if os_data:
            link = os_data.get("link", "")
            instructions = os_data["instructions"].get(selected_lang, msg["tool_hint_generic"])
            hint = f"{instructions}"
            if link:
                hint += f" (Link: {link})"
            return hint
    return msg["tool_hint_generic"]

def show_spinner(message: str):
    """Exibe um spinner animado no terminal."""
    global spinner_running
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    frame_cycle = cycle(frames)
    while spinner_running:
        sys.stderr.write(f"\r\033[96m{next(frame_cycle)} {message}\033[0m") # Ciano
        sys.stderr.flush()
        time.sleep(0.1)
    sys.stderr.write("\r" + " " * (len(message) + 5) + "\r")
    sys.stderr.flush()

def start_spinner(message: str) -> Thread:
    """Inicia a animação do spinner em uma thread separada."""
    global spinner_running
    spinner_running = True
    spinner_thread = Thread(target=show_spinner, args=(message,), daemon=True)
    spinner_thread.start()
    return spinner_thread

def stop_spinner(spinner_thread: Thread):
    """Para a thread de animação do spinner."""
    global spinner_running
    spinner_running = False
    spinner_thread.join(timeout=0.5)

# --- Interação com Ollama ---

def _ollama_request(prompt: str, operation_desc_key: str) -> Optional[str]:
    """Envia uma requisição para a API Ollama e trata erros básicos."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    spinner_message = msg.get(operation_desc_key, "Processing...")
    spinner_thread = start_spinner(spinner_message)
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        response_data = response.json()
        result = response_data.get('response', '').strip()
        result = result.removeprefix("```bash").removeprefix("```").removesuffix("```")
        result = result.strip('`"\'\n ')
        # Retorna None se o resultado for explicitamente vazio após limpeza,
        # indicando que a IA pode não ter tido nada a dizer.
        return result if result else None
    except requests.exceptions.ConnectionError:
        print_color(f"\n{msg.get('error_ollama_conn', 'Connection Error')}", "\033[91m")
        return None
    except requests.exceptions.Timeout:
        timeout_msg = msg.get('error_ollama_comm', 'Communication Error:') + f" Request timed out after {REQUEST_TIMEOUT} seconds."
        print_color(f"\n{timeout_msg}", "\033[91m")
        return None
    except requests.exceptions.RequestException as e:
        comm_error_msg = msg.get('error_ollama_comm', 'Communication Error:')
        print_color(f"\n{comm_error_msg} {e}", "\033[91m")
        return None
    finally:
        stop_spinner(spinner_thread)


def ask_ollama_for_command(user_request: str) -> Optional[str]:
    """Pede ao Ollama para gerar um comando shell."""
    prompt = (
        f"You are an expert system command generator. Your task is to convert the user's natural language request "
        f"into a *single*, *valid*, and *directly executable* shell command for the specified operating system. "
        f"Target OS: {selected_os.upper()}\n"
        f"User's Language (for context, not output): {selected_lang.upper()}\n"
        f"User Request: \"{user_request}\"\n\n"
        f"Constraints:\n"
        f"- Output *only* the raw shell command. No explanations, comments, apologies, or introductory phrases.\n"
        f"- Do not use placeholders like '<target>' unless the user explicitly used one.\n"
        f"- Ensure the command syntax is correct for the target OS ({selected_os}).\n"
        f"- If the request is ambiguous, make a reasonable assumption based on common security/networking tasks.\n"
        f"- If the request cannot be translated into a single shell command or is nonsensical, output the exact string: 'invalid-request'.\n\n"
        f"Generated Command:"
    )
    command = _ollama_request(prompt, "thinking")

    if command == "invalid-request":
        print_color(f"\n{msg['error_invalid_req']}", "\033[91m")
        return None
    elif not command:
        print_color(f"\n{msg['error_fetch']}", "\033[91m")
        return None
    return command

def ask_ollama_for_interpretation(user_request: str, command: str) -> str:
    """Pede ao Ollama para explicar o comando gerado."""
    lang_name = "English"
    if selected_lang in LANGUAGES and 'welcome' in LANGUAGES[selected_lang]:
         try:
             lang_name = LANGUAGES[selected_lang]['welcome'].split(' to ')[1].split(' v')[0]
         except IndexError:
              try:
                  lang_name = LANGUAGES[selected_lang]['welcome'].split()[1]
              except IndexError:
                  pass

    prompt = (
        f"You are a helpful assistant explaining shell commands.\n"
        f"Target OS: {selected_os.upper()}\n"
        f"User's Language (for explanation): {selected_lang.upper()}\n"
        f"Original User Request: \"{user_request}\"\n"
        f"Generated Command: `{command}`\n\n"
        f"Task: Provide a concise explanation (2-3 sentences max) in {lang_name} of what this command does, focusing on its main purpose and key flags/options.\n\n"
        f"Explanation:"
    )
    explanation = _ollama_request(prompt, "interpreting")
    return explanation if explanation else ""

def ask_ollama_for_correction(user_request: str, original_command: str, error_output: str) -> Optional[str]:
    """Pede ao Ollama para sugerir um comando corrigido."""
    prompt = (
        f"You are an expert system command corrector. A user tried to execute a command based on their request, but it failed.\n"
        f"Target OS: {selected_os.upper()}\n"
        f"User's Language (for context): {selected_lang.upper()}\n"
        f"Original User Request: \"{user_request}\"\n"
        f"Command That Failed: `{original_command}`\n"
        f"Error Output Received:\n---\n{error_output}\n---\n\n"
        f"Task: Analyze the error and the original command. Provide a *corrected*, *single*, *directly executable* shell command "
        f"that addresses the likely cause of the error and achieves the user's original intent on the target OS. \n"
        f"Constraints:\n"
        f"- Output *only* the raw corrected shell command. No explanations or extra text.\n"
        f"- If you cannot determine a reasonable correction or the error is too vague, output the exact string: 'no-suggestion'.\n\n"
        f"Corrected Command:"
    )
    corrected_command = _ollama_request(prompt, "correcting")

    if corrected_command == "no-suggestion":
        print_color(f"\n{msg['no_correction']}", "\033[93m")
        return None
    elif not corrected_command:
         print_color(f"\n{msg['error_correct']}", "\033[91m")
         return None
    return corrected_command

def ask_ollama_for_analysis(user_request: str, command: str, stdout: str, stderr: str) -> Optional[str]:
    """Pede ao Ollama para analisar a saída do comando."""
    # Limita o tamanho da saída enviada para análise para evitar prompts excessivamente longos
    max_output_len = 2000 # Ajuste conforme necessário
    truncated_stdout = stdout[:max_output_len] + ("..." if len(stdout) > max_output_len else "")
    truncated_stderr = stderr[:max_output_len] + ("..." if len(stderr) > max_output_len else "")

    if not truncated_stdout and not truncated_stderr:
        return msg.get("no_analysis", "No output to analyze.") # Não há nada para analisar

    prompt = (
        f"You are a security analysis assistant. A command was executed based on a user request. Analyze the output.\n"
        f"Target OS: {selected_os.upper()}\n"
        f"User's Language (for analysis summary): {selected_lang.upper()}\n"
        f"Original User Request: \"{user_request}\"\n"
        f"Executed Command: `{command}`\n"
        f"Standard Output (stdout):\n---\n{truncated_stdout}\n---\n"
        f"Standard Error (stderr):\n---\n{truncated_stderr}\n---\n\n"
        f"Task: Provide a brief analysis in {selected_lang.upper()} focusing on:\n"
        f"1. Key findings or results relevant to the user's request.\n"
        f"2. Any potential security issues, open ports, vulnerabilities, or interesting information discovered (if applicable).\n"
        f"3. A concise summary (2-4 bullet points or a short paragraph).\n"
        f"If the output is uninformative or just shows an error already handled, state that briefly.\n\n"
        f"Analysis:"
    )
    analysis = _ollama_request(prompt, "analyzing")

    if not analysis:
        print_color(f"\n{msg.get('no_analysis', 'AI could not provide an analysis.')}", "\033[93m") # Amarelo
        return None
    return analysis

def ask_ollama_for_followup(user_request: str, command: str, stdout: str, stderr: str, analysis: Optional[str]) -> Optional[List[str]]:
    """Pede ao Ollama para sugerir comandos de acompanhamento."""
    max_output_len = 1500 # Limita a saída para o prompt de acompanhamento
    truncated_stdout = stdout[:max_output_len] + ("..." if len(stdout) > max_output_len else "")
    truncated_stderr = stderr[:max_output_len] + ("..." if len(stderr) > max_output_len else "")

    analysis_context = f"Previous Analysis Summary:\n---\n{analysis}\n---\n" if analysis else "No previous analysis available.\n"

    prompt = (
        f"You are a security workflow assistant. Based on the previous command execution and its results (and analysis if available), suggest relevant next steps.\n"
        f"Target OS: {selected_os.upper()}\n"
        f"User's Language (for context): {selected_lang.upper()}\n"
        f"Original User Request: \"{user_request}\"\n"
        f"Executed Command: `{command}`\n"
        f"Standard Output (stdout):\n---\n{truncated_stdout}\n---\n"
        f"Standard Error (stderr):\n---\n{truncated_stderr}\n---\n"
        f"{analysis_context}"
        f"Task: Suggest 1 to 3 relevant follow-up shell commands for the target OS ({selected_os}) that would logically follow from these results. Examples: deeper scans, vulnerability checks, service enumeration, information gathering.\n"
        f"Constraints:\n"
        f"- Output *only* the raw suggested shell commands, each on a new line.\n"
        f"- Do not include explanations, numbering, or any text other than the commands.\n"
        f"- If no logical follow-up command comes to mind, output the exact string: 'no-suggestion'.\n\n"
        f"Suggested Follow-up Commands:"
    )
    suggestions_raw = _ollama_request(prompt, "suggesting")

    if not suggestions_raw or suggestions_raw == "no-suggestion":
        print_color(f"\n{msg.get('no_suggestions', 'AI could not provide follow-up suggestions.')}", "\033[93m") # Amarelo
        return None

    # Divide as sugestões em uma lista, removendo linhas vazias
    suggestions = [cmd.strip() for cmd in suggestions_raw.split('\n') if cmd.strip()]

    if not suggestions:
        print_color(f"\n{msg.get('no_suggestions', 'AI could not provide follow-up suggestions.')}", "\033[93m") # Amarelo
        return None

    return suggestions


# --- Execução de Comando ---

def run_command(command: str) -> Tuple[int, str, str]:
    """
    Executa o comando shell e captura sua saída. Retorna (código_retorno, stdout, stderr).
    """
    print_color(f"{msg['execute']} {command}", "\033[92m") # Verde
    tool_name_for_spinner = command.split()[0] if command else "command"
    spinner_thread = start_spinner(f"Running '{tool_name_for_spinner}'...")

    stdout_lines: List[str] = []
    stderr_lines: List[str] = []
    process = None

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Captura stdout e stderr
        stdout, stderr = process.communicate()
        return_code = process.returncode

        # Imprime a saída após a conclusão
        if stdout:
            print("\n--- Output ---")
            print(stdout)
            print("--------------")
        if stderr:
            print("\n--- Error Output ---")
            print_color(stderr, "\033[91m") # Vermelho
            print("--------------------")


    except FileNotFoundError:
        stop_spinner(spinner_thread)
        tool_name = command.split()[0] if command else "Command"
        print_color(f"\n{msg['error_not_found']} '{tool_name}'", "\033[91m")
        print_color(f"{msg['tool_hint']} {get_missing_tool_hint(tool_name)}", "\033[93m")
        return -1, "", f"{tool_name}: command not found"
    except PermissionError:
        stop_spinner(spinner_thread)
        print_color(f"\n{msg['error_permission']}", "\033[91m")
        return -2, "", "Permission denied"
    except Exception as e:
        stop_spinner(spinner_thread)
        print_color(f"\n{msg['error_general']} {e}", "\033[91m")
        if process and process.poll() is None:
            process.terminate()
            process.wait()
        return -3, "", str(e)
    finally:
        if 'spinner_thread' in locals() and spinner_thread.is_alive():
             stop_spinner(spinner_thread)
        # Não feche stdout/stderr aqui se usar communicate()

    # Garante que stdout e stderr sejam strings
    stdout = stdout or ""
    stderr = stderr or ""

    # Lógica de erro aprimorada
    if return_code != 0 and not stderr:
        stderr = f"Command exited with status {return_code}"

    if return_code != 0 and stderr:
        stderr_lower = stderr.lower()
        tool_name = command.split()[0] if command else "Command"
        if "command not found" in stderr_lower or \
           "não é reconhecido" in stderr_lower or \
           "not recognized" in stderr_lower or \
           "no such file or directory" in stderr_lower:
            print_color(f"{msg['tool_hint']} {get_missing_tool_hint(tool_name)}", "\033[93m")

    return return_code, stdout, stderr


def confirm_and_execute(user_request: str, command: str, is_correction: bool = False):
    """Trata confirmação, execução, análise, sugestão e correção."""

    explanation = ask_ollama_for_interpretation(user_request, command)

    print_color(msg['ai_generated'] if not is_correction else msg['ai_corrected'], "\033[94m") # Azul
    print_color(command, "\033[93m") # Amarelo

    if explanation:
        print_color("\n" + msg["ai_interpreted"], "\033[94m") # Azul
        print_color(explanation, "\033[92m") # Verde

    # Confirmação
    confirm_prompt = "\033[96m" + msg["confirm"] + "\033[0m" # Ciano
    user_confirm = input(confirm_prompt).strip().lower()
    should_execute = user_confirm == 's' if selected_lang == "pt" else user_confirm == 'y'

    if not should_execute:
        print_color(msg["cancel"], "\033[91m") # Vermelho
        return # Para se o usuário cancelar

    # Execução
    ret_code, stdout, stderr = run_command(command)

    # Análise e Sugestões (mesmo se houver erro, a saída pode ser útil)
    analysis = None
    if stdout or stderr: # Tenta analisar se houver qualquer saída
        analysis = ask_ollama_for_analysis(user_request, command, stdout, stderr)
        if analysis:
            print_color(msg["ai_analysis"], "\033[94m") # Azul
            print_color(analysis, "\033[92m") # Verde
        # else: Mensagem de "sem análise" já foi impressa

        suggestions = ask_ollama_for_followup(user_request, command, stdout, stderr, analysis)
        if suggestions:
            print_color(msg["ai_followup"], "\033[94m") # Azul
            for i, sug_cmd in enumerate(suggestions):
                print_color(f"  {i+1}. {sug_cmd}", "\033[93m") # Amarelo
        # else: Mensagem de "sem sugestões" já foi impressa

    # Tratamento de Erro e Correção
    if ret_code != 0:
        print_color(f"\nCommand failed with exit code {ret_code}.", "\033[91m") # Vermelho
        if stderr and not is_correction: # Oferece correção na primeira falha com saída de erro
            correction_q_prompt = "\033[96m" + msg["auto_correct_q"] + "\033[0m" # Ciano
            user_wants_correction = input(correction_q_prompt).strip().lower()
            should_correct = (user_wants_correction == 'y' and selected_lang == "en") or \
                             (user_wants_correction == 's' and selected_lang == "pt")

            if should_correct:
                corrected_command = ask_ollama_for_correction(user_request, command, stderr) # Usa stderr para correção
                if corrected_command:
                    # Chama recursivamente para confirmar e executar o comando *corrigido*
                    # Note: A análise/sugestão ocorrerá novamente para o comando corrigido
                    confirm_and_execute(user_request, corrected_command, is_correction=True)
                # else: AI não pôde sugerir correção

# --- Lógica Principal da Aplicação ---

def main():
    """Função principal para rodar a aplicação IA invader."""
    global msg, selected_lang, selected_os

    # Tratamento de argumentos de linha de comando
    lang_overridden_by_arg = False
    if len(sys.argv) > 1:
        if "-lang=pt" in sys.argv:
            selected_lang = "pt"
            msg = LANGUAGES[selected_lang]
            lang_overridden_by_arg = True
            lang_set_msg = msg.get("lang_set_by_arg", "Language set to {lang} by argument.").format(lang=selected_lang.upper())
            print_color(lang_set_msg, "\033[92m")
        elif "-lang=en" in sys.argv:
             selected_lang = "en"
             msg = LANGUAGES[selected_lang]
             lang_overridden_by_arg = True
             lang_set_msg = msg.get("lang_set_by_arg", "Language set to {lang} by argument.").format(lang=selected_lang.upper())
             print_color(lang_set_msg, "\033[92m")

    # Seleções iniciais se não definidas por args
    if not lang_overridden_by_arg:
        select_language()

    select_os()
    display_header()

    # --- Loop Principal ---
    while True:
        try:
            user_input = input(msg["input"]).strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                break
            elif user_input == "-h":
                show_help()
                continue
            elif user_input == "-v":
                show_version()
                continue
            elif user_input == "-lang":
                select_language()
                display_header()
                continue
            elif user_input == "-os":
                select_os()
                continue

            # --- Fluxo de Trabalho Principal ---
            command = ask_ollama_for_command(user_input)

            if command:
                tool_name = command.split()[0] if command else ""
                proceed_anyway = True # Assume que prossegue por padrão
                if tool_name and '/' not in tool_name and '\\' not in tool_name:
                    if not check_command_exists(tool_name):
                        warn_msg = msg.get("error_not_found", "Command not found:") + f" '{tool_name}' (might not be installed or in PATH)."
                        print_color(f"\nWarning: {warn_msg}", "\033[93m")
                        print_color(f"{msg['tool_hint']} {get_missing_tool_hint(tool_name)}", "\033[93m")
                        proceed_prompt = msg.get("proceed_q", "Proceed anyway? (y/n): ")
                        proceed = input(proceed_prompt).strip().lower()
                        should_proceed = proceed == 's' if selected_lang == "pt" else proceed == 'y'
                        if not should_proceed:
                            print_color(msg["cancel"], "\033[91m")
                            proceed_anyway = False # Marca para não prosseguir

                if proceed_anyway:
                    confirm_and_execute(user_input, command)

            print_color(msg["ready"], "\033[92m") # Verde

        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            error_msg = msg.get("error_general", "An unexpected error occurred:")
            print_color(f"\n{error_msg} {e}", "\033[91m")
            traceback.print_exc()
            time.sleep(1)

    goodbye_msg = msg.get("goodbye", "\n👋 Goodbye!")
    print_color(goodbye_msg, "\033[92m")

if __name__ == "__main__":
    main()
