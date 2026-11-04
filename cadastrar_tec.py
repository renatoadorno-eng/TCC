import pymysql
from werkzeug.security import generate_password_hash

# Função de conexão igual à do app.py
def conectar_banco():
    return pymysql.connect(
        host='localhost',
        user='root',          # Substitua pelo seu usuário do MySQL, se for diferente
        password='1234',      # Substitua pela sua senha do MySQL, se houver
        database='sistema_epi', # Substitua pelo nome do seu banco de dados
        cursorclass=pymysql.cursors.DictCursor
    )

def cadastrar_usuario():
    nome = "Técnico de Segurança"
    email = "tecnico@empresa.com"
    senha_plana = "123456" # Senha que você vai digitar no login
    
    # Gera a senha criptografada (hash segura)
    senha_hash = generate_password_hash(senha_plana)

    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            sql = "INSERT INTO Usuario (Nome, Email, Senha) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nome, email, senha_hash))
            conexao.commit()
            print("Técnico de segurança cadastrado com sucesso!")
    except Exception as e:
        print(f"Erro ao cadastrar (talvez o e-mail já exista): {e}")
    finally:
        conexao.close()

if __name__ == '__main__':
    cadastrar_usuario()