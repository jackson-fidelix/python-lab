from PySimpleGUI import PySimpleGUI as sg

#Layout
sg.theme('Kayak')
layout = [
    [sg.Text('Salário Bruto:'), sg.Input(key='salario_bruto',size=(14,2))],
    [sg.Text('Benefícios:'), sg.Input(key='beneficios',size=(16,2))],
    [sg.Text('Outros Descontos:'), sg.Input(key='outros_descontos',size=(10,2))],
    [sg.Text('')],# para pular uma linha
    [sg.Button('Calcular')],
    [sg.Text('')],# para pular uma linha
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
            salario_liquido = float(valores['salario_bruto'])
            janela['salario_liquido'].update(f'R$ {salario_liquido:.2f}')
        entrada_beneficios = valores["beneficios"].strip()
        if entrada_beneficios:
            beneficios = float(valores["beneficios"])
            salario_liquido += beneficios
            janela['salario_liquido'].update(f'R$ {salario_liquido:.2f}')
        entrada_descontos = valores["outros_descontos"].strip()
        if entrada_descontos:
            descontos = float(valores["outros_descontos"])
            salario_liquido -= descontos
            janela['salario_liquido'].update(f'R$ {salario_liquido:.2f}')
janela.close()
