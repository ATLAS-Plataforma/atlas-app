from flask import Flask, jsonify, request, render_template
from db import conectar
from login import login_bp
from lista import lista_bp
from email_service import enviar_email_alerta

app = Flask(
    __name__,
    template_folder='../frontend/frontend/templates',
    static_folder='../frontend/frontend/static'
)

# ==============================
# BLUEPRINTS
# ==============================
app.register_blueprint(login_bp)
app.register_blueprint(lista_bp)

# ==============================
# PÁGINAS
# ==============================
@app.route('/')
def home():
    return {"mensagem": "API rodando 🚀"}

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/produtos-page')
def produtos_page():
    return render_template("produtos.html")

@app.route('/movimentacao-page')
def movimentacao_page():
    return render_template('movimentacao.html')

@app.route('/lista-page')
def lista_page():
    return render_template("lista.html")

# ==============================
# LISTAR PRODUTOS
# ==============================
@app.route('/produtos', methods=['GET'])
def listar_produtos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, codigo, quantidade, quantidade_minima
        FROM produtos
        ORDER BY id
    """)

    produtos = cursor.fetchall()

    lista = []

    for p in produtos:
        lista.append({
            "id": p[0],
            "nome": p[1],
            "codigo": p[2],
            "quantidade": p[3],
            "quantidade_minima": p[4]
        })

    cursor.close()
    conn.close()

    return jsonify({
        "sucesso": True,
        "dados": lista
    })

# ==============================
# BUSCAR PRODUTO
# ==============================
@app.route('/produto/<nome>', methods=['GET'])
def buscar_produto(nome):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, codigo, quantidade, quantidade_minima
        FROM produtos
        WHERE LOWER(nome) = LOWER(%s)
    """, (nome,))

    produto = cursor.fetchone()

    cursor.close()
    conn.close()

    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    return jsonify({
        "nome": produto[0],
        "codigo": produto[1],
        "estoque": produto[2],
        "quantidade_minima": produto[3]
    })

# ==============================
# REGISTRAR MOVIMENTAÇÃO
# ==============================
@app.route('/movimentacao', methods=['POST'])
def registrar_movimentacao():

    dados = request.get_json()

    produto_nome = dados.get('produto_nome')
    tipo = dados.get('tipo')
    quantidade = dados.get('quantidade')
    observacao = dados.get('observacao', '')

    if not produto_nome:
        return jsonify({"erro": "Produto obrigatório"}), 400

    if tipo not in ['entrada', 'saida']:
        return jsonify({"erro": "Tipo inválido"}), 400

    if not quantidade or quantidade <= 0:
        return jsonify({"erro": "Quantidade inválida"}), 400

    conn = conectar()
    cursor = conn.cursor()

    try:
        # busca estoque atual e mínimo
        cursor.execute("""
            SELECT quantidade, quantidade_minima
            FROM produtos
            WHERE LOWER(nome)=LOWER(%s)
        """, (produto_nome,))

        produto = cursor.fetchone()

        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404

        estoque_atual = produto[0]
        estoque_minimo = produto[1]

        if tipo == "saida" and quantidade > estoque_atual:
            return jsonify({"erro": "Estoque insuficiente"}), 400

        # salva movimentação
        cursor.execute("""
            INSERT INTO movimentacoes
            (produto_nome, tipo, quantidade, observacao, data)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        """, (produto_nome, tipo, quantidade, observacao))

        movimentacao_id = cursor.fetchone()[0]

        # calcula novo estoque
        if tipo == "entrada":
            novo_estoque = estoque_atual + quantidade
        else:
            novo_estoque = estoque_atual - quantidade

        # atualiza estoque
        cursor.execute("""
            UPDATE produtos
            SET quantidade = %s
            WHERE LOWER(nome)=LOWER(%s)
        """, (novo_estoque, produto_nome))

        # envia email apenas em saída
        if tipo == "saida":

            if novo_estoque == 0:
                enviar_email_alerta(
                    produto_nome,
                    novo_estoque,
                    "ESTOQUE ZERADO"
                )

            elif novo_estoque <= estoque_minimo:
                enviar_email_alerta(
                    produto_nome,
                    novo_estoque,
                    "ESTOQUE BAIXO"
                )

        conn.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Movimentação registrada com sucesso!",
            "id": movimentacao_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# ==============================
# LISTAR MOVIMENTAÇÕES
# ==============================
# COLE EXATAMENTE ISSO NO BACKEND

@app.route('/movimentacoes', methods=['GET'])
def listar_movimentacoes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id,
            produto_nome,
            tipo,
            quantidade,

            CASE
                WHEN data IS NULL THEN ''
                ELSE TO_CHAR(data, 'DD/MM/YYYY HH24:MI:SS')
            END

        FROM movimentacoes
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    lista = []

    for row in rows:

        lista.append({
            "id": row[0],
            "produto": row[1],
            "tipo": row[2],
            "quantidade": row[3],
            "data": row[4]
        })

    cursor.close()
    conn.close()

    return jsonify(lista)
# ==============================
# RODAR
# ==============================
if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)