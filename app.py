from flask import Flask, request, render_template, redirect, flash, session, jsonify, url_for
from models import Usuario, db, Categoria, categorias_curso, Curso, Clase
# con eso importamos la password hasheada
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from flask_session import Session
# clase de Integrity Error
from sqlalchemy.exc import IntegrityError
# importaciones para login
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import requests

app= Flask(__name__)
app.config.from_object(Config)

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

db.init_app(app)

#configuraciones para logearse
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

#INDEX
@app.route("/")
@login_required
def index():
    if current_user.rol == 'tutor':
        cursos = Curso.query.filter_by(id_profesor=current_user.id).all()
    else:
        cursos = Curso.query.all()
    cursos_data = [curso.serialize() for curso in cursos]
    return render_template("index.html", cursos=cursos_data)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")


        print(f"{email, password}")

        if not email or not password:
            flash("Campos vacios", "danger")
            return redirect("/login")
        
        usuario = Usuario.query.filter_by(email_user=email).first()
        
        if usuario is None:
            flash("Usuario no encontrado", 'danger')
            return redirect("/login")

        print(f"U: {usuario.password_hash}")

        if not check_password_hash(usuario.password_hash, password):
            flash("Contraseñas no coinciden", 'warning')
            return redirect("/login")
        
        # si todos los campos y validaciones estan correctos
        login_user(usuario)
        flash("Inicio de sesion exitoso", 'success')
        return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/search")
def search():
    query = request.args.get("q")
    cursos_lista = Curso.query.filter(Curso.title.ilike(f'%{query}%')).all()
    print(cursos_lista)  # Verifica en la consola de Flask qué cursos se están devolviendo
    return render_template("courses.html", cursos=cursos_lista)

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol")

        print(f"{username, password}")
        # si los campos estan vacios
        if not username or not password:
            # es danger, porque es para errores
            flash("Campos vacios", "danger")
            return redirect("/register")
        
        # creamos un nuevo usuario
        # crear una password segura
        password_hash = generate_password_hash(password)
            
        try: 
            # si el usuario es nuevo
            new_user = Usuario(username=username, password_hash=password_hash, email_user=email, rol=rol)

            # guardamos a la base de datos con db
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("El usuario ya existe", 'danger')
            return redirect("/register")

        flash("Usuario registrado!", 'success ')
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/categories", methods=['POST', 'GET'])
def categoria():
    if request.method == "POST":
        nombre = request.form.get("nombre_categoria")
        descripcion = request.form.get("descripcion")
        
        if not nombre or not descripcion:
            flash("Error, campos vacios")
            return redirect("/categories")
        
        try:
            nueva_categoria = Categoria(name=nombre, description = descripcion)
            db.session.add(nueva_categoria)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("La categoria existe", "danger")
            return redirect("/categories")
        
        flash("Categoria creada", "success")
        return redirect("/categories")
    else:
        return render_template("categories.html")
    
@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        titulo = request.form.get("titulo")
        contenido = request.form.get("contenido")
        categorias = request.form.getlist("categoria")
        precio = request.form.get("price")
        
        try:
        
            if not titulo or not contenido or not categorias or not precio:
                flash("Campos vacios", "danger")
                return redirect("/create")
         
            float(precio)
            nuevo_curso = Curso(title=titulo, description=contenido, price=precio, id_profesor=current_user.id)
            
            for cat in categorias:
                print(f"dato: {cat}")
                categoria_id = Categoria.query.get(int(cat))
                nuevo_curso.categorias.append(categoria_id)
                print(f"Registro : {nuevo_curso.categorias}")
            
            db.session.add(nuevo_curso)
            db.session.commit() # confirmar el registro
        except Exception as e:
            print(f"El error fue: {e}")
            db.session.rollback()
            flash("Revise si ingreso mal un dato", "danger")
            return redirect("/create")

        #print(f"T: {titulo} Cont: {contenido} Cat: {categorias}")
        
        flash("Curso creado", "success")
        return redirect("/")
    else:
        categorias_list = Categoria.query.all()
        print(f"{categorias_list}")
        return render_template("create.html", categorias=categorias_list)
    
@app.route("/courses", methods=["POST", "GET"])
def courses():
    if request.method == "POST":
        pass
    else:
        return render_template("courses.html")
    
@app.route("/courses_details", methods=["POST", "GET"])
def courses_details():
    if request.method == "POST":
        pass
    else:
        return render_template("courses_details.html")
    
@app.route("/categories", methods=["POST", "GET"])
def categories():    
    return render_template("categories.html")
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado la sesion", 'success')
    return redirect("/")

@app.route("/validate_card", methods=['POST', 'GET'])
def validate_card():
    if request.method == 'POST':
        card_number = request.json.get("card_number")
        print(f"La tarjeta fue: {card_number}")
        bin_number = card_number[:6] 
        
        #print(f"BIN number: {bin_number}")
        
        url = "https://bin-ip-checker.p.rapidapi.com/"
        payload = {"bin": bin_number}
        headers = {
            "x-rapidapi-key": "05aea0045cmsh1ce0e88bf098ccdp1d50bajsnf296a4bbda73",
            "x-rapidapi-host": "bin-ip-checker.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        params = {"bin": bin_number}
        
        response = requests.post(url, json=payload, headers=headers, params=params)
        result = response.json()
        
        print(f"INFO: {result}")
        return jsonify(result)
    return render_template('validate_card.html')

@app.route("/cart", methods=["POST", "GET"])
def cart():
    if request.method == "POST":
        pass
    else:
        return render_template("cart.html")
 
@app.route("/configuration", methods=["POST", "GET"])
def configuration():
    return render_template("configuration.html")  

# crear lecciones
@app.route("/<int:id>/crear", methods=['POST', 'GET'])
def crear_lecciones(id):
    if request.method == "POST":
        # Agregar clases: titulo, descripcion, duracion, curso_id
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        horas = float(request.form.get("duracion"))
        curso_id = id

        if not titulo or not descripcion or not horas:
            flash("Campos vacios", "danger")
            print("Error")
            return redirect(url_for("crear_lecciones", id=curso_id))
        
        # crear una nueva leccion
        try:
            nueva_leccion = Clase(
                titulo = titulo,
                descripcion = descripcion,
                horas = horas,
                curso_id = curso_id
            )

            # agregalo
            db.session.add(nueva_leccion)
            db.session.commit()

            flash("Leccion agregada", "success")
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            print(f"El error fue: {e}")
            flash("Hubo un error", "danger")
            return redirect("/")
    else:
        curso = Curso.query.get(id)
        print(f"El curso es: {curso}")
        return render_template("crear_lecciones.html", curso=curso)

@app.route("/<int:id>/lecciones", methods=['GET'])
def lecciones_curso(id):
    lecciones = Clase.query.filter_by(curso_id = id).all()
    
    print(f"Lecciones: {lecciones}")
    return render_template("lecciones.html", lecciones=lecciones)
    
if __name__ == '__main__':
    app.run(debug=True)