import tkinter as tk
from tkinter import messagebox
import json
import os
import bcrypt
import random
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# Archivos de datos
archivoProyectos = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\proyectos.json"
archivoRegistro = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\registro.txt"
archivoSesion = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\sesion_actual.json"
archivoIntentos = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\intentos_fallidos.json"

# Configuración de correo
correoRemitente = "cristhianmy@icloud.com"
contrasenaRemitente = "zbbb-inqb-fqgv-hqpm"

class VentanaLogin:
    def __init__(self):
        self.ventanaPrincipal = tk.Tk()
        self.ventanaPrincipal.title("Gestor de Proyectos")
        self.ventanaPrincipal.geometry("500x500")
        self.ventanaPrincipal.configure(bg='#f0f0f0')
        
        # Variables
        self.usuarioActual = None
        
        self.crearInterfazLogin()
        
    def crearInterfazLogin(self):
        # Título principal
        marcoTitulo = tk.Frame(self.ventanaPrincipal, bg='#2c3e50', height=80)
        marcoTitulo.pack(fill='x', pady=(0, 20))
        marcoTitulo.pack_propagate(False)
        
        etiquetaTitulo = tk.Label(marcoTitulo, text="Equipo GMC", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#2c3e50')
        etiquetaTitulo.pack(pady=10)
        
        etiquetaSubtitulo = tk.Label(marcoTitulo, text="Gestor de Proyectos", 
                                 font=('Arial', 12), 
                                 fg='white', bg='#2c3e50')
        etiquetaSubtitulo.pack()
        
        # Marco principal
        marcoPrincipal = tk.Frame(self.ventanaPrincipal, bg='#f0f0f0')
        marcoPrincipal.pack(expand=True, fill='both', padx=40)
        
        # Formulario de login
        marcoLogin = tk.LabelFrame(marcoPrincipal, text="Iniciar Sesión", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#f0f0f0', padx=20, pady=20)
        marcoLogin.pack(pady=20, fill='x')
        
        # Email
        tk.Label(marcoLogin, text="Correo electrónico:", 
                font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        self.entradaEmail = tk.Entry(marcoLogin, font=('Arial', 10), width=40)
        self.entradaEmail.pack(pady=(0, 15))
        
        # Password
        tk.Label(marcoLogin, text="Contraseña:", 
                font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(0, 5))
        self.entradaContrasena = tk.Entry(marcoLogin, show="*", font=('Arial', 10), width=40)
        self.entradaContrasena.pack(pady=(0, 15))
        
        # Botones
        marcoBotones = tk.Frame(marcoLogin, bg='#f0f0f0')
        marcoBotones.pack(pady=10)
        
        botonLogin = tk.Button(marcoBotones, text="Iniciar Sesión", 
                             command=self.iniciarSesion,
                             bg='#3498db', fg='white', 
                             font=('Arial', 10, 'bold'),
                             padx=20, pady=5)
        botonLogin.pack(side='left', padx=(0, 10))
        
        botonCambiarContrasena = tk.Button(marcoBotones, text="Cambiar Contraseña", 
                                       command=self.cambiarContrasena,
                                       bg='#e74c3c', fg='white', 
                                       font=('Arial', 10, 'bold'),
                                       padx=20, pady=5)
        botonCambiarContrasena.pack(side='left')
        
        # Botón para desbloquear usuario
        botonDesbloquear = tk.Button(marcoLogin, text="Desbloquear Usuario", 
                              command=self.desbloquearUsuario,
                              bg='#f39c12', fg='white', 
                              font=('Arial', 10, 'bold'),
                              padx=20, pady=5)
        botonDesbloquear.pack(pady=10)
        
        # Bind Enter key to login
        self.ventanaPrincipal.bind('<Return>', lambda event: self.iniciarSesion())
    
    def cargarIntentosFallidos(self):
        """Carga los datos de intentos fallidos desde archivo"""
        if not os.path.exists(archivoIntentos):
            return {}
        try:
            with open(archivoIntentos, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def guardarIntentosFallidos(self, intentos):
        """Guarda los datos de intentos fallidos en archivo"""
        with open(archivoIntentos, "w", encoding="utf-8") as archivo:
            json.dump(intentos, archivo, ensure_ascii=False, indent=2)
    
    def registrarIntentoFallido(self, correo):
        """Registra un intento fallido de login"""
        intentos = self.cargarIntentosFallidos()
        ahora = datetime.now().isoformat()
        
        if correo not in intentos:
            intentos[correo] = {
                "contador": 0,
                "bloqueado": False,
                "fechaBloqueo": None,
                "ultimoIntento": None
            }
        
        intentos[correo]["contador"] += 1
        intentos[correo]["ultimoIntento"] = ahora
        
        # Bloquear después de 3 intentos
        if intentos[correo]["contador"] >= 3:
            intentos[correo]["bloqueado"] = True
            intentos[correo]["fechaBloqueo"] = ahora
        
        self.guardarIntentosFallidos(intentos)
        return intentos[correo]
    
    def verificarUsuarioBloqueado(self, correo):
        """Verifica si un usuario está bloqueado"""
        intentos = self.cargarIntentosFallidos()
        
        if correo not in intentos:
            return False, None
        
        datosUsuario = intentos[correo]
        if not datosUsuario.get("bloqueado", False):
            return False, None
        
        return True, datosUsuario
    
    def resetearIntentosFallidos(self, correo):
        """Resetea los intentos fallidos de un usuario"""
        intentos = self.cargarIntentosFallidos()
        if correo in intentos:
            intentos[correo] = {
                "contador": 0,
                "bloqueado": False,
                "fechaBloqueo": None,
                "ultimoIntento": None
            }
            self.guardarIntentosFallidos(intentos)
        
    def obtenerDatosUsuarioPorCorreo(self, correo):
        try:
            with open(archivoRegistro, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if len(datos) > 5 and datos[3].strip().lower() == correo.strip().lower():
                        return {
                            "nombre": f"{datos[0].strip()} {datos[1].strip()}",
                            "cedula": datos[2].strip(),
                            "correo": datos[3].strip(),
                            "contrasenaHash": datos[4].strip(),
                            "rol": datos[5].strip()
                        }
        except FileNotFoundError:
            return None
        return None
    
    def guardarSesion(self, datosUsuario):
        with open(archivoSesion, "w", encoding="utf-8") as archivo:
            json.dump(datosUsuario, archivo, ensure_ascii=False, indent=2)
    
    def iniciarSesion(self):
        correo = self.entradaEmail.get().strip()
        contrasena = self.entradaContrasena.get()
        
        if not correo or not contrasena:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        # Verificar si el usuario está bloqueado
        estaBloqueado, datosBloqueo = self.verificarUsuarioBloqueado(correo)
        if estaBloqueado:
            fechaBloqueo = datetime.fromisoformat(datosBloqueo["fechaBloqueo"])
            messagebox.showerror("Usuario Bloqueado", 
                               f"Su cuenta está bloqueada por múltiples intentos fallidos.\n"
                               f"Fecha de bloqueo: {fechaBloqueo.strftime('%d/%m/%Y %H:%M:%S')}\n"
                               f"Use 'Desbloquear Usuario' para recuperar el acceso.")
            return
        
        datosUsuario = self.obtenerDatosUsuarioPorCorreo(correo)
        
        if datosUsuario:
            try:
                if bcrypt.checkpw(contrasena.encode('utf-8'), datosUsuario['contrasenaHash'].encode('utf-8')):
                    # Login exitoso - resetear intentos fallidos
                    self.resetearIntentosFallidos(correo)
                    
                    messagebox.showinfo("Éxito", f"¡Bienvenido, {datosUsuario['nombre']}!")
                    self.guardarSesion(datosUsuario)
                    
                    self.ventanaPrincipal.destroy()
                    
                    if datosUsuario['rol'].lower() == 'estudiante':
                        from estudiante import AplicacionEstudiante
                        aplicacion = AplicacionEstudiante(datosUsuario)
                        aplicacion.ejecutar()
                    elif datosUsuario['rol'].lower() == 'administrador':
                        from administrador import AplicacionAdministrador
                        aplicacion = AplicacionAdministrador(datosUsuario)
                        aplicacion.ejecutar()
                    else:
                        messagebox.showerror("Error", "Rol de usuario no reconocido")
                else:
                    # Contraseña incorrecta - registrar intento fallido
                    datosIntento = self.registrarIntentoFallido(correo)
                    intentosRestantes = 3 - datosIntento["contador"]
                    
                    if datosIntento["bloqueado"]:
                        messagebox.showerror("Usuario Bloqueado", 
                                           "Su cuenta ha sido bloqueada por múltiples intentos fallidos.\n"
                                           "Use 'Desbloquear Usuario' para recuperar el acceso.")
                    else:
                        messagebox.showerror("Error", 
                                           f"Credenciales inválidas.\n"
                                           f"Intentos restantes: {intentosRestantes}")
            except Exception as e:
                messagebox.showerror("Error", "Error de autenticación. Contacte al administrador.")
        else:
            # Usuario no existe - también registrar como intento fallido
            datosIntento = self.registrarIntentoFallido(correo)
            intentosRestantes = 3 - datosIntento["contador"]
            
            if datosIntento["bloqueado"]:
                messagebox.showerror("Usuario Bloqueado", 
                                   "Esta dirección ha sido bloqueada por múltiples intentos fallidos.\n"
                                   "Use 'Desbloquear Usuario' para recuperar el acceso.")
            else:
                messagebox.showerror("Error", 
                                   f"Credenciales inválidas.\n"
                                   f"Intentos restantes: {intentosRestantes}")
    
    def desbloquearUsuario(self):
        """Proceso para desbloquear un usuario bloqueado"""
        # Ventana para solicitar correo
        ventanaDesbloqueo = tk.Toplevel(self.ventanaPrincipal)
        ventanaDesbloqueo.title("Desbloquear Usuario")
        ventanaDesbloqueo.geometry("400x400")
        ventanaDesbloqueo.configure(bg='#f0f0f0')
        ventanaDesbloqueo.transient(self.ventanaPrincipal)
        ventanaDesbloqueo.grab_set()
        
        tk.Label(ventanaDesbloqueo, text="Desbloquear Cuenta de Usuario", 
                font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=20)
        
        tk.Label(ventanaDesbloqueo, text="Ingrese el correo electrónico bloqueado:", 
                font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
        
        entradaEmail = tk.Entry(ventanaDesbloqueo, font=('Arial', 10), width=40)
        entradaEmail.pack(pady=5)
        
        def procesarDesbloqueo():
            correoDestino = entradaEmail.get().strip()
            
            if not correoDestino:
                messagebox.showerror("Error", "Ingrese un correo electrónico")
                return
            
            # Verificar que el correo existe en el sistema
            datosUsuario = self.obtenerDatosUsuarioPorCorreo(correoDestino)
            if not datosUsuario:
                messagebox.showerror("Error", "Correo no encontrado en el sistema")
                return
            
            # Verificar que el usuario esté bloqueado
            estaBloqueado, datosBloqueo = self.verificarUsuarioBloqueado(correoDestino)
            if not estaBloqueado:
                messagebox.showinfo("Información", "Este usuario no está bloqueado")
                return
            
            # Generar código de desbloqueo
            codigoDesbloqueo = str(random.randint(100000, 999999))
            
            if not self.enviarCorreoDesbloqueo(correoDestino, codigoDesbloqueo):
                return
            
            # Ventana para ingresar código
            ventanaCodigo = tk.Toplevel(ventanaDesbloqueo)
            ventanaCodigo.title("Código de Desbloqueo")
            ventanaCodigo.geometry("350x250")
            ventanaCodigo.configure(bg='#f0f0f0')
            ventanaCodigo.transient(ventanaDesbloqueo)
            ventanaCodigo.grab_set()
            
            tk.Label(ventanaCodigo, text="Código de Desbloqueo", 
                    font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=10)
            
            tk.Label(ventanaCodigo, text="Se ha enviado un código a su correo electrónico.", 
                    font=('Arial', 10), bg='#f0f0f0').pack(pady=5)
            
            tk.Label(ventanaCodigo, text="Ingrese el código para desbloquear su cuenta:", 
                    font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
            
            entradaCodigo = tk.Entry(ventanaCodigo, font=('Arial', 12), width=20, justify='center')
            entradaCodigo.pack(pady=5)
            
            def verificarCodigoDesbloqueo():
                codigoIngresado = entradaCodigo.get().strip()
                
                if codigoIngresado == codigoDesbloqueo:
                    # Desbloquear usuario
                    self.resetearIntentosFallidos(correoDestino)
                    messagebox.showinfo("Éxito", 
                                      f"Cuenta desbloqueada exitosamente.\n"
                                      f"Ya puede iniciar sesión normalmente.")
                    ventanaCodigo.destroy()
                    ventanaDesbloqueo.destroy()
                else:
                    messagebox.showerror("Error", "Código de desbloqueo incorrecto")
                    entradaCodigo.delete(0, tk.END)
            
            tk.Button(ventanaCodigo, text="Verificar y Desbloquear", 
                     command=verificarCodigoDesbloqueo,
                     bg='#2ecc71', fg='white', 
                     font=('Arial', 10, 'bold'), padx=20, pady=5).pack(pady=15)
            
            tk.Button(ventanaCodigo, text="Cancelar", 
                     command=ventanaCodigo.destroy,
                     bg='#95a5a6', fg='white', 
                     font=('Arial', 10, 'bold'), padx=20, pady=5).pack()
        
        tk.Button(ventanaDesbloqueo, text="Enviar Código de Desbloqueo", 
                 command=procesarDesbloqueo,
                 bg='#f39c12', fg='white', 
                 font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
        
        tk.Button(ventanaDesbloqueo, text="Cancelar", 
                 command=ventanaDesbloqueo.destroy,
                 bg='#95a5a6', fg='white', 
                 font=('Arial', 10, 'bold'), padx=20, pady=5).pack()
    
    def enviarCorreoDesbloqueo(self, destinatario, codigo):
        """Envía correo con código de desbloqueo"""
        try:
            mensaje = EmailMessage()
            mensaje["From"] = correoRemitente
            mensaje["To"] = destinatario
            mensaje["Subject"] = "Código de desbloqueo de cuenta - GMC"
            
            cuerpoCorreo = f"""
            Hola,

            Su cuenta ha sido bloqueada por múltiples intentos de acceso fallidos.

            Para desbloquear su cuenta, use el siguiente código:

            {codigo}

            Si no solicitó este desbloqueo, ignore este correo y contacte al administrador del sistema.

            Saludos,
            Sistema de Gestión de Proyectos
            GMC DESARROLLADORES
            """
            mensaje.set_content(cuerpoCorreo, charset="utf-8")
            
            contexto = ssl.create_default_context()
            servidorSmtp = "smtp.mail.me.com"
            puertoSmtp = 587
            
            with smtplib.SMTP(servidorSmtp, puertoSmtp) as smtp:
                smtp.starttls(context=contexto)
                smtp.login(correoRemitente, contrasenaRemitente)
                smtp.sendmail(correoRemitente, destinatario, mensaje.as_string())
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar correo de desbloqueo: {str(e)}")
            return False
    
    def enviarCorreoConCodigo(self, destinatario, codigo):
        try:
            mensaje = EmailMessage()
            mensaje["From"] = correoRemitente
            mensaje["To"] = destinatario
            mensaje["Subject"] = "Código de seguridad para cambiar tu contraseña"
            
            cuerpoCorreo = f"""
            Hola,

            Para cambiar tu contraseña, usa el siguiente código de seguridad:

            {codigo}

            Si no solicitaste este cambio, ignora este correo.

            Saludos,
            Equipo de soporte GMC.
            """
            mensaje.set_content(cuerpoCorreo, charset="utf-8")
            
            contexto = ssl.create_default_context()
            servidorSmtp = "smtp.mail.me.com"
            puertoSmtp = 587
            
            with smtplib.SMTP(servidorSmtp, puertoSmtp) as smtp:
                smtp.starttls(context=contexto)
                smtp.login(correoRemitente, contrasenaRemitente)
                smtp.sendmail(correoRemitente, destinatario, mensaje.as_string())
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar correo: {str(e)}")
            return False
    
    def cambiarContrasena(self):
        # Ventana para cambiar contraseña
        ventanaCambio = tk.Toplevel(self.ventanaPrincipal)
        ventanaCambio.title("Cambiar Contraseña")
        ventanaCambio.geometry("400x300")
        ventanaCambio.configure(bg='#f0f0f0')
        ventanaCambio.transient(self.ventanaPrincipal)
        ventanaCambio.grab_set()
        
        tk.Label(ventanaCambio, text="Ingrese el correo del usuario:", 
                font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
        
        entradaEmail = tk.Entry(ventanaCambio, font=('Arial', 10), width=40)
        entradaEmail.pack(pady=5)
        
        def procesarCambio():
            correoDestino = entradaEmail.get().strip()
            datosUsuario = self.obtenerDatosUsuarioPorCorreo(correoDestino)
            
            if not datosUsuario:
                messagebox.showerror("Error", "Correo no encontrado")
                return
            
            # Verificar si está bloqueado
            estaBloqueado, _ = self.verificarUsuarioBloqueado(correoDestino)
            if estaBloqueado:
                messagebox.showerror("Error", "Este usuario está bloqueado. Use 'Desbloquear Usuario' primero.")
                return
            
            codigoSeguridad = str(random.randint(100000, 999999))
            
            if not self.enviarCorreoConCodigo(datosUsuario['correo'], codigoSeguridad):
                return
            
            # Ventana para ingresar código
            ventanaCodigo = tk.Toplevel(ventanaCambio)
            ventanaCodigo.title("Código de Seguridad")
            ventanaCodigo.geometry("350x200")
            ventanaCodigo.configure(bg='#f0f0f0')
            ventanaCodigo.transient(ventanaCambio)
            ventanaCodigo.grab_set()
            
            tk.Label(ventanaCodigo, text="Ingrese el código enviado a su correo:", 
                    font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
            
            entradaCodigo = tk.Entry(ventanaCodigo, font=('Arial', 10), width=20)
            entradaCodigo.pack(pady=5)
            
            def verificarCodigo():
                if entradaCodigo.get() == codigoSeguridad:
                    ventanaCodigo.destroy()
                    self.mostrarVentanaNuevaContrasena(ventanaCambio, correoDestino)
                else:
                    messagebox.showerror("Error", "Código incorrecto")
            
            tk.Button(ventanaCodigo, text="Verificar", command=verificarCodigo,
                     bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)
        
        tk.Button(ventanaCambio, text="Enviar Código", command=procesarCambio,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=20)
    
    def mostrarVentanaNuevaContrasena(self, ventanaPadre, correo):
        # Ventana para nueva contraseña
        ventanaNuevaContrasena = tk.Toplevel(ventanaPadre)
        ventanaNuevaContrasena.title("Nueva Contraseña")
        ventanaNuevaContrasena.geometry("400x250")
        ventanaNuevaContrasena.configure(bg='#f0f0f0')
        ventanaNuevaContrasena.transient(ventanaPadre)
        ventanaNuevaContrasena.grab_set()
        
        tk.Label(ventanaNuevaContrasena, text="Nueva contraseña:", 
                font=('Arial', 10), bg='#f0f0f0').pack(pady=(20, 5))
        
        entradaNuevaContrasena = tk.Entry(ventanaNuevaContrasena, show="*", font=('Arial', 10), width=30)
        entradaNuevaContrasena.pack(pady=5)
        
        tk.Label(ventanaNuevaContrasena, text="Confirmar contraseña:", 
                font=('Arial', 10), bg='#f0f0f0').pack(pady=(10, 5))
        
        entradaConfirmarContrasena = tk.Entry(ventanaNuevaContrasena, show="*", font=('Arial', 10), width=30)
        entradaConfirmarContrasena.pack(pady=5)
        
        def guardarNuevaContrasena():
            nueva = entradaNuevaContrasena.get()
            confirmar = entradaConfirmarContrasena.get()
            
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
                with open(archivoRegistro, "r", encoding="utf-8") as archivo:
                    lineas = archivo.readlines()
                
                sal = bcrypt.gensalt()
                hashBytes = bcrypt.hashpw(nueva.encode("utf-8"), sal)
                
                for i, linea in enumerate(lineas):
                    datos = linea.strip().split(",")
                    if datos[3].strip().lower() == correo.lower():
                        datos[4] = hashBytes.decode("utf-8")
                        lineas[i] = ",".join(datos) + "\n"
                        break
                
                with open(archivoRegistro, "w", encoding="utf-8") as archivo:
                    archivo.writelines(lineas)
                
                # Resetear intentos fallidos también
                self.resetearIntentosFallidos(correo)
                
                messagebox.showinfo("Éxito", "Contraseña actualizada y cuenta desbloqueada exitosamente")
                ventanaNuevaContrasena.destroy()
                ventanaPadre.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar contraseña: {str(e)}")
        
        tk.Button(ventanaNuevaContrasena, text="Guardar", command=guardarNuevaContrasena,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold')).pack(pady=20)
    
    def ejecutar(self):
        self.ventanaPrincipal.mainloop()

# Función principal para ejecutar la aplicación
def main():
    # Crear archivos si no existen
    if not os.path.exists(archivoRegistro):
        # Crear usuario administrador por defecto
        contrasenaAdmin = "Admin123!"
        sal = bcrypt.gensalt()
        hashBytes = bcrypt.hashpw(contrasenaAdmin.encode('utf-8'), sal)
        with open(archivoRegistro, "w", encoding="utf-8") as archivo:
            archivo.write(f"Administrador,Sistema,1234567890,admin@sistema.com,{hashBytes.decode('utf-8')},Administrador\n")
        print("Usuario administrador creado:")
        print("Correo: admin@sistema.com")
        print("Contraseña: Admin123!")
    
    if not os.path.exists(archivoProyectos):
        with open(archivoProyectos, "w", encoding="utf-8") as archivo:
            json.dump([], archivo)
    
    # Crear archivo de intentos fallidos si no existe
    if not os.path.exists(archivoIntentos):
        with open(archivoIntentos, "w", encoding="utf-8") as archivo:
            json.dump({}, archivo)
    
    # Iniciar aplicación
    aplicacion = VentanaLogin()
    aplicacion.ejecutar()

if __name__ == "__main__":
    main()