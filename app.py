from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pymysql
# ... suas outras importações e conexao ...

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_super_segura_aqui'  # Necessário para usar session e flash messages

import os

def conectar_banco():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASS', '1234'),
        database=os.environ.get('DB_NAME', 'sistema_epi'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conexao = conectar_banco()
        try:
            with conexao.cursor() as cursor:
                sql = "SELECT * FROM Usuario WHERE Email = %s"
                cursor.execute(sql, (email,))
                usuario = cursor.fetchone()

                # Verifica se o usuário existe e se a senha confere com o hash
                if usuario and check_password_hash(usuario['Senha'], senha):
                    session['usuario_id'] = usuario['ID']
                    session['usuario_nome'] = usuario['Nome']
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('index')) # Redireciona para a página principal
                else:
                    flash('E-mail ou senha incorretos.', 'danger')
        finally:
            conexao.close()

    return render_template('login.html')

@app.before_request
def verificar_autenticacao():
    # Rotas liberadas sem necessidade de estar logado
    rotas_livres = ['login', 'static']
    
    # Se o usuário não está logado e tenta acessar uma rota protegida
    if 'usuario_id' not in session and request.endpoint not in rotas_livres:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    usuario = None
    if 'usuario_id' in session:
        conexao = conectar_banco()
        try:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT * FROM Usuario WHERE ID = %s", (session['usuario_id'],))
                usuario = cursor.fetchone()
        finally:
            conexao.close()
            
    return render_template('index.html', usuario=usuario)

@app.route('/colaboradores', methods=['GET', 'POST'])
def colaboradores():
    conexao = conectar_banco()
    try:
        # Se o usuário enviou o formulário (POST)
        if request.method == 'POST':
            nome = request.form['nome']
            setor = request.form['setor']

            with conexao.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO Colaborador (Nome, Setor, ativo) VALUES (%s, %s, 1)", (nome, setor))
                    conexao.commit()
                    
                    # Alerta nativo de SUCESSO
                    return """
                        <script>
                            alert('Colaborador cadastrado com sucesso!');
                            window.location.href = '/colaboradores';
                        </script>
                    """
                except Exception as e:
                    conexao.rollback()
                    # Alerta nativo de ERRO
                    return f"""
                        <script>
                            alert('Erro ao cadastrar colaborador: {e}');
                            window.location.href = '/colaboradores';
                        </script>
                    """

        # Se for apenas acesso (GET), busca apenas colaboradores ativos
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM Colaborador WHERE ativo = 1")
            lista_colaboradores = cursor.fetchall()
            return render_template('colaboradores.html', colaboradores=lista_colaboradores)
    finally:
        conexao.close()

@app.route('/colaboradores/editar/<int:id>', methods=['GET', 'POST'])
def editar_colaborador(id):
    conexao = conectar_banco()
    try:
        if request.method == 'POST':
            nome = request.form['nome']
            setor = request.form['setor']
 
            with conexao.cursor() as cursor:
                try:
                    sql = "UPDATE Colaborador SET Nome = %s, Setor = %s WHERE ID = %s"
                    cursor.execute(sql, (nome, setor, id))
                    conexao.commit()
                    
                    # Alerta nativo de SUCESSO ao editar
                    return """
                        <script>
                            alert('Colaborador atualizado com sucesso!');
                            window.location.href = '/colaboradores';
                        </script>
                    """
                except Exception as e:
                    conexao.rollback()
                    # Alerta nativo de ERRO ao editar
                    return f"""
                        <script>
                            alert('Erro ao atualizar colaborador: {e}');
                            window.location.href = '/colaboradores';
                        </script>
                    """

        # Se for GET, busca dados atuais para preencher formulário de edição
        with conexao.cursor() as cursor:
            sql = "SELECT * FROM Colaborador WHERE ID = %s"
            cursor.execute(sql, (id,))
            colaborador = cursor.fetchone()

            return render_template('editar_colaborador.html', colaborador=colaborador)
    finally:
        conexao.close()

@app.route('/colaboradores/excluir/<int:id>', methods=['GET'])
def excluir_colaborador(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Exclusão lógica (inativação) para preservar o histórico de empréstimos
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

@app.route('/equipamentos', methods=['GET', 'POST'])
def equipamentos():
    conexao = conectar_banco()
    try:
        # Se o utilizador enviou o formulário de cadastro (POST)
        if request.method == 'POST':
            nome = request.form['nome']
            qtd_estoque = request.form['qtd_estoque']

            with conexao.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO Equipamento (Nome, QTD_estoque, ativo) VALUES (%s, %s, 1)", (nome, qtd_estoque))
                    conexao.commit()
                    
                    # Alerta nativo de SUCESSO ao cadastrar equipamento
                    return """
                        <script>
                            alert('Equipamento cadastrado com sucesso!');
                            window.location.href = '/equipamentos';
                        </script>
                    """
                except Exception as e:
                    conexao.rollback()
                    # Alerta nativo de ERRO ao cadastrar equipamento
                    return f"""
                        <script>
                            alert('Erro ao cadastrar equipamento: {e}');
                            window.location.href = '/equipamentos';
                        </script>
                    """

        # Se for apenas acesso (GET), busca apenas equipamentos ativos
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM Equipamento WHERE ativo = 1")
            lista_equipamentos = cursor.fetchall()
            return render_template('equipamentos.html', equipamentos=lista_equipamentos)
    finally:
        conexao.close()


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
                    
                    # Alerta nativo de SUCESSO ao editar equipamento
                    return """
                        <script>
                            alert('Equipamento atualizado com sucesso!');
                            window.location.href = '/equipamentos';
                        </script>
                    """
                except Exception as e:
                    conexao.rollback()
                    # Alerta nativo de ERRO ao editar equipamento
                    return f"""
                        <script>
                            alert('Erro ao atualizar equipamento: {e}');
                            window.location.href = '/equipamentos';
                        </script>
                    """
        
        # Se for GET, busca dados atuais para preencher o formulário de edição
        with conexao.cursor() as cursor:
            sql = "SELECT * FROM Equipamento WHERE ID = %s"
            cursor.execute(sql, (id,))
            equipamento = cursor.fetchone()
            return render_template('editar_equipamento.html', equipamento=equipamento)

    finally:
        conexao.close()

@app.route('/equipamentos/excluir/<int:id>', methods=['GET'])
def exlcuir_equipamento(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Exclusão lógica (inativação) do equipamento para preservar os registos da tabela 'contem'
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

@app.route('/emprestimos')
def emprestimos():
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
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

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
def novo_emprestimo():
    conexao = conectar_banco()
    try:
        if request.method == 'POST':
            id_colaborador = request.form['id_colaborador']
            id_equipamento = request.form['id_equipamento']
            quantidade = int(request.form['quantidade'])
            status = request.form['status']

            # Se for 'Fornecido', não exige data prevista. Se for 'Emprestado', valida a data.
            if status == 'Fornecido':
                data_prevista_str = None
                situacao = 0  # Já nasce finalizado, pois não há devolução
            else:
                data_prevista_str = request.form['data_prevista_devolucao']
                situacao = 1  # Em aberto
                
                # Validação no backend: Data prevista deve ser posterior à data/hora atual
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
                # 1. Verificar estoque disponível
                cursor.execute("SELECT QTD_estoque, Nome FROM Equipamento WHERE ID = %s", (id_equipamento,))
                equipamento = cursor.fetchone()

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
                    # 2. Registar o empréstimo/fornecimento
                    sql_emp = """
                        INSERT INTO Emprestimo (Data, idColaborador, Situacao, data_prevista_devolucao, status) 
                        VALUES (NOW(), %s, %s, %s, %s)
                    """
                    cursor.execute(sql_emp, (id_colaborador, situacao, data_prevista_str, status))
                    id_emprestimo = cursor.lastrowid

                    # 3. Vincular o equipamento na tabela contem
                    sql_contem = "INSERT INTO contem (idEmprestimo, idEquipamento, Quantidade) VALUES (%s, %s, %s)"
                    cursor.execute(sql_contem, (id_emprestimo, id_equipamento, quantidade))
                    
                    # 4. Atualizar o estoque
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

        # Apenas colaboradores e equipamentos ATIVOS podem ser selecionados num novo empréstimo
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM Colaborador WHERE ativo = 1")
            colaboradores = cursor.fetchall()

            cursor.execute("SELECT * FROM Equipamento WHERE ativo = 1")
            equipamentos = cursor.fetchall()

            return render_template('novo_emprestimo.html', colaboradores=colaboradores, equipamentos=equipamentos)
    finally:
        conexao.close()

@app.route('/emprestimos/finalizar/<int:id>', methods=['GET', 'POST'])
def finalizar_emprestimo(id):
    conexao = conectar_banco()
    try:
        if request.method == 'POST':
            novo_status = request.form['status']
            observacao = request.form.get('observacao_devolucao', '')

            with conexao.cursor() as cursor:
                # 1. Buscar os equipamentos e quantidades vinculados a este empréstimo
                sql_itens = "SELECT idEquipamento, Quantidade FROM contem WHERE idEmprestimo = %s"
                cursor.execute(sql_itens, (id,))
                itens = cursor.fetchall()
                
                # 2. Gerenciar estoque: 
                # Se for Devolvido ou Danificado, o item retorna fisicamente ao stock.
                # Se for Perdido, o item extraviou, logo NÃO retorna ao stock.
                for item in itens:
                    id_equipamento = item['idEquipamento']
                    quantidade = item['Quantidade']
                    
                    if novo_status in ['Devolvido', 'Danificado']:
                        sql_devolve_estoque = "UPDATE Equipamento SET QTD_estoque = QTD_estoque + %s WHERE ID = %s"
                        cursor.execute(sql_devolve_estoque, (quantidade, id_equipamento))

                # 3. Atualizar o empréstimo para encerrado (Situacao = 0), salvando data efetiva, status e observação
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

        # Se for GET, carrega os dados para a página de escolha de status
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

@app.route('/emprestimos/visualizar/<int:id>')
def visualizar_emprestimo(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # 1. Buscar dados completos do empréstimo, colaborador e datas
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
            
            # 2. Buscar os equipamentos e quantidades associados a este empréstimo
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

@app.route('/relatorios', methods=['GET'])
def relatorios():
    # Captura os filtros enviados via GET
    filtro_colaborador = request.args.get('colaborador', '').strip()
    filtro_equipamento = request.args.get('equipamento', '').strip()
    filtro_status = request.args.get('status', '').strip()

    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Query base unindo Emprestimo, Colaborador, a tabela intermediária contem e Equipamento
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

            # Aplicar filtro dinâmico combinando com AND se preenchido
            if filtro_colaborador:
                sql += " AND c.Nome LIKE %s"
                parametros.append(f"%{filtro_colaborador}%")

            if filtro_equipamento:
                sql += " AND eq.Nome LIKE %s"
                parametros.append(f"%{filtro_equipamento}%")

            if filtro_status:
                sql += " AND e.status = %s"
                parametros.append(filtro_status)

            # Ordenar dos mais recentes para os mais antigos
            sql += " ORDER BY e.Data DESC"

            cursor.execute(sql, tuple(parametros))
            resultados = cursor.fetchall()

            return render_template('relatorios.html', resultados=resultados)
    finally:
        conexao.close()

if __name__ == '__main__':
    app.run(debug=True)