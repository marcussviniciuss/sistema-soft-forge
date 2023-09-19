from flask import render_template, url_for, redirect
from hms_softforge import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from hms_softforge.forms import FormLogin, FormCriarConta, FormNovaTarefa
from hms_softforge.models import Usuario, Tarefa

@app.route("/", methods=["GET", "POST"])
def homepage():
    formlogin = FormLogin()
    if formlogin.validate_on_submit():
        usuario = Usuario.query.filter_by(email=formlogin.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, formlogin.senha.data):
            login_user(usuario)
            if usuario.cargo == "gerente":
                return redirect(url_for("perfilgerente"))
            if usuario.cargo == "atendente":
                return redirect(url_for("perfilatendente"))
            if usuario.cargo == "funcionario":
                return redirect(url_for("perfilfuncionario"))
    return render_template("homepage.html", form=formlogin)

@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    formcriarconta = FormCriarConta()
    if formcriarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(formcriarconta.senha.data)
        usuario = Usuario(username= formcriarconta.username.data,
                          senha=senha,
                          email=formcriarconta.email.data,
                          cargo = formcriarconta.cargo.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("homepage"))
    return render_template("criarconta.html", form=formcriarconta)

# @app.route("/perfil/<usuario>")
# @login_required
# def perfil(usuario):
#     return render_template("perfil.html", usuario=usuario)

@app.route("/perfilgerente", methods=["GET", "POST"])
@login_required
def perfilgerente():
    tarefa = Tarefa.query.order_by(Tarefa.id).all()
    if current_user.cargo == "gerente":
        form = FormNovaTarefa()
        if form.is_submitted():
            nova_tarefa = Tarefa(tarefa=form.tarefa.data)
            database.session.add(nova_tarefa)
            database.session.commit()
            return redirect(url_for('perfilgerente'))
        return render_template("perfilgerente.html", form=form, tarefa=tarefa)
    else:
        return render_template("perfilgerente.html", form=None, tarefa=tarefa)

@app.route("/perfilatendente")
@login_required
def perfilatendente():
    return render_template("perfilatendente.html")

@app.route("/perfilfuncionario")
@login_required
def perfilfuncionario():
    return render_template("perfilfuncionario.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/telaHome")
@login_required
def telaHome():
    return render_template("telaHome.html")
