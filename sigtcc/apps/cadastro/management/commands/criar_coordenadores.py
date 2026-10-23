"""Cria os Coordenadores de Curso iniciais na implantação (RNF de Instalabilidade do RAN-CAD-01).

Cada conta nasce como Docente 'Aguardando Ativação', lotada no curso e com o papel de Coordenador
dele, sem envio de e-mail; o primeiro acesso segue o RBN-CAD-06.2 (spec 002, Q1 e Q2). Funciona
em produção (ao contrário de criar_conta_teste). Os dados pessoais ficam num arquivo fora do
repositório; a saída não mostra e-mails (research C17).

Exemplos:
    python manage.py criar_coordenadores --arquivo C:\\caminho\\coordenadores.csv
    python manage.py criar_coordenadores --curso "Sistemas de Informação" --nome "Ana Souza"
        --email ana@uea.edu.br --titulacao Doutor

O CSV tem as colunas curso;nome;email;titulacao (UTF-8, com ou sem BOM, separador ";").

[RAN-CAD-01][RBN-CAD-06.2][FR-045][FR-046][research C17]
"""

import csv

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from sigtcc.apps.cadastro import mensagens
from sigtcc.apps.cadastro.choices import Titulacao
from sigtcc.apps.cadastro.forms_contas import validar_email_institucional, validar_nome_completo
from sigtcc.apps.cadastro.models import Coordenadores, Cursos
from sigtcc.apps.cadastro.services import AUTOR_SISTEMA
from sigtcc.apps.cadastro.services_contas import ErroDeCampo, _criar_docente

COLUNAS = ("curso", "nome", "email", "titulacao")


class Recusa(Exception):
    """Linha recusada, com o texto das telas de cadastro (FR-046).

    [RAN-CAD-01][RBN-CAD-06.2][FR-046]
    """


class Command(BaseCommand):
    """Comando criar_coordenadores. [FR-045][FR-046]"""

    help = (
        "Cria os Coordenadores de Curso iniciais (Docente 'Aguardando Ativação', sem e-mail). "
        "Prefira --arquivo: o --email digitado fica no histórico do shell."
    )

    def add_arguments(self, parser):
        """--arquivo (CSV curso;nome;email;titulacao) ou um curso por --curso --nome --email
        --titulacao. [FR-045]
        """
        parser.add_argument("--arquivo", help="CSV fora do repositório: curso;nome;email;titulacao")
        parser.add_argument("--curso", help="nome do curso, como em Cursos")
        parser.add_argument("--nome")
        parser.add_argument("--email", help="fica no histórico do shell; prefira --arquivo")
        parser.add_argument("--titulacao", help="Especialista, Mestre ou Doutor")

    def handle(self, *args, **opcoes):
        """Processa cada curso numa transação própria; os demais seguem se um for recusado.

        [FR-045][FR-046]
        """
        for linha in self._linhas(opcoes):
            curso = (linha.get("curso") or "").strip()
            try:
                self._criar(linha)
            except Recusa as recusa:
                self.stdout.write(f"{curso}: recusado: {recusa}")
            else:
                self.stdout.write(f"{curso}: criado")

    def _linhas(self, opcoes):
        """Linhas do CSV (--arquivo) ou a linha única das opções. [FR-045]"""
        if opcoes["arquivo"]:
            try:
                with open(opcoes["arquivo"], encoding="utf-8-sig", newline="") as arquivo:
                    leitor = csv.DictReader(arquivo, delimiter=";")
                    if tuple(c.strip() for c in (leitor.fieldnames or ())) != COLUNAS:
                        raise CommandError("O CSV deve ter as colunas curso;nome;email;titulacao.")
                    return [{k.strip(): v for k, v in linha.items()} for linha in leitor]
            except OSError as erro:
                raise CommandError(f"Não foi possível ler o arquivo: {type(erro).__name__}")
        if not all(opcoes.get(c) for c in COLUNAS):
            raise CommandError("Informe --arquivo ou --curso, --nome, --email e --titulacao.")
        return [{c: opcoes[c] for c in COLUNAS}]

    def _criar(self, linha):
        """Valida na ordem curso → curso já tem Coordenador → nome → titulação → e-mail
        (research C17) e cria com o núcleo do cadastro de docente, autor "sistema".
        [FR-014][FR-046]
        """
        curso = Cursos.objects.filter(cur_nome=(linha.get("curso") or "").strip()).first()
        if curso is None:
            raise Recusa(mensagens.OPCAO_INVALIDA)
        if Coordenadores.objects.filter(cor_cur=curso).exists():
            raise Recusa(mensagens.CURSO_JA_TEM_COORDENADOR)
        try:
            nome = validar_nome_completo(linha.get("nome"))
            titulacao = (linha.get("titulacao") or "").strip()
            if titulacao not in Titulacao.values:
                raise Recusa(mensagens.OPCAO_INVALIDA)
            email = validar_email_institucional(linha.get("email"))
            _criar_docente(
                {
                    "nome": nome,
                    "email": email,
                    "titulacao": titulacao,
                    "curso_lotacao": curso,
                    "coordenador": True,
                    "curso_coordenado": curso,
                },
                autor=AUTOR_SISTEMA,
            )
        except ValidationError as erro:
            raise Recusa(erro.messages[0]) from None
        except ErroDeCampo as erro:
            raise Recusa(erro.mensagem) from None
