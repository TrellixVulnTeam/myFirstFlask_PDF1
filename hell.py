from flask import Flask,render_template,session,redirect,url_for,flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os

from flask.ext.sqlalchemy import SQLAlchemy
# 配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True

db = SQLAlchemy(app)

class NameForm(FlaskForm):
    name = StringField("请输入评论", validators=[DataRequired()])
    submit = SubmitField('提交')

class Role(db.Model):
    # 定义在数据库中的表名。若没定义，tablename，SQLAlchemy会使用一个默认名字
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)

    # 返回一个具有可读性的字符串表示模型，可在调试和测试时候使用。
    def __repr__(self):
        return '<Role %r>'%self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)

    def __repr__(self):
        return '<User %r>' % self.username



@app.route('/' ,methods=['GET','POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('You have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',
                           form = form,name =session.get('name'))
    #     name=form.name.data
    #     form.name.data=''
    # return render_template('index.html',
    #                        current_time=datetime.utcnow(),
    #                        form=form,
    #                        name=name)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name.capitalize())

@app.route('/test')
def tst():
    return render_template('test.html',title_name = 'test')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.route('/test1')
def ttt():
    return render_template('test1.html')
if __name__ == '__main__':
    app.run(debug=True)
