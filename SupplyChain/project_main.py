import internal_utils
import pandas as pd
import requests
import logging as log
import os
import pathlib


#
# Esse 'projeto_main.py' trata-se apenas de uma simulação de um projeto MAIN/APLICAÇÃO, usando a lib comprometida.
#



log.error('EXECUTADO APLICAÇÃO')
a = 1
b = 2
c = 3
e = 10

def calcular(a, b, c, e):
    a = a
    b = b
    c = c
    e = e

    if a == 0:
        log.error('Contém valor igual a 0 da variavel: {a}')
    elif b == 0:
        log.error('Contém valor igual a 0 da variavel: {b}')
    elif c == 0:
        log.error('Contém valor igual a 0 da variavel: {c}')
    elif e == 0:
        log.error('Contém valor igual a 0 da variavel: {e}')

calcular(a, b, c, e)
resultado = internal_utils.process_data({"nome": "joao", "valor": 42})
print("Resultado:", resultado)

log.error('FIM EXECUÇÃO DA APLICAÇÃO')
