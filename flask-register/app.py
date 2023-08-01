import logging
import re
import random
from flask import Flask, render_template, request, session, make_response

from db import Database
from get_captcha import get_captcha_code_and_content

app = Flask(__name__)

app.secret_key = 'notes.zhengxinonly.com'
app.permanent_session_lifetime = 3600


@app.route('/')
def index_view():
    is_login = session.get('is_login')
    return render_template('index.html', is_login=is_login)


@app.route('/register')
def register_view():
    return render_template('register.html')


@app.route('/login')
def login_view():
    return render_template('login.html')


@app.post('/api/send_register_sms')
def send_register_sms():
    # 1. 解析前端传递过来的数据
    data = request.get_json()
    mobile = data['mobile']

    # 2. 校验手机号码
    pattern = r'^1[3-9]\d{9}$'
    ret = re.match(pattern, mobile)
    if not ret:
        return {
            'message': '电话号码不符合格式',
            'code': -1
        }

    # 3. 发送短信验证码，并记录
    session['mobile'] = mobile
    # 3.1 生成随机验证码
    code = random.choices('123456789', k=6)
    session['code'] = ''.join(code)
    logging.warning(''.join(code))
    return {
        'message': '发送短信成功',
        'code': 0
    }


@app.post('/api/register')
def register_api():
    # 1. 解析前端传递过来的数据
    data = request.get_json()
    vercode = data['vercode']
    vercode2 = session['code']
    if vercode != vercode2:
        return {
            'message': '短信验证码错误',
            'code': -1
        }

    nickname = data['nickname']
    mobile = data['mobile']
    password = data['password']
    if not all([nickname, mobile, password]):
        return {
            'message': '数据缺失',
            'code': -1
        }
    Database().insert(nickname, mobile, password)
    return {
        'message': '注册用户成功',
        'code': 0
    }


@app.get('/get_captcha')
def get_captcha_view():
    # 1. 获取参数
    captcha_uuid = request.args.get("captcha_uuid")
    # 2. 生成验证码
    code, content = get_captcha_code_and_content()

    # 3. 记录数据到数据库（用session代替）
    session['code'] = code
    resp = make_response(content)  # 读取图片的二进制数据做成响应体
    resp.content_type = "image/png"
    # 4. 错误处理

    # 5. 响应返回
    return resp


@app.post('/api/login')
def login_api():
    data = request.get_json()
    ret = Database().search(data['mobile'])
    code = session['code']
    session['mobile'] = data['mobile']
    if code != data['captcha']:
        return {
            'message': '验证码错误',
            'code': -1
        }
    if not ret:
        return {
            'message': '用户不存在',
            'code': -1
        }
    pwd = ret[0]
    if pwd != data['password']:
        return {
            'message': '用户密码错误',
            'code': -1
        }
    session['is_login'] = True  # 记录用户登录
    return {
        'message': '用户登录成功',
        'code': 0
    }


@app.route('/logout')
def logout():
    resp = make_response(render_template('index.html'))
    resp.delete_cookie("session")
    return resp


@app.route('/login_mobile')
def login_mobile():
    return {
        'mobile': session.get('mobile'),
        'code': 0
    }


if __name__ == '__main__':
    app.run(debug=True)
