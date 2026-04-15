let tipoSelecionado = "";

// Selecionar tipo (entrada/saida)
function selecionarTipo(tipo) {
    tipoSelecionado = tipo;

    // efeito visual (opcional)
    document.getElementById("entrada").style.opacity = tipo === "entrada" ? "1" : "0.5";
    document.getElementById("saida").style.opacity = tipo === "saida" ? "1" : "0.5";
}

// Registrar movimentação
function registrar() {
    const produto = document.getElementById("produto").value;
    const quantidade = document.getElementById("quantidade").value;

    fetch("http://localhost:5000/movimentacao", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            produto_nome: produto,
            tipo: tipoSelecionado,
            quantidade: parseInt(quantidade)
        })
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById("mensagem");

        if (data.sucesso) {
            msg.innerText = "✅ " + data.mensagem;
            msg.style.color = "green";
        } else {
            msg.innerText = "❌ " + (data.erro || "Erro ao registrar");
            msg.style.color = "red";
        }
    })
    .catch(err => {
        console.error(err);
        document.getElementById("mensagem").innerText = "Erro ao conectar com o servidor";
    });
}