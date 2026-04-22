from flask import Blueprint, request
from db import conectar

lista_bp = Blueprint('lista', __name__)

@lista_bp.route('/buscar-produtos', methods=['GET'])
def buscar_produtos():
    termo = request.args.get('q')

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT id, nome, codigo, quantidade
        FROM produtos
        WHERE nome ILIKE %s OR codigo ILIKE %s
    """

    cursor.execute(query, (f"%{termo}%", f"%{termo}%"))
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

    return {"dados": lista}