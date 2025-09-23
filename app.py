from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_secreta_simples'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_de_dados.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)  

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)

@app.route('/')
def pagina_inicial():
    return render_template('index.html')

@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    erro = None
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        if Usuario.query.filter_by(email=email).first():
            erro = 'E-mail já cadastrado. Use outro.'
            return render_template('cadastro_usuario.html', erro=erro)
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro_usuario.html', erro=erro)

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('listar_produtos'))
        else:
            erro = 'Usuário ou senha incorretos'
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('pagina_inicial'))

@app.route('/produtos')
def listar_produtos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos, criar=False, editar=False)

@app.route('/produtos/novo', methods=['GET', 'POST'])
def criar_produto():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        descricao = request.form['descricao']
        novo_produto = Produto(nome=nome, preco=preco, descricao=descricao)
        db.session.add(novo_produto)
        db.session.commit()
        return redirect(url_for('listar_produtos'))
    return render_template('produtos.html', produtos=Produto.query.all(), criar=True, editar=False)

@app.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    produto = Produto.query.get_or_404(id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.preco = float(request.form['preco'])
        produto.descricao = request.form['descricao']
        db.session.commit()
        return redirect(url_for('listar_produtos'))
    return render_template('produtos.html', produtos=Produto.query.all(), produto=produto, criar=False, editar=True)

@app.route('/produtos/excluir/<int:id>')
def excluir_produto(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('listar_produtos'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
