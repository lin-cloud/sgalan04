"""
Controlador de la aplicacion
"""
import hashlib
import locale
import os
import sqlalchemy
from flask import Flask, request, session, jsonify, render_template, send_from_directory, Response, send_file
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import base64
from io import BytesIO
from PIL import Image
import estimacion


#
# ---> Run the application inside a Docker container <--
Docker = True
#
#
if Docker:
    import procesadoECG
else:
    import procesadoECG2

app = Flask(__name__)  # crea el objeto de aplicación
app.secret_key = "a84d51yOL2"

# Conexión con el sistema gestor MySQL. PyMySQL
db = sqlalchemy.create_engine(
    sqlalchemy.engine.URL.create(
        drivername='mysql+pymysql',
        username="root",
        password="Loncres2020",
        database="hospital",
        host="db"
    )
)

# Definimos clases DTO: Usuarios, Pacientes y Ecgs -> asociadas a las entidades usuarios, pacientes y ecgs
Base = declarative_base()


#  Usuarios: atributos username y password. Para definir usuarios con acceso a la aplicación
class Usuarios(Base):
    __tablename__ = 'usuarios'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(length=20))
    password = sqlalchemy.Column(sqlalchemy.String(length=20))

    def __repr__(self):
        return "{{username='{0}', password='{1}'}}'".format(
            self.username, self.password)


# Pacientes: atributos id, nombre, apellidos, dni, fecnac , sexo y observaciones. Contiene la información de los
# pacientes
class Pacientes(Base):
    __tablename__ = 'pacientes'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    dni = sqlalchemy.Column(sqlalchemy.String(length=10))
    nombre = sqlalchemy.Column(sqlalchemy.String(length=50))
    apellidos = sqlalchemy.Column(sqlalchemy.String(length=50))
    fecnac = sqlalchemy.Column(sqlalchemy.String(length=10))
    sexo = sqlalchemy.Column(sqlalchemy.Integer)
    iam = sqlalchemy.Column(sqlalchemy.Integer)
    cardiaco = sqlalchemy.Column(sqlalchemy.Integer)
    observaciones = sqlalchemy.Column(sqlalchemy.Text)


# Ecgs: atributos id, dni, alarma, qtc y time. qtc contiene el valor del parametro Qtc calculado en una ECG.
# alarma almacena el nivel de alarma que devuelve el sistema inteligente. ime es
# la fecha en que se ha procesado la fotografía y calculado el nivel de alarma.
class Ecgs(Base):
    __tablename__ = 'ecgs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    dni = sqlalchemy.Column(sqlalchemy.String(length=50))
    alarma = sqlalchemy.Column(sqlalchemy.Float)
    alarma_man = sqlalchemy.Column(sqlalchemy.Float)
    qtc = sqlalchemy.Column(sqlalchemy.Float)
    qtc_man = sqlalchemy.Column(sqlalchemy.Float)
    qtc_type = sqlalchemy.Column(sqlalchemy.Integer)
    incremento = sqlalchemy.Column(sqlalchemy.Float)
    incremento_man = sqlalchemy.Column(sqlalchemy.Float)
    contexto = sqlalchemy.Column(sqlalchemy.Float)
    fecnac = sqlalchemy.Column(sqlalchemy.String(length=10))
    sexo = sqlalchemy.Column(sqlalchemy.Integer)
    diuretico = sqlalchemy.Column(sqlalchemy.Integer)
    suero = sqlalchemy.Column(sqlalchemy.Integer)
    qtc_450 = sqlalchemy.Column(sqlalchemy.Integer)
    sepsis = sqlalchemy.Column(sqlalchemy.Integer)
    medQT = sqlalchemy.Column(sqlalchemy.Integer)
    medsQT = sqlalchemy.Column(sqlalchemy.Integer)
    fullimage = sqlalchemy.Column(sqlalchemy.BLOB)
    fullimageclipping = sqlalchemy.Column(sqlalchemy.String(length=50))
    image = sqlalchemy.Column(sqlalchemy.BLOB)
    time = sqlalchemy.Column(sqlalchemy.String(length=20))
    m1 = sqlalchemy.Column(sqlalchemy.Integer)
    m2 = sqlalchemy.Column(sqlalchemy.Integer)
    m3 = sqlalchemy.Column(sqlalchemy.Integer)
    m4 = sqlalchemy.Column(sqlalchemy.Integer)
    m5 = sqlalchemy.Column(sqlalchemy.Integer)
    observaciones = sqlalchemy.Column(sqlalchemy.Text)


error = ''
first = True


@app.route('/lang/<name>', methods=['GET'])
def langes(name):
    supported_languages = ['es', 'en', 'it', 'sv', 'el', 'de', 'ja', 'fa', 'ja', 'ku', 'ru', 'da', 'pl', 'zh']
    lang = request.accept_languages.best_match(supported_languages)
    template = 'lang.' + lang
    return render_template(template)


# El recurso por defecto tiene asociada la vista 'login.html', para procedear a la indetificación
# Si se ha realizado con éxito, se ha creado el objeto de sesión login_in y presenta la vista 'menu.html'
@app.route('/')
def home():
    global error, first
    if not session.get('logged_in'):
        if first:
            error = ''
            first = False
        return render_template('login.html', error=error)
    else:
        return render_template('menu.html')


@app.route('/creditos')
def creditos():
    return render_template('creditos.html')


# Devuelve la imagen favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Tratamiento de los datos usuario y contraseña que devuelve el formulario de la vista login.html.
@app.route('/login', methods=['POST'])
def do_admin_login():
    POST_USERNAME = str(request.form['username'])  # Extrae el nombre de usuario
    POST_PASSWORD = str(request.form['password'])  # Extrae la contraseña
    Session = sessionmaker(bind=db)
    s = Session()
    # Consulta si existe en la tabla usuarios un registro cuyo valor del atributo 'username' coincida con el nombre
    # de usuario introducido y el valor del atributo 'password' con el valor de contraseña (del formulario de
    # login.html)
    query = s.query(Usuarios).filter(Usuarios.username.in_([POST_USERNAME]), Usuarios.password.in_([POST_PASSWORD]))
    result = query.first()
    s.close()
    if result:
        session['logged_in'] = True  # si existe, crea el objeto de sesion logged_in con valor True
    else:
        global error
        error = 'Usuarios o contraseña inválidos. ¡Por favor, inténtalo otra vez!'
    return home()  # devuelve la vista login.html o menu.html, en función del éxito de las credenciales


# Finaliza la sesion -> logged_in a False
@app.route("/logout")
def logout():
    global first
    first = True
    session['logged_in'] = False
    return home()


# Comrpueba si quiere finalizar la sesión o cancelar la finalización
@app.route("/logout_check", methods=["GET"])
def salir():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('logout_check.html')


# El recurso /ecg tiene asociada la vista ecg.html. En ella se muestra un formulario para introducir el idenficador y
# subir la imagen de la ECG
@app.route("/ecg", methods=["GET"])
def ecg():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('ecg.html')


# El recurso /ecgedit tiene asociada la vista ecgedit.html. En ella se muestra un formulario para editar datos de la ECG
@app.route("/ecgedit", methods=["GET"])
def ecgedit():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        data = {"id": request.args.get('id'),
                "qtc_type": request.args.get('qtc_type')
                }
        return render_template('ecgedit.html', data=data)


# El recurso /ecgdraw  devuelve la imagen ECG image/jpg
@app.route("/ecgdraw", methods=["GET"])
def ecgdraw():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        id = request.args.get('id')
        Session = sessionmaker(bind=db)
        s = Session()
        # Recupera la imagen en la tabla ECG para ese id
        query = s.query(Ecgs.image).filter(Ecgs.id.in_([id]))
        data = query.all()
        image = getattr(data[0], 'image')
        s.close()
        if image == '':
            return send_file('static/files/blank.jpg')
        else:
            return Response(image, mimetype='image/jpg')


# El recurso /ecgdrawfull  devuelve fullimagen ECG image/jpg
@app.route("/ecgdrawfull", methods=["GET"])
def ecgdrawfull():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        id = request.args.get('id')
        Session = sessionmaker(bind=db)
        s = Session()
        # Recupera la imagen en la tabla ECG para ese id
        query = s.query(Ecgs.fullimage).filter(Ecgs.id.in_([id]))
        data = query.all()
        image = getattr(data[0], 'fullimage')
        s.close()
        if image == '':
            return send_file('static/files/blank.jpg')
        else:
            return Response(image, mimetype='image/jpg')


# El recurso /setecgObservaciones inserta observacion en ECG
@app.route("/setecgobservaciones", methods=["POST"])
def setObservaciones():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        id = request.form['id']
        observaciones = request.form['observaciones']
        Session = sessionmaker(bind=db)
        s = Session()
        # Actualiza las observaciones en la tabla ECG para ese id
        updateEcg = {'observaciones': observaciones}
        s.query(Ecgs).filter(Ecgs.id == id).update(updateEcg)
        s.commit()
        s.close()
        result = {"status": "200"}
        return jsonify(result)


# El recurso /ecgbase64tiene  devuelve la imagen ECG en formato base64
@app.route("/ecgbase64", methods=["GET"])
def ecgbase64():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        id = request.args.get('id')
        Session = sessionmaker(bind=db)
        s = Session()
        # Recupera la imagen en la tabla ECG para ese id
        query = s.query(Ecgs.fullimage).filter(Ecgs.id.in_([id]))
        data = query.all()
        image = getattr(data[0], 'fullimage')
        s.close()
        base64_bytes = base64.b64encode(image)
        base64_message = base64_bytes.decode('ascii')
        result = {"image": base64_message}
        return jsonify(result)


# El recurso /ecgupdate modifica los datos en la tabla ECG
@app.route("/ecgupdate", methods=["POST"])
def ecgupdate():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        x1 = float(request.form['x1'])
        y1 = float(request.form['y1'])
        x2 = float(request.form['x2'])
        y2 = float(request.form['y2'])
        id = int(request.form['id'])
        dni = request.form['dni']
        fecnac = request.form['fecnac']
        sexo = request.form['sexo']
        qtc_type = int(request.form['qtc_type'])
        content = str(request.form['content'])
        newImage = str(request.form['newImage'])
        newClipped = str(request.form['newClipped'])
        qtc_man = float(request.form['qtc_man'])
        contexto = float(request.form['contexto'])
        diuretico = request.form['diuretico']
        suero = request.form['suero']
        qtc_450 = request.form['qtc_450']
        sepsis = request.form['sepsis']
        medQT = request.form['medQT']
        medsQT = request.form['medsQT']
        m1 = request.form['m1']
        m2 = request.form['m2']
        m3 = request.form['m3']
        m4 = request.form['m4']
        m5 = request.form['m5']
        observaciones = request.form['observaciones']
        filename = 'temp.jpg'
        mode = 'update'

        r, id = uploadfunction(mode, id, x1, y1, x2, y2, filename, content, newImage, newClipped, dni, contexto, fecnac, sexo, diuretico, suero,
                           qtc_450, sepsis, medQT, medsQT, qtc_man, qtc_type, m1, m2, m3, m4, m5, observaciones)

        Session = sessionmaker(bind=db)
        s = Session()

        ri = r[-1]
        for i in r:
            if i['id'] == id:
                ri = i
                break

        selector = ri['qtc_type']
        time = ri['time']
        if (selector == 80) or (selector == 81):
            if selector == 80:
                basal = ri['qtc']
            else:
                basal = ri['qtc_man']

            print(basal)
            print(time)

            query = s.query(Ecgs.id, Ecgs.qtc, Ecgs.qtc_man, Ecgs.qtc_type).filter(Ecgs.dni.in_([dni]), Ecgs.time>time).order_by(Ecgs.time.asc())
            result = query.all()

            for r in result:
                incremento = 0
                incremento_man = 0
                id, qtc, qtc_man, qtc_selector = r
                if qtc_selector >= 80:
                    break
                if qtc_selector == 0:
                    incremento = max(0.0, qtc - basal)
                if qtc_selector == 1:
                    incremento_man = max(0.0, qtc_man - basal)
                if qtc_selector == 2:
                    incremento = max(0.0, qtc - basal)
                    incremento_man = max(0.0, qtc_man - basal)
                if qtc_selector < 80:
                    alarma = round(estimacion.alarma(qtc, float(contexto), incremento), 2)
                    alarma_man = round(estimacion.alarma(qtc_man, float(contexto), incremento_man), 2)
                    updates = {'incremento': incremento, 'incremento_man': incremento_man, 'alarma': alarma,
                               'alarma_man': alarma_man}
                    s.query(Ecgs).filter(Ecgs.id == id).update(updates)
        s.close()

        result = {"status": "1"}
        return jsonify(result)


# Se dan de alta o modifican pacientes
@app.route("/updatepaciente", methods=["POST"])
def updatecliente():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        # datos que provienen del formulario existente en administracion.html
        # nombre, apellidos, fechanacimiento, sexo, contexto y observaciones
        d = str(request.form['dni'])
        nombre = str(request.form['nombre'])
        apellidos = str(request.form['apellidos'])
        observaciones = str(request.form['observaciones'])
        fecnac = str(request.form['fecnac'])
        sexo = str(request.form['sexo'])
        iam = str(request.form['iam'])
        cardiaco = str(request.form['cardiaco'])

        Session = sessionmaker(bind=db)
        s = Session()
        # compruebo si existe en la tabla pacientes
        q = s.query(Pacientes).filter(Pacientes.dni == d)
        result = q.first()
        if result:  # si existe el paciente -> acutualizo
            updates = {'dni': d, 'nombre': nombre, 'apellidos': apellidos, 'fecnac': fecnac, 'sexo': sexo, 'iam': iam,
                       'cardiaco': cardiaco, 'observaciones': observaciones}
            s.query(Pacientes).filter(Pacientes.dni == d).update(updates)
            s.commit()
        else:  # si no existe -> creo el registro con un nuevo paciente
            newPaciente = Pacientes(dni=d, nombre=nombre, apellidos=apellidos, fecnac=fecnac, sexo=sexo, iam=iam,
                                    cardiaco=cardiaco, observaciones=observaciones)
            s.add(newPaciente)
            s.commit()
        result = {'status': '200 ok'}
        s.close()
        return jsonify(result)


"""Procesa los datos del formulario existente en la vista ecg.html. Se llaman a los métodos existente en: - grafica: 
grafica2ecg -> obtiene una señal a partir de la imagen ECG - procesadoECG: ecg2parametros -> obtiene los parámetros (
qtc) a partir de la señal - estimacion: alarma -> calcula un nivel de alarma a partir del qtc, contexto y una 
diferencia entre el qtc actual y el primer qtc calculado (a partir de la ECG inicial)

Obtiene el identificador de paciente y contenido de la imagen ECG (archivo). Este archivo se almacena en el sistema 
de archivos local, en la ubicacion: /static/files/<identificador_de_paciente>/<nombre_de_imagenEcg_subida>

Sucesivamente se van invocando métodos de grafica.py, procesadoECG.py y estamacion.py. Algunos parámetros como qtc y 
el nivel de alarma se guardan en la tabla ecgs, junto al identificador de paciente, fecha de cálculo y ubicación de 
la imagen para una posterior visualización 
"""


@app.route("/upload", methods=["POST"])
def upload():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        try:
            import time
            x1 = float(request.form['x1'])
            y1 = float(request.form['y1'])
            x2 = float(request.form['x2'])
            y2 = float(request.form['y2'])
            filename = str(request.form['filename'])
            content = str(request.form['content'])
            d = str(request.form['dni'])
            contexto = float(request.form['contexto'])
            fecnac = request.form['fecnac']
            sexo = request.form['sexo']
            diuretico = request.form['diuretico']
            suero = request.form['suero']
            qtc_450 = request.form['qtc_450']
            sepsis = request.form['sepsis']
            medQT = request.form['medQT']
            medsQT = request.form['medsQT']
            observaciones = ""

            qtc_man = float(request.form['qtc_man'])
            qtc_type = int(request.form['qtc_type'])

            mode = 'insert'

            result, id = uploadfunction(mode, -1, x1, y1, x2, y2, filename, content, 0, 0, d, contexto, fecnac, sexo, diuretico,
                                    suero, qtc_450, sepsis, medQT, medsQT, qtc_man, qtc_type, 0, 0, 0, 0, 0, observaciones)
            return jsonify(result)
        except Exception as e:
            print(e)
            return jsonify({"status": "501"})


def imagechanged(id, newImage, newClipped):
    Session = sessionmaker(bind=db)
    s = Session()
    query = s.query(Ecgs).filter(Ecgs.id == id)
    data = query.all()
    qtc = getattr(data[0], 'qtc')
    s.close()
    res = True
    if newImage == '0' and newClipped == '0':
        res = False
    return res, qtc


def uploadfunction(mode, id, x1, y1, x2, y2, filename, content, newImage, newClipped, d, contexto, fecnac, sexo, diuretico, suero, qtc_450, sepsis,
                   medQT, medsQT, qtc_man, qtc_type, m1, m2, m3, m4, m5, observaciones):
    if filename != "void" and content != '':
        has = '{:x}'.format(int(datetime.datetime.today().timestamp()))
        path = "./static/files/{0}/{1}_{2}".format(d, has, filename)
        path_clip = "./static/files/{0}/c-{1}_{2}".format(d, has, filename)
        direc = './static/files/{0}'.format(d)
        if not os.path.isdir(direc):
            os.makedirs(direc)
        im = Image.open(BytesIO(base64.b64decode(content)))
        # Guarda imagen completa
        # im.save(path)

        # Obtiene el contenido de la imagen completa
        output_buffer = BytesIO()
        im.save(output_buffer, format='JPEG')
        byte_data = output_buffer.getvalue()
        fullimage = byte_data

        fullimageclipping = "{:.{}f}, {:.{}f}, {:.{}f}, {:.{}f}".format(x1, 2, y1, 2, x2, 2, y2, 2)

        if id != -1:
            imgchange, qtcstored = imagechanged(id, newImage, newClipped)
        else:
            imgchange = True

        if imgchange:
            # The crop method from the Image module takes four coordinates as input.
            # The right can also be represented as (left+width)
            # and lower can be represented as (upper+height).
            (left, upper, right, lower) = (x1, y1, x2, y2)
            im_crop = im.crop((left, upper, right, lower))
            im_crop.save(path_clip)

            # Obtiene el contenido de la imagen
            output_buffer = BytesIO()
            im_crop.save(output_buffer, format='JPEG')
            byte_data = output_buffer.getvalue()
            # image = base64.b64encode(byte_data)
            image = byte_data

            #
            # <img src="data:image/jpg;base64,<contenido_image>">
            #
            if Docker:
                qtc, ppm, qtc_times, r_times = procesadoECG.ecg2parametros(path_clip)
            else:
                qtc, ppm, qtc_times, r_times = procesadoECG2.ecg2parametros(path_clip)

            qtc = round(1000 * qtc)

            # Borra los archivos de imagenes
            # os.remove(path)
            os.remove(path_clip)
        else:
            qtc = qtcstored

    else:
        qtc = 0
        image = 0
        fullimage = 0
        fullimageclipping = '{0, 0, 0, 0}'
        imgchange = True

    status_imagen = 200
    if qtc_type == 80 and qtc <= 0:
        qtc_type = 81
        status_imagen = 501
    if qtc_type == 2 and qtc <= 0:
        qtc_type = 1
        status_imagen = 501

    if qtc <= 0 and qtc_man <= 0:
        return jsonify({"status": "501"})
    else:
        # calcula qtc o qtc_man basal
        incremento = 0
        incremento_man = 0
        alarma = 0
        alarma_man = 0

        if qtc_type == 80:
            alarma = round(estimacion.alarma(qtc, contexto, incremento), 2)
            if qtc_man > 0:
                alarma_man = round(estimacion.alarma(qtc_man, contexto, incremento_man), 2)

        if qtc_type == 81:
            alarma_man = round(estimacion.alarma(qtc_man, contexto, incremento_man), 2)
            if qtc > 0:
                alarma = round(estimacion.alarma(qtc, contexto, incremento), 2)

        if qtc_type < 80:
            Session = sessionmaker(bind=db)
            s = Session()
            if id == -1:
                query = s.query(Ecgs.qtc, Ecgs.qtc_man, Ecgs.qtc_type).filter(Ecgs.dni.in_([d]), Ecgs.qtc_type >= 80).order_by(Ecgs.time.desc())
            else:
                query = s.query(Ecgs.qtc, Ecgs.qtc_man, Ecgs.qtc_type).filter(Ecgs.dni.in_([d]), Ecgs.qtc_type >= 80, Ecgs.id < id).order_by(Ecgs.time.desc())
            result = query.first()
            if result is not None:
                qtc_basal, qtc_man_basal, qtc_selector = result
            else:
                qtc_basal, qtc_man_basal, qtc_selector = (0, 0, 0)

            if qtc_type == 0:
                if qtc_selector == 80:
                    incremento = max(0.0, qtc - qtc_basal)
                if qtc_selector == 81:
                    incremento = max(0.0, qtc - qtc_man_basal)
                alarma = round(estimacion.alarma(qtc, contexto, incremento), 2)

            if qtc_type == 1:
                if qtc_selector == 80:
                    incremento_man = max(0.0, qtc_man - qtc_basal)
                if qtc_selector == 81:
                    incremento_man = max(0.0, qtc_man - qtc_man_basal)
                alarma_man = round(estimacion.alarma(qtc_man, contexto, incremento_man), 2)

            if qtc_type == 2:
                if qtc_selector == 80:
                    incremento = max(0.0, qtc - qtc_basal)
                    incremento_man = max(0.0, qtc_man - qtc_basal)
                if qtc_selector == 81:
                    incremento = max(0.0, qtc - qtc_man_basal)
                    incremento_man = max(0.0, qtc_man - qtc_man_basal)
                alarma = round(estimacion.alarma(qtc, contexto, incremento), 2)
                alarma_man = round(estimacion.alarma(qtc_man, contexto, incremento_man), 2)

        now = datetime.datetime.today()
        time = now.strftime("%Y-%m-%d %H:%M:%S")
        Session = sessionmaker(bind=db)
        s = Session()

        if mode == 'insert':
            newEcg = Ecgs(dni=d, qtc=str(qtc), qtc_man=str(qtc_man), qtc_type=str(qtc_type),
                          incremento=str(incremento), incremento_man=str(incremento_man),
                          diuretico=diuretico, suero=suero, qtc_450=qtc_450, sepsis=sepsis, medQT=medQT, medsQT=medsQT,
                          contexto=str(contexto), fecnac=fecnac, sexo=sexo,
                          alarma=str(alarma), alarma_man=str(alarma_man),
                          time=time, fullimage=fullimage, fullimageclipping=fullimageclipping,
                          image=image, m1=m1, m2=m2, m3=m3, m4=m4, m5=m5, observaciones=observaciones)
            s.add(newEcg)
            s.commit()

        if mode == 'update':
            if imgchange:
                updateEcg = {'qtc': str(qtc), 'qtc_man': str(qtc_man), 'qtc_type': str(qtc_type),
                             'incremento': str(incremento), 'incremento_man': str(incremento_man),
                             'diuretico': diuretico, 'suero': suero, 'qtc_450': qtc_450, 'sepsis': sepsis, 'medQT': medQT, 'medsQT': medsQT,
                             'contexto': str(contexto), 'fecnac': fecnac, 'sexo': sexo,
                             'alarma': str(alarma), 'alarma_man': str(alarma_man), 'fullimage': fullimage,
                             'fullimageclipping': fullimageclipping,
                             'image': image, 'm1': m1, 'm2': m2, 'm3': m3, 'm4': m4, 'm5': m5,
                             'observaciones': observaciones}
            else:
                updateEcg = {'qtc_man': str(qtc_man), 'qtc_type': str(qtc_type),
                             'incremento': str(incremento), 'incremento_man': str(incremento_man),
                             'diuretico': diuretico, 'suero': suero, 'qtc_450': qtc_450, 'sepsis': sepsis, 'medQT': medQT, 'medsQT': medsQT,
                             'contexto': str(contexto), 'fecnac': fecnac, 'sexo': sexo,
                             'alarma': str(alarma), 'alarma_man': str(alarma_man),
                             'fullimageclipping': fullimageclipping,
                             'm1': m1, 'm2': m2, 'm3': m3, 'm4': m4, 'm5': m5,
                             'observaciones': observaciones}

            s.query(Ecgs).filter(Ecgs.id == id).update(updateEcg)
            s.commit()

        query = s.query(Ecgs).filter(Ecgs.dni.in_([d])).order_by(Ecgs.time.desc())
        data = query.all()
        cols = ['id', 'dni', 'alarma', 'alarma_man', 'qtc', 'qtc_man', 'qtc_type', 'incremento',
                'incremento_man',
                'contexto', 'fecnac', 'sexo', 'diuretico', 'suero', 'qtc_450', 'sepsis', 'medQT', 'medsQT',
                'time', 'm1', 'm2', 'm3', 'm4', 'm5']
        result = [{col: getattr(d, col) for col in cols} for d in data]
        result[0]['status_imagen'] = status_imagen
        s.close()
        return result, id


# El recurso /historial tiene asociada la vista historial.html, donde se muestra el contenido de la tabla ecsg
@app.route("/historial", methods=["GET"])
def historial():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        data = {'dni': request.args.get('dni')}
        return render_template('historial.html', data=data)


# El recurso /administracion tiene asociada la vista administracion.html, donde se muestra un formulario para dar de
# modificar/dar de alta nuevos pacientes
@app.route("/administracion", methods=["GET"])
def administracion():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('administracion.html')


# devuelve todos los identificadores de paciente existentes en la tabla o los datos de un registro en particular si
# se indica un identificador de paciente
@app.route("/dni")
def dni():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        GET_USERNAME = request.args.get('dni')
        Session = sessionmaker(bind=db)
        s = Session()
        if GET_USERNAME is None:
            query = s.query(Pacientes.dni)  # devuelve los identificadores de pacientes
            cols = ['dni']
        else:
            query = s.query(Pacientes).filter(Pacientes.dni.in_([GET_USERNAME]))
            # devuelve el registro asociado a un identificador de paciente
            cols = ['dni', 'nombre', 'apellidos', 'sexo', 'fecnac', 'iam', 'cardiaco']
        data = query.all()
        result = [{col: getattr(d, col) for col in cols} for d in data]
        s.close()
        return jsonify(result)


# Devuelve un registro de la tabla pacientes, dado un identificador de paciente.
@app.route("/registro")
def registro():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        GET_USERNAME = request.args.get('dni')
        Session = sessionmaker(bind=db)
        s = Session()
        if GET_USERNAME is None:
            query = s.query(Pacientes)
            cols = ['dni', 'nombre', 'apellidos', 'fecnac', 'sexo', 'iam', 'cardiaco']
        else:
            query = s.query(Pacientes).filter(Pacientes.dni.in_([GET_USERNAME]))
            cols = ['dni', 'nombre', 'apellidos', 'fecnac', 'sexo', 'iam', 'cardiaco', 'observaciones']
        data = query.all()

        result = [{col: getattr(d, col) for col in cols} for d in data]
        s.close()
        return jsonify(result)


# Devuelve el contenido de la tabla Ecgs -> el valor de todos los atributos
@app.route("/detalle")
def detalle():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        GET_DNI = request.args.get('dni')
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        Session = sessionmaker(bind=db)
        s = Session()
        query = s.query(Ecgs).filter(Ecgs.dni.in_([GET_DNI])).order_by(Ecgs.time.desc())
        data = query.all()
        cols = ['id', 'dni', 'alarma', 'alarma_man', 'qtc', 'qtc_man', 'qtc_type', 'incremento', 'incremento_man',
                'contexto', 'diuretico', 'suero', 'qtc_450', 'sepsis', 'medQT', 'medsQT',
                'time', 'm1', 'm2', 'm3', 'm4', 'm5', 'observaciones']
        result = [{col: getattr(d, col) for col in cols} for d in data]
        s.close()
        return jsonify(result)


# Devuelve una fila de la tabla Ecgs -> en función de su id
@app.route("/ecgrow")
def ecgrow():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        GET_ID = request.args.get('id')
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        Session = sessionmaker(bind=db)
        s = Session()
        query = s.query(Ecgs).filter(Ecgs.id.in_([GET_ID])).order_by(Ecgs.time.desc())
        data = query.all()
        cols = ['id', 'dni', 'alarma', 'alarma_man', 'qtc', 'qtc_man', 'qtc_type', 'incremento', 'incremento_man',
                'contexto', 'fecnac', 'sexo', 'diuretico', 'suero', 'qtc_450', 'sepsis', 'medQT', 'medsQT',
                'time', 'fullimageclipping', 'm1', 'm2', 'm3', 'm4', 'm5', 'observaciones']
        result = [{col: getattr(d, col) for col in cols} for d in data]
        s.close()
        return jsonify(result)


@app.route("/medidas", methods=["POST"])
def medidas():
    m1 = request.form['m1']
    m2 = request.form['m2']
    m3 = request.form['m3']
    m4 = request.form['m4']
    m5 = request.form['m5']
    id = request.form['id']
    Session = sessionmaker(bind=db)
    s = Session()
    # compruebo si existe en la tabla pacientes
    # q = s.query(Ecgs).filter(Ecgs.id == id)
    # result = q.first()
    updates = {'m1': m1, 'm2': m2, 'm3': m3, 'm4': m4, 'm5': m5}
    s.query(Ecgs).filter(Ecgs.id == id).update(updates)
    s.commit()
    s.close()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
    # app.run(debug=True, ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=443)
