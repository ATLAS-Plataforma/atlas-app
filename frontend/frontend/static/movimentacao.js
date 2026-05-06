let tipoSelecionado = "";
let produtos = {};

// INICIAR
window.onload = function () {
    carregarProdutos();
    carregarHistorico();
};

// ======================
// CARREGAR PRODUTOS
// ======================
function carregarProdutos() {

    fetch("http://localhost:5000/produtos")
    .then(res => res.json())
    .then(res => {

        const lista = res.dados;

        const select = document.getElementById("selecionarProduto");
        const filtro = document.getElementById("produtoFiltro");

        select.innerHTML = "";
        filtro.innerHTML = '<option value="">Todos</option>';

        produtos = {};

        lista.forEach(produto => {

            const key = produto.nome;
            produtos[key] = produto;

            select.innerHTML += `
                <option value="${produto.nome}">
                    ${produto.nome}
                </option>
            `;

            filtro.innerHTML += `
                <option value="${produto.nome}">
                    ${produto.nome}
                </option>
            `;
        });

        const primeiro = lista[0];

        if (primeiro) {
            atualizarCard(primeiro.nome);
        }

    });
}

// ======================
// TROCAR PRODUTO
// ======================
function trocarProduto() {

    const nome = document.getElementById("selecionarProduto").value;
    atualizarCard(nome);

}

// ======================
// SELECIONAR TIPO
// ======================
function selecionarTipo(tipo) {

    tipoSelecionado = tipo;

    document.getElementById("entrada").style.opacity =
        tipo === "entrada" ? "1" : "0.5";

    document.getElementById("saida").style.opacity =
        tipo === "saida" ? "1" : "0.5";
}

// ======================
// ATUALIZAR CARD
// ======================
function atualizarCard(nome) {

    fetch(`http://localhost:5000/produto/${nome}`)
    .then(res => res.json())
    .then(p => {

        document.getElementById("nomeProduto").innerText = p.nome;
        document.getElementById("codigoProduto").innerText = p.codigo;

        const estoque = p.estoque ?? 0;
        const minimo = p.quantidade_minima ?? 0;

        document.getElementById("estoqueAtual").innerText = estoque;
        document.getElementById("estoqueMinimo").innerText = minimo;

        const alerta = document.getElementById("alertaEstoque");

        if (estoque === 0) {

            alerta.innerText = "❌ Estoque zerado!";
            alerta.style.background = "#f8d7da";
            alerta.style.color = "#721c24";

        } else if (estoque < minimo) {

            alerta.innerText = "⚠ Estoque baixo!";
            alerta.style.background = "#fff3cd";
            alerta.style.color = "#856404";

        } else {

            alerta.innerText = "✅ Estoque normal";
            alerta.style.background = "#d4edda";
            alerta.style.color = "#155724";

        }

    });

}

// ======================
// REGISTRAR MOVIMENTAÇÃO
// ======================
function registrar() {

    const produto = document.getElementById("selecionarProduto").value;
    const quantidade = parseInt(document.getElementById("quantidade").value);

    if (!produto || !quantidade || !tipoSelecionado) {

        Swal.fire({
            icon: "warning",
            title: "Campos obrigatórios",
            text: "Preencha todos os campos antes de continuar.",
            confirmButtonColor: "#3085d6"
        });

        return;
    }

    const estoqueAtual = parseInt(
        document.getElementById("estoqueAtual").innerText
    );

    const estoqueMinimo = parseInt(
        document.getElementById("estoqueMinimo").innerText
    );

    if (tipoSelecionado === "saida" && quantidade > estoqueAtual) {

        Swal.fire({
            icon: "error",
            title: "Estoque insuficiente!",
            text: "Você não tem essa quantidade disponível.",
            confirmButtonColor: "#d33"
        });

        document.getElementById("mensagem").innerText =
            "❌ Estoque insuficiente!";

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
            produto_nome: produto,
            tipo: tipoSelecionado,
            quantidade: quantidade
        })
    })
    .then(res => res.json())
    .then(data => {

        document.getElementById("quantidade").value = "";

        atualizarCard(produto);
        carregarHistorico();

        let novoEstoque = estoqueAtual;

        if (tipoSelecionado === "saida") {
            novoEstoque = estoqueAtual - quantidade;
        } else {
            novoEstoque = estoqueAtual + quantidade;
        }

        if (tipoSelecionado === "saida") {

            if (novoEstoque === 0) {

                Swal.fire({
                    icon: "error",
                    title: "Estoque zerado!",
                    text: "Este produto ficou sem unidades.",
                    confirmButtonColor: "#d33"
                });

                document.getElementById("mensagem").innerText =
                    "❌ Estoque zerado!";

            } else if (novoEstoque <= estoqueMinimo) {

                Swal.fire({
                    icon: "warning",
                    title: "Estoque baixo!",
                    text: `Quantidade abaixo do mínimo (${estoqueMinimo}). Restam ${novoEstoque} unidades.`,
                    confirmButtonColor: "#f39c12"
                });

                document.getElementById("mensagem").innerText =
                    `⚠️ Estoque abaixo do mínimo! Restam ${novoEstoque} unidades.`;

            } else {

                Swal.fire({
                    icon: "success",
                    title: "Movimentação registrada!",
                    text: data.mensagem,
                    confirmButtonColor: "#28a745"
                });

                document.getElementById("mensagem").innerText = data.mensagem;
            }

        } else {

            Swal.fire({
                icon: "success",
                title: "Entrada registrada!",
                text: data.mensagem,
                confirmButtonColor: "#28a745"
            });

            document.getElementById("mensagem").innerText = data.mensagem;

        }

    });

}

// ======================
// HISTÓRICO
// ======================
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

            let dataFormatada = item.data;

            if (item.data.includes("-")) {

                const partes = item.data.split(" ");
                const data = partes[0].split("-");
                const hora = partes[1];

                dataFormatada =
                    data[2] + "/" +
                    data[1] + "/" +
                    data[0] + " " +
                    hora;
            }

            const linha = document.createElement("tr");

            linha.innerHTML = `
                <td>${dataFormatada}</td>
                <td>${item.produto}</td>
                <td>${item.tipo}</td>
                <td>${item.quantidade}</td>
            `;

            tabela.appendChild(linha);

        });

    });

}

// TEMPO REAL
setInterval(carregarHistorico, 2000);
