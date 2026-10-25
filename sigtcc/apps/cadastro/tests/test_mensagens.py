"""Textos exatos das mensagens (SC-002): constantes de mensagens.py contra as US e a spec.

[SC-002][Q25][US-10][US-11][US-12][US-37][US-38]
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from sigtcc.apps.cadastro import mensagens

FONTE = Path(settings.BASE_DIR) / "docs" / "fonte"
SPEC = Path(settings.BASE_DIR) / "specs" / "003-acesso-login" / "spec.md"

# Textos e rótulos copiados das US (docs/fonte/Historias_de_Usuario_v3_4.md) que aparecem entre
# aspas no documento.
TEXTOS_DAS_US = (
    "LINK_ATIVACAO_ENVIADO",
    "CONTA_ATIVADA",
    "DADOS_NAO_ENCONTRADOS",
    "CONTA_JA_ATIVA",
    "EMAIL_INSTITUCIONAL",
    "MATRICULA_FORMATO",
    "EMAIL_DE_OUTRA_CONTA_ALUNO",
    "REGRA_SENHA",
    "SENHAS_NAO_CONFEREM",
    "LINK_SUBSTITUIDO",
    "CREDENCIAL_INVALIDA",
    "ACESSO_EXPIRADO",
    "CONTA_NAO_ATIVADA",
    "CONTA_INATIVA",
    "INFORME_CREDENCIAL",
    "SENHA_ALTERADA",
    "SENHA_ATUAL_INCORRETA",
    "ESQUECI_GENERICA",
    "LINK_INVALIDO_OU_VENCIDO",
    "LINK_ATIVACAO_VENCEU",
    "NOVO_LINK_ENVIADO",
    "PERFIL_ATUALIZADO",
    "SEM_NOTIFICACOES",
    "ITEM_INDISPONIVEL",
    "PRIMEIRO_ACESSO",
    "ESQUECI_MINHA_SENHA",
    "REENVIAR_LINK",
)

# Rótulos de botão e de menu que as US citam sem aspas (ex.: "o botão Entrar"): exigem o texto
# exato, sem as aspas. Enviar e Salvar passaram para cá na v3.4, que deixou de pôr os nomes de
# botão entre aspas. [Q-62][Q-77]
ROTULOS_DAS_US = (
    "ENTRAR",
    "ATIVAR_CONTA",
    "ALTERAR_SENHA",
    "RESETAR_PRIMEIRO_ACESSO",
    "MARCAR_COMO_LIDAS",
    "MEU_PERFIL",
    "ENVIAR",
    "SALVAR",
)

# Rótulos que vêm da spec 003 (FR-011: "Sair" no menu do usuário), não das US.
TEXTOS_DA_SPEC = ("SAIR",)


def _texto_corrido(caminho):
    """Texto do documento sem as quebras de linha das citações e sem espaços repetidos."""
    texto = caminho.read_text(encoding="utf-8")
    texto = re.sub(r"\n\s*>\s?", " ", texto)
    return re.sub(r"\s+", " ", texto)


def _mensagens_da_spec():
    """{"M-01": texto, ...} da tabela "Mensagens a validar com a PO" da spec 003."""
    textos = {}
    for linha in SPEC.read_text(encoding="utf-8").splitlines():
        achado = re.match(r'^\| (M-\d{2}) \| [^|]* \| "((?:[^"\\]|\\.)*)"', linha)
        if achado:
            textos[achado.group(1)] = achado.group(2).replace('\\"', '"')
    return textos


class MensagensTest(SimpleTestCase):
    """SC-002: cada mensagem é idêntica, caractere por caractere, à fonte. [SC-002]"""

    def test_textos_das_us(self):
        """Cada texto das US aparece entre aspas no documento das US."""
        historias = _texto_corrido(FONTE / "Historias_de_Usuario_v3_4.md")
        for nome in TEXTOS_DAS_US:
            texto = getattr(mensagens, nome)
            with self.subTest(constante=nome):
                self.assertIn(f'"{texto}', historias)

    def test_rotulos_das_us(self):
        """Cada rótulo citado sem aspas na v3.3 aparece com o texto exato no documento das US."""
        historias = _texto_corrido(FONTE / "Historias_de_Usuario_v3_4.md")
        for nome in ROTULOS_DAS_US:
            texto = getattr(mensagens, nome)
            with self.subTest(constante=nome):
                self.assertIn(texto, historias)

    def test_textos_da_spec(self):
        """Rótulos definidos na spec 003 aparecem entre aspas nela."""
        spec = _texto_corrido(SPEC)
        for nome in TEXTOS_DA_SPEC:
            with self.subTest(constante=nome):
                self.assertIn(f'"{getattr(mensagens, nome)}"', spec)

    def test_textos_da_matriz(self):
        """ "Código não reconhecido" vem da matriz (RBN-CAD-05.7)."""
        matriz = _texto_corrido(FONTE / "Matriz_Requisitos_17_10.md")
        self.assertIn(f'"{mensagens.CURSO_NAO_RECONHECIDO}"', matriz)

    def test_mensagens_provisorias_da_spec(self):
        """M-01 a M-17 são idênticas à tabela da spec (com N e NOME no lugar dos campos)."""
        da_spec = _mensagens_da_spec()
        self.assertEqual(sorted(da_spec), [f"M-{n:02d}" for n in range(1, 18)])
        for numero in range(1, 18):
            nome = next(n for n in dir(mensagens) if n.startswith(f"M{numero:02d}_"))
            texto = getattr(mensagens, nome).replace("{minutos}", "N").replace("{nome}", "NOME")
            with self.subTest(mensagem=f"M-{numero:02d}"):
                self.assertEqual(texto, da_spec[f"M-{numero:02d}"])
