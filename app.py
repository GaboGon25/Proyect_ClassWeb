from flask import Flask, request, render_template, redirect, flash, session, jsonify
from models import Usuario, db, Categoria, categorias_curso, Curso
# con eso importamos la password hasheada
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from flask_session import Session
# clase de Integrity Error
from sqlalchemy.exc import IntegrityError
# importaciones para login
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

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
def index():
    return render_template("index.html")

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
    
@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        titulo = request.form.get("titulo")
        contenido = request.form.get("contenido")
        categorias = request.form.getlist("categoria")

        if not titulo or not contenido or not categorias:
            flash("Campos vacios", "danger")
            return redirect("/create")
        
        try:
            nuevo_curso = Curso(title=titulo, description=contenido)
            
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
            flash("Hubo un error", "danger")
            return redirect("/create")

        #print(f"T: {titulo} Cont: {contenido} Cat: {categorias}")
        
        flash("Curso creado", "success")
        return redirect("/")
    else:
        return render_template("create.html")
    
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
    if request.method == "POST":
        pass
    else:
        return render_template("categories.html")
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado la sesion", 'success')
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)

