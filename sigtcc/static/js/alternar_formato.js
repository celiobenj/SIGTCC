/*
  Formato da Sessão (US-21, fluxo alternativo B), escrito do zero (nenhum código do protótipo):
  mostra só a caixa [data-caixa-formato] do formato escolhido; ao trocar o formato, limpa o campo
  da caixa que fica escondida. Vale ao carregar (inclusive na reexibição com erro) e a cada
  mudança. Sem JavaScript, as duas caixas aparecem e o servidor descarta o campo do outro
  formato (DadosDaSessaoForm.clean). [US-21][US-24][RBN-DEF-01.1][FR-004]
*/
(function () {
  "use strict";

  document.querySelectorAll("select[data-formato]").forEach(function (seletor) {
    var formulario = seletor.form;
    if (!formulario) return;
    var caixas = formulario.querySelectorAll("[data-caixa-formato]");
    function alternar(limpar) {
      caixas.forEach(function (caixa) {
        var visivel = caixa.getAttribute("data-caixa-formato") === seletor.value;
        caixa.hidden = !visivel;
        if (!visivel && limpar) {
          caixa.querySelectorAll("input").forEach(function (campo) { campo.value = ""; });
        }
      });
    }
    seletor.addEventListener("change", function () { alternar(true); });
    alternar(false);
  });
})();
