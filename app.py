from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pymysql, os


# Inicializa a aplicação web utilizando o Flask
app = Flask(__name__)

# Configura a chave secreta buscando na variável de ambiente do sistema ou usando um valor padrão para testes locais
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_super_segura_aqui')
# função estabelece conexão com base de dados
def conectar_banco():
    return pymysql.connect(
    
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASS', '1234'),
        database=os.environ.get('DB_NAME', 'sistema_epi'),
        # Configura o cursor para retornar os resultados das consultas em formato de dicionário 
        cursorclass=pymysql.cursors.DictCursor
    )

# Rota e função de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verifica se o usuário enviou o formulário de login
    if request.method == 'POST':
        # Captura o e-mail preenchido no formulário
        email = request.form['email']
        # Captura a senha preenchida no formulário
        senha = request.form['senha']

        # Abre a conexão com o banco de dados
        conexao = conectar_banco()
        try:
            # Cria um cursor para executar comandos SQL
            with conexao.cursor() as cursor:
                # instrução SQL para procurar o usuário pelo e-mail
                sql = "SELECT * FROM Usuario WHERE Email = %s"
                # query passando o email
                cursor.execute(sql, (email,))
                # primeiro registro encontrado no banco
                usuario = cursor.fetchone()

                # Verifica se o usuário existe na base e se a senha informada confere com o hash
                if usuario and check_password_hash(usuario['Senha'], senha):
                    # Salva o ID do usuário na sessão ativa do navegador
                    session['usuario_id'] = usuario['ID']
                    # Salva o nome do usuário na sessão ativa
                    session['usuario_nome'] = usuario['Nome']
                    # Cria uma mensagem flash informando o sucesso
                    flash('Login realizado com sucesso!', 'success')
                    # Redireciona o usuário para a página inicial
                    return redirect(url_for('index')) 
                else:
                    # Se falhar, exibe uma mensagem de erro na tela de login
                    flash('E-mail ou senha incorretos.', 'danger')
        finally:
            # conexão com o banco de dados será fechada independentemente de erros
            conexao.close()

    # Se for um acesso GET, renderiza e exibe a página HTML de login
    return render_template('login.html')

# Verifica se o usuário pode acessar as rotas
@app.before_request
def verificar_autenticacao():
    # rotas que não exigem que o usuário esteja logado
    rotas_livres = ['login', 'static']
    
    # Se tenta acessar rota sem id de usuário válido, volta pra tela de login
    if 'usuario_id' not in session and request.endpoint not in rotas_livres:
        return redirect(url_for('login'))

# Define a rota para encerrar a sessão do usuário
@app.route('/logout')
def logout():
    # Limpa todos os dados armazenados na sessão atual
    session.clear()
    # Exibe um aviso informando que saiu do sistema
    flash('Você saiu do sistema.', 'info')
    # Redireciona para a tela de login
    return redirect(url_for('login'))

# Define a rota raiz do sistema 
@app.route('/')
def index():
    usuario = None
    # Verifica se há um usuário autenticado na sessão
    if 'usuario_id' in session:
        conexao = conectar_banco()
        try:
            with conexao.cursor() as cursor:
                # Busca os dados do usuário logado no banco de dados
                cursor.execute("SELECT * FROM Usuario WHERE ID = %s", (session['usuario_id'],))
                usuario = cursor.fetchone()
        finally:
            conexao.close()
            
    # Renderiza a página principal enviando os dados do usuário logado
    return render_template('index.html', usuario=usuario)

# Define a rota para gerenciamento de colaboradores (listagem GET e cadastro POST)
@app.route('/colaboradores', methods=['GET', 'POST'])
def colaboradores():
    conexao = conectar_banco()
    try:
        # Se os dados foram enviados via formulário (POST), realiza o cadastro
        if request.method == 'POST':
            nome = request.form['nome']
            setor = request.form['setor']

            with conexao.cursor() as cursor:
                try:
                    # Insere o novo colaborador definindo o campo 'ativo' como 1 (Medida necessária para suportar escolhas de design que permita apagar usuários sem quebrar a lista de empréstimos)
                    cursor.execute("INSERT INTO Colaborador (Nome, Setor, ativo) VALUES (%s, %s, 1)", (nome, setor))
                    # Confirma a gravação dos dados no banco
                    conexao.commit()
                    
                    # alerta de sucesso e redirecionamento
                    return """
                        <script>
                            alert('Colaborador cadastrado com sucesso!');
                            window.location.href = '/colaboradores';
                        </script>
                    """
                except Exception as e:
                    # Em caso de erro, desfaz a alteração no banco
                    conexao.rollback()
                    # alerta indicando o erro ocorrido
                    return f"""
                        <script>
                            alert('Erro ao cadastrar colaborador: {e}');
                            window.location.href = '/colaboradores';
                        </script>
                    """

        # Se for uma requisição GET, busca e lista apenas os colaboradores ativos no sistema
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM Colaborador WHERE ativo = 1")
            lista_colaboradores = cursor.fetchall()
            return render_template('colaboradores.html', colaboradores=lista_colaboradores)
    finally:
        conexao.close()

# Define a rota para editar os dados de um colaborador
@app.route('/colaboradores/editar/<int:id>', methods=['GET', 'POST'])
def editar_colaborador(id):
    conexao = conectar_banco()
    try:
        # Se for POST, atualiza os dados alterados no formulário
        if request.method == 'POST':
            nome = request.form['nome']
            setor = request.form['setor']
 
            with conexao.cursor() as cursor:
                try:
                    sql = "UPDATE Colaborador SET Nome = %s, Setor = %s WHERE ID = %s"
                    cursor.execute(sql, (nome, setor, id))
                    conexao.commit()
                    
                    return """
                        <script>
                            alert('Colaborador atualizado com sucesso!');
                            window.location.href = '/colaboradores';
                        </script>
                    """
                except Exception as e:
                    conexao.rollback()
                    return f"""
                        <script>
                            alert('Erro ao atualizar colaborador: {e}');
                            window.location.href = '/colaboradores';
                        </script>
                    """

        # Se for GET, busca as informações atuais do colaborador
        with conexao.cursor() as cursor:
            sql = "SELECT * FROM Colaborador WHERE ID = %s"
            cursor.execute(sql, (id,))
            colaborador = cursor.fetchone()

            return render_template('editar_colaborador.html', colaborador=colaborador)
    finally:
        conexao.close()

# Define a rota para a exclusão lógica de um colaborador
@app.route('/colaboradores/excluir/<int:id>', methods=['GET'])
def excluir_colaborador(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Realiza uma exclusão lógica atualizando o status 'ativo' para 0, preservando o histórico de empréstimos
            sql = "UPDATE Colaborador SET ativo = 0 WHERE ID = %s"
            cursor.execute(sql, (id,))
            conexao.commit()
            
            return """
                <script>
                    alert('Colaborador inativado com sucesso! Os históricos de empréstimos foram preservados.');
                    window.location.href = '/colaboradores';
                </script>
            """
    finally:
        conexao.close()

# Define a rota para o gerenciamento de equipamentos
@app.route('/equipamentos', methods=['GET', 'POST'])
def equipamentos():
    conexao = conectar_banco()
    try:
        # Se POST, cadastra o novo equipamento
        if request.method == 'POST':
            nome = request.form['nome']
            qtd_estoque = request.form['qtd_estoque']

            with conexao.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO Equipamento (Nome, QTD_estoque, ativo) VALUES (%s, %s, 1)", (nome, qtd_estoque))
                    conexao.commit()
                    
                    return """
                        <script>
                            alert('Equipamento cadastrado com sucesso!');
                            window.location.href = '/equipamentos';
                        </script>
                    """
                except Exception as e:
                    conexao.rollback()
                    return f"""
                        <script>
                            alert('Erro ao cadastrar equipamento: {e}');
                            window.location.href = '/equipamentos';
                        </script>
                    """

        # Se for GET, busca e exibe apenas os equipamentos ativos
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM Equipamento WHERE ativo = 1")
            lista_equipamentos = cursor.fetchall()
            return render_template('equipamentos.html', equipamentos=lista_equipamentos)
    finally:
        conexao.close()

# Define a rota para editar um equipamento
@app.route('/equipamentos/editar/<int:id>', methods=['GET', 'POST'])
def editar_equipamento(id):
    conexao = conectar_banco()
    try:
        if request.method == 'POST':
            nome = request.form['nome']
            qtd_estoque = request.form['qtd_estoque']

            with conexao.cursor() as cursor:
                try:
                    sql = "UPDATE Equipamento SET Nome = %s, QTD_estoque = %s WHERE ID = %s"
                    cursor.execute(sql, (nome, qtd_estoque, id))
                    conexao.commit()
                    
                    return """
                        <script>
                            alert('Equipamento atualizado com sucesso!');
                            window.location.href = '/equipamentos';
                        </script>
                    """
                except Exception as e:
                    conexao.rollback()
                    return f"""
                        <script>
                            alert('Erro ao atualizar equipamento: {e}');
                            window.location.href = '/equipamentos';
                        </script>
                    """
        
        # Se for GET, recupera os dados do equipamento para exibir no formulário de edição
        with conexao.cursor() as cursor:
            sql = "SELECT * FROM Equipamento WHERE ID = %s"
            cursor.execute(sql, (id,))
            equipamento = cursor.fetchone()
            return render_template('editar_equipamento.html', equipamento=equipamento)

    finally:
        conexao.close()

# Define a rota para inativar um equipamento
@app.route('/equipamentos/excluir/<int:id>', methods=['GET'])
def exlcuir_equipamento(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Inativa o equipamento (ativo = 0) mantendo integridade com a tabela de histórico de empréstimos
            sql = "UPDATE Equipamento SET ativo = 0 WHERE ID = %s"
            cursor.execute(sql, (id,))
            conexao.commit()
            
            return """
                <script>
                    alert('Equipamento inativado com sucesso! O histórico foi mantido.');
                    window.location.href = '/equipamentos';
                </script>
            """
    finally:
        conexao.close()

# Define a rota para listar todos os empréstimos registrados no sistema
@app.route('/emprestimos')
def emprestimos():
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Executa uma consulta unindo a tabela de Empréstimos com Colaboradores para exibir os nomes
            sql = """
                SELECT e.ID, e.Data, e.Situacao, e.status, c.Nome AS Colaborador 
                FROM Emprestimo e 
                JOIN Colaborador c ON e.idColaborador = c.ID
                ORDER BY e.ID DESC
            """
            cursor.execute(sql)
            lista_emprestimos = cursor.fetchall()
            return render_template('emprestimos.html', emprestimos=lista_emprestimos)
    finally:
        conexao.close()

# Define a rota para registrar um novo empréstimo
@app.route('/emprestimos/novo', methods=['GET', 'POST'])
def novo_emprestimo():
    conexao = conectar_banco()
    try:
        if request.method == 'POST':
            # Capta os dados enviados pelo formulário
            id_colaborador = request.form['id_colaborador']
            id_equipamento = request.form['id_equipamento']
            quantidade = int(request.form['quantidade'])
            status = request.form['status']

            # Verifica o tipo de operação, se for fornecimento, não exige data de devolução e finaliza a situação
            if status == 'Fornecido':
                data_prevista_str = None
                situacao = 0  
            else:
                data_prevista_str = request.form['data_prevista_devolucao']
                situacao = 1  # Mantém em aberto
                
                # Converte e valida se a data de devolução prevista é posterior ao momento atual
                data_prevista = datetime.strptime(data_prevista_str, '%Y-%m-%dT%H:%M')
                agora = datetime.now()

                if data_prevista <= agora:
                    return """
                        <script>
                            alert('Erro: A data prevista para devolução deve ser posterior à data e hora atuais.');
                            window.history.back();
                        </script>
                    """

            with conexao.cursor() as cursor:
                # Consulta o estoque e o nome do equipamento selecionado
                cursor.execute("SELECT QTD_estoque, Nome FROM Equipamento WHERE ID = %s", (id_equipamento,))
                equipamento = cursor.fetchone()

                # Valida se há estoque suficiente para cobrir a quantidade solicitada
                if not equipamento or equipamento['QTD_estoque'] < quantidade:
                    disponivel = equipamento['QTD_estoque'] if equipamento else 0
                    nome_epi = equipamento['Nome'] if equipamento else 'EPI'
                    return f"""
                        <script>
                            alert('Erro: Não é possível emprestar {quantidade} unidade(s) de "{nome_epi}". O estoque atual disponível é de apenas {disponivel} unidade(s).');
                            window.history.back();
                        </script>
                    """

                try:
                    # Insere o registro principal do empréstimo na tabela 'Emprestimo'
                    sql_emp = """
                        INSERT INTO Emprestimo (Data, idColaborador, Situacao, data_prevista_devolucao, status) 
                        VALUES (NOW(), %s, %s, %s, %s)
                    """
                    cursor.execute(sql_emp, (id_colaborador, situacao, data_prevista_str, status))
                    # Captura o ID gerado para este novo empréstimo
                    id_emprestimo = cursor.lastrowid

                    # Associa o EPI e a quantidade na tabela intermediária 'contem'
                    sql_contem = "INSERT INTO contem (idEmprestimo, idEquipamento, Quantidade) VALUES (%s, %s, %s)"
                    cursor.execute(sql_contem, (id_emprestimo, id_equipamento, quantidade))
                    
                    # Atualiza o estoque subtraindo a quantidade emprestada
                    sql_estoque = "UPDATE Equipamento SET QTD_estoque = QTD_estoque - %s WHERE ID = %s"
                    cursor.execute(sql_estoque, (quantidade, id_equipamento))

                    conexao.commit()

                    return """
                        <script>
                            alert('Registro realizado com sucesso!');
                            window.location.href = '/emprestimos';
                        </script>
                    """
                except Exception as e:
                    conexao.rollback()
                    return f"""
                        <script>
                            alert('Erro ao registrar: {e}');
                            window.location.href = '/emprestimos/novo';
                        </script>
                    """

        # Se for GET, busca apenas colaboradores e equipamentos ativos para preencher os selects do formulário
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM Colaborador WHERE ativo = 1")
            colaboradores = cursor.fetchall()

            cursor.execute("SELECT * FROM Equipamento WHERE ativo = 1")
            equipamentos = cursor.fetchall()

            return render_template('novo_emprestimo.html', colaboradores=colaboradores, equipamentos=equipamentos)
    finally:
        conexao.close()

# Define a rota para finalizar um empréstimo
@app.route('/emprestimos/finalizar/<int:id>', methods=['GET', 'POST'])
def finalizar_emprestimo(id):
    conexao = conectar_banco()
    try:
        if request.method == 'POST':
            novo_status = request.form['status']
            observacao = request.form.get('observacao_devolucao', '')

            with conexao.cursor() as cursor:
                # Busca os itens vinculados ao empréstimo que está sendo encerrado
                sql_itens = "SELECT idEquipamento, Quantidade FROM contem WHERE idEmprestimo = %s"
                cursor.execute(sql_itens, (id,))
                itens = cursor.fetchall()
                
                # Lógica de devolução ao estoque: se foi devolvido ou danificado, o item retorna fisicamente ao estoque
                for item in itens:
                    id_equipamento = item['idEquipamento']
                    quantidade = item['Quantidade']
                    
                    if novo_status in ['Devolvido', 'Danificado']:
                        sql_devolve_estoque = "UPDATE Equipamento SET QTD_estoque = QTD_estoque + %s WHERE ID = %s"
                        cursor.execute(sql_devolve_estoque, (quantidade, id_equipamento))

                # Atualiza o registro do empréstimo para encerrado (Situacao = 0), registrando data efetiva e observações
                sql_emp = """
                    UPDATE Emprestimo 
                    SET Situacao = 0, 
                        status = %s, 
                        data_efetiva_devolucao = NOW(), 
                        observacao_devolucao = %s 
                    WHERE ID = %s
                """
                cursor.execute(sql_emp, (novo_status, observacao if observacao else None, id))
                
                conexao.commit()
                
                return f"""
                    <script>
                        alert('Empréstimo finalizado com sucesso para "{novo_status}"!');
                        window.location.href = '/emprestimos';
                    </script>
                """

        # Se for GET, carrega os dados básicos do empréstimo para a página de atualização
        with conexao.cursor() as cursor:
            sql_emp = """
                SELECT e.ID, c.Nome AS Colaborador 
                FROM Emprestimo e 
                JOIN Colaborador c ON e.idColaborador = c.ID 
                WHERE e.ID = %s
            """
            cursor.execute(sql_emp, (id,))
            emprestimo = cursor.fetchone()
            
            return render_template('atualizar_emprestimo.html', emprestimo=emprestimo)
    finally:
        conexao.close()

# Define a rota para visualizar os detalhes completos de um empréstimo específico
@app.route('/emprestimos/visualizar/<int:id>')
def visualizar_emprestimo(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Busca as informações gerais do empréstimo e do colaborador associado
            sql_emp = """
                SELECT 
                    e.ID, 
                    e.Data, 
                    e.Situacao, 
                    e.status,
                    e.data_prevista_devolucao,
                    e.data_efetiva_devolucao,
                    e.observacao_devolucao,
                    c.ID AS IdColaborador, 
                    c.Nome AS Colaborador, 
                    c.Setor 
                FROM Emprestimo e 
                JOIN Colaborador c ON e.idColaborador = c.ID 
                WHERE e.ID = %s
            """
            cursor.execute(sql_emp, (id,))
            emprestimo = cursor.fetchone()
            
            # Busca todos os equipamentos vinculados a este empréstimo na tabela 'contem'
            sql_itens = """
                SELECT eq.ID AS IdEquipamento, eq.Nome, co.Quantidade 
                FROM contem co 
                JOIN Equipamento eq ON co.idEquipamento = eq.ID 
                WHERE co.idEmprestimo = %s
            """
            cursor.execute(sql_itens, (id,))
            itens = cursor.fetchall()
            
            return render_template('visualizar_emprestimo.html', emprestimo=emprestimo, itens=itens)
    finally:
        conexao.close()

# Define a rota para o painel de relatórios com suporte a filtros
@app.route('/relatorios', methods=['GET'])
def relatorios():
    # Captura os filtros informados
    filtro_colaborador = request.args.get('colaborador', '').strip()
    filtro_equipamento = request.args.get('equipamento', '').strip()
    filtro_status = request.args.get('status', '').strip()

    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Constrói a consulta SQL base cruzando todas as tabelas relevantes do sistema
            sql = """
                SELECT 
                    e.ID, 
                    e.Data, 
                    e.Situacao, 
                    e.status,
                    e.data_prevista_devolucao,
                    e.data_efetiva_devolucao,
                    c.Nome AS Colaborador,
                    eq.Nome AS Equipamento,
                    co.Quantidade
                FROM Emprestimo e
                JOIN Colaborador c ON e.idColaborador = c.ID
                JOIN contem co ON e.ID = co.idEmprestimo
                JOIN Equipamento eq ON co.idEquipamento = eq.ID
                WHERE 1=1
            """
            parametros = []

            # Adiciona dinamicamente a condição do filtro de colaborador caso tenha sido preenchido
            if filtro_colaborador:
                sql += " AND c.Nome LIKE %s"
                parametros.append(f"%{filtro_colaborador}%")

            # Adiciona o filtro de equipamento se preenchido
            if filtro_equipamento:
                sql += " AND eq.Nome LIKE %s"
                parametros.append(f"%{filtro_equipamento}%")

            # Adiciona o filtro de status se preenchido
            if filtro_status:
                sql += " AND e.status = %s"
                parametros.append(filtro_status)

            # Ordena os resultados trazendo os registros mais recentes primeiro
            sql += " ORDER BY e.Data DESC"

            cursor.execute(sql, tuple(parametros))
            resultados = cursor.fetchall()

            return render_template('relatorios.html', resultados=resultados)
    finally:
        conexao.close()

if __name__ == '__main__':
    app.run(debug=True)