/*
  Botão Adicionar da janela Ouvintes (spec 009, US2), escrito do zero (nenhum código do
  protótipo). Só interface: clona o modelo da linha vazia (empty_form do formset, com __prefix__)
  no fim da lista, troca __prefix__ pelo próximo índice e atualiza o TOTAL_FORMS. A regra (nome,
  matrícula, repetidos e o máximo de linhas) continua no servidor.
  [US-30][RBN-DEF-08.2]
*/
(function () {
  "use strict";

  var botao = document.querySelector("[data-adicionar-ouvinte]");
  var modelo = document.querySelector("[data-modelo-ouvinte]");
  var lista = document.querySelector("[data-linhas-ouvintes]");
  if (!botao || !modelo || !lista) return;
  var prefixo = botao.getAttribute("data-prefixo");
  var total = document.getElementById("id_" + prefixo + "-TOTAL_FORMS");
  var maximo = document.getElementById("id_" + prefixo + "-MAX_NUM_FORMS");

  botao.addEventListener("click", function () {
    var indice = parseInt(total.value, 10);
    if (maximo && indice >= parseInt(maximo.value, 10)) return;
    var html = modelo.innerHTML.replace(/__prefix__/g, String(indice));
    lista.insertAdjacentHTML("beforeend", html);
    total.value = String(indice + 1);
    var campos = lista.querySelectorAll("[data-linha-ouvinte]");
    var nova = campos[campos.length - 1].querySelector("input");
    if (nova) nova.focus();
  });
})();
