#Criar os formularios do site
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from hms_softforge.models import Usuario

class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()]) 
    senha = PasswordField("Senha", validators=[DataRequired()])
    botao_confirmacao = SubmitField("Fazer Login")
    
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if not usuario:
            raise ValidationError("E-mail não cadastrado, por favor peça ao gerente que realize seu cadastro.")

class FormCriarConta(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField("Confirme a Senha", validators=[DataRequired(), EqualTo("senha")])
    cargo = SelectField('Cargo', choices = [('gerente', 'Gerente'), ('atendente', 'Atendente'), ('funcionario', 'Funcionário')])
    botao_confirmacao = SubmitField("Criar Conta")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("E-mail já cadastrado, por favor faça o login.")

class FormNovaTarefa(FlaskForm):
    tarefa = StringField("Nova tarefa", validators=[DataRequired()])
    botao_confirmacao = SubmitField("Enviar")
    