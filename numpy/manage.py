#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokemon_chat.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não consegui importar o Django. Você tem certeza que instalou e "
            "está com o ambiente virtual ativado?"
        ) from exc
    execute_from_command_line(sys.argv)