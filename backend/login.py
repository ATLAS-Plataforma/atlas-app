from flask import Blueprint, request
from db import conectar

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():

    dados = request.get_json()

    email = dados.get("email")
    senha = dados.get("senha")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE email=%s AND senha=%s",
        (email, senha)
    )

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if usuario:
        return {
            "sucesso": True,
            "mensagem": "Login realizado com sucesso"
        }

    return {
        "sucesso": False,
        "mensagem": "Email ou senha inválidos"
    }, 401