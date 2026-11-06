# Sistema de Gerenciamento de EPIs

Sistema desenvolvido em Python com **Flask** e **MySQL** para o controle de empréstimos, colaboradores e equipamentos de proteção individual (EPIs) de uma empresa do setor têxtil.

---

## Funcionalidades
- **Gestão de Colaboradores**: Cadastro, edição, exclusão e pesquisa por nome.
- **Gestão de Equipamentos**: Cadastro e controle de estoque de EPIs.
- **Controle de Empréstimos**: Registo de novos empréstimos com baixa automática no stock e finalização com devolução automática ao inventário.
- **Comprovante (Ticket)**: Visualização detalhada do empréstimo estilizada com Bootstrap 5.

---

## Tecnologias Utilizadas
- **Python 3.x** / **Flask**
- **MySQL** / **PyMySQL**
- **Bootstrap 5**
- **HTML5 / Jinja2**

---

## Como Executar o Projeto

Siga os passos abaixo para rodar o sistema na sua máquina:

### 1. Pré-requisitos
Certifique-se de ter instalado:
- Python (versão 3.x)
- MySQL Server ativo

### 2. Clonar o repositório
```bash
git clone https://github.com/renatoadorno-eng/TCC.git
````
### 2. Configurar o Ambiente Virtual (`venv`)
No terminal (PowerShell / Bash):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(Nota: Se houver bloqueio de execução no PowerShell, execute `Set-ExecutionPolicy Unrestricted -Scope Process` antes de ativar).*

### 3. Instalar as Dependências
```bash
pip install flask pymysql werkzeug
```

### 4. Inicializar o Banco de Dados Local
1. Abra o **MySQL Workbench** e conecte-se ao seu servidor local (`localhost:3306`).
2. Abra o arquivo `db.sql` incluído no projeto.
3. Execute o script para criar a base `sistema_epi` e suas tabelas.

### 5. Cadastrar o Usuário Inicial
Execute o script **cadastrar_tec.py** presente na pasta para criar o primeiro usuário de acesso:
```bash
python cadastrar_tec.py
```
usuário: tecnico@empresa.com  
senha: 123456

### 6. Iniciar a Aplicação
```bash
python app.py
```
  
