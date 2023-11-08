from flask import render_template, url_for, redirect, request
from hms_softforge import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from hms_softforge.forms import FormLogin, FormCriarConta, FormNovaTarefa, FormCriarQuarto, FormReservarQuarto, FormQuarto
from hms_softforge.models import Usuario, Tarefa, Quarto
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
                return redirect(url_for("home"))
            if usuario.cargo == "atendente":
                return redirect(url_for("home"))
            if usuario.cargo == "funcionario":
                return redirect(url_for("home"))
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
            return redirect(url_for("home"))
    return render_template("criarconta.html", form=formcriarconta)

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

@app.route("/reservas", methods=["GET", "POST", "PATCH"])
@login_required
def reservas():
    form_quarto = FormCriarQuarto()
    form_reserva = FormReservarQuarto()
    tabela_quartos = Quarto.query.order_by(Quarto.quarto).all()
    return render_template("reservas.html", form_quarto=form_quarto, form_reserva=form_reserva, tabela_quartos=tabela_quartos)

@app.route("/criar_quarto", methods=["POST", "GET"])
@login_required
def criar_quarto():
    form_quarto = FormCriarQuarto()
    form_reserva = FormReservarQuarto()
    tabela_quartos = Quarto.query.order_by(Quarto.quarto).all()

    if form_quarto.is_submitted():
        novo_quarto = Quarto(quarto=form_quarto.quarto.data, detalhes=form_quarto.detalhes.data)
        database.session.add(novo_quarto)
        database.session.commit()
        return redirect(url_for('reservas'))

    return render_template("reservas.html", form_quarto=form_quarto, form_reserva=form_reserva, tabela_quartos=tabela_quartos)

@app.route("/reservar_quarto", methods=["POST"])
@login_required
def reservar_quarto():
    form_quarto = FormCriarQuarto()
    form_reserva = FormReservarQuarto()
    tabela_quartos = Quarto.query.order_by(Quarto.quarto).all()

    if form_reserva.validate_on_submit():
        quarto_id = form_reserva.id.data
        quarto = Quarto.query.get(quarto_id)

        if quarto:
            if not quarto.status:
                quarto.status = True
                quarto.hospede = form_reserva.hospede.data
                quarto.check_in = datetime.now()
                quarto.check_out = datetime.combine(form_reserva.check_out.data, form_reserva.check_out_time.data)
                database.session.commit()

        return redirect(url_for('reservas'))

    return render_template("reservas.html", form_quarto=form_quarto, form_reserva=form_reserva, tabela_quartos=tabela_quartos)

@app.route("/excluir_info/<int:quarto_id>", methods=["GET"])
@login_required
def excluir_info(quarto_id):
    quarto = Quarto.query.get(quarto_id)
    if quarto:
        quarto.hospede = None
        quarto.check_in = None
        quarto.check_out = None
        quarto.status = False 
        database.session.commit()
    return redirect(url_for('reservas'))

@app.route("/editar_quarto/<int:quarto_id>", methods=["GET", "POST"])
@login_required
def editar_quarto(quarto_id):
    quarto = Quarto.query.get(quarto_id)
    
    if not quarto:
        return redirect(url_for('reservas'))
    
    form = FormQuarto(obj=quarto)
    
    if form.validate_on_submit():
        quarto.quarto = form.quarto.data
        quarto.hospede = form.hospede.data
        quarto.check_out = form.check_out.data
        quarto.check_out_time = form.check_out_time.data
        quarto.detalhes = form.detalhes.data
        database.session.commit()
        return redirect(url_for('reservas'))
    return render_template("editar_quarto.html", form=form, quarto=quarto)

@app.route("/excluir_quarto/<int:quarto_id>", methods=["GET"])
@login_required
def excluir_quarto(quarto_id):
    quarto = Quarto.query.get(quarto_id)
    if quarto:
        database.session.delete(quarto)
        database.session.commit()
    return redirect(url_for('reservas'))


@app.route("/filtrar_quartos", methods=["POST"])
@login_required
def filtrar_quartos():
    status = request.form.get("status")
    if status == "reservado":
        quartos_filtrados = Quarto.query.filter_by(status=True).all()
    elif status == "liberado":
        quartos_filtrados = Quarto.query.filter_by(status=False).all()
    else:
        quartos_filtrados = Quarto.query.order_by(Quarto.quarto).all()

    form_quarto = FormCriarQuarto()
    form_reserva = FormReservarQuarto() 
    return render_template("reservas.html", tabela_quartos=quartos_filtrados, form_quarto=form_quarto, form_reserva=form_reserva)



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    return render_template('home.html')

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