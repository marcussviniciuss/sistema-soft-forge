#Criar a estrutura do banco de dados
from hms_softforge import database, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    cargo = database.Column(database.String, nullable=False)

class Tarefa(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    tarefa = database.Column(database.String, nullable=False)
    data = database.Column(database.DateTime, nullable=False, default=lambda: datetime.now())
    estado = database.Column(database.Boolean, nullable=False, default=False)
    concluido_por = database.Column(database.String, nullable=True) 
    realizada_em = database.Column(database.DateTime, nullable=True)    
    