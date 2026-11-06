import pymysql
from werkzeug.security import generate_password_hash

# Cria uma função para conectar ao banco de dados MySQL local
def conectar_banco():
    return pymysql.connect(
        host='localhost',       # Define o endereço do servidor 
        user='root',            # Usuario padrão do MySQL 
        password='1234',        # Senha configurada para o banco
        database='sistema_epi', # Nome da base de dados 
        cursorclass=pymysql.cursors.DictCursor # Retorna os dados em formato de dicionário
    )

# funcao principal que realiza o cadastro do usuario inicial
def cadastrar_usuario():
    nome = "Técnico de Segurança"
    email = "tecnico@empresa.com"
    senha_plana = "123456" # Senha usada para login
    
    # Converte a senha em texto plano para hash 
    senha_hash = generate_password_hash(senha_plana)

    # Abre a conexão com o banco de dados
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # comando SQL para inserir o usuário na tabela correspondente
            sql = "INSERT INTO Usuario (Nome, Email, Senha) VALUES (%s, %s, %s)"
            # Executa a query passando as variáveis
            cursor.execute(sql, (nome, email, senha_hash))
            # Salva a operação no banco
            conexao.commit()
            print("Técnico de segurança cadastrado com sucesso!")
    except Exception as e:
        # Captura e exibe qualquer erro
        print(f"Erro ao cadastrar (talvez o e-mail já exista): {e}")
    finally:
        # Fecha a conexão com o banco de dados
        conexao.close()
        
if __name__ == '__main__':
    cadastrar_usuario()