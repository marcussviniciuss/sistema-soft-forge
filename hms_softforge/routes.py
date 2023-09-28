from flask import render_template, url_for, redirect, request
from hms_softforge import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from hms_softforge.forms import FormLogin, FormCriarConta, FormNovaTarefa
from hms_softforge.models import Usuario, Tarefa
from datetime import datetime
from sqlalchemy import or_

@app.route("/", methods=["GET", "POST"])
def login():
    formlogin = FormLogin()
    if formlogin.validate_on_submit():
        usuario = Usuario.query.filter_by(email=formlogin.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, formlogin.senha.data):
            login_user(usuario)
            if usuario.cargo == "gerente":
                return redirect(url_for("telaHome"))
            if usuario.cargo == "atendente":
                return redirect(url_for("telaHome"))
            if usuario.cargo == "funcionario":
                return redirect(url_for("telaHome"))
    return render_template("login.html", form=formlogin)

@app.route("/criarconta", methods=["GET", "POST"])
@login_required
def criarconta():
    if current_user.cargo == "gerente":
        formcriarconta = FormCriarConta()
        if formcriarconta.validate_on_submit():
            senha = bcrypt.generate_password_hash(formcriarconta.senha.data)
            usuario = Usuario(username= formcriarconta.username.data,
                            senha=senha,
                            email=formcriarconta.email.data,
                            cargo = formcriarconta.cargo.data)
            database.session.add(usuario)
            database.session.commit()
            return redirect(url_for("telaHome"))
    return render_template("criarconta.html", form=formcriarconta)

# @app.route("/perfil/<usuario>")
# @login_required
# def perfil(usuario):
#     return render_template("perfil.html", usuario=usuario)

@app.route("/tarefas", methods=["GET", "POST"])
@login_required
def tarefas():
    tarefa = Tarefa.query.order_by(Tarefa.id).all()
    if current_user.cargo != "funcionario":
        form = FormNovaTarefa()
        if form.is_submitted():
            nova_tarefa = Tarefa(tarefa=form.tarefa.data)
            database.session.add(nova_tarefa)
            database.session.commit()
            return redirect(url_for('tarefas'))
        return render_template("tarefas.html", form=form, tarefa=tarefa)
    else:
        return render_template("tarefas.html", form=None, tarefa=tarefa)

@app.route("/funcionarios", methods=["GET", "POST"])
@login_required
def funcionarios():
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

    return render_template("funcionarios.html", usuarios=usuarios)

@app.route("/reservas", methods=["GET", "POST"])
@login_required
def reservas():
    return render_template("reservas.html")
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/telaHome")
@login_required
def telaHome():
    return render_template('telaHome.html')

@app.route("/mudar_estado/<int:tarefa_id>/<int:novo_estado>")
@login_required
def mudar_estado(tarefa_id, novo_estado):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    
    if not tarefa.estado:
        tarefa.estado = bool(novo_estado)
        tarefa.concluido_por = current_user.username
        tarefa.realizada_em = datetime.now()
        database.session.commit()
    return redirect(url_for("tarefas"))

@app.route("/excluir_tarefa/<int:tarefa_id>")
@login_required
def excluir_tarefa(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    
    if current_user.cargo == "gerente":
        database.session.delete(tarefa)
        database.session.commit()
    return redirect(url_for('tarefas'))

@app.errorhandler(404)
def notFound(error):
    return render_template('404.html')

@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html')