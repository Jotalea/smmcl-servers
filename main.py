import asyncio, concurrent.futures, discord, hashlib, json, os, psutil, random, requests, string, subprocess, threading, time, queue
from threading import Thread
from flask import Flask, request, jsonify
from datetime import datetime
from cryptography.fernet import Fernet

# Only for the public
import keys

BOT_TOKEN = keys.BOT_TOKEN
BOT_INVITE = keys.BOT_INVITE
DISCORD_UPLOAD_CHANNEL_ID = keys.DISCORD_UPLOAD_CHANNEL_ID
SERVER_PASSWORD = keys.SERVER_PASSWORD
STAGE_WEBHOOK_URL = keys.WEBHOOK
UPLOAD_FOLDER = 'stages'
ALLOWED_EXTENSIONS = {'cw', 'json'}
SERVER_IP = "127.0.0.1"
SERVER_PORT = 14984
MODERATOR_TEAM = ["795013781607546931", "1102029166850867230", "1185758698975531099", "801458646914695218", "1142952460508483696"]
BETA_TESTERS = MODERATOR_TEAM

with open("database.json", "r") as db:
    DATABASE = json.loads(db.read())

print(DATABASE)

if not DATABASE:
    DATABASE = {
        "stages": [],
        "accounts": [
            {
                "id": 1,
                "username": "Server",
                "password": "123456",
                "discordid": "",
                "uploads": [],
                "banned": False
            }
        ],
        "sessions": []
    }

def webserver(): # Poder minimizar el código del servidor en el editor
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    def generate_id():
        id = ''
        for _ in range(4): # 1-2-3-4
            id += ''.join(random.choices(string.ascii_letters + string.digits, k=4)) # k= 1234-
            id += '-'
        return id[:-1].upper()  # Eliminar el último guion y hacer mayúscula

    def generate_session_token(input_t):
        hashed_value = hashlib.sha256(input_t.encode()).hexdigest()
        secret_key = Fernet.generate_key()
        cipher_suite = Fernet(secret_key)
        return f"cl-{str(cipher_suite.encrypt(hashed_value.encode()))[16:][:77]}"

    @app.route("/", methods=["GET"])
    def index():
        return "Hello!"

    @app.route("/api/stage/upload", methods=["POST"])
    def uploadstage():
        global DATABASE
        if request.method == "POST":
            data = request.get_json()

            # Revisar si es una solicitud autorizada
            serverpasscode = data.get('auth')
            user_session = data.get('session')
            if str(serverpasscode) == str(SERVER_PASSWORD):
                # Es una solicitud autorizada por el juego, continuar con el proceso
                user_auth_required = True
                if user_auth_required:
                    for session in DATABASE['sessions']:
                        if session['hash'] == user_session:
                            # El usuario inició sesión
                            if int(time.time()) - session['time'] < 604800:
                                # Sesión válida
                                pass
                            else:
                                # Es una solicitud NO autorizada
                                return jsonify({"message": "Session expired, try logging in again"}), 403
                        else:
                            return jsonify({"message": "Not logged in"}), 403
            else:
                # Es una solicitud NO autorizada
                return jsonify({"message": "Not authorized"}), 401

            stage_username = data.get('username')

            accounts = []
            for account in DATABASE['accounts']:
                accounts.append(account)
                if account['username'] == stage_username:
                    if account['banned']:
                        return jsonify({"message": "The user is banned", "stageid": stage_id, "extracontent": ""}), 403

            if not stage_username in DATABASE['accounts']:
                return jsonify({"message": "Unregistered user", "stageid": stage_id, "extracontent": ""}), 404

            # Procesando datos del nivel
            stage_title = data.get('title').replace('"', '').replace('/', '').replace('(', '').replace(')', '').replace('=', '').replace('`', '').replace('\'', '').replace('\\', '')#.replace(' ', '_').replace('#', '')
            stage_description = data.get('description')
            stage_data = data.get('content')

            stage_id = generate_id()

            # Verificar si el directorio existe, si no existe, créalo
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            # Guardar el archivo en el directorio
            with open(os.path.join(app.config['UPLOAD_FOLDER'], f"{stage_id}.cw"), "w") as stage_file:
                stage_file.write(stage_data)

            # Datos del nuevo nivel
            nuevo_nivel = {
                "id": stage_id,
                "title": stage_title,
                "description": stage_description,
                "author": stage_username,
                "file": f"{stage_id}.cw",
                "likes": 0,
                "dislikes": 0,
                "difficulty": "Normal",
                "reacted": [],
                "timestamp": int(time.time())
            }

            # Agregar el nuevo nivel al arreglo 'stages'
            DATABASE['stages'].append(nuevo_nivel)

            # Actualizar los datos del usuario que publicó el nuevo nivel en el arreglo 'accounts'
            for account in DATABASE['accounts']:
                if account['username'] == stage_username:
                    account['uploads'].append(nuevo_nivel['id'])

            # Guardar los datos actualizados en el archivo
            with open("database.json", 'w') as file:
                json.dump(DATABASE, file, indent=4)


            payload = {
                "embeds": [
                    {
                        "title": "Nuevo nivel publicado!",
                        "color": 1127128,
                        "description": f"**{stage_title}**\n\nHecho por **{stage_username}**\n\nDescripción: `{stage_description}`\nID: `{stage_id}`",
                    }
                ]
            }

            # Definir los archivos
            files = {"file1": open(stage_file, "rb")}

            # Enviar la solicitud POST
            response = requests.post(STAGE_WEBHOOK_URL, json=payload)
            response = requests.post(STAGE_WEBHOOK_URL, files=files)

            #request.form["title"] # Contenido desde formulario HTML
            #request.form.get["title"] # Existe? desde formulario HTML

            # Debug
            print( "Título: "      + stage_title       )
            print( "Descripción: " + stage_description )
            print( "Usuario: "     + stage_username    )
            print( "Datos: "       + stage_data        )

            return jsonify({"message": "Stage uploaded", "stageid": stage_id}), 200

    @app.route("/api/stage/id", methods=["POST"])
    def downloadstage():
        global DATABASE
        if request.method == "POST":
            data = request.get_json()

            # Revisar si es una solicitud autorizada
            serverpasscode = data.get('auth')
            user_session = data.get('session')
            if str(serverpasscode) == str(SERVER_PASSWORD):
                # Es una solicitud autorizada por el juego, continuar con el proceso
                user_auth_required = True
                if user_auth_required:
                    for session in DATABASE['sessions']:
                        if session['hash'] == user_session:
                            # El usuario inició sesión
                            if int(time.time()) - session['time'] < 604800:
                                # Sesión válida
                                pass
                            else:
                                # Es una solicitud NO autorizada
                                return jsonify({"message": "Session expired, try logging in again"}), 403
                        else:
                            return jsonify({"message": "Not logged in"}), 403
            else:
                # Es una solicitud NO autorizada
                return jsonify({"message": "Not authorized"}), 401

            stage_id = data.get('stageid')
            print(stage_id)

            for level in DATABASE['stages']:
                if level['id'] == stage_id:
                    stage_title = level['title']

            # Verificar si el archivo existe
            filename = f"{stage_id}.cw"
            filepath = f"{str(os.getcwd())}/" + str(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(filepath)
            print(str(os.getcwd()))

            if os.path.exists(filepath):
                with open(filepath, "r") as stagefile:
                    stagecontent = stagefile.read()
                return jsonify({"message": "Sucess", "content": stagecontent})
            else:
                return jsonify({"message": f"File {filename} not found"}), 404

    @app.route("/api/stage/getlatest", methods=["POST"])
    def getstageslatest():
        global DATABASE
        if request.method == "POST":
            data = request.get_json()

            # Revisar si es una solicitud autorizada
            serverpasscode = data.get('auth')
            user_session = data.get('session')
            if str(serverpasscode) == str(SERVER_PASSWORD):
                # Es una solicitud autorizada por el juego, continuar con el proceso
                user_auth_required = True
                if user_auth_required:
                    for session in DATABASE['sessions']:
                        if session['hash'] == user_session:
                            # El usuario inició sesión
                            if int(time.time()) - session['time'] < 604800:
                                # Sesión válida
                                pass
                            else:
                                # Es una solicitud NO autorizada
                                return jsonify({"message": "Session expired, try logging in again"}), 403
                        else:
                            return jsonify({"message": "Not logged in"}), 403
            else:
                # Es una solicitud NO autorizada
                return jsonify({"message": "Not authorized"}), 401

            page = data.get('page', 0)  # Valor predeterminado de la página
            stages_per_page = 10  # Número de escenarios por página

            # Lista para almacenar los nombres de los archivos de los niveles
            stage_files_list = []

            # Obtener la lista de archivos ordenados por fecha de modificación
            files_sorted = sorted(os.listdir('stages'), key=lambda x: os.path.getmtime(os.path.join('stages', x)), reverse=True)

            # Calcular el índice inicial y final de los escenarios para la página especificada
            start_index = page * stages_per_page
            end_index = (page + 1) * stages_per_page

            # Extraer los nombres de los escenarios para la página actual
            for archivo in files_sorted[start_index:end_index]:
                stage_files_list.append(archivo)

            stages_list = []

            for stage in stage_files_list:
                stage_id = stage[:3] # Sacar la extensión del archivo para tener sólo la ID del nivel
                stage_file = stage
                for x in DATABASE["stages"]:
                    if x["id"] == stage_id:
                        stage_title = x["title"]
                        stage_author = x["author"]
                stage_info = {
                    "id": stage_id,
                    "file": stage_file,
                    "title": stage_title,
                    "author": stage_author
                }
                stages_list.append(stage_info)

            return jsonify({"message": "", "list": stages_list})

    @app.route("/api/stage/like", methods=["POST"])
    def like():
        global DATABASE
        if request.method == "POST":
            data = request.get_json()

            # Revisar si es una solicitud autorizada
            serverpasscode = data.get('auth')
            user_session = data.get('session')
            if str(serverpasscode) == str(SERVER_PASSWORD):
                # Es una solicitud autorizada por el juego, continuar con el proceso
                user_auth_required = True
                if user_auth_required:
                    for session in DATABASE['sessions']:
                        if session['hash'] == user_session:
                            # El usuario inició sesión
                            if int(time.time()) - session['time'] < 604800:
                                # Sesión válida
                                pass
                            else:
                                # Es una solicitud NO autorizada
                                return jsonify({"message": "Session expired, try logging in again"}), 403
                        else:
                            return jsonify({"message": "Not logged in"}), 403
            else:
                # Es una solicitud NO autorizada
                return jsonify({"message": "Not authorized"}), 401

            likedstage = data.get('stageid')
            userid = data.get('userid')

            for level in DATABASE['stages']:
                if level['id'] == likedstage:
                    if userid in level['reacted']:
                        return jsonify({"message": "User already reacted"}), 409
                    else:
                        level['likes'] = level['likes'] + 1
                        level["reacted"].append(userid)

            with open("database.json", 'w') as file:
                json.dump(DATABASE, file, indent=4)

            return jsonify({"message": "Like successful"}), 200

    @app.route("/api/stage/dislike", methods=["POST"])
    def dislike():
        global DATABASE
        if request.method == "POST":
            data = request.get_json()

            # Revisar si es una solicitud autorizada
            serverpasscode = data.get('auth')
            user_session = data.get('session')
            if str(serverpasscode) == str(SERVER_PASSWORD):
                # Es una solicitud autorizada por el juego, continuar con el proceso
                user_auth_required = True
                if user_auth_required:
                    for session in DATABASE['sessions']:
                        if session['hash'] == user_session:
                            # El usuario inició sesión
                            if int(time.time()) - session['time'] < 604800:
                                # Sesión válida
                                pass
                            else:
                                # Es una solicitud NO autorizada
                                return jsonify({"message": "Session expired, try logging in again"}), 403
                        else:
                            return jsonify({"message": "Not logged in"}), 403
            else:
                # Es una solicitud NO autorizada
                return jsonify({"message": "Not authorized"}), 401

            dislikedstage = data.get('stageid')
            userid = data.get('userid')

            for level in DATABASE['stages']:
                if level['id'] == dislikedstage:
                    if userid in level['reacted']:
                        return jsonify({"message": "User already reacted"}), 409
                    else:
                        level['dislikes'] = level['dislikes'] + 1
                        level["reacted"].append(userid)

            with open("database.json", 'w') as file:
                json.dump(DATABASE, file, indent=4)

            return jsonify({"message": "Dislike successful"}), 200

    @app.route("/api/account/register", methods=["POST"])
    def registeraccount():
        if request.method == "POST":
            data = request.get_json()

            # Revisar si es una solicitud autorizada
            serverpasscode = data.get('auth')
            user_session = data.get('session')
            if str(serverpasscode) == str(SERVER_PASSWORD):
                # Es una solicitud autorizada por el juego, continuar con el proceso
                user_auth_required = False
            else:
                # Es una solicitud NO autorizada
                return jsonify({"message": "Not authorized"}), 401

            account_username = data.get('username')
            account_password = data.get('password')
            account_discordid = data.get('discord')

            # Datos de la nueva cuenta
            nueva_cuenta = {
                "id": max(account["id"] for account in DATABASE["accounts"]) + 1,
                "username": account_username,
                "password": account_password,
                "discordid": account_discordid,
                "uploads": [],
                "banned": False
            }

            # Agregar la nueva cuenta al arreglo 'accounts'
            DATABASE['accounts'].append(nueva_cuenta)

            # Guardar los datos actualizados en el archivo
            with open("database.json", 'w') as file:
                json.dump(DATABASE, file, indent=4)

            return jsonify({"message": "Account created"}), 200

    @app.route("/api/account/login", methods=["POST"])
    def login():
        if request.method == "POST":
            data = request.get_json()

            # Revisar si es una solicitud autorizada
            serverpasscode = data.get('auth')
            user_session = data.get('session')
            if str(serverpasscode) == str(SERVER_PASSWORD):
                # Es una solicitud autorizada por el juego, continuar con el proceso
                user_auth_required = False
            else:
                # Es una solicitud NO autorizada
                return jsonify({"message": "Not authorized"}), 401

            session_username = data.get('username')
            session_password = data.get('password')

            session_token = generate_session_token(f"{session_username}{session_password}")

            # Datos de la nueva sesion
            session = {
                "id": max(account["id"] for account in DATABASE["accounts"]) + 1,
                "username": session_username,
                "password": session_password,
                "token": session_token,
                "timestamp": int(time.time())
            }

            # Agregar la nueva cuenta al arreglo 'accounts'
            DATABASE['sessions'].append(session)

            # Guardar los datos actualizados en el archivo
            with open("database.json", 'w') as file:
                json.dump(DATABASE, file, indent=4)

            return jsonify({"message": f"Logged in as {session_username}", "token": session_token}), 200

    @app.route("/api/example", methods=["POST"])
    def example():
        if request.method == "POST":
            data = request.get_json()

            # Revisar si es una solicitud autorizada
            serverpasscode = data.get('auth')
            user_session = data.get('session')
            if str(serverpasscode) == str(SERVER_PASSWORD):
                # Es una solicitud autorizada por el juego, continuar con el proceso
                user_auth_required = False
                if user_auth_required:
                    for session in DATABASE['sessions']:
                        if session['hash'] == user_session:
                            # El usuario inició sesión
                            if int(time.time()) - session['time'] < 604800:
                                # Sesión válida
                                pass
                            else:
                                # Es una solicitud NO autorizada
                                return jsonify({"message": "Session expired, try logging in again"}), 403
                        else:
                            return jsonify({"message": "Not logged in"}), 403
            else:
                # Es una solicitud NO autorizada
                return jsonify({"message": "Not authorized"}), 401

            return jsonify({"message": "Example text"}), 200

    def run():
        app.run(host='0.0.0.0',port=8081)

    t = Thread(target=run) 
    t.start()

if True: # Poder minimizar el código del bot de Discord en el editor
    from discord.ext import commands
    from discord.ext.commands import has_permissions
    from discord.gateway import DiscordWebSocket

    bot = commands.Bot(command_prefix='lw.', intents=discord.Intents.all())

    async def identify(self):
        payload = {
            "op": self.IDENTIFY,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "Discord Android",
                    "$browser": "Discord Android",
                    "$device": "Android",
                    "$referrer": "",
                    "$referring_domain": "",
                },
                "compress": True,
                "large_threshold": 250,
            },
        }

        if self.shard_id is not None and self.shard_count is not None:
            payload["d"]["shard"] = [self.shard_id, self.shard_count]

        state = self._connection
        if state._activity is not None or state._status is not None:
            payload["d"]["presence"] = {
                "status": state._status,
                "game": state._activity,
                "since": 0,
                "afk": False,
            }

        if state._intents is not None:
            payload["d"]["intents"] = state._intents.value

        await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
        await self.send_as_json(payload)

    # Usar celular (50%/50%)
    #if random.choice([True, False]):
    #    DiscordWebSocket.identify = identify

    #DiscordWebSocket.identify = identify

    # Función para enviar un mensaje al canal específico
    async def send_message_to_channel(channel_id=DISCORD_UPLOAD_CHANNEL_ID, message="Prueba"):
        channel = bot.get_channel(channel_id)
        await channel.send(message)

    @bot.event
    async def on_ready():
        print(f"Bot {bot.user} online ID ({bot.user.id})")
        await bot.change_presence(activity=discord.Game(name="SMM Legacy World"))

    @bot.command(name='setup')
    async def setup(ctx):
        global SERVER_PORT
        global SERVER_IP
        global BETA_TESTERS
        embed = discord.Embed(title="Registrar una cuenta", description="Para registrar una cuenta, responde las preguntas por mensaje directo", color=0xffffff)
        await ctx.send(embed=embed)

        pr1 = discord.Embed(title="Registro", description="Escribe tu nombre de usuario", color=0xffffff)
        pr2 = discord.Embed(title="Registro", description="Escribe tu contraseña (mínimo 5 caracteres)", color=0xffffff)

        # Preguntas del formulario
        preguntas = [pr1, pr2]

        respuestas = []

        # Iterar sobre las preguntas y esperar las respuestas del usuario
        def check(m):
            return m.author.id == ctx.author.id and m.channel.type == discord.ChannelType.private

        for pregunta in preguntas:
            await ctx.author.send(embed=pregunta)
            respuesta = await bot.wait_for('message', check=check)
            respuestas.append(respuesta.content)

        # Mostrar las respuestas del formulario
        await ctx.author.send("Procesando...")

        usuario, contraseña = respuestas

        if len(usuario) > 16:
            e = discord.Embed(title="Error", description="Nombre de usuario demasiado largo\nIntentá de nuevo", color=0xffffff)
            await ctx.send(embed=e)
            return
        elif len(usuario) < 4:
            e = discord.Embed(title="Error", description="Nombre de usuario demasiado corto\nIntentá de nuevo", color=0xffffff)
            await ctx.send(embed=e)
            return
        elif len(contraseña) < 4:
            e = discord.Embed(title="Error", description="Contraseña demasiado corta\nIntentá de nuevo", color=0xffffff)
            await ctx.send(embed=e)
            return
        elif len(contraseña) > 64:
            e = discord.Embed(title="Error", description="Contraseña demasiado larga\nIntentá de nuevo", color=0xffffff)
            await ctx.send(embed=e)
            return

        e = discord.Embed(title="Verificación", description="Son estos valores correctos?", color=0xffffff)
        e.add_field(name="Nombre", value=str(usuario))
        e.add_field(name="Contraseña", value=str(contraseña))
        await ctx.author.send(embed=e)

        def check_confirmation(m):
            return m.author.id == ctx.author.id and m.channel.type == discord.ChannelType.private and m.content.lower() in ["si", "sí", "s", "y", "yes", "obvio", "claro"]

        respuestafinal = await bot.wait_for('message', check=check_confirmation)
        if respuestafinal.content.lower() in ["si", "sí", "s", "y", "yes", "obvio", "claro"]:
            await ctx.send("Procesando...")
            # URL del servidor donde está alojado el código
            url = f'http://{SERVER_IP}:{SERVER_PORT}/api/account/register'  # Reemplaza con la dirección y puerto correctos

            # Datos de la nueva cuenta
            nueva_cuenta = {
                "id": max(account["id"] for account in DATABASE["accounts"]) + 1,
                "username": usuario,
                "password": contraseña,
                "discordid": str(ctx.author.id),
                "uploads": [],
                "banned": False,
                "beta": False if nueva_cuenta["discordid"] in BETA_TESTERS else True
            }

            # Agregar la nueva cuenta al arreglo 'accounts'
            DATABASE['accounts'].append(nueva_cuenta)

            # Guardar los datos actualizados en el archivo
            with open("database.json", 'w') as file:
                json.dump(DATABASE, file, indent=4)

            # Datos para registrar una cuenta
            #data = {
            #    "auth": SERVER_PASSWORD,
            #    "username": usuario,
            #    "password": contraseña,
            #    "discord": str(ctx.author.id)
            #}

            # Realizar la solicitud POST
            #response = requests.post(url, json=data)

            # Analizar la respuesta
            #if response.status_code == 200:
            #    print("Cuenta creada exitosamente")
            #elif response.status_code == 403:
            #    print("No autorizado para realizar la solicitud")
            #else:
            #    print("Error al procesar la solicitud:", response.status_code)
            #    print(response.json())

            e = discord.Embed(title="Éxito", description="Cuenta registrada\nYa podés jugar", color=0xffffff)
            await ctx.author.send(embed=e)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(title="Cancelar", description="Cancelando...", color=0xffffff)
            await ctx.author.send(embed=e)
            await ctx.send(embed=e)
            return

    @bot.command(name='link')
    async def link(ctx):
        await ctx.send("Comando en desarrollo...")

    @bot.command(name='gameban')
    async def gameban(ctx, *, args):
        if not str(ctx.author.id) in MODERATOR_TEAM:
            await ctx.send("No sos moderador del juego")
            return
        if args.split(" ")[1]:
            if args.split(" ")[1] == "unban":
                for user in DATABASE['accounts']:
                    if user['username'] == str(args.split(" ")[0]):
                        user['banned'] = False
                        await ctx.send(f"Usuario {user['username']} desbaneado")
        else:
            for user in DATABASE['accounts']:
                if user['username'] == str(args.split(" ")[0]):
                    user['banned'] = True
                    await ctx.send(f"Usuario {user['username']} baneado")

        # Guardar los datos actualizados en el archivo
        with open("database.json", 'w') as file:
            json.dump(DATABASE, file, indent=4)

    @bot.command(name='list')
    async def lists(ctx, *, args):
        if not str(ctx.author.id) in MODERATOR_TEAM:
            await ctx.send("No sos moderador del juego")
            return
        if args.split(" ")[0]:
            if args.split(" ")[0] == "showpasswords":
                e = discord.Embed(title="Usuarios y contraseñas", description="Listado de todos los usuarios y sus contraseñas", color=0xffffff)
                for user in DATABASE['accounts']:
                    e.add_field(name=str(user['username']), value=str(user['password']))
                await ctx.send(embed=e)
            elif args.split(" ")[0] == "users":
                e = discord.Embed(title="Usuarios", description="Listado de todos los usuarios", color=0xffffff)
                for user in DATABASE['accounts']:
                    e.add_field(name="Nombre", value=str(user['username']))
                await ctx.send(embed=e)
        else:
            e = discord.Embed(title="Comando list", description="Uso:\n`list` + opción\nOpciones:\n- `showpasswords`\n- `users`", color=0xffffff)
            await ctx.send(embed=e)

    @bot.command()
    async def removeallusers(ctx):
        await ctx.send("Comando en desarrollo")

    @bot.command()
    async def variable(ctx, action, variable_name):
        # Verificar si el usuario tiene el ID correcto
        if str(ctx.author.id) in MODERATOR_TEAM:
            # Acción de leer el contenido de una variable
            if action == 'read':
                try:
                    # Obtener el valor de la variable
                    variable_value = eval(variable_name)
                    await ctx.send(f"El contenido de '{variable_name}' es: {variable_value}")
                except NameError:
                    await ctx.send(f"La variable '{variable_name}' no existe.")
            else:
                await ctx.send("Acción no válida. Debes usar 'read' para leer el contenido de una variable.")
        else:
            # Si el usuario no tiene el ID correcto, enviar un mensaje de error
            await ctx.send("No tienes permiso para usar este comando.")

    @bot.command()
    async def cmdrun(ctx, program_name):
        try:
            output_bytes = subprocess.check_output(program_name, shell=True)
            output = output_bytes.decode('utf-8')
        except subprocess.CalledProcessError:
            output = f"bash: {program_name}: command not found"
        finally:
            e = discord.Embed(title="Comando ejecutado", description=f"{os.getcwd()}$ {program_name}\n{str(output)}", color=0xffffff)
            await ctx.send(embed=e)

    @bot.command()
    async def search(ctx):
        await ctx.send("Comando en desarrollo")

    @bot.command()
    async def delete(ctx):
        await ctx.send("Comando en desarrollo")

    @bot.command()
    async def ping(ctx):

        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        bot_latency = round(bot.latency * 1000)
        api_latency = round((discord.utils.utcnow() - ctx.message.created_at).total_seconds() * 1000)

        embed = discord.Embed(title="Pong!", color=0xffffff)
        embed.add_field(name="Bot ping", value=f"{bot_latency}ms")
        embed.add_field(name="API ping", value=f"{api_latency}ms")
        embed.add_field(name="CPU Usage", value=f"{cpu_percent}%")
        embed.add_field(name="RAM Usage", value=f"{memory_percent}%")
        await ctx.reply(embed=embed, mention_author=True)

    @bot.listen('on_message')
    async def on_message(message):
        server_name = message.guild.name if message.guild else "the DMs"
        username = message.author.name
        print(f"[MESSAGE] {datetime.now().strftime('%H:%M %d/%m/%Y')} [{server_name}] #{message.channel.name} @{username} ({message.author.id}):\n{message.content}")
        if message.attachments:
            for attachment in message.attachments:
                print(f'Attached file: {attachment.url}')

webserver()
bot.run(BOT_TOKEN)