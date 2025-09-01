import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

# Archivos de datos (usando las mismas rutas que en inicio.py)
archivoProyectos = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\proyectos.json"
archivoRegistro = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\registro.txt"
archivoSesion = "C:\\Users\\Personal\\Desktop\\codigoInterfaz\\sesion_actual.json"

class AplicacionEstudiante:
    def __init__(self, usuarioActual):
        self.usuarioActual = usuarioActual
        self.ventanaPrincipal = tk.Tk()
        self.ventanaPrincipal.title(f"Gestor de Proyectos - {usuarioActual['nombre']}")
        self.ventanaPrincipal.geometry("900x700")
        self.ventanaPrincipal.configure(bg='#f0f0f0')
        
        self.crearInterfaz()
        
    def crearInterfaz(self):
        # Header
        marcoEncabezado = tk.Frame(self.ventanaPrincipal, bg='#2c3e50', height=60)
        marcoEncabezado.pack(fill='x')
        marcoEncabezado.pack_propagate(False)
        
        tk.Label(marcoEncabezado, text=f"Gestor de Proyectos - {self.usuarioActual['nombre']}", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=15)
        
        botonCerrarSesion = tk.Button(marcoEncabezado, text="Cerrar Sesión", 
                              command=self.cerrarSesion,
                              bg='#e74c3c', fg='white', 
                              font=('Arial', 10, 'bold'))
        botonCerrarSesion.pack(side='right', padx=20, pady=15)
        
        # Notebook para pestañas
        self.cuadernoPestanas = ttk.Notebook(self.ventanaPrincipal)
        self.cuadernoPestanas.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Pestaña de Proyectos
        self.crearPestanaProyectos()
        
        # Pestaña de Tareas
        self.crearPestanaTareas()
        
        # Pestaña de Mis Proyectos
        self.crearPestanaMisProyectos()
    
    def crearPestanaProyectos(self):
        marcoProyectos = ttk.Frame(self.cuadernoPestanas)
        self.cuadernoPestanas.add(marcoProyectos, text="Gestión de Proyectos")
        
        # Botones principales
        marcoBotones = tk.Frame(marcoProyectos, bg='#f0f0f0')
        marcoBotones.pack(fill='x', padx=10, pady=10)
        
        tk.Button(marcoBotones, text="Crear Proyecto", command=self.crearProyecto,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Actualizar Proyecto", command=self.actualizarProyecto,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Eliminar Proyecto", command=self.eliminarProyecto,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Listar Proyectos", command=self.listarProyectos,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Lista de proyectos
        marcoLista = tk.Frame(marcoProyectos, bg='#f0f0f0')
        marcoLista.pack(expand=True, fill='both', padx=10, pady=10)
        
        tk.Label(marcoLista, text="Lista de Proyectos:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        # Treeview para mostrar proyectos
        columnas = ('Proyecto', 'Categoría', 'Costo', 'Avance', 'Responsable')
        self.arbolProyectos = ttk.Treeview(marcoLista, columns=columnas, show='headings', height=15)
        
        for columna in columnas:
            self.arbolProyectos.heading(columna, text=columna)
            self.arbolProyectos.column(columna, width=150)
        
        barraDesplazamientoProyectos = ttk.Scrollbar(marcoLista, orient='vertical', command=self.arbolProyectos.yview)
        self.arbolProyectos.configure(yscrollcommand=barraDesplazamientoProyectos.set)
        
        self.arbolProyectos.pack(side='left', expand=True, fill='both')
        barraDesplazamientoProyectos.pack(side='right', fill='y')
        
        # Doble clic para ver detalles
        self.arbolProyectos.bind('<Double-1>', self.verDetalleProyecto)
    
    def crearPestanaTareas(self):
        marcoTareas = ttk.Frame(self.cuadernoPestanas)
        self.cuadernoPestanas.add(marcoTareas, text="Gestión de Tareas")
        
        # Botones de tareas
        marcoBotones = tk.Frame(marcoTareas, bg='#f0f0f0')
        marcoBotones.pack(fill='x', padx=10, pady=10)
        
        tk.Button(marcoBotones, text="Agregar Tarea", command=self.agregarTarea,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Editar Tarea", command=self.editarTarea,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Eliminar Tarea", command=self.eliminarTarea,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(marcoBotones, text="Marcar Estado", command=self.marcarTarea,
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=5)
        
        # Lista de tareas
        marcoLista = tk.Frame(marcoTareas, bg='#f0f0f0')
        marcoLista.pack(expand=True, fill='both', padx=10, pady=10)
        
        tk.Label(marcoLista, text="Mis Tareas:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        # Treeview para mostrar tareas
        columnas = ('Proyecto', 'Tarea', 'Descripción', 'Inicio', 'Fin', 'Estado')
        self.arbolTareas = ttk.Treeview(marcoLista, columns=columnas, show='headings', height=15)
        
        for columna in columnas:
            self.arbolTareas.heading(columna, text=columna)
            self.arbolTareas.column(columna, width=120)
        
        barraDesplazamientoTareas = ttk.Scrollbar(marcoLista, orient='vertical', command=self.arbolTareas.yview)
        self.arbolTareas.configure(yscrollcommand=barraDesplazamientoTareas.set)
        
        self.arbolTareas.pack(side='left', expand=True, fill='both')
        barraDesplazamientoTareas.pack(side='right', fill='y')
    
    def crearPestanaMisProyectos(self):
        marcoMisProyectos = ttk.Frame(self.cuadernoPestanas)
        self.cuadernoPestanas.add(marcoMisProyectos, text="Mis Proyectos")
        
        # Botón para refrescar
        tk.Button(marcoMisProyectos, text="Actualizar Vista", command=self.actualizarMisProyectos,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(pady=10)
        
        # Frame para contenido
        marcoContenido = tk.Frame(marcoMisProyectos, bg='#f0f0f0')
        marcoContenido.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Text widget con scrollbar
        self.textoMisProyectos = tk.Text(marcoContenido, font=('Arial', 10), wrap='word')
        barraDesplazamientoTexto = ttk.Scrollbar(marcoContenido, orient='vertical', command=self.textoMisProyectos.yview)
        self.textoMisProyectos.configure(yscrollcommand=barraDesplazamientoTexto.set)
        
        self.textoMisProyectos.pack(side='left', expand=True, fill='both')
        barraDesplazamientoTexto.pack(side='right', fill='y')
        
        # Cargar datos iniciales
        self.actualizarMisProyectos()
    
    # Métodos auxiliares
    def cargarDatos(self, archivo):
        if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
            return []
        try:
            with open(archivo, "r", encoding="utf-8") as archivoLectura:
                return json.load(archivoLectura)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def guardarDatos(self, datos, archivo):
        with open(archivo, "w", encoding="utf-8") as archivoEscritura:
            json.dump(datos, archivoEscritura, ensure_ascii=False, indent=2)
    
    def buscarProyectoPorNombre(self, nombreProyecto):
        datos = self.cargarDatos(archivoProyectos)
        for indice, proyecto in enumerate(datos):
            if proyecto.get("proyecto", "").strip().lower() == nombreProyecto.strip().lower():
                return indice, proyecto
        return None, None
    
    def obtenerDatosUsuarioPorCedula(self, cedula):
        try:
            with open(archivoRegistro, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if len(datos) > 5 and datos[2].strip().lower() == cedula.strip().lower():
                        return {
                            "nombre": f"{datos[0].strip()} {datos[1].strip()}",
                            "cedula": datos[2].strip(),
                            "correo": datos[3].strip(),
                            "contrasenaHash": datos[4].strip(),
                            "rol": datos[5].strip()
                        }
        except FileNotFoundError:
            pass
        return None
    
    def validarFecha(self, fechaCadena):
        try:
            datetime.strptime(fechaCadena, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def calcularAvanceProyecto(self, proyecto):
        tareas = proyecto.get("tareas", [])
        if not tareas:
            return 0
        tareasCompletadas = [tarea for tarea in tareas if tarea.get("estado") == "Completada"]
        return (len(tareasCompletadas) / len(tareas)) * 100
    
    # Métodos de gestión de proyectos
    def crearProyecto(self):
        # Ventana para crear proyecto
        ventanaCrear = tk.Toplevel(self.ventanaPrincipal)
        ventanaCrear.title("Crear Nuevo Proyecto")
        ventanaCrear.geometry("500x600")
        ventanaCrear.configure(bg='#f0f0f0')
        ventanaCrear.transient(self.ventanaPrincipal)
        ventanaCrear.grab_set()
        
        # Variables
        campos = {}
        
        # Campos del formulario
        camposFormulario = [
            ("Nombre del proyecto:", "nombre"),
            ("Costo del proyecto:", "costo"),
            ("Categoría del proyecto:", "categoria"),
            ("Descripción del proyecto:", "descripcion"),
            ("Materiales requeridos:", "materiales"),
            ("Fecha de inicio (dd/mm/yyyy):", "fechaInicio"),
            ("Fecha de fin (dd/mm/yyyy):", "fechaFin")
        ]
        
        for textoEtiqueta, nombreCampo in camposFormulario:
            tk.Label(ventanaCrear, text=textoEtiqueta, font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
            if nombreCampo in ["descripcion", "materiales"]:
                campos[nombreCampo] = tk.Text(ventanaCrear, font=('Arial', 10), height=3, width=50)
            else:
                campos[nombreCampo] = tk.Entry(ventanaCrear, font=('Arial', 10), width=50)
            campos[nombreCampo].pack(padx=20, pady=(0, 5))
        
        def guardarProyecto():
            # Validar campos
            valores = {}
            for nombreCampo, widget in campos.items():
                if isinstance(widget, tk.Text):
                    valores[nombreCampo] = widget.get("1.0", tk.END).strip()
                else:
                    valores[nombreCampo] = widget.get().strip()
                
                if not valores[nombreCampo]:
                    messagebox.showerror("Error", f"El campo {nombreCampo} es obligatorio")
                    return
            
            # Validar fechas
            if not self.validarFecha(valores["fechaInicio"]):
                messagebox.showerror("Error", "Fecha de inicio inválida. Use el formato dd/mm/yyyy")
                return
            
            if not self.validarFecha(valores["fechaFin"]):
                messagebox.showerror("Error", "Fecha de fin inválida. Use el formato dd/mm/yyyy")
                return
            
            # Validar que fecha de fin sea posterior a fecha de inicio
            try:
                fechaInicio = datetime.strptime(valores["fechaInicio"], "%d/%m/%Y")
                fechaFin = datetime.strptime(valores["fechaFin"], "%d/%m/%Y")
                if fechaFin < fechaInicio:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Error en las fechas")
                return
            
            # Crear proyecto
            nuevoProyecto = {
                "proyecto": valores["nombre"],
                "costo": valores["costo"],
                "categoria": valores["categoria"],
                "descripcion": valores["descripcion"],
                "materiales": valores["materiales"],
                "fehceInicio": valores["fechaInicio"],  # Mantengo el typo original
                "fechaFin": valores["fechaFin"],
                "responsableProyecto": {
                    "cedula": self.usuarioActual['cedula'],
                    "nombre": self.usuarioActual['nombre']
                },
                "tareas": []
            }
            
            datos = self.cargarDatos(archivoProyectos)
            datos.append(nuevoProyecto)
            self.guardarDatos(datos, archivoProyectos)
            
            messagebox.showinfo("Éxito", "Proyecto creado exitosamente")
            ventanaCrear.destroy()
            self.listarProyectos()
        
        tk.Button(ventanaCrear, text="Guardar Proyecto", command=guardarProyecto,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def actualizarProyecto(self):
        # Seleccionar proyecto de la lista
        if not self.arbolProyectos.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un proyecto de la lista")
            return
        
        elementoSeleccionado = self.arbolProyectos.selection()[0]
        nombreProyecto = self.arbolProyectos.item(elementoSeleccionado)['values'][0]
        
        indice, proyecto = self.buscarProyectoPorNombre(nombreProyecto)
        if proyecto is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        # Verificar permisos
        if proyecto.get('responsableProyecto', {}).get('cedula') != self.usuarioActual['cedula']:
            messagebox.showerror("Error", "No tiene permisos para actualizar este proyecto")
            return
        
        # Ventana para actualizar proyecto
        ventanaActualizar = tk.Toplevel(self.ventanaPrincipal)
        ventanaActualizar.title("Actualizar Proyecto")
        ventanaActualizar.geometry("500x600")
        ventanaActualizar.configure(bg='#f0f0f0')
        ventanaActualizar.transient(self.ventanaPrincipal)
        ventanaActualizar.grab_set()
        
        # Variables
        campos = {}
        
        # Campos del formulario con valores actuales
        camposFormulario = [
            ("Nombre del proyecto:", "nombre", proyecto.get('proyecto', '')),
            ("Costo del proyecto:", "costo", proyecto.get('costo', '')),
            ("Categoría del proyecto:", "categoria", proyecto.get('categoria', '')),
            ("Descripción del proyecto:", "descripcion", proyecto.get('descripcion', '')),
            ("Materiales requeridos:", "materiales", proyecto.get('materiales', '')),
            ("Fecha de inicio (dd/mm/yyyy):", "fechaInicio", proyecto.get('fehceInicio', '')),
            ("Fecha de fin (dd/mm/yyyy):", "fechaFin", proyecto.get('fechaFin', ''))
        ]
        
        for textoEtiqueta, nombreCampo, valorActual in camposFormulario:
            tk.Label(ventanaActualizar, text=textoEtiqueta, font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 0))
            if nombreCampo in ["descripcion", "materiales"]:
                campos[nombreCampo] = tk.Text(ventanaActualizar, font=('Arial', 10), height=3, width=50)
                campos[nombreCampo].insert("1.0", valorActual)
            else:
                campos[nombreCampo] = tk.Entry(ventanaActualizar, font=('Arial', 10), width=50)
                campos[nombreCampo].insert(0, valorActual)
            campos[nombreCampo].pack(padx=20, pady=(0, 5))
        
        def actualizar():
            # Obtener valores
            valores = {}
            for nombreCampo, widget in campos.items():
                if isinstance(widget, tk.Text):
                    valores[nombreCampo] = widget.get("1.0", tk.END).strip()
                else:
                    valores[nombreCampo] = widget.get().strip()
                
                if not valores[nombreCampo]:
                    messagebox.showerror("Error", f"El campo {nombreCampo} es obligatorio")
                    return
            
            # Validar fechas
            if not self.validarFecha(valores["fechaInicio"]):
                messagebox.showerror("Error", "Fecha de inicio inválida. Use el formato dd/mm/yyyy")
                return
            
            if not self.validarFecha(valores["fechaFin"]):
                messagebox.showerror("Error", "Fecha de fin inválida. Use el formato dd/mm/yyyy")
                return
            
            try:
                fechaInicio = datetime.strptime(valores["fechaInicio"], "%d/%m/%Y")
                fechaFin = datetime.strptime(valores["fechaFin"], "%d/%m/%Y")
                if fechaFin < fechaInicio:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Error en las fechas")
                return
            
            # Actualizar proyecto
            proyecto['proyecto'] = valores["nombre"]
            proyecto['costo'] = valores["costo"]
            proyecto['categoria'] = valores["categoria"]
            proyecto['descripcion'] = valores["descripcion"]
            proyecto['materiales'] = valores["materiales"]
            proyecto['fehceInicio'] = valores["fechaInicio"]
            proyecto['fechaFin'] = valores["fechaFin"]
            
            datos = self.cargarDatos(archivoProyectos)
            datos[indice] = proyecto
            self.guardarDatos(datos, archivoProyectos)
            
            messagebox.showinfo("Éxito", "Proyecto actualizado exitosamente")
            ventanaActualizar.destroy()
            self.listarProyectos()
        
        tk.Button(ventanaActualizar, text="Actualizar Proyecto", command=actualizar,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def eliminarProyecto(self):
        if not self.arbolProyectos.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un proyecto de la lista")
            return
        
        elementoSeleccionado = self.arbolProyectos.selection()[0]
        nombreProyecto = self.arbolProyectos.item(elementoSeleccionado)['values'][0]
        
        indice, proyecto = self.buscarProyectoPorNombre(nombreProyecto)
        if proyecto is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        # Verificar permisos
        if proyecto.get('responsableProyecto', {}).get('cedula') != self.usuarioActual['cedula']:
            messagebox.showerror("Error", "No tiene permisos para eliminar este proyecto")
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar el proyecto '{proyecto['proyecto']}' y todas sus tareas?"):
            datos = self.cargarDatos(archivoProyectos)
            datos.pop(indice)
            self.guardarDatos(datos, archivoProyectos)
            messagebox.showinfo("Éxito", "Proyecto eliminado exitosamente")
            self.listarProyectos()
    
    def listarProyectos(self):
        # Limpiar el treeview
        for elemento in self.arbolProyectos.get_children():
            self.arbolProyectos.delete(elemento)
        
        # Cargar proyectos
        datos = self.cargarDatos(archivoProyectos)
        for proyecto in datos:
            avance = self.calcularAvanceProyecto(proyecto)
            responsable = proyecto.get('responsableProyecto', {}).get('nombre', 'N/A')
            
            self.arbolProyectos.insert('', 'end', values=(
                proyecto.get('proyecto', 'N/A'),
                proyecto.get('categoria', 'N/A'),
                proyecto.get('costo', 'N/A'),
                f"{avance:.1f}%",
                responsable
            ))
    
    def verDetalleProyecto(self, evento):
        if not self.arbolProyectos.selection():
            return
        
        elementoSeleccionado = self.arbolProyectos.selection()[0]
        nombreProyecto = self.arbolProyectos.item(elementoSeleccionado)['values'][0]
        
        indice, proyecto = self.buscarProyectoPorNombre(nombreProyecto)
        if proyecto is None:
            return
        
        # Ventana de detalles
        ventanaDetalle = tk.Toplevel(self.ventanaPrincipal)
        ventanaDetalle.title(f"Detalles del Proyecto: {proyecto.get('proyecto', 'N/A')}")
        ventanaDetalle.geometry("600x500")
        ventanaDetalle.configure(bg='#f0f0f0')
        ventanaDetalle.transient(self.ventanaPrincipal)
        
        # Text widget con scrollbar
        marcoTexto = tk.Frame(ventanaDetalle)
        marcoTexto.pack(expand=True, fill='both', padx=10, pady=10)
        
        widgetTexto = tk.Text(marcoTexto, font=('Arial', 10), wrap='word')
        barraDesplazamiento = ttk.Scrollbar(marcoTexto, orient='vertical', command=widgetTexto.yview)
        widgetTexto.configure(yscrollcommand=barraDesplazamiento.set)
        
        # Contenido del detalle
        avance = self.calcularAvanceProyecto(proyecto)
        responsable = proyecto.get("responsableProyecto", {})
        
        detalle = f"""===== Detalle del Proyecto =====

Proyecto: {proyecto.get('proyecto', 'N/A')} (Avance: {avance:.2f}%)
Costo: {proyecto.get('costo', 'N/A')}
Categoría: {proyecto.get('categoria', 'N/A')}
Fecha de inicio: {proyecto.get('fehceInicio', 'N/A')}
Fecha de fin: {proyecto.get('fechaFin', 'N/A')}
Responsable: {responsable.get('nombre', 'N/A')} (Cédula: {responsable.get('cedula', 'N/A')})

Descripción:
{proyecto.get('descripcion', 'N/A')}

Materiales:
{proyecto.get('materiales', 'N/A')}

Tareas:
"""
        
        tareas = proyecto.get("tareas", [])
        if not tareas:
            detalle += "   - No hay tareas registradas.\n"
        else:
            for i, tarea in enumerate(tareas, 1):
                responsableTarea = tarea.get("responsable", {})
                detalle += f"""   {i}. {tarea.get('nombre', 'N/A')} - {tarea.get('descripcion', 'N/A')}
      Inicio: {tarea.get('fecha_inicio', 'N/A')} | Fin: {tarea.get('fecha_fin', 'N/A')} | Estado: {tarea.get('estado', 'N/A')}
      Responsable: {responsableTarea.get('nombre', 'N/A')} ({responsableTarea.get('cedula', 'N/A')})

"""
        
        widgetTexto.insert('1.0', detalle)
        widgetTexto.configure(state='disabled')
        
        widgetTexto.pack(side='left', expand=True, fill='both')
        barraDesplazamiento.pack(side='right', fill='y')
    
    # Métodos de gestión de tareas
    def agregarTarea(self):
        datos = self.cargarDatos(archivoProyectos)
        if not datos:
            messagebox.showwarning("Advertencia", "No hay proyectos. No se puede agregar una tarea.")
            return
        
        # Ventana para agregar tarea
        ventanaAgregarTarea = tk.Toplevel(self.ventanaPrincipal)
        ventanaAgregarTarea.title("Agregar Tarea")
        ventanaAgregarTarea.geometry("500x500")
        ventanaAgregarTarea.configure(bg='#f0f0f0')
        ventanaAgregarTarea.transient(self.ventanaPrincipal)
        ventanaAgregarTarea.grab_set()
        
        # Selección de proyecto
        tk.Label(ventanaAgregarTarea, text="Seleccionar Proyecto:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(20, 5))
        
        variableProyecto = tk.StringVar()
        comboProyecto = ttk.Combobox(ventanaAgregarTarea, textvariable=variableProyecto, font=('Arial', 10), width=47)
        comboProyecto['values'] = [proyecto.get('proyecto', 'N/A') for proyecto in datos]
        comboProyecto.pack(padx=20, pady=(0, 10))
        
        # Campos de la tarea
        tk.Label(ventanaAgregarTarea, text="Nombre de la tarea:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        entradaTarea = tk.Entry(ventanaAgregarTarea, font=('Arial', 10), width=50)
        entradaTarea.pack(padx=20, pady=(0, 10))
        
        tk.Label(ventanaAgregarTarea, text="Descripción de la tarea:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        textoDescripcion = tk.Text(ventanaAgregarTarea, font=('Arial', 10), height=3, width=50)
        textoDescripcion.pack(padx=20, pady=(0, 10))
        
        tk.Label(ventanaAgregarTarea, text="Fecha de inicio (dd/mm/yyyy):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        entradaFechaInicio = tk.Entry(ventanaAgregarTarea, font=('Arial', 10), width=50)
        entradaFechaInicio.pack(padx=20, pady=(0, 10))
        
        tk.Label(ventanaAgregarTarea, text="Fecha de fin (dd/mm/yyyy):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        entradaFechaFin = tk.Entry(ventanaAgregarTarea, font=('Arial', 10), width=50)
        entradaFechaFin.pack(padx=20, pady=(0, 10))
        
        tk.Label(ventanaAgregarTarea, text="Cédula del responsable:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        entradaCedula = tk.Entry(ventanaAgregarTarea, font=('Arial', 10), width=50)
        entradaCedula.pack(padx=20, pady=(0, 10))
        
        def guardarTarea():
            nombreProyecto = variableProyecto.get()
            nombreTarea = entradaTarea.get().strip()
            descripcion = textoDescripcion.get("1.0", tk.END).strip()
            fechaInicio = entradaFechaInicio.get().strip()
            fechaFin = entradaFechaFin.get().strip()
            cedulaResponsable = entradaCedula.get().strip()
            
            if not all([nombreProyecto, nombreTarea, descripcion, fechaInicio, fechaFin, cedulaResponsable]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            # Validar fechas
            if not self.validarFecha(fechaInicio) or not self.validarFecha(fechaFin):
                messagebox.showerror("Error", "Fechas inválidas. Use el formato dd/mm/yyyy")
                return
            
            try:
                fechaInicioDate = datetime.strptime(fechaInicio, "%d/%m/%Y")
                fechaFinDate = datetime.strptime(fechaFin, "%d/%m/%Y")
                if fechaFinDate < fechaInicioDate:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Error en las fechas")
                return
            
            # Validar responsable
            datosResponsable = self.obtenerDatosUsuarioPorCedula(cedulaResponsable)
            if not datosResponsable or datosResponsable['rol'].lower() != "estudiante":
                messagebox.showerror("Error", "Cédula no encontrada o rol no válido (debe ser estudiante)")
                return
            
            # Buscar proyecto
            indice, proyecto = self.buscarProyectoPorNombre(nombreProyecto)
            if proyecto is None:
                messagebox.showerror("Error", "Proyecto no encontrado")
                return
            
            # Crear tarea
            nuevaTarea = {
                "nombre": nombreTarea,
                "descripcion": descripcion,
                "fecha_inicio": fechaInicio,
                "fecha_fin": fechaFin,
                "responsable": {
                    "cedula": cedulaResponsable,
                    "nombre": datosResponsable['nombre']
                },
                "estado": "Asignada"
            }
            
            proyecto.setdefault("tareas", []).append(nuevaTarea)
            datos[indice] = proyecto
            self.guardarDatos(datos, archivoProyectos)
            
            messagebox.showinfo("Éxito", "Tarea agregada exitosamente")
            ventanaAgregarTarea.destroy()
            self.cargarMisTareas()
        
        tk.Button(ventanaAgregarTarea, text="Guardar Tarea", command=guardarTarea,
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def editarTarea(self):
        if not self.arbolTareas.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarea de la lista")
            return
        
        elementoSeleccionado = self.arbolTareas.selection()[0]
        valores = self.arbolTareas.item(elementoSeleccionado)['values']
        nombreProyecto = valores[0]
        nombreTarea = valores[1]
        
        # Buscar proyecto y tarea
        indice, proyecto = self.buscarProyectoPorNombre(nombreProyecto)
        if proyecto is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        tareas = proyecto.get("tareas", [])
        indiceTarea = None
        tarea = None
        
        for i, t in enumerate(tareas):
            if t.get('nombre') == nombreTarea:
                indiceTarea = i
                tarea = t
                break
        
        if tarea is None:
            messagebox.showerror("Error", "Tarea no encontrada")
            return
        
        # Ventana para editar tarea
        ventanaEditar = tk.Toplevel(self.ventanaPrincipal)
        ventanaEditar.title("Editar Tarea")
        ventanaEditar.geometry("500x500")
        ventanaEditar.configure(bg='#f0f0f0')
        ventanaEditar.transient(self.ventanaPrincipal)
        ventanaEditar.grab_set()
        
        # Campos con valores actuales
        tk.Label(ventanaEditar, text="Nombre de la tarea:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(20, 5))
        entradaNombre = tk.Entry(ventanaEditar, font=('Arial', 10), width=50)
        entradaNombre.insert(0, tarea.get('nombre', ''))
        entradaNombre.pack(padx=20, pady=(0, 10))
        
        tk.Label(ventanaEditar, text="Descripción de la tarea:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        textoDescripcion = tk.Text(ventanaEditar, font=('Arial', 10), height=3, width=50)
        textoDescripcion.insert("1.0", tarea.get('descripcion', ''))
        textoDescripcion.pack(padx=20, pady=(0, 10))
        
        tk.Label(ventanaEditar, text="Fecha de inicio (dd/mm/yyyy):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        entradaFechaInicio = tk.Entry(ventanaEditar, font=('Arial', 10), width=50)
        entradaFechaInicio.insert(0, tarea.get('fecha_inicio', ''))
        entradaFechaInicio.pack(padx=20, pady=(0, 10))
        
        tk.Label(ventanaEditar, text="Fecha de fin (dd/mm/yyyy):", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        entradaFechaFin = tk.Entry(ventanaEditar, font=('Arial', 10), width=50)
        entradaFechaFin.insert(0, tarea.get('fecha_fin', ''))
        entradaFechaFin.pack(padx=20, pady=(0, 10))
        
        tk.Label(ventanaEditar, text="Cédula del responsable:", font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=20, pady=(10, 5))
        entradaCedula = tk.Entry(ventanaEditar, font=('Arial', 10), width=50)
        entradaCedula.insert(0, tarea.get('responsable', {}).get('cedula', ''))
        entradaCedula.pack(padx=20, pady=(0, 10))
        
        def actualizarTarea():
            nuevoNombre = entradaNombre.get().strip()
            nuevaDescripcion = textoDescripcion.get("1.0", tk.END).strip()
            nuevaFechaInicio = entradaFechaInicio.get().strip()
            nuevaFechaFin = entradaFechaFin.get().strip()
            nuevaCedula = entradaCedula.get().strip()
            
            if not all([nuevoNombre, nuevaDescripcion, nuevaFechaInicio, nuevaFechaFin, nuevaCedula]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            # Validar fechas
            if not self.validarFecha(nuevaFechaInicio) or not self.validarFecha(nuevaFechaFin):
                messagebox.showerror("Error", "Fechas inválidas. Use el formato dd/mm/yyyy")
                return
            
            try:
                fechaInicioDate = datetime.strptime(nuevaFechaInicio, "%d/%m/%Y")
                fechaFinDate = datetime.strptime(nuevaFechaFin, "%d/%m/%Y")
                if fechaFinDate < fechaInicioDate:
                    messagebox.showerror("Error", "La fecha de fin no puede ser anterior a la fecha de inicio")
                    return
            except ValueError:
                messagebox.showerror("Error", "Error en las fechas")
                return
            
            # Validar responsable
            datosResponsable = self.obtenerDatosUsuarioPorCedula(nuevaCedula)
            if not datosResponsable or datosResponsable['rol'].lower() != "estudiante":
                messagebox.showerror("Error", "Cédula no encontrada o rol no válido (debe ser estudiante)")
                return
            
            # Actualizar tarea
            tarea['nombre'] = nuevoNombre
            tarea['descripcion'] = nuevaDescripcion
            tarea['fecha_inicio'] = nuevaFechaInicio
            tarea['fecha_fin'] = nuevaFechaFin
            tarea['responsable'] = {
                "cedula": nuevaCedula,
                "nombre": datosResponsable['nombre']
            }
            
            tareas[indiceTarea] = tarea
            proyecto['tareas'] = tareas
            datos = self.cargarDatos(archivoProyectos)
            datos[indice] = proyecto
            self.guardarDatos(datos, archivoProyectos)
            
            messagebox.showinfo("Éxito", "Tarea actualizada exitosamente")
            ventanaEditar.destroy()
            self.cargarMisTareas()
        
        tk.Button(ventanaEditar, text="Actualizar Tarea", command=actualizarTarea,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=10).pack(pady=20)
    
    def eliminarTarea(self):
        if not self.arbolTareas.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarea de la lista")
            return
        
        elementoSeleccionado = self.arbolTareas.selection()[0]
        valores = self.arbolTareas.item(elementoSeleccionado)['values']
        nombreProyecto = valores[0]
        nombreTarea = valores[1]
        
        # Buscar proyecto y tarea
        indice, proyecto = self.buscarProyectoPorNombre(nombreProyecto)
        if proyecto is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        tareas = proyecto.get("tareas", [])
        indiceTarea = None
        
        for i, t in enumerate(tareas):
            if t.get('nombre') == nombreTarea:
                indiceTarea = i
                break
        
        if indiceTarea is None:
            messagebox.showerror("Error", "Tarea no encontrada")
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar la tarea '{nombreTarea}'?"):
            tareas.pop(indiceTarea)
            proyecto['tareas'] = tareas
            datos = self.cargarDatos(archivoProyectos)
            datos[indice] = proyecto
            self.guardarDatos(datos, archivoProyectos)
            
            messagebox.showinfo("Éxito", "Tarea eliminada exitosamente")
            self.cargarMisTareas()
    
    def marcarTarea(self):
        if not self.arbolTareas.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarea de la lista")
            return
        
        elementoSeleccionado = self.arbolTareas.selection()[0]
        valores = self.arbolTareas.item(elementoSeleccionado)['values']
        nombreProyecto = valores[0]
        nombreTarea = valores[1]
        
        # Buscar proyecto y tarea
        indice, proyecto = self.buscarProyectoPorNombre(nombreProyecto)
        if proyecto is None:
            messagebox.showerror("Error", "Proyecto no encontrado")
            return
        
        tareas = proyecto.get("tareas", [])
        indiceTarea = None
        tarea = None
        
        for i, t in enumerate(tareas):
            if t.get('nombre') == nombreTarea and t.get('responsable', {}).get('cedula') == self.usuarioActual['cedula']:
                indiceTarea = i
                tarea = t
                break
        
        if tarea is None:
            messagebox.showerror("Error", "No puede modificar esta tarea (no es el responsable)")
            return
        
        # Ventana para cambiar estado
        ventanaEstado = tk.Toplevel(self.ventanaPrincipal)
        ventanaEstado.title("Cambiar Estado de Tarea")
        ventanaEstado.geometry("300x200")
        ventanaEstado.configure(bg='#f0f0f0')
        ventanaEstado.transient(self.ventanaPrincipal)
        ventanaEstado.grab_set()
        
        tk.Label(ventanaEstado, text=f"Tarea: {nombreTarea}", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=20)
        tk.Label(ventanaEstado, text=f"Estado actual: {tarea.get('estado', 'N/A')}", font=('Arial', 10), bg='#f0f0f0').pack(pady=10)
        
        variableEstado = tk.StringVar()
        estados = ["Asignada", "En ejecución", "Completada"]
        
        for estado in estados:
            radioButton = tk.Radiobutton(ventanaEstado, text=estado, variable=variableEstado, value=estado, 
                               font=('Arial', 10), bg='#f0f0f0')
            radioButton.pack(anchor='w', padx=50)
            if estado == tarea.get('estado'):
                radioButton.select()
        
        def cambiarEstado():
            nuevoEstado = variableEstado.get()
            if not nuevoEstado:
                messagebox.showwarning("Advertencia", "Por favor seleccione un estado")
                return
            
            tarea['estado'] = nuevoEstado
            tareas[indiceTarea] = tarea
            proyecto['tareas'] = tareas
            datos = self.cargarDatos(archivoProyectos)
            datos[indice] = proyecto
            self.guardarDatos(datos, archivoProyectos)
            
            messagebox.showinfo("Éxito", f"Estado actualizado a '{nuevoEstado}'")
            ventanaEstado.destroy()
            self.cargarMisTareas()
        
        tk.Button(ventanaEstado, text="Cambiar Estado", command=cambiarEstado,
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold')).pack(pady=20)
    
    def cargarMisTareas(self):
        # Limpiar el treeview
        for elemento in self.arbolTareas.get_children():
            self.arbolTareas.delete(elemento)
        
        # Cargar tareas del usuario actual
        cedula = self.usuarioActual['cedula']
        datos = self.cargarDatos(archivoProyectos)
        
        for proyecto in datos:
            for tarea in proyecto.get("tareas", []):
                if tarea.get('responsable', {}).get('cedula') == cedula:
                    self.arbolTareas.insert('', 'end', values=(
                        proyecto.get('proyecto', 'N/A'),
                        tarea.get('nombre', 'N/A'),
                        tarea.get('descripcion', 'N/A')[:50] + '...' if len(tarea.get('descripcion', '')) > 50 else tarea.get('descripcion', 'N/A'),
                        tarea.get('fecha_inicio', 'N/A'),
                        tarea.get('fecha_fin', 'N/A'),
                        tarea.get('estado', 'N/A')
                    ))
    
    def actualizarMisProyectos(self):
        self.textoMisProyectos.configure(state='normal')
        self.textoMisProyectos.delete('1.0', tk.END)
        
        cedula = self.usuarioActual['cedula']
        datos = self.cargarDatos(archivoProyectos)
        misProyectos = []
        misTareas = []
        
        for proyecto in datos:
            responsableProyecto = proyecto.get("responsableProyecto", {})
            if responsableProyecto.get("cedula", "").strip() == cedula:
                misProyectos.append(proyecto)
            for tarea in proyecto.get("tareas", []):
                responsableTarea = tarea.get("responsable", {})
                if responsableTarea.get("cedula", "").strip() == cedula:
                    misTareas.append((proyecto.get("proyecto", ""), tarea))
        
        contenido = "===== Proyectos creados por mí =====\n\n"
        if not misProyectos:
            contenido += "No tiene proyectos como responsable.\n\n"
        else:
            for i, proyecto in enumerate(misProyectos, 1):
                avance = self.calcularAvanceProyecto(proyecto)
                contenido += f"{i}. {proyecto.get('proyecto', 'N/A')} | Avance: {avance:.2f}% | Costo: {proyecto.get('costo', 'N/A')} | Inicio: {proyecto.get('fehceInicio', 'N/A')} | Fin: {proyecto.get('fechaFin', 'N/A')}\n"
        
        contenido += "\n===== Tareas asignadas a mí =====\n\n"
        if not misTareas:
            contenido += "No tiene tareas asignadas.\n"
        else:
            for i, (nombreProyecto, tarea) in enumerate(misTareas, 1):
                contenido += f"{i}. [{nombreProyecto}] {tarea.get('nombre', 'N/A')} - {tarea.get('descripcion', 'N/A')}\n"
                contenido += f"   Inicio: {tarea.get('fecha_inicio', 'N/A')} | Fin: {tarea.get('fecha_fin', 'N/A')} | Estado: {tarea.get('estado', 'N/A')}\n\n"
        
        self.textoMisProyectos.insert('1.0', contenido)
        self.textoMisProyectos.configure(state='disabled')
    
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
        self.listarProyectos()
        self.cargarMisTareas()
        self.ventanaPrincipal.mainloop()