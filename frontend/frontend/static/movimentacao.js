let tipoSelecionado = "";

// 🔹 PRODUTOS
const produtos = {
    arroz: { nome: "Arroz", codigo: "ARZ-001", minimo: 20 },
    feijao: { nome: "Feijão", codigo: "FJ-002", minimo: 20 },
    acucar: { nome: "Açúcar", codigo: "ACR-003", minimo: 20 },
    cafe: { nome: "Café", codigo: "CF-004", minimo: 20 },
    oleo: { nome: "Óleo", codigo: "OL-005", minimo: 20 },
    leite: { nome: "Leite", codigo: "LT-006", minimo: 20 },
    sal: { nome: "Sal", codigo: "SAL-007", minimo: 20 },
    ovos: { nome: "Ovos", codigo: "OVO-008", minimo: 20 },
    macarrao: { nome: "Macarrão", codigo: "MSS-009", minimo: 20 },
    detergente: { nome: "Detergente", codigo: "DT-010", minimo: 20 }
};

// 🔹 TROCAR PRODUTO
function trocarProduto() {
    const produtoSelecionado = document.getElementById("selecionarProduto").value;
    atualizarCard(produtoSelecionado);
}

// 🔹 SELECIONAR TIPO
function selecionarTipo(tipo) {
    tipoSelecionado = tipo;

    document.getElementById("entrada").style.opacity = tipo === "entrada" ? "1" : "0.5";
    document.getElementById("saida").style.opacity = tipo === "saida" ? "1" : "0.5";
}

// 🔹 ATUALIZAR CARD
function atualizarCard(produtoKey) {

    const nome = produtos[produtoKey].nome;

    const nomeEl = document.getElementById("nomeProduto");
    const codigoEl = document.getElementById("codigoProduto");
    const estoqueEl = document.getElementById("estoqueAtual");
    const minimoEl = document.getElementById("estoqueMinimo");
    const alerta = document.getElementById("alertaEstoque");

    // 🔥 limpa antes de carregar
    estoqueEl.innerText = "-";

    fetch(`http://localhost:5000/produto/${nome}?t=${new Date().getTime()}`)
    .then(res => res.json())
    .then(p => {

        const minimo = produtos[produtoKey].minimo;
        minimoEl.innerText = minimo;

        // ❌ erro ou não encontrado
        if (p.erro || !p.nome || !p.codigo) {
            nomeEl.innerText = "Produto não encontrado";
            codigoEl.innerText = "-";
            estoqueEl.innerText = "-";
            alerta.style.display = "none";
            return;
        }

        // ✅ dados corretos
        nomeEl.innerText = p.nome;
        codigoEl.innerText = p.codigo;

        const estoque = p.estoque;

        // 🔥 MOSTRAR VALOR REAL DO BANCO
        estoqueEl.innerText =
            (estoque === null || estoque === undefined)
                ? "-"
                : estoque;

        // ⚠️ alerta de estoque baixo
        if (estoque < minimo) {
    alerta.style.display = "block";
    alerta.innerText = "⚠️ Estoque baixo!";
} else {
    alerta.style.display = "block";
    alerta.innerText = "✅ Estoque normal";
}

    })
    .catch(err => {
        console.error("Erro:", err);

        nomeEl.innerText = "Erro ao conectar";
        codigoEl.innerText = "-";
        estoqueEl.innerText = "-";
        alerta.style.display = "none";
    });
}

// 🔹 REGISTRAR MOVIMENTAÇÃO
function registrar() {

    const produtoNome = document.getElementById("produto").value;
    const quantidade = parseInt(document.getElementById("quantidade").value);
    const data = new Date().toLocaleString("sv-SE").replace(" ", "T");

    if (!produtoNome || !quantidade || !tipoSelecionado) {
        alert("Preencha todos os campos!");
        return;
    }

    fetch("http://localhost:5000/movimentacao", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            produto_nome: produtoNome,
            tipo: tipoSelecionado,
            quantidade: quantidade,
            data: data
        })
    })
    .then(res => res.json())
    .then(data => {

        const msg = document.getElementById("mensagem");

        if (data.sucesso) {

            msg.innerText = "✅ " + data.mensagem;
            msg.style.color = "green";

            document.getElementById("produto").value = "";
            document.getElementById("quantidade").value = "";

            tipoSelecionado = "";

            document.getElementById("entrada").style.opacity = "1";
            document.getElementById("saida").style.opacity = "1";

            carregarHistorico();

            // 🔥 ATUALIZA CARD COM VALOR DO BANCO
            const select = document.getElementById("selecionarProduto");
            atualizarCard(select.value);

        } else {
            msg.innerText = "❌ " + (data.erro || "Erro ao registrar");
            msg.style.color = "red";
        }

    })
    .catch(err => {
        console.error(err);
        document.getElementById("mensagem").innerText =
            "Erro ao conectar com o servidor";
    });
}

// 🔹 HISTÓRICO
function carregarHistorico() {

    fetch("http://localhost:5000/movimentacoes")
    .then(res => res.json())
    .then(dados => {

        const tabela = document.getElementById("tabela");
        tabela.innerHTML = "";

        dados.forEach(item => {

            const tipo = item.tipo.toUpperCase();

            const linha = document.createElement("tr");

            linha.innerHTML = `
                <td>${new Date(item.data).toLocaleString('pt-BR')}</td>
                <td>${item.produto}</td>
                <td>
                    <span class="tag ${tipo === 'ENTRADA' ? 'entrada' : 'saida'}">
                        ${tipo === 'ENTRADA' ? '⬆ ENTRADA' : '⬇ SAÍDA'}
                    </span>
                </td>
                <td>${item.quantidade}</td>
            `;

            tabela.appendChild(linha);
        });

    })
    .catch(err => {
        console.error("Erro ao carregar histórico:", err);
    });
}

// 🔹 INICIAR
window.onload = function() {
    carregarHistorico();
    atualizarCard("arroz"); // 🔥 já carrega certo ao abrir
};