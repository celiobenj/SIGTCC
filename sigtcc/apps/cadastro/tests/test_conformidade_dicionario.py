"""Conformidade do banco com o dicionário de dados de 18/10.

Lê o próprio documento-fonte (docs/fonte/Modelo_Logico_e_Dicionario_18_10.md) e compara com o
catálogo do PostgreSQL, para que SC-001 e SC-006 sejam verificados contra o dicionário e não
contra uma cópia (research R11). Índices não são comparados: não são colunas. As colunas são
comparadas por nome, não pela ordem física: o Django põe as FKs no fim da tabela e o modelo
relacional não dá significado à ordem (research R14, decisão de 2026-10-19).

[base de todas as US; sem RBN específica][spec 001, US1 cenários 1 a 5][FR-001][FR-002][FR-003]
[FR-004][FR-005][FR-020][SC-001][SC-006]
"""

import re
from functools import lru_cache

from django.conf import settings
from django.db import connection
from django.test import TestCase

from sigtcc.apps.cadastro.models import Cursos

CAMINHO_DICIONARIO = settings.BASE_DIR / "docs" / "fonte" / "Modelo_Logico_e_Dicionario_18_10.md"

# Tabelas internas do framework admitidas pela spec (FR-020), sem dados de negócio.
TABELAS_DO_FRAMEWORK = {
    "django_migrations",
    "django_content_type",
    "django_session",
    "auth_permission",
    "auth_group",
    "auth_group_permissions",
}


@lru_cache(maxsize=1)
def ler_dicionario():
    """Devolve {tabela: [(campo, tipo, nulo, chave, descricao), ...]} na ordem do dicionário."""
    texto = CAMINHO_DICIONARIO.read_text(encoding="utf-8")
    tabelas, atual = {}, None
    for linha in texto.splitlines():
        cabecalho = re.match(r"^### 3\.\d\.\d+ Tabela (\S+)", linha)
        if cabecalho:
            atual = cabecalho.group(1)
            tabelas[atual] = []
            continue
        if linha.startswith("#"):
            atual = None
        if atual and linha.startswith("| ") and not linha.startswith("| **"):
            celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
            if re.match(r"^[a-z_]+$", celulas[0]):
                campo, tipo, nulo, chave, descricao = celulas[:5]
                tabelas[atual].append((campo, tipo.replace(" ", ""), nulo, chave, descricao))
    return tabelas


@lru_cache(maxsize=1)
def ler_fks_do_modelo_logico():
    """Devolve {(tabela, coluna): tabela_destino} a partir da seção 2 do dicionário."""
    texto = CAMINHO_DICIONARIO.read_text(encoding="utf-8")
    secao = texto.split("# 2. MODELO LÓGICO RELACIONAL")[1].split("# 3. DICIONÁRIO DE DADOS")[0]
    secao = re.sub(r"\s+", " ", secao.replace("\\", ""))
    fks = {}
    for tabela, corpo in re.findall(r"\*\*\d+\. (\S+)\*\* \((.*?)\)\s*(?=\*\*\d+\.|$)", secao):
        for coluna, destino in re.findall(
            r"(?:<u>)?([a-z_]+)(?:</u>)?\*?\*? \*\[FK (\w+)[.(]", corpo
        ):
            fks[(tabela, coluna)] = destino
    return fks


def tipo_esperado(tipo):
    """Converte o tipo do dicionário em (data_type, tamanho, precisão, escala) do PostgreSQL."""
    if tipo == "INT":
        return ("integer", None, None, None)
    tamanho = re.match(r"^(VARCHAR|CHAR)\((\d+)\)$", tipo)
    if tamanho:
        nome = "character varying" if tamanho.group(1) == "VARCHAR" else "character"
        return (nome, int(tamanho.group(2)), None, None)
    decimal = re.match(r"^DECIMAL\((\d+),(\d+)\)$", tipo)
    if decimal:
        return ("numeric", None, int(decimal.group(1)), int(decimal.group(2)))
    simples = {
        "TIMESTAMP": "timestamp without time zone",
        "TIME": "time without time zone",
        "DATE": "date",
        "BOOLEAN": "boolean",
    }
    return (simples[tipo], None, None, None)


def consultar(sql, parametros=()):
    """Executa uma consulta no catálogo e devolve todas as linhas."""
    with connection.cursor() as cursor:
        cursor.execute(sql, parametros)
        return cursor.fetchall()


def colunas_do_banco(tabela):
    """Colunas da tabela no PostgreSQL, na ordem física."""
    return consultar(
        """
        SELECT column_name, data_type, character_maximum_length, numeric_precision,
               numeric_scale, is_nullable, is_identity, identity_generation
          FROM information_schema.columns
         WHERE table_schema = 'public' AND table_name = %s
         ORDER BY ordinal_position
        """,
        [tabela],
    )


def colunas_da_pk(tabela):
    """Colunas da chave primária da tabela, na ordem da chave."""
    return [
        linha[0]
        for linha in consultar(
            """
            SELECT kcu.column_name
              FROM information_schema.table_constraints tc
              JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
               AND tc.table_schema = kcu.table_schema
               AND tc.table_name = kcu.table_name
             WHERE tc.table_schema = 'public' AND tc.table_name = %s
               AND tc.constraint_type = 'PRIMARY KEY'
             ORDER BY kcu.ordinal_position
            """,
            [tabela],
        )
    ]


def fks_do_banco(tabela):
    """Lista de (colunas, tabela_destino, definição) das FKs da tabela no banco."""
    resultado = []
    for (definicao,) in consultar(
        """
        SELECT pg_get_constraintdef(oid)
          FROM pg_constraint
         WHERE contype = 'f' AND conrelid = %s::regclass
        """,
        [f'"{tabela}"'],
    ):
        partes = re.match(r'FOREIGN KEY \(([^)]*)\) REFERENCES "?(\w+)"?\(', definicao)
        colunas = tuple(c.strip() for c in partes.group(1).split(","))
        resultado.append((colunas, partes.group(2), definicao))
    return resultado


class EstruturaConformeDicionarioTest(TestCase):
    """Parte 1: tabelas e colunas (spec US1, cenários 1 e 2; FR-001, FR-002, FR-020)."""

    def test_dicionario_lido_por_inteiro(self):
        """Garante que o leitor encontrou as 36 tabelas e as 201 colunas do documento."""
        dicionario = ler_dicionario()
        self.assertEqual(len(dicionario), 36)
        self.assertEqual(sum(len(c) for c in dicionario.values()), 201)

    def test_cenario1_36_tabelas_sem_salas(self):
        """Dado um banco migrado, então existem as 36 tabelas do dicionário e nenhuma de Salas."""
        existentes = {
            t
            for (t,) in consultar(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        }
        faltando = set(ler_dicionario()) - existentes
        self.assertFalse(faltando, f"Tabelas do dicionário ausentes no banco: {sorted(faltando)}")
        salas = [t for t in existentes if "sala" in t.lower()]
        self.assertFalse(salas, f"Tabelas de Salas (fora do escopo desde 17/10): {salas}")

    def test_cenario2_colunas_conforme_dicionario(self):
        """Nome, tipo, tamanho, precisão e nulidade das 201 colunas iguais ao dicionário.

        A comparação é por nome; a ordem física não é verificada (research R14).
        """
        for tabela, campos in ler_dicionario().items():
            banco = {c[0]: c for c in colunas_do_banco(tabela)}
            with self.subTest(tabela=tabela):
                self.assertEqual(
                    sorted(banco),
                    sorted(c[0] for c in campos),
                    f"{tabela}: colunas diferentes do dicionário",
                )
            for campo, tipo, nulo, _chave, _desc in campos:
                coluna = banco.get(campo)
                if coluna is None:
                    continue  # a falta da coluna já é apontada pela verificação acima
                with self.subTest(tabela=tabela, coluna=campo):
                    nome_tipo, tamanho, precisao, escala = tipo_esperado(tipo)
                    self.assertEqual(coluna[1], nome_tipo, f"{tabela}.{campo}: tipo")
                    if tamanho is not None:
                        self.assertEqual(coluna[2], tamanho, f"{tabela}.{campo}: tamanho")
                    if precisao is not None:
                        self.assertEqual(
                            (coluna[3], coluna[4]),
                            (precisao, escala),
                            f"{tabela}.{campo}: precisão",
                        )
                    self.assertEqual(
                        coluna[5], "YES" if nulo == "Sim" else "NO", f"{tabela}.{campo}: nulidade"
                    )

    def test_sem_tabelas_fora_do_dicionario(self):
        """Só existem as 36 tabelas e as internas do framework (FR-020, SC-006)."""
        existentes = {
            t
            for (t,) in consultar(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        }
        extras = existentes - set(ler_dicionario()) - TABELAS_DO_FRAMEWORK
        self.assertFalse(extras, f"Tabelas fora do dicionário: {sorted(extras)}")

    def test_usuarios_tem_6_colunas(self):
        """Usuarios sem last_login, is_staff nem is_superuser (research D1)."""
        nomes = [c[0] for c in colunas_do_banco("Usuarios")]
        self.assertEqual(len(nomes), 6)
        for tecnica in ("last_login", "is_staff", "is_superuser"):
            self.assertNotIn(tecnica, nomes)


class ChavesEIdentidadeTest(TestCase):
    """Parte 2: chaves e identidade (spec US1, cenários 3, 4 e 5; FR-003, FR-004, FR-005)."""

    def test_pk_conforme_dicionario(self):
        """As colunas de cada PK (inclusive as 5 compostas) são as marcadas com PK no dicionário."""
        for tabela, campos in ler_dicionario().items():
            esperadas = [c[0] for c in campos if "PK" in c[3]]
            with self.subTest(tabela=tabela):
                self.assertEqual(colunas_da_pk(tabela), esperadas)

    def test_cenario3_avaliacoes(self):
        """PK composta de Avaliacoes e FK composta para Banca_Defesa, adiada (research D3)."""
        self.assertEqual(colunas_da_pk("Avaliacoes"), ["ava_def_id", "ava_usu_id", "ava_cri_id"])
        definicao = consultar(
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
            "WHERE conname = 'fk_avaliacoes_banca_defesa'"
        )
        self.assertEqual(
            definicao,
            [
                (
                    'FOREIGN KEY (ava_def_id, ava_usu_id) REFERENCES "Banca_Defesa"'
                    "(ban_def_id, ban_usu_id) DEFERRABLE INITIALLY DEFERRED",
                )
            ],
        )

    def test_cenario4_especializacoes(self):
        """A PK de Alunos, Docentes, MembrosExternos e Secretarios também é FK para Usuarios."""
        for tabela, coluna in (
            ("Alunos", "alu_id"),
            ("Docentes", "doc_id"),
            ("MembrosExternos", "mem_id"),
            ("Secretarios", "sec_id"),
        ):
            with self.subTest(tabela=tabela):
                self.assertEqual(colunas_da_pk(tabela), [coluna])
                self.assertIn(((coluna,), "Usuarios"), [(c, d) for c, d, _ in fks_do_banco(tabela)])

    def test_fks_conforme_modelo_logico(self):
        """Cada [FK Tabela.coluna] da seção 2 do dicionário existe no banco com o destino certo."""
        for (tabela, coluna), destino in ler_fks_do_modelo_logico().items():
            fks = [(c, d) for c, d, _ in fks_do_banco(tabela)]
            with self.subTest(tabela=tabela, coluna=coluna):
                if destino == "Banca_Defesa":
                    self.assertIn((("ava_def_id", "ava_usu_id"), "Banca_Defesa"), fks)
                else:
                    self.assertIn(((coluna,), destino), fks)
        # ava_def_id e ava_usu_id só participam da FK composta (sem FKs simples).
        simples = [c for c, _, _ in fks_do_banco("Avaliacoes") if len(c) == 1]
        self.assertNotIn(("ava_def_id",), simples)
        self.assertNotIn(("ava_usu_id",), simples)

    def test_cenario5_identidade_by_default(self):
        """Identificadores gerados pelo banco com BY DEFAULT (desvio aprovado em FR-003)."""
        for tabela, campos in ler_dicionario().items():
            identidades = [c[0] for c in campos if "GENERATED ALWAYS AS IDENTITY" in c[4]]
            colunas = {c[0]: c for c in colunas_do_banco(tabela)}
            for campo in identidades:
                with self.subTest(tabela=tabela, coluna=campo):
                    self.assertEqual(colunas[campo][6], "YES")
                    self.assertEqual(colunas[campo][7], "BY DEFAULT")
        curso = Cursos.objects.create(cur_nome="Curso de teste de identidade")
        self.assertIsInstance(curso.cur_id, int)
