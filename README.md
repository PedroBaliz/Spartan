# Spartan

Spartan is a full-stack web application for creating and managing personalized workout routines, developed as the Final Project for Harvard's CS50.

The application allows users to create an account, organize workout routines, add exercises, define sets and repetitions, reorder exercises, and manage their profile through a responsive interface.

The project combines frontend development, backend logic, authentication, security, relational database concepts, and containerization in a complete web application.

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
- Automatic database initialization
- Docker support with persistent data storage
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
   ├──────────────► SQLite Database
   │
   ▼
Jinja Templates
   │
   ▼
HTML + CSS
```

The browser sends requests to Flask, which handles authentication, validation, and application logic. Flask communicates with SQLite when data needs to be retrieved or modified and renders Jinja templates to generate the interface returned to the browser.

This structure separates the application's presentation, backend logic, and persistent data.

The application can also run inside a Docker container. When containerized, the SQLite database can be stored in a Docker volume, allowing application data to persist even when the container is removed and recreated.

---

## Design Decisions

Several design decisions were made to keep Spartan simple to use while maintaining a clear and extensible application structure.

### Flask and Server-Side Rendering

Flask was chosen as the backend framework because it provides a lightweight structure while allowing the application logic to remain explicit. Routes, authentication, validation, database operations, and access control are handled in Python, while Jinja templates generate the HTML presented to the user.

The application uses server-side rendering instead of a separate frontend framework. For Spartan's current scope, this avoids unnecessary complexity and keeps communication between the interface and backend straightforward.

### Relational Database Structure

SQLite was selected because Spartan's data is naturally relational and the application does not currently require the infrastructure of a separate database server.

Instead of storing all workout information in a single table, the database separates users, workouts, exercises, and the relationship between workouts and exercises.

This reduces data duplication and makes the structure easier to maintain.

### Exercise Catalog

Exercises are stored in their own `exercises` table rather than being stored directly inside each workout.

This allows the same exercise to be reused across multiple workouts without duplicating its name and muscle group. The initial catalog is created through `schema.sql`, providing a consistent set of exercises when the database is initialized.

### Workout-Exercise Relationship

The `workout_exercises` table acts as an associative table between `workouts` and `exercises`.

This design was necessary because the same exercise can belong to multiple workouts while having different sets and repetitions in each one.

For example, the same exercise could be configured as 3 × 10 in one workout and 4 × 12 in another without modifying the original exercise stored in the catalog.

### Exercise Ordering

The `position` column in `workout_exercises` stores the order of exercises independently for each workout.

This was preferred over relying on database IDs because an exercise's ID represents its record, not its intended position in a training routine. Keeping position as separate data allows users to reorder exercises without recreating them.

### Authentication and Ownership

Workouts are associated with users through `user_id`.

Protected operations verify the authenticated user and the ownership of the requested workout. This prevents one account from editing or deleting another user's workout simply by changing an ID in the URL.

Passwords are stored as hashes rather than plain text, and Flask sessions are used to maintain authentication between requests.

### CSRF Protection

Forms that modify application data use CSRF protection through Flask-WTF.

This adds protection against requests submitted from unauthorized external pages and applies to operations such as profile changes, password changes, workout modifications, exercise actions, and logout.

### Automatic Database Initialization

Spartan automatically initializes its database when `spartan.db` does not exist.

The application executes `schema.sql` to create the required relational structure and populate the initial exercise catalog. This makes a fresh installation easier to run and allows a new Docker container to initialize the application without requiring a pre-existing database file.

The database location can also be configured through the `DATABASE_PATH` environment variable. By default, the application uses `spartan.db`.

### Docker and Data Persistence

Docker support was added to provide a consistent and isolated runtime environment for the application.

The Docker image contains the Flask application and its Python dependencies but does not include the local SQLite database. When running the application with Docker, the database can be stored in a named Docker volume.

This separates persistent application data from the container itself. As a result, a container can be stopped, removed, and recreated without deleting registered users, workouts, or exercise configurations stored in the database.

### Interface and Responsive Design

The interface was built with custom HTML and CSS instead of a UI framework.

This provided greater control over Spartan's visual identity and allowed the interface to follow a consistent dark, high-contrast design inspired by the Spartan theme.

Responsive layouts and mobile navigation were implemented so the same application can be used on both desktop and smaller screens without maintaining separate interfaces.

### Extensibility

The current architecture was designed around the project's present scope while leaving room for future features.

Separating users, workouts, exercises, workout-specific exercise data, and runtime configuration makes it possible to later introduce features such as workout history, progression tracking, custom exercises, statistics, and cloud deployment without redesigning the application's core data model.

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

**Containerization**

Docker | Docker Volumes

**Development**

Git | GitHub | Visual Studio Code | GitHub Codespaces

---

## Project Structure

```text
Spartan/
│
├── app.py
├── Dockerfile
├── .dockerignore
├── .gitignore
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
- `schema.sql` — database schema and initial exercise catalog.
- `Dockerfile` — defines the Docker image used to run Spartan in a container.
- `.dockerignore` — prevents unnecessary or local files from being copied into the Docker image.
- `.gitignore` — excludes local database, environment, and generated files from version control.
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

Run the application:

```bash
flask run
```

If `spartan.db` does not exist, Spartan automatically creates the database using `schema.sql` and loads the initial exercise catalog.

Open the local address provided by Flask in your browser.

---

## Running with Docker

Spartan can also run inside a Docker container without requiring a local Python environment.

Build the Docker image:

```bash
docker build -t spartan .
```

Create a persistent Docker volume:

```bash
docker volume create spartan-data
```

Run the container:

```bash
docker run --name spartan-app -p 5000:5000 -e DATABASE_PATH=/app/data/spartan.db -v spartan-data:/app/data spartan
```

Open the application at:

```text
http://localhost:5000
```

The `spartan-data` volume stores the SQLite database independently from the container. This means users, workouts, and exercise configurations remain available even if the `spartan-app` container is removed and recreated.

To stop the running container, press:

```text
Ctrl + C
```

If the container is removed, it can be recreated using the same `docker run` command and the existing `spartan-data` volume.

---

## Requirements

The Python dependencies are listed in `requirements.txt`:

```text
Flask
Flask-WTF
```

Docker is optional and is only required when running the containerized version of Spartan.

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
- Production WSGI server
- Cloud deployment

---

## Author

Developed by **Pedro Baliza** as the Final Project for **CS50 — Introduction to Computer Science**.