from flask import render_template, url_for, redirect, request
from hms_softforge import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from hms_softforge.forms import FormLogin, FormCriarConta, FormNovaTarefa
from hms_softforge.models import Usuario, Tarefa
from datetime import datetime
from sqlalchemy import or_

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



@app.route("/perfilatendente", methods=["GET", "POST"])
@login_required
def perfilatendente():
    # consulta para obter todos os usuários
    usuarios = Usuario.query.all()

    # filtros
    filtro_cargo = request.form.get("filtro_cargo")
    termo_pesquisa = request.form.get("termo_pesquisa")

    # aplicar filtro por cargo
    if filtro_cargo:
        usuarios = Usuario.query.filter_by(cargo=filtro_cargo).all()

    # aplicar pesquisa por nome ee emial
    if termo_pesquisa:
        termo_pesquisa = f"%{termo_pesquisa}%"
        usuarios = Usuario.query.filter(
            or_(Usuario.username.like(termo_pesquisa), Usuario.email.like(termo_pesquisa))
        ).all()

    return render_template("perfilatendente.html", usuarios=usuarios)


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

@app.route("/mudar_estado/<int:tarefa_id>/<int:novo_estado>")
@login_required
def mudar_estado(tarefa_id, novo_estado):
    tarefa = Tarefa.query.get_or_404(tarefa_id)

    if current_user.cargo != "gerente":
        return redirect(url_for("perfilgerente"))

    if not tarefa.estado:
        tarefa.estado = bool(novo_estado)
        tarefa.concluido_por = current_user.username
        tarefa.realizada_em = datetime.now()
        database.session.commit()

    return redirect(url_for("perfilgerente"))

@app.errorhandler(404)
def notFound(error):
    return render_template('404.html')

@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html')