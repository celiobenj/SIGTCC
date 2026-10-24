/*
  Contador de caracteres restantes, escrito do zero (nenhum código do protótipo). Só interface:
  para cada campo com data-contador="LIMITE", mostra abaixo dele quantos caracteres ainda cabem e
  atualiza durante a digitação. Campo desabilitado (somente leitura) não ganha contador. A regra
  do limite continua no formulário (maxlength no navegador e max_length no servidor).
  [US-13][RBN-CAD-07.1][FR-001] (passo 2 e E3 da US-13)
*/
(function () {
  "use strict";

  function ligarContador(campo) {
    var limite = parseInt(campo.getAttribute("data-contador"), 10);
    if (!limite || campo.disabled) return;
    var saida = document.createElement("div");
    saida.className = "dica";
    saida.setAttribute("aria-live", "polite");
    campo.insertAdjacentElement("afterend", saida);
    function atualizar() {
      saida.textContent = "Caracteres restantes: " + Math.max(limite - campo.value.length, 0);
    }
    campo.addEventListener("input", atualizar);
    atualizar();
  }

  document.querySelectorAll("[data-contador]").forEach(ligarContador);
})();
