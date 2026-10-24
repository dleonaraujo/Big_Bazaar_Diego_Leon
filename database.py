import sqlite3
import os

# Ruta de la base de datos
DB_DIR = "./Database"
DB_PATH = os.path.join(DB_DIR, "store.db")

def init_db():
    # Asegurar que el directorio de la base de datos exista
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificar si la tabla 'employee' antigua carece de la columna 'contact' y regenerarla si es necesario
    cursor.execute("PRAGMA table_info(employee)")
    columns = [col[1] for col in cursor.fetchall()]
    if columns and "contact" not in columns:
        cursor.execute("DROP TABLE employee")

    # 1. Tabla de Empleados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee (
        emp_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        contact TEXT NOT NULL,
        address TEXT NOT NULL,
        aadhar_num TEXT NOT NULL,
        password TEXT NOT NULL,
        designation TEXT NOT NULL
    );
    """)

    # 2. Tabla de Inventario Crudo / Maestro (raw_inventory)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_inventory (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_cat TEXT NOT NULL,
        product_subcat TEXT NOT NULL,
        stock INTEGER NOT NULL,
        mrp REAL NOT NULL,
        cost_price REAL NOT NULL,
        vendor_phn TEXT NOT NULL,
        image_path TEXT DEFAULT ''
    );
    """)

    # 3. Tabla de Facturas (bill)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bill (
        bill_no INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL
    );
    """)

    # 4. Tabla de Detalle de Facturas (inventory)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_no INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (bill_no) REFERENCES bill (bill_no)
    );
    """)

    # --------------------------------------------------------------------------
    # SEED DATA (Datos Iniciales de Prueba)
    # --------------------------------------------------------------------------

    # Insertar administrador por defecto si no existe
    cursor.execute("SELECT 1 FROM employee WHERE emp_id = 'EMP1001'")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO employee (emp_id, name, contact, address, aadhar_num, password, designation)
        VALUES ('EMP1001', 'Admin Principal', '9876543210', 'Oficina Central', '123456789012', 'admin123', 'Admin')
        """)

    # Insertar productos de prueba si la tabla de inventario está vacía
    cursor.execute("SELECT COUNT(*) FROM raw_inventory")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Camiseta Algodón", "Ropa", "Hombre", 50, 25.00, 12.50, "9876543210", ""),
            ("Pantalón Jean", "Ropa", "Mujer", 30, 45.00, 22.00, "9876543210", ""),
            ("Zapatillas Deportivas", "Calzado", "Unisex", 20, 80.00, 40.00, "9876543210", "")
        ]
        cursor.executemany("""
        INSERT INTO raw_inventory (product_name, product_cat, product_subcat, stock, mrp, cost_price, vendor_phn, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_products)

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    init_db()