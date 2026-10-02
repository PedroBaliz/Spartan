import os
import sqlite3

from functools import wraps
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash


# =========================================
# CONFIGURAÇÃO
# =========================================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

csrf = CSRFProtect(app)

DATABASE = "spartan.db"


# =========================================
# BANCO DE DADOS
# =========================================

def get_db_connection():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


# =========================================
# HELPERS
# =========================================

def login_required(route):
    @wraps(route)
    def wrapped_route(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        return route(*args, **kwargs)

    return wrapped_route


def get_user_workout(db, workout_id):
    workout = db.execute(
        """
        SELECT id, user_id, name
        FROM workouts
        WHERE id = ? AND user_id = ?
        """,
        (workout_id, session["user_id"])
    ).fetchone()

    if workout is None:
        abort(404)

    return workout


def get_workout_exercise(db, workout_id, workout_exercise_id):
    exercise = db.execute(
        """
        SELECT id, workout_id, exercise_id, sets, reps, position
        FROM workout_exercises
        WHERE id = ? AND workout_id = ?
        """,
        (workout_exercise_id, workout_id)
    ).fetchone()

    if exercise is None:
        abort(404)

    return exercise


def validate_volume(sets_value, reps_value):
    try:
        sets = int(sets_value)
        reps = int(reps_value)
    except (ValueError, TypeError):
        return None, None, "Séries e repetições devem ser números."

    if not 1 <= sets <= 10:
        return None, None, "O número de séries deve estar entre 1 e 10."

    if not 1 <= reps <= 30:
        return None, None, "O número de repetições deve estar entre 1 e 30."

    return sets, reps, None


# =========================================
# HOME
# =========================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================
# TREINOS
# =========================================

@app.route("/workouts")
@login_required
def workouts():
    db = get_db_connection()

    workouts = db.execute(
        """
        SELECT id, name
        FROM workouts
        WHERE user_id = ?
        ORDER BY name
        """,
        (session["user_id"],)
    ).fetchall()

    db.close()

    return render_template("workouts.html", workouts=workouts)


@app.route("/workouts/new", methods=["GET", "POST"])
@login_required
def new_workout():
    if request.method == "POST":
        name = request.form["name"].strip()

        if not name:
            flash("Digite um nome para o treino.", "error")
            return redirect(url_for("new_workout"))

        if len(name) > 50:
            flash("O nome do treino deve ter no máximo 50 caracteres.", "error")
            return redirect(url_for("new_workout"))

        db = get_db_connection()

        db.execute(
            """
            INSERT INTO workouts (user_id, name)
            VALUES (?, ?)
            """,
            (session["user_id"], name)
        )

        db.commit()
        db.close()

        flash("Treino criado com sucesso.", "success")
        return redirect(url_for("workouts"))

    return render_template("workout_form.html")


@app.route("/workouts/<int:workout_id>")
@login_required
def workout(workout_id):
    db = get_db_connection()

    workout = get_user_workout(db, workout_id)

    exercises = db.execute(
        """
        SELECT
            workout_exercises.id,
            workout_exercises.sets,
            workout_exercises.reps,
            workout_exercises.position,
            exercises.name,
            exercises.muscle_group
        FROM workout_exercises
        JOIN exercises ON workout_exercises.exercise_id = exercises.id
        WHERE workout_exercises.workout_id = ?
        ORDER BY workout_exercises.position ASC, workout_exercises.id ASC
        """,
        (workout_id,)
    ).fetchall()

    db.close()

    return render_template("workout.html", workout=workout, exercises=exercises)


# =========================================
# ADICIONAR EXERCÍCIO
# =========================================

@app.route("/workouts/<int:workout_id>/add", methods=["GET", "POST"])
@login_required
def add_exercise(workout_id):
    db = get_db_connection()

    get_user_workout(db, workout_id)

    if request.method == "POST":
        exercise_id = request.form["exercise_id"]

        exercise = db.execute(
            """
            SELECT id
            FROM exercises
            WHERE id = ?
            """,
            (exercise_id,)
        ).fetchone()

        if exercise is None:
            db.close()
            flash("Exercício inválido.", "error")
            return redirect(url_for("add_exercise", workout_id=workout_id))

        sets, reps, error = validate_volume(request.form.get("sets"), request.form.get("reps"))

        if error:
            db.close()
            flash(error, "error")
            return redirect(url_for("add_exercise", workout_id=workout_id))

        last_position = db.execute(
            """
            SELECT COALESCE(MAX(position), 0) AS max_position
            FROM workout_exercises
            WHERE workout_id = ?
            """,
            (workout_id,)
        ).fetchone()["max_position"]

        db.execute(
            """
            INSERT INTO workout_exercises (workout_id, exercise_id, sets, reps, position)
            VALUES (?, ?, ?, ?, ?)
            """,
            (workout_id, exercise_id, sets, reps, last_position + 1)
        )

        db.commit()
        db.close()

        flash("Exercício adicionado com sucesso.", "success")
        return redirect(url_for("workout", workout_id=workout_id))

    exercises = db.execute(
        """
        SELECT id, name, muscle_group
        FROM exercises
        ORDER BY muscle_group, name
        """
    ).fetchall()

    db.close()

    return render_template("exercise_form.html", exercises=exercises, workout_id=workout_id)


# =========================================
# REMOVER EXERCÍCIO
# =========================================

@app.route("/workouts/<int:workout_id>/exercise/<int:workout_exercise_id>/delete", methods=["POST"])
@login_required
def delete_exercise(workout_id, workout_exercise_id):
    db = get_db_connection()

    get_user_workout(db, workout_id)
    get_workout_exercise(db, workout_id, workout_exercise_id)

    db.execute(
        """
        DELETE FROM workout_exercises
        WHERE id = ? AND workout_id = ?
        """,
        (workout_exercise_id, workout_id)
    )

    db.commit()
    db.close()

    flash("Exercício removido com sucesso.", "success")
    return redirect(url_for("workout", workout_id=workout_id))


# =========================================
# EDITAR EXERCÍCIO
# =========================================

@app.route("/workouts/<int:workout_id>/exercise/<int:workout_exercise_id>/edit", methods=["GET", "POST"])
@login_required
def edit_exercise(workout_id, workout_exercise_id):
    db = get_db_connection()

    get_user_workout(db, workout_id)

    exercise = db.execute(
        """
        SELECT
            workout_exercises.id,
            workout_exercises.sets,
            workout_exercises.reps,
            exercises.name
        FROM workout_exercises
        JOIN exercises ON workout_exercises.exercise_id = exercises.id
        WHERE workout_exercises.id = ? AND workout_exercises.workout_id = ?
        """,
        (workout_exercise_id, workout_id)
    ).fetchone()

    if exercise is None:
        db.close()
        abort(404)

    if request.method == "POST":
        sets, reps, error = validate_volume(request.form.get("sets"), request.form.get("reps"))

        if error:
            db.close()
            flash(error, "error")
            return redirect(url_for("edit_exercise", workout_id=workout_id, workout_exercise_id=workout_exercise_id))

        db.execute(
            """
            UPDATE workout_exercises
            SET sets = ?, reps = ?
            WHERE id = ? AND workout_id = ?
            """,
            (sets, reps, workout_exercise_id, workout_id)
        )

        db.commit()
        db.close()

        flash("Exercício atualizado com sucesso.", "success")
        return redirect(url_for("workout", workout_id=workout_id))

    db.close()

    return render_template("edit_exercise.html", exercise=exercise, workout_id=workout_id)


# =========================================
# ORDENAR EXERCÍCIOS
# =========================================

@app.route("/workouts/<int:workout_id>/exercise/<int:workout_exercise_id>/up", methods=["POST"])
@login_required
def move_exercise_up(workout_id, workout_exercise_id):
    db = get_db_connection()

    get_user_workout(db, workout_id)
    current_exercise = get_workout_exercise(db, workout_id, workout_exercise_id)

    previous_exercise = db.execute(
        """
        SELECT id, position
        FROM workout_exercises
        WHERE workout_id = ? AND position < ?
        ORDER BY position DESC, id DESC
        LIMIT 1
        """,
        (workout_id, current_exercise["position"])
    ).fetchone()

    if previous_exercise is None:
        db.close()
        return redirect(url_for("workout", workout_id=workout_id))

    db.execute(
        """
        UPDATE workout_exercises
        SET position = ?
        WHERE id = ?
        """,
        (previous_exercise["position"], current_exercise["id"])
    )

    db.execute(
        """
        UPDATE workout_exercises
        SET position = ?
        WHERE id = ?
        """,
        (current_exercise["position"], previous_exercise["id"])
    )

    db.commit()
    db.close()

    return redirect(url_for("workout", workout_id=workout_id))


@app.route("/workouts/<int:workout_id>/exercise/<int:workout_exercise_id>/down", methods=["POST"])
@login_required
def move_exercise_down(workout_id, workout_exercise_id):
    db = get_db_connection()

    get_user_workout(db, workout_id)
    current_exercise = get_workout_exercise(db, workout_id, workout_exercise_id)

    next_exercise = db.execute(
        """
        SELECT id, position
        FROM workout_exercises
        WHERE workout_id = ? AND position > ?
        ORDER BY position ASC, id ASC
        LIMIT 1
        """,
        (workout_id, current_exercise["position"])
    ).fetchone()

    if next_exercise is None:
        db.close()
        return redirect(url_for("workout", workout_id=workout_id))

    db.execute(
        """
        UPDATE workout_exercises
        SET position = ?
        WHERE id = ?
        """,
        (next_exercise["position"], current_exercise["id"])
    )

    db.execute(
        """
        UPDATE workout_exercises
        SET position = ?
        WHERE id = ?
        """,
        (current_exercise["position"], next_exercise["id"])
    )

    db.commit()
    db.close()

    return redirect(url_for("workout", workout_id=workout_id))


# =========================================
# EXCLUIR TREINO
# =========================================

@app.route("/workouts/<int:workout_id>/delete", methods=["POST"])
@login_required
def delete_workout(workout_id):
    db = get_db_connection()

    get_user_workout(db, workout_id)

    db.execute(
        """
        DELETE FROM workout_exercises
        WHERE workout_id = ?
        """,
        (workout_id,)
    )

    db.execute(
        """
        DELETE FROM workouts
        WHERE id = ? AND user_id = ?
        """,
        (workout_id, session["user_id"])
    )

    db.commit()
    db.close()

    flash("Treino excluído com sucesso.", "success")
    return redirect(url_for("workouts"))


# =========================================
# EDITAR TREINO
# =========================================

@app.route("/workouts/<int:workout_id>/edit", methods=["GET", "POST"])
@login_required
def edit_workout(workout_id):
    db = get_db_connection()

    workout = get_user_workout(db, workout_id)

    if request.method == "POST":
        name = request.form["name"].strip()

        if not name:
            db.close()
            flash("Digite um nome para o treino.", "error")
            return redirect(url_for("edit_workout", workout_id=workout_id))

        if len(name) > 50:
            db.close()
            flash("O nome do treino deve ter no máximo 50 caracteres.", "error")
            return redirect(url_for("edit_workout", workout_id=workout_id))

        db.execute(
            """
            UPDATE workouts
            SET name = ?
            WHERE id = ? AND user_id = ?
            """,
            (name, workout_id, session["user_id"])
        )

        db.commit()
        db.close()

        flash("Treino atualizado com sucesso.", "success")
        return redirect(url_for("workout", workout_id=workout_id))

    db.close()

    return render_template("edit_workout.html", workout=workout)


# =========================================
# REGISTRO
# =========================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirmation = request.form["confirmation"]

        if not username:
            flash("Digite um nome de usuário.", "error")
            return redirect(url_for("register"))

        if len(username) < 3:
            flash("O nome de usuário deve ter pelo menos 3 caracteres.", "error")
            return redirect(url_for("register"))

        if len(username) > 30:
            flash("O nome de usuário deve ter no máximo 30 caracteres.", "error")
            return redirect(url_for("register"))

        if not password:
            flash("Digite uma senha.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "error")
            return redirect(url_for("register"))

        if password != confirmation:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for("register"))

        db = get_db_connection()

        existing_user = db.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if existing_user:
            db.close()
            flash("Este nome de usuário já existe.", "error")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        cursor = db.execute(
            """
            INSERT INTO users (username, hash)
            VALUES (?, ?)
            """,
            (username, password_hash)
        )

        db.commit()

        session.clear()
        session["user_id"] = cursor.lastrowid

        db.close()

        flash("Conta criada com sucesso. Bem-vindo ao Spartan!", "success")
        return redirect(url_for("workouts"))

    return render_template("register.html")


# =========================================
# LOGIN
# =========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Preencha o nome de usuário e a senha.", "error")
            return redirect(url_for("login"))

        db = get_db_connection()

        user = db.execute(
            """
            SELECT id, username, hash
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        db.close()

        if user is None or not check_password_hash(user["hash"], password):
            flash("Usuário ou senha inválidos.", "error")
            return redirect(url_for("login"))

        session.clear()
        session["user_id"] = user["id"]

        flash("Login realizado com sucesso.", "success")
        return redirect(url_for("workouts"))

    return render_template("login.html")


# =========================================
# PERFIL
# =========================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db_connection()

    user = db.execute(
        """
        SELECT id, username
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if user is None:
        db.close()
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        new_username = request.form["username"].strip()

        if not new_username:
            db.close()
            flash("O nome de usuário não pode estar vazio.", "error")
            return redirect(url_for("profile"))

        if len(new_username) < 3:
            db.close()
            flash("O nome de usuário deve ter pelo menos 3 caracteres.", "error")
            return redirect(url_for("profile"))

        if len(new_username) > 30:
            db.close()
            flash("O nome de usuário deve ter no máximo 30 caracteres.", "error")
            return redirect(url_for("profile"))

        existing_user = db.execute(
            """
            SELECT id
            FROM users
            WHERE username = ? AND id != ?
            """,
            (new_username, session["user_id"])
        ).fetchone()

        if existing_user:
            db.close()
            flash("Este nome de usuário já está em uso.", "error")
            return redirect(url_for("profile"))

        db.execute(
            """
            UPDATE users
            SET username = ?
            WHERE id = ?
            """,
            (new_username, session["user_id"])
        )

        db.commit()
        db.close()

        flash("Nome de usuário alterado com sucesso.", "success")
        return redirect(url_for("profile"))

    workout_count = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM workouts
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()["total"]

    exercise_count = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM workout_exercises
        JOIN workouts ON workout_exercises.workout_id = workouts.id
        WHERE workouts.user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()["total"]

    db.close()

    return render_template(
        "profile.html",
        user=user,
        workout_count=workout_count,
        exercise_count=exercise_count
    )


# =========================================
# ALTERAR SENHA
# =========================================

@app.route("/profile/password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirmation = request.form["confirmation"]

    if not current_password or not new_password or not confirmation:
        flash("Preencha todos os campos.", "error")
        return redirect(url_for("profile"))

    if new_password != confirmation:
        flash("As novas senhas não coincidem.", "error")
        return redirect(url_for("profile"))

    if len(new_password) < 6:
        flash("A nova senha deve ter pelo menos 6 caracteres.", "error")
        return redirect(url_for("profile"))

    db = get_db_connection()

    user = db.execute(
        """
        SELECT id, hash
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if user is None:
        db.close()
        session.clear()
        return redirect(url_for("login"))

    if not check_password_hash(user["hash"], current_password):
        db.close()
        flash("Senha atual incorreta.", "error")
        return redirect(url_for("profile"))

    new_hash = generate_password_hash(new_password)

    db.execute(
        """
        UPDATE users
        SET hash = ?
        WHERE id = ?
        """,
        (new_hash, session["user_id"])
    )

    db.commit()
    db.close()

    flash("Senha alterada com sucesso.", "success")
    return redirect(url_for("profile"))


# =========================================
# LOGOUT
# =========================================

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


# =========================================
# ERRO 404
# =========================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
