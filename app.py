from flask import Flask
# ... resto das importações

app = Flask(__name__)  # ← TEM QUE TER ISSO!

# ... suas rotas e configurações

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)