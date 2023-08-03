from datetime import datetime

from flask import Flask, request, render_template, url_for
import config
from extensions import register_extension, db
from orms import StudentORM

app = Flask(__name__)

app.config.from_object(config)
register_extension(app)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.cli.command()
def create():
    db.drop_all()
    db.create_all()
    from faker import Faker
    import random

    faker = Faker(locale="zh-CN")

    for i in range(100):
        student = StudentORM()
        info = faker.simple_profile()
        student.name = info['name']
        student.gender = info['sex']
        student.mobile = faker.phone_number()
        student.address = info['address']
        student.class_name = random.choice(['一班', '二班', '三班'])
        student.save()


@app.route('/api/student')
def student_view():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)

    # paginate = StudentORM.query.paginate(page=page, per_page=per_page, error_out=False)
    q = db.select(StudentORM)
    name = request.args.get('name')
    if name:
        q = q.where(StudentORM.name == name)
    paginate = db.paginate(q, page=page, per_page=per_page, error_out=False)
    items: [StudentORM] = paginate.items
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': paginate.total,
        'data': [
            {
                'id': item.id,
                'name': item.name,
                'gender': item.gender,
                'mobile': item.mobile,
                'class_name': item.class_name,
                'address': item.address,
                'disable': item.disable,
                'is_del': item.is_del,
                'create_at': item.create_at.strftime('%Y-%m-%d %H:%M:%S'),
                'update_at': item.update_at.strftime('%Y-%m-%d %H:%M:%S'),
            } for item in items
        ]
    }


@app.post('/api/student')
def api_student_post():
    data = request.get_json()
    data['create_at'] = datetime.strptime(data['create_at'], '%Y-%m-%d %H:%M:%S')
    student = StudentORM()
    student.update(data)
    try:
        student.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '新增数据失败'
        }
    return {
        'code': 0,
        'msg': '新增数据成功'
    }


@app.get('/student_add')
def student_add():
    return render_template('student_add.html')


@app.put('/api/student/<int:sid>')
def api_student_put(sid):
    data = request.get_json()
    data['create_at'] = datetime.strptime(data['create_at'], '%Y-%m-%d %H:%M:%S')
    # student = StudentORM.query.get(sid)
    student = db.get_or_404(StudentORM, sid)
    student.update(data)
    try:
        student.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


@app.delete('/api/student/<int:sid>')
def api_student_del(sid):
    student: StudentORM = db.get_or_404(StudentORM, sid)
    try:
        # db.session.delete(student)
        student.is_del = True
        db.session.commit()
    except Exception as e:
        return {
            'code': -1,
            'msg': '删除数据失败'
        }
    return {
        'code': 0,
        'msg': '删除数据成功'
    }


@app.put('/api/student/<int:sid>/class_name')
def api_student_class_name(sid):
    student: StudentORM = db.get_or_404(StudentORM, sid)
    data = request.get_json()
    try:
        student.class_name = data['class_name']
        student.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改班级失败'
        }
    return {
        'code': 0,
        'msg': '修改班级成功'
    }


@app.put('/api/student/<int:sid>/address')
def api_student_address(sid):
    student: StudentORM = db.get_or_404(StudentORM, sid)
    data = request.get_json()
    try:
        student.address = data['address']
        student.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改地址失败'
        }
    return {
        'code': 0,
        'msg': '修改地址成功'
    }


@app.put('/api/student/<int:sid>/disable')
def api_student_disable(sid):
    student: StudentORM = db.get_or_404(StudentORM, sid)
    data = request.get_json()
    try:
        student.disable = data['disable']
        student.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改禁用失败'
        }
    return {
        'code': 0,
        'msg': '修改禁用成功'
    }


if __name__ == '__main__':
    app.run(debug=True)
