/*
  Mostra só a caixa do Tipo escolhido, escrito do zero (nenhum código do protótipo; só o
  comportamento visual de formCoorientador, de 17/10). Para cada <select data-alterna>, as caixas
  [data-tipo] do mesmo formulário ficam visíveis só quando data-tipo é igual ao valor escolhido;
  vale ao carregar (inclusive na reexibição com erro, que volta com o Tipo enviado) e a cada
  mudança. Sem JavaScript, as duas caixas aparecem e o servidor decide o que vale (o formulário
  continua funcionando). [US-45][RBN-CAD-10.3][FR-028]
*/
(function () {
  "use strict";

  function ligar(seletor) {
    var formulario = seletor.form;
    if (!formulario) return;
    var caixas = formulario.querySelectorAll("[data-tipo]");
    function alternar() {
      caixas.forEach(function (caixa) {
        caixa.hidden = caixa.getAttribute("data-tipo") !== seletor.value;
      });
    }
    seletor.addEventListener("change", alternar);
    alternar();
  }

  document.querySelectorAll("select[data-alterna]").forEach(ligar);
})();
