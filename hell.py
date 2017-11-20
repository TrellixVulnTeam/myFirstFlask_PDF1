from flask import Flask,render_template,session,redirect,url_for,flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField,IntegerField
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
    return dict(app=app, db=db, User=User, Role=Role, Comment=Comment,Thing=Thing)
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
    # name = StringField('Name',validators=[DataRequired()])
    comment = TextAreaField("输入评论",validators=[DataRequired()])
    fromid = IntegerField('用户id',validators=[DataRequired()])
    toid = IntegerField('评论id',default=None)
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
    content = db.Column(db.String(64),index=True)
    time = db.Column(db.DateTime,default=datetime.datetime.utcnow())
    thing_id = db.Column(db.String(64),db.ForeignKey('things.id'))
    from_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    to_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=True)

    def __repr__(self):
        return '<Comment:%r, name:%r, thingid:%r, fromid:%r, toid:%r>'%(self.content,self.name,self.thing_id,self.from_id,self.to_id)

class Thing(db.Model):
    __tablename__='things'
    id = db.Column(db.Integer,primary_key=True)
    thing = db.Column(db.String(64))
    comments = db.relationship('Comment',backref='thing')
    price = db.Column(db.Integer)
    about = db.Column(db.String(256))

    def __repr__(self):
        return '<Thing %r>'%self.thing


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    reply_to = db.relationship('Comment',foreign_keys=[Comment.from_id],backref=db.backref('replier', lazy='joined'))
    replier = db.relationship('Comment', foreign_keys=[Comment.to_id], backref=db.backref('reply_to', lazy='joined'))

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
        new_comment = Comment(content=form.comment.data,time=datetime.datetime.now()
                              ,from_id=form.fromid.data,to_id=form.toid.data,thing_id=1)
        db.session.add(new_comment)
        # session['known'] = False
        # session['name'] = form.comment.data
        db.session.commit()
        flash("已评论！")
        # 页面刷新后清除评论记录，整型的有问题
        form.fromid.raw_data=None
        form.toid.raw_data=None
        form.comment.data=''

    comments = Comment.query.filter_by().all()
    things = Thing.query.filter_by(id=1).first()
    # print(form.fromid.data,'评论了： ',form.comment.data)


    return render_template('user.html',things=things,comments=comments,form=form,name=name.capitalize())

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
