import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import bcrypt
import random
import smtplib
import ssl
from email.message import EmailMessage
import re
import subprocess

# Archivos de datos
ARCHIVO_PROYECTOS = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\proyectos.json"
ARCHIVO_REGISTRO = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\registro.txt"
ARCHIVO_SESION = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\sesion_actual.json"
ARCHIVO_INTENTOS = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\intentos_fallidos.json"

# Configuración de correo
CORREO_REMITENTE = "cristhianmy@icloud.com"
CONTRASENA_REMITENTE = "zbbb-inqb-fqgv-hqpm"

class FileManager:
    """Clase para manejar operaciones de archivos de manera centralizada"""
    
    @staticmethod
    def cargar_json(archivo):
        """Carga datos JSON desde un archivo"""
        if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
            return []
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    @staticmethod
    def guardar_json(data, archivo):
        """Guarda datos en formato JSON"""
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class DateValidator:
    """Clase para validaciones de fechas"""
    
    @staticmethod
    def validar_fecha(fecha_str):
        """Valida formato de fecha dd/mm/yyyy"""
        try:
            datetime.strptime(fecha_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def convertir_fecha(fecha_str):
        """Convierte string a objeto datetime"""
        try:
            return datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            return None
    
    @staticmethod
    def validar_fechas_tarea(fecha_inicio_tarea, fecha_fin_tarea, fecha_inicio_proyecto, fecha_fin_proyecto):
        """Valida que las fechas de la tarea estén dentro del rango del proyecto"""
        try:
            dt_inicio_tarea = datetime.strptime(fecha_inicio_tarea, "%d/%m/%Y")
            dt_fin_tarea = datetime.strptime(fecha_fin_tarea, "%d/%m/%Y")
            dt_inicio_proyecto = datetime.strptime(fecha_inicio_proyecto, "%d/%m/%Y")
            dt_fin_proyecto = datetime.strptime(fecha_fin_proyecto, "%d/%m/%Y")
            
            # Validar que fecha de fin de tarea sea posterior a fecha de inicio
            if dt_fin_tarea < dt_inicio_tarea:
                return False, "La fecha de fin de la tarea no puede ser anterior a la fecha de inicio"
            
            # Validar que la tarea esté dentro del rango del proyecto
            if dt_inicio_tarea < dt_inicio_proyecto:
                return False, f"La fecha de inicio de la tarea no puede ser anterior a la fecha de inicio del proyecto ({fecha_inicio_proyecto})"
            
            if dt_fin_tarea > dt_fin_proyecto:
                return False, f"La fecha de fin de la tarea no puede ser posterior a la fecha de fin del proyecto ({fecha_fin_proyecto})"
            
            return True, ""
            
        except ValueError:
            return False, "Error en el formato de fechas"

class UserManager:
    """Clase para manejar operaciones de usuarios"""
    
    @staticmethod
    def obtener_datos_usuario_por_correo(correo):
        try:
            with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if len(datos) > 5 and datos[3].strip().lower() == correo.strip().lower():
                        return {
                            "nombre": f"{datos[0].strip()} {datos[1].strip()}",
                            "cedula": datos[2].strip(),
                            "correo": datos[3].strip(),
                            "contraseña_hash": datos[4].strip(),
                            "rol": datos[5].strip()
                        }
        except FileNotFoundError:
            return None
        return None
    
    @staticmethod
    def obtener_datos_usuario_por_cedula(cedula):
        try:
            with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if len(datos) > 5 and datos[2].strip().lower() == cedula.strip().lower():
                        return {
                            "nombre": f"{datos[0].strip()} {datos[1].strip()}",
                            "cedula": datos[2].strip(),
                            "correo": datos[3].strip(),
                            "contraseña_hash": datos[4].strip(),
                            "rol": datos[5].strip()
                        }
        except FileNotFoundError:
            pass
        return None
    
    @staticmethod
    def validar_cedula(cedula):
        return len(cedula) == 10 and cedula.isdigit()
    
    @staticmethod
    def validar_contrasena(contrasena):
        if len(contrasena) < 8:
            return False, "Debe tener al menos 8 caracteres."
        if not re.search(r"[A-Z]", contrasena):
            return False, "Debe tener al menos una letra en mayúscula."
        if not re.search(r"[a-z]", contrasena):
            return False, "Debe tener al menos una letra en minúscula."
        if not re.search(r"[0-9]", contrasena):
            return False, "Debe tener al menos un número."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", contrasena):
            return False, "Debe tener al menos un carácter especial."
        return True, ""

class ProjectManager:
    """Clase para manejar operaciones de proyectos"""
    
    @staticmethod
    def buscar_proyecto_por_nombre(nombre_proyecto):
        data = FileManager.cargar_json(ARCHIVO_PROYECTOS)
        for i, p in enumerate(data):
            if p.get("proyecto", "").strip().lower() == nombre_proyecto.strip().lower():
                return i, p
        return None, None
    
    @staticmethod
    def calcular_avance_proyecto(proyecto):
        tareas = proyecto.get("tareas", [])
        if not tareas:
            return 0
        tareas_completadas = [t for t in tareas if t.get("estado") == "Completada"]
        return (len(tareas_completadas) / len(tareas)) * 100

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gestor de Proyectos")
        self.root.geometry("500x500")
        self.root.configure(bg='#f0f0f0')
        
        self.usuario_actual = None
        self.create_login_interface()
        
    def create_login_interface(self):
        # Título principal
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Equipo GMC", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(title_frame, text="Gestor de Proyectos", 
                                 font=('Arial', 12), 
                                 fg='white', bg='#2c3e50')
        subtitle_label.pack()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=40)
        
        # Login form
        login_frame = tk.LabelFrame(main_frame, text="Iniciar Sesión", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#f0f0f0', padx=20, pady=20)
        login_frame.pack(pady=20, fill='x')
        
        # Email
        tk.Label(login_frame, text="Correo electrónico:", 
                font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        self.email_entry = tk.Entry(login_frame, font=('Arial', 10), width=40)
        self.email_entry.pack(pady=(0, 15))
        
        # Password
        tk.Label(login_frame, text="Contraseña:", 
                font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(login_frame, show="*", font=('Arial', 10), width=40)
        self.password_entry.pack(pady=(0, 15))
        
        # Buttons
        button_frame = tk.Frame(login_frame, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        login_btn = tk.Button(button_frame, text="Iniciar Sesión", 
                             command=self.iniciar_sesion,
                             bg='#3498db', fg='white', 
                             font=('Arial', 10, 'bold'),
                             padx=20, pady=5)
        login_btn.pack(side='left', padx=(0, 10))
        
        change_password_btn = tk.Button(button_frame, text="Cambiar Contraseña", 
                                       command=self.cambiar_contrasena,
                                       bg='#e74c3c', fg='white', 
                                       font=('Arial', 10, 'bold'),
                                       padx=20, pady=5)
        change_password_btn.pack(side='left')
        
        # Botón para desbloquear usuario
        unlock_btn = tk.Button(login_frame, text="Desbloquear Usuario", 
                              command=self.desbloquear_usuario,
                              bg='#f39c12', fg='white', 
                              font=('Arial', 10, 'bold'),
                              padx=20, pady=5)
        unlock_btn.pack(pady=10)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.iniciar_sesion())
    
    def cargar_intentos_fallidos(self):
        """Carga los datos de intentos fallidos desde archivo"""
        return FileManager.cargar_json(ARCHIVO_INTENTOS) if os.path.exists(ARCHIVO_INTENTOS) else {}
    
    def guardar_intentos_fallidos(self, intentos):
        """Guarda los datos de intentos fallidos en archivo"""
        FileManager.guardar_json(intentos, ARCHIVO_INTENTOS)
    
    def registrar_intento_fallido(self, correo):
        """Registra un intento fallido de login"""
        intentos = self.cargar_intentos_fallidos()
        ahora = datetime.now().isoformat()
        
        if correo not in intentos:
            intentos[correo] = {
                "contador": 0,
                "bloqueado": False,
                "fecha_bloqueo": None,
                "ultimo_intento": None
            }
        
        intentos[correo]["contador"] += 1
        intentos[correo]["ultimo_intento"] = ahora
        
        # Bloquear después de 3 intentos
        if intentos[correo]["contador"] >= 3:
            intentos[correo]["bloqueado"] = True
            intentos[correo]["fecha_bloqueo"] = ahora
        
        self.guardar_intentos_fallidos(intentos)
        return intentos[correo]
    
    def verificar_usuario_bloqueado(self, correo):
        """Verifica si un usuario está bloqueado"""
        intentos = self.cargar_intentos_fallidos()
        
        if correo not in intentos:
            return False, None
        
        datos_usuario = intentos[correo]
        if not datos_usuario.get("bloqueado", False):
            return False, None
        
        return True, datos_usuario
    
    def resetear_intentos_fallidos(self, correo):
        """Resetea los intentos fallidos de un usuario"""
        intentos = self.cargar_intentos_fallidos()
        if correo in intentos:
            intentos[correo] = {
                "contador": 0,
                "bloqueado": False,
                "fecha_bloqueo": None,
                "ultimo_intento": None
            }
            self.guardar_intentos_fallidos(intentos)
    
    def guardar_sesion(self, datos_usuario):
        FileManager.guardar_json(datos_usuario, ARCHIVO_SESION)
    
    def iniciar_sesion(self):
        correo = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not correo or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        # Verificar si el usuario está bloqueado
        esta_bloqueado, datos_bloqueo = self.verificar_usuario_bloqueado(correo)
        if esta_bloqueado:
            fecha_bloqueo = datetime.fromisoformat(datos_bloqueo["fecha_bloqueo"])
            messagebox.showerror("Usuario Bloqueado", 
                               f"Su cuenta está bloqueada por múltiples intentos fallidos.\n"
                               f"Fecha de bloqueo: {fecha_bloqueo.strftime('%d/%m/%Y %H:%M:%S')}\n"
                               f"Use 'Desbloquear Usuario' para recuperar el acceso.")
            return
        
        datos_usuario = UserManager.obtener_datos_usuario_por_correo(correo)
        
        if datos_usuario:
            try:
                if bcrypt.checkpw(password.encode('utf-8'), datos_usuario['contraseña_hash'].encode('utf-8')):
                    # Login exitoso - resetear intentos fallidos
                    self.resetear_intentos_fallidos(correo)
                    
                    messagebox.showinfo("Éxito", f"¡Bienvenido, {datos_usuario['nombre']}!")
                    self.guardar_sesion(datos_usuario)
                    
                    self.root.destroy()
                    
                    if datos_usuario['rol'].lower() == 'estudiante':
                        app = EstudianteApp(datos_usuario)
                        app.run()
                    elif datos_usuario['rol'].lower() == 'administrador':
                        app = AdministradorApp(datos_usuario)
                        app.run()
                    else:
                        messagebox.showerror("Error", "Rol de usuario no reconocido")
                else:
                    # Contraseña incorrecta - registrar intento fallido
                    datos_intento = self.registrar_intento_fallido(correo)
                    intentos_restantes = 3 - datos_intento["contador"]
                    
                    if datos_intento["bloqueado"]:
                        messagebox.showerror("Usuario Bloqueado", 
                                           "Su cuenta ha sido bloqueada por múltiples intentos fallidos.\n"
                                           "Use 'Desbloquear Usuario' para recuperar el acceso.")
                    else:
                        messagebox.showerror("Error", 
                                           f"Credenciales inválidas.\n"
                                           f"Intentos restantes: {intentos_restantes}")
            except Exception as e:
                messagebox.showerror("Error", "Error de autenticación. Contacte al administrador.")
        else:
            # Usuario no existe - también registrar como intento fallido
            datos_intento = self.registrar_intento_fallido(correo)
            intentos_restantes = 3 - datos_intento["contador"]
            
            if datos_intento["bloqueado"]:
                messagebox.showerror("Usuario Bloqueado", 
                                   "Esta dirección ha sido bloqueada por múltiples intentos fallidos.\n"
                                   "Use 'Desbloquear Usuario' para recuperar el acceso.")
            else:
                messagebox.showerror("Error", 
                                   f"Credenciales inválidas.\n"
                                   f"Intentos restantes: {intentos_restantes}")
    
    def desbloquear_usuario(self):
        """Proceso para desbloquear un usuario bloqueado"""
        # Ventana para solicitar correo
        unlock_window = tk.Toplevel(self.root)
        unlock_window.title("Desbloquear Usuario")
        unlock_window.geometry("400x400")
        unlock_window.configure(bg='#f0f0f0')
        unlock_window.transient(self.root)
        unlock_window.grab_set()
        
        tk.Label(unlock_window, text="Desbloquear Cuenta de Usuario", 
                font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=20)
        
        tk.Label(unlock_window, text="Ingrese el correo electrónico bloqueado:", 
                font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
        
        email_entry = tk.Entry(unlock_window, font=('Arial', 10), width=40)
        email_entry.pack(pady=5)
        
        def procesar_desbloqueo():
            correo_destino = email_entry.get().strip()
            
            if not correo_destino:
                messagebox.showerror("Error", "Ingrese un correo electrónico")
                return
            
            # Verificar que el correo existe en el sistema
            datos_usuario = UserManager.obtener_datos_usuario_por_correo(correo_destino)
            if not datos_usuario:
                messagebox.showerror("Error", "Correo no encontrado en el sistema")
                return
            
            # Verificar que el usuario esté bloqueado
            esta_bloqueado, datos_bloqueo = self.verificar_usuario_bloqueado(correo_destino)
            if not esta_bloqueado:
                messagebox.showinfo("Información", "Este usuario no está bloqueado")
                return
            
            # Generar código de desbloqueo
            codigo_desbloqueo = str(random.randint(100000, 999999))
            
            if not self.enviar_correo_desbloqueo(correo_destino, codigo_desbloqueo):
                return
            
            # Ventana para ingresar código
            code_window = tk.Toplevel(unlock_window)
            code_window.title("Código de Desbloqueo")
            code_window.geometry("350x250")
            code_window.configure(bg='#f0f0f0')
            code_window.transient(unlock_window)
            code_window.grab_set()
            
            tk.Label(code_window, text="Código de Desbloqueo", 
                    font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=10)
            
            tk.Label(code_window, text="Se ha enviado un código a su correo electrónico.", 
                    font=('Arial', 10), bg='#f0f0f0').pack(pady=5)
            
            tk.Label(code_window, text="Ingrese el código para desbloquear su cuenta:", 
                    font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
            
            code_entry = tk.Entry(code_window, font=('Arial', 12), width=20, justify='center')
            code_entry.pack(pady=5)
            
            def verificar_codigo_desbloqueo():
                codigo_ingresado = code_entry.get().strip()
                
                if codigo_ingresado == codigo_desbloqueo:
                    # Desbloquear usuario
                    self.resetear_intentos_fallidos(correo_destino)
                    messagebox.showinfo("Éxito", 
                                      f"Cuenta desbloqueada exitosamente.\n"
                                      f"Ya puede iniciar sesión normalmente.")
                    code_window.destroy()
                    unlock_window.destroy()
                else:
                    messagebox.showerror("Error", "Código de desbloqueo incorrecto")
                    code_entry.delete(0, tk.END)
            
            tk.Button(code_window, text="Verificar y Desbloquear", 
                     command=verificar_codigo_desbloqueo,
                     bg='#2ecc71', fg='white', 
                     font=('Arial', 10, 'bold'), padx=20, pady=5).pack(pady=15)
            
            tk.Button(code_window, text="Cancelar", 
                     command=code_window.destroy,
                     bg='#95a5a6', fg='white', 
                     font=('Arial', 10, 'bold'), padx=20, pady=5).pack()
        
        tk.Button(unlock_window, text="Enviar Código de Desbloqueo", 
                 command=procesar_desbloqueo,
                 bg='#f39c12', fg='white', 
                 font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
        
        tk.Button(unlock_window, text="Cancelar", 
                 command=unlock_window.destroy,
                 bg='#95a5a6', fg='white', 
                 font=('Arial', 10, 'bold'), padx=20, pady=5).pack()
    
    def enviar_correo_desbloqueo(self, destinatario, codigo):
        """Envía correo con código de desbloqueo"""
        try:
            em = EmailMessage()
            em["From"] = CORREO_REMITENTE
            em["To"] = destinatario
            em["Subject"] = "Código de desbloqueo de cuenta - GMC"
            
            cuerpo_correo = f"""
            Hola,

            Su cuenta ha sido bloqueada por múltiples intentos de acceso fallidos.

            Para desbloquear su cuenta, use el siguiente código:

            {codigo}

            Si no solicitó este desbloqueo, ignore este correo y contacte al administrador del sistema.

            Saludos,
            Sistema de Gestión de Proyectos
            GMC DESARROLLADORES
            """
            em.set_content(cuerpo_correo, charset="utf-8")
            
            context = ssl.create_default_context()
            server_smtp = "smtp.mail.me.com"
            puerto_smtp = 587
            
            with smtplib.SMTP(server_smtp, puerto_smtp) as smtp:
                smtp.starttls(context=context)
                smtp.login(CORREO_REMITENTE, CONTRASENA_REMITENTE)
                smtp.sendmail(CORREO_REMITENTE, destinatario, em.as_string())
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar correo de desbloqueo: {str(e)}")
            return False
    
    def enviar_correo_con_codigo(self, destinatario, codigo):
        try:
            em = EmailMessage()
            em["From"] = CORREO_REMITENTE
            em["To"] = destinatario
            em["Subject"] = "Código de seguridad para cambiar tu contraseña"
            
            cuerpo_correo = f"""
            Hola,

            Para cambiar tu contraseña, usa el siguiente código de seguridad:

            {codigo}

            Si no solicitaste este cambio, ignora este correo.

            Saludos,
            Equipo de soporte GMC.
            """
            em.set_content(cuerpo_correo, charset="utf-8")
            
            context = ssl.create_default_context()
            server_smtp = "smtp.mail.me.com"
            puerto_smtp = 587
            
            with smtplib.SMTP(server_smtp, puerto_smtp) as smtp:
                smtp.starttls(context=context)
                smtp.login(CORREO_REMITENTE, CONTRASENA_REMITENTE)
                smtp.sendmail(CORREO_REMITENTE, destinatario, em.as_string())
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar correo: {str(e)}")
            return False
    
    def cambiar_contrasena(self):
        # Ventana para cambiar contraseña
        change_window = tk.Toplevel(self.root)
        change_window.title("Cambiar Contraseña")
        change_window.geometry("400x300")
        change_window.configure(bg='#f0f0f0')
        change_window.transient(self.root)
        change_window.grab_set()
        
        tk.Label(change_window, text="Ingrese el correo del usuario:", 
                font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
        
        email_entry = tk.Entry(change_window, font=('Arial', 10), width=40)
        email_entry.pack(pady=5)
        
        def procesar_cambio():
            correo_destino = email_entry.get().strip()
            datos_usuario = UserManager.obtener_datos_usuario_por_correo(correo_destino)
            
            if not datos_usuario:
                messagebox.showerror("Error", "Correo no encontrado")
                return
            
            # Verificar si está bloqueado
            esta_bloqueado, _ = self.verificar_usuario_bloqueado(correo_destino)
            if esta_bloqueado:
                messagebox.showerror("Error", "Este usuario está bloqueado. Use 'Desbloquear Usuario' primero.")
                return
            
            codigo_seguridad = str(random.randint(100000, 999999))
            
            if not self.enviar_correo_con_codigo(datos_usuario['correo'], codigo_seguridad):
                return
            
            # Ventana para ingresar código
            code_window = tk.Toplevel(change_window)
            code_window.title("Código de Seguridad")
            code_window.geometry("350x200")
            code_window.configure(bg='#f0f0f0')
            code_window.transient(change_window)
            code_window.grab_set()
            
            tk.Label(code_window, text="Ingrese el código enviado a su correo:", 
                    font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
            
            code_entry = tk.Entry(code_window, font=('Arial', 10), width=20)
            code_entry.pack(pady=5)
            
            def verificar_codigo():
                if code_entry.get() == codigo_seguridad:
                    code_window.destroy()
                    self.mostrar_ventana_nueva_contrasena(change_window, correo_destino)
                else:
                    messagebox.showerror("Error", "Código incorrecto")
            
            tk.Button(code_window, text="Verificar", command=verificar_codigo,
                     bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)
        
        tk.Button(change_window, text="Enviar Código", command=procesar_cambio,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=20)
    
    def mostrar_ventana_nueva_contrasena(self, parent, correo):
        # Ventana para nueva contraseña
        new_password_window = tk.Toplevel(parent)
        new_password_window.title("Nueva Contraseña")
        new_password_window.geometry("400x250")
        new_password_window.configure(bg='#f0f0f0')
        new_password_window.transient(parent)
        new_password_window.grab_set()
        
        tk.Label(new_password_window, text="Nueva contraseña:", 
                font=('Arial', 10), bg='#f0f0f0').pack(pady=(20, 5))
        
        new_password_entry = tk.Entry(new_password_window, show="*", font=('Arial', 10), width=30)
        new_password_entry.pack(pady=5)
        
        tk.Label(new_password_window, text="Confirmar contraseña:", 
                font=('Arial', 10), bg='#f0f0f0').pack(pady=(10, 5))
        
        confirm_password_entry = tk.Entry(new_password_window, show="*", font=('Arial', 10), width=30)
        confirm_password_entry.pack(pady=5)
        
        def guardar_nueva_contrasena():
            nueva = new_password_entry.get()
            confirmar = confirm_password_entry.get()
            
            if not nueva:
                messagebox.showerror("Error", "La contraseña no puede estar vacía")
                return
            
            es_valida, mensaje = UserManager.validar_contrasena(nueva)
            if not es_valida:
                messagebox.showerror("Error", f"Contraseña inválida: {mensaje}")
                return
            
            if nueva != confirmar:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            try:
                with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as f:
                    lineas = f.readlines()
                
                salt = bcrypt.gensalt()
                hash_bytes = bcrypt.hashpw(nueva.encode("utf-8"), salt)
                
                for i, linea in enumerate(lineas):
                    datos = linea.strip().split(",")
                    if datos[3].strip().lower() == correo.lower():
                        datos[4] = hash_bytes.decode("utf-8")
                        lineas[i] = ",".join(datos) + "\n"
                        break
                
                with open(ARCHIVO_REGISTRO, "w", encoding="utf-8") as f:
                    f.writelines(lineas)
                
                # Resetear intentos fallidos también
                self.resetear_intentos_fallidos(correo)
                
                messagebox.showinfo("Éxito", "Contraseña actualizada y cuenta desbloqueada exitosamente")
                new_password_window.destroy()
                parent.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar contraseña: {str(e)}")
        
        tk.Button(new_password_window, text="Guardar", command=guardar_nueva_contrasena,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold')).pack(pady=20)
    
    def run(self):
        self.root.mainloop()

class EstudianteApp:
    def __init__(self, usuario_actual):
        self.usuario_actual = usuario_actual
        self.root = tk.Tk()
        self.root.title(f"Gestor de Proyectos - {usuario_actual['nombre']}")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.create_interface()
        
    def create_interface(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"Gestor de Proyectos - {self.usuario_actual['nombre']}", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=15)
        
        logout_btn = tk.Button(header_frame, text="Cerrar Sesión", 
                              command=self.cerrar_sesion,
                              bg='#e74c3c', fg='white', 
                              font=('Arial', 10, 'bold'))
        logout_btn.pack(side='right', padx=20, pady=15)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Pestaña de Proyectos
        self.create_proyectos_tab()
        
        # Pestaña de Tareas
        self.create_tareas_tab()
        
        # Pestaña de Mis Proyectos
        self.create_mis_proyectos_tab()
    
    def create_proyectos_tab(self):
        proyectos_frame = ttk.Frame(self.notebook)
        self.notebook.add(proyectos_frame, text="Gestión de Proyectos")
        
        # Botones principales
        buttons_frame = tk.Frame(proyectos_frame, bg='#f0f0f0')
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(buttons_frame, text="Crear Proyecto", command=self.crear_proyecto,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Actualizar Proyecto", command=self.actualizar_proyecto,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Eliminar Proyecto", command=self.eliminar_proyecto,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Listar Proyectos", command=self.listar_proyectos,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Lista de proyectos
        list_frame = tk.Frame(proyectos_frame, bg='#f0f0f0')
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        tk.Label(list_frame, text="Lista de Proyectos:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        # Treeview para mostrar proyectos
        columns = ('Proyecto', 'Categoría', 'Costo', 'Avance', 'Responsable')
        self.proyectos_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.proyectos_tree.heading(col, text=col)
            self.proyectos_tree.column(col, width=150)
        
        scrollbar_proyectos = ttk.Scrollbar(list_frame, orient='vertical', command=self.proyectos_tree.yview)
        self.proyectos_tree.configure(yscrollcommand=scrollbar_proyectos.set)
        
        self.proyectos_tree.pack(side='left', expand=True, fill='both')
        scrollbar_proyectos.pack(side='right', fill='y')
        
        # Doble clic para ver detalles
        self.proyectos_tree.bind('<Double-1>', self.ver_detalle_proyecto)
    
    def create_tareas_tab(self):
        tareas_frame = ttk.Frame(self.notebook)
        self.notebook.add(tareas_frame, text="Gestión de Tareas")
        
        # Botones de tareas
        buttons_frame = tk.Frame(tareas_frame, bg='#f0f0f0')
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(buttons_frame, text="Agregar Tarea", command=self.agregar_tarea,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Editar Tarea", command=self.editar_tarea,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Eliminar Tarea", command=self.eliminar_tarea,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Marcar Estado", command=self.marcar_tarea,
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Lista de tareas
        list_frame = tk.Frame(tareas_frame, bg='#f0f0f0')
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        tk.Label(list_frame, text="Mis Tareas:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        # Treeview para mostrar tareas
        columns = ('Proyecto', 'Tarea', 'Descripción', 'Inicio', 'Fin', 'Estado')
        self.tareas_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tareas_tree.heading(col, text=col)
            self.tareas_tree.column(col, width=120)
        
        scrollbar_tareas = ttk.Scrollbar(list_frame, orient='vertical', command=self.tareas_tree.yview)
        self.tareas_tree.configure(yscrollcommand=scrollbar_tareas.set)
        
        self.tareas_tree.pack(side='left', expand=True, fill='both')
        scrollbar_tareas.pack(side='right', fill='y')
    
    def create_mis_proyectos_tab(self):
        mis_proyectos_frame = ttk.Frame(self.notebook)
        self.notebook.add(mis_proyectos_frame, text="Mis Proyectos")
        
        # Botón para refrescar
        tk.Button(mis_proyectos_frame, text="Actualizar Vista", command=self.actualizar_mis_proyectos,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(pady=10)
        
        # Frame para contenido
        content_frame = tk.Frame(mis_proyectos_frame, bg='#f0f0f0')
        content_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Text widget con scrollbar
        self.mis_proyectos_text = tk.Text(content_frame, font=('Arial', 10), wrap='word')
        scrollbar_text = ttk.Scrollbar(content_frame, orient='vertical', command=self.mis_proyectos_text.yview)
        self.mis_proyectos_text.configure(yscrollcommand=scrollbar_text.set)
        
        self.mis_proyectos_text.pack(side='left', expand=True, fill='both')
        scrollbar_text.pack(side='right', fill='y')
        
        # Cargar datos iniciales
        self.actualizar_mis_proyectos()
    
    # Método para obtener las fechas del proyecto
    def obtener_fechas_proyecto(self, nombre_proyecto):
        """Obtiene las fechas de inicio y fin de un proyecto"""
        idx, proj = ProjectManager.buscar_proyecto_por_nombre(nombre_proyecto)
        if proj:
            return proj.get('fehceInicio', ''), proj.get('fechaFin', '')
        return None, None