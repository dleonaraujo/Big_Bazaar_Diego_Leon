import tkinter as tk
import admin
from admin import LoginPage as AdminLoginPage, AdminDashboardPage, InventoryPage, EmployeePage, InvoicePage
import employee
from employee import LoginPage as EmployeeLoginPage, BillWindow

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Big Bazaar")
        self.root.geometry("1024x600")
        self.root.resizable(1, 1)
        self.show_welcome_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        self.clear_screen()
        
        # Fondo degradado o contenedor principal
        canvas = tk.Canvas(self.root, width=1366, height=768, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Fondo anaranjado/rojo
        canvas.create_rectangle(0, 0, 1366, 768, fill="#E64A19", outline="")

        # Título principal
        canvas.create_text(
            683, 280, 
            text="Bienvenido a Big Bazaar", 
            font="-family {Poppins} -size 28 -weight bold", 
            fill="#FFFFFF"
        )
        canvas.create_text(
            683, 330, 
            text="Seleccione su perfil para ingresar", 
            font="-family {Poppins} -size 14", 
            fill="#FFE0B2"
        )

        # Botón Empleado
        btn_emp = tk.Button(
            self.root, 
            text="Empleado", 
            font="-family {Poppins} -size 14 -weight bold", 
            bg="#FFFFFF", 
            fg="#D32F2F", 
            bd=0, 
            cursor="hand2",
            command=self.open_employee_login
        )
        btn_emp.place(x=480, y=390, width=180, height=130)

        # Botón Administrador
        btn_admin = tk.Button(
            self.root, 
            text="Administrador", 
            font="-family {Poppins} -size 14 -weight bold", 
            bg="#212121", 
            fg="#FFFFFF", 
            bd=0, 
            cursor="hand2",
            command=self.open_admin_login
        )
        btn_admin.place(x=700, y=390, width=180, height=130)

    def open_admin_login(self):
        self.clear_screen()
        AdminLoginPage(self.root, on_login_success=self.show_admin_dashboard)

    def open_employee_login(self):
        self.clear_screen()
        EmployeeLoginPage(self.root, on_login_success=self.show_employee_billing)

    def show_admin_dashboard(self):
        self.clear_screen()
        AdminDashboardPage(self.root, self)

    def show_employee_billing(self, username=""):
        self.clear_screen()
        BillWindow(self.root, username, on_logout_callback=self.show_welcome_screen)

    def open_inventory(self):
        self.clear_screen()
        InventoryPage(self.root, self)

    def open_employees(self):
        self.clear_screen()
        EmployeePage(self.root, self)

    def open_invoices(self):
        self.clear_screen()
        InvoicePage(self.root, self)

    def return_to_admin(self, current_top=None):
        self.clear_screen()
        self.show_admin_dashboard()

    def logout(self, current_top=None):
        self.show_welcome_screen()

if __name__ == "__main__":
    from database import init_db
    init_db()  # Inicializa las tablas si no existen
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()