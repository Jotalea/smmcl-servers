from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from math import ceil
import os, uuid, random, string, hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Cambia el nombre del archivo por el que desees
db = SQLAlchemy(app)
set_token = "40592520046229"

class Stages(db.Model):
    id_stage = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    archivo = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, nullable=False)
    stage_id = db.Column(db.Text, nullable=False)
    entorno = db.Column(db.Text, nullable=False)
    apariencia = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    intentos = db.Column(db.Integer, nullable=False, default=0)
    muertes = db.Column(db.Integer, nullable=False, default=0)
    completed = db.Column(db.String(5), nullable=False, default='no')
    liked = db.Column(db.String(5), nullable=False, default='3')
    victorias = db.Column(db.Integer, nullable=False, default=0)
    featured = db.Column(db.String(5), nullable=False, default='0')
    record = db.Column(db.String(5), nullable=False, default='no')
    r_alias = db.Column(db.String(5), nullable=False, default='no')
    r_id = db.Column(db.String(5), nullable=False, default='no')
    r_time = db.Column(db.String(5), nullable=False, default='0')

class User(db.Model):
    id_user   = db.Column(db.Integer(11), primary_key=True)
    alias     = db.Column(db.String(255), nullable=False)
    password  = db.Column(db.String(255), nullable=False)
    auth_code = db.Column(db.String(6),   nullable=False)
    user_id   = db.Column(db.String(8),   nullable=False)
    uploads   = db.Column(db.Boolean,     nullable=False, default=False)
    booster   = db.Column(db.Boolean,     nullable=False, default=False)
    mod       = db.Column(db.Boolean,     nullable=False, default=False)
    mobile    = db.Column(db.Boolean,     nullable=False, default=False)
    create    = db.Column(db.DateTime,    nullable=False)

    def __init__(self, alias, password, auth_code, id_user, user_id):
        self.alias = alias
        self.password = password
        self.auth_code = auth_code
        self.id = id_user
        self.user_id = user_id
        self.uploads = 0
        self.booster = False
        self.mod = False
        self.mobile = False
        self.create = datetime.now()

@app.route('/stages', methods=['GET'])
def get_stages():
    stages = Stages.query.all()
    output = []
    for stage in stages:
        stage_data = {
            'id_stage': stage.id_stage,
            'name': stage.name,
            'archivo': stage.archivo,
            'date': stage.date,
            'id': stage.id,
            'entorno': stage.entorno,
            'apariencia': stage.apariencia,
            'author': stage.author,
            'likes': stage.likes,
            'intentos': stage.intentos,
            'muertes': stage.muertes,
            'completed': stage.completed,
            'liked': stage.liked,
            'victorias': stage.victorias,
            'featured': stage.featured,
            'record': stage.record,
            'r_alias': stage.r_alias,
            'r_id': stage.r_id,
            'r_time': stage.r_time
        }
        output.append(stage_data)
    return jsonify({'stages': output})

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {
            'id_user': user.id_user,
            'alias': user.alias,
            'password': user.password,
            'auth_code': user.auth_code,
            'booster': user.booster,
            'id': user.id,
            'mobile': user.mobile,
            'mod': user.mod,
            'uploads': user.uploads,
            'user_id': user.user_id
        }
        output.append(user_data)
    return jsonify({'users': output})

@app.route('/stages/delete', methods=['POST'])
def delete_stage():
    data = request.form
    token = data.get("token")
    discord_id = data.get("discord_id")
    auth_code = data.get("auth_code")
    stage_id = data.get("id")
    author = data.get("author")

    if token == set_token:
        stage = Stages.query.filter_by(id=stage_id, author=author).first()
        if stage:
            db.session.delete(stage)
            db.session.commit()
            return jsonify({"success": stage_id}), 200
        else:
            return jsonify({"message": "Error access denied", "code": "01"}), 401
    else:
        return jsonify({"message": "Error access denied", "code": "01"}), 401
    
@app.route('/stages/detailed_search_featured', methods=['POST'])
def detailed_search_featured():
    data = request.form
    token = data.get("token")
    discord_id = data.get("discord_id")
    auth_code = data.get("auth_code")
    page = int(data.get("page", 1))

    if token == set_token:
        rows_perpage = 20
        offset = (page - 1) * rows_perpage

        featured_stages = Stages.query.filter_by(featured='1').limit(rows_perpage).offset(offset).all()
        total_stages = Stages.query.filter_by(featured='1').count()
        pages = max(1, ceil(total_stages / rows_perpage))

        if featured_stages:
            result = []
            for stage in featured_stages:
                temp = {
                    "apariencia": stage.apariencia,
                    "archivo": stage.archivo,
                    "author": stage.author,
                    "date": stage.date,
                    "entorno": stage.entorno,
                    "featured": stage.featured,
                    "id": stage.id,
                    "intentos": stage.intentos,
                    "likes": stage.likes,
                    "muertes": stage.muertes,
                    "name": stage.name,
                    "record": {
                        "alias": stage.r_alias if stage.record == "yes" else None,
                        "id": stage.r_id if stage.record == "yes" else None,
                        "record": stage.record,
                        "time": stage.r_time if stage.record == "yes" else None
                    },
                    "user_data": {
                        "completed": stage.completed,
                        "liked": stage.liked
                    },
                    "victorias": stage.victorias
                }
                result.append(temp)

            response = {
                "num_rows": total_stages,
                "pages": pages,
                "rows_perpage": rows_perpage,
                "type": "detailed_search",
                "result": result
            }
            return jsonify(response), 200
        else:
            return jsonify({"message": "No featured stages found", "code": "01"}), 404
    else:
        return jsonify({"message": "Error access denied", "code": "01"}), 401

@app.route('/stages/detailed_search_id', methods=['POST'])
def detailed_search_id():
    data = request.form
    token = data.get("token")
    discord_id = data.get("discord_id")
    auth_code = data.get("auth_code")
    stage_id = data.get("id")

    if token == set_token:
        stage = Stages.query.filter_by(id=stage_id).first()
        if stage:
            stage_data = {
                "apariencia": stage.apariencia,
                "archivo": stage.archivo,
                "author": stage.author,
                "comments": stage.comments,
                "date": stage.date,
                "description": stage.description,
                "dislikes": stage.dislikes,
                "entorno": stage.entorno,
                "etiquetas": stage.etiquetas,
                "featured": stage.featured,
                "id": stage.id,
                "intentos": stage.intentos,
                "likes": stage.likes,
                "muertes": stage.muertes,
                "name": stage.name,
                "record": {
                    "alias": stage.r_alias if stage.record == "yes" else None,
                    "id": stage.r_id if stage.record == "yes" else None,
                    "record": stage.record,
                    "time": stage.time_r if stage.record == "yes" else None
                },
                "user_data": {
                    "completed": stage.completed,
                    "liked": stage.liked
                },
                "victorias": stage.victorias
            }
            response = {
                "result": stage_data,
                "type": "id"
            }
            return jsonify(response), 200
        else:
            return jsonify({"message": "Error level not found", "error_type": "01"}), 404
    else:
        return jsonify({"message": "Error access denied", "error_type": "01"}), 401

@app.route('/stages/detailed_search_popular', methods=['POST'])
def detailed_search_popular():
    data = request.form
    token = data.get("token")
    discord_id = data.get("discord_id")
    auth_code = data.get("auth_code")
    page = int(data.get("page", 1))

    if token == set_token:
        rows_perpage = 20
        offset = (page - 1) * rows_perpage

        popular_stages = Stages.query.order_by(Stages.intentos.desc()).limit(rows_perpage).offset(offset).all()
        total_stages = Stages.query.count()
        pages = max(1, ceil(total_stages / rows_perpage))

        if popular_stages:
            result = []
            for stage in popular_stages:
                stage_data = {
                    "apariencia": stage.apariencia,
                    "archivo": stage.archivo,
                    "author": stage.author,
                    "comments": stage.comments,
                    "date": stage.date,
                    "description": stage.description,
                    "dislikes": stage.dislikes,
                    "entorno": stage.entorno,
                    "etiquetas": stage.etiquetas,
                    "featured": stage.featured,
                    "id": stage.id,
                    "intentos": stage.intentos,
                    "likes": stage.likes,
                    "muertes": stage.muertes,
                    "name": stage.name,
                    "record": {
                        "alias": stage.r_alias if stage.record == "yes" else None,
                        "id": stage.r_id if stage.record == "yes" else None,
                        "record": stage.record,
                        "time": stage.time_r if stage.record == "yes" else None
                    },
                    "user_data": {
                        "completed": stage.completed,
                        "liked": stage.liked
                    },
                    "victorias": stage.victorias
                }
                result.append(stage_data)

            response = {
                "num_rows": total_stages,
                "pages": pages,
                "rows_perpage": rows_perpage,
                "type": "detailed_search_popular",
                "result": result
            }
            return jsonify(response), 200
        else:
            return jsonify({"message": "No popular stages found", "error_type": "01"}), 404
    else:
        return jsonify({"message": "Error access denied", "error_type": "01"}), 401

@app.route('/stages/detailed_search', methods=['POST'])
def detailed_search():
    data = request.form
    token = data.get("token")
    discord_id = data.get("discord_id")
    auth_code = data.get("auth_code")
    page = int(data.get("page", 1))

    if token == set_token:
        rows_perpage = 20
        offset = (page - 1) * rows_perpage

        popular_stages = Stages.query.order_by(Stages.intentos.desc()).limit(rows_perpage).offset(offset).all()
        total_stages = Stages.query.count()
        pages = max(1, ceil(total_stages / rows_perpage))

        if popular_stages:
            result = []
            for stage in popular_stages:
                stage_data = {
                    "apariencia": stage.apariencia,
                    "archivo": stage.archivo,
                    "author": stage.author,
                    "comments": stage.comments,
                    "date": stage.date,
                    "description": stage.description,
                    "dislikes": stage.dislikes,
                    "entorno": stage.entorno,
                    "etiquetas": stage.etiquetas,
                    "featured": stage.featured,
                    "id": stage.id,
                    "intentos": stage.intentos,
                    "likes": stage.likes,
                    "muertes": stage.muertes,
                    "name": stage.name,
                    "record": {
                        "alias": stage.r_alias if stage.record == "yes" else None,
                        "id": stage.r_id if stage.record == "yes" else None,
                        "record": stage.record,
                        "time": stage.time_r if stage.record == "yes" else None
                    },
                    "user_data": {
                        "completed": stage.completed,
                        "liked": stage.liked
                    },
                    "victorias": stage.victorias
                }
                result.append(stage_data)

            response = {
                "num_rows": total_stages,
                "pages": pages,
                "rows_perpage": rows_perpage,
                "type": "detailed_search_popular",
                "result": result
            }
            return jsonify(response), 200
        else:
            return jsonify({"message": "No popular stages found", "error_type": "01"}), 404
    else:
        return jsonify({"message": "Error access denied", "error_type": "01"}), 401

@app.route('/stages/stats', methods=['POST'])
def update_stats():
    data = request.form
    token = data.get("token")
    discord_id = data.get("discord_id")
    auth_code = data.get("auth_code")
    id = data.get("id")
    stats = data.get("stats")

    if token == set_token:
        stage = Stages.query.filter_by(id=id).first()
        if stage:
            if stats == "likes" or stats == "intentos" or stats == "muertes" or stats == "victorias":
                setattr(stage, stats, getattr(stage, stats) + 1)
                db.session.commit()
                return jsonify({"success": f"{stats} has been updated successfully.", "id": id, "type": "stats"}), 200
            else:
                return jsonify({"message": "Invalid stats field", "code": "02"}), 400
        else:
            return jsonify({"message": "Error level not found", "error_type": "01"}), 404
    else:
        return jsonify({"message": "Error access denied", "code": "01"}), 401

from datetime import datetime

@app.route('/stages/upload', methods=['POST'])
def upload_stage():
    data = request.form
    token = data.get("token")
    discord_id = data.get("discord_id")
    auth_code = data.get("auth_code")
    name = data.get("name")
    desc = data.get("desc")
    aparience = data.get("aparience")
    entorno = data.get("entorno")
    tags = data.get("tags")
    author = data.get("author")
    cw = data.get("cw")

    if token == set_token:
        DateAndTime = datetime.now().strftime("%d/%m/%Y")
        stage_id = "-".join(uuid.uuid4().hex[:8] for _ in range(4))
        stage_id = stage_id.upper()

        stage = Stages.query.filter_by(id=id).first()
        if not stage:
            try:
                # Guardar el archivo CW
                cw_filename = f"{id}.cw"
                with open(os.path.join("levels", cw_filename), "w") as f:
                    f.write(cw)

                # Guardar la información del nivel en la base de datos
                stage = Stages(
                    name=name,
                    apariencia=aparience,
                    entorno=entorno,
                    etiquetas=tags,
                    date=DateAndTime,
                    author=author,
                    description=desc,
                    archivo=cw_filename,
                    id=id
                )
                db.session.add(stage)
                db.session.commit()

                return jsonify({"success": name, "id": id}), 200
            except Exception as e:
                return jsonify({"message": "Error uploading stage", "error": str(e)}), 500
        else:
            return jsonify({"message": "Error: Stage already exists", "code": "07"}), 400
    else:
        return jsonify({"message": "Error access denied", "code": "01"}), 401

@app.route('/user/info', methods=['GET'])
def user_info():
    discord_id = request.args.get("discord_id")
    token = request.args.get("token")

    if token == set_token:
        user = User.query.filter_by(id=discord_id).first()
        if user:
            return jsonify({
                "User": user.alias,
                "Uploads": user.uploads,
                "Account date": user.create,
                "ID user": user.id_user
            }), 200
        else:
            return jsonify({"message": "The user is not registered"}), 404
    else:
        return jsonify({"message": "Error access denied"}), 401

@app.route('/user/login', methods=['POST'])
def user_login():
    data = request.form
    alias = data.get("alias")
    password = data.get("password")
    token = data.get("token")

    if token == set_token:
        user = User.query.filter_by(alias=alias, password=password).first()
        if user:
            auth_code = random.randint(1000, 9999)
            user.auth_code = auth_code
            db.session.commit()

            response = {
                "alias": user.alias,
                "id": user.id,
                "uploads": user.uploads,
                "auth_code": auth_code,
                "booster": user.booster,
                "mod": user.mod,
                "mobile": user.mobile
            }
            return jsonify(response), 200
        else:
            return jsonify({"message": "Incorrect username or password"}), 401
    else:
        return jsonify({"message": "Access denied"}), 403
    
@app.route('/user/sign', methods=['GET'])
def user_sign():
    alias = request.args.get("alias")
    discord_id = request.args.get("discord_id")
    password = request.args.get("password")
    token = request.args.get("token")

    if token == set_token:
        if not User.query.filter_by(id=discord_id).first():
            if not User.query.filter_by(alias=alias).first():
                result = create_user(alias, password, discord_id)
                if result:
                    return ":white_check_mark: Account successfully created for " + alias, 200
                else:
                    return "Error creating account", 500
            else:
                return ":x: ERROR: The username is not available.", 400
        else:
            return ":x: ERROR: You have already created an account.", 400
    else:
        return "Error access denied", 403

def create_user(alias, password, discord_id):
    auth = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    id_user = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)).replace("-", "")
    password = hashlib.sha1(password.encode()).hexdigest()

    user = User(alias=alias, password=password, auth_code=auth, id=discord_id, user_id=id_user)
    db.session.add(user)
    db.session.commit()
    return True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)