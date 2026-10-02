PRAGMA foreign_keys = ON;


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);


CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    muscle_group TEXT NOT NULL,

    UNIQUE (name, muscle_group)
);


CREATE TABLE workout_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    sets INTEGER NOT NULL CHECK (sets BETWEEN 1 AND 10),
    reps INTEGER NOT NULL CHECK (reps BETWEEN 1 AND 30),
    position INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (workout_id)
        REFERENCES workouts(id)
        ON DELETE CASCADE,

    FOREIGN KEY (exercise_id)
        REFERENCES exercises(id)
);


-- ==========================================
-- CATÁLOGO INICIAL DE EXERCÍCIOS
-- ==========================================

INSERT INTO exercises (name, muscle_group) VALUES
    ('Agachamento Smith', 'Perna'),
    ('Cadeira Extensora', 'Perna'),
    ('Mesa Flexora', 'Perna'),
    ('Cadeira Adutora', 'Perna'),
    ('Panturrilha', 'Perna'),
    ('Puxada Alta', 'Costas'),
    ('Puxada Fechada', 'Costas'),
    ('Bíceps Polia', 'Bíceps'),
    ('Bíceps Corda', 'Bíceps'),
    ('Antebraço Polia', 'Antebraço'),
    ('Abdômen', 'Abdômen'),
    ('Supino 45°', 'Peito'),
    ('Crucifixo', 'Peito'),
    ('Tríceps Polia', 'Tríceps'),
    ('Tríceps Corda', 'Tríceps'),
    ('Elevação Lateral', 'Ombro');
