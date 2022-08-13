from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import event
from pytz import timezone
from dateutil import parser
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(256), unique=True,
                        nullable=False)
    print_name = db.Column(db.String(256), unique=False, nullable=False)
    password = db.Column(db.String(256), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    n_submit = db.Column(db.Integer, default=0)
    scores = db.relationship("Score", backref="users")

    def __init__(self, user_id, password, print_name, is_admin=False):
        self.user_id = user_id
        self.password = password
        self.print_name = print_name
        self.is_admin = is_admin

    def __repr__(self):
        return self.user_id

    def get_id(self):
        return (self.user_id)


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value)
    return value


class Score(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.TIMESTAMP, server_default=current_timestamp())
    user_primary_key = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.Column(db.String(256), unique=False, nullable=True)
    user = db.relationship("User")

    # 複数の評価指標を表示したい場合以下に適宜追加
    ndcg = db.Column(db.Float, nullable=False)
    f1 = db.Column(db.Float, nullable=False)

    # 各評価指標の変数名と表示名のマッピング。
    metrics_name_dict = {
        "ndcg": "nDCG@5",
        "f1": "F値"
    }

    # ソートに用いる（最終評価に用いる）評価指標を変数名で指定
    sort_key = "ndcg"

    def __init__(self, result_dict):
        self.user_primary_key = result_dict['user_primary_key']
        self.comment = result_dict['comment']

        for var_name in self.metrics_name_dict.keys():
            self.__dict__[var_name] = result_dict['var_name']
