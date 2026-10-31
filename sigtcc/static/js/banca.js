/*
  Seção Banca examinadora (US-23), escrita do zero (nenhum código do protótipo; só o comportamento
  visual de atualizarBanca e filtrarBanca, de 17/10). Sem JavaScript, as listas trazem todos os
  candidatos e o servidor recusa o que não vale (validar_banca).
  - Lista TCC [data-tcc]: mostra o Orientador (Presidente) da opção escolhida (data-orientador) e
    tira das listas da banca o orientador e os coorientadores (data-excluir).
  - Listas [data-banca], na ordem da tela: cada uma esconde quem já foi escolhido nas anteriores
    (o 2º Avaliador sem o 1º; o Suplente sem os dois).
  - Link [data-cadastrar-externo]: leva ao cadastro rápido os campos já preenchidos e o campo da
    banca em foco, para voltar com o Membro Externo já escolhido nele (contrato §3 da spec 002).
  [US-23][RBN-DEF-02.1][RBN-DEF-02.3][FR-007][FR-008][FR-010]
*/
(function () {
  "use strict";

  var formulario = document.querySelector("form select[data-banca]");
  if (!formulario) return;
  formulario = formulario.form;
  var listas = Array.prototype.slice.call(formulario.querySelectorAll("select[data-banca]"));
  var tcc = formulario.querySelector("select[data-tcc]");
  var presidente = document.getElementById("presidente");
  var emFoco = "";

  function excluidosDoTcc() {
    if (!tcc || !tcc.selectedOptions.length) return [];
    var valor = tcc.selectedOptions[0].getAttribute("data-excluir") || "";
    return valor ? valor.split(",") : [];
  }

  function atualizar() {
    var fora = excluidosDoTcc();
    if (tcc && presidente && tcc.selectedOptions.length) {
      presidente.value = tcc.selectedOptions[0].getAttribute("data-orientador") || "";
    }
    listas.forEach(function (lista, posicao) {
      var escolhidos = listas.slice(0, posicao).map(function (l) { return l.value; });
      Array.prototype.forEach.call(lista.options, function (opcao) {
        var esconder = !!opcao.value && (fora.indexOf(opcao.value) !== -1 || escolhidos.indexOf(opcao.value) !== -1);
        opcao.hidden = esconder;
        if (esconder && opcao.selected) lista.value = "";
      });
    });
  }

  listas.forEach(function (lista) {
    lista.addEventListener("change", atualizar);
    lista.addEventListener("focus", function () { emFoco = lista.getAttribute("data-banca"); });
  });
  if (tcc) tcc.addEventListener("change", atualizar);
  atualizar();

  var link = formulario.querySelector("[data-cadastrar-externo]");
  if (link) {
    link.addEventListener("click", function () {
      var url = new URL(link.href, window.location.href);
      var volta = new URL(url.searchParams.get("voltar") || window.location.pathname, window.location.href);
      new FormData(formulario).forEach(function (valor, nome) {
        if (nome !== "csrfmiddlewaretoken" && valor) volta.searchParams.set(nome, valor);
      });
      if (emFoco) volta.searchParams.set("campo", emFoco);
      url.searchParams.set("voltar", volta.pathname + volta.search);
      link.href = url.pathname + url.search;
    });
  }
})();
