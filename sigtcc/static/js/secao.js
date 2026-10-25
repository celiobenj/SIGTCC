/*
  Abre a aba Meu TCC já na seção indicada por ?secao= (orientacao, atas ou publicacao), escrito
  do zero (nenhum código do protótipo). O fragmento # se perde no POST do login; o parâmetro
  sobrevive ao "next" da spec 003 (research R12). Sem o parâmetro, com outro valor ou sem
  JavaScript, a página abre normalmente no topo.
  [US-17][US-19][US-45][US-46][FR-042][research R12]
*/
(function () {
  "use strict";

  var SECOES = ["orientacao", "atas", "publicacao"];
  var secao = new URLSearchParams(window.location.search).get("secao");
  if (SECOES.indexOf(secao) === -1) return;
  var alvo = document.getElementById(secao);
  if (alvo) alvo.scrollIntoView({ block: "start" });
})();
