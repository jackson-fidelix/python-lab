# importe a biblioteca PySimpleGUI "pip install PySimpleGUI"
from PySimpleGUI import PySimpleGUI as sg
import sys
# colocar caminho correto, de acordo com seu repositório
sys.path.append(r'C:\Users\smcti\Documents\ex')
from lib.impostos import *

#Layout
sg.theme('DarkAmber')
layout = [
    [sg.Text('Salário Bruto:'), sg.Input(key='salario_bruto',size=(14,2))],
    [sg.Text('Benefícios:'), sg.Input(key='beneficios',size=(16,2))],
    [sg.Text('Outros Descontos:'), sg.Input(key='outros_descontos',size=(10,2))],
    [sg.Text('')],# para pular uma linha
    [sg.Button('Calcular')],
    [sg.Text('')],# para pular uma linha
    [sg.Text('INSS:'), sg.Input('', size=(15,2), key='percentual_inss')],
    [sg.Text('IRRF:'), sg.Input('', size=(15,2), key='percentual_irrf')],
    [sg.Text('Salário Liquido:'), sg.Input('', size=(13,2),key='salario_liquido')]
]

#Janela
janela = sg.Window('Calculadora de Salário Líquido', layout, element_justification='center')

#Ler os eventos
while True:
    eventos, valores = janela.read()
    if eventos == sg.WIN_CLOSED:
        break
    # condição de calculo
    if eventos == "Calcular":
        entrada = valores["salario_bruto"].strip()
        if entrada:
            salario = float(valores['salario_bruto'])
        entrada_beneficios = valores["beneficios"].strip()
        if entrada_beneficios:
            beneficios = float(valores["beneficios"])
        else:
            beneficios = 0.0
        entrada_descontos = valores["outros_descontos"].strip()
        if entrada_descontos:
            descontos = float(valores["outros_descontos"])
        else:
            descontos = 0.0
    inss = cacular_inss(salario)
    irrf = calcular_irrf(salario)
    janela['percentual_inss'].update(f' {inss*100:.2f}%')
    janela['percentual_irrf'].update(f' {irrf*100:.2f}%')
    salario_liquido = calcular_salario(salario, inss, irrf, beneficios, descontos)
    janela['salario_liquido'].update(f'R$ {salario_liquido:.2f}')
janela.close()
