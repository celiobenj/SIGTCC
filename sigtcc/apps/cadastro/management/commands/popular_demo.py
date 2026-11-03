"""Limpa o banco e carrega dados fictícios de demonstração (ambiente de validação, deploy).

Apaga todas as contas, turmas, TCCs, entregas, orientações, atas, publicações, notificações e
sessões; mantém só as cargas das migrações (Cursos, Equivalencia_Cursos e Areas_Interesse). Depois
monta turmas dos três cursos com alunos em todos os Status do TCC, passando pelos mesmos serviços
das telas (matrícula, Proposta, entregas, pedidos, coorientação, atas, Apto para Defesa, Versão
Final e aproveitamento de artigo). O resultado da defesa, que ainda não tem tela (Épico 2), é
simulado pelo serviço único do Status com o gatilho "Liberação do resultado", como nos testes.
As sessões de defesa (spec 007) ficam num TCC "Apto para Defesa" de cada curso, uma em cada Status
da sessão, criadas só pelos serviços da Defesa (agendar_sessao e transicionar_status).

Todas as contas ativas usam a mesma senha, informada em --senha. Os e-mails são fictícios
(demo.nome@uea.edu.br) e nenhum e-mail é enviado durante a carga.

Exemplo (docs/deploy-render.md, Passo 4):
    python manage.py popular_demo --senha Demo2026sig --confirmar

[infraestrutura do ambiente de validação, sem US específica]
"""

import re
from datetime import date, datetime, time, timedelta

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.test.utils import override_settings
from django.utils import timezone

from sigtcc.apps.cadastro import (
    services_artigos,
    services_atas,
    services_entregas,
    services_orientacao,
    services_tcc,
    services_turmas,
)
from sigtcc.apps.cadastro.cargas import (
    CURSO_ENG_COMPUTACAO,
    CURSO_LIC_COMPUTACAO,
    CURSO_SIST_INFORMACAO,
)
from sigtcc.apps.cadastro.choices import (
    DescricaoTurma,
    DiaSemana,
    GatilhoStatusTCC,
    ModalidadeTCC,
    StatusConta,
    StatusSolicitacao,
    StatusTCC,
    TipoEntrega,
    TipoSolicitacao,
    Titulacao,
)
from sigtcc.apps.cadastro.models import (
    Alunos,
    AreasInteresse,
    Coordenadores,
    Cursos,
    Docentes,
    MembrosExternos,
    Notificacoes,
    PalavrasChaveTCC,
    Secretarios,
    SolicitacoesOrientacao,
    TCCs,
    Turmas,
    TurmasMarcos,
    Usuarios,
)
from sigtcc.apps.defesa import services_defesa
from sigtcc.apps.defesa.choices import FormatoSessao, PapelBanca, StatusSessao
from sigtcc.apps.defesa.models import Defesas

# Tabelas carregadas pelas migrações, que a limpeza mantém.
MANTER = {"Cursos", "Equivalencia_Cursos", "Areas_Interesse"}

# Código UEA de cada curso (Equivalencia_Cursos).
CODIGO = {
    CURSO_ENG_COMPUTACAO: "EST08MCPD",
    CURSO_SIST_INFORMACAO: "EST31MSII",
    CURSO_LIC_COMPUTACAO: "EST03MLV",
}

# E-mails fictícios no formato institucional, com o prefixo "demo." para não coincidir com
# contas reais da UEA.
DOMINIO = "uea.edu.br"

NOMES_ALUNOS = [
    "Ana Beatriz Ferreira",
    "Bruno Henrique Lima",
    "Camila Rodrigues Souza",
    "Daniel Oliveira Castro",
    "Eduarda Martins Rocha",
    "Felipe Augusto Nunes",
    "Gabriela Alves Pinto",
    "Heitor Cavalcante Reis",
    "Isabela Monteiro Dias",
    "João Pedro Barbosa",
    "Karina Lopes Andrade",
    "Lucas Gabriel Moreira",
    "Mariana Costa Ribeiro",
    "Nicolas Teixeira Melo",
    "Olívia Santana Cardoso",
    "Pedro Lucas Farias",
    "Rafaela Batista Gomes",
    "Samuel Correia Freitas",
    "Thaís Mendes Araújo",
    "Vinícius Rocha Sales",
    "Yasmin Carvalho Brito",
    "Arthur Nogueira Peixoto",
    "Beatriz Campos Vieira",
    "Caio Fernandes Duarte",
    "Débora Siqueira Prado",
    "Enzo Rezende Matos",
    "Fernanda Queiroz Lins",
    "Gustavo Pires Leal",
    "Helena Bezerra Torres",
    "Igor Magalhães Cunha",
    "Júlia Azevedo Paiva",
    "Kauã Ramos Fontes",
    "Larissa Moura Bastos",
    "Matheus Viana Coelho",
    "Natália Franco Aguiar",
    "Otávio Brandão Serra",
    "Priscila Guimarães Lago",
    "Rodrigo Tavares Neves",
    "Sofia Damasceno Luz",
    "Tiago Barros Quintela",
    "Valentina Assis Moraes",
    "Wesley Pacheco Amaral",
    "Alice Menezes Cordeiro",
    "Bernardo Lacerda Fonseca",
    "Clara Vasconcelos Rangel",
    "Davi Sampaio Toledo",
    "Elisa Carneiro Bittencourt",
    "Fábio Godinho Marques",
    # Spec 007: alunos dos TCCs Aptos sem sessão (roteiro da T056).
    "Giovana Teles Amorim",
    "Hugo Benevides Caldas",
    "Ingrid Sales Portela",
    "Jonas Albuquerque Neto",
    "Kelly Duarte Fontenele",
    "Leonardo Prado Esteves",
]

TEMAS = [
    ("Detecção de desmatamento na Amazônia com redes neurais", "Inteligência Artificial"),
    ("Aplicativo de acompanhamento de consultas para UBS de Manaus", "Engenharia de Software"),
    ("Monitoramento da qualidade da água com sensores IoT", "Sistemas Embarcados"),
    ("Análise de vulnerabilidades em sistemas web de prefeituras", "Segurança da Informação"),
    ("Recomendação de disciplinas optativas com aprendizado de máquina", "Ciência de Dados"),
    ("Acessibilidade em portais de universidades públicas", "Interação Humano-Computador"),
    ("Roteamento em redes de sensores sem fio ribeirinhas", "Redes de Computadores"),
    ("Banco de dados geográfico de comunidades indígenas", "Banco de Dados"),
    ("Jogos educativos para o ensino de lógica no ensino médio", "Educação em Computação"),
    ("Reconstrução 3D de sítios arqueológicos com fotogrametria", "Computação Gráfica"),
    ("Chatbot para atendimento acadêmico da secretaria", "Inteligência Artificial"),
    ("Previsão de cheias do Rio Negro com séries temporais", "Ciência de Dados"),
    ("Arquitetura de microsserviços para o SUS municipal", "Engenharia de Software"),
    ("Controle de acesso com biometria em laboratórios", "Segurança da Informação"),
    ("Tradução automática de português para nheengatu", "Inteligência Artificial"),
    ("Plataforma de ensino de programação para escolas rurais", "Educação em Computação"),
    ("Otimização de rotas de barcos de transporte escolar", "Ciência de Dados"),
    ("Sistema embarcado para irrigação de hortas comunitárias", "Sistemas Embarcados"),
    ("Avaliação de usabilidade de aplicativos bancários por idosos", "Interação Humano-Computador"),
    ("Replicação de bancos de dados em ambientes de baixa conectividade", "Banco de Dados"),
    ("Visualização interativa de dados de queimadas", "Computação Gráfica"),
    ("Detecção de fraudes em notas fiscais eletrônicas", "Ciência de Dados"),
    ("Rede mesh comunitária para escolas do interior", "Redes de Computadores"),
    ("Testes automatizados em aplicações Django", "Engenharia de Software"),
]

PALAVRAS = {
    "Inteligência Artificial": ["redes neurais", "aprendizado profundo", "visão computacional"],
    "Engenharia de Software": ["arquitetura", "requisitos", "testes"],
    "Sistemas Embarcados": ["IoT", "microcontroladores", "sensores"],
    "Segurança da Informação": ["vulnerabilidades", "criptografia", "LGPD"],
    "Ciência de Dados": ["séries temporais", "mineração de dados", "previsão"],
    "Interação Humano-Computador": ["usabilidade", "acessibilidade", "experiência do usuário"],
    "Redes de Computadores": ["roteamento", "redes sem fio", "conectividade"],
    "Banco de Dados": ["PostgreSQL", "modelagem", "replicação"],
    "Educação em Computação": ["pensamento computacional", "ensino", "jogos educativos"],
    "Computação Gráfica": ["visualização", "modelagem 3D", "renderização"],
}


def _slug(nome):
    """Parte local do e-mail fictício: primeiro e último nome, sem acento."""
    tabela = str.maketrans("áàâãéêíóôõúçÁÉÍÓÚÇ", "aaaaeeiooouc" + "aeiouc")
    partes = nome.lower().translate(tabela).split()
    return re.sub(r"[^a-z.]", "", f"{partes[0]}.{partes[-1]}")


def _aluno_do(tcc):
    """Nome do aluno do TCC, para as tabelas do roteiro. [spec 007, T056]"""
    return tcc.tcc_alu.alu.usu_nome


def _prazo(dia):
    """Data limite às 23:59 do dia informado."""
    return datetime.combine(dia, time(23, 59))


class Command(BaseCommand):
    """Comando popular_demo."""

    help = "Apaga os dados e carrega cenários fictícios de demonstração (ambiente de validação)."

    def add_arguments(self, parser):
        """--senha (de todas as contas ativas) e --confirmar (obrigatório: apaga os dados)."""
        parser.add_argument("--senha", required=True, help="senha de todas as contas ativas")
        parser.add_argument(
            "--confirmar", action="store_true", help="confirma que TODOS os dados serão apagados"
        )
        parser.add_argument(
            "--local", action="store_true", help="permite usar um banco desta máquina (localhost)"
        )

    def handle(self, *args, **opcoes):
        """Confere as opções, limpa e popula numa única transação (falhou, nada muda)."""
        banco = connection.settings_dict
        self.stdout.write(f"Banco: {banco.get('NAME')} em {banco.get('HOST') or 'localhost'}")
        if not opcoes["confirmar"]:
            raise CommandError(
                "Este comando APAGA todos os dados do banco acima. Rode de novo com --confirmar."
            )
        if banco.get("HOST", "") in ("", "localhost", "127.0.0.1", "::1") and not opcoes["local"]:
            raise CommandError(
                "O banco acima é local. Defina DATABASE_URL com o banco do Render ou, se for "
                "mesmo um banco local de teste, rode com --local."
            )
        # Segunda trava: digitar o nome do banco (evita apagar o banco local por engano).
        resposta = input(f"Digite o nome do banco ({banco.get('NAME')}) para apagar e popular: ")
        if resposta.strip() != banco.get("NAME"):
            raise CommandError("Nome diferente: nada foi alterado.")
        senha = opcoes["senha"]
        if not (
            8 <= len(senha) <= 64 and re.search(r"[A-Za-z]", senha) and re.search(r"\d", senha)
        ):
            raise CommandError("A senha precisa ter de 8 a 64 caracteres, com letra e número.")
        self.senha = senha
        self.hoje = timezone.now().date()
        self.nomes = iter(NOMES_ALUNOS)
        self.temas = iter(TEMAS * 3)
        self.matricula = 0
        self.logins = []
        # E-mails descartados (locmem) e síncronos, para nenhum sair depois da carga.
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
            SIGTCC_EMAIL_SINCRONO=True,
        ):
            with transaction.atomic():
                self._limpar()
                self._contas()
                self._turmas_engenharia()
                self._turmas_sistemas()
                self._turmas_licenciatura()
                self._defesas()
                services_entregas.marcar_nao_entregues()
        self._resumo()
        self._roteiro_defesa()

    # =========================================================================================
    # Limpeza
    # =========================================================================================

    def _limpar(self):
        """TRUNCATE de todas as tabelas dos apps e das sessões, menos as cargas das migrações."""
        tabelas = [
            modelo._meta.db_table
            for nome in ("cadastro", "defesa")
            for modelo in apps.get_app_config(nome).get_models()
            if modelo._meta.db_table not in MANTER
        ]
        tabelas.append("django_session")
        nomes = ", ".join(connection.ops.quote_name(t) for t in tabelas)
        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE {nomes} RESTART IDENTITY CASCADE")
        self.stdout.write(f"Limpeza: {len(tabelas)} tabelas esvaziadas.")

    # =========================================================================================
    # Contas
    # =========================================================================================

    def _usuario(self, nome, email, status=StatusConta.ATIVA, papel=None):
        """Conta com a senha da demonstração quando 'Ativa'; entra no resumo se tiver papel."""
        usuario = Usuarios.objects.create_user(
            email,
            nome,
            password=self.senha if status == StatusConta.ATIVA else None,
            usu_status=status,
        )
        if papel:
            self.logins.append((papel, email, status))
        return usuario

    def _docente(self, nome, curso, papel=None, status=StatusConta.ATIVA, titulacao=None):
        """Docente do NUCOMP lotado no curso."""
        usuario = self._usuario(nome, f"demo.{_slug(nome)}@{DOMINIO}", status, papel)
        Docentes.objects.create(
            doc=usuario, doc_titulacao=titulacao or Titulacao.DOUTOR, doc_cur=curso
        )
        return usuario

    def _contas(self):
        """Coordenadores, secretarias, docentes e membros externos dos três cursos."""
        self.ecp = Cursos.objects.get(cur_nome=CURSO_ENG_COMPUTACAO)
        self.si = Cursos.objects.get(cur_nome=CURSO_SIST_INFORMACAO)
        self.lic = Cursos.objects.get(cur_nome=CURSO_LIC_COMPUTACAO)

        # Coordenadores de Curso (são docentes).
        self.coord_ecp = self._docente(
            "Ricardo Almeida Prado", self.ecp, "Coordenador (Eng. Comp.)"
        )
        self.coord_si = self._docente("Patrícia Moura Leão", self.si, "Coordenadora (Sist. Inf.)")
        self.coord_lic = self._docente("Sérgio Pontes Dantas", self.lic, "Coordenador (Lic. Comp.)")
        for curso, docente in (
            (self.ecp, self.coord_ecp),
            (self.si, self.coord_si),
            (self.lic, self.coord_lic),
        ):
            Coordenadores.objects.create(cor_cur=curso, cor_doc=docente.docentes)

        # Secretarias: uma ativa por curso e uma inativa.
        for nome, curso, papel, status in (
            ("Lúcia Helena Barros", self.ecp, "Secretaria (Eng. Comp.)", StatusConta.ATIVA),
            ("Marta Regina Sousa", self.si, "Secretaria (Sist. Inf.)", StatusConta.ATIVA),
            ("Cláudia Neves Frota", self.lic, "Secretaria (Lic. Comp.)", StatusConta.ATIVA),
            ("Rosa Maria Antunes", self.ecp, None, StatusConta.INATIVA),
        ):
            usuario = self._usuario(nome, f"demo.{_slug(nome)}@{DOMINIO}", status, papel)
            Secretarios.objects.create(sec=usuario, sec_cur=curso)

        # Professores da Disciplina e orientadores.
        d = self._docente
        self.prof_ecp1 = d("Fernando Costa Lima", self.ecp, "Professor TCC 1 (Eng. Comp.)")
        self.prof_ecp2 = d("Juliana Mota Ferraz", self.ecp, "Professora TCC 2 (Eng. Comp.)")
        self.prof_ecp3 = d("Marcelo Ramos Teles", self.ecp, "Professor TCC 2 turma B (Eng. Comp.)")
        self.ori_ecp1 = d("Adriana Lopes Viana", self.ecp, "Orientadora (Eng. Comp.)")
        self.ori_ecp2 = d("Carlos Eduardo Pinheiro", self.ecp, "Orientador (Eng. Comp.)")
        self.ori_ecp3 = d("Renata Silveira Cruz", self.ecp, None, titulacao=Titulacao.MESTRE)
        self.prof_si1 = d("Eduardo Farias Brito", self.si, "Professor TCC 1 (Sist. Inf.)")
        self.prof_si2 = d("Vanessa Duarte Lobo", self.si, "Professora TCC 2 (Sist. Inf.)")
        self.ori_si1 = d("Roberto Cunha Matos", self.si, "Orientador (Sist. Inf.)")
        self.ori_si2 = d("Simone Arruda Paes", self.si, None, titulacao=Titulacao.MESTRE)
        self.prof_lic = d("Gilberto Sena Moraes", self.lic, "Professor TCC 1 (Lic. Comp.)")
        self.ori_lic = d("Tânia Ribeiro Maia", self.lic, None, titulacao=Titulacao.ESPECIALISTA)
        # Spec 007: docentes extras, só para compor bancas (roteiro da T056).
        self.extra_ecp1 = d("Beatriz Lemos Aragão", self.ecp, "Docente extra de banca (Eng. Comp.)")
        self.extra_ecp2 = d("Henrique Matos Couto", self.ecp, "Docente extra de banca (Eng. Comp.)")
        self.extra_si = d("Sandra Pires Lacerda", self.si, "Docente extra de banca (Sist. Inf.)")
        d("Paulo Henrique Sá", self.ecp, None, status=StatusConta.INATIVA)
        d("Laura Fontes Bessa", self.si, None, status=StatusConta.AGUARDANDO_ATIVACAO)

        # Membros externos: ativo, expirado e aguardando ativação.
        for nome, instituicao, status, validade, papel in (
            (
                "Marcos Vinícius Teixeira",
                "UFAM",
                StatusConta.ATIVA,
                date(2027, 6, 30),
                "Membro externo",
            ),
            ("Helena Duarte Campos", "INPA", StatusConta.EXPIRADA, date(2026, 3, 31), None),
            (
                "Otávio Lins Barreto",
                "IFAM",
                StatusConta.AGUARDANDO_ATIVACAO,
                date(2027, 3, 31),
                None,
            ),
        ):
            usuario = self._usuario(nome, f"demo.{_slug(nome)}@{DOMINIO}", status, papel)
            if status == StatusConta.ATIVA:
                self.externo = usuario
            elif status == StatusConta.EXPIRADA:
                self.externo_expirado = usuario
            MembrosExternos.objects.create(
                mem=usuario,
                mem_titulacao=Titulacao.DOUTOR,
                mem_instituicao=instituicao,
                mem_validade_ate=validade,
            )

    # =========================================================================================
    # Peças dos cenários
    # =========================================================================================

    def _turma(self, professor, curso, identificador, descricao, ano, semestre, dia, local):
        """Turma pelo serviço da US-07."""
        etapa = "1" if descricao == DescricaoTurma.TCC_1 else "2"
        return services_turmas.criar_turma(
            professor,
            {
                "codigo_disciplina": f"{CODIGO[curso.cur_nome][:5]}TCC{etapa}",
                "identificador": identificador,
                "ano": ano,
                "semestre": semestre,
                "dia_semana": dia,
                "hora_inicio": time(14, 0),
                "hora_termino": time(17, 40),
                "local": local,
                "descricao": descricao,
                "curso": curso,
            },
        )

    def _entrega(self, professor, turma, tipo, titulo, dia, instrucao=None):
        """Entrega pelo serviço da US-43 (cria o registro de cada aluno já matriculado)."""
        return services_entregas.cadastrar_entrega(
            professor,
            turma.pk,
            {"tipo": tipo, "titulo": titulo, "instrucao": instrucao, "data_limite": _prazo(dia)},
        )

    def _aluno(self, professor, turma, ativo=True):
        """Matrícula pelo serviço da US-08; com `ativo`, a conta já fez o primeiro acesso."""
        nome = next(self.nomes)
        self.matricula += 1
        matricula = f"{turma.tur_ano - 4}{self.matricula:06d}"
        services_turmas.matricular_individual(
            professor, turma.pk, matricula, nome, CODIGO[turma.tur_cur.cur_nome]
        )
        aluno = Alunos.objects.select_related("alu").get(alu_matricula=matricula)
        if ativo:
            usuario = aluno.alu
            usuario.usu_email = f"demo.{_slug(nome)}{self.matricula}@{DOMINIO}"
            usuario.set_password(self.senha)
            usuario.usu_status = StatusConta.ATIVA
            usuario.save()
        return aluno

    def _tcc(self, aluno, turma):
        """TCC atual do aluno na turma."""
        return TCCs.objects.get(tcc_alu=aluno, tcc_tur=turma)

    def _proposta(self, aluno, turma, modalidade=ModalidadeTCC.MONOGRAFIA, completa=True):
        """Proposta pelo serviço da US-13; com `completa`, Área e Palavras-Chave."""
        titulo, area = next(self.temas)
        services_tcc.salvar_proposta(
            aluno,
            turma.pk,
            {
                "titulo": titulo,
                "subtitulo": None,
                "resumo": (
                    f"Este trabalho propõe {titulo.lower()}, com levantamento bibliográfico, "
                    "desenvolvimento de um protótipo e avaliação com usuários e dados reais "
                    "da região amazônica."
                ),
                "modalidade": modalidade,
                "link": f"https://drive.google.com/demo/proposta-{aluno.alu_matricula}",
            },
        )
        tcc = self._tcc(aluno, turma)
        if completa:
            tcc.tcc_ari = AreasInteresse.objects.get(ari_nome=area)
            tcc.save(update_fields=["tcc_ari"])
            for palavra in PALAVRAS[area]:
                PalavrasChaveTCC.objects.create(pal_tcc=tcc, pal_palavra=palavra)
        return tcc

    def _enviar(self, aluno, marco, nome="documento"):
        """Envio de link pelo serviço da US-15."""
        services_entregas.enviar_entrega(
            aluno, marco.pk, f"https://drive.google.com/demo/{nome}-{aluno.alu_matricula}"
        )

    def _orientador(self, aluno, turma, docente):
        """Pedido de orientação aceito pelo docente (US-17 e US-18)."""
        sol = services_orientacao.enviar_pedido(aluno.alu, turma.pk, docente.pk)
        services_orientacao.aceitar_solicitacao(docente, sol.pk)

    def _pedido(self, aluno, turma, docente):
        """Pedido de orientação (ou de troca) aguardando resposta."""
        return services_orientacao.enviar_pedido(aluno.alu, turma.pk, docente.pk)

    def _coorientador_docente(self, aluno, turma, docente, aceitar=True):
        """Convite de coorientação a um docente do NUCOMP (US-45), aceito ou pendente (US-36)."""
        services_orientacao.registrar_coorientador(
            aluno.alu, turma.pk, {"tipo": "docente", "docente": docente.pk}
        )
        if aceitar:
            convite = SolicitacoesOrientacao.objects.filter(
                sol_tcc__tcc_alu=aluno,
                sol_doc=docente.docentes,
                sol_tipo=TipoSolicitacao.COORIENTACAO,
                sol_status=StatusSolicitacao.AGUARDANDO_ACEITE,
            ).latest("sol_id")
            services_orientacao.aceitar_solicitacao(docente, convite.pk)

    def _coorientador_externo(self, aluno, turma, nome, email, instituicao):
        """Coorientador externo, sem conta (US-45)."""
        services_orientacao.registrar_coorientador(
            aluno.alu,
            turma.pk,
            {"tipo": "externo", "nome": nome, "email": email, "instituicao": instituicao},
        )

    def _atas(self, aluno, tcc, orientador, quantidade=2):
        """Atas de orientação registradas pelo aluno, com comentário do orientador (US-19)."""
        pautas = [
            ("Definição do escopo e do cronograma.", "Entregar o capítulo de introdução."),
            ("Revisão da fundamentação teórica.", "Concluir a revisão bibliográfica."),
            ("Discussão do protótipo.", "Implementar a primeira versão do protótipo."),
            ("Análise dos primeiros resultados.", "Escrever o capítulo de resultados."),
        ]
        for i in range(quantidade):
            pauta, metas = pautas[i % len(pautas)]
            dia = self.hoje - timedelta(days=14 * (quantidade - i))
            ata = services_atas.registrar_ata(
                aluno.alu, tcc.pk, {"data": dia, "pauta": pauta, "metas": metas}
            )
            services_atas.comentar_ata(
                orientador, tcc.pk, ata.pk, "Bom andamento. Atenção às referências da ABNT."
            )

    def _resultado(self, tcc, autor, status):
        """Simula a liberação do resultado da defesa (Épico 2 ainda sem tela)."""
        with transaction.atomic():
            tcc = TCCs.objects.select_for_update().get(pk=tcc.pk)
            services_turmas.atualizar_status_tcc(
                tcc, tcc.tcc_tur, autor, status, GatilhoStatusTCC.LIBERACAO_DO_RESULTADO
            )

    def _apto(self, orientador, tcc):
        """Indicação de Apto para Defesa pelo orientador (US-42)."""
        services_orientacao.indicar_apto(orientador, tcc.pk)

    def _prazo_passado(self, marco, dias):
        """Recua a Data Limite de uma entrega já cadastrada (cenário de prazo vencido)."""
        TurmasMarcos.objects.filter(pk=marco.pk).update(
            tma_data_limite=_prazo(self.hoje - timedelta(days=dias))
        )
        marco.refresh_from_db()

    # =========================================================================================
    # Engenharia de Computação
    # =========================================================================================

    def _turmas_engenharia(self):
        """TCC 1 e TCC 2 de 2026/1 (arquivadas) e de 2026/2, com todos os Status do TCC."""
        p1, p2, p3 = self.prof_ecp1, self.prof_ecp2, self.prof_ecp3

        # --- TCC 1 2026/1 (arquivada): origem dos alunos do TCC 2 atual. ---------------------
        t_ant = self._turma(
            p1,
            self.ecp,
            "ECP-TCC1-2026.1",
            DescricaoTurma.TCC_1,
            2026,
            1,
            DiaSemana.TERCA,
            "Bloco B, sala 12",
        )
        doc_ant = self._entrega(
            p1,
            t_ant,
            TipoEntrega.DOCUMENTO_PARA_DEFESA,
            "Documento para a defesa do TCC 1",
            self.hoje + timedelta(days=5),
        )
        aprovados = []
        for _ in range(7):
            aluno = self._aluno(p1, t_ant)
            tcc = self._proposta(aluno, t_ant)
            orientador = [self.ori_ecp1, self.ori_ecp2, self.ori_ecp3][len(aprovados) % 3]
            self._orientador(aluno, t_ant, orientador)
            self._enviar(aluno, doc_ant)
            self._apto(orientador, tcc)
            self._resultado(tcc, p1, StatusTCC.APROVADO_PARA_TCC_2)
            aprovados.append(aluno)
        reprovado = self._aluno(p1, t_ant)
        tcc = self._proposta(reprovado, t_ant)
        self._orientador(reprovado, t_ant, self.ori_ecp2)
        self._enviar(reprovado, doc_ant)
        self._apto(self.ori_ecp2, tcc)
        self._resultado(tcc, p1, StatusTCC.REPROVADO)
        desistente = self._aluno(p1, t_ant)
        self._proposta(desistente, t_ant)
        services_turmas.encerrar_participacao(
            p1,
            t_ant.pk,
            desistente.pk,
            StatusTCC.DESISTENTE,
            "Aluno trancou o curso por motivo de trabalho.",
        )
        self._prazo_passado(doc_ant, 120)
        services_turmas.arquivar_turma(p1, t_ant.pk)

        # --- TCC 2 2026/1 (arquivada): alunos concluídos. -----------------------------------
        t2_ant = self._turma(
            p2,
            self.ecp,
            "ECP-TCC2-2026.1",
            DescricaoTurma.TCC_2,
            2026,
            1,
            DiaSemana.QUINTA,
            "Bloco B, sala 14",
        )
        doc2_ant = self._entrega(
            p2,
            t2_ant,
            TipoEntrega.DOCUMENTO_PARA_DEFESA,
            "Monografia para a banca",
            self.hoje + timedelta(days=5),
        )
        vf_ant = self._entrega(
            p2,
            t2_ant,
            TipoEntrega.VERSAO_FINAL,
            "Versão final com ficha",
            self.hoje + timedelta(days=10),
        )
        for status in (StatusTCC.APROVADO, StatusTCC.APROVADO_COM_CORRECOES):
            aluno = self._aluno(p2, t2_ant)
            tcc = self._proposta(aluno, t2_ant)
            self._enviar(aluno, doc2_ant)
            self._apto(p2, tcc)
            self._resultado(tcc, p2, status)
            self._enviar(aluno, vf_ant, "versao-final")
            services_entregas.homologar_versao_final(p2, t2_ant.pk, aluno.pk)
        self._prazo_passado(doc2_ant, 150)
        self._prazo_passado(vf_ant, 100)
        services_turmas.arquivar_turma(p2, t2_ant.pk)

        # --- TCC 1 2026/2 (ativa): todas as situações do TCC 1. ------------------------------
        t1 = self._turma(
            p1,
            self.ecp,
            "ECP-TCC1-2026.2",
            DescricaoTurma.TCC_1,
            2026,
            2,
            DiaSemana.TERCA,
            "Bloco B, sala 12",
        )
        alunos = [self._aluno(p1, t1, ativo=i < 12) for i in range(14)]
        # Spec 007: três alunos que chegam a Apto para Defesa sem sessão (roteiro da T056).
        novos = [self._aluno(p1, t1) for _ in range(3)]
        proposta = self._entrega(
            p1,
            t1,
            TipoEntrega.PROPOSTA,
            "Proposta de TCC",
            self.hoje + timedelta(days=3),
            "Preencha a Proposta na aba Meu TCC.",
        )
        revisao = self._entrega(
            p1,
            t1,
            TipoEntrega.OUTRA,
            "Revisão bibliográfica",
            self.hoje + timedelta(days=3),
            "Link do documento com no mínimo 15 referências.",
        )
        doc = self._entrega(
            p1,
            t1,
            TipoEntrega.DOCUMENTO_PARA_DEFESA,
            "Documento para a banca do TCC 1",
            self.hoje + timedelta(days=33),
        )
        self._entrega(
            p1, t1, TipoEntrega.OUTRA, "Cronograma de escrita", self.hoje + timedelta(days=12)
        )
        a = alunos
        # a[0], a[1]: Sem Proposta (a[1] com pedido de orientação pendente).
        self._pedido(a[1], t1, self.ori_ecp1)
        # a[2]..a[10]: com Proposta no prazo.
        tccs = {i: self._proposta(a[i], t1) for i in range(2, 11)}
        # a[11]: Proposta sem Área nem Palavras-Chave (não pode ser Apto).
        tccs[11] = self._proposta(a[11], t1, completa=False)
        tccs_novos = [self._proposta(aluno, t1) for aluno in novos]
        # Revisão: entregue no prazo por alguns.
        for i in (4, 5, 6, 7, 9):
            self._enviar(a[i], revisao, "revisao")
        self._prazo_passado(proposta, 40)
        self._prazo_passado(revisao, 15)
        # Revisão entregue com atraso.
        self._enviar(a[8], revisao, "revisao")
        self._enviar(a[10], revisao, "revisao")
        # a[2]: pedido pendente; a[3]: pedido recusado e novo pedido pendente.
        self._pedido(a[2], t1, self.ori_ecp2)
        sol = self._pedido(a[3], t1, self.ori_ecp3)
        services_orientacao.recusar_solicitacao(self.ori_ecp3, sol.pk)
        self._pedido(a[3], t1, self.ori_ecp1)
        # a[4]: orientador, coorientador docente aceito, atas.
        self._orientador(a[4], t1, self.ori_ecp1)
        self._coorientador_docente(a[4], t1, self.ori_ecp2)
        self._atas(a[4], tccs[4], self.ori_ecp1, 3)
        # a[5]: orientador, convite de coorientação pendente, coorientador externo.
        self._orientador(a[5], t1, self.ori_ecp2)
        self._coorientador_docente(a[5], t1, self.ori_ecp3, aceitar=False)
        self._coorientador_externo(
            a[5],
            t1,
            "Jorge Amazonas Freire",
            f"demo.jorge.freire@{DOMINIO}",
            "Embrapa Amazônia Ocidental",
        )
        self._atas(a[5], tccs[5], self.ori_ecp2, 2)
        # a[6]: orientador e Documento entregue: "Apto para Defesa" disponível ao orientador.
        self._orientador(a[6], t1, self.ori_ecp1)
        self._enviar(a[6], doc, "documento-defesa")
        self._atas(a[6], tccs[6], self.ori_ecp1, 2)
        # a[7]: Apto para Defesa.
        self._orientador(a[7], t1, self.ori_ecp3)
        self._enviar(a[7], doc, "documento-defesa")
        self._apto(self.ori_ecp3, tccs[7])
        self.apto_ecp1 = tccs[7]
        # a[6] fica sem a indicação de Apto: não aparece na lista do agendamento (spec 007).
        self.nao_apto_ecp = tccs[6]
        # Spec 007: Aptos sem sessão; no 3º, a troca de orientador pendente (US-24, fluxo A).
        self.aptos_ecp = [
            self._apto_com_coorientador(
                novos[0], t1, doc, tccs_novos[0], self.ori_ecp1, self.ori_ecp3
            ),
            self._apto_com_coorientador(
                novos[1], t1, doc, tccs_novos[1], self.ori_ecp2, self.ori_ecp1
            ),
        ]
        self.apto_troca = self._apto_com_coorientador(
            novos[2], t1, doc, tccs_novos[2], self.ori_ecp3, self.ori_ecp2
        )
        self.troca_para = self.ori_ecp1
        self._pedido(novos[2], t1, self.troca_para)
        # a[8]: orientador e pedido de troca de orientação pendente.
        self._orientador(a[8], t1, self.ori_ecp2)
        self._pedido(a[8], t1, self.ori_ecp1)
        # a[9]: Artigo Científico com publicação aceita (aproveitamento "Em Análise").
        tcc9 = self._proposta_trocada(a[9], t1, tccs[9])
        self._orientador(a[9], t1, self.ori_ecp1)
        services_artigos.salvar_publicacao(
            a[9].alu,
            tcc9.pk,
            {
                "veiculo": "Revista Brasileira de Computação Aplicada",
                "link": "https://doi.org/10.5753/demo.2026.001",
                "qualis": "A3",
                "status": "Aceito",
            },
        )
        # a[10]: Jubilado; a[11]: Proposta sem Área nem Palavras-Chave, com orientador.
        services_turmas.encerrar_participacao(
            p1, t1.pk, a[10].pk, StatusTCC.JUBILADO, "Prazo máximo de integralização excedido."
        )
        self._orientador(a[11], t1, self.ori_ecp3)
        # a[12], a[13]: contas aguardando o primeiro acesso, Sem Proposta.
        # Aluno excluído da turma (Sem Proposta).
        excluido = self._aluno(p1, t1)
        services_turmas.excluir_aluno(
            p1, t1.pk, excluido.pk, "Matrícula feita por engano: aluno de outra turma."
        )

        # --- TCC 2 2026/2 (ativa, orientador automático): alunos vindos do TCC 1. -----------
        t2 = self._turma(
            p2,
            self.ecp,
            "ECP-TCC2-2026.2-A",
            DescricaoTurma.TCC_2,
            2026,
            2,
            DiaSemana.QUINTA,
            "Bloco B, sala 14",
        )
        t2b = self._turma(
            p3,
            self.ecp,
            "ECP-TCC2-2026.2-B",
            DescricaoTurma.TCC_2,
            2026,
            2,
            DiaSemana.SEXTA,
            "Laboratório 3",
        )
        for aluno in aprovados:
            services_turmas.matricular_individual(
                p2, t2.pk, aluno.alu_matricula, aluno.alu.usu_nome, CODIGO[CURSO_ENG_COMPUTACAO]
            )
        doc2 = self._entrega(
            p2,
            t2,
            TipoEntrega.DOCUMENTO_PARA_DEFESA,
            "Monografia para a banca",
            self.hoje + timedelta(days=20),
        )
        vf2 = self._entrega(
            p2,
            t2,
            TipoEntrega.VERSAO_FINAL,
            "Versão final com ficha catalográfica",
            self.hoje + timedelta(days=50),
        )
        self._entrega(
            p2, t2, TipoEntrega.OUTRA, "Capítulo de resultados", self.hoje + timedelta(days=8)
        )
        b = aprovados
        t2tcc = {i: self._tcc(b[i], t2) for i in range(len(b))}
        # b[0]: Em Andamento, nada enviado. b[1]: Documento enviado (Apto disponível).
        self._enviar(b[1], doc2, "monografia")
        self._atas(b[1], t2tcc[1], p2, 2)
        # b[2]: Apto para Defesa.
        self._enviar(b[2], doc2, "monografia")
        self._apto(p2, t2tcc[2])
        self.apto_ecp2 = t2tcc[2]
        # b[3]: Aprovado, Versão Final enviada aguardando homologação.
        for i, status in (
            (3, StatusTCC.APROVADO),
            (4, StatusTCC.APROVADO),
            (5, StatusTCC.APROVADO_COM_CORRECOES),
        ):
            self._enviar(b[i], doc2, "monografia")
            self._apto(p2, t2tcc[i])
            if i == 3:
                self._sessao_realizada(t2tcc[i], p2)
            self._resultado(t2tcc[i], p2, status)
            self._enviar(b[i], vf2, "versao-final")
        # b[4]: Concluído (Versão Final homologada).
        services_entregas.homologar_versao_final(p2, t2.pk, b[4].pk)
        # b[5]: Versão Final devolvida para ajuste.
        services_entregas.devolver_versao_final(
            p2, t2.pk, b[5].pk, "Ajustar a ficha catalográfica e incluir a folha de aprovação."
        )
        # b[6]: transferido para a turma B.
        services_turmas.transferir(
            p2, t2.pk, b[6].pk, t2b.pk, "Conflito de horário com estágio obrigatório."
        )
        # Turma B com alunos novos no TCC 2.
        for _ in range(3):
            aluno = self._aluno(p3, t2b)
            self._proposta(aluno, t2b)

    def _apto_com_coorientador(self, aluno, turma, doc, tcc, orientador, coorientador):
        """TCC Apto para Defesa pelo caminho das telas (spec 007, roteiro da T056): orientador
        aceito (US-17/18), coorientador do NUCOMP aceito (US-45/36), Documento para Defesa enviado
        (US-15) e indicação de Apto (US-42). A Proposta já tem Área e Palavras-Chave.
        [US-21][RBN-DEF-01.1][RBN-CAD-11.5]
        """
        self._orientador(aluno, turma, orientador)
        self._coorientador_docente(aluno, turma, coorientador)
        self._enviar(aluno, doc, "documento-defesa")
        self._apto(orientador, tcc)
        tcc.refresh_from_db()
        return tcc

    def _proposta_trocada(self, aluno, turma, tcc):
        """Muda a modalidade para Artigo Científico (mudança de tema, US-13)."""
        TCCs.objects.filter(pk=tcc.pk).update(tcc_modalidade=ModalidadeTCC.ARTIGO_CIENTIFICO)
        tcc.refresh_from_db()
        return tcc

    # =========================================================================================
    # Sistemas de Informação
    # =========================================================================================

    def _turmas_sistemas(self):
        """TCC 1 e TCC 2 de 2026/2, com correções conferidas e aproveitamento de artigos."""
        p1, p2 = self.prof_si1, self.prof_si2
        t1 = self._turma(
            p1,
            self.si,
            "SI-TCC1-2026.2",
            DescricaoTurma.TCC_1,
            2026,
            2,
            DiaSemana.SEGUNDA,
            "Bloco C, sala 5",
        )
        # alunos[6] e alunos[7]: Aptos sem sessão da spec 007 (roteiro da T056).
        alunos = [self._aluno(p1, t1) for _ in range(8)]
        proposta = self._entrega(
            p1, t1, TipoEntrega.PROPOSTA, "Proposta", self.hoje + timedelta(days=2)
        )
        doc = self._entrega(
            p1,
            t1,
            TipoEntrega.DOCUMENTO_PARA_DEFESA,
            "Projeto de TCC",
            self.hoje + timedelta(days=30),
        )
        tccs = {i: self._proposta(alunos[i], t1) for i in range(1, 8)}
        self._prazo_passado(proposta, 30)
        self._orientador(alunos[1], t1, self.ori_si1)
        self._orientador(alunos[2], t1, self.ori_si2)
        self._enviar(alunos[2], doc, "projeto")
        self._apto(self.ori_si2, tccs[2])
        self.apto_si = tccs[2]
        # Spec 007: em Sistemas de Informação, quem agenda é o Professor da Disciplina.
        self.aptos_si = [
            self._apto_com_coorientador(alunos[6], t1, doc, tccs[6], self.ori_si1, self.ori_si2),
            self._apto_com_coorientador(alunos[7], t1, doc, tccs[7], self.ori_si2, self.ori_si1),
        ]
        self._pedido(alunos[3], t1, self.ori_si1)
        self._orientador(alunos[4], t1, self.ori_si1)
        self._coorientador_externo(
            alunos[4], t1, "Luciana Prestes Valente", f"demo.luciana.valente@{DOMINIO}", "SEDUC-AM"
        )
        self._atas(alunos[4], tccs[4], self.ori_si1, 2)
        # Artigo Científico com publicação: Homologado pela coordenação.
        tcc5 = self._proposta_trocada(alunos[5], t1, tccs[5])
        self._orientador(alunos[5], t1, self.ori_si2)
        services_artigos.salvar_publicacao(
            alunos[5].alu,
            tcc5.pk,
            {
                "veiculo": "Anais do SBSI 2026",
                "link": "https://doi.org/10.5753/sbsi.2026.042",
                "qualis": "A4",
                "status": "Publicado",
            },
        )
        services_artigos.homologar_artigo(self.coord_si, tcc5.pk)

        t2 = self._turma(
            p2,
            self.si,
            "SI-TCC2-2026.2",
            DescricaoTurma.TCC_2,
            2026,
            2,
            DiaSemana.QUARTA,
            "Bloco C, sala 7",
        )
        alunos2 = [self._aluno(p2, t2) for _ in range(5)]
        doc2 = self._entrega(
            p2, t2, TipoEntrega.DOCUMENTO_PARA_DEFESA, "Monografia", self.hoje + timedelta(days=15)
        )
        vf2 = self._entrega(
            p2, t2, TipoEntrega.VERSAO_FINAL, "Versão final", self.hoje + timedelta(days=45)
        )
        orientadores = [self.ori_si1, self.ori_si2, self.ori_si1, self.ori_si2, self.ori_si1]
        tccs2 = {}
        for i, aluno in enumerate(alunos2):
            modalidade = ModalidadeTCC.ARTIGO_CIENTIFICO if i == 4 else ModalidadeTCC.MONOGRAFIA
            tccs2[i] = self._proposta(aluno, t2, modalidade)
            self._orientador(aluno, t2, orientadores[i])
        # 0: Em Andamento. 1 e 2: Aprovado com Correções com Versão Final enviada; 1 conferida.
        for i in (1, 2):
            self._enviar(alunos2[i], doc2, "monografia")
            self._apto(orientadores[i], tccs2[i])
            self._resultado(tccs2[i], p2, StatusTCC.APROVADO_COM_CORRECOES)
            self._enviar(alunos2[i], vf2, "versao-final")
        services_orientacao.conferir_correcoes(orientadores[1], tccs2[1].pk)
        # 3: Reprovado.
        self._enviar(alunos2[3], doc2, "monografia")
        self._apto(orientadores[3], tccs2[3])
        self._resultado(tccs2[3], p2, StatusTCC.REPROVADO)
        # 4: Artigo Científico com publicação recusada pela coordenação.
        services_artigos.salvar_publicacao(
            alunos2[4].alu,
            tccs2[4].pk,
            {
                "veiculo": "Revista de Sistemas e Computação",
                "status": "Aceito",
                "qualis": "B2",
                "link": "https://doi.org/10.5753/rsc.2026.007",
            },
        )
        services_artigos.recusar_artigo(self.coord_si, tccs2[4].pk)

    # =========================================================================================
    # Licenciatura em Computação
    # =========================================================================================

    def _turmas_licenciatura(self):
        """TCC 1 de 2026/2, pequena, para o filtro por curso."""
        p = self.prof_lic
        t1 = self._turma(
            p,
            self.lic,
            "LIC-TCC1-2026.2",
            DescricaoTurma.TCC_1,
            2026,
            2,
            DiaSemana.SABADO,
            "Bloco A, sala 2",
        )
        alunos = [self._aluno(p, t1) for _ in range(4)]
        self._entrega(p, t1, TipoEntrega.PROPOSTA, "Proposta", self.hoje + timedelta(days=10))
        doc = self._entrega(
            p, t1, TipoEntrega.DOCUMENTO_PARA_DEFESA, "Projeto", self.hoje + timedelta(days=40)
        )
        tccs = {i: self._proposta(alunos[i], t1) for i in (1, 2, 3)}
        # alunos[2]: Apto para Defesa (sessão cancelada em _defesas, volta a poder agendar).
        self._orientador(alunos[2], t1, self.ori_lic)
        self._enviar(alunos[2], doc, "projeto")
        self._apto(self.ori_lic, tccs[2])
        self.apto_lic = tccs[2]
        self._pedido(alunos[3], t1, self.ori_lic)

    # =========================================================================================
    # Sessões de defesa (spec 007): uma em cada Status da sessão
    # =========================================================================================

    def _agendar(self, tcc, autor, dia, hora, banca, local=None, link=None):
        """Sessão "Agendada" pelo mesmo serviço do botão Agendar (US-21 a US-24): confere quem
        agenda, a elegibilidade, a banca, as contas e o conflito de horário, avisa o Aluno e a
        banca e recalcula a validade dos Membros Externos. Presencial com `local`, remota com
        `link`. A data no passado (sessões Em Andamento e Realizada) simula a passagem do tempo:
        a regra de data futura é do formulário. [US-21][US-24][RBN-DEF-01.1][contrato §5]
        """
        formato = FormatoSessao.PRESENCIAL if local else FormatoSessao.REMOTA
        primeiro, segundo, *suplente = banca
        return services_defesa.agendar(
            autor,
            tcc.pk,
            {"data": dia, "h_inicio": hora, "formato": formato, "local": local, "link": link},
            {
                "primeiro_avaliador": primeiro,
                "segundo_avaliador": segundo,
                "suplente": suplente[0] if suplente else None,
            },
        )

    def _sessao_realizada(self, tcc, orientador):
        """Sessão já realizada, antes da liberação do resultado (US-24, US-27): agendada há 5
        dias, iniciada pelo início automático e passada a Realizada pelo serviço único de status,
        como a feat-08 fará. [US-24][RBN-DEF-01.2][contrato §5]
        """
        sessao = self._agendar(
            tcc,
            orientador,
            self.hoje - timedelta(days=5),
            time(14, 0),
            (self.ori_ecp2, self.ori_ecp3),
            local="Bloco B, sala 14",
        )
        services_defesa.iniciar_sessoes_vencidas()
        sessao.refresh_from_db()
        services_defesa.transicionar_status(sessao, StatusSessao.REALIZADA, orientador)
        self.sessao_realizada = sessao

    def _defesas(self):
        """Uma sessão em cada Status (a Realizada fica no TCC 2 de Eng. Comp. que recebeu o
        resultado): Agendada daqui a 3 dias às 14:00, com docente extra e suplente (conflito e
        Alterar banca); Reagendada; Em Andamento com suplente (Acionar suplente); Cancelada (o TCC
        volta a poder agendar). Quem agenda segue o curso (RBN-DEF-01.3).
        [US-21][US-22][US-23][US-24][RBN-DEF-01.2][RBN-DEF-01.3][contrato §5]
        """
        self.sessao_agendada = self._agendar(
            self.apto_ecp1,
            self.ori_ecp3,
            self.hoje + timedelta(days=3),
            time(14, 0),
            (self.extra_ecp1, self.ori_ecp2, self.externo),
            local="Laboratório LSI",
        )
        sessao = self._agendar(
            self.apto_ecp2,
            self.prof_ecp2,
            self.hoje + timedelta(days=6),
            time(9, 0),
            (self.ori_ecp1, self.prof_ecp3),
            link="https://meet.google.com/demo-defesa-ecp",
        )
        self.sessao_reagendada = services_defesa.reagendar(
            self.prof_ecp2,
            sessao.pk,
            {
                "data": self.hoje + timedelta(days=12),
                "h_inicio": time(10, 0),
                "formato": FormatoSessao.REMOTA,
                "link": "https://meet.google.com/demo-defesa-ecp",
            },
            "Avaliador em viagem para congresso na data original.",
        )
        # Em Andamento: marcada para 20 minutos atrás; o início automático faz a transição.
        inicio = (timezone.now() - timedelta(minutes=20)).replace(second=0, microsecond=0)
        self.sessao_em_andamento = self._agendar(
            self.apto_si,
            self.prof_si1,
            inicio.date(),
            inicio.time(),
            (self.ori_si1, self.prof_si2, self.extra_si),
            local="Bloco C, sala 5",
        )
        services_defesa.iniciar_sessoes_vencidas()
        sessao = self._agendar(
            self.apto_lic,
            self.prof_lic,
            self.hoje + timedelta(days=15),
            time(16, 0),
            (self.prof_lic, self.externo),
            local="Bloco A, sala 2",
        )
        self.sessao_cancelada = services_defesa.cancelar(
            self.prof_lic, sessao.pk, "Aluno pediu mais prazo para revisar o projeto."
        )

    # =========================================================================================
    # Resumo
    # =========================================================================================

    def _resumo(self):
        """Contagens e as contas de acesso (sem a senha)."""
        self.stdout.write(self.style.SUCCESS("Carga concluída."))
        self.stdout.write(
            f"Contas: {Usuarios.objects.count()} | Turmas: {Turmas.objects.count()} | "
            f"TCCs: {TCCs.objects.count()} | Notificações: {Notificacoes.objects.count()} | "
            f"Sessões de defesa: {Defesas.objects.count()}"
        )
        self.stdout.write("\nContas para a demonstração (todas com a senha informada):")
        for papel, email, _status in self.logins:
            self.stdout.write(f"  {papel:<40} {email}")
        self.stdout.write("\nAlunos (entram com o e-mail ou a matrícula):")
        for aluno in (
            Alunos.objects.select_related("alu")
            .filter(alu__usu_status=StatusConta.ATIVA)
            .order_by("alu_matricula")
        ):
            tcc = (
                TCCs.objects.filter(tcc_alu=aluno)
                .select_related("tcc_tur")
                .order_by("-tcc_id")
                .first()
            )
            situacao = f"{tcc.tcc_tur.tur_identificador}: {tcc.tcc_status}" if tcc else "-"
            self.stdout.write(f"  {aluno.alu_matricula}  {aluno.alu.usu_email:<45} {situacao}")

    # =========================================================================================
    # Roteiro da spec 007 (T056)
    # =========================================================================================

    def _linha(self, perfil, curso, login, uso):
        """Uma linha da tabela do roteiro. [spec 007, T056]"""
        self.stdout.write(f"  {perfil:<26} {curso:<11} {login:<46} {uso}")

    def _login_aluno(self, tcc):
        """Matrícula e e-mail do aluno do TCC. [spec 007, T056]"""
        aluno = tcc.tcc_alu
        return f"{aluno.alu_matricula} / {aluno.alu.usu_email}"

    def _roteiro_defesa(self):
        """Contas do roteiro manual da spec 007 (quickstart.md, T056), o uso de cada uma, quem pode
        agendar o quê (services_defesa.tccs_elegiveis) e as sessões de cada status.
        [US-21][US-22][US-23][US-24][US-40][spec 007, T056]
        """
        sigla = {
            CURSO_ENG_COMPUTACAO: "Eng. Comp.",
            CURSO_SIST_INFORMACAO: "Sist. Inf.",
            CURSO_LIC_COMPUTACAO: "Lic. Comp.",
        }
        ec, si = sigla[CURSO_ENG_COMPUTACAO], sigla[CURSO_SIST_INFORMACAO]
        agendada = self.sessao_agendada
        quando = f"{agendada.def_data:%d/%m/%Y} às {agendada.def_h_inicio:%H:%M}"
        self.stdout.write(
            "\nRoteiro da spec 007 (quickstart.md, T056) — todas com a senha informada:"
        )
        self._linha("Perfil", "Curso", "Login (e-mail ou matrícula)", "Uso no roteiro")
        linhas = [
            (
                "Orientadora",
                ec,
                self.ori_ecp1,
                f"Agenda o TCC de {_aluno_do(self.aptos_ecp[0])}; o de "
                f"{_aluno_do(self.nao_apto_ecp)} (não Apto) não aparece",
            ),
            (
                "Orientador",
                ec,
                self.ori_ecp2,
                f"Agenda o TCC de {_aluno_do(self.aptos_ecp[1])}; está na banca da sessão Agendada",
            ),
            (
                "Orientadora",
                ec,
                self.ori_ecp3,
                f"Agenda o TCC de {_aluno_do(self.apto_troca)} (troca pendente, cancelada ao "
                "agendar); Alterar banca na sessão Agendada",
            ),
            (
                "Professor da Disciplina",
                ec,
                self.prof_ecp1,
                "Aba Defesas da turma ECP-TCC1-2026.2; não agenda TCC de Eng. Comp. (US-21 E7)",
            ),
            (
                "Professor da Disciplina",
                si,
                self.prof_si1,
                f"Agenda os TCCs de {_aluno_do(self.aptos_si[0])} e {_aluno_do(self.aptos_si[1])}; "
                "reagenda e cancela as sessões de SI",
            ),
            (
                "Orientador",
                si,
                self.ori_si1,
                "Não agenda em Sist. Inf. (US-21 E7, endereço direto)",
            ),
            ("Orientadora", si, self.ori_si2, "Acionar suplente na sessão Em Andamento"),
            (
                "Docente extra",
                ec,
                self.extra_ecp1,
                f"Está na sessão Agendada de {quando}: use para o conflito de horário (US-22)",
            ),
            ("Docente extra", ec, self.extra_ecp2, "Livre para compor bancas"),
            ("Docente extra", si, self.extra_si, "Suplente da sessão Em Andamento"),
            ("Membro Externo (Ativa)", "-", self.externo, "Suplente da sessão Agendada"),
            (
                "Membro Externo (Expirada)",
                "-",
                self.externo_expirado,
                "Aparece entre os avaliadores; ao entrar numa banca, a validade é renovada (US-06)",
            ),
            (
                "Coordenador",
                ec,
                self.coord_ecp,
                "Filtro de Curso na tela Defesas; não abre a janela da sessão (US-40 E5)",
            ),
            ("Coordenadora", si, self.coord_si, "Filtro de Curso na tela Defesas"),
            (
                "Secretaria",
                ec,
                Secretarios.objects.get(sec_cur=self.ecp, sec__usu_status=StatusConta.ATIVA).sec,
                "Reagenda e cancela sessões de Eng. Comp.; filtro de Curso",
            ),
            (
                "Secretaria",
                si,
                Secretarios.objects.get(sec_cur=self.si).sec,
                "Reagenda e cancela sessões de Sist. Inf.; filtro de Curso",
            ),
        ]
        for perfil, curso, usuario, uso in linhas:
            self._linha(perfil, curso, usuario.usu_email, uso)
        alunos = [(tcc, "TCC Apto sem sessão") for tcc in (*self.aptos_ecp, *self.aptos_si)] + [
            (self.apto_troca, "TCC Apto com troca de orientador pendente"),
            (self.nao_apto_ecp, "TCC ainda não Apto"),
            (self.apto_ecp1, "Vê a própria sessão Agendada (Defesas e Histórico)"),
        ]
        for tcc, uso in alunos:
            curso = sigla[tcc.tcc_tur.tur_cur.cur_nome]
            self._linha("Aluno", curso, self._login_aluno(tcc), f"{_aluno_do(tcc)}: {uso}")

        self.stdout.write("\nQuem pode agendar o quê (TCCs Aptos, sem sessão ativa):")
        for docente in Docentes.objects.select_related("doc").order_by("doc__usu_nome"):
            tccs = services_defesa.tccs_elegiveis(docente.doc)
            if tccs:
                descricao = "; ".join(
                    f"{_aluno_do(tcc)} ({tcc.tcc_tur.tur_identificador})" for tcc in tccs
                )
                self.stdout.write(f"  {docente.doc.usu_nome:<28} {descricao}")

        self.stdout.write("\nSessões de defesa:")
        for sessao in Defesas.objects.select_related(
            "def_tcc__tcc_alu__alu", "def_tcc__tcc_tur"
        ).order_by("def_data", "def_h_inicio"):
            banca = services_defesa.banca_por_papel(sessao)
            membros = ", ".join(
                f"{papel}: {banca[papel].usu_nome}"
                for papel in (*services_defesa.PAPEIS_TITULARES, PapelBanca.SUPLENTE)
                if papel in banca
            )
            turma = sessao.def_tcc.tcc_tur.tur_identificador
            self.stdout.write(
                f"  {sessao.def_status:<13} {sessao.def_data:%d/%m/%Y} {sessao.def_h_inicio:%H:%M}"
                f"  {_aluno_do(sessao.def_tcc)} ({turma}) — {membros}"
            )
