/*
 * Formulário "Avaliação" (spec 008, research A5): prévia da imagem de assinatura no navegador
 * (URL.createObjectURL), troca do rótulo para "Atualizar imagem" depois da primeira escolha e
 * conferência imediata de tamanho e extensão, com as mensagens da US-26 E2 e E3 trazidas pelo
 * próprio campo. Sem regra de negócio: a validação que vale é a do servidor no envio.
 * [US-26][RBN-DEF-05.2][FR-015][FR-016][FR-017]
 */
(function () {
  "use strict";

  var campo = document.querySelector("[data-arquivo-assinatura]");
  if (!campo) {
    return;
  }
  var previa = document.querySelector("[data-previa-assinatura]");
  var erro = document.querySelector("[data-erro-assinatura]");
  var rotulo = document.querySelector("[data-rotulo-arquivo]");
  var limite = parseInt(campo.getAttribute("data-limite"), 10);
  var urlAnterior = null;

  // Extensões aceitas no navegador (o servidor confere o conteúdo real). [US-26][FR-016]
  function extensaoAceita(nome) {
    return /\.(png|jpe?g)$/i.test(nome || "");
  }

  // Mostra a mensagem, limpa a escolha e mantém a prévia anterior. [US-26][FR-016]
  function recusar(mensagem) {
    erro.textContent = mensagem;
    campo.value = "";
  }

  campo.addEventListener("change", function () {
    var arquivo = campo.files && campo.files[0];
    erro.textContent = "";
    if (!arquivo) {
      return;
    }
    if (arquivo.size > limite) {
      recusar(campo.getAttribute("data-erro-tamanho"));
      return;
    }
    if (!extensaoAceita(arquivo.name)) {
      recusar(campo.getAttribute("data-erro-formato"));
      return;
    }
    if (urlAnterior) {
      URL.revokeObjectURL(urlAnterior);
    }
    urlAnterior = URL.createObjectURL(arquivo);
    previa.innerHTML = "";
    var imagem = document.createElement("img");
    imagem.className = "assin";
    imagem.alt = "Prévia da assinatura";
    imagem.src = urlAnterior;
    previa.appendChild(imagem);
    rotulo.textContent = rotulo.getAttribute("data-atualizar");
  });
})();
