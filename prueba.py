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

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gestor de Proyectos")
        self.root.geometry("500x500")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
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
        if not os.path.exists(ARCHIVO_INTENTOS):
            return {}
        try:
            with open(ARCHIVO_INTENTOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def guardar_intentos_fallidos(self, intentos):
        """Guarda los datos de intentos fallidos en archivo"""
        with open(ARCHIVO_INTENTOS, "w", encoding="utf-8") as f:
            json.dump(intentos, f, ensure_ascii=False, indent=2)
    
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
        
    def obtener_datos_usuario_por_correo(self, correo):
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
    
    def guardar_sesion(self, datos_usuario):
        with open(ARCHIVO_SESION, "w", encoding="utf-8") as f:
            json.dump(datos_usuario, f, ensure_ascii=False, indent=2)
    
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
        
        datos_usuario = self.obtener_datos_usuario_por_correo(correo)
        
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
            datos_usuario = self.obtener_datos_usuario_por_correo(correo_destino)
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
            GMC DESAROLLADORES
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
            datos_usuario = self.obtener_datos_usuario_por_correo(correo_destino)
            
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
            
            if len(nueva) < 8:
                messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres")
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
    
    # Métodos auxiliares
    def cargar_datos(self, archivo):
        if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
            return []
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def guardar_datos(self, data, archivo):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def buscar_proyecto_por_nombre(self, nombre_proyecto):
        data = self.cargar_datos(ARCHIVO_PROYECTOS)
        for i, p in enumerate(data):
            if p.get("proyecto", "").strip().lower() == nombre_proyecto.strip().lower():
                return i, p
        return None, None
    
    def obtener_datos_usuario_por_cedula(self, cedula):
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
    
    def validar_fecha(self, fecha_str):
        try:
            datetime.strptime(fecha_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def calcular_avance_proyecto(self, proyecto):
        tareas = proyecto.get("tareas", [])
        if not tareas:
            return 0
        tareas_completadas = [t for t in tareas if t.get("estado") == "Completada"]
        return (len(tareas_completadas) / len(tareas)) * 100
    
    # Métodos de gestión de proyectos
    def crear_proyecto(self):
        # Ventana para crear proyecto
        create_window = tk.Toplevel(self.root)
        create_window.title("Crear Nuevo Proyecto")
        create_window.geometry("500x600")
        create_window.configure(bg='#f0f0f0')
        create_window.transient(self.root)
        create_window.grab_set()
        
        # Variables
        fields = {}
        
        # Campos del formulario
        form_fields = [
            ("Nombre del proyecto:", "nombre"),
            ("Costo del proyecto:", "costo"),
            ("Categoría del proyecto:", "categoria"),
            ("Descripción del proyecto:", "descripcion"),
            ("Materiales requeridos:", "materiales"),
            ("Fecha de inicio (dd/mm/yyyy):", "fecha_inicio"),
            ("Fecha de fin (dd/mm/yyyy):", "fecha_fin")
        ]
        
        for label_text, field_name in form_fields:
            tk.Label(create_window, text=label_text, font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
            if field_name in ["descripcion", "materiales"]:
                fields[field_name] = tk.Text(create_window, font=('Arial', 10), height=3, width=50)
            else:
                fields[field_name] = tk.Entry(create_window, font=('Arial', 10), width=50)
            fields[field_name].pack(padx=20, pady=(0, 5))
        
        def guardar_proyecto():
            # Validar campos
            valores = {}
            for field_name, widget in fields.items():
                if isinstance(widget, tk.Text):
                    valores[field_name] = widget.get("1.0", tk.END).strip()
                else:
                    valores[field_name] = widget.get().strip()
                
                if not valores[field_name]:
                    messagebox.showerror("Error", f"El campo {field_name} es obligatorio")
                    return
            
            # Validar fechas
            if not self.validar_fecha(valores["fecha_inicio"]):
                messagebox.showerror("Error", "Fecha de inicio inválida. Use el formato dd/mm/yyyy")
                return
            
            if not self.validar_fecha(valores["fecha_fin"]):
                messagebox.showerror("Error", "Fecha de fin inválida. Use el formato dd/mm/yyyy")
                return
            
            # Validar que fecha de fin sea posterior a fecha de inicio
            try:
                fecha_inicio = datetime.strptime(valores["fecha_inicio"], "%d/%m/%Y")
                fecha_fin = datetime.strptime(valores["fecha_fin"], "%d/%m/%Y")
                if fecha_fin < fecha_inicio:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Error en las fechas")
                return
            
            # Crear proyecto
            nuevo_proyecto = {
                "proyecto": valores["nombre"],
                "costo": valores["costo"],
                "categoria": valores["categoria"],
                "descripcion": valores["descripcion"],
                "materiales": valores["materiales"],
                "fehceInicio": valores["fecha_inicio"],  # Mantengo el typo original
                "fechaFin": valores["fecha_fin"],
                "responsableProyecto": {
                    "cedula": self.usuario_actual['cedula'],
                    "nombre": self.usuario_actual['nombre']
                },
                "tareas": []
            }
            
            data = self.cargar_datos(ARCHIVO_PROYECTOS)
            data.append(nuevo_proyecto)
            self.guardar_datos(data, ARCHIVO_PROYECTOS)
            
            messagebox.showinfo("Éxito", "Proyecto creado exitosamente")
            create_window.destroy()
            self.listar_proyectos()
        
        tk.Button(create_window, text="Guardar Proyecto", command=guardar_proyecto,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def actualizar_proyecto(self):
        # Seleccionar proyecto de la lista
        if not self.proyectos_tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un proyecto de la lista")
            return
        
        selected_item = self.proyectos_tree.selection()[0]
        nombre_proyecto = self.proyectos_tree.item(selected_item)['values'][0]
        
        idx, proj = self.buscar_proyecto_por_nombre(nombre_proyecto)
        if proj is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        # Verificar permisos
        if proj.get('responsableProyecto', {}).get('cedula') != self.usuario_actual['cedula']:
            messagebox.showerror("Error", "No tiene permisos para actualizar este proyecto")
            return
        
        # Ventana para actualizar proyecto
        update_window = tk.Toplevel(self.root)
        update_window.title("Actualizar Proyecto")
        update_window.geometry("500x600")
        update_window.configure(bg='#f0f0f0')
        update_window.transient(self.root)
        update_window.grab_set()
        
        # Variables
        fields = {}
        
        # Campos del formulario con valores actuales
        form_fields = [
            ("Nombre del proyecto:", "nombre", proj.get('proyecto', '')),
            ("Costo del proyecto:", "costo", proj.get('costo', '')),
            ("Categoría del proyecto:", "categoria", proj.get('categoria', '')),
            ("Descripción del proyecto:", "descripcion", proj.get('descripcion', '')),
            ("Materiales requeridos:", "materiales", proj.get('materiales', '')),
            ("Fecha de inicio (dd/mm/yyyy):", "fecha_inicio", proj.get('fehceInicio', '')),
            ("Fecha de fin (dd/mm/yyyy):", "fecha_fin", proj.get('fechaFin', ''))
        ]
        
        for label_text, field_name, current_value in form_fields:
            tk.Label(update_window, text=label_text, font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
            if field_name in ["descripcion", "materiales"]:
                fields[field_name] = tk.Text(update_window, font=('Arial', 10), height=3, width=50)
                fields[field_name].insert("1.0", current_value)
            else:
                fields[field_name] = tk.Entry(update_window, font=('Arial', 10), width=50)
                fields[field_name].insert(0, current_value)
            fields[field_name].pack(padx=20, pady=(0, 5))
        
        def actualizar():
            # Obtener valores
            valores = {}
            for field_name, widget in fields.items():
                if isinstance(widget, tk.Text):
                    valores[field_name] = widget.get("1.0", tk.END).strip()
                else:
                    valores[field_name] = widget.get().strip()
                
                if not valores[field_name]:
                    messagebox.showerror("Error", f"El campo {field_name} es obligatorio")
                    return
            
            # Validar fechas
            if not self.validar_fecha(valores["fecha_inicio"]):
                messagebox.showerror("Error", "Fecha de inicio inválida. Use el formato dd/mm/yyyy")
                return
            
            if not self.validar_fecha(valores["fecha_fin"]):
                messagebox.showerror("Error", "Fecha de fin inválida. Use el formato dd/mm/yyyy")
                return
            
            try:
                fecha_inicio = datetime.strptime(valores["fecha_inicio"], "%d/%m/%Y")
                fecha_fin = datetime.strptime(valores["fecha_fin"], "%d/%m/%Y")
                if fecha_fin < fecha_inicio:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Error en las fechas")
                return
            
            # Actualizar proyecto
            proj['proyecto'] = valores["nombre"]
            proj['costo'] = valores["costo"]
            proj['categoria'] = valores["categoria"]
            proj['descripcion'] = valores["descripcion"]
            proj['materiales'] = valores["materiales"]
            proj['fehceInicio'] = valores["fecha_inicio"]
            proj['fechaFin'] = valores["fecha_fin"]
            
            data = self.cargar_datos(ARCHIVO_PROYECTOS)
            data[idx] = proj
            self.guardar_datos(data, ARCHIVO_PROYECTOS)
            
            messagebox.showinfo("Éxito", "Proyecto actualizado exitosamente")
            update_window.destroy()
            self.listar_proyectos()
        
        tk.Button(update_window, text="Actualizar Proyecto", command=actualizar,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def eliminar_proyecto(self):
        if not self.proyectos_tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un proyecto de la lista")
            return
        
        selected_item = self.proyectos_tree.selection()[0]
        nombre_proyecto = self.proyectos_tree.item(selected_item)['values'][0]
        
        idx, proj = self.buscar_proyecto_por_nombre(nombre_proyecto)
        if proj is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        # Verificar permisos
        if proj.get('responsableProyecto', {}).get('cedula') != self.usuario_actual['cedula']:
            messagebox.showerror("Error", "No tiene permisos para eliminar este proyecto")
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar el proyecto '{proj['proyecto']}' y todas sus tareas?"):
            data = self.cargar_datos(ARCHIVO_PROYECTOS)
            data.pop(idx)
            self.guardar_datos(data, ARCHIVO_PROYECTOS)
            messagebox.showinfo("Éxito", "Proyecto eliminado exitosamente")
            self.listar_proyectos()
    
    def listar_proyectos(self):
        # Limpiar el treeview
        for item in self.proyectos_tree.get_children():
            self.proyectos_tree.delete(item)
        
        # Cargar proyectos
        data = self.cargar_datos(ARCHIVO_PROYECTOS)
        for proyecto in data:
            avance = self.calcular_avance_proyecto(proyecto)
            responsable = proyecto.get('responsableProyecto', {}).get('nombre', 'N/A')
            
            self.proyectos_tree.insert('', 'end', values=(
                proyecto.get('proyecto', 'N/A'),
                proyecto.get('categoria', 'N/A'),
                proyecto.get('costo', 'N/A'),
                f"{avance:.1f}%",
                responsable
            ))
    
    def ver_detalle_proyecto(self, event):
        if not self.proyectos_tree.selection():
            return
        
        selected_item = self.proyectos_tree.selection()[0]
        nombre_proyecto = self.proyectos_tree.item(selected_item)['values'][0]
        
        idx, proj = self.buscar_proyecto_por_nombre(nombre_proyecto)
        if proj is None:
            return
        
        # Ventana de detalles
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Detalles del Proyecto: {proj.get('proyecto', 'N/A')}")
        detail_window.geometry("600x500")
        detail_window.configure(bg='#f0f0f0')
        detail_window.transient(self.root)
        
        # Text widget con scrollbar
        text_frame = tk.Frame(detail_window)
        text_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, font=('Arial', 10), wrap='word')
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Contenido del detalle
        avance = self.calcular_avance_proyecto(proj)
        resp = proj.get("responsableProyecto", {})
        
        detalle = f"""===== Detalle del Proyecto =====

Proyecto: {proj.get('proyecto', 'N/A')} (Avance: {avance:.2f}%)
Costo: {proj.get('costo', 'N/A')}
Categoría: {proj.get('categoria', 'N/A')}
Fecha de inicio: {proj.get('fehceInicio', 'N/A')}
Fecha de fin: {proj.get('fechaFin', 'N/A')}
Responsable: {resp.get('nombre', 'N/A')} (Cédula: {resp.get('cedula', 'N/A')})

Descripción:
{proj.get('descripcion', 'N/A')}

Materiales:
{proj.get('materiales', 'N/A')}

Tareas:
"""
        
        tareas = proj.get("tareas", [])
        if not tareas:
            detalle += "   - No hay tareas registradas.\n"
        else:
            for i, t in enumerate(tareas, 1):
                r = t.get("responsable", {})
                detalle += f"""   {i}. {t.get('nombre', 'N/A')} - {t.get('descripcion', 'N/A')}
      Inicio: {t.get('fecha_inicio', 'N/A')} | Fin: {t.get('fecha_fin', 'N/A')} | Estado: {t.get('estado', 'N/A')}
      Responsable: {r.get('nombre', 'N/A')} ({r.get('cedula', 'N/A')})

"""
        
        text_widget.insert('1.0', detalle)
        text_widget.configure(state='disabled')
        
        text_widget.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
    
    # Métodos de gestión de tareas
    def agregar_tarea(self):
        data = self.cargar_datos(ARCHIVO_PROYECTOS)
        if not data:
            messagebox.showwarning("Advertencia", "No hay proyectos. No se puede agregar una tarea.")
            return
        
        # Ventana para agregar tarea
        add_task_window = tk.Toplevel(self.root)
        add_task_window.title("Agregar Tarea")
        add_task_window.geometry("500x500")
        add_task_window.configure(bg='#f0f0f0')
        add_task_window.transient(self.root)
        add_task_window.grab_set()
        
        # Selección de proyecto
        tk.Label(add_task_window, text="Seleccionar Proyecto:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(20, 5))
        
        proyecto_var = tk.StringVar()
        proyecto_combo = ttk.Combobox(add_task_window, textvariable=proyecto_var, font=('Arial', 10), width=47)
        proyecto_combo['values'] = [p.get('proyecto', 'N/A') for p in data]
        proyecto_combo.pack(padx=20, pady=(0, 10))
        
        # Campos de la tarea
        tk.Label(add_task_window, text="Nombre de la tarea:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        tarea_entry = tk.Entry(add_task_window, font=('Arial', 10), width=50)
        tarea_entry.pack(padx=20, pady=(0, 10))
        
        tk.Label(add_task_window, text="Descripción de la tarea:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        descripcion_text = tk.Text(add_task_window, font=('Arial', 10), height=3, width=50)
        descripcion_text.pack(padx=20, pady=(0, 10))
        
        tk.Label(add_task_window, text="Fecha de inicio (dd/mm/yyyy):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        fecha_inicio_entry = tk.Entry(add_task_window, font=('Arial', 10), width=50)
        fecha_inicio_entry.pack(padx=20, pady=(0, 10))
        
        tk.Label(add_task_window, text="Fecha de fin (dd/mm/yyyy):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        fecha_fin_entry = tk.Entry(add_task_window, font=('Arial', 10), width=50)
        fecha_fin_entry.pack(padx=20, pady=(0, 10))
        
        tk.Label(add_task_window, text="Cédula del responsable:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        cedula_entry = tk.Entry(add_task_window, font=('Arial', 10), width=50)
        cedula_entry.pack(padx=20, pady=(0, 10))
        
        def guardar_tarea():
            nombre_proyecto = proyecto_var.get()
            nombre_tarea = tarea_entry.get().strip()
            descripcion = descripcion_text.get("1.0", tk.END).strip()
            fecha_inicio = fecha_inicio_entry.get().strip()
            fecha_fin = fecha_fin_entry.get().strip()
            cedula_resp = cedula_entry.get().strip()
            
            if not all([nombre_proyecto, nombre_tarea, descripcion, fecha_inicio, fecha_fin, cedula_resp]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            # Validar fechas
            if not self.validar_fecha(fecha_inicio) or not self.validar_fecha(fecha_fin):
                messagebox.showerror("Error", "Fechas inválidas. Use el formato dd/mm/yyyy")
                return
            
            try:
                dt_inicio = datetime.strptime(fecha_inicio, "%d/%m/%Y")
                dt_fin = datetime.strptime(fecha_fin, "%d/%m/%Y")
                if dt_fin < dt_inicio:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Error en las fechas")
                return
            
            # Validar responsable
            datos_resp = self.obtener_datos_usuario_por_cedula(cedula_resp)
            if not datos_resp or datos_resp['rol'].lower() != "estudiante":
                messagebox.showerror("Error", "Cédula no encontrada o rol no válido (debe ser estudiante)")
                return
            
            # Buscar proyecto
            idx, proj = self.buscar_proyecto_por_nombre(nombre_proyecto)
            if proj is None:
                messagebox.showerror("Error", "Proyecto no encontrado")
                return
            
            # Crear tarea
            nueva_tarea = {
                "nombre": nombre_tarea,
                "descripcion": descripcion,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "responsable": {
                    "cedula": cedula_resp,
                    "nombre": datos_resp['nombre']
                },
                "estado": "Asignada"
            }
            
            proj.setdefault("tareas", []).append(nueva_tarea)
            data[idx] = proj
            self.guardar_datos(data, ARCHIVO_PROYECTOS)
            
            messagebox.showinfo("Éxito", "Tarea agregada exitosamente")
            add_task_window.destroy()
            self.cargar_mis_tareas()
        
        tk.Button(add_task_window, text="Guardar Tarea", command=guardar_tarea,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def editar_tarea(self):
        if not self.tareas_tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarea de la lista")
            return
        
        selected_item = self.tareas_tree.selection()[0]
        valores = self.tareas_tree.item(selected_item)['values']
        nombre_proyecto = valores[0]
        nombre_tarea = valores[1]
        
        # Buscar proyecto y tarea
        idx, proj = self.buscar_proyecto_por_nombre(nombre_proyecto)
        if proj is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        tareas = proj.get("tareas", [])
        tarea_idx = None
        tarea = None
        
        for i, t in enumerate(tareas):
            if t.get('nombre') == nombre_tarea:
                tarea_idx = i
                tarea = t
                break
        
        if tarea is None:
            messagebox.showerror("Error", "Tarea no encontrada")
            return
        
        # Ventana para editar tarea
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Tarea")
        edit_window.geometry("500x500")
        edit_window.configure(bg='#f0f0f0')
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Campos con valores actuales
        tk.Label(edit_window, text="Nombre de la tarea:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(20, 5))
        nombre_entry = tk.Entry(edit_window, font=('Arial', 10), width=50)
        nombre_entry.insert(0, tarea.get('nombre', ''))
        nombre_entry.pack(padx=20, pady=(0, 10))
        
        tk.Label(edit_window, text="Descripción de la tarea:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        descripcion_text = tk.Text(edit_window, font=('Arial', 10), height=3, width=50)
        descripcion_text.insert("1.0", tarea.get('descripcion', ''))
        descripcion_text.pack(padx=20, pady=(0, 10))
        
        tk.Label(edit_window, text="Fecha de inicio (dd/mm/yyyy):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        fecha_inicio_entry = tk.Entry(edit_window, font=('Arial', 10), width=50)
        fecha_inicio_entry.insert(0, tarea.get('fecha_inicio', ''))
        fecha_inicio_entry.pack(padx=20, pady=(0, 10))
        
        tk.Label(edit_window, text="Fecha de fin (dd/mm/yyyy):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        fecha_fin_entry = tk.Entry(edit_window, font=('Arial', 10), width=50)
        fecha_fin_entry.insert(0, tarea.get('fecha_fin', ''))
        fecha_fin_entry.pack(padx=20, pady=(0, 10))
        
        tk.Label(edit_window, text="Cédula del responsable:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        cedula_entry = tk.Entry(edit_window, font=('Arial', 10), width=50)
        cedula_entry.insert(0, tarea.get('responsable', {}).get('cedula', ''))
        cedula_entry.pack(padx=20, pady=(0, 10))
        
        def actualizar_tarea():
            nuevo_nombre = nombre_entry.get().strip()
            nueva_descripcion = descripcion_text.get("1.0", tk.END).strip()
            nueva_fecha_inicio = fecha_inicio_entry.get().strip()
            nueva_fecha_fin = fecha_fin_entry.get().strip()
            nueva_cedula = cedula_entry.get().strip()
            
            if not all([nuevo_nombre, nueva_descripcion, nueva_fecha_inicio, nueva_fecha_fin, nueva_cedula]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            # Validar fechas
            if not self.validar_fecha(nueva_fecha_inicio) or not self.validar_fecha(nueva_fecha_fin):
                messagebox.showerror("Error", "Fechas inválidas. Use el formato dd/mm/yyyy")
                return
            
            try:
                dt_inicio = datetime.strptime(nueva_fecha_inicio, "%d/%m/%Y")
                dt_fin = datetime.strptime(nueva_fecha_fin, "%d/%m/%Y")
                if dt_fin < dt_inicio:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Error en las fechas")
                return
            
            # Validar responsable
            datos_resp = self.obtener_datos_usuario_por_cedula(nueva_cedula)
            if not datos_resp or datos_resp['rol'].lower() != "estudiante":
                messagebox.showerror("Error", "Cédula no encontrada o rol no válido (debe ser estudiante)")
                return
            
            # Actualizar tarea
            tarea['nombre'] = nuevo_nombre
            tarea['descripcion'] = nueva_descripcion
            tarea['fecha_inicio'] = nueva_fecha_inicio
            tarea['fecha_fin'] = nueva_fecha_fin
            tarea['responsable'] = {
                "cedula": nueva_cedula,
                "nombre": datos_resp['nombre']
            }
            
            tareas[tarea_idx] = tarea
            proj['tareas'] = tareas
            data = self.cargar_datos(ARCHIVO_PROYECTOS)
            data[idx] = proj
            self.guardar_datos(data, ARCHIVO_PROYECTOS)
            
            messagebox.showinfo("Éxito", "Tarea actualizada exitosamente")
            edit_window.destroy()
            self.cargar_mis_tareas()
        
        tk.Button(edit_window, text="Actualizar Tarea", command=actualizar_tarea,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def eliminar_tarea(self):
        if not self.tareas_tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarea de la lista")
            return
        
        selected_item = self.tareas_tree.selection()[0]
        valores = self.tareas_tree.item(selected_item)['values']
        nombre_proyecto = valores[0]
        nombre_tarea = valores[1]
        
        # Buscar proyecto y tarea
        idx, proj = self.buscar_proyecto_por_nombre(nombre_proyecto)
        if proj is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        tareas = proj.get("tareas", [])
        tarea_idx = None
        
        for i, t in enumerate(tareas):
            if t.get('nombre') == nombre_tarea:
                tarea_idx = i
                break
        
        if tarea_idx is None:
            messagebox.showerror("Error", "Tarea no encontrada")
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar la tarea '{nombre_tarea}'?"):
            tareas.pop(tarea_idx)
            proj['tareas'] = tareas
            data = self.cargar_datos(ARCHIVO_PROYECTOS)
            data[idx] = proj
            self.guardar_datos(data, ARCHIVO_PROYECTOS)
            
            messagebox.showinfo("Éxito", "Tarea eliminada exitosamente")
            self.cargar_mis_tareas()
    
    def marcar_tarea(self):
        if not self.tareas_tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarea de la lista")
            return
        
        selected_item = self.tareas_tree.selection()[0]
        valores = self.tareas_tree.item(selected_item)['values']
        nombre_proyecto = valores[0]
        nombre_tarea = valores[1]
        
        # Buscar proyecto y tarea
        idx, proj = self.buscar_proyecto_por_nombre(nombre_proyecto)
        if proj is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        tareas = proj.get("tareas", [])
        tarea_idx = None
        tarea = None
        
        for i, t in enumerate(tareas):
            if t.get('nombre') == nombre_tarea and t.get('responsable', {}).get('cedula') == self.usuario_actual['cedula']:
                tarea_idx = i
                tarea = t
                break
        
        if tarea is None:
            messagebox.showerror("Error", "No puede modificar esta tarea (no es el responsable)")
            return
        
        # Ventana para cambiar estado
        estado_window = tk.Toplevel(self.root)
        estado_window.title("Cambiar Estado de Tarea")
        estado_window.geometry("300x200")
        estado_window.configure(bg='#f0f0f0')
        estado_window.transient(self.root)
        estado_window.grab_set()
        
        tk.Label(estado_window, text=f"Tarea: {nombre_tarea}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=20)
        tk.Label(estado_window, text=f"Estado actual: {tarea.get('estado', 'N/A')}", font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
        
        estado_var = tk.StringVar()
        estados = ["Asignada", "En ejecución", "Completada"]
        
        for estado in estados:
            rb = tk.Radiobutton(estado_window, text=estado, variable=estado_var, value=estado, 
                               font=('Arial', 10), bg='#f0f0f0')
            rb.pack(anchor='w', padx=50)
            if estado == tarea.get('estado'):
                rb.select()
        
        def cambiar_estado():
            nuevo_estado = estado_var.get()
            if not nuevo_estado:
                messagebox.showwarning("Advertencia", "Por favor seleccione un estado")
                return
            
            tarea['estado'] = nuevo_estado
            tareas[tarea_idx] = tarea
            proj['tareas'] = tareas
            data = self.cargar_datos(ARCHIVO_PROYECTOS)
            data[idx] = proj
            self.guardar_datos(data, ARCHIVO_PROYECTOS)
            
            messagebox.showinfo("Éxito", f"Estado actualizado a '{nuevo_estado}'")
            estado_window.destroy()
            self.cargar_mis_tareas()
        
        tk.Button(estado_window, text="Cambiar Estado", command=cambiar_estado,
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold')).pack(pady=20)
    
    def cargar_mis_tareas(self):
        # Limpiar el treeview
        for item in self.tareas_tree.get_children():
            self.tareas_tree.delete(item)
        
        # Cargar tareas del usuario actual
        ced = self.usuario_actual['cedula']
        data = self.cargar_datos(ARCHIVO_PROYECTOS)
        
        for proyecto in data:
            for tarea in proyecto.get("tareas", []):
                if tarea.get('responsable', {}).get('cedula') == ced:
                    self.tareas_tree.insert('', 'end', values=(
                        proyecto.get('proyecto', 'N/A'),
                        tarea.get('nombre', 'N/A'),
                        tarea.get('descripcion', 'N/A')[:50] + '...' if len(tarea.get('descripcion', '')) > 50 else tarea.get('descripcion', 'N/A'),
                        tarea.get('fecha_inicio', 'N/A'),
                        tarea.get('fecha_fin', 'N/A'),
                        tarea.get('estado', 'N/A')
                    ))
    
    def actualizar_mis_proyectos(self):
        self.mis_proyectos_text.configure(state='normal')
        self.mis_proyectos_text.delete('1.0', tk.END)
        
        ced = self.usuario_actual['cedula']
        data = self.cargar_datos(ARCHIVO_PROYECTOS)
        mis_proyectos = []
        mis_tareas = []
        
        for p in data:
            rp = p.get("responsableProyecto", {})
            if rp.get("cedula", "").strip() == ced:
                mis_proyectos.append(p)
            for t in p.get("tareas", []):
                r = t.get("responsable", {})
                if r.get("cedula", "").strip() == ced:
                    mis_tareas.append((p.get("proyecto", ""), t))
        
        contenido = "===== Proyectos creados por mí =====\n\n"
        if not mis_proyectos:
            contenido += "No tiene proyectos como responsable.\n\n"
        else:
            for i, p in enumerate(mis_proyectos, 1):
                avance = self.calcular_avance_proyecto(p)
                contenido += f"{i}. {p.get('proyecto', 'N/A')} | Avance: {avance:.2f}% | Costo: {p.get('costo', 'N/A')} | Inicio: {p.get('fehceInicio', 'N/A')} | Fin: {p.get('fechaFin', 'N/A')}\n"
        
        contenido += "\n===== Tareas asignadas a mí =====\n\n"
        if not mis_tareas:
            contenido += "No tiene tareas asignadas.\n"
        else:
            for i, (nombre_proy, t) in enumerate(mis_tareas, 1):
                contenido += f"{i}. [{nombre_proy}] {t.get('nombre', 'N/A')} - {t.get('descripcion', 'N/A')}\n"
                contenido += f"   Inicio: {t.get('fecha_inicio', 'N/A')} | Fin: {t.get('fecha_fin', 'N/A')} | Estado: {t.get('estado', 'N/A')}\n\n"
        
        self.mis_proyectos_text.insert('1.0', contenido)
        self.mis_proyectos_text.configure(state='disabled')
    
    def cerrar_sesion(self):
        if os.path.exists(ARCHIVO_SESION):
            os.remove(ARCHIVO_SESION)
        self.root.destroy()
        # Volver al login
        login = LoginWindow()
        login.run()
    
    def run(self):
        # Cargar datos iniciales
        self.listar_proyectos()
        self.cargar_mis_tareas()
        self.root.mainloop()

class AdministradorApp:
    def __init__(self, usuario_actual):
        self.usuario_actual = usuario_actual
        self.root = tk.Tk()
        self.root.title(f"Sistema de Administración - {usuario_actual['nombre']}")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.create_interface()
    
    def create_interface(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"Sistema de Administración - {self.usuario_actual['nombre']}", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=15)
        
        logout_btn = tk.Button(header_frame, text="Cerrar Sesión", 
                              command=self.cerrar_sesion,
                              bg='#e74c3c', fg='white', 
                              font=('Arial', 10, 'bold'))
        logout_btn.pack(side='right', padx=20, pady=15)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Pestaña de Usuarios
        self.create_usuarios_tab()
        
        # Pestaña de Reportes
        self.create_reportes_tab()
    
    def create_usuarios_tab(self):
        usuarios_frame = ttk.Frame(self.notebook)
        self.notebook.add(usuarios_frame, text="Gestión de Usuarios")
        
        # Botones principales
        buttons_frame = tk.Frame(usuarios_frame, bg='#f0f0f0')
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(buttons_frame, text="Registrar Usuario", command=self.registrar_usuario,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Actualizar Usuario", command=self.actualizar_usuario,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Eliminar Usuario", command=self.eliminar_usuario,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Actualizar Lista", command=self.cargar_usuarios,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Lista de usuarios
        list_frame = tk.Frame(usuarios_frame, bg='#f0f0f0')
        list_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        tk.Label(list_frame, text="Lista de Usuarios:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        # Treeview para mostrar usuarios
        columns = ('Nombre', 'Apellido', 'Cédula', 'Correo', 'Rol')
        self.usuarios_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.usuarios_tree.heading(col, text=col)
            self.usuarios_tree.column(col, width=150)
        
        scrollbar_usuarios = ttk.Scrollbar(list_frame, orient='vertical', command=self.usuarios_tree.yview)
        self.usuarios_tree.configure(yscrollcommand=scrollbar_usuarios.set)
        
        self.usuarios_tree.pack(side='left', expand=True, fill='both')
        scrollbar_usuarios.pack(side='right', fill='y')
    
    def create_reportes_tab(self):
        reportes_frame = ttk.Frame(self.notebook)
        self.notebook.add(reportes_frame, text="Reportes de Proyectos")
        
        # Botones de reportes
        buttons_frame = tk.Frame(reportes_frame, bg='#f0f0f0')
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(buttons_frame, text="Todos los Proyectos", command=self.ver_todos_proyectos,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Buscar Proyecto", command=self.buscar_proyecto_reporte,
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Resumen de Proyectos", command=self.generar_resumen,
                 bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Ordenar Proyectos", command=self.ordenar_proyectos,
                 bg='#1abc9c', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Área de reportes
        reportes_text_frame = tk.Frame(reportes_frame, bg='#f0f0f0')
        reportes_text_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        tk.Label(reportes_text_frame, text="Reportes de Proyectos:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        # Text widget con scrollbar
        self.reportes_text = tk.Text(reportes_text_frame, font=('Arial', 10), wrap='word')
        scrollbar_reportes = ttk.Scrollbar(reportes_text_frame, orient='vertical', command=self.reportes_text.yview)
        self.reportes_text.configure(yscrollcommand=scrollbar_reportes.set)
        
        self.reportes_text.pack(side='left', expand=True, fill='both')
        scrollbar_reportes.pack(side='right', fill='y')
    
    # Métodos auxiliares
    def validar_cedula(self, cedula):
        return len(cedula) == 10 and cedula.isdigit()
    
    def validar_contrasena(self, contrasena):
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
    
    def hash_contrasena(self, contrasena):
        salt = bcrypt.gensalt()
        hash_bytes = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
        return hash_bytes.decode('utf-8')
    
    def leer_usuarios(self):
        if not os.path.exists(ARCHIVO_REGISTRO):
            return []
        usuarios = []
        try:
            with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
            
            for linea in lineas:
                linea = linea.strip()
                if linea:  # Solo procesar líneas no vacías
                    datos = linea.split(',')
                    if len(datos) >= 6:
                        usuario = {
                            "nombre": datos[0].strip(),
                            "apellido": datos[1].strip(),
                            "cedula": datos[2].strip(),
                            "correo": datos[3].strip(),
                            "contraseña": datos[4].strip(),
                            "rol": datos[5].strip()
                        }
                        usuarios.append(usuario)
                        print(f"Debug: Usuario cargado - Cédula: '{usuario['cedula']}'")  # Debug temporal
        except Exception as e:
            print(f"Error al leer usuarios: {e}")
            messagebox.showerror("Error", f"Error al leer archivo de usuarios: {e}")
        
        return usuarios
    
    def guardar_usuarios(self, usuarios):
        with open(ARCHIVO_REGISTRO, "w", encoding="utf-8") as archivo:
            for u in usuarios:
                archivo.write(f"{u['nombre']},{u['apellido']},{u['cedula']},{u['correo']},{u['contraseña']},{u['rol']}\n")
    
    def cargar_proyectos(self):
        if not os.path.exists(ARCHIVO_PROYECTOS) or os.stat(ARCHIVO_PROYECTOS).st_size == 0:
            return []
        try:
            with open(ARCHIVO_PROYECTOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def calcular_avance_proyecto(self, proyecto):
        tareas = proyecto.get("tareas", [])
        if not tareas:
            return 0
        tareas_completadas = [t for t in tareas if t.get("estado") == "Completada"]
        return (len(tareas_completadas) / len(tareas)) * 100
    
    # Métodos de gestión de usuarios
    def registrar_usuario(self):
        # Ventana para registrar usuario
        register_window = tk.Toplevel(self.root)
        register_window.title("Registrar Nuevo Usuario")
        register_window.geometry("450x500")
        register_window.configure(bg='#f0f0f0')
        register_window.transient(self.root)
        register_window.grab_set()
        
        # Variables
        fields = {}
        
        # Campos del formulario
        form_fields = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Cédula de identidad:", "cedula"),
            ("Correo electrónico:", "correo")
        ]
        
        for label_text, field_name in form_fields:
            tk.Label(register_window, text=label_text, font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
            fields[field_name] = tk.Entry(register_window, font=('Arial', 10), width=40)
            fields[field_name].pack(padx=20, pady=(0, 5))
        
        # Contraseña
        tk.Label(register_window, text="Contraseña:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        password_entry = tk.Entry(register_window, show="*", font=('Arial', 10), width=40)
        password_entry.pack(padx=20, pady=(0, 5))
        
        tk.Label(register_window, text="Confirmar contraseña:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        confirm_password_entry = tk.Entry(register_window, show="*", font=('Arial', 10), width=40)
        confirm_password_entry.pack(padx=20, pady=(0, 5))
        
        # Rol
        tk.Label(register_window, text="Rol:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        rol_var = tk.StringVar()
        rol_frame = tk.Frame(register_window, bg='#f0f0f0')
        rol_frame.pack(anchor='w', padx=20)
        
        tk.Radiobutton(rol_frame, text="Administrador", variable=rol_var, value="Administrador", 
                      font=('Arial', 10), bg='#f0f0f0').pack(side='left', padx=(0, 20))
        tk.Radiobutton(rol_frame, text="Estudiante", variable=rol_var, value="Estudiante", 
                      font=('Arial', 10), bg='#f0f0f0').pack(side='left')
        
        def guardar_usuario():
            # Validar campos
            valores = {}
            for field_name, widget in fields.items():
                valores[field_name] = widget.get().strip()
                if not valores[field_name]:
                    messagebox.showerror("Error", f"El campo {field_name} es obligatorio")
                    return
            
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            rol = rol_var.get()
            
            if not password:
                messagebox.showerror("Error", "La contraseña es obligatoria")
                return
            
            if not rol:
                messagebox.showerror("Error", "Debe seleccionar un rol")
                return
            
            # Validar cédula
            if not self.validar_cedula(valores["cedula"]):
                messagebox.showerror("Error", "Cédula inválida. Debe tener 10 dígitos.")
                return
            
            # Validar contraseña
            es_valida, mensaje = self.validar_contrasena(password)
            if not es_valida:
                messagebox.showerror("Error", f"Contraseña inválida: {mensaje}")
                return
            
            if password != confirm_password:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            # Verificar que no exista usuario con la misma cédula o correo
            usuarios_existentes = self.leer_usuarios()
            for u in usuarios_existentes:
                if u['cedula'] == valores["cedula"]:
                    messagebox.showerror("Error", "Ya existe un usuario con esta cédula")
                    return
                if u['correo'] == valores["correo"]:
                    messagebox.showerror("Error", "Ya existe un usuario con este correo")
                    return
            
            # Crear usuario
            hash_str = self.hash_contrasena(password)
            with open(ARCHIVO_REGISTRO, "a", encoding="utf-8") as archivo:
                archivo.write(f"{valores['nombre']},{valores['apellido']},{valores['cedula']},{valores['correo']},{hash_str},{rol}\n")
            
            messagebox.showinfo("Éxito", "Usuario registrado exitosamente")
            register_window.destroy()
            self.cargar_usuarios()
        
        tk.Button(register_window, text="Registrar Usuario", command=guardar_usuario,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def actualizar_usuario(self):
        if not self.usuarios_tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario de la lista")
            return
        
        selected_item = self.usuarios_tree.selection()[0]
        valores = self.usuarios_tree.item(selected_item)['values']
        cedula_usuario = str(valores[2]).strip()  # Asegurar que sea string y sin espacios
        
        print(f"Debug: Buscando usuario con cédula: '{cedula_usuario}'")  # Debug temporal
        
        usuarios = self.leer_usuarios()
        usuario_encontrado = None
        indice = None
        
        for i, usuario in enumerate(usuarios):
            usuario_cedula = str(usuario["cedula"]).strip()
            print(f"Debug: Comparando '{cedula_usuario}' con '{usuario_cedula}'")  # Debug temporal
            
            if usuario_cedula == cedula_usuario:
                usuario_encontrado = usuario
                indice = i
                print(f"Debug: Usuario encontrado en índice {i}")  # Debug temporal
                break
        
        if not usuario_encontrado:
            print(f"Debug: Usuario no encontrado. Cédulas disponibles: {[u['cedula'] for u in usuarios]}")  # Debug temporal
            messagebox.showerror("Error", f"Usuario con cédula '{cedula_usuario}' no encontrado")
            return
        
        # Ventana para actualizar usuario
        update_window = tk.Toplevel(self.root)
        update_window.title("Actualizar Usuario")
        update_window.geometry("450x400")
        update_window.configure(bg='#f0f0f0')
        update_window.transient(self.root)
        update_window.grab_set()
        
        # Variables
        fields = {}
        
        # Campos del formulario con valores actuales
        form_fields = [
            ("Nombre:", "nombre", usuario_encontrado['nombre']),
            ("Apellido:", "apellido", usuario_encontrado['apellido']),
            ("Correo electrónico:", "correo", usuario_encontrado['correo'])
        ]
        
        for label_text, field_name, current_value in form_fields:
            tk.Label(update_window, text=label_text, font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
            fields[field_name] = tk.Entry(update_window, font=('Arial', 10), width=40)
            fields[field_name].insert(0, current_value)
            fields[field_name].pack(padx=20, pady=(0, 5))
        
        # Checkbox para cambiar contraseña
        cambiar_password_var = tk.BooleanVar()
        tk.Checkbutton(update_window, text="Cambiar contraseña", variable=cambiar_password_var, 
                      font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        
        # Contraseña (inicialmente deshabilitada)
        password_frame = tk.Frame(update_window, bg='#f0f0f0')
        password_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(password_frame, text="Nueva contraseña:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w')
        password_entry = tk.Entry(password_frame, show="*", font=('Arial', 10), width=40, state='disabled')
        password_entry.pack()
        
        tk.Label(password_frame, text="Confirmar contraseña:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(5, 0))
        confirm_password_entry = tk.Entry(password_frame, show="*", font=('Arial', 10), width=40, state='disabled')
        confirm_password_entry.pack()
        
        def toggle_password():
            state = 'normal' if cambiar_password_var.get() else 'disabled'
            password_entry.configure(state=state)
            confirm_password_entry.configure(state=state)
            if state == 'disabled':
                password_entry.delete(0, tk.END)
                confirm_password_entry.delete(0, tk.END)
        
        cambiar_password_var.trace('w', lambda *args: toggle_password())
        
        def actualizar():
            # Obtener valores
            valores = {}
            for field_name, widget in fields.items():
                valores[field_name] = widget.get().strip()
                if not valores[field_name]:
                    messagebox.showerror("Error", f"El campo {field_name} es obligatorio")
                    return
            
            # Verificar correo único
            for i, u in enumerate(usuarios):
                if i != indice and u['correo'] == valores["correo"]:
                    messagebox.showerror("Error", "Ya existe otro usuario con este correo")
                    return
            
            # Actualizar datos básicos
            usuario_encontrado['nombre'] = valores["nombre"]
            usuario_encontrado['apellido'] = valores["apellido"]
            usuario_encontrado['correo'] = valores["correo"]
            
            # Actualizar contraseña si se solicita
            if cambiar_password_var.get():
                password = password_entry.get()
                confirm_password = confirm_password_entry.get()
                
                if not password:
                    messagebox.showerror("Error", "Ingrese la nueva contraseña")
                    return
                
                es_valida, mensaje = self.validar_contrasena(password)
                if not es_valida:
                    messagebox.showerror("Error", f"Contraseña inválida: {mensaje}")
                    return
                
                if password != confirm_password:
                    messagebox.showerror("Error", "Las contraseñas no coinciden")
                    return
                
                usuario_encontrado['contraseña'] = self.hash_contrasena(password)
            
            usuarios[indice] = usuario_encontrado
            self.guardar_usuarios(usuarios)
            
            messagebox.showinfo("Éxito", "Usuario actualizado exitosamente")
            update_window.destroy()
            self.cargar_usuarios()
        
        tk.Button(update_window, text="Actualizar Usuario", command=actualizar,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def eliminar_usuario(self):
        if not self.usuarios_tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario de la lista")
            return
        
        selected_item = self.usuarios_tree.selection()[0]
        valores = self.usuarios_tree.item(selected_item)['values']
        nombre_completo = f"{valores[0]} {valores[1]}"
        cedula_usuario = str(valores[2]).strip()  # Asegurar que sea string y sin espacios
        
        print(f"Debug: Intentando eliminar usuario con cédula: '{cedula_usuario}'")  # Debug temporal
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar al usuario {nombre_completo}?"):
            usuarios = self.leer_usuarios()
            usuarios_originales = len(usuarios)
            
            # Filtrar usuarios - mantener solo los que NO coincidan con la cédula
            usuarios_filtrados = []
            for u in usuarios:
                usuario_cedula = str(u['cedula']).strip()
                if usuario_cedula != cedula_usuario:
                    usuarios_filtrados.append(u)
                else:
                    print(f"Debug: Eliminando usuario: {u['nombre']} {u['apellido']} - {usuario_cedula}")  # Debug temporal
            
            if len(usuarios_filtrados) == usuarios_originales:
                print(f"Debug: No se eliminó ningún usuario. Cédulas disponibles: {[u['cedula'] for u in usuarios]}")  # Debug temporal
                messagebox.showerror("Error", f"Usuario con cédula '{cedula_usuario}' no encontrado para eliminar")
            else:
                self.guardar_usuarios(usuarios_filtrados)
                messagebox.showinfo("Éxito", "Usuario eliminado exitosamente")
                self.cargar_usuarios()
    
    def cargar_usuarios(self):
        # Limpiar el treeview
        for item in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item)
        
        # Cargar usuarios
        usuarios = self.leer_usuarios()
        for usuario in usuarios:
            self.usuarios_tree.insert('', 'end', values=(
                usuario.get('nombre', 'N/A'),
                usuario.get('apellido', 'N/A'),
                usuario.get('cedula', 'N/A'),
                usuario.get('correo', 'N/A'),
                usuario.get('rol', 'N/A')
            ))
    
    # Métodos de reportes
    def mostrar_proyectos_en_reporte(self, proyectos, titulo="Reporte de Proyectos"):
        self.reportes_text.configure(state='normal')
        self.reportes_text.delete('1.0', tk.END)
        
        if not proyectos:
            self.reportes_text.insert('1.0', "No hay proyectos para mostrar.")
            self.reportes_text.configure(state='disabled')
            return
        
        contenido = f"===== {titulo} =====\n\n"
        for i, p in enumerate(proyectos, 1):
            tareas = p.get("tareas", [])
            total_tareas = len(tareas)
            tareas_completadas = sum(1 for t in tareas if t.get("estado") == "Completada")
            avance = (tareas_completadas / total_tareas) * 100 if total_tareas > 0 else 0
            
            contenido += f"--- Proyecto {i} ---\n"
            contenido += f"  Nombre: {p.get('proyecto', 'N/A')}\n"
            contenido += f"  Costo: {p.get('costo', 'N/A')}\n"
            contenido += f"  Categoría: {p.get('categoria', 'N/A')}\n"
            contenido += f"  Descripción: {p.get('descripcion', 'N/A')}\n"
            contenido += f"  Materiales: {p.get('materiales', 'N/A')}\n"
            contenido += f"  Fecha de Inicio: {p.get('fehceInicio', 'N/A')}\n"
            contenido += f"  Fecha de Fin: {p.get('fechaFin', 'N/A')}\n"
            resp = p.get("responsableProyecto", {})
            contenido += f"  Responsable: {resp.get('nombre', 'N/A')} (Cédula: {resp.get('cedula', 'N/A')})\n"
            contenido += f"  Avance: {avance:.2f}% ({tareas_completadas}/{total_tareas} tareas completadas)\n\n"
            
            contenido += "  Tareas:\n"
            if not tareas:
                contenido += "   - No hay tareas registradas.\n"
            else:
                for t in tareas:
                    r = t.get("responsable", {})
                    contenido += f"   - Nombre: {t.get('nombre', 'N/A')}\n"
                    contenido += f"     Descripción: {t.get('descripcion', 'N/A')}\n"
                    contenido += f"     Inicio: {t.get('fecha_inicio', 'N/A')} | Fin: {t.get('fecha_fin', 'N/A')}\n"
                    contenido += f"     Estado: {t.get('estado', 'N/A')}\n"
                    contenido += f"     Responsable: {r.get('nombre', 'N/A')}\n\n"
            contenido += "\n" + "="*50 + "\n\n"
        
        self.reportes_text.insert('1.0', contenido)
        self.reportes_text.configure(state='disabled')
    
    def ver_todos_proyectos(self):
        proyectos = self.cargar_proyectos()
        self.mostrar_proyectos_en_reporte(proyectos, "Todos los Proyectos")
    
    def buscar_proyecto_reporte(self):
        nombre_buscar = simpledialog.askstring("Buscar Proyecto", "Ingrese el nombre del proyecto a buscar:")
        if not nombre_buscar:
            return
        
        proyectos = self.cargar_proyectos()
        proyectos_filtrados = [p for p in proyectos if p.get('proyecto', '').lower() == nombre_buscar.strip().lower()]
        
        if proyectos_filtrados:
            self.mostrar_proyectos_en_reporte(proyectos_filtrados, f"Proyecto: {nombre_buscar}")
        else:
            messagebox.showinfo("Sin resultados", f"No se encontró el proyecto '{nombre_buscar}'")
    
    def generar_resumen(self):
        proyectos = self.cargar_proyectos()
        if not proyectos:
            messagebox.showinfo("Sin datos", "No hay proyectos registrados.")
            return
        
        self.reportes_text.configure(state='normal')
        self.reportes_text.delete('1.0', tk.END)
        
        contenido = "===== Resumen de Proyectos =====\n\n"
        for i, p in enumerate(proyectos, 1):
            tareas = p.get("tareas", [])
            total_tareas = len(tareas)
            tareas_completadas = sum(1 for t in tareas if t.get("estado") == "Completada")
            tareas_no_completadas = total_tareas - tareas_completadas
            avance = (tareas_completadas / total_tareas) * 100 if total_tareas > 0 else 0
            
            contenido += f"--- Proyecto {i}: {p.get('proyecto', 'N/A')} ---\n"
            contenido += f"  Total de tareas: {total_tareas}\n"
            contenido += f"  Tareas completadas: {tareas_completadas}\n"
            contenido += f"  Tareas no completadas: {tareas_no_completadas}\n"
            contenido += f"  Porcentaje de avance: {avance:.2f}%\n\n"
            
            contenido += "  Estado de las tareas:\n"
            if not tareas:
                contenido += "   - No hay tareas asignadas.\n"
            else:
                for t in tareas:
                    contenido += f"   - {t.get('nombre', 'N/A')}: {t.get('estado', 'N/A')}\n"
            contenido += "\n" + "="*40 + "\n\n"
        
        self.reportes_text.insert('1.0', contenido)
        self.reportes_text.configure(state='disabled')
    
    def ordenar_proyectos(self):
        # Ventana para seleccionar criterio de ordenamiento
        orden_window = tk.Toplevel(self.root)
        orden_window.title("Ordenar Proyectos")
        orden_window.geometry("300x200")
        orden_window.configure(bg='#f0f0f0')
        orden_window.transient(self.root)
        orden_window.grab_set()
        
        tk.Label(orden_window, text="Ordenar proyectos por:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=20)
        
        orden_var = tk.StringVar()
        opciones = [
            ("Nombre (Alfabético)", "nombre"),
            ("Fecha de inicio", "fecha"),
            ("Responsable", "responsable")
        ]
        
        for texto, valor in opciones:
            tk.Radiobutton(orden_window, text=texto, variable=orden_var, value=valor, 
                          font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=50)
        
        def aplicar_orden():
            criterio = orden_var.get()
            if not criterio:
                messagebox.showwarning("Advertencia", "Por favor seleccione un criterio")
                return
            
            proyectos = self.cargar_proyectos()
            if not proyectos:
                messagebox.showinfo("Sin datos", "No hay proyectos para ordenar")
                return
            
            proyectos_ordenados = proyectos[:]
            
            if criterio == "nombre":
                proyectos_ordenados.sort(key=lambda p: p.get('proyecto', '').lower())
                titulo = "Proyectos Ordenados por Nombre"
            elif criterio == "fecha":
                def parse_fecha(fecha_str):
                    try:
                        return datetime.strptime(fecha_str, '%d/%m/%Y')
                    except:
                        return datetime(1900, 1, 1)
                proyectos_ordenados.sort(key=lambda p: parse_fecha(p.get('fehceInicio', '01/01/1900')))
                titulo = "Proyectos Ordenados por Fecha de Inicio"
            elif criterio == "responsable":
                proyectos_ordenados.sort(key=lambda p: p.get('responsableProyecto', {}).get('nombre', '').lower())
                titulo = "Proyectos Ordenados por Responsable"
            
            orden_window.destroy()
            self.mostrar_proyectos_en_reporte(proyectos_ordenados, titulo)
        
        tk.Button(orden_window, text="Ordenar", command=aplicar_orden,
                 bg='#1abc9c', fg='white', font=('Arial', 10, 'bold')).pack(pady=20)
    
    def cerrar_sesion(self):
        if os.path.exists(ARCHIVO_SESION):
            os.remove(ARCHIVO_SESION)
        self.root.destroy()
        # Volver al login
        login = LoginWindow()
        login.run()
    
    def run(self):
        # Cargar datos iniciales
        self.cargar_usuarios()
        self.root.mainloop()

# Función principal para ejecutar la aplicación
def main():
    # Crear archivos si no existen
    if not os.path.exists(ARCHIVO_REGISTRO):
        # Crear usuario administrador por defecto
        admin_password = "Admin123!"
        salt = bcrypt.gensalt()
        hash_bytes = bcrypt.hashpw(admin_password.encode('utf-8'), salt)
        with open(ARCHIVO_REGISTRO, "w", encoding="utf-8") as f:
            f.write(f"Administrador,Sistema,1234567890,admin@sistema.com,{hash_bytes.decode('utf-8')},Administrador\n")
        print("Usuario administrador creado:")
        print("Correo: admin@sistema.com")
        print("Contraseña: Admin123!")
    
    if not os.path.exists(ARCHIVO_PROYECTOS):
        with open(ARCHIVO_PROYECTOS, "w", encoding="utf-8") as f:
            json.dump([], f)
    
    # Crear archivo de intentos fallidos si no existe
    if not os.path.exists(ARCHIVO_INTENTOS):
        with open(ARCHIVO_INTENTOS, "w", encoding="utf-8") as f:
            json.dump({}, f)
    
    # Iniciar aplicación
    app = LoginWindow()
    app.run()

if __name__ == "__main__":
    main()