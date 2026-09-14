# Importar
from flask import Flask, render_template, request



app = Flask(__name__)

# Conteúdo da página
@app.route('/')
def index():
    return render_template('index.html')


# Processar os formulários enviados pela página
@app.route('/', methods=['POST'])
def process_form():
    button_python = request.form.get('button_python')
    email = request.form.get('email')
    text = request.form.get('text')

    return render_template(
        'index.html', 
        button_python=button_python, 
        email=email, 
        text=text,
    )


if __name__ == "__main__":
    app.run(debug=True)
