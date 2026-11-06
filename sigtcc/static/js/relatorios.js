/*
  Tela Relatórios (spec 010), escrita do zero; só facilita, e tudo funciona sem este arquivo.
  - Botão [data-expande]: recolhe a sub-lista da linha e alterna ao acionar. Enter e Espaço vêm do
    próprio botão. Sem JavaScript, as sub-listas ficam abertas.
  - Formulário [data-filtros]: envia ao trocar uma lista, nunca ao mexer num campo de data, para
    não enviar uma data incompleta. O botão Aplicar continua disponível.
  [US-31][RBN-REL-01.1][FR-025][FR-076][research R8]
*/
(function () {
  "use strict";

  document.querySelectorAll("[data-expande]").forEach(function (botao) {
    var linha = document.getElementById(botao.getAttribute("aria-controls"));
    if (!linha) return;
    function alternar(aberta) {
      linha.hidden = !aberta;
      botao.setAttribute("aria-expanded", String(aberta));
      botao.querySelector(".ms").textContent = aberta ? "expand_more" : "chevron_right";
    }
    alternar(false);
    botao.addEventListener("click", function () {
      alternar(linha.hidden);
    });
  });

  var formulario = document.querySelector("[data-filtros]");
  if (formulario) {
    formulario.querySelectorAll("select").forEach(function (lista) {
      lista.addEventListener("change", function () {
        formulario.submit();
      });
    });
  }
})();
