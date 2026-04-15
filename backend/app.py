from flask import Flask, jsonify, request, render_template
from db import conectar
from login import login_bp

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

@app.route('/movimentacao-page')
def movimentacao_page():
    return render_template('movimentacao.html')

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


# ✅ REGISTRAR MOVIMENTAÇÃO
# ============================================
@app.route('/movimentacao', methods=['POST'])
def registrar_movimentacao():
    # 1. Receber dados do frontend
    dados = request.get_json()
    
    produto_nome = dados.get('produto_nome')
    tipo = dados.get('tipo')
    quantidade = dados.get('quantidade')
    observacao = dados.get('observacao', '')
    
    # 2. Validar dados obrigatórios
    if not produto_nome:
        return jsonify({"erro": "Nome do produto é obrigatório"}), 400
    
    if not tipo or tipo not in ['entrada', 'saida']:
        return jsonify({"erro": "Tipo deve ser 'entrada' ou 'saida'"}), 400
    
    if not quantidade or quantidade <= 0:
        return jsonify({"erro": "Quantidade deve ser maior que zero"}), 400
    
    # 3. Conectar ao banco
    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro no banco de dados"}), 500
    
    cursor = conn.cursor()
    
    try:
        # 4. Inserir movimentação no banco
        cursor.execute("""
            INSERT INTO movimentacoes (produto_nome, tipo, quantidade, observacao)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (produto_nome, tipo, quantidade, observacao))
        
        movimentacao_id = cursor.fetchone()[0]
        
        # 5. Salvar (commit)
        conn.commit()
        
        print(f"✅ Movimentação {movimentacao_id} salva: {produto_nome} - {tipo} de {quantidade}")
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Movimentação de {tipo} registrada com sucesso!",
            "id": movimentacao_id,
            "dados": {
                "produto": produto_nome,
                "tipo": tipo,
                "quantidade": quantidade,
                "observacao": observacao
            }
        }), 201
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {e}")
        return jsonify({"erro": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)