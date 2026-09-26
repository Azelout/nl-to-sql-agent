import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "company.db")


def init_db(db_path: str = DB_PATH) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript(
        """
        PRAGMA foreign_keys = ON;

        DROP TABLE IF EXISTS employee_projects;
        DROP TABLE IF EXISTS projects;
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS departments;

        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            budget REAL NOT NULL,
            location TEXT NOT NULL
        );

        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hire_date DATE NOT NULL,
            salary REAL NOT NULL,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
        );

        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            budget REAL NOT NULL,
            status TEXT CHECK(status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
        );

        CREATE TABLE employee_projects (
            employee_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            hours_allocated INTEGER DEFAULT 0,
            PRIMARY KEY (employee_id, project_id),
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Données de test
        INSERT INTO departments (name, budget, location) VALUES
            ('Engineering', 850000.0, 'Paris'),
            ('Data & AI', 620000.0, 'Paris'),
            ('Product', 310000.0, 'Lyon'),
            ('Security', 400000.0, 'Rennes');

        INSERT INTO employees (first_name, last_name, email, hire_date, salary, department_id) VALUES
            ('Alice', 'Moreau', 'alice.m@company.com', '2022-03-15', 68000.0, 2),
            ('Bob', 'Durand', 'bob.d@company.com', '2021-06-01', 74000.0, 1),
            ('Camille', 'Leroy', 'camille.l@company.com', '2023-01-10', 52000.0, 2),
            ('David', 'Bernard', 'david.b@company.com', '2020-11-20', 82000.0, 1),
            ('Elena', 'Roux', 'elena.r@company.com', '2024-02-01', 48000.0, 3),
            ('Farid', 'Haddad', 'farid.h@company.com', '2022-09-01', 61000.0, 4);

        INSERT INTO projects (name, start_date, end_date, budget, status) VALUES
            ('Argon Pipeline', '2025-01-01', '2026-06-30', 250000.0, 'IN_PROGRESS'),
            ('Cyber Threat Ingestion', '2024-05-01', '2025-12-31', 140000.0, 'COMPLETED'),
            ('Core Engine Refactor', '2025-08-01', NULL, 180000.0, 'IN_PROGRESS'),
            ('Mobile App V2', '2026-02-01', NULL, 90000.0, 'PLANNED');

        INSERT INTO employee_projects (employee_id, project_id, role, hours_allocated) VALUES
            (1, 1, 'Lead Data Scientist', 30),
            (3, 1, 'ML Engineer', 35),
            (2, 3, 'Backend Lead', 25),
            (4, 3, 'Senior Architect', 20),
            (6, 2, 'SecOps Lead', 40),
            (1, 2, 'NLP Consultant', 10);
        """
    )
    conn.commit()
    conn.close()


def get_schema(db_path: str = DB_PATH) -> str:
    """Extrait le DDL brut de création des tables pour l'injecter au prompt LLM."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT sql 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return "\n\n".join(row[0] for row in rows if row[0] is not None)


def execute_query(
    query: str, db_path: str = DB_PATH
) -> tuple[bool, list[tuple] | str]:
    """Tente d'exécuter la requête SQL.

    Renvoie (True, [rows]) si succès, ou (False, "message d'erreur") si
    échec.
    """
    # Nettoyage minimal et blocage des requêtes destructrices
    sanitized = query.strip().rstrip(";")
    first_token = sanitized.split()[0].upper() if sanitized else ""
    if first_token not in ("SELECT", "WITH"):
        return False, "Only read-only queries (SELECT, WITH) are authorized."

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sanitized)
        results = cursor.fetchall()
        conn.close()
        return True, results
    except sqlite3.Error as e:
        conn.close()
        return False, f"{type(e).__name__}: {str(e)}"


if __name__ == "__main__":
    init_db()
    print("Base initialisée avec succès.")
    print("\n--- Schéma DDL extrait ---")
    print(get_schema())