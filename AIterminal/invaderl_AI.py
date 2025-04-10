import os
import time
import subprocess
import requests
import sys
from threading import Thread
from itertools import cycle

# Configuration
OLLAMA_MODEL = "mistral"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Global flag for spinner control and variables for language and operating system
spinner_running = False
selected_lang = None
selected_os = None
msg = {}

# Dictionary with links and installation instructions for known tools.
DOWNLOAD_LINKS = {
    "nmap": {
        "windows": {
            "link": "https://nmap.org/download.html#windows",
            "instructions": {
                "en": "Download and install Nmap from the official website.",
                "pt": "Baixe e instale o Nmap pelo site oficial."
            }
        },
        "linux": {
            "link": "https://nmap.org/download.html",
            "instructions": {
                "en": "Install Nmap using your package manager (e.g., 'sudo apt install nmap').",
                "pt": "Instale o Nmap pelo seu gerenciador de pacotes (ex.: 'sudo apt install nmap')."
            }
        }
    },
    "nikto": {
        "windows": {
            "link": "https://cirt.net/Nikto2",
            "instructions": {
                "en": "Download Nikto for Windows from the official page.",
                "pt": "Baixe o Nikto para Windows na página oficial."
            }
        },
        "linux": {
            "link": "https://cirt.net/Nikto2",
            "instructions": {
                "en": "Install Nikto using your package manager or follow instructions on its official site.",
                "pt": "Instale o Nikto pelo gerenciador de pacotes ou siga as instruções no site oficial."
            }
        }
    },
    "ip": {
        "linux": {
            "link": "https://wiki.archlinux.org/title/Iproute2",
            "instructions": {
                "en": "Ensure iproute2 is installed on your system (usually 'sudo apt install iproute2').",
                "pt": "Certifique-se de que o iproute2 está instalado (normalmente 'sudo apt install iproute2')."
            }
        }
    }
}

# Multilingual messages and dictionaries
LANGUAGES = {
    "en": {
        "header": r"""
 
                                                                                           
                          ,,                                         ,,                    
      db      `7MMF'      db                                       `7MM                    
     ;MM:       MM                                                   MM                    
    ,V^MM.      MM      `7MM  `7MMpMMMb.  `7M'   `MF' ,6"Yb.    ,M""bMM   .gP"Ya  `7Mb,od8 
   ,M  `MM      MM        MM    MM    MM    VA   ,V  8)   MM  ,AP    MM  ,M'   Yb   MM' "' 
   AbmmmqMA     MM        MM    MM    MM     VA ,V    ,pm9MM  8MI    MM  8M""""""   MM     
  A'     VML    MM        MM    MM    MM      VVV    8M   MM  `Mb    MM  YM.    ,   MM     
.AMA.   .AMMA..JMML.    .JMML..JMML  JMML.     W     `Moo9^Yo. `Wbmd"MML. `Mbmmd' .JMML.   
                                                                                           
                                                                                           
                                         

""",
        "welcome": "Welcome to HackerAI - Your Local AI Security Assistant",
        "separator": "----------------------------------------------------",
        "usage": "Usage: Type your command like 'scan google.com with nmap'",
        "options": "Options: -h for help | -v for version\n",
        "help": (
            "\nUsage:\n  scan <target> with <tool>\nSupported tools: nmap, nikto\n"
            "Options:\n  -h : Show this help message\n  -v : Show version info\n"
        ),
        "version": "HackerAI v1.0 - Powered by Ollama & Mistral",
        "input": "\nWhat do you want to do? (e.g., scan google.com with nmap): ",
        "thinking": "HackerAI is thinking... 🤔",
        "ai_interpreted": "\nThe AI interpreted your request as follows:",
        "confirm": "Do you want to execute this command? (y/n): ",
        "execute": "\nExecuting command:",
        "ready": "\nHackerAI is ready for the next command! (Press CTRL+C to exit)\n",
        "cancel": "Command execution canceled by the user.",
        "error_fetch": "Failed to fetch command from Ollama.",
        "goodbye": "\nGoodbye! 👋",
        "not_found": "The command was not found.",
        "os_select": "Select your target operating system:",
        "os_options": "1. Linux\n2. Windows\nChoice (1/2): ",
        "auto_correct_q": "The command failed. Would you like to try an AI-suggested alternative? (y/n): "
    },
    "pt": {
        "header": r"""                                                                           

                                                                                           
                          ,,                                         ,,                    
      db      `7MMF'      db                                       `7MM                    
     ;MM:       MM                                                   MM                    
    ,V^MM.      MM      `7MM  `7MMpMMMb.  `7M'   `MF' ,6"Yb.    ,M""bMM   .gP"Ya  `7Mb,od8 
   ,M  `MM      MM        MM    MM    MM    VA   ,V  8)   MM  ,AP    MM  ,M'   Yb   MM' "' 
   AbmmmqMA     MM        MM    MM    MM     VA ,V    ,pm9MM  8MI    MM  8M""""""   MM     
  A'     VML    MM        MM    MM    MM      VVV    8M   MM  `Mb    MM  YM.    ,   MM     
.AMA.   .AMMA..JMML.    .JMML..JMML  JMML.     W     `Moo9^Yo. `Wbmd"MML. `Mbmmd' .JMML.   
                                                                                           
                                                                                           

""",
        "welcome": "Bem-vindo ao AI invader - Seu Assistente de Segurança Local com IA",
        "separator": "----------------------------------------------------",
        "usage": "Uso: Digite seu comando, por exemplo, 'varrer google.com com nmap'",
        "options": "Opções: -h para ajuda | -v para versão\n",
        "help": (
            "\nUso:\n  varrer <alvo> com <ferramenta>\nFerramentas suportadas: nmap, nikto\n"
            "Opções:\n  -h : Mostra esta mensagem de ajuda\n  -v : Mostra informações da versão\n"
        ),
        "version": "AI invader v1.0 - Alimentado por Ollama & Mistral",
        "input": "\nO que você deseja fazer? (ex.: varrer google.com com nmap): ",
        "thinking": "AI invader está pensando... 🤔",
        "ai_interpreted": "\nA IA interpretou seu pedido da seguinte forma:",
        "confirm": "Deseja executar este comando? (s/n): ",
        "execute": "\nExecutando o comando:",
        "ready": "\nHackerAI está pronto para o próximo comando! (Pressione CTRL+C para sair)\n",
        "cancel": "Execução do comando cancelada pelo usuário.",
        "error_fetch": "Falha ao buscar o comando da Ollama.",
        "goodbye": "\nAdeus! 👋",
        "not_found": "O comando não foi encontrado.",
        "os_select": "Selecione o sistema operacional de destino:",
        "os_options": "1. Linux\n2. Windows\nEscolha (1/2): ",
        "auto_correct_q": "O comando falhou. Deseja tentar uma alternativa sugerida pela IA? (s/n): "
    }
}

def select_language():
    global selected_lang, msg
    print("Select language / Selecione a língua:")
    print("1. English")
    print("2. Português")
    choice = input("Choice / Escolha (1/2): ").strip()
    if choice == "2":
        selected_lang = "pt"
    else:
        selected_lang = "en"
    msg = LANGUAGES[selected_lang]

def select_os():
    global selected_os
    print("\n" + msg["os_select"])
    choice = input(msg["os_options"]).strip()
    if choice == "2":
        selected_os = "windows"
    else:
        selected_os = "linux"

def display_header():
    print("\033[95m")
    print(msg["header"])
    print(msg["welcome"])
    print(msg["separator"] + "\033[0m\n")
    print(msg["usage"])
    print(msg["options"])

def show_help():
    print(msg["help"])

def show_version():
    print(msg["version"])

def ask_ollama(question):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": (
            f"You are a command generator. Your job is to convert user requests into a single valid shell command.\n"
            f"Rules:\n"
            f"- No explanations.\n"
            f"- No extra text.\n"
            f"- No backticks.\n"
            f"- No creative answers.\n"
            f"- Only the raw shell command itself.\n"
            f"- If the request does not make sense for a shell command, return this exact string: 'invalid-request'.\n"
            f"- The command should be generated considering the user's language (language: {selected_lang}) and target operating system (OS: {selected_os}).\n"
            f"User Request: {question}\n"
            f"Shell Command:"
        ),
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
    except Exception as e:
        print(f"\033[91mError connecting to Ollama: {str(e)}\033[0m")
        return None

    if response.status_code == 200:
        command = response.json().get('response', '').strip()
        command = command.strip("`").strip('"').strip("'").strip()
        if command == "invalid-request":
            error_msg = ("This request doesn't translate into a valid shell command." 
                         if selected_lang == "en" 
                         else "Este pedido não se traduz em um comando de shell válido.")
            print("\033[91m[!] " + error_msg + "\033[0m")
            return None
        return command
    else:
        print(f"\033[91mError communicating with Ollama: {response.text}\033[0m")
        return None

def ask_interpreter(user_request, command):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": (
            f"You are a command interpreter. Given the user's request and the generated shell command, "
            f"provide a brief explanation in {selected_lang.upper()} of what this command will do on a {selected_os.upper()} system. "
            f"Ensure your answer is in the same language as specified. "
            f"User Request: {user_request}\n"
            f"Generated Command: {command}\n"
            f"Explanation:"
        ),
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
    except Exception as e:
        print(f"\033[91mError connecting to Ollama for interpretation: {str(e)}\033[0m")
        return ""
    if response.status_code == 200:
        explanation = response.json().get('response', '').strip()
        explanation = explanation.strip("`").strip('"').strip("'").strip()
        return explanation
    else:
        print(f"\033[91mError communicating with Ollama for interpretation: {response.text}\033[0m")
        return ""

def get_missing_component_hint(command):
    """
    Identifies a missing tool by checking the first token of the command,
    and returns a custom message with a link and instructions.
    """
    tool = command.split()[0].lower()
    if tool in DOWNLOAD_LINKS:
        os_data = DOWNLOAD_LINKS[tool].get(selected_os)
        if os_data:
            link = os_data["link"]
            instructions = os_data["instructions"][selected_lang]
            return f"{instructions} (Link: {link})"
    generic = {
        "en": "Ensure that the required tool is installed and available in your system PATH.",
        "pt": "Certifique-se de que a ferramenta necessária está instalada e disponível no PATH do sistema."
    }
    return generic[selected_lang]

def show_spinner(command):
    global spinner_running
    # Sequência de frames utilizando caracteres Unicode modernos
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    frame_cycle = cycle(frames)
    message = f"{msg['execute']} {command}"
    while spinner_running:
        sys.stderr.write(f"\r\033[96m{next(frame_cycle)} {message}\033[0m")
        sys.stderr.flush()
        time.sleep(0.1)
    sys.stderr.write("\r" + " " * (len(message) + 4) + "\r")

def run_command(command):
    global spinner_running
    spinner_running = True
    spinner_thread = Thread(target=show_spinner, args=(command,))
    spinner_thread.start()

    try:
        process = subprocess.Popen(command, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except PermissionError as e:
        spinner_running = False
        spinner_thread.join()
        print("\033[91mPermissionError: Acesso negado ao executar o comando.\033[0m")
        print("\033[91mTente executar o script com privilégios de administrador.\033[0m")
        return -1, str(e)

    stdout, stderr = process.communicate()

    spinner_running = False
    spinner_thread.join()

    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
        if ("não é reconhecido" in stderr.lower()) or ("not recognized" in stderr.lower()):
            hint = get_missing_component_hint(command)
            print("\033[91m" + msg["not_found"] + " " + hint + "\033[0m")
    return process.returncode, stderr

def auto_correct_command(user_request, original_command, error_output):
    """
    New function to handle errors by asking the AI for an alternative solution.
    It sends a prompt including the original user request, the generated command, 
    and the error output. The AI is expected to return an alternative command.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": (
            f"You are a command corrector. The original command generated was:\n"
            f"{original_command}\n"
            f"User Request: {user_request}\n"
            f"However, executing it resulted in the following error output:\n"
            f"{error_output}\n"
            f"Provide a corrected shell command that addresses the error and can work on a {selected_os.upper()} system, "
            f"without any extra text or explanation. If no correction is possible, just output 'no-suggestion'.\n"
            f"Corrected Command:"
        ),
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
    except Exception as e:
        print(f"\033[91mError connecting to Ollama for auto-correction: {str(e)}\033[0m")
        return None

    if response.status_code == 200:
        new_command = response.json().get('response', '').strip()
        new_command = new_command.strip("`").strip('"').strip("'").strip()
        if new_command == "no-suggestion":
            return None
        return new_command
    else:
        print(f"\033[91mError communicating with Ollama for auto-correction: {response.text}\033[0m")
        return None

def confirm_command(command, explanation):
    print("\n\033[94m" + msg["ai_interpreted"] + "\033[0m")
    print(f"\033[93m{command}\033[0m")
    if explanation:
        print("\n\033[92m" + explanation + "\033[0m")
    user_confirm = input("\033[96m" + msg["confirm"] + "\033[0m").strip().lower()
    return user_confirm == 's' if selected_lang == "pt" else user_confirm == 'y'

def main():
    select_language()
    select_os()
    display_header()

    while True:
        user_input = input(msg["input"]).strip()

        if user_input == "-h":
            show_help()
            continue
        elif user_input == "-v":
            show_version()
            continue

        print(msg["thinking"])

        command = ask_ollama(user_input)
        if not command:
            print("\033[91m" + msg["error_fetch"] + "\033[0m")
            continue

        explanation = ask_interpreter(user_input, command)

        if not confirm_command(command, explanation):
            print("\033[91m" + msg["cancel"] + "\033[0m")
            continue

        print("\n\033[92m" + msg["execute"], command, "\033[0m\n")
        ret_code, err_output = run_command(command)

        # Se ocorrer um erro, tenta auto-correção
        if ret_code != 0 and err_output:
            user_wants_correction = input("\033[96m" + msg["auto_correct_q"] + "\033[0m").strip().lower()
            if (user_wants_correction == 'y' and selected_lang == "en") or (user_wants_correction == 's' and selected_lang == "pt"):
                new_command = auto_correct_command(user_input, command, err_output)
                if new_command:
                    new_explanation = ask_interpreter(user_input, new_command)
                    if confirm_command(new_command, new_explanation):
                        print("\n\033[92m" + msg["execute"], new_command, "\033[0m\n")
                        run_command(new_command)
                    else:
                        print("\033[91m" + msg["cancel"] + "\033[0m")
                else:
                    print("\033[91m" + ("No alternative command suggested by AI." 
                                        if selected_lang == "en"
                                        else "Nenhum comando alternativo sugerido pela IA.") + "\033[0m")

        print("\n\033[92m" + msg["ready"] + "\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(msg.get("goodbye", "\nGoodbye! 👋"))
