from flask import Flask, request, render_template, redirect, flash, session, jsonify, url_for
from models import Carrito, Usuario, db, Categoria, categorias_curso, Curso, Clase, Transacciones
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
        # Exclude purchased courses for students
        purchased_course_ids = [transaccion.id_curso for transaccion in Transacciones.query.filter_by(id_user=current_user.id, purchased=True).all()]
        cursos = Curso.query.filter(Curso.id.notin_(purchased_course_ids)).all()

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
    
@app.route("/courses_details/<int:id>")
@login_required
def courses_details(id):
    course_detail = Curso.query.get(id)
    print(f"c: {course_detail}")
    return render_template("courses_details.html", curso=course_detail)

    
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

#@app.route("/cart", methods=["POST", "GET"])
#def cart():
#    if request.method == "POST":
#        pass
#    else:
#        return render_template("cart.html")
 
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
    curso = Curso.query.get_or_404(id)
    #print(f"Lecciones: {lecciones}")
    return render_template("lecciones.html", curso=curso, lecciones=lecciones)

@app.route("/review", methods=["POST", "GET"])
def review():
    if request.method == "POST":
        pass
    else:
        return render_template("review.html")
    
#boton en cursos ELIMINAR (vista editar/configuracion de curso)
@app.route("/Eliminar_curso/<int:id>", methods=["POST", "GET"])
def delete_course(id):
    curso = Curso.query.get_or_404(id)
    
    if request.method == "POST":
        try:
            db.session.delete(curso)
            db.session.commit()
            flash("Curso eliminado exitosamente", "success")
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash("Hubo un error al eliminar el curso", "danger")
            print('erro', e)
            return redirect(url_for('index'))  # or render_template as needed
        
    
    # Handling GET request to show confirmation or details
    return render_template("index.html", curso=curso)

@app.route('/add_to_cart/<int:curso_id>', methods=['POST'])
@login_required
def add_to_cart(curso_id):
    curso = Curso.query.get(curso_id)
    if not curso:
        print("no encontrado")
        flash('Curso no encontrado', 'error')
        return redirect(url_for('courses'))

    # Verificar si el curso ya está en el carrito
    existing_item = Carrito.query.filter_by(id_curso=curso_id, id_user=current_user.id, estado=True).first()
    if existing_item:
        flash('Este curso ya está en tu carrito', 'info')
        return redirect(url_for('courses'))

    # Agregar curso al carrito
    carrito_item = Carrito(id_curso=curso_id, id_user=current_user.id)
    db.session.add(carrito_item)
    db.session.commit()
    flash('Curso agregado al carrito', 'success')
    return redirect(url_for('cart'))


@app.route('/cart')
@login_required
def cart():
    carrito_items = Carrito.query.filter_by(id_user=current_user.id, estado=True).all()
    return render_template('cart.html', carrito_items=carrito_items)


@app.route('/remove_from_cart/<int:carrito_id>', methods=['POST'])
@login_required
def remove_from_cart(carrito_id):
    carrito_item = Carrito.query.get(carrito_id)
    if carrito_item and carrito_item.id_user == current_user.id:
        carrito_item.estado = False
        db.session.commit()
        flash('Curso eliminado del carrito', 'success')
    else:
        flash('Error al eliminar el curso del carrito', 'error')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    card_number = request.form.get('card_number')

    # Verifica nuevamente la tarjeta con la API
    response = requests.post('http://127.0.0.1:5000/validate_card', json={'card_number': card_number})
    data = response.json()

    if not data['success'] or not data['BIN']['valid']:
        flash('La tarjeta no es válida. No se puede proceder con la compra.', 'danger')
        return redirect(url_for('cart'))

    # Proceder con la compra si la tarjeta es válida
    user_id = current_user.id
    carrito_items = Carrito.query.filter_by(id_user=user_id, estado=True).all()
    
    for item in carrito_items:
        item.estado = False  # Actualizar el estado a False para indicar que ha sido comprado
        db.session.add(item)

        # Crear una entrada en la tabla de transacciones
        nueva_transaccion = Transacciones(
            id_curso=item.id_curso,
            id_user=user_id,
            purchased=True
        )
        db.session.add(nueva_transaccion)
        
    db.session.commit()

    flash('Compra realizada con éxito.', 'success')
    return redirect(url_for('purchased_courses'))



@app.route('/purchased_courses')
@login_required
def purchased_courses():
    user_id = current_user.id
    purchased_items = Carrito.query.filter_by(id_user=user_id, estado=False).all()  # estado=False indica que el curso ha sido comprado
    return render_template('purchased_courses.html', purchased_items=purchased_items)


    
if __name__ == '__main__':
    app.run(debug=True) 