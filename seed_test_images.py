import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont

DB_PATH = "Database/store.db"
IMAGE_DIR = os.path.join(".", "product_images")

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def create_sample_image(filename, text, color):
    """Genera una imagen JPG de prueba con un color de fondo y un nombre."""
    img_path = os.path.join(IMAGE_DIR, filename)
    img = Image.new("RGB", (400, 300), color=color)
    draw = ImageDraw.Draw(img)
    
    # Dibujar texto al centro
    draw.text((30, 140), f"Producto: {text}", fill=(255, 255, 255))
    img.save(img_path)
    return img_path

def seed_images_for_testing():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Asegurar columna image_path
    try:
        cursor.execute("ALTER TABLE raw_inventory ADD COLUMN image_path TEXT;")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Ya existe

    # Obtener los primeros 6 productos
    products = cursor.execute("SELECT product_id, product_name FROM raw_inventory LIMIT 6").fetchall()

    colors = [
        (211, 47, 47),   # Rojo
        (245, 124, 0),   # Naranja
        (56, 142, 60),   # Verde
        (25, 118, 210),  # Azul
        (123, 31, 162),  # Morado
        (0, 150, 136)    # Teal
    ]

    print(f"Asignando imágenes a {len(products)} productos para pruebas (R05)...")

    for idx, (prod_id, prod_name) in enumerate(products):
        filename = f"test_prod_{prod_id}.jpg"
        color = colors[idx % len(colors)]
        
        # Generar imagen
        img_path = create_sample_image(filename, prod_name[:20], color)
        
        # Actualizar en base de datos
        cursor.execute(
            "UPDATE raw_inventory SET image_path = ? WHERE product_id = ?",
            [img_path, prod_id]
        )
        print(f" - Producto ID {prod_id} ({prod_name}) -> Imagen: {img_path}")

    conn.commit()
    conn.close()
    print("¡Pruebas (R05) completadas con éxito!")

if __name__ == "__main__":
    seed_images_for_testing()