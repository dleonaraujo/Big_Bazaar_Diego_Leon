import sqlite3
import re
import random
import string
import csv
import os
import shutil
from datetime import date
from time import strftime
from tkinter import NO
from tkinter import *

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter import scrolledtext as tkst
from PIL import Image, ImageTk

# Carpeta de almacenamiento para imágenes de productos
IMAGE_DIR = os.path.join(".", "product_images")
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# ==============================================================================
# 1. CAPA DE INTERNACIONALIZACIÓN (i18n)
# ==============================================================================
class I18n:
    def __init__(self):
        self.lang = "ES"
        self.texts = {
            "ES": {
                "admin_title": "Retail Manager",
                "admin_mode": "ADMIN MODE",
                "login": "INGRESAR",
                "logout": "Salir",
                "confirm_logout": "¿Está seguro de que desea salir?",
                "exit": "Salir",
                "confirm_exit": "¿Está seguro de que desea salir del sistema?",
                "login_success": "Inicio de sesión exitoso.",
                "login_error": "Usuario o contraseña incorrectos.",
                "not_admin": "No tiene permisos de administrador.",
                "forgot_pass": "¿Olvidó su contraseña?",
                "reset_title": "Recuperar contraseña",
                "reset_prompt_id": "Ingrese su Employee ID",
                "reset_prompt_pass": "Ingrese la nueva contraseña",
                "reset_ok": "Contraseña actualizada correctamente.",
                "reset_not_found": "Employee ID no encontrado.",
                "reset_empty": "Debe ingresar una contraseña válida.",
                "inventory": "Inventario",
                "employees": "Empleados",
                "invoices": "Facturas",
                "reports": "Reportes",
                "lang_btn": "EN",
                "report_title": "Generar Reporte",
                "report_ok": "Reporte generado correctamente en:",
                "report_err": "No se pudo generar el reporte.",
                "search": "Buscar",
                "add_prod": "AGREGAR PRODUCTO",
                "update_prod": "ACTUALIZAR PRODUCTO",
                "delete_prod": "ELIMINAR PRODUCTO",
                "add_emp": "AGREGAR EMPLEADO",
                "update_emp": "ACTUALIZAR EMPLEADO",
                "delete_emp": "ELIMINAR EMPLEADO",
                "view_invoice": "VER FACTURA",
                "delete_invoice": "ELIMINAR FACTURA",
                "add": "AGREGAR",
                "update": "ACTUALIZAR",
                "clear": "LIMPIAR",
                "confirm_del_prod": "¿Está seguro de que desea eliminar los productos seleccionados?",
                "confirm_del_emp": "¿Está seguro de que desea eliminar los empleados seleccionados?",
                "confirm_del_inv": "¿Está seguro de que desea eliminar las facturas seleccionadas?",
                "sel_prod_err": "Por favor seleccione un producto.",
                "sel_emp_err": "Por favor seleccione un empleado.",
                "sel_inv_err": "Por favor seleccione una factura.",
                "master_admin_err": "No se puede eliminar al administrador principal.",
                "one_prod_err": "Solo se puede actualizar un producto a la vez.",
                "one_emp_err": "Solo se puede actualizar un empleado a la vez.",
                "back_btn": "← Volver",
                "view_img": "Ver Imagen (Pantalla)"
            },
            "EN": {
                "admin_title": "Retail Manager",
                "admin_mode": "ADMIN MODE",
                "login": "LOGIN",
                "logout": "Logout",
                "confirm_logout": "Are you sure you want to logout?",
                "exit": "Exit",
                "confirm_exit": "Are you sure you want to exit?",
                "login_success": "The login is successful.",
                "login_error": "Incorrect username or password.",
                "not_admin": "You are not an admin.",
                "forgot_pass": "Forgot your password?",
                "reset_title": "Recover password",
                "reset_prompt_id": "Enter your Employee ID",
                "reset_prompt_pass": "Enter the new password",
                "reset_ok": "Password updated successfully.",
                "reset_not_found": "Employee ID not found.",
                "reset_empty": "You must enter a valid password.",
                "inventory": "Inventory",
                "employees": "Employees",
                "invoices": "Invoices",
                "reports": "Reports",
                "lang_btn": "ES",
                "report_title": "Generate Report",
                "report_ok": "Report generated successfully at:",
                "report_err": "Could not generate the report.",
                "search": "Search",
                "add_prod": "ADD PRODUCT",
                "update_prod": "UPDATE PRODUCT",
                "delete_prod": "DELETE PRODUCT",
                "add_emp": "ADD EMPLOYEE",
                "update_emp": "UPDATE EMPLOYEE",
                "delete_emp": "DELETE EMPLOYEE",
                "view_invoice": "VIEW INVOICE",
                "delete_invoice": "DELETE INVOICE",
                "add": "ADD",
                "update": "UPDATE",
                "clear": "CLEAR",
                "confirm_del_prod": "Are you sure you want to delete selected products?",
                "confirm_del_emp": "Are you sure you want to delete selected employee(s)?",
                "confirm_del_inv": "Are you sure you want to delete selected invoice(s)?",
                "sel_prod_err": "Please select a product.",
                "sel_emp_err": "Please select an employee.",
                "sel_inv_err": "Please select an invoice.",
                "master_admin_err": "Cannot delete master admin.",
                "one_prod_err": "Can only update one product at a time.",
                "one_emp_err": "Can only update one employee at a time.",
                "back_btn": "← Back",
                "view_img": "View Image (Window)"
            }
        }

    def t(self, key):
        return self.texts[self.lang].get(key, key)

    def toggle(self):
        self.lang = "EN" if self.lang == "ES" else "ES"

i18n = I18n()

# ==============================================================================
# 2. CAPA DE SERVICIOS / ACCESO A DATOS (DAO)
# ==============================================================================
class DatabaseService:
    DB_PATH = "./Database/store.db"

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DB_PATH)

class Validators:
    @staticmethod
    def valid_phone(phn):
        return bool(re.match(r"^\d{7,10}$", phn))

    @staticmethod
    def valid_aadhar(aad):
        return aad.isdigit() and len(aad) == 12

    @staticmethod
    def random_emp_id(string_length=7):
        return 'EMP' + ''.join(random.choices(string.digits, k=string_length - 3))

class AuthService:
    @staticmethod
    def verify_login(emp_id, password):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT designation FROM employee WHERE emp_id = ? AND password = ?", [emp_id, password])
            res = cur.fetchone()
            return (True, res[0]) if res else (False, None)

    @staticmethod
    def reset_password(emp_id, new_pass):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT 1 FROM employee WHERE emp_id = ?", [emp_id])
            if not cur.fetchone():
                return False, "reset_not_found"
            cur.execute("UPDATE employee SET password = ? WHERE emp_id = ?", [new_pass, emp_id])
            db.commit()
            return True, "reset_ok"

class InventoryService:
    @staticmethod
    def fetch_all():
        with DatabaseService.get_connection() as db:
            return db.cursor().execute("SELECT * FROM raw_inventory").fetchall()

    @staticmethod
    def add_product(name, cat, subcat, stock, mrp, cp, vendor, image_path=""):
        with DatabaseService.get_connection() as db:
            db.cursor().execute(
                "INSERT INTO raw_inventory(product_name, product_cat, product_subcat, stock, mrp, cost_price, vendor_phn, image_path) VALUES(?,?,?,?,?,?,?,?)",
                [name, cat, subcat, stock, mrp, cp, vendor, image_path]
            )
            db.commit()

    @staticmethod
    def update_product(prod_id, name, cat, subcat, stock, mrp, cp, vendor, image_path=""):
        with DatabaseService.get_connection() as db:
            db.cursor().execute(
                "UPDATE raw_inventory SET product_name = ?, product_cat = ?, product_subcat = ?, stock = ?, mrp = ?, cost_price = ?, vendor_phn = ?, image_path = ? WHERE product_id = ?",
                [name, cat, subcat, stock, mrp, cp, vendor, image_path, prod_id]
            )
            db.commit()

    @staticmethod
    def delete_products(prod_ids):
        with DatabaseService.get_connection() as db:
            db.cursor().executemany("DELETE FROM raw_inventory WHERE product_id = ?", [(pid,) for pid in prod_ids])
            db.commit()

class EmployeeService:
    @staticmethod
    def fetch_all():
        with DatabaseService.get_connection() as db:
            return db.cursor().execute("SELECT * FROM employee").fetchall()

    @staticmethod
    def add_employee(emp_id, name, contact, add, aadhar, password, des):
        with DatabaseService.get_connection() as db:
            db.cursor().execute(
                "INSERT INTO employee VALUES(?,?,?,?,?,?,?)",
                [emp_id, name, contact, add, aadhar, password, des]
            )
            db.commit()

    @staticmethod
    def update_employee(emp_id, name, contact, add, aadhar, password, des):
        with DatabaseService.get_connection() as db:
            db.cursor().execute(
                "UPDATE employee SET name = ?, contact = ?, address = ?, aadhar_num = ?, password = ?, designation = ? WHERE emp_id = ?",
                [name, contact, add, aadhar, password, des, emp_id]
            )
            db.commit()

    @staticmethod
    def delete_employees(emp_ids):
        if "EMP1001" in emp_ids:
            return False
        with DatabaseService.get_connection() as db:
            db.cursor().executemany("DELETE FROM employee WHERE emp_id = ?", [(eid,) for eid in emp_ids])
            db.commit()
            return True

class InvoiceService:
    @staticmethod
    def fetch_all():
        with DatabaseService.get_connection() as db:
            return db.cursor().execute("SELECT bill_no, date, customer_name, customer_phone FROM bill").fetchall()

    @staticmethod
    def get_bill_details(bill_num):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT customer_name, customer_phone, date FROM bill WHERE bill_no = ?", [bill_num])
            b_info = cur.fetchone()

            cur.execute("SELECT product_name, quantity, price FROM inventory WHERE bill_no = ?", [bill_num])
            items = cur.fetchall()

        if not b_info:
            return "Factura no encontrada."

        res = f"{'='*50}\n"
        res += f" FACTURA DE VENTA  # {bill_num}\n"
        res += f"{'='*50}\n"
        res += f"Cliente:  {b_info[0]}\n"
        res += f"Teléfono: {b_info[1]}\n"
        res += f"Fecha:    {b_info[2]}\n"
        res += f"{'-'*50}\n"
        res += f"{'Producto':<25} {'Cant':<8} {'Precio':<10}\n"
        res += f"{'-'*50}\n"

        total = 0.0
        for item in items:
            p_name, qty, price = item[0], item[1], float(item[2])
            subtotal = qty * price
            total += subtotal
            res += f"{p_name[:24]:<25} {qty:<8} ${price:<9.2f}\n"

        res += f"{'='*50}\n"
        res += f" TOTAL A PAGAR: ${total:.2f}\n"
        res += f"{'='*50}\n"
        return res

    @staticmethod
    def delete_invoices(bill_nums):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.executemany("DELETE FROM bill WHERE bill_no = ?", [(b,) for b in bill_nums])
            cur.executemany("DELETE FROM inventory WHERE bill_no = ?", [(b,) for b in bill_nums])
            db.commit()

class ReportService:
    @staticmethod
    def generate_daily_csv(report_date, output_filepath):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            query = """
            SELECT b.bill_no, b.date, b.customer_name, b.customer_phone,
                   i.product_name, i.quantity, i.price, (i.quantity * i.price) as subtotal
            FROM bill b
            JOIN inventory i ON b.bill_no = i.bill_no
            WHERE b.date = ?
            """
            cur.execute(query, [report_date])
            rows = cur.fetchall()

        with open(output_filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Factura No", "Fecha", "Cliente", "Telefono", "Producto", "Cantidad", "Precio Unitario", "Subtotal"])
            writer.writerows(rows)

# ==============================================================================
# 3. COMPONENTES VISUALES Y ESTILOS
# ==============================================================================
class StyleHelper:
    PRIMARY_COLOR = "#D32F2F"
    SECONDARY_COLOR = "#F57C00"
    PANEL_BG = "#F4F5F7"

    @classmethod
    def apply_primary_button(cls, btn, text, font_size=11):
        btn.configure(
            text=text,
            font=f"-family {{Poppins}} -size {font_size} -weight bold",
            bg=cls.PRIMARY_COLOR,
            fg="#FFFFFF",
            activebackground="#B71C1C",
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            cursor="hand2"
        )

    @classmethod
    def create_header(cls, parent, title_text):
        header = tk.Frame(parent, bg=cls.PRIMARY_COLOR, height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text=title_text,
            font="-family {Poppins} -size 16 -weight bold",
            bg=cls.PRIMARY_COLOR, fg="#FFFFFF"
        ).pack(side="left", padx=20)
        return header

# ==============================================================================
# 4. VENTANA DE VISUALIZACIÓN DE IMAGEN
# ==============================================================================
class ImageViewerDialog:
    def __init__(self, parent, image_path, product_name):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Vista previa: {product_name}")
        self.top.geometry("500x550")
        self.top.configure(bg="#FFFFFF")
        self.top.resizable(False, False)

        tk.Label(
            self.top, 
            text=product_name, 
            font="-family {Poppins} -size 14 -weight bold", 
            bg="#FFFFFF", 
            fg="#212121"
        ).pack(pady=10)

        self.img_container = tk.Frame(self.top, bg="#F4F5F7", width=440, height=420, bd=1, relief="solid")
        self.img_container.pack_propagate(False)
        self.img_container.pack(pady=10)

        if image_path and os.path.exists(str(image_path)):
            try:
                raw_img = Image.open(str(image_path))
                raw_img.thumbnail((420, 400))
                self.photo = ImageTk.PhotoImage(raw_img)
                lbl_img = tk.Label(self.img_container, image=self.photo, bg="#F4F5F7")
                lbl_img.pack(expand=True)
            except Exception:
                tk.Label(self.img_container, text="Error al cargar la imagen", bg="#F4F5F7", fg="red").pack(expand=True)
        else:
            tk.Label(self.img_container, text="Sin imagen disponible", bg="#F4F5F7", fg="#757575").pack(expand=True)

# ==============================================================================
# 5. VISTAS Y PÁGINAS DE ADMINISTRACIÓN
# ==============================================================================
class LoginPage:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.geometry("1366x768")
        self.root.resizable(0, 0)
        self.root.title(i18n.t("admin_title"))

        self.canvas = tk.Canvas(self.root, width=1366, height=768, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_gradient("#D32F2F", "#F57C00")

        self.card = tk.Frame(self.root, bg="#FFFFFF", width=400, height=450)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_lang = tk.Button(self.card, text=i18n.t("lang_btn"), command=self.toggle_language, font="-family {Poppins} -size 9 -weight bold", bg="#F4F5F7", fg="#D32F2F", bd=0, cursor="hand2")
        self.btn_lang.place(x=330, y=15, width=45, height=25)

        tk.Label(self.card, text=i18n.t("admin_title"), font="-family {Poppins} -size 18 -weight bold", bg="#FFFFFF", fg="#D32F2F").place(x=40, y=35)
        tk.Label(self.card, text=i18n.t("admin_mode"), font="-family {Poppins} -size 10 -weight bold", bg="#FFFFFF", fg="#757575").place(x=40, y=70)

        tk.Label(self.card, text="Employee ID", font="-family {Poppins} -size 10", bg="#FFFFFF", fg="#212121").place(x=40, y=120)
        self.entry_user = tk.Entry(self.card, font="-family {Poppins} -size 11", bg="#F4F5F7", relief="flat")
        self.entry_user.place(x=40, y=145, width=320, height=35)

        tk.Label(self.card, text="Password", font="-family {Poppins} -size 10", bg="#FFFFFF", fg="#212121").place(x=40, y=200)
        self.entry_pass = tk.Entry(self.card, show="*", font="-family {Poppins} -size 11", bg="#F4F5F7", relief="flat")
        self.entry_pass.place(x=40, y=225, width=320, height=35)

        self.btn_forgot = tk.Button(self.card, text=i18n.t("forgot_pass"), command=self.reset_password, font="-family {Poppins} -size 9 -underline 1", bg="#FFFFFF", fg="#757575", bd=0, cursor="hand2")
        self.btn_forgot.place(x=40, y=265)

        self.btn_login = tk.Button(self.card, command=self.login)
        self.btn_login.place(x=40, y=310, width=320, height=45)
        StyleHelper.apply_primary_button(self.btn_login, i18n.t("login"), 12)

    def draw_gradient(self, color1, color2):
        r1, g1, b1 = self.root.winfo_rgb(color1)
        r2, g2, b2 = self.root.winfo_rgb(color2)
        r_ratio = (r2 - r1) / 768
        g_ratio = (g2 - g1) / 768
        b_ratio = (b2 - b1) / 768

        for i in range(768):
            nr = int(r1 + (r_ratio * i)) // 256
            ng = int(g1 + (g_ratio * i)) // 256
            nb = int(b1 + (b_ratio * i)) // 256
            self.canvas.create_line(0, i, 1366, i, fill=f"#{nr:02x}{ng:02x}{nb:02x}")

    def toggle_language(self):
        i18n.toggle()
        self.btn_lang.config(text=i18n.t("lang_btn"))
        self.btn_forgot.config(text=i18n.t("forgot_pass"))
        StyleHelper.apply_primary_button(self.btn_login, i18n.t("login"), 12)

    def login(self):
        u, p = self.entry_user.get().strip(), self.entry_pass.get().strip()
        success, role = AuthService.verify_login(u, p)

        if success:
            if role == "Admin":
                messagebox.showinfo("Success", i18n.t("login_success"), parent=self.root)
                self.on_login_success()
            else:
                messagebox.showerror("Error", i18n.t("not_admin"), parent=self.root)
        else:
            messagebox.showerror("Error", i18n.t("login_error"), parent=self.root)

    def reset_password(self):
        emp_id = simpledialog.askstring(i18n.t("reset_title"), i18n.t("reset_prompt_id"), parent=self.root)
        if not emp_id:
            return
        new_pass = simpledialog.askstring(i18n.t("reset_title"), i18n.t("reset_prompt_pass"), show="*", parent=self.root)
        if not new_pass or not new_pass.strip():
            messagebox.showerror("Error", i18n.t("reset_empty"), parent=self.root)
            return

        ok, msg_key = AuthService.reset_password(emp_id.strip(), new_pass.strip())
        if ok:
            messagebox.showinfo("OK", i18n.t(msg_key), parent=self.root)
        else:
            messagebox.showerror("Error", i18n.t(msg_key), parent=self.root)


class AdminDashboardPage:
    def __init__(self, top, app_controller):
        self.top = top
        self.app = app_controller
        self.top.geometry("1024x600")
        self.top.resizable(1, 1)
        self.top.title(f"{i18n.t('admin_title')} - Dashboard")
        self.top.configure(bg=StyleHelper.PANEL_BG)

        StyleHelper.create_header(self.top, f"{i18n.t('admin_title')} - Dashboard")

        container = tk.Frame(self.top, bg=StyleHelper.PANEL_BG)
        container.place(relx=0.5, rely=0.5, anchor="center")

        modules = [
            (i18n.t("inventory"), self.app.open_inventory),
            (i18n.t("employees"), self.app.open_employees),
            (i18n.t("invoices"), self.app.open_invoices),
            (i18n.t("reports"), self.open_reports_dialog)
        ]

        for i, (title, cmd) in enumerate(modules):
            btn = tk.Button(container, command=cmd)
            btn.grid(row=i//2, column=i%2, padx=20, pady=20, ipadx=40, ipady=30)
            StyleHelper.apply_primary_button(btn, title, 14)

        btn_logout = tk.Button(self.top, command=self.logout)
        btn_logout.place(x=1200, y=700, width=120, height=40)
        StyleHelper.apply_primary_button(btn_logout, i18n.t("logout"), 11)

    def open_reports_dialog(self):
        report_date = simpledialog.askstring(i18n.t("report_title"), "Ingrese la fecha (YYYY-MM-DD):", initialvalue=str(date.today()), parent=self.top)
        if report_date:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"report_{report_date}.csv",
                parent=self.top
            )
            if filepath:
                try:
                    ReportService.generate_daily_csv(report_date, filepath)
                    messagebox.showinfo("OK", f"{i18n.t('report_ok')}\n{filepath}", parent=self.top)
                except Exception as e:
                    messagebox.showerror("Error", f"{i18n.t('report_err')}\n{e}", parent=self.top)

    def logout(self):
        if messagebox.askyesno(i18n.t("logout"), i18n.t("confirm_logout"), parent=self.top):
            self.app.logout()


class BaseManagementPage:
    def __init__(self, top, app_controller, title_key):
        self.top = top
        self.app = app_controller
        self.top.geometry("1024x600")
        self.top.resizable(1, 1)
        self.top.title(i18n.t(title_key))
        self.top.configure(bg=StyleHelper.PANEL_BG)
        self.sel = []

        StyleHelper.create_header(self.top, i18n.t(title_key))

        self.side_panel = tk.Frame(self.top, bg="#FFFFFF", width=320)
        self.side_panel.pack(side="left", fill="y", padx=10, pady=10)

        self.main_panel = tk.Frame(self.top, bg="#FFFFFF")
        self.main_panel.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)

        self.entry_search = tk.Entry(self.side_panel, font="-family {Poppins} -size 11", bg="#F4F5F7", relief="flat")
        self.entry_search.place(relx=0.05, rely=0.03, relwidth=0.6, height=30)

        self.btn_search = tk.Button(self.side_panel, command=self.search_item)
        self.btn_search.place(relx=0.68, rely=0.03, relwidth=0.27, height=30)
        StyleHelper.apply_primary_button(self.btn_search, i18n.t("search"), 10)

        self.button_back = tk.Button(self.side_panel, command=self.exit_page)
        self.button_back.place(relx=0.05, rely=0.92, relwidth=0.4, height=35)
        StyleHelper.apply_primary_button(self.button_back, i18n.t("back_btn"), 10)

        self.button_logout = tk.Button(self.side_panel, command=self.logout)
        self.button_logout.place(relx=0.55, rely=0.92, relwidth=0.4, height=35)
        StyleHelper.apply_primary_button(self.button_logout, i18n.t("logout"), 10)

        self.setup_tree()
        self.top.protocol("WM_DELETE_WINDOW", self.exit_page)

    def setup_tree(self):
        self.tree = ttk.Treeview(self.main_panel)
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbary = ttk.Scrollbar(self.main_panel, orient="vertical", command=self.tree.yview)
        self.scrollbary.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbary.set, selectmode="extended")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_tree_select(self, event):
        self.sel = list(self.tree.selection())

    def search_item(self):
        pass

    def exit_page(self):
        self.app.return_to_admin(self.top)

    def logout(self):
        if messagebox.askyesno(i18n.t("logout"), i18n.t("confirm_logout"), parent=self.top):
            self.app.logout(self.top)

# ==============================================================================
# 6. MÓDULO DE INVENTARIO
# ==============================================================================
class InventoryPage(BaseManagementPage):
    def __init__(self, top, app_controller):
        super().__init__(top, app_controller, "inventory")

        self.tree.configure(columns=("ID", "Name", "Category", "Sub-Category", "Stock", "MRP", "Cost Price", "Vendor", "ImagePath"))
        for col in ("ID", "Name", "Category", "Sub-Category", "Stock", "MRP", "Cost Price", "Vendor"):
            self.tree.heading(col, text=col, anchor=tk.W)
        self.tree["displaycolumns"] = ("ID", "Name", "Category", "Sub-Category", "Stock", "MRP", "Cost Price", "Vendor")
        self.tree.column("#0", stretch=NO, width=0)

        self.btn_add = tk.Button(self.side_panel, command=self.add_product)
        self.btn_add.place(relx=0.05, rely=0.10, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_add, i18n.t("add_prod"), 10)

        self.btn_update = tk.Button(self.side_panel, command=self.update_product)
        self.btn_update.place(relx=0.05, rely=0.16, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_update, i18n.t("update_prod"), 10)

        self.btn_delete = tk.Button(self.side_panel, command=self.delete_product)
        self.btn_delete.place(relx=0.05, rely=0.22, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_delete, i18n.t("delete_prod"), 10)

        self.preview_frame = tk.LabelFrame(self.side_panel, text="Vista Previa", bg="#FFFFFF", font="-family {Poppins} -size 9 -weight bold")
        self.preview_frame.place(relx=0.05, rely=0.30, relwidth=0.9, height=210)

        self.lbl_preview_img = tk.Label(self.preview_frame, text="Seleccione un producto", bg="#F4F5F7", fg="#757575")
        self.lbl_preview_img.pack(fill="both", expand=True, padx=5, pady=5)

        self.btn_view_img = tk.Button(self.side_panel, command=self.open_image_viewer)
        self.btn_view_img.place(relx=0.05, rely=0.60, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_view_img, i18n.t("view_img"), 10)

        self.display_data()

    def display_data(self):
        self.tree.delete(*self.tree.get_children())
        for data in InventoryService.fetch_all():
            self.tree.insert("", "end", values=data)

    def on_tree_select(self, event):
        super().on_tree_select(event)
        if self.sel:
            values = self.tree.item(self.sel[0])["values"]
            img_path = values[8] if len(values) > 8 else ""
            self.update_image_preview(img_path)

    def update_image_preview(self, img_path):
        if img_path and os.path.exists(str(img_path)):
            try:
                raw_img = Image.open(str(img_path))
                raw_img.thumbnail((250, 160))
                self.preview_photo = ImageTk.PhotoImage(raw_img)
                self.lbl_preview_img.configure(image=self.preview_photo, text="")
            except Exception:
                self.lbl_preview_img.configure(image="", text="Imagen no válida", fg="red")
        else:
            self.lbl_preview_img.configure(image="", text="Sin Imagen", fg="#757575")

    def open_image_viewer(self):
        if not self.sel:
            messagebox.showerror("Error", i18n.t("sel_prod_err"), parent=self.top)
            return
        values = self.tree.item(self.sel[0])["values"]
        prod_name = values[1]
        img_path = values[8] if len(values) > 8 else ""
        ImageViewerDialog(self.top, img_path, prod_name)

    def search_item(self):
        to_search = self.entry_search.get().strip()
        if not to_search.isdigit():
            messagebox.showerror("Error", "ID inválido.", parent=self.top)
            return

        for item in self.tree.get_children():
            if str(self.tree.item(item)["values"][0]) == to_search:
                self.tree.selection_set(item)
                self.tree.focus(item)
                return
        messagebox.showerror("Error", f"Producto ID: {to_search} no encontrado.", parent=self.top)

    def delete_product(self):
        if not self.sel:
            messagebox.showerror("Error", i18n.t("sel_prod_err"), parent=self.top)
            return

        if messagebox.askyesno("Confirm", i18n.t("confirm_del_prod"), parent=self.top):
            to_delete = [self.tree.item(i)["values"][0] for i in self.sel]
            InventoryService.delete_products(to_delete)
            self.sel.clear()
            self.display_data()

    def add_product(self):
        AddProductDialog(tk.Toplevel(), on_complete_callback=self.display_data)

    def update_product(self):
        if len(self.sel) == 1:
            values = self.tree.item(self.sel[0])["values"]
            UpdateProductDialog(tk.Toplevel(), product_data=values, on_complete_callback=self.display_data)
        elif not self.sel:
            messagebox.showerror("Error", i18n.t("sel_prod_err"), parent=self.top)
        else:
            messagebox.showerror("Error", i18n.t("one_prod_err"), parent=self.top)

# ==============================================================================
# 7. MÓDULO DE EMPLEADOS
# ==============================================================================
class EmployeePage(BaseManagementPage):
    def __init__(self, top, app_controller):
        super().__init__(top, app_controller, "employees")

        self.tree.configure(columns=("Employee ID", "Name", "Contact", "Address", "Aadhar", "Password", "Designation"))
        for col in ("Employee ID", "Name", "Contact", "Address", "Aadhar", "Password", "Designation"):
            self.tree.heading(col, text=col, anchor=tk.W)
        self.tree.column("#0", stretch=NO, width=0)

        self.btn_add = tk.Button(self.side_panel, command=self.add_employee)
        self.btn_add.place(relx=0.05, rely=0.10, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_add, i18n.t("add_emp"), 10)

        self.btn_update = tk.Button(self.side_panel, command=self.update_employee)
        self.btn_update.place(relx=0.05, rely=0.16, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_update, i18n.t("update_emp"), 10)

        self.btn_delete = tk.Button(self.side_panel, command=self.delete_employee)
        self.btn_delete.place(relx=0.05, rely=0.22, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_delete, i18n.t("delete_emp"), 10)

        self.display_data()

    def display_data(self):
        self.tree.delete(*self.tree.get_children())
        for data in EmployeeService.fetch_all():
            self.tree.insert("", "end", values=data)

    def search_item(self):
        to_search = self.entry_search.get().strip()
        if not to_search:
            messagebox.showerror("Error", "Ingrese un ID de empleado.", parent=self.top)
            return

        for item in self.tree.get_children():
            if str(self.tree.item(item)["values"][0]).lower() == to_search.lower():
                self.tree.selection_set(item)
                self.tree.focus(item)
                return
        messagebox.showerror("Error", f"Empleado {to_search} no encontrado.", parent=self.top)

    def delete_employee(self):
        if not self.sel:
            messagebox.showerror("Error", i18n.t("sel_emp_err"), parent=self.top)
            return

        to_delete = [self.tree.item(i)["values"][0] for i in self.sel]
        if "EMP1001" in to_delete:
            messagebox.showerror("Error", i18n.t("master_admin_err"), parent=self.top)
            return

        if messagebox.askyesno("Confirm", i18n.t("confirm_del_emp"), parent=self.top):
            EmployeeService.delete_employees(to_delete)
            self.sel.clear()
            self.display_data()

    def add_employee(self):
        AddEmployeeDialog(tk.Toplevel(), on_complete_callback=self.display_data)

    def update_employee(self):
        if len(self.sel) == 1:
            values = self.tree.item(self.sel[0])["values"]
            UpdateEmployeeDialog(tk.Toplevel(), employee_data=values, on_complete_callback=self.display_data)
        elif not self.sel:
            messagebox.showerror("Error", i18n.t("sel_emp_err"), parent=self.top)
        else:
            messagebox.showerror("Error", i18n.t("one_emp_err"), parent=self.top)

# ==============================================================================
# 8. MÓDULO DE FACTURAS
# ==============================================================================
class InvoicePage(BaseManagementPage):
    def __init__(self, top, app_controller):
        super().__init__(top, app_controller, "invoices")

        self.tree.configure(columns=("Bill No", "Date", "Customer Name", "Customer Phone"))
        for col in ("Bill No", "Date", "Customer Name", "Customer Phone"):
            self.tree.heading(col, text=col, anchor=tk.W)
        self.tree.column("#0", stretch=NO, width=0)

        self.btn_view = tk.Button(self.side_panel, command=self.view_invoice)
        self.btn_view.place(relx=0.05, rely=0.10, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_view, i18n.t("view_invoice"), 10)

        self.btn_delete = tk.Button(self.side_panel, command=self.delete_invoice)
        self.btn_delete.place(relx=0.05, rely=0.16, relwidth=0.9, height=32)
        StyleHelper.apply_primary_button(self.btn_delete, i18n.t("delete_invoice"), 10)

        self.display_data()

    def display_data(self):
        self.tree.delete(*self.tree.get_children())
        for data in InvoiceService.fetch_all():
            self.tree.insert("", "end", values=data)

    def search_item(self):
        query = self.entry_search.get().strip().lower()
        all_data = InventoryService.fetch_all()
        
        # Limpiar la lista actual en pantalla
        self.tree.delete(*self.tree.get_children())
        
        # Si el campo está vacío, volver a mostrar todos los productos
        if not query:
            for data in all_data:
                self.tree.insert("", "end", values=data)
            return

        # Filtrar productos que coincidan con la búsqueda (ID, Nombre, Categoría, Subcategoría, etc.)
        matches = []
        for data in all_data:
            # Convierte todos los campos de la fila a texto para buscar coincidencias
            row_text = " ".join(str(val).lower() for val in data[:8])
            if query in row_text:
                matches.append(data)

        if matches:
            for data in matches:
                self.tree.insert("", "end", values=data)
        else:
            messagebox.showinfo("Búsqueda", f"No se encontraron productos para: '{query}'", parent=self.top)
            # Restaurar lista completa si no hay coincidencias
            for data in all_data:
                self.tree.insert("", "end", values=data)

    def view_invoice(self):
        if not self.sel:
            messagebox.showerror("Error", i18n.t("sel_inv_err"), parent=self.top)
            return
        bill_num = self.tree.item(self.sel[0])["values"][0]
        ViewInvoiceDialog(tk.Toplevel(), bill_num)

    def delete_invoice(self):
        if not self.sel:
            messagebox.showerror("Error", i18n.t("sel_inv_err"), parent=self.top)
            return

        if messagebox.askyesno("Confirm", i18n.t("confirm_del_inv"), parent=self.top):
            to_delete = [self.tree.item(i)["values"][0] for i in self.sel]
            InvoiceService.delete_invoices(to_delete)
            self.sel.clear()
            self.display_data()

# ==============================================================================
# 9. DIÁLOGOS DE PRODUCTOS Y EMPLEADOS
# ==============================================================================
class AddProductDialog:
    def __init__(self, top, on_complete_callback):
        self.top = top
        self.on_complete_callback = on_complete_callback
        self.top.geometry("520x600")
        self.top.resizable(True, True)
        self.top.title(i18n.t("add_prod"))
        self.top.configure(bg="#FFFFFF")

        self.selected_image_path = ""

        tk.Label(
            self.top, 
            text=i18n.t("add_prod"), 
            font="-family {Poppins} -size 14 -weight bold", 
            bg="#FFFFFF", 
            fg=StyleHelper.PRIMARY_COLOR
        ).pack(side="top", fill="x", pady=10)

        btn_frame = tk.Frame(self.top, bg="#FFFFFF", bd=1, relief="solid")
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.btn_add = tk.Button(btn_frame, command=self.add)
        self.btn_add.pack(side="left", padx=20, pady=10, expand=True)
        StyleHelper.apply_primary_button(self.btn_add, i18n.t("add"), 10)

        self.btn_clear = tk.Button(btn_frame, command=self.clear)
        self.btn_clear.pack(side="right", padx=20, pady=10, expand=True)
        StyleHelper.apply_primary_button(self.btn_clear, i18n.t("clear"), 10)

        canvas_container = tk.Frame(self.top, bg="#FFFFFF")
        canvas_container.pack(side="top", fill="both", expand=True, padx=10)

        canvas = tk.Canvas(canvas_container, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFFFFF")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.entries = {}
        fields = [
            ("Nombre", "name"), ("Categoría", "cat"), ("Sub-Categoría", "subcat"),
            ("Stock", "stock"), ("MRP", "mrp"), ("Precio Costo", "cp"), ("Teléfono Proveedor", "vendor")
        ]

        for label, key in fields:
            f = tk.Frame(scrollable_frame, bg="#FFFFFF")
            f.pack(fill="x", pady=5, padx=5)
            tk.Label(f, text=label, font="-family {Poppins} -size 10", bg="#FFFFFF", width=18, anchor="w").pack(side="left")
            e = tk.Entry(f, font="-family {Poppins} -size 10", bg="#F4F5F7", relief="flat")
            e.pack(side="right", fill="x", expand=True, ipady=3)
            self.entries[key] = e

        f_img = tk.Frame(scrollable_frame, bg="#FFFFFF")
        f_img.pack(fill="x", pady=5, padx=5)
        tk.Label(f_img, text="Imagen del Producto", font="-family {Poppins} -size 10", bg="#FFFFFF", width=18, anchor="w").pack(side="left")
        
        btn_select_img = tk.Button(f_img, text="Seleccionar...", command=self.select_image)
        btn_select_img.pack(side="right")
        StyleHelper.apply_primary_button(btn_select_img, "Seleccionar...", 9)

        self.lbl_img_path = tk.Label(f_img, text="Sin selección", font="-family {Poppins} -size 9 -weight italic", bg="#FFFFFF", fg="#757575", anchor="w")
        self.lbl_img_path.pack(side="left", fill="x", expand=True, padx=5)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            self.selected_image_path = file_path
            self.lbl_img_path.config(text=os.path.basename(file_path), fg="#000000")

    def save_image_file(self, source_path):
        if not source_path or not os.path.exists(source_path):
            return ""
        ext = os.path.splitext(source_path)[1]
        filename = f"prod_{random.randint(10000, 99999)}{ext}"
        dest_path = os.path.join(IMAGE_DIR, filename)
        shutil.copy(source_path, dest_path)
        return dest_path

    def clear(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.selected_image_path = ""
        self.lbl_img_path.config(text="Sin selección", fg="#757575")

    def add(self):
        d = {k: v.get().strip() for k, v in self.entries.items()}
        if not all(d.values()):
            messagebox.showerror("Error", "Campos incompletos.", parent=self.top)
            return

        try:
            cp_f, mrp_f, stock_i = float(d["cp"]), float(d["mrp"]), int(d["stock"])
        except ValueError:
            messagebox.showerror("Error", "Valores numéricos inválidos.", parent=self.top)
            return

        if not Validators.valid_phone(d["vendor"]):
            messagebox.showerror("Error", "Teléfono inválido.", parent=self.top)
            return

        final_img = self.save_image_file(self.selected_image_path)
        InventoryService.add_product(d["name"], d["cat"], d["subcat"], stock_i, mrp_f, cp_f, d["vendor"], final_img)
        self.on_complete_callback()
        self.top.destroy()


class UpdateProductDialog(AddProductDialog):
    def __init__(self, top, product_data, on_complete_callback):
        super().__init__(top, on_complete_callback)
        self.product_data = product_data
        self.top.title(i18n.t("update_prod"))

        data_mapping = [
            ("name", product_data[1]), ("cat", product_data[2]), ("subcat", product_data[3]),
            ("stock", product_data[4]), ("mrp", product_data[5]), ("cp", product_data[6]), ("vendor", product_data[7])
        ]
        for key, val in data_mapping:
            self.entries[key].insert(0, str(val))

        if len(product_data) > 8 and product_data[8]:
            self.selected_image_path = str(product_data[8])
            self.lbl_img_path.config(text=os.path.basename(self.selected_image_path), fg="#000000")

        StyleHelper.apply_primary_button(self.btn_add, i18n.t("update"), 10)
        self.btn_add.configure(command=self.update)

    def update(self):
        d = {k: v.get().strip() for k, v in self.entries.items()}
        if not all(d.values()):
            messagebox.showerror("Error", "Campos incompletos.", parent=self.top)
            return

        try:
            cp_f, mrp_f, stock_i = float(d["cp"]), float(d["mrp"]), int(d["stock"])
        except ValueError:
            messagebox.showerror("Error", "Valores numéricos inválidos.", parent=self.top)
            return

        if not Validators.valid_phone(d["vendor"]):
            messagebox.showerror("Error", "Teléfono inválido.", parent=self.top)
            return

        orig_img = self.product_data[8] if len(self.product_data) > 8 else ""
        if self.selected_image_path and self.selected_image_path != orig_img and not self.selected_image_path.startswith(IMAGE_DIR):
            final_img = self.save_image_file(self.selected_image_path)
        else:
            final_img = self.selected_image_path

        InventoryService.update_product(self.product_data[0], d["name"], d["cat"], d["subcat"], stock_i, mrp_f, cp_f, d["vendor"], final_img)
        self.on_complete_callback()
        self.top.destroy()


class AddEmployeeDialog:
    def __init__(self, top, on_complete_callback):
        self.top = top
        self.on_complete_callback = on_complete_callback
        self.top.geometry("500x520")
        self.top.resizable(False, False)
        self.top.title(i18n.t("add_emp"))
        self.top.configure(bg="#FFFFFF")

        tk.Label(self.top, text=i18n.t("add_emp"), font="-family {Poppins} -size 14 -weight bold", bg="#FFFFFF", fg=StyleHelper.PRIMARY_COLOR).pack(side="top", fill="x", pady=10)

        btn_frame = tk.Frame(self.top, bg="#FFFFFF")
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=15)

        self.btn_add = tk.Button(btn_frame, command=self.add)
        self.btn_add.pack(side="left", padx=20, expand=True)
        StyleHelper.apply_primary_button(self.btn_add, i18n.t("add"), 10)

        self.btn_clear = tk.Button(btn_frame, command=self.clear)
        self.btn_clear.pack(side="right", padx=20, expand=True)
        StyleHelper.apply_primary_button(self.btn_clear, i18n.t("clear"), 10)

        form_frame = tk.Frame(self.top, bg="#FFFFFF")
        form_frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)

        self.entries = {}
        fields = [
            ("Nombre", "name"), ("Teléfono", "contact"), ("Dirección", "add"),
            ("Aadhar/DNI (12 dig)", "aadhar"), ("Contraseña", "password")
        ]

        for label, key in fields:
            f = tk.Frame(form_frame, bg="#FFFFFF")
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label, font="-family {Poppins} -size 10", bg="#FFFFFF", width=18, anchor="w").pack(side="left")
            e = tk.Entry(f, font="-family {Poppins} -size 10", bg="#F4F5F7", relief="flat")
            e.pack(side="right", fill="x", expand=True, ipady=3)
            self.entries[key] = e

        f_des = tk.Frame(form_frame, bg="#FFFFFF")
        f_des.pack(fill="x", pady=5)
        tk.Label(f_des, text="Cargo", font="-family {Poppins} -size 10", bg="#FFFFFF", width=18, anchor="w").pack(side="left")
        self.combo_des = ttk.Combobox(f_des, values=["Employee", "Admin"], state="readonly")
        self.combo_des.current(0)
        self.combo_des.pack(side="right", fill="x", expand=True)

    def clear(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def add(self):
        d = {k: v.get().strip() for k, v in self.entries.items()}
        des = self.combo_des.get()

        if not all(d.values()):
            messagebox.showerror("Error", "Campos incompletos.", parent=self.top)
            return

        if not Validators.valid_phone(d["contact"]):
            messagebox.showerror("Error", "Teléfono inválido.", parent=self.top)
            return

        if not Validators.valid_aadhar(d["aadhar"]):
            messagebox.showerror("Error", "Aadhar/DNI debe ser de 12 dígitos.", parent=self.top)
            return

        emp_id = Validators.random_emp_id()
        EmployeeService.add_employee(emp_id, d["name"], d["contact"], d["add"], d["aadhar"], d["password"], des)
        messagebox.showinfo("Éxito", f"Empleado registrado con ID: {emp_id}", parent=self.top)
        self.on_complete_callback()
        self.top.destroy()


class UpdateEmployeeDialog(AddEmployeeDialog):
    def __init__(self, top, employee_data, on_complete_callback):
        super().__init__(top, on_complete_callback)
        self.employee_data = employee_data
        self.top.title(i18n.t("update_emp"))

        data_mapping = [
            ("name", employee_data[1]), ("contact", employee_data[2]),
            ("add", employee_data[3]), ("aadhar", employee_data[4]),
            ("password", employee_data[5])
        ]
        for key, val in data_mapping:
            self.entries[key].insert(0, str(val))

        if employee_data[6] in ["Employee", "Admin"]:
            self.combo_des.set(employee_data[6])

        StyleHelper.apply_primary_button(self.btn_add, i18n.t("update"), 10)
        self.btn_add.configure(command=self.update)

    def update(self):
        d = {k: v.get().strip() for k, v in self.entries.items()}
        des = self.combo_des.get()

        if not all(d.values()):
            messagebox.showerror("Error", "Campos incompletos.", parent=self.top)
            return

        if not Validators.valid_phone(d["contact"]):
            messagebox.showerror("Error", "Teléfono inválido.", parent=self.top)
            return

        if not Validators.valid_aadhar(d["aadhar"]):
            messagebox.showerror("Error", "Aadhar/DNI debe tener 12 dígitos.", parent=self.top)
            return

        EmployeeService.update_employee(self.employee_data[0], d["name"], d["contact"], d["add"], d["aadhar"], d["password"], des)
        self.on_complete_callback()
        self.top.destroy()


class ViewInvoiceDialog:
    def __init__(self, parent, bill_num):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Factura #{bill_num}")
        self.top.geometry("480x520")
        self.top.configure(bg="#FFFFFF")
        self.top.resizable(False, False)

        txt = tkst.ScrolledText(self.top, font="-family {Courier} -size 10", bg="#F4F5F7", relief="flat")
        txt.pack(fill="both", expand=True, padx=15, pady=15)

        content = InvoiceService.get_bill_details(bill_num)
        txt.insert(tk.END, content)
        txt.configure(state="disabled")