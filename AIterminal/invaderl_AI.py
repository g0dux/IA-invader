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
REQUEST_TIMEOUT: int = 60 # Timeout para requisições Ollama em segundos

# --- Estado Global ---
spinner_running: bool = False
selected_lang: str = "en" # Idioma padrão
selected_os: str = "linux" # SO padrão
msg: Dict[str, Any] = {} # Dicionário para mensagens específicas do idioma

# --- Constantes ---
# Dicionário com links e instruções de instalação para ferramentas conhecidas.
# Adicionadas mais ferramentas e instruções refinadas.
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
         "macos": { # Exemplo de suporte para macOS adicionado
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
    "ip": { # Específico para Linux geralmente
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
            "link": "", # Geralmente instalado via gerenciador de pacotes
            "instructions": {
                "en": "'whois' not found. Install it using your package manager (e.g., 'sudo apt install whois' or 'sudo dnf install whois').",
                "pt": "'whois' não encontrado. Instale usando seu gerenciador de pacotes (ex.: 'sudo apt install whois' ou 'sudo dnf install whois')."
            }
        },
        "macos": {
            "link": "", # Geralmente pré-instalado ou via brew
            "instructions": {
                "en": "'whois' not found. It might be pre-installed. If not, try 'brew install whois'.",
                "pt": "'whois' não encontrado. Pode estar pré-instalado. Se não, tente 'brew install whois'."
            }
        }
    }
    # Adicione mais ferramentas conforme necessário
}

# Dicionário de mensagens multilíngues
LANGUAGES: Dict[str, Dict[str, Any]] = {
    "en": {
        "header": r"""
 _   _       _           _ _   _       _      _ _     _
| | | | __ _| |__   __ _| | | | |_ __ (_) ___| (_) __| |
| |_| |/ _` | '_ \ / _` | | | | | '_ \| |/ __| | |/ _` |
|  _  | (_| | | | | (_| | | | | | |_) | | (__| | | (_| |
|_| |_|\__,_|_| |_|\__,_|_|_| |_| .__/|_|\___|_|_|\__,_|
                                |_| AI v2.0
""", # Arte ASCII atualizada ligeiramente
        "welcome": "Welcome to HackerAI v2 - Your Enhanced Local AI Security Assistant",
        "separator": "-----------------------------------------------------------------",
        "usage": "Usage: Enter your security task (e.g., 'scan example.com with nmap -sV')",
        "options": "Options: -h for help | -v for version | -lang to change language | -os to change OS",
        "help": (
            "\nUsage:\n  <Describe your task> (e.g., 'check open ports on 192.168.1.1 with nmap')\n"
            "Supported tools depend on your system and Ollama's knowledge.\n"
            "Common examples: nmap, nikto, whois, ping, traceroute, dig, etc.\n"
            "Options:\n"
            "  -h : Show this help message\n"
            "  -v : Show version info\n"
            "  -lang : Change interface language\n"
            "  -os : Change target OS for command generation\n"
            "  exit : Quit the application\n"
        ),
        "version": f"HackerAI v2.0 - Powered by Ollama ({OLLAMA_MODEL})",
        "input": "\nHackerAI> ",
        "thinking": "HackerAI is thinking... 🤔",
        "interpreting": "HackerAI is interpreting the command... 🧐",
        "correcting": "HackerAI is attempting to correct the command... 🛠️",
        "ai_generated": "\n🤖 AI Generated Command:",
        "ai_interpreted": "🤖 AI Interpretation:",
        "ai_corrected": "\n🤖 AI Corrected Command Suggestion:",
        "confirm": "Do you want to execute this command? (y/n): ",
        "execute": "🚀 Executing:",
        "ready": "\n✅ HackerAI is ready for your next command! (Type 'exit' to quit)\n",
        "cancel": "❌ Command execution canceled by the user.",
        "error_fetch": "🚫 Failed to generate command via Ollama.",
        "error_interpret": "🚫 Failed to get interpretation from Ollama.",
        "error_correct": "🚫 Failed to get correction from Ollama.",
        "error_ollama_comm": "🚫 Error communicating with Ollama API:",
        "error_ollama_conn": "🚫 Error connecting to Ollama API. Is Ollama running?",
        "error_invalid_req": "🚫 The request doesn't seem to translate into a valid shell command.",
        "error_permission": "🚫 Permission Denied: Cannot execute the command. Try running HackerAI with administrator/root privileges if necessary.",
        "error_not_found": "🚫 Command not found:",
        "error_general": "🚫 An error occurred during execution:",
        "goodbye": "\n👋 Goodbye!",
        "os_select": "Select the target operating system for command generation:",
        "os_options": "1. Linux\n2. Windows\n3. macOS\nChoice (1/2/3): ",
        "lang_select": "Select language / Selecione o idioma:",
        "lang_options": "1. English\n2. Português\nChoice / Escolha (1/2): ",
        "auto_correct_q": "The command failed. Would you like to ask the AI for a correction? (y/n): ",
        "no_correction": "🤷 No alternative command suggested by AI.",
        "tool_hint": "Hint:",
        "tool_hint_generic": "Ensure the required tool is installed and available in your system's PATH.",
        "lang_set_by_arg": "Language set to {lang} by argument.", # Nova mensagem
        "proceed_q": "Proceed anyway? (y/n): ", # Nova mensagem
    },
    "pt": {
        "header": r"""
 _   _       _           _ _   _       _      _ _     _
| | | | __ _| |__   __ _| | | | |_ __ (_) ___| (_) __| |
| |_| |/ _` | '_ \ / _` | | | | | '_ \| |/ __| | |/ _` |
|  _  | (_| | | | | (_| | | | | | |_) | | (__| | | (_| |
|_| |_|\__,_|_| |_|\__,_|_|_| |_| .__/|_|\___|_|_|\__,_|
                                |_| AI v2.0
""",
        "welcome": "Bem-vindo ao HackerAI v2 - Seu Assistente de Segurança Local com IA Aprimorado",
        "separator": "-----------------------------------------------------------------",
        "usage": "Uso: Descreva sua tarefa de segurança (ex: 'escanear example.com com nmap -sV')",
        "options": "Opções: -h para ajuda | -v para versão | -lang para mudar idioma | -os para mudar SO",
        "help": (
            "\nUso:\n  <Descreva sua tarefa> (ex: 'verificar portas abertas em 192.168.1.1 com nmap')\n"
            "Ferramentas suportadas dependem do seu sistema e do conhecimento do Ollama.\n"
            "Exemplos comuns: nmap, nikto, whois, ping, traceroute, dig, etc.\n"
            "Opções:\n"
            "  -h : Mostra esta mensagem de ajuda\n"
            "  -v : Mostra informações da versão\n"
            "  -lang : Muda o idioma da interface\n"
            "  -os : Muda o SO alvo para geração de comandos\n"
            "  exit : Sai da aplicação\n"
        ),
        "version": f"HackerAI v2.0 - Alimentado por Ollama ({OLLAMA_MODEL})",
        "input": "\nHackerAI> ",
        "thinking": "HackerAI está pensando... 🤔",
        "interpreting": "HackerAI está interpretando o comando... 🧐",
        "correcting": "HackerAI está tentando corrigir o comando... 🛠️",
        "ai_generated": "\n🤖 Comando Gerado pela IA:",
        "ai_interpreted": "🤖 Interpretação da IA:",
        "ai_corrected": "\n🤖 Sugestão de Correção da IA:",
        "confirm": "Deseja executar este comando? (s/n): ",
        "execute": "🚀 Executando:",
        "ready": "\n✅ HackerAI está pronto para o próximo comando! (Digite 'exit' para sair)\n",
        "cancel": "❌ Execução do comando cancelada pelo usuário.",
        "error_fetch": "🚫 Falha ao gerar comando via Ollama.",
        "error_interpret": "🚫 Falha ao obter interpretação do Ollama.",
        "error_correct": "🚫 Falha ao obter correção do Ollama.",
        "error_ollama_comm": "🚫 Erro ao comunicar com a API Ollama:",
        "error_ollama_conn": "🚫 Erro ao conectar à API Ollama. O Ollama está rodando?",
        "error_invalid_req": "🚫 A solicitação não parece traduzir-se num comando de shell válido.",
        "error_permission": "🚫 Permissão Negada: Não é possível executar o comando. Tente rodar o HackerAI com privilégios de administrador/root se necessário.",
        "error_not_found": "🚫 Comando não encontrado:",
        "error_general": "🚫 Ocorreu um erro durante a execução:",
        "goodbye": "\n👋 Adeus!",
        "os_select": "Selecione o sistema operacional alvo para geração de comandos:",
        "os_options": "1. Linux\n2. Windows\n3. macOS\nEscolha (1/2/3): ",
        "lang_select": "Select language / Selecione o idioma:",
        "lang_options": "1. English\n2. Português\nChoice / Escolha (1/2): ",
        "auto_correct_q": "O comando falhou. Deseja pedir uma correção à IA? (s/n): ",
        "no_correction": "🤷 Nenhuma sugestão de comando alternativo pela IA.",
        "tool_hint": "Dica:",
        "tool_hint_generic": "Certifique-se de que a ferramenta necessária está instalada e disponível no PATH do seu sistema.",
        "lang_set_by_arg": "Idioma definido para {lang} por argumento.", # Nova mensagem
        "proceed_q": "Prosseguir mesmo assim? (s/n): ", # Nova mensagem
    }
}

# --- Funções Auxiliares ---

def print_color(text: str, color_code: str):
    """Imprime texto em uma cor ANSI especificada."""
    print(f"{color_code}{text}\033[0m")

def select_language():
    """Permite ao usuário selecionar o idioma da interface."""
    global selected_lang, msg
    # Usa msg.get para evitar erro se msg ainda não estiver totalmente inicializado
    prompt_text = msg.get("lang_select", "Select language / Selecione o idioma:")
    options_text = msg.get("lang_options", "Choice / Escolha (1/2): ")

    print_color(prompt_text, "\033[96m") # Ciano
    print("1. English")
    print("2. Português")
    choice = input(options_text).strip()
    if choice == "2":
        selected_lang = "pt"
    else:
        selected_lang = "en" # Padrão para Inglês
    # Atualiza o dicionário global msg AGORA que selected_lang está definido
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
        selected_os = "linux" # Padrão para Linux
    print_color(f"Target OS set to {selected_os.upper()}", "\033[92m") # Verde

def display_header():
    """Exibe o cabeçalho da aplicação e mensagens iniciais."""
    # Garante que msg está definido antes de chamar esta função
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
    # Frames de spinner modernos Unicode Braille
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    frame_cycle = cycle(frames)
    while spinner_running:
        # Usa stderr para evitar interferir com o pipe stdout do comando
        sys.stderr.write(f"\r\033[96m{next(frame_cycle)} {message}\033[0m") # Ciano
        sys.stderr.flush()
        time.sleep(0.1)
    # Limpa a linha do spinner
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
    spinner_thread.join(timeout=0.5) # Dá um momento para a thread terminar

# --- Interação com Ollama ---

def _ollama_request(prompt: str, operation_desc_key: str) -> Optional[str]:
    """Envia uma requisição para a API Ollama e trata erros básicos."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    # Usa msg.get com um fallback caso msg não esteja pronto
    spinner_message = msg.get(operation_desc_key, "Processing...")
    spinner_thread = start_spinner(spinner_message)
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # Levanta HTTPError para respostas ruins (4xx ou 5xx)
        response_data = response.json()
        result = response_data.get('response', '').strip()
        # Limpa potenciais blocos de código markdown ou aspas
        result = result.removeprefix("```bash").removeprefix("```").removesuffix("```")
        result = result.strip('`"\'\n ')
        return result
    except requests.exceptions.ConnectionError:
        print_color(f"\n{msg.get('error_ollama_conn', 'Connection Error')}", "\033[91m") # Vermelho
        return None
    except requests.exceptions.Timeout:
        timeout_msg = msg.get('error_ollama_comm', 'Communication Error:') + f" Request timed out after {REQUEST_TIMEOUT} seconds."
        print_color(f"\n{timeout_msg}", "\033[91m") # Vermelho
        return None
    except requests.exceptions.RequestException as e:
        comm_error_msg = msg.get('error_ollama_comm', 'Communication Error:')
        print_color(f"\n{comm_error_msg} {e}", "\033[91m") # Vermelho
        return None
    finally:
        stop_spinner(spinner_thread)


def ask_ollama_for_command(user_request: str) -> Optional[str]:
    """Pede ao Ollama para gerar um comando shell baseado na requisição do usuário."""
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
        print_color(f"\n{msg['error_invalid_req']}", "\033[91m") # Vermelho
        return None
    elif not command:
        print_color(f"\n{msg['error_fetch']}", "\033[91m") # Vermelho
        return None

    return command

def ask_ollama_for_interpretation(user_request: str, command: str) -> str:
    """Pede ao Ollama para explicar o comando gerado."""
    # Tenta obter o nome do idioma de forma mais segura
    lang_name = "English" # Fallback
    if selected_lang in LANGUAGES and 'welcome' in LANGUAGES[selected_lang]:
         try:
             lang_name = LANGUAGES[selected_lang]['welcome'].split()[1]
         except IndexError:
             pass # Mantém o fallback se a divisão falhar

    prompt = (
        f"You are a helpful assistant explaining shell commands. The user wants to perform a task and you generated a command.\n"
        f"Target OS: {selected_os.upper()}\n"
        f"User's Language (for explanation): {selected_lang.upper()}\n"
        f"Original User Request: \"{user_request}\"\n"
        f"Generated Command: `{command}`\n\n"
        f"Task: Provide a concise explanation of what this command does, focusing on its main purpose and key flags/options. "
        f"Explain it in {lang_name}. Keep it brief (2-3 sentences max).\n\n"
        f"Explanation:"
    )
    explanation = _ollama_request(prompt, "interpreting")
    return explanation if explanation else ""

def ask_ollama_for_correction(user_request: str, original_command: str, error_output: str) -> Optional[str]:
    """Pede ao Ollama para sugerir um comando corrigido baseado em um erro."""
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
        print_color(f"\n{msg['no_correction']}", "\033[93m") # Amarelo
        return None
    elif not corrected_command:
         print_color(f"\n{msg['error_correct']}", "\033[91m") # Vermelho
         return None

    return corrected_command

# --- Execução de Comando ---

def run_command(command: str) -> Tuple[int, str, str]:
    """
    Executa o comando shell e captura sua saída.

    Retorna:
        Tuple[int, str, str]: (return_code, stdout, stderr)
    """
    print_color(f"{msg['execute']} {command}", "\033[92m") # Verde
    # Tenta obter o nome da ferramenta de forma mais segura
    tool_name_for_spinner = command.split()[0] if command else "command"
    spinner_thread = start_spinner(f"Running '{tool_name_for_spinner}'...")

    stdout_lines: List[str] = []
    stderr_lines: List[str] = []
    process = None # Inicializa o processo como None

    try:
        # Usa Popen para streaming de saída em tempo real (opcional, mas bom para comandos longos)
        process = subprocess.Popen(
            command,
            shell=True, # Tenha cuidado com shell=True
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8', # Define explicitamente a codificação
            errors='replace' # Trata potenciais erros de decodificação
        )

        # Lê stdout e stderr linha por linha
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line, end='') # Imprime a linha stdout imediatamente
                stdout_lines.append(line)
        if process.stderr:
             for line in iter(process.stderr.readline, ''):
                print_color(line, "\033[91m") # Imprime a linha stderr imediatamente em vermelho
                stderr_lines.append(line)

        process.wait() # Espera o processo completar
        return_code = process.returncode

    except FileNotFoundError:
        # Captura se o próprio comando não for encontrado
        stop_spinner(spinner_thread)
        tool_name = command.split()[0] if command else "Command"
        print_color(f"\n{msg['error_not_found']} '{tool_name}'", "\033[91m") # Vermelho
        print_color(f"{msg['tool_hint']} {get_missing_tool_hint(tool_name)}", "\033[93m") # Amarelo
        return -1, "", f"{tool_name}: command not found" # Simula código de retorno e stderr
    except PermissionError:
        stop_spinner(spinner_thread)
        print_color(f"\n{msg['error_permission']}", "\033[91m") # Vermelho
        return -2, "", "Permission denied" # Simula código de retorno e stderr
    except Exception as e:
        stop_spinner(spinner_thread)
        print_color(f"\n{msg['error_general']} {e}", "\033[91m") # Vermelho
        # Garante que o processo seja terminado se existir e ainda estiver rodando
        if process and process.poll() is None:
            process.terminate()
            process.wait()
        return -3, "", str(e) # Simula código de retorno e stderr
    finally:
        # Garante que o spinner pare mesmo se ocorrerem exceções
        if 'spinner_thread' in locals() and spinner_thread.is_alive():
             stop_spinner(spinner_thread)
        # Garante que os streams do processo sejam fechados se o processo foi criado
        if process:
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()


    stdout = "".join(stdout_lines)
    stderr = "".join(stderr_lines)

    # Verifica stderr para padrões de erro comuns mesmo se o código de retorno for 0 (algumas ferramentas reportam erros para stderr)
    if return_code != 0 and not stderr: # Se código de erro mas sem stderr, fornece mensagem genérica
        stderr = f"Command exited with status {return_code}"

    if return_code != 0 and stderr:
         # Verifica variações de 'command not found' de forma mais robusta
        stderr_lower = stderr.lower()
        tool_name = command.split()[0] if command else "Command"
        if "command not found" in stderr_lower or \
           "não é reconhecido" in stderr_lower or \
           "not recognized" in stderr_lower or \
           "no such file or directory" in stderr_lower:
            print_color(f"{msg['tool_hint']} {get_missing_tool_hint(tool_name)}", "\033[93m") # Amarelo

    return return_code, stdout, stderr


def confirm_and_execute(user_request: str, command: str, is_correction: bool = False):
    """Trata confirmação, execução e loop de correção potencial."""

    explanation = ask_ollama_for_interpretation(user_request, command)

    print_color(msg['ai_generated'] if not is_correction else msg['ai_corrected'], "\033[94m") # Azul
    print_color(command, "\033[93m") # Texto do comando em amarelo

    if explanation:
        print_color("\n" + msg["ai_interpreted"], "\033[94m") # Azul
        print_color(explanation, "\033[92m") # Texto da explicação em verde

    # Confirmação
    confirm_prompt = "\033[96m" + msg["confirm"] + "\033[0m" # Prompt em ciano
    user_confirm = input(confirm_prompt).strip().lower()
    should_execute = user_confirm == 's' if selected_lang == "pt" else user_confirm == 'y'

    if not should_execute:
        print_color(msg["cancel"], "\033[91m") # Vermelho
        return # Para se o usuário cancelar

    # Execução
    ret_code, _, err_output = run_command(command)

    # Trata falha potencial e auto-correção
    if ret_code != 0:
        print_color(f"\nCommand failed with exit code {ret_code}.", "\033[91m") # Vermelho
        if err_output and not is_correction: # Oferece correção apenas na *primeira* falha
            correction_q_prompt = "\033[96m" + msg["auto_correct_q"] + "\033[0m" # Prompt em ciano
            user_wants_correction = input(correction_q_prompt).strip().lower()
            should_correct = (user_wants_correction == 'y' and selected_lang == "en") or \
                             (user_wants_correction == 's' and selected_lang == "pt")

            if should_correct:
                corrected_command = ask_ollama_for_correction(user_request, command, err_output)
                if corrected_command:
                    # Chama recursivamente para confirmar e executar o comando *corrigido*
                    confirm_and_execute(user_request, corrected_command, is_correction=True)
                # else: IA não pôde sugerir uma correção (mensagem já impressa por ask_ollama_for_correction)

# --- Lógica Principal da Aplicação ---

def main():
    """Função principal para rodar a aplicação HackerAI."""
    # Declara globais usadas/modificadas em main para clareza
    global msg, selected_lang, selected_os

    # Trata argumentos de linha de comando para configuração inicial (opcional)
    # Estes argumentos podem sobrescrever os padrões definidos globalmente
    lang_overridden_by_arg = False
    if len(sys.argv) > 1:
        if "-lang=pt" in sys.argv:
            selected_lang = "pt"
            # Garante que msg seja atualizado imediatamente se lang for definido por arg
            msg = LANGUAGES[selected_lang]
            lang_overridden_by_arg = True
            # Usa msg.get para a mensagem formatada, com fallback
            lang_set_msg = msg.get("lang_set_by_arg", "Language set to {lang} by argument.").format(lang=selected_lang.upper())
            print_color(lang_set_msg, "\033[92m") # Verde
        elif "-lang=en" in sys.argv:
             selected_lang = "en"
             # Garante que msg seja atualizado imediatamente se lang for definido por arg
             msg = LANGUAGES[selected_lang]
             lang_overridden_by_arg = True
             # Usa msg.get para a mensagem formatada, com fallback
             lang_set_msg = msg.get("lang_set_by_arg", "Language set to {lang} by argument.").format(lang=selected_lang.upper())
             print_color(lang_set_msg, "\033[92m") # Verde
        # Adicione verificações similares para -os aqui, definindo selected_os

    # Seleções iniciais usando prompts interativos se não definidos por args
    if not lang_overridden_by_arg:
        # Se o idioma não foi definido por argumento, chama a função de seleção.
        # Esta função define ambos global selected_lang e global msg.
        select_language()
    # else: msg já foi definido baseado no argumento de linha de comando

    # msg agora está garantido de estar definido corretamente baseado em selected_lang
    # Agora, trata a seleção de SO (poderia adicionar tratamento de arg para -os também)
    select_os() # Isso define global selected_os

    # Exibe o cabeçalho usando o dicionário msg agora corretamente definido
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
                # Permite mudar o idioma durante a sessão
                select_language()
                display_header() # Reexibe o cabeçalho com o novo idioma
                continue
            elif user_input == "-os":
                # Permite mudar o SO durante a sessão
                select_os()
                continue

            # --- Fluxo de Trabalho Principal ---
            command = ask_ollama_for_command(user_input)

            if command:
                # Verifica se a ferramenta primária existe *antes* da confirmação (opcional, mas útil)
                # Trata potenciais comandos com caminhos ou estruturas complexas
                tool_name = command.split()[0] if command else ""
                # Verificação básica, pode precisar de refinamento para caminhos/aliases complexos
                if tool_name and '/' not in tool_name and '\\' not in tool_name:
                    if not check_command_exists(tool_name):
                        warn_msg = msg.get("error_not_found", "Command not found:") + f" '{tool_name}' (might not be installed or in PATH)."
                        print_color(f"\nWarning: {warn_msg}", "\033[93m") # Amarelo
                        print_color(f"{msg['tool_hint']} {get_missing_tool_hint(tool_name)}", "\033[93m") # Amarelo
                        # Pergunta ao usuário se deseja prosseguir mesmo assim
                        proceed_prompt = msg.get("proceed_q", "Proceed anyway? (y/n): ")
                        proceed = input(proceed_prompt).strip().lower()
                        should_proceed = proceed == 's' if selected_lang == "pt" else proceed == 'y'
                        if not should_proceed:
                            print_color(msg["cancel"], "\033[91m") # Vermelho
                            continue
                    # else: Ferramenta existe, prossegue normalmente
                # else: Comando inclui caminho ou está vazio, pula check_command_exists por enquanto

                confirm_and_execute(user_input, command)

            print_color(msg["ready"], "\033[92m") # Verde

        except KeyboardInterrupt:
            break # Permite Ctrl+C para sair graciosamente
        except EOFError:
            break # Trata EOF (ex: se a entrada for redirecionada)
        except Exception as e:
            # Captura erros inesperados no loop principal
            error_msg = msg.get("error_general", "An unexpected error occurred:")
            print_color(f"\n{error_msg} {e}", "\033[91m") # Vermelho
            traceback.print_exc() # Imprime traceback detalhado para depuração
            time.sleep(1) # Pausa breve

    goodbye_msg = msg.get("goodbye", "\n👋 Goodbye!")
    print_color(goodbye_msg, "\033[92m") # Verde

if __name__ == "__main__":
    main()
