from flask import Flask,render_template
from flask import request
from flask import make_response
from flask import redirect
from flask_script import Manager
from flask_bootstrap import Bootstrap


app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

# 返回可变值
@app.route('/user/<name>')
def user(name):
    return '<h1>hello %s</h1>'%name.upper()

# 返回浏览器版本
@app.route('/agent')
def agent():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>'%user_agent

# 返回响应码
@app.route('/bad')
def bad():
    return '<h1>Bad Request</h1>',404

# 返回多个参数的相应
@app.route('/response')
def resp():
    response = make_response('<h1>This is a doc carried cookie.</h1>')
    response.set_cookie('answer','150')
    return response

# 返回重定向地址
@app.route('/redirect')
def red():
    return redirect('http://www.baidu.com')



if __name__ == '__main__':
    manager.run()
    app.run(debug=True)