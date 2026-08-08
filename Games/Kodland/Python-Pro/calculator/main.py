# Importações
from flask import Flask, render_template, request


app = Flask(__name__)

def result_calculate(size, lights, device):
    """Calcula o consumo estimado com base na área, número de luminárias e aparelhos.

    Args:
        size (int): Tamanho (área) da residência
        lights (int): Quantidade de luminárias
        device (int): Quantidade de aparelhos

    Returns:
        float: Consumo estimado
    """
    # Coeficientes usados no cálculo do consumo de energia
    home_coef = 100
    light_coef = 0.04
    devices_coef = 5
    return size * home_coef + lights * light_coef + device * devices_coef

# A primeira página
@app.route('/')
def index():
    return render_template('index.html')

# A segunda página
@app.route('/<size>')
def lights(size):
    return render_template(
                            'lights.html', 
                            size=size
                           )

# A terceira página
@app.route('/<size>/<lights>')
def electronics(size, lights):
    return render_template(
                            'electronics.html',
                            size = size, 
                            lights = lights                           
                           )

# Cálculo
@app.route('/<size>/<lights>/<device>')
def end(size, lights, device):
    return render_template('end.html', 
                            result=result_calculate(int(size),
                                                    int(lights), 
                                                    int(device)
                                                    )
                        )

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_form():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    date = request.form.get('date', '')

    return render_template(
        'form_result.html',
        name=name,
        email=email,
        address=address,
        date=date
    )

if __name__ == '__main__':
    app.run(debug=True)
