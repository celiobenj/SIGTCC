"""Textos exatos das mensagens da feature 006 (SC-003; FR-048): constantes de mensagens.py contra
as US-17, 18, 19, 20, 36, 41, 42, 45 e 46 (v3.3) e contra a tabela "Mensagens a validar com a PO"
da spec 006 (MO-01 a MO-26).

Mesmo padrão de test_mensagens_tcc.py. As linhas da tabela MO podem ter mais de um texto entre
aspas (formas de pedido e convite, de link e de notificação, e o assunto do e-mail); cada
constante MOxx_ precisa aparecer, entre aspas, na linha da sua MO. Os nomes dos campos variáveis
são normalizados para os da tabela ({data_hora} ↔ {data e hora}; {tipo} ↔ "{pedido de orientação
ou convite de coorientação}").

[SC-003][FR-048][US-17][US-18][US-19][US-20][US-36][US-41][US-42][US-45][US-46] (tasks T055)
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.tests.test_mensagens import _texto_corrido

FONTE = Path(settings.BASE_DIR) / "docs" / "fonte" / "Historias_de_Usuario_v3_4.md"
SPEC = Path(settings.BASE_DIR) / "specs" / "006-orientacao" / "spec.md"

# Textos copiados das US desta feature (T001), com os campos variáveis no formato da US.
TEXTOS_DAS_US = {
    "PEDIDO_ENVIADO": {"{docente}": "[nome do docente]"},
    "PROPOSTA_AINDA_NAO_REGISTRADA": {},
    "SEM_ORIENTADOR": {},
    "SEM_PROPOSTA": {},
    "PEDIDO_RECUSADO": {},
    "PEDIDO_NAO_DISPONIVEL": {},
    "PEDIDO_CANCELADO_PELO_ALUNO": {},
    "PEDIDO_CANCELADO_AGENDAMENTO": {},
    "CONVITE_ACEITO": {},
    "CONVITE_RECUSADO": {},
    "CONVITE_NAO_DISPONIVEL": {},
    "CONVITE_CANCELADO_PELO_ALUNO": {},
    "EMAIL_JA_COORIENTADOR": {},
    "ATA_REGISTRADA": {},
    "DATA_ENCONTRO_FUTURA": {},
    "CONFIRMAR_APTO": {"{nome}": "[nome do aluno]"},
    "TCC_INDICADO_APTO": {},
    "ENTREGA_DOCUMENTO_NAO_CADASTRADA": {},
    "PUBLICACAO_SALVA": {},
    "APROVEITAMENTO_HOMOLOGADO": {},
    "APROVEITAMENTO_RECUSADO": {},
}

NORMALIZA_MO = {
    "{data_hora}": "{data e hora}",
    "O {tipo} de": "O {pedido de orientação ou convite de coorientação} de",
}


def _historias():
    """Texto corrido das US, sem o escape do Markdown (ex.: "\\[nome\\]" vira "[nome]")."""
    return _texto_corrido(FONTE).replace("\\", "")


def _linhas_mo():
    """{"MO-01": linha inteira da tabela, ...} da spec 006."""
    linhas = {}
    for linha in SPEC.read_text(encoding="utf-8").splitlines():
        achado = re.match(r"^\| (MO-\d{2}) \|", linha)
        if achado:
            linhas[achado.group(1)] = linha
    return linhas


class MensagensOrientacaoTest(SimpleTestCase):
    """SC-003: cada mensagem é idêntica, caractere por caractere, à fonte. [SC-003][FR-048]"""

    def test_textos_das_us(self):
        historias = _historias()
        for nome, troca in TEXTOS_DAS_US.items():
            texto = getattr(mensagens, nome)
            for de, para in troca.items():
                texto = texto.replace(de, para)
            with self.subTest(constante=nome):
                self.assertIn(f'"{texto}', historias)

    def test_tabela_da_spec_tem_mo01_a_mo26(self):
        self.assertEqual(sorted(_linhas_mo()), [f"MO-{n:02d}" for n in range(1, 27)])

    def test_cada_mo_tem_constante(self):
        for numero in range(1, 27):
            with self.subTest(mensagem=f"MO-{numero:02d}"):
                nomes = [n for n in dir(mensagens) if n.startswith(f"MO{numero:02d}_")]
                self.assertTrue(nomes)

    def test_constantes_mo_iguais_a_tabela_da_spec(self):
        linhas = _linhas_mo()
        for nome in sorted(n for n in dir(mensagens) if re.match(r"MO\d{2}_", n)):
            numero = f"MO-{nome[2:4]}"
            texto = getattr(mensagens, nome)
            for de, para in NORMALIZA_MO.items():
                texto = texto.replace(de, para)
            with self.subTest(constante=nome):
                self.assertIn(f'"{texto}"', linhas[numero])
