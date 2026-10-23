/*
  Comportamento de tela do SIGTCC, escrito do zero (nenhum código do protótipo).
  Só interface: abrir e fechar o menu lateral, fechar avisos temporários e mostrar os ícones
  quando a fonte carrega. Nenhuma regra de negócio.
  [FR-024] research A14
*/
(function () {
  "use strict";

  // Mostra os ícones só depois que a fonte Material Symbols carrega.
  function ativarIcones() {
    if (!document.fonts || !document.fonts.load) {
      document.body.classList.add("icones");
      return;
    }
    document.fonts
      .load('24px "Material Symbols Outlined"', "home")
      .then(function (fontes) {
        if (fontes.length) document.body.classList.add("icones");
      })
      .catch(function () {});
  }

  // Botão da barra superior abre e fecha o menu lateral.
  function ligarMenuLateral() {
    var botao = document.querySelector("[data-alternar-menu]");
    var gaveta = document.getElementById("menu-lateral");
    if (!botao || !gaveta) return;
    // Em telas estreitas o menu começa recolhido.
    if (window.matchMedia("(max-width: 900px)").matches) gaveta.classList.add("oculto");
    botao.setAttribute("aria-expanded", String(!gaveta.classList.contains("oculto")));
    botao.addEventListener("click", function () {
      var oculto = gaveta.classList.toggle("oculto");
      botao.setAttribute("aria-expanded", String(!oculto));
    });
  }

  // Botão "x" fecha o aviso; avisos de sucesso somem sozinhos depois de alguns segundos.
  function ligarAvisos() {
    document.querySelectorAll("[data-fechar-aviso]").forEach(function (botao) {
      botao.addEventListener("click", function () {
        botao.closest(".alerta").remove();
      });
    });
    document.querySelectorAll(".alerta.sucesso[data-temporario]").forEach(function (aviso) {
      window.setTimeout(function () {
        aviso.remove();
      }, 8000);
    });
  }

  // Spec 002: mostra o campo Curso Coordenado só com a caixa "Coordenador de Curso" marcada. Só
  // apresentação: sem JavaScript o campo fica visível e o servidor o ignora sem a caixa (C6).
  function ligarCursoCoordenado() {
    document.querySelectorAll("[data-mostra-se-marcado]").forEach(function (bloco) {
      var caixa = document.getElementById(bloco.getAttribute("data-mostra-se-marcado"));
      if (!caixa) return;
      var atualizar = function () {
        bloco.hidden = !caixa.checked;
      };
      caixa.addEventListener("change", atualizar);
      atualizar();
    });
  }

  // Spec 002: desabilita o botão depois do primeiro envio (ex.: Prorrogar), contra clique duplo.
  function ligarEnvioUnico() {
    document.querySelectorAll("form[data-envio-unico]").forEach(function (formulario) {
      formulario.addEventListener("submit", function () {
        formulario.querySelectorAll("button[type=submit]").forEach(function (botao) {
          botao.disabled = true;
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ativarIcones();
    ligarMenuLateral();
    ligarAvisos();
    ligarCursoCoordenado();
    ligarEnvioUnico();
  });
})();
