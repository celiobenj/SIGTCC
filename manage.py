#!/usr/bin/env python
"""Utilitário de linha de comando do Django para o SIGTCC.

[infraestrutura da feature 001, sem US específica]
"""

import os
import sys


def main():
    """Executa os comandos administrativos do Django com as configurações do SIGTCC."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigtcc.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Ative o ambiente virtual (venv) e instale o "
            "requirements.txt."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
