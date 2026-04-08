from flask import Flask, jsonify, request
import itertools

app = Flask(__name__)

# 🔥 ID automático (corrige problema de duplicação)
contador_id = itertools.count(1)

produtos = [
    {
        'id': next(contador_id),
        'nome': 'Arroz',
        'codigo': '001',
        'quantidade': 5
    }
]

def verificar_status(qtd):
    return "baixo" if qtd <= 10 else "normal"


# ✅ ROTA INICIAL
@app.route('/')
def home():
    return {"mensagem": "API rodando 🚀"}


# ✅ LISTAR PRODUTOS + FILTRO
@app.route('/produtos', methods=['GET'])
def listar_produtos():

    status_filtro = request.args.get('status')

    lista = []

    for p in produtos:
        produto = p.copy()
        produto['status'] = verificar_status(p['quantidade'])

        if status_filtro and produto['status'] != status_filtro:
            continue

        lista.append(produto)

    return {
        "sucesso": True,
        "dados": lista
    }


# ✅ CADASTRAR PRODUTO COM VALIDAÇÃO
@app.route('/produtos', methods=['POST'])
def cadastrar_produto():

    dados = request.get_json()

    # 🔥 validações
    if not dados:
        return {"erro": "JSON inválido"}, 400

    if not dados.get("nome") or not dados.get("codigo"):
        return {"erro": "Nome e código são obrigatórios"}, 400

    if type(dados.get("quantidade")) != int:
        return {"erro": "Quantidade deve ser número"}, 400

    # 🔥 evitar código duplicado
    for p in produtos:
        if p['codigo'] == dados.get("codigo"):
            return {"erro": "Código já existe"}, 400

    novo_produto = {
        "id": next(contador_id),
        "nome": dados.get("nome"),
        "codigo": dados.get("codigo"),
        "quantidade": dados.get("quantidade")
    }

    produtos.append(novo_produto)

    novo_produto["status"] = verificar_status(novo_produto["quantidade"])

    return {
        "sucesso": True,
        "dados": novo_produto
    }, 201


# 🔥 ATUALIZAR OU DELETAR
@app.route('/produtos/<int:id>', methods=['PUT', 'DELETE'])
def manipular_produto(id):

    # 👉 ATUALIZAR
    if request.method == 'PUT':
        dados = request.get_json()

        for p in produtos:
            if p['id'] == id:

                p['nome'] = dados.get("nome", p['nome'])
                p['codigo'] = dados.get("codigo", p['codigo'])
                p['quantidade'] = dados.get("quantidade", p['quantidade'])

                p['status'] = verificar_status(p['quantidade'])

                return {
                    "sucesso": True,
                    "dados": p
                }

        return {"erro": "Produto não encontrado"}, 404

    # 👉 DELETAR
    elif request.method == 'DELETE':

        for p in produtos:
            if p['id'] == id:
                produtos.remove(p)
                return {"mensagem": "Produto removido com sucesso"}

        return {"erro": "Produto não encontrado"}, 404


if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)