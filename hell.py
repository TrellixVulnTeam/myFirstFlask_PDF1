from flask import Flask,render_template,session,redirect,url_for,flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField
from wtforms.validators import DataRequired
from flask_script import Manager,Shell
import datetime

import os

from flask_sqlalchemy import SQLAlchemy
# 配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)
manager = Manager(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'

# 回调函数自动导入对象
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Comment=Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))


# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
SQLALCHEMY_TRACK_MODIFICATIONS = True

db = SQLAlchemy(app)

class NameForm(FlaskForm):
    name = StringField("请输入名字", validators=[DataRequired()])
    submit1 = SubmitField('提交')


class CommentForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    comment = TextAreaField("输入评论",validators=[DataRequired()])
    submit2 = SubmitField('提交')

class Role(db.Model):
    # 定义在数据库中的表名。若没定义，tablename，SQLAlchemy会使用一个默认名字
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    # backref参数向User模型中添加一个role属性，从而定义反向关系。这个属性可以代替role_id 访问Role模型。
    users =db.relationship('User',backref='role')

    # 返回一个具有可读性的字符串表示模型，可在调试和测试时候使用。
    def __repr__(self):
        return '<Role %r>'%self.name

class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer,primary_key=True)
    comment = db.Column(db.String(64),index=True)
    name = db.Column(db.String(64),index=True)
    time = db.Column(db.DateTime,default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Comment %r>'%self.comment

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

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

@app.route('/user/<name>',methods=['GET','POST'])
def user(name):
    new_comment = None
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(comment=form.comment.data,name=form.name.data,time=datetime.datetime.now())
        db.session.add(new_comment)
        # session['known'] = False
        # session['name'] = form.comment.data
        db.session.commit()
        flash("已评论！")

    comments = Comment.query.filter_by().all()
    print(form.comment.data)
    print(form.name.data)


    return render_template('user.html',comments=comments,form=form,name=name.capitalize())

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
    manager.run()
    app.run(debug=True)
