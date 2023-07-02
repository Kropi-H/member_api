from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = 'admin'
api_password = 'password'

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Authentication failed'}), 403
    return decorated

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()

    members_cur = db.execute('SELECT id, name, email, level from members')
    members_result = members_cur.fetchall()

    return_values = []
    for member in members_result:
        member_dict = {}
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']

        return_values.append(member_dict)

    return jsonify({'members':return_values})

@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db  = get_db()

    member_cur = db.execute('SELECT id, name, email, level FROM members WHERE id = ? ', [member_id])
    member_res = member_cur.fetchone()

    return jsonify({'member':{'id':member_res['id'],
                               'name':member_res['name'],
                               'email':member_res['email'],
                               'level':member_res['level']
                               }
                    })

@app.route('/member', methods=['POST'])
@protected
def add_member():
    db = get_db()

    new_member_data = request.get_json()

    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db.execute('INSERT INTO members (name, email, level) VALUES (?,?,?)', [name, email, level])
    db.commit()

    member_cur = db.execute('SELECT id, name, email, level FROM members WHERE name = ?', [name])
    member_result = member_cur.fetchone()

    return jsonify({'member':{'id':member_result['id'],
                    'name':member_result['name'],
                    'email':member_result['email'],
                    'level':member_result['level']}
                   })

@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
def edit_member(member_id):
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('UPDATE members SET name = ?, email = ?, level = ? WHERE id = ? ',[name, email, level, member_id])
    db.commit()

    member_cur = db.execute('SELECT id, name, email, level FROM members WHERE id = ?', [member_id])
    member_res = member_cur.fetchone()

    return jsonify({'member':{'id':member_res['id'],
                              'name':member_res['name'],
                              'email':member_res['email'],
                              'level':member_res['level']
                              }
                    })

@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()

    db.execute('DELETE FROM members WHERE id = ?', [member_id])
    db.commit()

    return jsonify({'message':'The member was deleted'})

if __name__=='__main__':
    app.run(debug=True)