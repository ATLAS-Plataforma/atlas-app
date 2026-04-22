from flask import Flask, jsonify, request, render_template
from db import conectar
from login import login_bp
from lista import lista_bp

app = Flask(
    __name__,
    template_folder='../frontend/frontend/templates',
    static_folder='../frontend/frontend/static'
)

# ==============================
# 🔹 BLUEPRINTS
# ==============================
app.register_blueprint(login_bp)
app.register_blueprint(lista_bp)

# ==============================
# 🔹 PÁGINAS HTML
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
# 🔹 LISTAR PRODUTOS
# ==============================
@app.route('/produtos', methods=['GET'])
def listar_produtos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, codigo, quantidade FROM produtos")
    produtos = cursor.fetchall()

    lista = []
    for p in produtos:
        lista.append({
            "id": p[0],
            "nome": p[1],
            "codigo": p[2],
            "quantidade": p[3]
        })

    cursor.close()
    conn.close()

    return jsonify({
        "sucesso": True,
        "dados": lista
    })


# ==============================
# 🔹 BUSCAR PRODUTO (ESTOQUE)
# ==============================
@app.route('/produto/<nome>', methods=['GET'])
def buscar_produto(nome):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, codigo, quantidade
        FROM produtos
        WHERE nome = %s
    """, (nome,))

    produto = cursor.fetchone()

    cursor.close()
    conn.close()

    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    return jsonify({
        "nome": produto[0],
        "codigo": produto[1],
        "estoque": produto[2]
    })


# ==============================
# 🔹 REGISTRAR MOVIMENTAÇÃO
# ==============================
@app.route('/movimentacao', methods=['POST'])
def registrar_movimentacao():

    dados = request.get_json()

    produto_nome = dados.get('produto_nome')
    tipo = dados.get('tipo')
    quantidade = dados.get('quantidade')
    observacao = dados.get('observacao', '')
    data = dados.get('data')

    if not produto_nome:
        return jsonify({"erro": "Nome do produto é obrigatório"}), 400

    if tipo not in ['entrada', 'saida']:
        return jsonify({"erro": "Tipo deve ser 'entrada' ou 'saida'"}), 400

    if not quantidade or quantidade <= 0:
        return jsonify({"erro": "Quantidade deve ser maior que zero"}), 400

    conn = conectar()
    cursor = conn.cursor()

    try:

        # registrar movimentação
        cursor.execute("""
        INSERT INTO movimentacoes (produto_nome, tipo, quantidade, observacao, data)
        VALUES (%s, %s, %s, %s, %s)
         RETURNING id
""", (produto_nome, tipo, quantidade, observacao, data))

        movimentacao_id = cursor.fetchone()[0]

        # atualizar estoque
        if tipo == "entrada":

            cursor.execute("""
                UPDATE produtos
                SET quantidade = quantidade + %s
                WHERE LOWER(nome)= LOWER(%s)
            """, (quantidade, produto_nome))

        else:

            cursor.execute("""
                UPDATE produtos
                SET quantidade = quantidade - %s
                WHERE LOWER(nome)= LOWER(%s)
            """, (quantidade, produto_nome))

        conn.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Movimentação registrada com sucesso!",
            "id": movimentacao_id
        }), 201

    except Exception as e:

        conn.rollback()
        print("❌ ERRO POST:", e)

        return jsonify({"erro": str(e)}), 500

    finally:

        cursor.close()
        conn.close()


# ==============================
# 🔹 LISTAR MOVIMENTAÇÕES
# ==============================
@app.route('/movimentacoes', methods=['GET'])
def listar_movimentacoes():

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, produto_nome, tipo, quantidade, observacao, data
            FROM movimentacoes
            ORDER BY data DESC
        """)

        resultados = cursor.fetchall()

        movimentacoes = []

        for row in resultados:
            movimentacoes.append({
                "id": row[0],
                "produto": row[1],
                "tipo": row[2],
                "quantidade": row[3],
                "observacao": row[4],
                "data": str(row[5])
            })

        return jsonify(movimentacoes)

    except Exception as e:
        print("❌ ERRO GET:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ==============================
# 🚀 RODAR SERVIDOR
# ==============================
if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)