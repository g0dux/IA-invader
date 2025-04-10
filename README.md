# IA invader

Welcome to **IA invader**, your local security assistant powered by artificial intelligence! This tool is designed to interpret natural language commands and automatically convert them into valid shell commands, helping you perform security scans and vulnerability analysis with ease.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Prerequisites & Dependencies](#prerequisites--dependencies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Examples](#command-examples)
- [Llama Pull Mistral & Ollama](#llama-pull-mistral--ollama)
- [Feedback & Auto-Correction](#feedback--auto-correction)
- [Logs & History](#logs--history)
- [Contribution](#contribution)
- [License](#license)
- [Contact](#contact)

---

## About

**IA invader** is a command-line tool that uses the **Ollama API** with the **Mistral** model to generate shell commands from natural language requests. The tool supports both Linux and Windows systems and offers features such as:

- **Automatic Command Generation:** Translates user requests into appropriate shell commands.
- **Command Interpretation:** Displays a brief explanation of the generated command.
- **Auto-Correction:** Suggests alternative commands in case of execution errors.
- **Multilingual Interface:** Supports English and Portuguese.
- **Spinner & Visual Feedback:** Displays an animation while the command is being processed.
- **Installation Tips:** If a required tool is missing, instructions and download links are provided.

---

## Features

- **Intelligent Generation:** Converts requests into shell commands using AI.
- **Interactive Execution:** Asks for confirmation before executing sensitive commands.
- **Visual Feedback:** Includes an animated spinner to indicate processing.
- **Correction Suggestions:** If an error occurs, the tool suggests an alternative command.
- **Multilingual Support:** Interface available in English and Portuguese.
- **Customization:** Allows selecting the target operating system (Linux or Windows).

---

## Prerequisites & Dependencies

Before using IA invader, ensure the following items are installed:

- **Python 3.7+**  
  The tool is built in Python and requires the following modules:
  - `os`, `time`, `subprocess`, `requests`, `sys`, `threading`, `itertools`

  If you don’t have the *requests* module, install it with:
  ```bash
  pip install requests
  ```

- **Ollama API with Mistral Model**  
  The tool uses the Ollama API to generate commands. The default URL is:  
  `http://localhost:11434/api/generate`  
  Ensure the service is running.

- **Llama Pull Mistral with Ollama**  
  To use the **Mistral** model, you need to download and configure **Llama Pull Mistral**. See more details in the [Llama Pull Mistral & Ollama](#llama-pull-mistral--ollama) section below.

- **Security Tools**  
  Depending on the generated commands, you may need tools such as:
  - **Nmap:**  
    - [Download for Windows](https://nmap.org/download.html#windows)  
      or, on Linux:
      ```bash
      sudo apt install nmap
      ```
  - **Nikto:**  
    - [Download for Windows](https://cirt.net/Nikto2)  
      or follow Linux installation instructions.

- **Execution Permissions:**  
  On Windows or when commands require root privileges on Linux, run the script with appropriate permissions.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-user/ia-invader.git
   cd ia-invader
   ```

2. **Create a virtual environment (optional, but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/macOS
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Ollama API:**  
   Ensure the API is running at the specified URL. If necessary, update the `OLLAMA_API_URL` variable in the code.

5. **Set up Llama Pull Mistral with Ollama:**  
   See steps in [Llama Pull Mistral & Ollama](#llama-pull-mistral--ollama).

---

## Usage

To start IA invader, run:

```bash
python ia_invader.py
```

Follow these steps:

1. **Select Language:**  
   Choose between English or Portuguese.

2. **Select Target OS:**  
   Specify whether the generated commands will be for Linux or Windows.

3. **Interactive Interface:**  
   - Displays welcome messages and usage instructions.
   - Prompts for a user request, e.g.:
     ```
     What would you like to do? (e.g., scan google.com with nmap):
     ```

4. **Processing & Execution:**  
   - The generated command will be displayed with a brief explanation.
   - Upon confirmation, the command executes. If an error occurs, the tool may suggest a correction automatically.

### Command Examples

- **Scan a website with Nmap:**
  ```
  scan google.com with nmap
  ```
- **Perform a scan with Nikto:**
  ```
  scan example.com with nikto
  ```

---

## Llama Pull Mistral & Ollama

To use the **Mistral** model with IA invader, set up **Llama Pull Mistral** via Ollama:

1. **Install Ollama:**
   - Download the installer for your OS from the [Ollama official website](https://ollama.com/download).
   - Follow the installation instructions.

2. **Verify Ollama installation:**
   - Open a terminal and run:
     ```bash
     ollama --version
     ```
   - This should display the installed Ollama version.

3. **Download the Mistral model:**
   - Run:
     ```bash
     ollama pull mistral
     ```
   - This will download and prepare the **Mistral** model for use.

4. **Run the Mistral model:**
   - Start the model with:
     ```bash
     ollama run mistral
     ```
   - This launches an interactive session, allowing the API to use the model for command generation.

5. **Integrate with IA invader:**
   - Ensure the **Mistral** model is running so that the API communication (via `OLLAMA_API_URL`) works properly.

---

## Contribution

To contribute to the project:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/new-feature
   ```
3. Commit your changes:
   ```bash
   git commit -am 'Add new feature'
   ```
4. Push to the remote repository:
   ```bash
   git push origin feature/new-feature
   ```
5. Open a Pull Request.

Your contributions are highly appreciated!

---

## License

Distributed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Contact

- **Author:** andha0  
- **Email:** baleiaazul660@gmail.com  
- **GitHub:** [your-profile](https://github.com/your-user)

---

> **Tip:** If you encounter any issues or have suggestions, open an *issue* on the repository or contact us via email. We are always looking to improve IA invader!
```

This README now provides complete information about IA invader in English, including setup instructions for Ollama and Mistral. Let me know if you need further refinements!

