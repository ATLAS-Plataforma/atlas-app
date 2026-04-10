from flask import Flask, jsonify, request, render_template
from db import conectar
from routes.login import login_bp

app = Flask(
    __name__,
    template_folder='../frontend/frontend/templates',
    static_folder='../frontend/frontend/static'
)
@app.route('/produtos-page')
def produtos_page():
    return render_template("produtos.html")

app.register_blueprint(login_bp)

@app.route('/login-page')
def login_page():
    return render_template('login.html')


@app.route('/')
def home():
    return {"mensagem": "API rodando 🚀"}


# ✅ LISTAR PRODUTOS
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

    return {
        "sucesso": True,
        "dados": lista
    }


# ✅ CADASTRAR PRODUTO
@app.route('/produtos', methods=['POST'])
def cadastrar_produto():

    dados = request.get_json()

    if not dados:
        return {"erro": "JSON inválido"}, 400

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO produtos (nome, codigo, quantidade)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (dados['nome'], dados['codigo'], dados['quantidade']))

    id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "sucesso": True,
        "id": id
    }, 201
# ✅ REGISTRAR MOVIMENTAÇÃO
@app.route('/movimentacao', methods=['POST'])
def registrar_movimentacao():

    dados = request.get_json()

    if not dados:
        return {"erro": "JSON inválido"}, 400

    produto_id = dados.get("produto_id")
    tipo = dados.get("tipo")
    quantidade = dados.get("quantidade")
    observacao = dados.get("observacao", "")

    if not produto_id or not tipo or not quantidade:
        return {"erro": "Dados obrigatórios faltando"}, 400

    if quantidade <= 0:
        return {"erro": "Quantidade inválida"}, 400

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT quantidade FROM produtos WHERE id = %s",
            (produto_id,)
        )
        resultado = cursor.fetchone()

        if not resultado:
            return {"erro": "Produto não encontrado"}, 404

        estoque_atual = resultado[0]

        if tipo == "entrada":
            novo_estoque = estoque_atual + quantidade

        elif tipo == "saida":
            if estoque_atual < quantidade:
                return {"erro": "Estoque insuficiente"}, 400
            novo_estoque = estoque_atual - quantidade

        else:
            return {"erro": "Tipo inválido"}, 400

        cursor.execute(
            "UPDATE produtos SET quantidade = %s WHERE id = %s",
            (novo_estoque, produto_id)
        )

        cursor.execute("""
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, observacao)
            VALUES (%s, %s, %s, NOW(), %s)
        """, (produto_id, tipo, quantidade, observacao))

        conn.commit()

    except Exception as e:
        conn.rollback()
        return {"erro": str(e)}, 500

    finally:
        cursor.close()
        conn.close()

    return {
        "sucesso": True,
        "mensagem": "Movimentação registrada",
        "estoque_atual": novo_estoque
    }



if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)