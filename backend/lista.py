from flask import Blueprint, request, jsonify
from db import conectar

lista_bp = Blueprint('lista', __name__)

# CADASTRAR PRODUTO
@lista_bp.route('/produtos', methods=['POST'])
def cadastrar_produto():
    dados = request.get_json()

    nome = dados.get("nome")
    codigo = dados.get("codigo")
    quantidade = dados.get("quantidade", 0)
    quantidade_minima = dados.get("quantidade_minima", 0)
    if not nome or not codigo:
        return jsonify({"erro": "Preencha nome e código"}), 400

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
    INSERT INTO produtos (nome, codigo, quantidade, quantidade_minima)
    VALUES (%s, %s, %s, %s)
""", (nome, codigo, quantidade, quantidade_minima))

        conn.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Produto cadastrado com sucesso!"
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# LISTAR PRODUTOS
@lista_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, codigo, quantidade
        FROM produtos
        ORDER BY nome
    """)

    produtos = cursor.fetchall()

    cursor.close()
    conn.close()

    lista = []
    for p in produtos:
        lista.append({
            "id": p[0],
            "nome": p[1],
            "codigo": p[2],
            "quantidade": p[3]
        })

    return jsonify({
        "sucesso": True,
        "dados": lista
    })