# Spartan

Spartan is a full-stack web application for creating and managing personalized workout routines, developed as the Final Project for Harvard's CS50.

The application allows users to create an account, organize workout routines, add exercises, define sets and repetitions, reorder exercises, and manage their profile through a responsive interface.

The project combines frontend development, backend logic, authentication, security, relational database design, Docker containerization, persistent storage, and cloud deployment.

---

## Live Application

Spartan is deployed on Railway and is publicly available at:

**https://spartan-production-d656.up.railway.app**

The production environment runs the Flask application inside a Docker container built from the project's `Dockerfile`.

Application data is stored in a persistent Railway Volume mounted at `/app/data`. The `DATABASE_PATH` environment variable points SQLite to `/app/data/spartan.db`, keeping the database outside the container's ephemeral filesystem.

This allows containers to be restarted, replaced, or redeployed without losing registered users, workouts, or exercise configurations.

Database persistence was tested by creating application data, redeploying the service, and confirming that the user account, workout, and exercise configuration remained available.

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
- Docker containerization
- Persistent database storage
- Cloud deployment
- Public HTTPS access
- Responsive desktop and mobile interface
- Custom 404 error page

---

## Architecture

Spartan uses a server-rendered architecture built with Flask.

In production, the application is containerized with Docker and deployed on Railway.

```text
User Browser
     │
     │ HTTPS
     ▼
Railway Public Domain
     │
     ▼
Docker Container
     │
     ├── Python
     ├── Flask
     ├── Routes
     ├── Authentication
     ├── Validation
     ├── Application Logic
     │
     └── /app/data
            │
            ▼
   Persistent Railway Volume
            │
            └── spartan.db
```

The browser communicates with the application through a public HTTPS endpoint.

Railway builds the application from the `Dockerfile` stored in the GitHub repository and runs the resulting container.

Inside the container, Flask handles routing, authentication, validation, database operations, and application logic. Jinja templates generate the HTML returned to the browser.

Persistent application data is stored separately from the container through a Railway Volume mounted at `/app/data`.

This separates the application runtime from its persistent data and allows the container to be replaced or redeployed without deleting application data.

---

## Design Decisions

Several design decisions were made to keep Spartan simple to use while maintaining a clear and extensible application structure.

### Flask and Server-Side Rendering

Flask was chosen as the backend framework because it provides a lightweight structure while allowing the application logic to remain explicit.

Routes, authentication, validation, database operations, and access control are handled in Python, while Jinja templates generate the HTML presented to the user.

The application uses server-side rendering instead of a separate frontend framework. For Spartan's current scope, this avoids unnecessary complexity and keeps communication between the interface and backend straightforward.

### Relational Database Structure

SQLite was selected because Spartan's data is naturally relational and the current application does not require the infrastructure of a separate database server.

Instead of storing all workout information in a single table, the database separates users, workouts, exercises, and the relationship between workouts and exercises.

This reduces data duplication and makes the structure easier to maintain.

### Exercise Catalog

Exercises are stored in their own `exercises` table rather than being stored directly inside each workout.

This allows the same exercise to be reused across multiple workouts without duplicating its name and muscle group.

The initial catalog is created through `schema.sql`, providing a consistent set of exercises when the database is initialized.

### Workout-Exercise Relationship

The `workout_exercises` table acts as an associative table between `workouts` and `exercises`.

This design is necessary because the same exercise can belong to multiple workouts while having different sets and repetitions in each one.

For example, the same exercise can be configured as 3 × 10 in one workout and 4 × 12 in another without modifying the original exercise stored in the catalog.

### Exercise Ordering

The `position` column in `workout_exercises` stores the order of exercises independently for each workout.

This was preferred over relying on database IDs because an exercise's ID represents its database record, not its intended position in a training routine.

Keeping position as separate data allows users to reorder exercises without recreating them.

### Authentication and Ownership

Workouts are associated with users through `user_id`.

Protected operations verify the authenticated user and ownership of the requested workout. This prevents one account from editing or deleting another user's workout simply by changing an ID in the URL.

Passwords are stored as hashes rather than plain text, and Flask sessions maintain authentication between requests.

### CSRF Protection

Forms that modify application data use CSRF protection through Flask-WTF.

This protects operations such as profile changes, password changes, workout modifications, exercise actions, and logout against unauthorized cross-site requests.

### Automatic Database Initialization

Spartan automatically initializes its database when the configured database file does not exist.

The application executes `schema.sql` to create the required relational structure and populate the initial exercise catalog.

This allows both local installations and new container environments to initialize the application without requiring a pre-existing database file.

### Environment-Based Configuration

The database location can be configured using the `DATABASE_PATH` environment variable.

When the variable is not defined, Spartan uses:

```text
spartan.db
```

In the production environment, Railway defines:

```text
DATABASE_PATH=/app/data/spartan.db
```

This allows the same application code to run in different environments without hardcoding environment-specific database paths.

### Docker Containerization

Spartan is containerized using Docker.

The `Dockerfile` defines the Python runtime, installs the application's dependencies, copies the project files, exposes the application port, and defines the command used to start Flask.

This provides a consistent and isolated execution environment regardless of the host machine.

The Docker image contains the application and its runtime dependencies but does not contain the persistent SQLite database.

### Persistent Storage

Containers can be replaced or recreated, so persistent application data is stored outside the container.

For local Docker execution, Spartan can use a named Docker volume:

```text
spartan-data
```

In production, Railway provides a persistent volume mounted at:

```text
/app/data
```

The SQLite database is stored inside this volume at:

```text
/app/data/spartan.db
```

The resulting production structure is:

```text
Docker Container
      │
      └── /app/data
             │
             ▼
      Railway Volume
             │
             └── spartan.db
```

This architecture allows the application container to be redeployed without deleting registered users, workouts, or workout configurations.

Persistence was verified in production by creating a user, workout, and exercise configuration, performing a Railway redeploy, and confirming that all data remained available afterward.

### Cloud Deployment

The production version of Spartan is deployed on Railway directly from the GitHub repository.

The deployment workflow is:

```text
Local Development
       │
       ▼
GitHub Repository
       │
       ▼
Railway
       │
       │ reads Dockerfile
       ▼
Docker Build
       │
       ▼
Docker Container
       │
       ├── Flask Application
       │
       └── /app/data
               │
               ▼
        Persistent Volume
               │
               └── spartan.db
```

This creates a direct path between source control and the deployed application.

Changes pushed to the GitHub repository can be used to rebuild and redeploy the application while persistent data remains stored independently in the Railway Volume.

### Interface and Responsive Design

The interface was built with custom HTML and CSS instead of a UI framework.

This provides greater control over Spartan's visual identity and allows the interface to follow a consistent dark, high-contrast design inspired by the Spartan theme.

Responsive layouts and mobile navigation allow the same application to work on desktop and smaller screens without maintaining separate interfaces.

### Extensibility

The current architecture was designed around the project's present scope while leaving room for future development.

Separating application logic, relational data, runtime configuration, containerization, and persistent storage makes it possible to introduce features such as workout history, progression tracking, custom exercises, statistics, or a different database system without redesigning the entire application.

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

Environment variables allow environment-specific configuration to remain separate from the application code.

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

**Cloud and Deployment**

Railway | Persistent Volume | HTTPS

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
- `Dockerfile` — defines the Docker image used to run Spartan.
- `.dockerignore` — prevents unnecessary and local files from being included in the Docker build context.
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

## Running Locally

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

The `spartan-data` volume stores the SQLite database independently from the container.

This means registered users, workouts, and exercise configurations remain available even if the application container is removed and recreated.

---

## Production Deployment

Spartan is deployed on Railway using the project's GitHub repository and Docker configuration.

**Live application:**

https://spartan-production-d656.up.railway.app

The production environment uses:

```text
GitHub
   │
   ▼
Railway
   │
   ▼
Docker Container
   │
   ├── Flask
   ├── Application
   │
   └── /app/data
          │
          ▼
   Persistent Railway Volume
          │
          └── spartan.db
```

The Railway Volume is mounted at:

```text
/app/data
```

The production database path is configured through:

```text
DATABASE_PATH=/app/data/spartan.db
```

This keeps the SQLite database outside the lifecycle of the Docker container.

The production persistence configuration was tested by creating application data, redeploying the service, and verifying that the user account, workout, exercise, sets, and repetitions remained available after the redeploy.

---

## Requirements

The Python dependencies are listed in `requirements.txt`:

```text
Flask
Flask-WTF
```

Docker is optional for local development and is used for the containerized deployment.

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
- Migration to a server-based database for larger deployments
- Automated testing
- CI/CD workflow

---

## Author

Developed by **Pedro Baliza** as the Final Project for **CS50 — Introduction to Computer Science**.