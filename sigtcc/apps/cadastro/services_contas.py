"""Regras de negócio da Gestão de Contas (spec 002): docentes, Coordenador de Curso, Secretaria,
membros externos, inativação, validade, expiração e prorrogação.

Direção das importações (research C3): views_contas → services_contas → services → permissoes →
models; services_contas → sigtcc.apps.defesa.models. Este módulo nunca é importado por
permissoes.py nem por defesa/models.py.

Travas (research C19): sempre dentro de transaction.atomic(), na ordem Usuarios (id crescente) →
especialização (Docentes, Secretarios, MembrosExternos) → Cursos (id crescente) → trava consultiva
do e-mail (services.travar_email). Depois de travar, tudo o que decide a regra é relido.

[US-03][US-04][US-05][US-06][US-50][RBN-CAD-01.1 a 01.4][RBN-CAD-02.1 a 02.3]
[RBN-CAD-03.1 a 03.3][RBN-CAD-14.1]
"""

import logging
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import Count, Exists, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.urls import Resolver404, resolve
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from sigtcc.apps.cadastro import mensagens, services
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    StatusConta,
    StatusCoorientacao,
    StatusEntrega,
    StatusOrientacao,
    StatusSolicitacao,
    StatusTCC,
    StatusTurma,
    TipoEntrega,
    TipoSolicitacao,
)
from sigtcc.apps.cadastro.models import (
    Coordenadores,
    Coorientacoes,
    Cursos,
    Docentes,
    EntregasMarcos,
    MembrosExternos,
    Orientacoes,
    Secretarios,
    SolicitacoesOrientacao,
    TCCs,
    Turmas,
    Usuarios,
)
from sigtcc.apps.cadastro.permissoes import (
    curso_id_do_usuario,
    pode_gerir,
    professor_com_turma_ativa,
    tem_perfil,
    validade_vencida,
)
from sigtcc.apps.defesa.choices import StatusSessao
from sigtcc.apps.defesa.models import BancaDefesa

# Erros técnicos da Gestão de Contas, só com o tipo do erro (research C18, m3).
registro_contas = logging.getLogger("sigtcc.contas")

# =============================================================================================
# Recusa por curso (research C21)
# =============================================================================================


class ForaDoCurso(Exception):
    """Ação sobre registro de outro curso; a view mostra a mensagem com status 403.

    [US-03][US-04][RBN-CAD-14.1][FR-009][research C21]
    """

    def __init__(self, mensagem):
        """Guarda o texto do FR-009 que a view vai exibir. [FR-009]"""
        super().__init__(mensagem)
        self.mensagem = mensagem


def exigir_curso(usuario, registro, mensagem):
    """Levanta ForaDoCurso se o registro (Docentes ou Secretarios) não for do curso do usuário.

    Chamar depois de travar e reler o registro (o curso atual decide, Q5).
    [US-03][US-04][RBN-CAD-14.1][FR-009][Q5][Q26]
    """
    if not pode_gerir(usuario, registro):
        raise ForaDoCurso(mensagem)


# =============================================================================================
# Travas (research C19; B1)
# =============================================================================================

_ESPECIALIZACOES = ("alunos", "docentes", "membrosexternos", "secretarios")


def travar_contas(*usu_ids):
    """Trava as linhas de Usuarios em ordem crescente de id e as devolve relidas, por id.

    Só a linha de Usuarios é travada (o PostgreSQL não trava o lado opcional de um outer join).
    [research C19][B1]
    """
    ids = sorted({int(i) for i in usu_ids if i is not None})
    contas = (
        Usuarios.objects.select_related(*_ESPECIALIZACOES)
        .select_for_update(of=("self",))
        .filter(pk__in=ids)
        .order_by("pk")
    )
    return {conta.pk: conta for conta in contas}


def travar_conta(usu_id):
    """Trava e devolve a conta relida, ou None se não existir. [research C19][B1]"""
    return travar_contas(usu_id).get(int(usu_id))


def travar_cursos(*cur_ids):
    """Trava as linhas de Cursos em ordem crescente de id (C5, C19). [FR-014][FR-021]"""
    ids = sorted({int(i) for i in cur_ids if i is not None})
    return list(Cursos.objects.select_for_update().filter(pk__in=ids).order_by("pk"))


# =============================================================================================
# Listas de escolha e criação de vínculos (contrato de serviços 002, §1)
# =============================================================================================


def docentes_ativos():
    """Docentes com a conta 'Ativa': base das listas de orientador, coorientador, Professor da
    Disciplina e avaliador (as features donas aplicam os demais filtros).
    [US-04][RBN-CAD-01.3][FR-028]
    """
    return Docentes.objects.filter(doc__usu_status=StatusConta.ATIVA)


def membros_externos_disponiveis():
    """Todos os membros externos ('Aguardando Ativação', 'Ativa' e 'Expirada'): o Membro Externo
    não tem o status 'Inativa' (RBN-CAD-03.3), e a banca renova a validade (US-06 A1).
    [US-05][US-06][RBN-CAD-03.3][FR-028]
    """
    return MembrosExternos.objects.all()


def travar_e_conferir_ativo(usuario):
    """Trava a conta e confere, relida, se ela pode receber um vínculo novo.

    Docente: só 'Ativa'. Membro Externo: sempre (a banca renova a validade). Chamar na mesma
    transação do INSERT do vínculo, no POST (contrato §1; research B1).
    [US-04][RBN-CAD-01.3][FR-026][FR-028][B1]
    """
    conta = travar_conta(usuario.pk)
    if conta is None:
        return False
    if hasattr(conta, "membrosexternos"):
        return True
    return conta.usu_status == StatusConta.ATIVA


# =============================================================================================
# Atalho da banca (FR-034; research C23)
# =============================================================================================


def destino_interno(valor, request):
    """Caminho interno de "voltar" que resolve numa rota do sistema, ou None.

    Aceita só caminho relativo começando com "/" (sem "//"), do próprio host, e que resolve numa
    rota existente. [US-05][RBN-DEF-02.3][FR-034][research C23][m1]
    """
    if not valor or not valor.startswith("/") or valor.startswith("//"):
        return None
    if not url_has_allowed_host_and_scheme(
        valor, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return None
    try:
        resolve(urlsplit(valor).path)
    except Resolver404:
        return None
    return valor


def com_parametro(caminho, nome, valor):
    """Acrescenta (ou troca) um parâmetro na query do caminho, preservando os demais.

    [US-05][FR-034][research C23]
    """
    partes = urlsplit(caminho)
    parametros = [(k, v) for k, v in parse_qsl(partes.query, keep_blank_values=True) if k != nome]
    parametros.append((nome, str(valor)))
    return urlunsplit(partes._replace(query=urlencode(parametros)))


# =============================================================================================
# Erros e resultados comuns (FR-001 a FR-006)
# =============================================================================================


class ErroDeCampo(Exception):
    """Regra recusada que a view mostra junto de um campo (ou no topo, com campo None).

    [US-03][US-05][FR-001][FR-006][FR-014][FR-021]
    """

    def __init__(self, campo, mensagem):
        """campo: nome do campo do formulário ou None; mensagem: texto da US ou da tabela MC."""
        super().__init__(mensagem)
        self.campo = campo
        self.mensagem = mensagem


@dataclass(frozen=True)
class Resultado:
    """Mensagem a mostrar depois de gravar (sucesso, ou aviso na MC-13) e a conta afetada.

    [US-03][US-05][FR-008][FR-015][FR-016]
    """

    mensagem: str
    conta: object = None
    aviso: bool = False


def _nomes_alterados(antes, depois):
    """Nomes dos campos que mudaram, para o log (nunca os valores; research C18). [FR-047]"""
    return ",".join(sorted(campo for campo in depois if antes.get(campo) != depois[campo]))


def _conferir_email_livre(email, exceto=None):
    """Trava o e-mail (C4) e recusa se outra conta já o usa (FR-001). Exige transação aberta.

    [US-03][US-05][FR-001][research C4]
    """
    services.travar_email(email)
    if services.email_em_uso(email, exceto=exceto):
        raise ErroDeCampo("email", mensagens.EMAIL_JA_CADASTRADO)


def _gravar(funcao):
    """Roda a gravação. IntegrityError de unicidade vira a mensagem da regra; outro erro de banco
    vira "Não foi possível salvar. Tente novamente" (FR-006, US-03 E10), sem gravar nada.
    [US-03][US-04][US-05][FR-006][FR-030]
    """
    try:
        return funcao()
    except IntegrityError as erro:
        texto = str(erro)
        if "usu_email" in texto:
            raise ErroDeCampo("email", mensagens.EMAIL_JA_CADASTRADO) from None
        if "cor_cur" in texto or "cor_doc" in texto:
            raise ErroDeCampo("curso_coordenado", mensagens.CURSO_JA_TEM_COORDENADOR) from None
        registro_contas.error("Falha ao gravar conta: %s", type(erro).__name__)
        raise ErroDeCampo(None, mensagens.FALHA_AO_SALVAR) from None
    except DatabaseError as erro:
        registro_contas.error("Falha ao gravar conta: %s", type(erro).__name__)
        raise ErroDeCampo(None, mensagens.FALHA_AO_SALVAR) from None


# =============================================================================================
# Docentes e papel de Coordenador (US-03; FR-012 a FR-019; research C5, C6, C17)
# =============================================================================================


def _coordenador_do_curso(cur_id):
    """Linha de Coordenadores do curso, ou None. [FR-014]"""
    return Coordenadores.objects.filter(cor_cur_id=cur_id).first()


def _criar_docente(dados, autor):
    """Núcleo do cadastro de Docente, sem conferir permissão (tela e comando dos Coordenadores).

    dados: nome, email (normalizado), titulacao, curso_lotacao (Cursos), coordenador (bool) e
    curso_coordenado (Cursos ou None). Ordem: curso já tem Coordenador → e-mail (quickstart, C17).
    Cria a conta 'Aguardando Ativação', sem senha e sem enviar e-mail (Q1).
    [US-03][RBN-CAD-01.1][RAN-CAD-01][FR-005][FR-012][FR-014][FR-045][research C6][C17]
    """
    coordenado = dados["curso_coordenado"] if dados["coordenador"] else None

    def gravar():
        with transaction.atomic():
            travar_cursos(dados["curso_lotacao"].pk, coordenado.pk if coordenado else None)
            if coordenado is not None and _coordenador_do_curso(coordenado.pk):
                raise ErroDeCampo("curso_coordenado", mensagens.CURSO_JA_TEM_COORDENADOR)
            _conferir_email_livre(dados["email"])
            conta = Usuarios.objects.create_user(
                dados["email"], dados["nome"], usu_status=StatusConta.AGUARDANDO_ATIVACAO
            )
            docente = Docentes.objects.create(
                doc=conta, doc_titulacao=dados["titulacao"], doc_cur=dados["curso_lotacao"]
            )
            if coordenado is not None:
                Coordenadores.objects.create(cor_cur=coordenado, cor_doc=docente)
        return conta

    conta = _gravar(gravar)
    papel = " coordenador" if coordenado is not None else ""
    services.registrar_evento(
        services.EventoAcesso.CONTA_CRIADA,
        conta,
        autor=autor,
        detalhe=f"docente{papel} curso={dados['curso_lotacao'].pk}",
    )
    return conta


def cadastrar_docente(usuario, dados):
    """Cadastro de Docente pela Secretaria ou pelo Coordenador: o Curso de Lotação tem de ser o
    curso do usuário (US-03 E8, cenário 17); o Curso Coordenado pode ser qualquer curso sem
    Coordenador (cenário 33, Q5). Devolve Resultado com "Docente cadastrado com sucesso".
    [US-03][RBN-CAD-01.1][RBN-CAD-14.1][FR-009][FR-012][FR-015][Q5][Q6]
    """
    if not tem_perfil(usuario, "secretaria", "coordenador"):
        raise PermissionDenied
    if curso_id_do_usuario(usuario) != dados["curso_lotacao"].pk:
        raise ErroDeCampo("curso_lotacao", mensagens.SO_DO_SEU_CURSO_CADASTRO)
    conta = _criar_docente(dados, autor=usuario)
    return Resultado(mensagens.DOCENTE_CADASTRADO, conta)


def docente_para_editar(usuario, doc_id):
    """Docente (Docentes) que o usuário pode alterar; ForaDoCurso fora do curso (US-03 E8; Q26).

    A busca é pela especialização: id de outro tipo de conta dá 404 (research C22).
    [US-03][RBN-CAD-01.2][RBN-CAD-14.1][FR-009][Q26]
    """
    if not tem_perfil(usuario, "secretaria", "coordenador"):
        raise PermissionDenied
    docente = get_object_or_404(Docentes.objects.select_related("doc", "doc_cur"), pk=doc_id)
    exigir_curso(usuario, docente, mensagens.SO_DO_SEU_CURSO_CADASTRO)
    return docente


def curso_coordenado_de(docente):
    """Curso (Cursos) coordenado pelo docente, ou None. [US-03][FR-013]"""
    linha = Coordenadores.objects.select_related("cor_cur").filter(cor_doc=docente).first()
    return linha.cor_cur if linha else None


def alterar_docente(usuario, doc_id, dados):
    """Alteração de Docente (US-03 A8 a A11): trava conta, docente e cursos (C19), relê, confere
    o curso atual (Q5, Q26) e grava só os campos editáveis (C20). Papel: cria, troca ou apaga a
    linha de Coordenadores (C6); docente 'Inativa' não recebe o papel (MC-10, Q32). Troca de
    e-mail: fluxo do gestor (FR-008). Devolve Resultado ("Dados atualizados", MC-12 ou MC-13).
    [US-03][RBN-CAD-01.2][FR-008][FR-009][FR-013][FR-014][FR-016][Q5][Q26][Q32][research C6]
    """
    docente_para_editar(usuario, doc_id)
    email_novo = _email_mudou(doc_id, dados.get("email"))
    if email_novo:
        _conferir_email_e_senha(usuario, email_novo, dados.get("sua_senha"), doc_id)
    novo = dados["curso_coordenado"] if dados["coordenador"] else None
    alterados = []

    def gravar():
        with transaction.atomic():
            conta = travar_conta(doc_id)
            docente = Docentes.objects.select_for_update().get(pk=doc_id)
            exigir_curso(usuario, docente, mensagens.SO_DO_SEU_CURSO_CADASTRO)
            atual = Coordenadores.objects.filter(cor_doc=docente).first()
            travar_cursos(
                docente.doc_cur_id,
                dados["curso_lotacao"].pk,
                atual.cor_cur_id if atual else None,
                novo.pk if novo else None,
            )
            if email_novo:
                _conferir_email_livre(email_novo, exceto=conta)
            muda_papel = novo is not None and (atual is None or atual.cor_cur_id != novo.pk)
            if muda_papel:
                if conta.usu_status == StatusConta.INATIVA:
                    raise ErroDeCampo("coordenador", mensagens.MC10_STATUS_INCOMPATIVEL)
                if _coordenador_do_curso(novo.pk):
                    raise ErroDeCampo("curso_coordenado", mensagens.CURSO_JA_TEM_COORDENADOR)
            antes = {
                "nome": conta.usu_nome,
                "titulacao": docente.doc_titulacao,
                "curso_lotacao": docente.doc_cur_id,
                "curso_coordenado": atual.cor_cur_id if atual else None,
            }
            if atual is not None and (novo is None or atual.cor_cur_id != novo.pk):
                atual.delete()
            if muda_papel:
                Coordenadores.objects.create(cor_cur=novo, cor_doc=docente)
            conta.usu_nome = dados["nome"]
            conta.save(update_fields=["usu_nome"])
            docente.doc_titulacao = dados["titulacao"]
            docente.doc_cur = dados["curso_lotacao"]
            docente.save(update_fields=["doc_titulacao", "doc_cur"])
            depois = {
                "nome": conta.usu_nome,
                "titulacao": docente.doc_titulacao,
                "curso_lotacao": docente.doc_cur_id,
                "curso_coordenado": novo.pk if novo else None,
            }
            alterados.append(_nomes_alterados(antes, depois))
        return conta

    conta = _gravar(gravar)
    services.registrar_evento(
        services.EventoAcesso.CONTA_ALTERADA,
        conta,
        autor=usuario,
        detalhe="docente campos=" + (alterados[0] or "-"),
    )
    return _depois_de_alterar(usuario, conta, email_novo)


# =============================================================================================
# Secretaria (US-03 A4 e A5; FR-020 a FR-023; research C5)
# =============================================================================================

_OCUPAM_O_CURSO = (StatusConta.AGUARDANDO_ATIVACAO, StatusConta.ATIVA)


def _curso_tem_secretaria(cur_id, exceto=None):
    """O curso já tem Secretaria 'Aguardando Ativação' ou 'Ativa' (Q7). [FR-021]"""
    secretarias = Secretarios.objects.filter(sec_cur_id=cur_id, sec__usu_status__in=_OCUPAM_O_CURSO)
    if exceto is not None:
        secretarias = secretarias.exclude(pk=exceto)
    return secretarias.exists()


def cadastrar_secretaria(usuario, dados):
    """Cadastro da Secretaria pelo Coordenador, só no curso dele (FR-009, FR-020); o curso não
    pode ter outra Secretaria não inativa (FR-021, Q7). Sem e-mail (Q1).
    [US-03][RBN-CAD-02.1][RBN-CAD-14.1][FR-005][FR-020][FR-021][Q7]
    """
    if not tem_perfil(usuario, "coordenador"):
        raise PermissionDenied
    curso = dados["curso_vinculado"]
    if curso_id_do_usuario(usuario) != curso.pk:
        raise ErroDeCampo("curso_vinculado", mensagens.SO_DO_SEU_CURSO_CADASTRO)

    def gravar():
        with transaction.atomic():
            travar_cursos(curso.pk)
            if _curso_tem_secretaria(curso.pk):
                raise ErroDeCampo("curso_vinculado", mensagens.CURSO_JA_TEM_SECRETARIA)
            _conferir_email_livre(dados["email"])
            conta = Usuarios.objects.create_user(
                dados["email"], dados["nome"], usu_status=StatusConta.AGUARDANDO_ATIVACAO
            )
            Secretarios.objects.create(sec=conta, sec_cur=curso)
        return conta

    conta = _gravar(gravar)
    services.registrar_evento(
        services.EventoAcesso.CONTA_CRIADA,
        conta,
        autor=usuario,
        detalhe=f"secretaria curso={curso.pk}",
    )
    return Resultado(mensagens.SECRETARIA_CADASTRADA, conta)


def secretaria_para_editar(usuario, sec_id):
    """Secretaria (Secretarios) que o Coordenador pode alterar; ForaDoCurso fora do curso.

    [US-03][RBN-CAD-02.2][FR-009][FR-022]
    """
    if not tem_perfil(usuario, "coordenador"):
        raise PermissionDenied
    secretaria = get_object_or_404(Secretarios.objects.select_related("sec", "sec_cur"), pk=sec_id)
    exigir_curso(usuario, secretaria, mensagens.SO_DO_SEU_CURSO_CADASTRO)
    return secretaria


def alterar_secretaria(usuario, sec_id, dados):
    """Alteração da Secretaria pelo Coordenador do curso (US-03 A5): Nome, E-mail e Curso
    Vinculado; o curso de destino não pode ter outra Secretaria não inativa (cenário 38).
    [US-03][RBN-CAD-02.2][FR-008][FR-009][FR-021][FR-022][Q7][research C5][C20]
    """
    secretaria_para_editar(usuario, sec_id)
    email_novo = _email_mudou(sec_id, dados.get("email"))
    if email_novo:
        _conferir_email_e_senha(usuario, email_novo, dados.get("sua_senha"), sec_id)
    destino = dados["curso_vinculado"]
    alterados = []

    def gravar():
        with transaction.atomic():
            conta = travar_conta(sec_id)
            secretaria = Secretarios.objects.select_for_update().get(pk=sec_id)
            exigir_curso(usuario, secretaria, mensagens.SO_DO_SEU_CURSO_CADASTRO)
            travar_cursos(secretaria.sec_cur_id, destino.pk)
            if email_novo:
                _conferir_email_livre(email_novo, exceto=conta)
            if destino.pk != secretaria.sec_cur_id and conta.usu_status in _OCUPAM_O_CURSO:
                if _curso_tem_secretaria(destino.pk, exceto=secretaria.pk):
                    raise ErroDeCampo("curso_vinculado", mensagens.CURSO_JA_TEM_SECRETARIA)
            antes = {"nome": conta.usu_nome, "curso_vinculado": secretaria.sec_cur_id}
            conta.usu_nome = dados["nome"]
            conta.save(update_fields=["usu_nome"])
            secretaria.sec_cur = destino
            secretaria.save(update_fields=["sec_cur"])
            depois = {"nome": conta.usu_nome, "curso_vinculado": secretaria.sec_cur_id}
            alterados.append(_nomes_alterados(antes, depois))
        return conta

    conta = _gravar(gravar)
    services.registrar_evento(
        services.EventoAcesso.CONTA_ALTERADA,
        conta,
        autor=usuario,
        detalhe="secretaria campos=" + (alterados[0] or "-"),
    )
    return _depois_de_alterar(usuario, conta, email_novo)


# =============================================================================================
# Troca de e-mail pelo gestor (FR-008; Q17, Q24, Q28, Q30, Q31, Q35; research C7)
# =============================================================================================


def _email_mudou(usu_id, email):
    """E-mail novo (normalizado) se for diferente do atual sem diferenciar maiúsculas, senão None.

    Só a caixa diferente não abre troca (m12). [US-03][US-05][FR-008][research C7]
    """
    if not email:
        return None
    atual = Usuarios.objects.filter(pk=usu_id).values_list("usu_email", flat=True).first()
    return None if (atual or "").lower() == email.lower() else email


def _conferir_email_e_senha(usuario, email_novo, senha, usu_id):
    """Antes de gravar: e-mail novo já usado por outra conta → "Este e-mail já está cadastrado"
    (US-03 cenário 30; FR-008, validações do cadastro); depois, "Sua senha" (MC-11). A
    unicidade é conferida de novo, com trava, na gravação. [US-03][US-05][FR-001][FR-008]
    """
    if services.email_em_uso(email_novo, exceto=Usuarios(pk=usu_id)):
        raise ErroDeCampo("email", mensagens.EMAIL_JA_CADASTRADO)
    _conferir_senha_do_gestor(usuario, senha, usu_id)


def _conferir_senha_do_gestor(usuario, senha, usu_id):
    """Confere "Sua senha" de quem altera (FR-008); errada: MC-11 e log, sem limite (Q35).

    [US-03][US-05][FR-008][Q17][Q35][research C7]
    """
    if not senha or not services.senha_atual_confere(usuario, senha):
        conta = Usuarios.objects.filter(pk=usu_id).first()
        services.registrar_evento(
            services.EventoAcesso.SENHA_GESTOR_INCORRETA, conta, autor=usuario
        )
        raise ErroDeCampo("sua_senha", mensagens.MC11_SENHA_INCORRETA)


def _depois_de_alterar(usuario, conta, email_novo):
    """Depois de gravar os demais campos, pede a troca de e-mail numa transação própria (Q24).

    Sem e-mail novo: "Dados atualizados". Com e-mail novo: MC-12 ou, se o envio falhar, MC-13
    (os demais campos já ficaram gravados). [US-03][US-05][FR-008][Q17][Q24][research C7]
    """
    if not email_novo:
        return Resultado(mensagens.DADOS_ATUALIZADOS, conta)
    try:
        with transaction.atomic():
            services.travar_email(email_novo)
            services.pedir_troca_email(conta, email_novo, autor=usuario)
    except services.EmailEmUso:
        raise ErroDeCampo("email", mensagens.EMAIL_JA_CADASTRADO) from None
    except services.FalhaEnvioEmail:
        return Resultado(mensagens.MC13_FALHA_ENVIO_TROCA, conta, aviso=True)
    return Resultado(mensagens.MC12_TROCA_EMAIL_ENVIADA, conta)


# =============================================================================================
# Listas de docentes e de Secretarias (FR-017, FR-018, FR-023; RBN-CAD-11.3; research C9, C10)
# =============================================================================================

LIMITE_ORIENTANDOS = 5


def filtro_de_curso(usuario, valor):
    """Curso do filtro: "todos", o id de um curso existente ou, sem valor válido, o curso do
    usuário (RBN-CAD-14.1). Devolve (cur_id ou None para todos, valor para o template).
    [US-03][RBN-CAD-14.1][FR-018][research C10]
    """
    if valor == "todos":
        return None, "todos"
    if valor and valor.isdigit() and Cursos.objects.filter(pk=int(valor)).exists():
        return int(valor), valor
    padrao = curso_id_do_usuario(usuario)
    return padrao, str(padrao) if padrao is not None else "todos"


def _contagem_de_orientandos(descricao):
    """Subconsulta: TCCs com orientação 'Ativa' do docente em turma da descrição (TCC 1 ou 2).

    [US-03][RBN-CAD-11.3][FR-017][Q8][research C9]
    """
    contagem = (
        Orientacoes.objects.filter(
            ori_doc=OuterRef("pk"),
            ori_status=StatusOrientacao.ATIVA,
            ori_tcc__tcc_tur__tur_descricao=descricao,
        )
        .order_by()
        .values("ori_doc")
        .annotate(total=Count("ori_tcc", distinct=True))
        .values("total")
    )
    return Coalesce(Subquery(contagem), Value(0))


def listar_docentes(usuario, cur_id):
    """Docentes do curso (ou de todos), com papéis, Curso Coordenado e orientandos em TCC 1 e
    TCC 2, numa consulta (C9). pode_gerir marca as linhas do curso do usuário (FR-019).
    [US-03][RBN-CAD-01.4][RBN-CAD-11.3][FR-017][FR-018][FR-019][Q8]
    """
    docentes = Docentes.objects.select_related("doc", "doc_cur").annotate(
        coordenado=Subquery(
            Coordenadores.objects.filter(cor_doc=OuterRef("pk")).values("cor_cur__cur_nome")[:1]
        ),
        professor=Exists(Turmas.objects.filter(tur_doc=OuterRef("pk"))),
        orientador=Exists(
            Orientacoes.objects.filter(ori_doc=OuterRef("pk"), ori_status=StatusOrientacao.ATIVA)
        ),
        coorientador=Exists(
            Coorientacoes.objects.filter(
                coo_doc=OuterRef("pk"), coo_status=StatusCoorientacao.ATIVA
            )
        ),
        tcc1=_contagem_de_orientandos(DescricaoTurma.TCC_1),
        tcc2=_contagem_de_orientandos(DescricaoTurma.TCC_2),
    )
    if cur_id is not None:
        docentes = docentes.filter(doc_cur_id=cur_id)
    meu_curso = curso_id_do_usuario(usuario)
    linhas = []
    for docente in docentes.order_by("doc__usu_nome"):
        papeis = [
            rotulo
            for marcado, rotulo in (
                (docente.coordenado, "Coordenador de Curso"),
                (docente.professor, "Professor da Disciplina"),
                (docente.orientador, "Orientador"),
                (docente.coorientador, "Coorientador"),
            )
            if marcado
        ]
        linhas.append(
            {
                "docente": docente,
                "papeis": papeis or ["Docente"],
                "total": docente.tcc1 + docente.tcc2,
                "acima_do_limite": docente.tcc1 + docente.tcc2 > LIMITE_ORIENTANDOS,
                "pode_gerir": meu_curso is not None and meu_curso == docente.doc_cur_id,
            }
        )
    return linhas


def listar_secretarias(usuario, cur_id):
    """Secretarias do curso (ou de todos); só o Coordenador do curso as gerencia (FR-023).

    [US-03][US-04][RBN-CAD-02.1][FR-023]
    """
    secretarias = Secretarios.objects.select_related("sec", "sec_cur").order_by("sec__usu_nome")
    if cur_id is not None:
        secretarias = secretarias.filter(sec_cur_id=cur_id)
    coordenador = tem_perfil(usuario, "coordenador")
    meu_curso = curso_id_do_usuario(usuario)
    return [
        {
            "secretaria": secretaria,
            "pode_gerir": coordenador and meu_curso == secretaria.sec_cur_id,
        }
        for secretaria in secretarias
    ]


# =============================================================================================
# Membros Externos (US-05; FR-031 a FR-036, FR-038; research C11, C20, C22)
# =============================================================================================

PERFIS_MEMBROS = ("orientador", "professor_disciplina", "secretaria", "coordenador")
VALIDADE_SEM_BANCA = timedelta(days=30)


def hoje():
    """Data de hoje no fuso do servidor (USE_TZ = False), pelo relógio do Django. [US-06]"""
    return timezone.now().date()


def pode_ver_membros(usuario):
    """Menu e lista de Membros externos: Orientador, Professor da Disciplina (inclusive só com
    turmas arquivadas), Secretaria e Coordenador (FR-031). [US-05][RBN-CAD-03.1][FR-031][Q10]
    """
    return tem_perfil(usuario, *PERFIS_MEMBROS)


def pode_gerir_membros(usuario):
    """Cadastrar e alterar membros: Orientador, Secretaria, Coordenador ou Professor da
    Disciplina com turma não arquivada (FR-031; Q10, regra Q27 da spec 003).
    [US-05][RBN-CAD-03.1][RBN-CAD-03.2][FR-031][Q10]
    """
    if tem_perfil(usuario, "orientador", "secretaria", "coordenador"):
        return True
    return tem_perfil(usuario, "professor_disciplina") and professor_com_turma_ativa(usuario)


def pode_trocar_email(usuario, conta):
    """Troca do e-mail do Membro Externo com conta 'Ativa' ou 'Expirada' (inclusive 'Ativa'
    vencida): só Secretaria e Coordenador (Q30). Nas demais contas, quem pode alterar.
    [US-05][RBN-CAD-03.2][FR-008][FR-035][Q30]
    """
    if conta.usu_status in (StatusConta.ATIVA, StatusConta.EXPIRADA):
        return tem_perfil(usuario, "secretaria", "coordenador")
    return pode_gerir_membros(usuario)


def status_exibido(conta):
    """Status da conta para as telas: 'Ativa' com a validade vencida aparece como 'Expirada'
    (Edge Case; research C15). [US-06][RBN-CAD-03.3][FR-036]
    """
    if conta.usu_status == StatusConta.ATIVA and validade_vencida(conta):
        return StatusConta.EXPIRADA
    return conta.usu_status


def cadastrar_membro(usuario, dados):
    """Cadastro de Membro Externo (US-05): conta 'Aguardando Ativação', sem e-mail (Q1), com a
    validade inicial de 30 dias corridos a partir do cadastro (Q12, FR-038).
    [US-05][RBN-CAD-03.1][FR-005][FR-032][FR-033][FR-038][Q12]
    """
    if not pode_gerir_membros(usuario):
        raise PermissionDenied

    def gravar():
        with transaction.atomic():
            _conferir_email_livre(dados["email"])
            conta = Usuarios.objects.create_user(
                dados["email"], dados["nome"], usu_status=StatusConta.AGUARDANDO_ATIVACAO
            )
            MembrosExternos.objects.create(
                mem=conta,
                mem_titulacao=dados["titulacao"],
                mem_instituicao=dados["instituicao"],
                mem_validade_ate=hoje() + VALIDADE_SEM_BANCA,
            )
        return conta

    conta = _gravar(gravar)
    services.registrar_evento(
        services.EventoAcesso.CONTA_CRIADA, conta, autor=usuario, detalhe="membro_externo"
    )
    return Resultado(mensagens.MEMBRO_CADASTRADO, conta)


def membro_para_editar(usuario, mem_id):
    """Membro Externo (MembrosExternos) que o usuário pode alterar; id de outro tipo de conta dá
    404 (C22); sem permissão, PermissionDenied (M-02). [US-05][RBN-CAD-03.2][FR-035]
    """
    membro = get_object_or_404(MembrosExternos.objects.select_related("mem"), pk=mem_id)
    if not pode_gerir_membros(usuario):
        raise PermissionDenied
    return membro


def alterar_membro(usuario, mem_id, dados):
    """Alteração de Membro Externo (US-05 A2, A3, A6): Nome, Titulação e Instituição gravados com
    update_fields (C20); a alteração de conta 'Expirada' não reabre o acesso (A6). E-mail: fluxo
    do gestor (FR-008), só Secretaria e Coordenador em conta 'Ativa' ou 'Expirada' (Q30).
    [US-05][RBN-CAD-03.2][FR-008][FR-035][Q30][research C7][C20]
    """
    membro_para_editar(usuario, mem_id)
    email_novo = _email_mudou(mem_id, dados.get("email"))
    if email_novo:
        conta = Usuarios.objects.get(pk=mem_id)
        if not pode_trocar_email(usuario, conta):
            raise PermissionDenied
        _conferir_email_e_senha(usuario, email_novo, dados.get("sua_senha"), mem_id)
    alterados = []

    def gravar():
        with transaction.atomic():
            conta = travar_conta(mem_id)
            membro = MembrosExternos.objects.select_for_update().get(pk=mem_id)
            if email_novo:
                if not pode_trocar_email(usuario, conta):
                    raise PermissionDenied
                _conferir_email_livre(email_novo, exceto=conta)
            antes = {
                "nome": conta.usu_nome,
                "titulacao": membro.mem_titulacao,
                "instituicao": membro.mem_instituicao,
            }
            conta.usu_nome = dados["nome"]
            conta.save(update_fields=["usu_nome"])
            membro.mem_titulacao = dados["titulacao"]
            membro.mem_instituicao = dados["instituicao"]
            membro.save(update_fields=["mem_titulacao", "mem_instituicao"])
            depois = {
                "nome": conta.usu_nome,
                "titulacao": membro.mem_titulacao,
                "instituicao": membro.mem_instituicao,
            }
            alterados.append(_nomes_alterados(antes, depois))
        return conta

    conta = _gravar(gravar)
    services.registrar_evento(
        services.EventoAcesso.CONTA_ALTERADA,
        conta,
        autor=usuario,
        detalhe="membro_externo campos=" + (alterados[0] or "-"),
    )
    return _depois_de_alterar(usuario, conta, email_novo)


def listar_membros(usuario):
    """Todos os membros externos, sem filtro de Curso (Q19), com o status exibido (validade
    vencida = 'Expirada') e a validade. [US-05][US-50][RBN-CAD-03.1][FR-036][Q19]
    """
    pode_gerir_todos = pode_gerir_membros(usuario)
    linhas = []
    for membro in MembrosExternos.objects.select_related("mem").order_by("mem__usu_nome"):
        linhas.append(
            {
                "membro": membro,
                "status": status_exibido(membro.mem),
                "pode_editar": pode_gerir_todos,
            }
        )
    return linhas


# =============================================================================================
# Inativação e reativação (US-04; FR-024 a FR-030; research C8, C19)
# =============================================================================================

_TCC_ATIVO = (StatusTCC.EM_ANDAMENTO, StatusTCC.APTO_PARA_DEFESA)
_TCC_APROVADO = (StatusTCC.APROVADO, StatusTCC.APROVADO_COM_CORRECOES)
_SESSAO_EM_ABERTO = (StatusSessao.AGENDADA, StatusSessao.REAGENDADA, StatusSessao.EM_ANDAMENTO)


class VinculosEmAberto(Exception):
    """O docente tem vínculos que impedem a inativação; mensagem: o alerta do FR-027.

    [US-04][RBN-CAD-01.3][FR-026][FR-027]
    """

    def __init__(self, mensagem):
        """Guarda o alerta com todos os motivos. [FR-027]"""
        super().__init__(mensagem)
        self.mensagem = mensagem


def vinculos_do_docente(docente):
    """Quantidades dos cinco vínculos que impedem a inativação (US-04 E1 a E6; research C8).

    (a) TCCs com orientação ou coorientação 'Ativa' do docente em Em Andamento ou Apto para
    Defesa, ou Aprovado / Aprovado com Correções sem a Versão Final homologada, cada TCC uma
    vez; (b) convites de coorientação 'Aguardando Aceite'; (c) bancas de sessão Agendada,
    Reagendada ou Em Andamento; (d) turmas 'Ativa' do docente; (e) papel de Coordenador.
    'Sem Proposta' não impede (Q16).
    [US-04][RBN-CAD-01.3][FR-026][Q16][research C8]
    """
    versao_final_homologada = EntregasMarcos.objects.filter(
        ent_alu=OuterRef("tcc_alu"),
        ent_tma__tma_tur=OuterRef("tcc_tur"),
        ent_tma__tma_tipo=TipoEntrega.VERSAO_FINAL,
        ent_status=StatusEntrega.HOMOLOGADA,
    )
    com_o_docente = Q(
        orientacoes__ori_doc=docente, orientacoes__ori_status=StatusOrientacao.ATIVA
    ) | Q(coorientacoes__coo_doc=docente, coorientacoes__coo_status=StatusCoorientacao.ATIVA)
    tccs = (
        TCCs.objects.filter(com_o_docente)
        .annotate(homologada=Exists(versao_final_homologada))
        .filter(Q(tcc_status__in=_TCC_ATIVO) | Q(tcc_status__in=_TCC_APROVADO, homologada=False))
        .values("pk")
        .distinct()
    )
    return {
        "tcc_ativo": tccs.count(),
        "convites": SolicitacoesOrientacao.objects.filter(
            sol_doc=docente,
            sol_tipo=TipoSolicitacao.COORIENTACAO,
            sol_status=StatusSolicitacao.AGUARDANDO_ACEITE,
        ).count(),
        "bancas": BancaDefesa.objects.filter(
            ban_usu_id=docente.pk, ban_def__def_status__in=_SESSAO_EM_ABERTO
        )
        .values("ban_def")
        .distinct()
        .count(),
        "turmas": Turmas.objects.filter(tur_doc=docente, tur_status=StatusTurma.ATIVA).count(),
        "coordenador": Coordenadores.objects.filter(cor_doc=docente).exists(),
    }


def _plural(n, singular, plural):
    """Motivo (b) a (d) com concordância de número (Q14). [FR-027]"""
    return singular if n == 1 else plural.format(n=n)


def alerta_de_vinculos(contagens):
    """Alerta do FR-027 com todos os motivos, na ordem (a) a (e), ou None sem vínculos.

    "Não é possível inativar: o docente MOTIVOS"; com mais de um motivo, unidos por vírgulas e
    "e", terminando com ". Encerre ou transfira esses vínculos primeiro" (US-04 E1 e E6).
    O motivo (a) fica sempre no plural (Q18).
    [US-04][RBN-CAD-01.3][FR-027][Q14][Q18]
    """
    motivos = []
    if contagens["tcc_ativo"]:
        motivos.append(mensagens.MOTIVO_TCC_ATIVO.format(n=contagens["tcc_ativo"]))
    if contagens["convites"]:
        motivos.append(
            _plural(contagens["convites"], mensagens.MC05_CONVITE_1, mensagens.MC05_CONVITES)
        )
    if contagens["bancas"]:
        motivos.append(_plural(contagens["bancas"], mensagens.MC06_BANCA_1, mensagens.MC06_BANCAS))
    if contagens["turmas"]:
        motivos.append(_plural(contagens["turmas"], mensagens.MC07_TURMA_1, mensagens.MC07_TURMAS))
    if contagens["coordenador"]:
        motivos.append(mensagens.MOTIVO_COORDENADOR)
    if not motivos:
        return None
    if len(motivos) == 1:
        return mensagens.NAO_E_POSSIVEL_INATIVAR.format(motivos=motivos[0])
    texto = ", ".join(motivos[:-1]) + " e " + motivos[-1]
    return mensagens.NAO_E_POSSIVEL_INATIVAR.format(motivos=texto) + mensagens.FIM_ALERTA_VINCULOS


def docente_para_status(usuario, doc_id):
    """Docente que o usuário pode inativar ou reativar; fora do curso, ForaDoCurso com "Você só
    pode alterar dados do seu curso" (US-04 cenário 18). [US-04][RBN-CAD-14.1][FR-009]
    """
    if not tem_perfil(usuario, "secretaria", "coordenador"):
        raise PermissionDenied
    docente = get_object_or_404(Docentes.objects.select_related("doc"), pk=doc_id)
    exigir_curso(usuario, docente, mensagens.SO_DO_SEU_CURSO_ALTERACAO)
    return docente


def _mudar_status(usuario, conta, de, para, evento, detalhe):
    """Grava só usu_status (C20) e registra o evento. Exige a conta travada e relida. [FR-047]"""
    if conta.usu_status != de:
        raise ErroDeCampo(None, mensagens.MC10_STATUS_INCOMPATIVEL)
    conta.usu_status = para
    conta.save(update_fields=["usu_status"])
    return lambda: services.registrar_evento(evento, conta, autor=usuario, detalhe=detalhe)


def inativar_docente(usuario, doc_id):
    """Inativa o docente 'Ativa' sem vínculos (US-04 fluxo principal): trava a conta e o docente,
    repete a verificação de vínculos (E7, cenário 15) e grava 'Inativa'. Com vínculo: o alerta
    do FR-027, sem alterar nada. [US-04][RBN-CAD-01.3][FR-025][FR-026][FR-027][FR-030][B1]
    """
    docente_para_status(usuario, doc_id)
    registrar = []

    def gravar():
        with transaction.atomic():
            conta = travar_conta(doc_id)
            docente = Docentes.objects.select_for_update().get(pk=doc_id)
            exigir_curso(usuario, docente, mensagens.SO_DO_SEU_CURSO_ALTERACAO)
            if conta.usu_status != StatusConta.ATIVA:
                raise ErroDeCampo(None, mensagens.MC10_STATUS_INCOMPATIVEL)
            alerta = alerta_de_vinculos(vinculos_do_docente(docente))
            if alerta:
                raise VinculosEmAberto(alerta)
            registrar.append(
                _mudar_status(
                    usuario,
                    conta,
                    StatusConta.ATIVA,
                    StatusConta.INATIVA,
                    services.EventoAcesso.CONTA_INATIVADA,
                    "docente",
                )
            )
        return conta

    conta = _gravar(gravar)
    registrar[0]()
    return Resultado(mensagens.DOCENTE_INATIVADO, conta)


def reativar_docente(usuario, doc_id):
    """Reativa o docente 'Inativa' do curso do usuário (US-04 A1): volta a 'Ativa', com a senha
    que já tinha, como Docente comum. [US-04][RBN-CAD-01.3][FR-029][FR-030]
    """
    docente_para_status(usuario, doc_id)
    registrar = []

    def gravar():
        with transaction.atomic():
            conta = travar_conta(doc_id)
            docente = Docentes.objects.select_for_update().get(pk=doc_id)
            exigir_curso(usuario, docente, mensagens.SO_DO_SEU_CURSO_ALTERACAO)
            registrar.append(
                _mudar_status(
                    usuario,
                    conta,
                    StatusConta.INATIVA,
                    StatusConta.ATIVA,
                    services.EventoAcesso.CONTA_REATIVADA,
                    "docente",
                )
            )
        return conta

    conta = _gravar(gravar)
    registrar[0]()
    return Resultado(mensagens.MC02_DOCENTE_REATIVADO, conta)


def secretaria_para_status(usuario, sec_id):
    """Secretaria que o Coordenador do curso pode inativar (US-04 A2, E9). [FR-024]"""
    if not tem_perfil(usuario, "coordenador"):
        raise PermissionDenied
    secretaria = get_object_or_404(Secretarios.objects.select_related("sec"), pk=sec_id)
    exigir_curso(usuario, secretaria, mensagens.SO_DO_SEU_CURSO_ALTERACAO)
    return secretaria


def inativar_secretaria(usuario, sec_id):
    """Inativa a Secretaria 'Ativa' do curso (US-04 A2): perde o login, mantém o histórico e o
    curso fica livre para outra Secretaria (FR-021, FR-024; Q27: não há reativação).
    [US-04][RBN-CAD-02.3][FR-024][FR-030][Q27]
    """
    secretaria_para_status(usuario, sec_id)
    registrar = []

    def gravar():
        with transaction.atomic():
            conta = travar_conta(sec_id)
            secretaria = Secretarios.objects.select_for_update().get(pk=sec_id)
            exigir_curso(usuario, secretaria, mensagens.SO_DO_SEU_CURSO_ALTERACAO)
            registrar.append(
                _mudar_status(
                    usuario,
                    conta,
                    StatusConta.ATIVA,
                    StatusConta.INATIVA,
                    services.EventoAcesso.CONTA_INATIVADA,
                    "secretaria",
                )
            )
        return conta

    conta = _gravar(gravar)
    registrar[0]()
    return Resultado(mensagens.MC04_SECRETARIA_INATIVADA, conta)
