# locales.py

TEXTS = {
    "ES": {
        # General & Login
        "login_title": "Inicio de Sesión",
        "username": "Usuario",
        "password": "Contraseña",
        "btn_login": "Iniciar Sesión",
        "forgot_pass": "¿Olvidaste tu contraseña?",
        "lang_toggle": "English",
        
        # Recuperación de Contraseña
        "reset_title": "Recuperar Contraseña",
        "enter_user": "Ingresa tu usuario registrado:",
        "new_pass": "Ingresa tu nueva contraseña:",
        "user_not_found": "El usuario no existe.",
        "pass_success": "Contraseña actualizada correctamente.",
        "error_empty": "Todos los campos son obligatorios.",
        
        # Dashboard / Menú
        "welcome": "Bienvenido al Sistema",
        "btn_export_csv": "Exportar Reporte a CSV",
        "btn_employees": "Empleados",
        "btn_logout": "Cerrar Sesión",
        
        # Exportación CSV
        "csv_success": "Reporte exportado exitosamente en:",
        "csv_error": "Error al exportar el archivo CSV.",
        "csv_no_data": "No hay datos disponibles para exportar."
    },
    "EN": {
        # General & Login
        "login_title": "Login",
        "username": "Username",
        "password": "Password",
        "btn_login": "Login",
        "forgot_pass": "Forgot password?",
        "lang_toggle": "Español",
        
        # Recuperación de Contraseña
        "reset_title": "Password Recovery",
        "enter_user": "Enter your registered username:",
        "new_pass": "Enter your new password:",
        "user_not_found": "User does not exist.",
        "pass_success": "Password updated successfully.",
        "error_empty": "All fields are required.",
        
        # Dashboard / Menú
        "welcome": "Welcome to the System",
        "btn_export_csv": "Export Report to CSV",
        "btn_employees": "Employees",
        "btn_logout": "Logout",
        
        # Exportación CSV
        "csv_success": "Report exported successfully to:",
        "csv_error": "Error exporting CSV file.",
        "csv_no_data": "No data available to export."
    }
}

class LanguageManager:
    def __init__(self):
        self.current_lang = "ES"

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "ES" else "ES"

    def get(self, key):
        return TEXTS[self.current_lang].get(key, key)

# Instancia global para ser importada en la aplicación
lang_manager = LanguageManager()