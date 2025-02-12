def cacular_inss(salario = float):
    if 0 < salario <= 1518.00:
        inss = 0.075
    elif  1518.00 < salario <= 2793.88:
        inss = 0.09
    elif 2793.88 < salario <= 4190.83:
        inss = 0.12
    elif 4190.83 < salario <= 8157.41:
        inss = 0.14
    else:
        inss = 1139.28 / salario
    return inss


def calcular_irrf(salario = float):
    if 0 < salario <= 2259.20:
        irrf = 0
    elif 2259.20 < salario <= 2828.65:
        irrf = 0.075
    elif 2828.65 < salario <= 3751.05:
        irrf = 0.15
    elif 3751.05 < salario <= 4664.68:
        irrf = 0.225
    else:
        irrf = 0.275
    return irrf


def calcular_salario(salario, inss, irrf , beneficios, descontos):
    imposto_inss = salario * inss 
    imposto_irrf = salario * irrf
    novo_salario = (salario - (imposto_inss + imposto_irrf)) + beneficios - descontos
    return novo_salario

    
