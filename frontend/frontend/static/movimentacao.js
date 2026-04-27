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

    estoqueEl.innerText = "-";

    fetch(`http://localhost:5000/produto/${nome}?t=${new Date().getTime()}`)
    .then(res => res.json())
    .then(p => {

        const minimo = produtos[produtoKey].minimo;
        minimoEl.innerText = minimo;

        if (p.erro || !p.nome || !p.codigo) {
            nomeEl.innerText = "Produto não encontrado";
            codigoEl.innerText = "-";
            estoqueEl.innerText = "-";
            alerta.style.display = "none";
            return;
        }

        nomeEl.innerText = p.nome;
        codigoEl.innerText = p.codigo;

        const estoque = p.estoque;

        estoqueEl.innerText =
            (estoque === null || estoque === undefined)
                ? "-"
                : estoque;

        // 🚨 ERRO: estoque negativo
        if (estoque < 0) {
            alerta.style.display = "block";
            alerta.innerText = "❌ Erro: estoque negativo! Não é possível ter valor menor que 0.";
            alerta.style.background = "#f8d7da";
            alerta.style.color = "#721c24";
        }

        // ⚠️ estoque baixo
        else if (estoque < minimo) {
            alerta.style.display = "block";
            alerta.innerText = "⚠️ Estoque baixo!";
            alerta.style.background = "#fff3cd";
            alerta.style.color = "#856404";
        }

        // ✅ estoque normal
        else {
            alerta.style.display = "block";
            alerta.innerText = "✅ Estoque normal";
            alerta.style.background = "#d4edda";
            alerta.style.color = "#155724";
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

    const produtoKey = document.getElementById("selecionarProduto").value;
    const produtoNome = produtos[produtoKey].nome;

    const quantidade = parseInt(document.getElementById("quantidade").value);
    const data = new Date().toLocaleString("sv-SE").replace(" ", "T");

    if (!produtoNome || !quantidade || !tipoSelecionado) {
        alert("Preencha todos os campos!");
        return;
    }

    // 🚨 BLOQUEAR SAÍDA MAIOR QUE ESTOQUE
    if (tipoSelecionado === "saida") {
        const estoqueAtual = parseInt(document.getElementById("estoqueAtual").innerText);

        if (quantidade > estoqueAtual) {
            alert("❌ Não é possível fazer saída maior que o estoque!");
            return;
        }
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

            document.getElementById("quantidade").value = "";
            tipoSelecionado = "";

            carregarHistorico();
            atualizarCard(produtoKey);

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

    const produto = document.getElementById("produtoFiltro").value;
    const tipo = document.getElementById("tipoFiltro").value;
    const qtd = document.getElementById("quantidadeFiltro").value;

    fetch("http://localhost:5000/movimentacoes")
    .then(res => res.json())
    .then(dados => {

        const tabela = document.getElementById("tabela");
        tabela.innerHTML = "";

        dados
        .filter(item => {
            return (
                (!produto || item.produto === produto) &&
                (!tipo || item.tipo === tipo) &&
                (!qtd || item.quantidade == qtd)
            );
        })
        .forEach(item => {

            const tipoUpper = item.tipo.toUpperCase();

            const linha = document.createElement("tr");

            linha.innerHTML = `
                <td>${new Date(item.data).toLocaleString('pt-BR')}</td>
                <td>${item.produto}</td>
                <td>
                    <span class="tag ${tipoUpper === 'ENTRADA' ? 'entrada' : 'saida'}">
                        ${tipoUpper === 'ENTRADA' ? '⬆ ENTRADA' : '⬇ SAÍDA'}
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
    atualizarCard("arroz");
};