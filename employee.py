import sqlite3
import random
import string
import csv
from datetime import date
from time import strftime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter import scrolledtext as tkst

# ==============================================================================
# 1. CAPA DE INTERNACIONALIZACIÓN (i18n)
# ==============================================================================
class I18n:
    def __init__(self):
        self.lang = "ES"
        self.texts = {
            "ES": {
                "main_title": "Sistema de Facturación",
                "cust_details": "Detalles del Cliente",
                "bill_num_label": "Número de Factura",
                "cust_name_label": "Nombre del Cliente",
                "contact_num_label": "Teléfono de Contacto",
                "products_title": "Productos",
                "select_cat": "Seleccionar Categoría",
                "sub_cat": "Subcategoría",
                "product": "Producto",
                "quantity": "Cantidad",
                "bill_options": "Opciones de Facturación",
                "bill_window_title": "Vista de Factura",
                "login": "INGRESAR",
                "login_success": "Inicio de sesión exitoso",
                "login_error": "Usuario o contraseña incorrectos",
                "logout": "Salir",
                "confirm_logout": "¿Está seguro de que desea salir?",
                "forgot_pass": "¿Olvidó su contraseña?",
                "reset_title": "Recuperar contraseña",
                "reset_prompt_id": "Ingrese su Employee ID:",
                "reset_prompt_pass": "Ingrese la nueva contraseña:",
                "reset_ok": "Contraseña actualizada correctamente.",
                "reset_not_found": "Employee ID no encontrado.",
                "reset_empty": "Debe ingresar una contraseña válida.",
                "lang_btn": "EN",
                "search": "Buscar",
                "total": "Total",
                "generate": "Generar",
                "clear": "Limpiar",
                "clear_view": "Limpiar Vista",
                "exit": "Salir",
                "confirm_exit": "¿Está seguro de que desea salir del sistema?",
                "add_cart": "Agregar",
                "remove": "Quitar",
                "reports": "Reportes",
                "report_title": "Generar Reporte",
                "report_ok": "Reporte generado correctamente en:",
                "report_err": "No se pudo generar el reporte.",
                "in_stock": "Stock disponible: {}",
                "login_title": "Iniciar Sesión",
                "username_label": "Nombre de Usuario",
                "password_label": "Contraseña",
                "update": "ACTUALIZAR",
                "back_btn": "← Volver",
                "pay_title": "Forma de Pago",
                "pay_btn": "Pago",
                "cash": "Contado",
                "card": "Tarjeta",
                "transfer": "Yape",
                "amount_received": "Monto Recibido:",
                "change_due": "Vuelto / Cambio:",
                "ref_num": "N° de Referencia / Operación:",
                "confirm_pay": "CONFIRMAR PAGO",
                "pay_success": "Pago procesado y factura generada con éxito.",
                "insufficient_cash": "El monto recibido es menor al total.",
                "missing_ref": "Por favor ingrese el número de referencia/operación."
            },
            "EN": {
                "main_title": "Billing System",
                "cust_details": "Customer Details",
                "bill_num_label": "Bill Number",
                "cust_name_label": "Customer Name",
                "contact_num_label": "Contact Number",
                "products_title": "Products",
                "select_cat": "Select Category",
                "sub_cat": "Sub Category",
                "product": "Product",
                "quantity": "Quantity",
                "bill_options": "Bill Options",
                "bill_window_title": "Bill Window",
                "login": "LOGIN",
                "login_success": "The login is successful",
                "login_error": "Incorrect username or password.",
                "logout": "Logout",
                "confirm_logout": "Are you sure you want to logout?",
                "forgot_pass": "Forgot your password?",
                "reset_title": "Recover password",
                "reset_prompt_id": "Enter your Employee ID:",
                "reset_prompt_pass": "Enter the new password:",
                "reset_ok": "Password updated successfully.",
                "reset_not_found": "Employee ID not found.",
                "reset_empty": "You must enter a valid password.",
                "lang_btn": "ES",
                "search": "Search",
                "total": "Total",
                "generate": "Generate",
                "clear": "Clear",
                "clear_view": "Clear View",
                "exit": "Exit",
                "confirm_exit": "Are you sure you want to exit?",
                "add_cart": "Add To Cart",
                "remove": "Remove",
                "reports": "Reports",
                "report_title": "Generate Report",
                "report_ok": "Report generated successfully at:",
                "report_err": "Could not generate the report.",
                "in_stock": "In Stock: {}",
                "login_title": "Login",
                "username_label": "Username",
                "password_label": "Password",
                "update": "UPDATE",
                "back_btn": "← Back",
                "pay_title": "Payment Method",
                "pay_btn": "Payment",
                "cash": "Cash",
                "card": "Card",
                "transfer": "Transfer",
                "amount_received": "Amount Received:",
                "change_due": "Change Due:",
                "ref_num": "Ref / Operation No:",
                "confirm_pay": "CONFIRM PAYMENT",
                "pay_success": "Payment processed and bill generated successfully.",
                "insufficient_cash": "Amount received is less than total.",
                "missing_ref": "Please enter the reference/operation number."
            }
        }

    def t(self, key):
        return self.texts[self.lang].get(key, key)

    def toggle(self):
        self.lang = "EN" if self.lang == "ES" else "ES"

i18n = I18n()

# ==============================================================================
# 2. CAPA DE MODELOS Y NEGOCIO
# ==============================================================================
class Item:
    def __init__(self, name, price, qty):
        self.product_name = name
        self.price = price
        self.qty = qty

class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self):
        if self.items:
            self.items.pop()

    def remove_items(self):
        self.items.clear()

    def total(self):
        return sum(i.price * i.qty for i in self.items)

    def is_empty(self):
        return len(self.items) == 0

    def get_summary_dictionary(self):
        summary = {}
        for i in self.items:
            summary[i.product_name] = summary.get(i.product_name, 0) + i.qty
        return summary

# ==============================================================================
# 3. CAPA DE SERVICIOS / ACCESO A DATOS (DAO)
# ==============================================================================
class DatabaseService:
    DB_PATH = "./Database/store.db"

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DB_PATH)

class AuthService:
    @staticmethod
    def verify_login(emp_id, password):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM employee WHERE emp_id = ? AND password = ?", [emp_id, password])
            return cur.fetchone() is not None

    @staticmethod
    def reset_password(emp_id, new_pass):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM employee WHERE emp_id = ?", [emp_id])
            if not cur.fetchone():
                return False, "reset_not_found"
            cur.execute("UPDATE employee SET password = ? WHERE emp_id = ?", [new_pass, emp_id])
            db.commit()
            return True, "reset_ok"

class InventoryService:
    @staticmethod
    def get_categories():
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT DISTINCT product_cat FROM raw_inventory")
            return [row[0] for row in cur.fetchall()]

    @staticmethod
    def get_subcategories(category):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT DISTINCT product_subcat FROM raw_inventory WHERE product_cat = ?", [category])
            return [row[0] for row in cur.fetchall()]

    @staticmethod
    def get_products(category, subcategory):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT product_name FROM raw_inventory WHERE product_cat = ? AND product_subcat = ?", [category, subcategory])
            return [row[0] for row in cur.fetchall()]

    @staticmethod
    def get_product_info(product_name):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT mrp, stock FROM raw_inventory WHERE product_name = ?", [product_name])
            row = cur.fetchone()
            return {"mrp": row[0], "stock": row[1]} if row else None

class BillingService:
    @staticmethod
    def generate_bill_number(length=8):
        chars = string.ascii_uppercase + string.digits
        return 'BB' + ''.join(random.choice(chars) for _ in range(length - 2))

    @staticmethod
    def save_bill_and_update_stock(cust_name, cust_num, bill_details, cart_summary):
        bill_no = BillingService.generate_bill_number()
        today = str(date.today())
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO bill(bill_no, date, customer_name, customer_no, bill_details) VALUES(?,?,?,?,?)",
                [bill_no, today, cust_name, cust_num, bill_details]
            )
            for name, qty in cart_summary.items():
                cur.execute("UPDATE raw_inventory SET stock = stock - ? WHERE product_name = ?", [qty, name])
            db.commit()
        return bill_no

    @staticmethod
    def find_bill(bill_no):
        with DatabaseService.get_connection() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM bill WHERE bill_no = ?", [bill_no.strip()])
            return cur.fetchone()

# ==============================================================================
# 4. ESTILOS Y HELPERS
# ==============================================================================
class StyleHelper:
    @staticmethod
    def apply_primary_button(btn, text, font_size=9):
        btn.configure(
            relief="flat", overrelief="flat", activebackground="#CF1E14",
            cursor="hand2", fg="#ffffff", bg="#CF1E14",
            font=f"-family {{Poppins SemiBold}} -size {font_size}",
            borderwidth=0, text=text
        )

# ==============================================================================
# 5. VISTAS DE LA INTERFAZ
# ==============================================================================
class ForgotPasswordPage:
    def __init__(self, top, on_back_callback):
        self.top = top
        self.on_back_callback = on_back_callback
        self.top.geometry("1366x768")
        self.top.resizable(0, 0)
        self.top.title(i18n.t("reset_title"))

        self.reset_user = tk.StringVar()
        self.reset_pass = tk.StringVar()

        self.bg_frame = tk.Frame(self.top, bg="#FF7F66")
        self.bg_frame.place(relx=0, rely=0, width=1366, height=768)

        self.button_lang = tk.Button(self.top, command=self.toggle_lang)
        self.button_lang.place(relx=0.92, rely=0.03, width=60, height=30)
        StyleHelper.apply_primary_button(self.button_lang, i18n.t("lang_btn"), 10)

        self.card = tk.Frame(self.top, bg="#ffffff", bd=0)
        self.card.place(relx=0.33, rely=0.08, relwidth=0.34, relheight=0.84)

        self.lbl_title = tk.Label(self.card, text=i18n.t("reset_title"), font="-family {Poppins} -size 20 -weight bold", bg="#ffffff", fg="#000000")
        self.lbl_title.place(relx=0.5, rely=0.12, anchor="center")

        self.lbl_user_title = tk.Label(self.card, text=i18n.t("reset_prompt_id").replace(":", ""), font="-family {Poppins} -size 10", bg="#ffffff", fg="#666666", anchor="w")
        self.lbl_user_title.place(relx=0.12, rely=0.25)

        self.lbl_user_icon = tk.Label(self.card, text="👤", font="-family {Segoe UI Emoji} -size 11", bg="#ffffff", fg="#333333")
        self.lbl_user_icon.place(relx=0.12, rely=0.30)

        self.entry_user = tk.Entry(self.card, textvariable=self.reset_user, font="-family {Poppins} -size 10", relief="flat", bd=0)
        self.entry_user.place(relx=0.18, rely=0.30, relwidth=0.70, height=25)

        self.line1 = tk.Frame(self.card, bg="#CCCCCC", height=1)
        self.line1.place(relx=0.12, rely=0.35, relwidth=0.76)

        self.lbl_pass_title = tk.Label(self.card, text=i18n.t("reset_prompt_pass").replace(":", ""), font="-family {Poppins} -size 10", bg="#ffffff", fg="#666666", anchor="w")
        self.lbl_pass_title.place(relx=0.12, rely=0.40)

        self.lbl_pass_icon = tk.Label(self.card, text="🔑", font="-family {Segoe UI Emoji} -size 11", bg="#ffffff", fg="#333333")
        self.lbl_pass_icon.place(relx=0.12, rely=0.45)

        self.entry_pass = tk.Entry(self.card, textvariable=self.reset_pass, show="*", font="-family {Poppins} -size 10", relief="flat", bd=0)
        self.entry_pass.place(relx=0.18, rely=0.45, relwidth=0.70, height=25)

        self.line2 = tk.Frame(self.card, bg="#CCCCCC", height=1)
        self.line2.place(relx=0.12, rely=0.50, relwidth=0.76)

        self.button_reset = tk.Button(self.card, command=self.process_reset)
        self.button_reset.place(relx=0.12, rely=0.64, relwidth=0.76, height=45)
        StyleHelper.apply_primary_button(self.button_reset, i18n.t("update"), 12)

        self.button_back = tk.Button(self.card, command=self.go_back)
        self.button_back.place(relx=0.12, rely=0.73, relwidth=0.76, height=35)
        self.button_back.configure(
            relief="flat", overrelief="flat", activebackground="#f0f0f0", cursor="hand2",
            fg="#666666", bg="#ffffff", font="-family {Poppins} -size 10", borderwidth=0, text=i18n.t("back_btn")
        )

    def toggle_lang(self):
        i18n.toggle()
        self.update_ui_language()

    def process_reset(self):
        emp_id = self.reset_user.get().strip()
        new_pass = self.reset_pass.get().strip()

        if not emp_id or not new_pass:
            messagebox.showwarning("Error", i18n.t("reset_empty"), parent=self.top)
            return

        success, msg_key = AuthService.reset_password(emp_id, new_pass)
        if success:
            messagebox.showinfo("OK", i18n.t(msg_key), parent=self.top)
            self.go_back()
        else:
            messagebox.showerror("Error", i18n.t(msg_key), parent=self.top)

    def go_back(self):
        self.top.destroy()
        self.on_back_callback()

    def update_ui_language(self):
        self.button_lang.configure(text=i18n.t("lang_btn"))
        self.lbl_title.configure(text=i18n.t("reset_title"))
        self.lbl_user_title.configure(text=i18n.t("reset_prompt_id").replace(":", ""))
        self.lbl_pass_title.configure(text=i18n.t("reset_prompt_pass").replace(":", ""))
        self.button_reset.configure(text=i18n.t("update"))
        self.button_back.configure(text=i18n.t("back_btn"))



class PaymentPage:
    def __init__(self, top, total_amount, on_success_callback):
        self.top = top
        self.total_amount = total_amount
        self.on_success_callback = on_success_callback

        self.top.geometry("480x560")
        self.top.resizable(0, 0)
        self.top.title(i18n.t("pay_title"))
        self.top.configure(bg="#ffffff")
        self.top.grab_set()

        self.pay_method_var = tk.StringVar(value="Contado")
        self.cash_amount_var = tk.StringVar(value="0.00")
        self.transfer_amount_var = tk.StringVar(value="0.00")
        self.change_var = tk.StringVar(value="0.00")
        self.ref_var = tk.StringVar()

        self.lbl_title = tk.Label(self.top, text=i18n.t("pay_title"), font="-family {Poppins} -size 16 -weight bold", bg="#ffffff", fg="#D2463E")
        self.lbl_title.pack(pady=(15, 5))

        self.lbl_total = tk.Label(self.top, text=f"Total Factura: S/. {self.total_amount:.2f}", font="-family {Poppins SemiBold} -size 14", bg="#ffffff", fg="#333333")
        self.lbl_total.pack(pady=(0, 10))

        self.frame_methods = tk.Frame(self.top, bg="#ffffff")
        self.frame_methods.pack(pady=5)

        self.rb_cash = tk.Radiobutton(self.frame_methods, text="Contado", value="Contado", variable=self.pay_method_var, bg="#ffffff", command=self.on_method_change)
        self.rb_cash.grid(row=0, column=0, padx=5)

        self.rb_transfer = tk.Radiobutton(self.frame_methods, text="Transferencia/Yape", value="Transferencia", variable=self.pay_method_var, bg="#ffffff", command=self.on_method_change)
        self.rb_transfer.grid(row=0, column=1, padx=5)

        self.rb_mixed = tk.Radiobutton(self.frame_methods, text="Mixto", value="Mixto", variable=self.pay_method_var, bg="#ffffff", command=self.on_method_change)
        self.rb_mixed.grid(row=0, column=2, padx=5)

        self.frame_details = tk.Frame(self.top, bg="#ffffff")
        self.frame_details.pack(fill="x", padx=40, pady=10)

        # Campos de entrada
        self.lbl_cash = tk.Label(self.frame_details, text="Monto en Efectivo:", bg="#ffffff")
        self.entry_cash = tk.Entry(self.frame_details, textvariable=self.cash_amount_var, bd=1, relief="solid")
        self.cash_amount_var.trace_add("write", self.calculate_totals)

        self.lbl_transfer = tk.Label(self.frame_details, text="Monto en Transferencia:", bg="#ffffff")
        self.entry_transfer = tk.Entry(self.frame_details, textvariable=self.transfer_amount_var, bd=1, relief="solid")
        self.transfer_amount_var.trace_add("write", self.calculate_totals)

        self.lbl_ref = tk.Label(self.frame_details, text="N° Operación / Referencia:", bg="#ffffff")
        self.entry_ref = tk.Entry(self.frame_details, textvariable=self.ref_var, bd=1, relief="solid")

        self.lbl_change_title = tk.Label(self.frame_details, text="Vuelto / Cambio:", bg="#ffffff")
        self.lbl_change_val = tk.Label(self.frame_details, textvariable=self.change_var, font="-family {Poppins SemiBold} -size 11", bg="#ffffff", fg="#2E7D32")

        self.on_method_change()

        self.btn_confirm = tk.Button(self.top, command=self.process_payment)
        self.btn_confirm.pack(side="bottom", pady=20, ipady=5)
        StyleHelper.apply_primary_button(self.btn_confirm, "CONFIRMAR PAGO", 11)

    def on_method_change(self):
        method = self.pay_method_var.get()
        for w in self.frame_details.winfo_children():
            w.pack_forget()

        if method == "Contado":
            self.lbl_cash.pack(fill="x", pady=2)
            self.entry_cash.pack(fill="x", pady=(0, 5))
            self.lbl_change_title.pack(fill="x", pady=2)
            self.lbl_change_val.pack(fill="x", pady=(0, 5))
            self.transfer_amount_var.set("0.00")
        elif method == "Transferencia":
            self.lbl_transfer.pack(fill="x", pady=2)
            self.entry_transfer.pack(fill="x", pady=(0, 5))
            self.lbl_ref.pack(fill="x", pady=2)
            self.entry_ref.pack(fill="x", pady=(0, 5))
            self.cash_amount_var.set("0.00")
            self.transfer_amount_var.set(f"{self.total_amount:.2f}")
        else: # Pago Mixto
            self.lbl_cash.pack(fill="x", pady=2)
            self.entry_cash.pack(fill="x", pady=(0, 5))
            self.lbl_transfer.pack(fill="x", pady=2)
            self.entry_transfer.pack(fill="x", pady=(0, 5))
            self.lbl_ref.pack(fill="x", pady=2)
            self.entry_ref.pack(fill="x", pady=(0, 5))
            self.lbl_change_title.pack(fill="x", pady=2)
            self.lbl_change_val.pack(fill="x", pady=(0, 5))

    def calculate_totals(self, *args):
        try:
            cash = float(self.cash_amount_var.get() or 0.0)
            transfer = float(self.transfer_amount_var.get() or 0.0)
            total_paid = cash + transfer
            change = total_paid - self.total_amount
            self.change_var.set(f"S/. {max(0.0, change):.2f}")
        except ValueError:
            self.change_var.set("S/. 0.00")

    def process_payment(self):
        try:
            cash = float(self.cash_amount_var.get() or 0.0)
            transfer = float(self.transfer_amount_var.get() or 0.0)
        except ValueError:
            messagebox.showerror("Error", "Ingrese montos numéricos válidos.", parent=self.top)
            return

        method = self.pay_method_var.get()

        # RESTRICCIONES Y VALIDACIONES
        if cash < 0 or transfer < 0:
            messagebox.showerror("Error", "Los montos no pueden ser negativos.", parent=self.top)
            return

        if method == "Transferencia" and not self.ref_var.get().strip():
            messagebox.showerror("Error", "Ingrese el número de referencia/operación.", parent=self.top)
            return

        if method == "Mixto":
            if not self.ref_var.get().strip() and transfer > 0:
                messagebox.showerror("Error", "Ingrese el número de referencia para el pago por transferencia.", parent=self.top)
                return
            if (cash + transfer) < self.total_amount:
                messagebox.showerror("Error", f"El total ingresado (S/. {cash + transfer:.2f}) no cubre el total de la factura (S/. {self.total_amount:.2f}).", parent=self.top)
                return

        if method == "Contado" and cash < self.total_amount:
            messagebox.showerror("Error", "El monto ingresado en efectivo es menor al total.", parent=self.top)
            return

        # Restricción: No permitir abonar más por transferencia de lo que vale la factura
        if transfer > self.total_amount:
            messagebox.showerror("Error", "El monto por transferencia no puede superar el total de la factura.", parent=self.top)
            return

        # Detalle para la base de datos y reporte
        pay_info = f"\n[FORMA DE PAGO: {method}]\n- Efectivo: S/. {cash:.2f}\n- Transferencia: S/. {transfer:.2f}"
        if self.ref_var.get().strip():
            pay_info += f"\n- Ref/Op: {self.ref_var.get().strip()}"
        pay_info += f"\n- Cambio: {self.change_var.get()}"

        self.top.destroy()
        self.on_success_callback(pay_info)

class LoginPage:
    def __init__(self, top, on_login_success):
        self.top = top
        self.on_login_success = on_login_success
        self.top.geometry("1366x768")
        self.top.resizable(0, 0)
        self.top.title("Retail Manager")

        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()

        self.bg_frame = tk.Frame(self.top, bg="#FF7F66")
        self.bg_frame.place(relx=0, rely=0, width=1366, height=768)

        self.button_lang = tk.Button(self.top, command=self.toggle_lang)
        self.button_lang.place(relx=0.92, rely=0.03, width=60, height=30)
        StyleHelper.apply_primary_button(self.button_lang, i18n.t("lang_btn"), 10)

        self.card = tk.Frame(self.top, bg="#ffffff", bd=0)
        self.card.place(relx=0.33, rely=0.08, relwidth=0.34, relheight=0.84)

        self.lbl_title = tk.Label(self.card, text=i18n.t("login_title"), font="-family {Poppins} -size 28 -weight bold", bg="#ffffff", fg="#000000")
        self.lbl_title.place(relx=0.5, rely=0.12, anchor="center")

        self.lbl_user_title = tk.Label(self.card, text=i18n.t("username_label"), font="-family {Poppins} -size 10", bg="#ffffff", fg="#666666", anchor="w")
        self.lbl_user_title.place(relx=0.12, rely=0.25)

        self.lbl_user_icon = tk.Label(self.card, text="👤", font="-family {Segoe UI Emoji} -size 11", bg="#ffffff", fg="#333333")
        self.lbl_user_icon.place(relx=0.12, rely=0.30)

        self.entry1 = tk.Entry(self.card, textvariable=self.user_var, font="-family {Poppins} -size 10", relief="flat", bd=0)
        self.entry1.place(relx=0.18, rely=0.30, relwidth=0.70, height=25)

        self.line1 = tk.Frame(self.card, bg="#CCCCCC", height=1)
        self.line1.place(relx=0.12, rely=0.35, relwidth=0.76)

        self.lbl_pass_title = tk.Label(self.card, text=i18n.t("password_label"), font="-family {Poppins} -size 10", bg="#ffffff", fg="#666666", anchor="w")
        self.lbl_pass_title.place(relx=0.12, rely=0.40)

        self.lbl_pass_icon = tk.Label(self.card, text="🔒", font="-family {Segoe UI Emoji} -size 11", bg="#ffffff", fg="#333333")
        self.lbl_pass_icon.place(relx=0.12, rely=0.45)

        self.entry2 = tk.Entry(self.card, textvariable=self.pass_var, show="*", font="-family {Poppins} -size 10", relief="flat", bd=0)
        self.entry2.place(relx=0.18, rely=0.45, relwidth=0.70, height=25)

        self.line2 = tk.Frame(self.card, bg="#CCCCCC", height=1)
        self.line2.place(relx=0.12, rely=0.50, relwidth=0.76)

        self.button1 = tk.Button(self.card, command=self.handle_login)
        self.button1.place(relx=0.12, rely=0.68, relwidth=0.76, height=45)
        StyleHelper.apply_primary_button(self.button1, i18n.t("login"), 14)

        self.button_forgot = tk.Button(self.card, command=self.forgot_password)
        self.button_forgot.place(relx=0.12, rely=0.76, relwidth=0.76, height=25)
        self.button_forgot.configure(
            relief="flat", overrelief="flat", activebackground="#ffffff", cursor="hand2",
            fg="#D2463E", bg="#ffffff", font="-family {Poppins} -size 9", borderwidth=0, text=i18n.t("forgot_pass")
        )

        self.top.bind("<Return>", lambda e: self.handle_login())

    def toggle_lang(self):
        i18n.toggle()
        self.update_ui_language()

    def handle_login(self):
        username = self.user_var.get()
        password = self.pass_var.get()
        if AuthService.verify_login(username, password):
            messagebox.showinfo("Login", i18n.t("login_success"))
            self.entry1.delete(0, tk.END)
            self.entry2.delete(0, tk.END)
            self.on_login_success(username)
        else:
            messagebox.showerror("Error", i18n.t("login_error"))
            self.entry2.delete(0, tk.END)

    def update_ui_language(self):
        self.button_lang.configure(text=i18n.t("lang_btn"))
        self.lbl_title.configure(text=i18n.t("login_title"))
        self.lbl_user_title.configure(text=i18n.t("username_label"))
        self.lbl_pass_title.configure(text=i18n.t("password_label"))
        self.button1.configure(text=i18n.t("login"))
        self.button_forgot.configure(text=i18n.t("forgot_pass"))

    def forgot_password(self):
        self.top.withdraw()
        reset_win = tk.Toplevel()
        reset_page = ForgotPasswordPage(reset_win, on_back_callback=self.top.deiconify)
        reset_win.protocol("WM_DELETE_WINDOW", reset_page.go_back)

class BillWindow:
    def __init__(self, top, username, on_logout_callback):
        self.top = top
        self.username = username
        self.on_logout_callback = on_logout_callback

        self.top.geometry("1366x768")
        self.top.resizable(0, 0)
        self.top.title("Retail Manager")
        self.top.configure(background="#f4f4f4")

        self.cart = Cart()
        self.cust_name = tk.StringVar()
        self.cust_num = tk.StringVar()
        self.cust_search_bill = tk.StringVar()

        self._build_ui()
        self.load_categories()
        self.update_time()
        self.update_ui_language()

    def _build_ui(self):
        # Encabezado Superior
        self.top_frame = tk.Frame(self.top, bg="#f4f4f4")
        self.top_frame.place(relx=0, rely=0, width=1366, height=100)

        self.main_title = tk.Label(self.top_frame, font="-family {Poppins Bold} -size 28", bg="#f4f4f4", fg="#333333")
        self.main_title.place(relx=0.35, rely=0.2)

        self.message = tk.Label(self.top_frame, font="-family {Poppins} -size 10", fg="#000000", bg="#ffffff", text=self.username, anchor="w")
        self.message.place(relx=0.038, rely=0.55, width=136, height=30)

        self.clock = tk.Label(self.top_frame, font="-family {Poppins Light} -size 12", fg="#000000", bg="#ffffff")
        self.clock.place(relx=0.85, rely=0.55, width=120, height=30)

        self.button_lang = tk.Button(self.top_frame, command=self.toggle_lang)
        self.button_lang.place(relx=0.94, rely=0.15, width=50, height=25)
        self.button_lang.configure(relief="flat", activebackground="#CF1E14", cursor="hand2", fg="#ffffff", bg="#333333", font="-family {Poppins SemiBold} -size 10", text=i18n.t("lang_btn"))

        self.btn_logout = tk.Button(self.top_frame, command=self.logout)
        self.btn_logout.place(relx=0.038, rely=0.15, width=76, height=25)
        StyleHelper.apply_primary_button(self.btn_logout, i18n.t("logout"), 10)

        # Sección de Detalles de Cliente
        self.frame_cust = tk.LabelFrame(self.top, font="-family {Poppins SemiBold} -size 11", bg="#ffffff")
        self.frame_cust.place(relx=0.03, rely=0.13, width=1290, height=80)

        self.lbl_bill_search = tk.Label(self.frame_cust, font="-family {Poppins} -size 9", bg="#ffffff")
        self.lbl_bill_search.place(relx=0.02, rely=0.1)
        self.entry_search = tk.Entry(self.frame_cust, font="-family {Poppins} -size 10", textvariable=self.cust_search_bill, bd=1, relief="solid")
        self.entry_search.place(relx=0.02, rely=0.45, width=180, height=25)

        self.btn_search = tk.Button(self.frame_cust, command=self.search_bill)
        self.btn_search.place(relx=0.17, rely=0.43, width=80, height=27)
        StyleHelper.apply_primary_button(self.btn_search, i18n.t("search"), 9)

        self.lbl_cust_name = tk.Label(self.frame_cust, font="-family {Poppins} -size 9", bg="#ffffff")
        self.lbl_cust_name.place(relx=0.35, rely=0.1)
        self.entry_name = tk.Entry(self.frame_cust, font="-family {Poppins} -size 10", textvariable=self.cust_name, bd=1, relief="solid")
        self.entry_name.place(relx=0.35, rely=0.45, width=280, height=25)

        self.lbl_cust_num = tk.Label(self.frame_cust, font="-family {Poppins} -size 9", bg="#ffffff")
        self.lbl_cust_num.place(relx=0.68, rely=0.1)
        self.entry_phone = tk.Entry(self.frame_cust, font="-family {Poppins} -size 10", textvariable=self.cust_num, bd=1, relief="solid")
        self.entry_phone.place(relx=0.68, rely=0.45, width=280, height=25)

        # Sección de Productos
        self.frame_prod = tk.LabelFrame(self.top, font="-family {Poppins SemiBold} -size 11", bg="#ffffff")
        self.frame_prod.place(relx=0.03, rely=0.25, width=520, height=430)

        self.lbl_cat = tk.Label(self.frame_prod, font="-family {Poppins} -size 9", bg="#ffffff")
        self.lbl_cat.place(relx=0.05, rely=0.03)
        self.combo1 = ttk.Combobox(self.frame_prod, font="-family {Poppins} -size 9", state="readonly")
        self.combo1.place(relx=0.05, rely=0.1, width=460, height=26)

        self.lbl_subcat = tk.Label(self.frame_prod, font="-family {Poppins} -size 9", bg="#ffffff")
        self.lbl_subcat.place(relx=0.05, rely=0.23)
        self.combo2 = ttk.Combobox(self.frame_prod, font="-family {Poppins} -size 9", state="disabled")
        self.combo2.place(relx=0.05, rely=0.3, width=460, height=26)

        self.lbl_product = tk.Label(self.frame_prod, font="-family {Poppins} -size 9", bg="#ffffff")
        self.lbl_product.place(relx=0.05, rely=0.43)
        self.combo3 = ttk.Combobox(self.frame_prod, font="-family {Poppins} -size 9", state="disabled")
        self.combo3.place(relx=0.05, rely=0.5, width=460, height=26)

        self.lbl_qty = tk.Label(self.frame_prod, font="-family {Poppins} -size 9", bg="#ffffff")
        self.lbl_qty.place(relx=0.05, rely=0.63)
        self.entry_qty = ttk.Entry(self.frame_prod, font="-family {Poppins} -size 9", state="disabled")
        self.entry_qty.place(relx=0.05, rely=0.7, width=460, height=26)

        self.qty_label = tk.Label(self.frame_prod, font="-family {Poppins} -size 8", bg="#ffffff", fg="#333333", anchor="w")
        self.qty_label.place(relx=0.05, rely=0.78, width=200, height=20)

        self.btn_add = tk.Button(self.frame_prod, command=self.add_to_cart)
        self.btn_add.place(relx=0.1, rely=0.86, width=100, height=28)
        StyleHelper.apply_primary_button(self.btn_add, i18n.t("add_cart"), 9)

        self.btn_remove = tk.Button(self.frame_prod, command=self.remove_product)
        self.btn_remove.place(relx=0.38, rely=0.86, width=100, height=28)
        StyleHelper.apply_primary_button(self.btn_remove, i18n.t("remove"), 9)

        self.btn_clear_prod = tk.Button(self.frame_prod, command=self.clear_selection)
        self.btn_clear_prod.place(relx=0.66, rely=0.86, width=100, height=28)
        StyleHelper.apply_primary_button(self.btn_clear_prod, i18n.t("clear"), 9)

        # Sección de Opciones Generales
        self.frame_opts = tk.LabelFrame(self.top, font="-family {Poppins SemiBold} -size 11", bg="#ffffff")
        self.frame_opts.place(relx=0.03, rely=0.82, width=520, height=100)

        self.btn_total = tk.Button(self.frame_opts, command=self.total_bill)
        self.btn_total.place(relx=0.02, rely=0.25, width=70, height=28)
        StyleHelper.apply_primary_button(self.btn_total, i18n.t("total"), 9)

        self.btn_pay = tk.Button(self.frame_opts, command=self.open_payment_window)
        self.btn_pay.place(relx=0.18, rely=0.25, width=75, height=28)
        StyleHelper.apply_primary_button(self.btn_pay, i18n.t("pay_btn"), 9)

        self.btn_gen = tk.Button(self.frame_opts, command=self.gen_bill)
        self.btn_gen.place(relx=0.35, rely=0.25, width=80, height=28)
        StyleHelper.apply_primary_button(self.btn_gen, i18n.t("generate"), 9)

        self.btn_clear = tk.Button(self.frame_opts, command=self.clear_bill)
        self.btn_clear.place(relx=0.53, rely=0.25, width=70, height=28)
        StyleHelper.apply_primary_button(self.btn_clear, i18n.t("clear"), 9)

        self.btn_exit = tk.Button(self.frame_opts, command=self.exit_app)
        self.btn_exit.place(relx=0.69, rely=0.25, width=70, height=28)
        StyleHelper.apply_primary_button(self.btn_exit, i18n.t("exit"), 9)

        self.btn_reports = tk.Button(self.frame_opts, command=self.generate_report)
        self.btn_reports.place(relx=0.85, rely=0.25, width=75, height=28)
        StyleHelper.apply_primary_button(self.btn_reports, i18n.t("reports"), 9)

        # Panel de Vista Previa de Factura
        self.frame_bill = tk.LabelFrame(self.top, font="-family {Poppins SemiBold} -size 11", bg="#ffffff")
        self.frame_bill.place(relx=0.42, rely=0.25, width=760, height=535)

        self.btn_clear_view = tk.Button(self.frame_bill, command=self.clear_bill_text)
        self.btn_clear_view.place(relx=0.82, rely=0.02, width=110, height=25)
        StyleHelper.apply_primary_button(self.btn_clear_view, i18n.t("clear_view"), 9)

        self.Scrolledtext1 = tkst.ScrolledText(self.frame_bill, font="-family {Podkova} -size 9", bd=0, state="disabled")
        self.Scrolledtext1.place(relx=0.02, rely=0.08, width=720, height=450)

    def load_categories(self):
        categories = InventoryService.get_categories()
        self.combo1.configure(values=categories)
        self.combo1.bind("<<ComboboxSelected>>", self.get_category)

    def toggle_lang(self):
        i18n.toggle()
        self.update_ui_language()

    def update_ui_language(self):
        self.main_title.configure(text=i18n.t("main_title"))
        self.frame_cust.configure(text=i18n.t("cust_details"))
        self.lbl_bill_search.configure(text=i18n.t("bill_num_label"))
        self.lbl_cust_name.configure(text=i18n.t("cust_name_label"))
        self.lbl_cust_num.configure(text=i18n.t("contact_num_label"))

        self.frame_prod.configure(text=i18n.t("products_title"))
        self.lbl_cat.configure(text=i18n.t("select_cat"))
        self.lbl_subcat.configure(text=i18n.t("sub_cat"))
        self.lbl_product.configure(text=i18n.t("product"))
        self.lbl_qty.configure(text=i18n.t("quantity"))

        self.frame_opts.configure(text=i18n.t("bill_options"))
        self.frame_bill.configure(text=i18n.t("bill_window_title"))

        self.button_lang.configure(text=i18n.t("lang_btn"))
        self.btn_logout.configure(text=i18n.t("logout"))
        self.btn_search.configure(text=i18n.t("search"))
        self.btn_total.configure(text=i18n.t("total"))
        self.btn_pay.configure(text=i18n.t("pay_btn"))
        self.btn_gen.configure(text=i18n.t("generate"))
        self.btn_clear.configure(text=i18n.t("clear"))
        self.btn_exit.configure(text=i18n.t("exit"))
        self.btn_add.configure(text=i18n.t("add_cart"))
        self.btn_clear_prod.configure(text=i18n.t("clear"))
        self.btn_remove.configure(text=i18n.t("remove"))
        self.btn_reports.configure(text=i18n.t("reports"))
        self.btn_clear_view.configure(text=i18n.t("clear_view"))

        if self.combo3.get():
            self.show_qty(None)

    def clear_bill_text(self):
        self.Scrolledtext1.configure(state="normal")
        self.Scrolledtext1.delete('1.0', tk.END)
        self.Scrolledtext1.configure(state="disabled")
        self.cart.remove_items()

    def get_category(self, event):
        self.combo2.configure(state="readonly")
        self.combo2.set('')
        self.combo3.set('')
        subcats = InventoryService.get_subcategories(self.combo1.get())
        self.combo2.configure(values=subcats)
        self.combo2.bind("<<ComboboxSelected>>", self.get_subcat)
        self.combo3.configure(state="disabled")

    def get_subcat(self, event):
        self.combo3.configure(state="readonly")
        self.combo3.set('')
        products = InventoryService.get_products(self.combo1.get(), self.combo2.get())
        self.combo3.configure(values=products)
        self.combo3.bind("<<ComboboxSelected>>", self.show_qty)
        self.entry_qty.configure(state="disabled")

    def show_qty(self, event):
        self.entry_qty.configure(state="normal")
        product_name = self.combo3.get()
        info = InventoryService.get_product_info(product_name)
        if info:
            self.qty_label.configure(text=i18n.t("in_stock").format(info["stock"]))

    def add_to_cart(self):
        self.Scrolledtext1.configure(state="normal")
        product_name = self.combo3.get()
        if product_name:
            product_qty = self.entry_qty.get()
            info = InventoryService.get_product_info(product_name)
            if info:
                stock, mrp = info["stock"], info["mrp"]
                if product_qty.isdigit():
                    qty = int(product_qty)
                    if (stock - qty) >= 0:
                        sp = mrp * qty
                        item = Item(product_name, mrp, qty)
                        self.cart.add_item(item)
                        bill_text = f"{product_name}\t\t\t\t\t\t{qty}\t\t\t\t\t   {sp}\n"
                        self.Scrolledtext1.insert('insert', bill_text)
                    else:
                        messagebox.showerror("Error", "Out of stock.", parent=self.top)
                else:
                    messagebox.showerror("Error", "Invalid quantity.", parent=self.top)
        else:
            messagebox.showerror("Error", "Choose a product.", parent=self.top)
        self.Scrolledtext1.configure(state="disabled")

    def remove_product(self):
        if not self.cart.is_empty():
            self.cart.remove_item()
            self.Scrolledtext1.configure(state="normal")
            lines = [l for l in self.Scrolledtext1.get('1.0', tk.END).split("\n") if l]
            if lines:
                lines.pop()
            self.Scrolledtext1.delete('1.0', tk.END)
            for line in lines:
                self.Scrolledtext1.insert('insert', line + '\n')
            self.Scrolledtext1.configure(state="disabled")
        else:
            messagebox.showerror("Error", "Cart is empty", parent=self.top)

    def total_bill(self):
        if self.cart.is_empty():
            messagebox.showerror("Error", "Add a product.", parent=self.top)
        else:
            self.Scrolledtext1.configure(state="normal")
            strr = self.Scrolledtext1.get('1.0', tk.END)
            if 'Total' not in strr:
                divider = "\n\n\n" + ("─" * 61)
                self.Scrolledtext1.insert('insert', divider)
                total = f"\nTotal\t\t\t\t\t\t\t\t\t\t\tRs. {self.cart.total()}"
                self.Scrolledtext1.insert('insert', total)
                divider2 = "\n" + ("─" * 61)
                self.Scrolledtext1.insert('insert', divider2)
            self.Scrolledtext1.configure(state="disabled")

    def open_payment_window(self):
        if self.cart.is_empty():
            messagebox.showerror("Error", "Cart is empty.", parent=self.top)
            return
        if not self.cust_name.get().strip():
            messagebox.showerror("Error", "Please enter a name.", parent=self.top)
            return
        if not self.cust_num.get().strip():
            messagebox.showerror("Error", "Please enter a number.", parent=self.top)
            return

        self.total_bill()
        pay_win = tk.Toplevel(self.top)
        PaymentPage(pay_win, self.cart.total(), self.complete_sale_with_payment)

    def complete_sale_with_payment(self, payment_info):
        self.Scrolledtext1.configure(state="normal")
        self.Scrolledtext1.insert('insert', f"\n{payment_info}\n")
        self.Scrolledtext1.configure(state="disabled")
        self.gen_bill()

    def gen_bill(self):
        if self.cart.is_empty():
            messagebox.showerror("Error", "Cart is empty.", parent=self.top)
            return
        if not self.cust_name.get().strip():
            messagebox.showerror("Error", "Please enter a name.", parent=self.top)
            return
        if not self.cust_num.get().strip():
            messagebox.showerror("Error", "Please enter a number.", parent=self.top)
            return

        details = self.Scrolledtext1.get('1.0', tk.END)
        BillingService.save_bill_and_update_stock(
            self.cust_name.get(), self.cust_num.get(), details, self.cart.get_summary_dictionary()
        )
        messagebox.showinfo("Success", i18n.t("pay_success"), parent=self.top)

    def clear_bill(self):
        self.entry_name.configure(state="normal")
        self.entry_phone.configure(state="normal")
        self.entry_name.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_search.delete(0, tk.END)
        self.clear_bill_text()

    def clear_selection(self):
        self.entry_qty.delete(0, tk.END)
        self.combo1.configure(state="normal")
        self.combo2.configure(state="normal")
        self.combo3.configure(state="normal")
        self.combo1.delete(0, tk.END)
        self.combo2.delete(0, tk.END)
        self.combo3.delete(0, tk.END)
        self.combo2.configure(state="disabled")
        self.combo3.configure(state="disabled")
        self.entry_qty.configure(state="disabled")
        self.qty_label.configure(text="")

    def search_bill(self):
        result = BillingService.find_bill(self.cust_search_bill.get())
        if result:
            self.clear_bill()
            self.Scrolledtext1.configure(state="normal")
            self.Scrolledtext1.insert(tk.END, result[4])
            self.Scrolledtext1.configure(state="disabled")
        else:
            messagebox.showerror("Error", "Bill not found.", parent=self.top)
            self.entry_search.delete(0, tk.END)

    def generate_report(self):
        today_str = date.today().strftime("%Y-%m-%d")
        report_date = simpledialog.askstring(
            i18n.t("report_title"),
            "Ingrese la fecha para el reporte diario (YYYY-MM-DD):",
            initialvalue=today_str,
            parent=self.top
        )
        if not report_date:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"reporte_diario_{report_date}.csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title=i18n.t("report_title"),
            parent=self.top
        )
        if not filepath:
            return

        try:
            with DatabaseService.get_connection() as db_r:
                cur_r = db_r.cursor()
                cur_r.execute("SELECT * FROM raw_inventory")
                inv_rows = cur_r.fetchall()
                inv_cols = [d[0] for d in cur_r.description]

                cur_r.execute("SELECT * FROM bill WHERE date LIKE ?", [f"%{report_date}%"])
                bill_rows = cur_r.fetchall()
                bill_cols = [d[0] for d in cur_r.description]

            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([f"REPORTE DIARIO DE VENTAS - FECHA: {report_date}"])
                writer.writerow([])
                writer.writerow(["FACTURAS / VENTAS DEL DÍA"])
                writer.writerow(bill_cols)
                writer.writerows(bill_rows)
                writer.writerow([])
                writer.writerow(["INVENTARIO ACTUAL"])
                writer.writerow(inv_cols)
                writer.writerows(inv_rows)

            messagebox.showinfo("OK", f"{i18n.t('report_ok')}\n{filepath}", parent=self.top)
        except Exception as e:
            messagebox.showerror("Error", f"{i18n.t('report_err')}\n{e}", parent=self.top)

    def update_time(self):
        time_str = strftime("%H:%M:%S %p")
        self.clock.config(text=time_str)
        self.clock.after(1000, self.update_time)

    def logout(self):
        sure = messagebox.askyesno(i18n.t("logout"), i18n.t("confirm_logout"), parent=self.top)
        if sure:
            self.top.destroy()
            self.on_logout_callback()

    def exit_app(self):
        sure = messagebox.askyesno(i18n.t("exit"), i18n.t("confirm_exit"), parent=self.top)
        if sure:
            self.top.destroy()
            self.top.quit()

# ==============================================================================
# 6. PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================
class ApplicationController:
    def __init__(self):
        self.root = tk.Tk()
        self.biller_win = None
        self.show_login()

    def show_login(self):
        self.login_page = LoginPage(self.root, on_login_success=self.open_billing_window)

    def open_billing_window(self, username):
        self.root.withdraw()
        self.biller_win = tk.Toplevel()
        biller_app = BillWindow(self.biller_win, username, on_logout_callback=self.on_logout)
        self.biller_win.protocol("WM_DELETE_WINDOW", biller_app.exit_app)

    def on_logout(self):
        self.root.deiconify()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ApplicationController()
    app.run()