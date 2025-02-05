from flask import Blueprint

# Создание Blueprint для модуля user
user_blueprint = Blueprint('user', __name__, template_folder='templates')

from . import routes  # Импортируем routes для регистрации маршрутов