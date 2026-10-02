# Spartan

Spartan is a full-stack web application for creating and managing personalized workout routines, developed as the Final Project for Harvard's CS50.

The application allows users to create an account, organize workout routines, add exercises, define sets and repetitions, reorder exercises, and manage their profile through a responsive interface.

The project combines frontend development, backend logic, authentication, security, and relational database concepts in a complete web application.

---

## Features

- User registration, login, and logout
- Session-based authentication
- Secure password hashing
- Create, edit, and delete workouts
- Add exercises from an exercise catalog
- Define sets and repetitions
- Edit and remove exercises
- Reorder exercises within a workout
- User profile management
- Username and password updates
- CSRF protection
- Responsive desktop and mobile interface
- Custom 404 error page

---

## Architecture

Spartan uses a server-rendered web architecture built with Flask.

```text
Browser
   │
   │ HTTP Request
   ▼
Flask Application
   │
   ├── Routes
   ├── Authentication
   ├── Validation
   └── Application Logic
   │
   ▼
SQLite Database
   │
   ▼
Jinja Templates
   │
   ▼
HTML + CSS
```

The browser sends requests to Flask, which handles authentication, validation, and application logic. When necessary, Flask communicates with SQLite to retrieve or modify data and then renders the corresponding Jinja template.

This structure separates the application's presentation, backend logic, and persistent data.

---

## Database

Spartan uses SQLite as its relational database.

The database contains four main tables:

```text
users
  │
  └── workouts
        │
        └── workout_exercises
                 │
                 └── exercises
```

### `users`

Stores user accounts and password hashes.

### `workouts`

Stores workout routines and associates each workout with its owner through `user_id`.

A single user can have multiple workouts.

### `exercises`

Stores the exercise catalog, including the exercise name and muscle group.

Exercises are stored separately so they can be reused across different workouts.

### `workout_exercises`

Connects workouts and exercises while storing information specific to that relationship:

- Sets
- Repetitions
- Exercise position

This structure allows the same exercise to appear in different workouts with different configurations without duplicating the exercise itself.

---

## Security

Spartan includes several security mechanisms.

Passwords are processed using Werkzeug password hashing functions and are never stored as plain text.

Authentication is session-based, and protected routes verify the logged-in user before allowing access to workout information.

Forms that modify application data are protected against Cross-Site Request Forgery using Flask-WTF and CSRF tokens.

Workout operations also verify ownership so users cannot modify workouts belonging to other accounts.

---

## Technologies

**Languages**

Python | SQL | HTML | CSS

**Frameworks and Libraries**

Flask | Flask-WTF | Jinja | Werkzeug

**Database**

SQLite

**Development**

Git | GitHub | Visual Studio Code | GitHub Codespaces

---

## Project Structure

```text
Spartan/
│
├── app.py
├── README.md
├── requirements.txt
├── schema.sql
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│       └── Spartan_logo.png
│
└── templates/
    ├── 404.html
    ├── edit_exercise.html
    ├── edit_workout.html
    ├── exercise_form.html
    ├── index.html
    ├── layout.html
    ├── login.html
    ├── profile.html
    ├── register.html
    ├── workout_form.html
    ├── workout.html
    └── workouts.html
```

### Main Files

- `app.py` — Flask application containing routes, authentication, validation, database operations, and application logic.
- `schema.sql` — relational database structure used by the application.
- `templates/` — Jinja templates rendered by Flask.
- `static/css/style.css` — visual system, responsive layouts, components, and animations.
- `static/images/` — static visual assets used by the interface.
- `requirements.txt` — Python dependencies required to run the application.

---

## Interface

Spartan uses a dark visual identity inspired by strength, discipline, and the Spartan theme.

The interface includes high-contrast colors, structured workout cards, responsive layouts, subtle animations, interactive states, and mobile navigation.

Accessibility considerations include semantic form labels, visible keyboard focus states, ARIA attributes in navigation controls, and support for reduced-motion preferences.

---

## Running the Project

Clone the repository:

```bash
git clone https://github.com/PedroBaliz/Spartan.git
```

Enter the project directory:

```bash
cd Spartan
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Initialize the SQLite database:

```bash
sqlite3 spartan.db < schema.sql
```

This command creates the database structure and loads the initial exercise catalog.

Run the application:

```bash
flask run
```

Open the local address provided by Flask in your browser.

---

## Requirements

The Python dependencies are listed in `requirements.txt`:

```text
Flask
Flask-WTF
```

---

## Future Improvements

The current version focuses on workout creation and management. Possible future improvements include:

- Workout history
- Weight and progression tracking
- Training statistics
- Custom exercises
- Exercise search and filtering
- Workout duplication
- Rest timers
- Progressive overload tracking
- Docker containerization
- Cloud deployment

---

## Author

Developed by **Pedro Baliza** as the Final Project for **CS50 — Introduction to Computer Science**.
