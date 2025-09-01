import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import json
import os
import bcrypt
import re

# Archivos de datos (usando las mismas rutas que en inicio.py)
archivoProyectos = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\proyectos.json"
archivoRegistro = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\registro.txt"
archivoSesion = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\sesion_actual.json"

class AplicacionAdministrador:
    def __init__(self, usuarioActual):
        self.usuarioActual = usuarioActual
        self.ventanaPrincipal = tk.Tk()
        self.ventanaPrincipal.title(f"Sistema de Administración - {usuarioActual['nombre']}")
        self.ventanaPrincipal.geometry("1000x700")
        self.ventanaPrincipal.configure(bg='#f0f0f0')
        
        self.crearInterfaz()
    
    def crearInterfaz(self):
        # Header
        marcoEncabezado = tk.Frame(self.ventanaPrincipal, bg='#2c3e50', height=60)
        marcoEncabezado.pack(fill='x')
        marcoEncabezado.pack_propagate(False)
        
        tk.Label(marcoEncabezado, text=f"Sistema de Administración - {self.usuarioActual['nombre']}", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=15)
        
        botonCerrarSesion = tk.Button(marcoEncabezado, text="Cerrar Sesión", 
                              command=self.cerrarSesion,
                              bg='#e74c3c', fg='white', 
                              font=('Arial', 10, 'bold'))
        botonCerrarSesion.pack(side='right', padx=20, pady=15)
        
        # Notebook para pestañas
        self.cuadernoPestanas = ttk.Notebook(self.ventanaPrincipal)
        self.cuadernoPestanas.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Pestaña de Usuarios
        self.crearPestanaUsuarios()
        
        # Pestaña de Reportes
        self.crearPestanaReportes()
    
    def crearPestanaUsuarios(self):
        marcoUsuarios = ttk.Frame(self.cuadernoPestanas)
        self.cuadernoPestanas.add(marcoUsuarios, text="Gestión de Usuarios")
        
        # Botones principales
        marcoBotones = tk.Frame(marcoUsuarios, bg='#f0f0f0')
        marcoBotones.pack(fill='x', padx=10, pady=10)
        
        tk.Button(marcoBotones, text="Registrar Usuario", command=self.registrarUsuario,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Actualizar Usuario", command=self.actualizarUsuario,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Eliminar Usuario", command=self.eliminarUsuario,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Actualizar Lista", command=self.cargarUsuarios,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Lista de usuarios
        marcoLista = tk.Frame(marcoUsuarios, bg='#f0f0f0')
        marcoLista.pack(expand=True, fill='both', padx=10, pady=10)
        
        tk.Label(marcoLista, text="Lista de Usuarios:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        # Treeview para mostrar usuarios
        columnas = ('Nombre', 'Apellido', 'Cédula', 'Correo', 'Rol')
        self.arbolUsuarios = ttk.Treeview(marcoLista, columns=columnas, show='headings', height=15)
        
        for columna in columnas:
            self.arbolUsuarios.heading(columna, text=columna)
            self.arbolUsuarios.column(columna, width=150)
        
        barraDesplazamientoUsuarios = ttk.Scrollbar(marcoLista, orient='vertical', command=self.arbolUsuarios.yview)
        self.arbolUsuarios.configure(yscrollcommand=barraDesplazamientoUsuarios.set)
        
        self.arbolUsuarios.pack(side='left', expand=True, fill='both')
        barraDesplazamientoUsuarios.pack(side='right', fill='y')
    
    def crearPestanaReportes(self):
        marcoReportes = ttk.Frame(self.cuadernoPestanas)
        self.cuadernoPestanas.add(marcoReportes, text="Reportes de Proyectos")
        
        # Botones de reportes
        marcoBotones = tk.Frame(marcoReportes, bg='#f0f0f0')
        marcoBotones.pack(fill='x', padx=10, pady=10)
        
        tk.Button(marcoBotones, text="Todos los Proyectos", command=self.verTodosProyectos,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Buscar Proyecto", command=self.buscarProyectoReporte,
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Resumen de Proyectos", command=self.generarResumen,
                 bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Ordenar Proyectos", command=self.ordenarProyectos,
                 bg='#1abc9c', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Área de reportes
        marcoTextoReportes = tk.Frame(marcoReportes, bg='#f0f0f0')
        marcoTextoReportes.pack(expand=True, fill='both', padx=10, pady=10)
        
        tk.Label(marcoTextoReportes, text="Reportes de Proyectos:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        # Text widget con scrollbar
        self.textoReportes = tk.Text(marcoTextoReportes, font=('Arial', 10), wrap='word')
        barraDesplazamientoReportes = ttk.Scrollbar(marcoTextoReportes, orient='vertical', command=self.textoReportes.yview)
        self.textoReportes.configure(yscrollcommand=barraDesplazamientoReportes.set)
        
        self.textoReportes.pack(side='left', expand=True, fill='both')
        barraDesplazamientoReportes.pack(side='right', fill='y')
    
    # Métodos auxiliares
    def validarCedula(self, cedula):
        return len(cedula) == 10 and cedula.isdigit()
    
    def validarContrasena(self, contrasena):
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
    
    def hashContrasena(self, contrasena):
        sal = bcrypt.gensalt()
        hashBytes = bcrypt.hashpw(contrasena.encode('utf-8'), sal)
        return hashBytes.decode('utf-8')
    
    def leerUsuarios(self):
        if not os.path.exists(archivoRegistro):
            return []
        usuarios = []
        try:
            with open(archivoRegistro, "r", encoding="utf-8") as archivo:
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
                            "contrasena": datos[4].strip(),
                            "rol": datos[5].strip()
                        }
                        usuarios.append(usuario)
        except Exception as e:
            print(f"Error al leer usuarios: {e}")
            messagebox.showerror("Error", f"Error al leer archivo de usuarios: {e}")
        
        return usuarios
    
    def guardarUsuarios(self, usuarios):
        with open(archivoRegistro, "w", encoding="utf-8") as archivo:
            for usuario in usuarios:
                archivo.write(f"{usuario['nombre']},{usuario['apellido']},{usuario['cedula']},{usuario['correo']},{usuario['contrasena']},{usuario['rol']}\n")
    
    def cargarProyectos(self):
        if not os.path.exists(archivoProyectos) or os.stat(archivoProyectos).st_size == 0:
            return []
        try:
            with open(archivoProyectos, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def calcularAvanceProyecto(self, proyecto):
        tareas = proyecto.get("tareas", [])
        if not tareas:
            return 0
        tareasCompletadas = [t for t in tareas if t.get("estado") == "Completada"]
        return (len(tareasCompletadas) / len(tareas)) * 100
    
    # Métodos de gestión de usuarios
    def registrarUsuario(self):
        # Ventana para registrar usuario
        ventanaRegistrar = tk.Toplevel(self.ventanaPrincipal)
        ventanaRegistrar.title("Registrar Nuevo Usuario")
        ventanaRegistrar.geometry("450x500")
        ventanaRegistrar.configure(bg='#f0f0f0')
        ventanaRegistrar.transient(self.ventanaPrincipal)
        ventanaRegistrar.grab_set()
        
        # Variables
        campos = {}
        
        # Campos del formulario
        camposFormulario = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Cédula de identidad:", "cedula"),
            ("Correo electrónico:", "correo")
        ]
        
        for textoEtiqueta, nombreCampo in camposFormulario:
            tk.Label(ventanaRegistrar, text=textoEtiqueta, font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
            campos[nombreCampo] = tk.Entry(ventanaRegistrar, font=('Arial', 10), width=40)
            campos[nombreCampo].pack(padx=20, pady=(0, 5))
        
        # Contraseña
        tk.Label(ventanaRegistrar, text="Contraseña:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        entradaContrasena = tk.Entry(ventanaRegistrar, show="*", font=('Arial', 10), width=40)
        entradaContrasena.pack(padx=20, pady=(0, 5))
        
        tk.Label(ventanaRegistrar, text="Confirmar contraseña:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        entradaConfirmarContrasena = tk.Entry(ventanaRegistrar, show="*", font=('Arial', 10), width=40)
        entradaConfirmarContrasena.pack(padx=20, pady=(0, 5))
        
        # Rol
        tk.Label(ventanaRegistrar, text="Rol:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        variableRol = tk.StringVar()
        marcoRol = tk.Frame(ventanaRegistrar, bg='#f0f0f0')
        marcoRol.pack(anchor='w', padx=20)
        
        tk.Radiobutton(marcoRol, text="Administrador", variable=variableRol, value="Administrador", 
                      font=('Arial', 10), bg='#f0f0f0').pack(side='left', padx=(0, 20))
        tk.Radiobutton(marcoRol, text="Estudiante", variable=variableRol, value="Estudiante", 
                      font=('Arial', 10), bg='#f0f0f0').pack(side='left')
        
        def guardarUsuario():
            # Validar campos
            valores = {}
            for nombreCampo, widget in campos.items():
                valores[nombreCampo] = widget.get().strip()
                if not valores[nombreCampo]:
                    messagebox.showerror("Error", f"El campo {nombreCampo} es obligatorio")
                    return
            
            contrasena = entradaContrasena.get()
            confirmarContrasena = entradaConfirmarContrasena.get()
            rol = variableRol.get()
            
            if not contrasena:
                messagebox.showerror("Error", "La contraseña es obligatoria")
                return
            
            if not rol:
                messagebox.showerror("Error", "Debe seleccionar un rol")
                return
            
            # Validar cédula
            if not self.validarCedula(valores["cedula"]):
                messagebox.showerror("Error", "Cédula inválida. Debe tener 10 dígitos.")
                return
            
            # Validar contraseña
            esValida, mensaje = self.validarContrasena(contrasena)
            if not esValida:
                messagebox.showerror("Error", f"Contraseña inválida: {mensaje}")
                return
            
            if contrasena != confirmarContrasena:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            # Verificar que no exista usuario con la misma cédula o correo
            usuariosExistentes = self.leerUsuarios()
            for usuario in usuariosExistentes:
                if usuario['cedula'] == valores["cedula"]:
                    messagebox.showerror("Error", "Ya existe un usuario con esta cédula")
                    return
                if usuario['correo'] == valores["correo"]:
                    messagebox.showerror("Error", "Ya existe un usuario con este correo")
                    return
            
            # Crear usuario
            hashCadena = self.hashContrasena(contrasena)
            with open(archivoRegistro, "a", encoding="utf-8") as archivo:
                archivo.write(f"{valores['nombre']},{valores['apellido']},{valores['cedula']},{valores['correo']},{hashCadena},{rol}\n")
            
            messagebox.showinfo("Éxito", "Usuario registrado exitosamente")
            ventanaRegistrar.destroy()
            self.cargarUsuarios()
        
        tk.Button(ventanaRegistrar, text="Registrar Usuario", command=guardarUsuario,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def actualizarUsuario(self):
        if not self.arbolUsuarios.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario de la lista")
            return
        
        elementoSeleccionado = self.arbolUsuarios.selection()[0]
        valores = self.arbolUsuarios.item(elementoSeleccionado)['values']
        cedulaUsuario = str(valores[2]).strip()
        
        usuarios = self.leerUsuarios()
        usuarioEncontrado = None
        indice = None
        
        for i, usuario in enumerate(usuarios):
            usuarioCedula = str(usuario["cedula"]).strip()
            
            if usuarioCedula == cedulaUsuario:
                usuarioEncontrado = usuario
                indice = i
                break
        
        if not usuarioEncontrado:
            messagebox.showerror("Error", f"Usuario con cédula '{cedulaUsuario}' no encontrado")
            return
        
        # Ventana para actualizar usuario
        ventanaActualizar = tk.Toplevel(self.ventanaPrincipal)
        ventanaActualizar.title("Actualizar Usuario")
        ventanaActualizar.geometry("450x400")
        ventanaActualizar.configure(bg='#f0f0f0')
        ventanaActualizar.transient(self.ventanaPrincipal)
        ventanaActualizar.grab_set()
        
        # Variables
        campos = {}
        
        # Campos del formulario con valores actuales
        camposFormulario = [
            ("Nombre:", "nombre", usuarioEncontrado['nombre']),
            ("Apellido:", "apellido", usuarioEncontrado['apellido']),
            ("Correo electrónico:", "correo", usuarioEncontrado['correo'])
        ]
        
        for textoEtiqueta, nombreCampo, valorActual in camposFormulario:
            tk.Label(ventanaActualizar, text=textoEtiqueta, font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
            campos[nombreCampo] = tk.Entry(ventanaActualizar, font=('Arial', 10), width=40)
            campos[nombreCampo].insert(0, valorActual)
            campos[nombreCampo].pack(padx=20, pady=(0, 5))
        
        # Checkbox para cambiar contraseña
        variableCambiarContrasena = tk.BooleanVar()
        tk.Checkbutton(ventanaActualizar, text="Cambiar contraseña", variable=variableCambiarContrasena, 
                      font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
        
        # Contraseña (inicialmente deshabilitada)
        marcoContrasena = tk.Frame(ventanaActualizar, bg='#f0f0f0')
        marcoContrasena.pack(fill='x', padx=20, pady=5)
        
        tk.Label(marcoContrasena, text="Nueva contraseña:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w')
        entradaContrasena = tk.Entry(marcoContrasena, show="*", font=('Arial', 10), width=40, state='disabled')
        entradaContrasena.pack()
        
        tk.Label(marcoContrasena, text="Confirmar contraseña:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', pady=(5, 0))
        entradaConfirmarContrasena = tk.Entry(marcoContrasena, show="*", font=('Arial', 10), width=40, state='disabled')
        entradaConfirmarContrasena.pack()
        
        def alternarContrasena():
            estado = 'normal' if variableCambiarContrasena.get() else 'disabled'
            entradaContrasena.configure(state=estado)
            entradaConfirmarContrasena.configure(state=estado)
            if estado == 'disabled':
                entradaContrasena.delete(0, tk.END)
                entradaConfirmarContrasena.delete(0, tk.END)
        
        variableCambiarContrasena.trace('w', lambda *args: alternarContrasena())
        
        def actualizar():
            # Obtener valores
            valores = {}
            for nombreCampo, widget in campos.items():
                valores[nombreCampo] = widget.get().strip()
                if not valores[nombreCampo]:
                    messagebox.showerror("Error", f"El campo {nombreCampo} es obligatorio")
                    return
            
            # Verificar correo único
            for i, usuario in enumerate(usuarios):
                if i != indice and usuario['correo'] == valores["correo"]:
                    messagebox.showerror("Error", "Ya existe otro usuario con este correo")
                    return
            
            # Actualizar datos básicos
            usuarioEncontrado['nombre'] = valores["nombre"]
            usuarioEncontrado['apellido'] = valores["apellido"]
            usuarioEncontrado['correo'] = valores["correo"]
            
            # Actualizar contraseña si se solicita
            if variableCambiarContrasena.get():
                contrasena = entradaContrasena.get()
                confirmarContrasena = entradaConfirmarContrasena.get()
                
                if not contrasena:
                    messagebox.showerror("Error", "Ingrese la nueva contraseña")
                    return
                
                esValida, mensaje = self.validarContrasena(contrasena)
                if not esValida:
                    messagebox.showerror("Error", f"Contraseña inválida: {mensaje}")
                    return
                
                if contrasena != confirmarContrasena:
                    messagebox.showerror("Error", "Las contraseñas no coinciden")
                    return
                
                usuarioEncontrado['contrasena'] = self.hashContrasena(contrasena)
            
            usuarios[indice] = usuarioEncontrado
            self.guardarUsuarios(usuarios)
            
            messagebox.showinfo("Éxito", "Usuario actualizado exitosamente")
            ventanaActualizar.destroy()
            self.cargarUsuarios()
        
        tk.Button(ventanaActualizar, text="Actualizar Usuario", command=actualizar,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def eliminarUsuario(self):
        if not self.arbolUsuarios.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario de la lista")
            return
        
        elementoSeleccionado = self.arbolUsuarios.selection()[0]
        valores = self.arbolUsuarios.item(elementoSeleccionado)['values']
        nombreCompleto = f"{valores[0]} {valores[1]}"
        cedulaUsuario = str(valores[2]).strip()
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar al usuario {nombreCompleto}?"):
            usuarios = self.leerUsuarios()
            usuariosOriginales = len(usuarios)
            
            # Filtrar usuarios - mantener solo los que NO coincidan con la cédula
            usuariosFiltrados = []
            for usuario in usuarios:
                usuarioCedula = str(usuario['cedula']).strip()
                if usuarioCedula != cedulaUsuario:
                    usuariosFiltrados.append(usuario)
            
            if len(usuariosFiltrados) == usuariosOriginales:
                messagebox.showerror("Error", f"Usuario con cédula '{cedulaUsuario}' no encontrado para eliminar")
            else:
                self.guardarUsuarios(usuariosFiltrados)
                messagebox.showinfo("Éxito", "Usuario eliminado exitosamente")
                self.cargarUsuarios()
    
    def cargarUsuarios(self):
        # Limpiar el treeview
        for elemento in self.arbolUsuarios.get_children():
            self.arbolUsuarios.delete(elemento)
        
        # Cargar usuarios
        usuarios = self.leerUsuarios()
        for usuario in usuarios:
            self.arbolUsuarios.insert('', 'end', values=(
                usuario.get('nombre', 'N/A'),
                usuario.get('apellido', 'N/A'),
                usuario.get('cedula', 'N/A'),
                usuario.get('correo', 'N/A'),
                usuario.get('rol', 'N/A')
            ))
    
    # Métodos de reportes
    def mostrarProyectosEnReporte(self, proyectos, titulo="Reporte de Proyectos"):
        self.textoReportes.configure(state='normal')
        self.textoReportes.delete('1.0', tk.END)
        
        if not proyectos:
            self.textoReportes.insert('1.0', "No hay proyectos para mostrar.")
            self.textoReportes.configure(state='disabled')
            return
        
        contenido = f"===== {titulo} =====\n\n"
        for i, proyecto in enumerate(proyectos, 1):
            tareas = proyecto.get("tareas", [])
            totalTareas = len(tareas)
            tareasCompletadas = sum(1 for t in tareas if t.get("estado") == "Completada")
            avance = (tareasCompletadas / totalTareas) * 100 if totalTareas > 0 else 0
            
            contenido += f"--- Proyecto {i} ---\n"
            contenido += f"  Nombre: {proyecto.get('proyecto', 'N/A')}\n"
            contenido += f"  Costo: {proyecto.get('costo', 'N/A')}\n"
            contenido += f"  Categoría: {proyecto.get('categoria', 'N/A')}\n"
            contenido += f"  Descripción: {proyecto.get('descripcion', 'N/A')}\n"
            contenido += f"  Materiales: {proyecto.get('materiales', 'N/A')}\n"
            contenido += f"  Fecha de Inicio: {proyecto.get('fehceInicio', 'N/A')}\n"
            contenido += f"  Fecha de Fin: {proyecto.get('fechaFin', 'N/A')}\n"
            responsable = proyecto.get("responsableProyecto", {})
            contenido += f"  Responsable: {responsable.get('nombre', 'N/A')} (Cédula: {responsable.get('cedula', 'N/A')})\n"
            contenido += f"  Avance: {avance:.2f}% ({tareasCompletadas}/{totalTareas} tareas completadas)\n\n"
            
            contenido += "  Tareas:\n"
            if not tareas:
                contenido += "   - No hay tareas registradas.\n"
            else:
                for tarea in tareas:
                    responsableTarea = tarea.get("responsable", {})
                    contenido += f"   - Nombre: {tarea.get('nombre', 'N/A')}\n"
                    contenido += f"     Descripción: {tarea.get('descripcion', 'N/A')}\n"
                    contenido += f"     Inicio: {tarea.get('fecha_inicio', 'N/A')} | Fin: {tarea.get('fecha_fin', 'N/A')}\n"
                    contenido += f"     Estado: {tarea.get('estado', 'N/A')}\n"
                    contenido += f"     Responsable: {responsableTarea.get('nombre', 'N/A')}\n\n"
            contenido += "\n" + "="*50 + "\n\n"
        
        self.textoReportes.insert('1.0', contenido)
        self.textoReportes.configure(state='disabled')
    
    def verTodosProyectos(self):
        proyectos = self.cargarProyectos()
        self.mostrarProyectosEnReporte(proyectos, "Todos los Proyectos")
    
    def buscarProyectoReporte(self):
        nombreBuscar = simpledialog.askstring("Buscar Proyecto", "Ingrese el nombre del proyecto a buscar:")
        if not nombreBuscar:
            return
        
        proyectos = self.cargarProyectos()
        proyectosFiltrados = [proyecto for proyecto in proyectos if proyecto.get('proyecto', '').lower() == nombreBuscar.strip().lower()]
        
        if proyectosFiltrados:
            self.mostrarProyectosEnReporte(proyectosFiltrados, f"Proyecto: {nombreBuscar}")
        else:
            messagebox.showinfo("Sin resultados", f"No se encontró el proyecto '{nombreBuscar}'")
    
    def generarResumen(self):
        proyectos = self.cargarProyectos()
        if not proyectos:
            messagebox.showinfo("Sin datos", "No hay proyectos registrados.")
            return
        
        self.textoReportes.configure(state='normal')
        self.textoReportes.delete('1.0', tk.END)
        
        contenido = "===== Resumen de Proyectos =====\n\n"
        for i, proyecto in enumerate(proyectos, 1):
            tareas = proyecto.get("tareas", [])
            totalTareas = len(tareas)
            tareasCompletadas = sum(1 for t in tareas if t.get("estado") == "Completada")
            tareasNoCompletadas = totalTareas - tareasCompletadas
            avance = (tareasCompletadas / totalTareas) * 100 if totalTareas > 0 else 0
            
            contenido += f"--- Proyecto {i}: {proyecto.get('proyecto', 'N/A')} ---\n"
            contenido += f"  Total de tareas: {totalTareas}\n"
            contenido += f"  Tareas completadas: {tareasCompletadas}\n"
            contenido += f"  Tareas no completadas: {tareasNoCompletadas}\n"
            contenido += f"  Porcentaje de avance: {avance:.2f}%\n\n"
            
            contenido += "  Estado de las tareas:\n"
            if not tareas:
                contenido += "   - No hay tareas asignadas.\n"
            else:
                for tarea in tareas:
                    contenido += f"   - {tarea.get('nombre', 'N/A')}: {tarea.get('estado', 'N/A')}\n"
            contenido += "\n" + "="*40 + "\n\n"
        
        self.textoReportes.insert('1.0', contenido)
        self.textoReportes.configure(state='disabled')
    
    def ordenarProyectos(self):
        # Ventana para seleccionar criterio de ordenamiento
        ventanaOrden = tk.Toplevel(self.ventanaPrincipal)
        ventanaOrden.title("Ordenar Proyectos")
        ventanaOrden.geometry("300x200")
        ventanaOrden.configure(bg='#f0f0f0')
        ventanaOrden.transient(self.ventanaPrincipal)
        ventanaOrden.grab_set()
        
        tk.Label(ventanaOrden, text="Ordenar proyectos por:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=20)
        
        variableOrden = tk.StringVar()
        opciones = [
            ("Nombre (Alfabético)", "nombre"),
            ("Fecha de inicio", "fecha"),
            ("Responsable", "responsable")
        ]
        
        for texto, valor in opciones:
            tk.Radiobutton(ventanaOrden, text=texto, variable=variableOrden, value=valor, 
                          font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=50)
        
        def aplicarOrden():
            criterio = variableOrden.get()
            if not criterio:
                messagebox.showwarning("Advertencia", "Por favor seleccione un criterio")
                return
            
            proyectos = self.cargarProyectos()
            if not proyectos:
                messagebox.showinfo("Sin datos", "No hay proyectos para ordenar")
                return
            
            proyectosOrdenados = proyectos[:]
            
            if criterio == "nombre":
                proyectosOrdenados.sort(key=lambda p: p.get('proyecto', '').lower())
                titulo = "Proyectos Ordenados por Nombre"
            elif criterio == "fecha":
                def parsearFecha(fechaCadena):
                    try:
                        return datetime.strptime(fechaCadena, '%d/%m/%Y')
                    except:
                        return datetime(1900, 1, 1)
                proyectosOrdenados.sort(key=lambda p: parsearFecha(p.get('fehceInicio', '01/01/1900')))
                titulo = "Proyectos Ordenados por Fecha de Inicio"
            elif criterio == "responsable":
                proyectosOrdenados.sort(key=lambda p: p.get('responsableProyecto', {}).get('nombre', '').lower())
                titulo = "Proyectos Ordenados por Responsable"
            
            ventanaOrden.destroy()
            self.mostrarProyectosEnReporte(proyectosOrdenados, titulo)
        
        tk.Button(ventanaOrden, text="Ordenar", command=aplicarOrden,
                 bg='#1abc9c', fg='white', font=('Arial', 10, 'bold')).pack(pady=20)
    
    def cerrarSesion(self):
        if os.path.exists(archivoSesion):
            os.remove(archivoSesion)
        self.ventanaPrincipal.destroy()
        # Volver al login
        from inicio import VentanaLogin
        login = VentanaLogin()
        login.ejecutar()
    
    def ejecutar(self):
        # Cargar datos iniciales
        self.cargarUsuarios()
        self.ventanaPrincipal.mainloop()