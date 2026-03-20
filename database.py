import sqlite3

DB_PATH = "health.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT UNIQUE NOT NULL,
            age        INTEGER,
            gender     TEXT,
            height     REAL DEFAULT 0,
            weight     REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS vitals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER,
            bp_sys      INTEGER,
            bp_dia      INTEGER,
            heart_rate  INTEGER,
            glucose     INTEGER,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER,
            name        TEXT NOT NULL,
            dosage      TEXT,
            frequency   TEXT,
            time_of_day TEXT,
            notes       TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    conn.commit()
    conn.close()
    try:
        conn = get_conn()
        conn.execute("ALTER TABLE patients ADD COLUMN height REAL DEFAULT 0")
        conn.execute("ALTER TABLE patients ADD COLUMN weight REAL DEFAULT 0")
        conn.commit()
        conn.close()
    except Exception:
        pass

def add_patient(name, age, gender, height=0.0, weight=0.0):
    try:
        conn = get_conn()
        conn.execute(
            "INSERT INTO patients (name, age, gender, height, weight) VALUES (?, ?, ?, ?, ?)",
            (name, age, gender, height, weight)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_patients():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_patient_by_name(name):
    conn = get_conn()
    row = conn.execute("SELECT * FROM patients WHERE name=?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_patient_measurements(patient_id, height, weight):
    conn = get_conn()
    conn.execute(
        "UPDATE patients SET height=?, weight=? WHERE id=?",
        (height, weight, patient_id)
    )
    conn.commit()
    conn.close()

def delete_patient(patient_id):
    conn = get_conn()
    conn.execute("DELETE FROM vitals    WHERE patient_id=?", (patient_id,))
    conn.execute("DELETE FROM medicines WHERE patient_id=?", (patient_id,))
    conn.execute("DELETE FROM patients  WHERE id=?",         (patient_id,))
    conn.commit()
    conn.close()

def save_vitals(patient_id, bp_sys, bp_dia, heart_rate, glucose):
    conn = get_conn()
    conn.execute(
        "INSERT INTO vitals (patient_id, bp_sys, bp_dia, heart_rate, glucose) VALUES (?,?,?,?,?)",
        (patient_id, bp_sys, bp_dia, heart_rate, glucose)
    )
    conn.commit()
    conn.close()

def get_vitals_history(patient_id, limit=20):
    conn = get_conn()
    rows = conn.execute("""
        SELECT p.name, v.bp_sys, v.bp_dia, v.heart_rate, v.glucose, v.recorded_at
        FROM vitals v JOIN patients p ON v.patient_id = p.id
        WHERE v.patient_id = ?
        ORDER BY v.recorded_at DESC
        LIMIT ?
    """, (patient_id, limit)).fetchall()
    conn.close()
    return [tuple(r) for r in rows]

def add_medicine(patient_id, name, dosage, frequency, time_of_day, notes=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO medicines (patient_id, name, dosage, frequency, time_of_day, notes) VALUES (?,?,?,?,?,?)",
        (patient_id, name, dosage, frequency, time_of_day, notes)
    )
    conn.commit()
    conn.close()

def get_medicines(patient_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM medicines WHERE patient_id=? ORDER BY time_of_day, name",
        (patient_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_medicine(medicine_id):
    conn = get_conn()
    conn.execute("DELETE FROM medicines WHERE id=?", (medicine_id,))
    conn.commit()
    conn.close()