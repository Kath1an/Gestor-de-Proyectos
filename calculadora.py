import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
import math

class BinanceLeverageCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Binance Leverage Calculator")
        self.root.geometry("800x700")
        self.root.configure(bg="#0b0e11")
        self.root.resizable(True, True)
        
        # Configurar fuentes personalizadas
        self.setup_fonts()
        
        # Configurar estilo
        self.setup_style()
        
        # Crear widgets
        self.create_widgets()
        
        # Centrar la ventana
        self.center_window()
        
    def setup_fonts(self):
        self.title_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.heading_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=11)
        self.entry_font = font.Font(family="Segoe UI", size=11)
        self.result_font = font.Font(family="Consolas", size=10)
        
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores principales de Binance
        self.bg_primary = "#0b0e11"
        self.bg_secondary = "#1e2329"
        self.bg_tertiary = "#2b3139"
        self.accent_color = "#f0b90b"
        self.text_primary = "#ffffff"
        self.text_secondary = "#c99400"
        self.success_color = "#02c076"
        self.danger_color = "#f84960"
        
        # Configurar estilos personalizados
        style.configure('Custom.TFrame', background=self.bg_primary)
        style.configure('Card.TFrame', background=self.bg_secondary, relief='flat')
        style.configure('Primary.TLabel', background=self.bg_primary, foreground=self.text_primary, font=self.label_font)
        style.configure('Title.TLabel', background=self.bg_primary, foreground=self.accent_color, font=self.title_font)
        style.configure('Heading.TLabel', background=self.bg_secondary, foreground=self.text_secondary, font=self.heading_font)
        
        # Estilo para entries personalizados
        style.configure('Custom.TEntry', 
                       fieldbackground=self.bg_tertiary, 
                       foreground=self.text_primary,
                       borderwidth=1,
                       relief='solid',
                       insertcolor=self.text_primary)
        style.map('Custom.TEntry', 
                 focuscolor=[('!focus', self.accent_color)],
                 bordercolor=[('focus', self.accent_color)])
        
        # Estilo para botones
        style.configure('Accent.TButton',
                       background=self.accent_color,
                       foreground='#000000',
                       font=self.heading_font,
                       relief='flat',
                       borderwidth=0)
        style.map('Accent.TButton', 
                 background=[('active', '#ffd700'), ('pressed', '#c99400')])
        
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        # Container principal con scrolling
        main_container = tk.Frame(self.root, bg=self.bg_primary)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header con logo y título
        header_frame = tk.Frame(main_container, bg=self.bg_primary, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(header_frame, 
                              text="⚡ Binance Leverage Calculator", 
                              font=self.title_font,
                              bg=self.bg_primary, 
                              fg=self.accent_color)
        title_label.pack(expand=True)
        
        # Crear contenedor con dos columnas
        content_frame = tk.Frame(main_container, bg=self.bg_primary)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Panel izquierdo - Inputs
        self.create_input_panel(content_frame)
        
        # Panel derecho - Resultados
        self.create_results_panel(content_frame)
        
    def create_input_panel(self, parent):
        # Card para inputs
        input_card = tk.Frame(parent, bg=self.bg_secondary, relief='solid', bd=1)
        input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=10)
        
        # Padding interno
        input_frame = tk.Frame(input_card, bg=self.bg_secondary)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Título de la sección
        section_title = tk.Label(input_frame, 
                                text="📊 Parámetros de Operación", 
                                font=self.heading_font,
                                bg=self.bg_secondary, 
                                fg=self.text_secondary)
        section_title.pack(anchor=tk.W, pady=(0, 20))
        
        # Capital inicial
        self.create_input_field(input_frame, "Capital Inicial ($)", "capital_var")
        
        # Precio de entrada
        self.create_input_field(input_frame, "Precio de Entrada ($)", "precio_entrada_var")
        
        # Precio objetivo
        self.create_input_field(input_frame, "Precio Objetivo ($)", "precio_objetivo_var")
        
        # Apalancamiento con entrada manual
        self.create_leverage_field(input_frame)
        
        # Tipo de posición con botones elegantes
        self.create_position_buttons(input_frame)
        
        # Botón de cálculo
        calc_button = ttk.Button(input_frame, 
                                text="🚀 CALCULAR GANANCIAS", 
                                style='Accent.TButton',
                                command=self.calcular_ganancias)
        calc_button.pack(fill=tk.X, pady=(30, 10))
        
        # Botón de limpiar
        clear_button = tk.Button(input_frame, 
                               text="🗑️ Limpiar", 
                               bg=self.bg_tertiary,
                               fg=self.text_primary,
                               font=self.label_font,
                               relief='flat',
                               cursor='hand2',
                               command=self.clear_fields)
        clear_button.pack(fill=tk.X)
        
    def create_input_field(self, parent, label_text, var_name):
        field_frame = tk.Frame(parent, bg=self.bg_secondary)
        field_frame.pack(fill=tk.X, pady=(0, 15))
        
        label = tk.Label(field_frame, 
                        text=label_text, 
                        font=self.label_font,
                        bg=self.bg_secondary, 
                        fg=self.text_primary)
        label.pack(anchor=tk.W, pady=(0, 5))
        
        var = tk.StringVar()
        setattr(self, var_name, var)
        
        entry = ttk.Entry(field_frame, 
                         textvariable=var, 
                         style='Custom.TEntry',
                         font=self.entry_font)
        entry.pack(fill=tk.X, ipady=8)
        
        # Agregar placeholder effect
        self.add_placeholder_effect(entry, var, self.get_placeholder_text(label_text))
        
    def create_leverage_field(self, parent):
        leverage_frame = tk.Frame(parent, bg=self.bg_secondary)
        leverage_frame.pack(fill=tk.X, pady=(0, 15))
        
        label = tk.Label(leverage_frame, 
                        text="Apalancamiento", 
                        font=self.label_font,
                        bg=self.bg_secondary, 
                        fg=self.text_primary)
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para entry y botones rápidos
        controls_frame = tk.Frame(leverage_frame, bg=self.bg_secondary)
        controls_frame.pack(fill=tk.X)
        
        # Entry para apalancamiento
        self.apalancamiento_var = tk.StringVar(value="10")
        leverage_entry = ttk.Entry(controls_frame, 
                                  textvariable=self.apalancamiento_var, 
                                  style='Custom.TEntry',
                                  font=self.entry_font,
                                  width=8)
        leverage_entry.pack(side=tk.LEFT, ipady=8)
        
        # Label "x"
        x_label = tk.Label(controls_frame, text="x", 
                          font=self.label_font, 
                          bg=self.bg_secondary, 
                          fg=self.text_primary)
        x_label.pack(side=tk.LEFT, padx=(5, 15))
        
        # Botones de apalancamiento rápido
        quick_leverages = [5, 10, 20, 50, 100]
        for lev in quick_leverages:
            btn = tk.Button(controls_frame, 
                           text=f"{lev}x", 
                           bg=self.bg_tertiary,
                           fg=self.text_primary,
                           font=("Segoe UI", 9),
                           relief='flat',
                           cursor='hand2',
                           width=4,
                           command=lambda x=lev: self.set_leverage(x))
            btn.pack(side=tk.LEFT, padx=2)
            
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.accent_color, fg='black'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.bg_tertiary, fg=self.text_primary))
    
    def create_position_buttons(self, parent):
        position_frame = tk.Frame(parent, bg=self.bg_secondary)
        position_frame.pack(fill=tk.X, pady=(0, 20))
        
        label = tk.Label(position_frame, 
                        text="Tipo de Posición", 
                        font=self.label_font,
                        bg=self.bg_secondary, 
                        fg=self.text_primary)
        label.pack(anchor=tk.W, pady=(0, 10))
        
        buttons_frame = tk.Frame(position_frame, bg=self.bg_secondary)
        buttons_frame.pack(fill=tk.X)
        
        self.posicion_var = tk.StringVar(value="Long")
        
        # Botón Long
        self.long_button = tk.Button(buttons_frame, 
                                    text="📈 LONG (Comprar)", 
                                    bg=self.success_color,
                                    fg='white',
                                    font=self.label_font,
                                    relief='flat',
                                    cursor='hand2',
                                    command=lambda: self.select_position("Long"))
        self.long_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=10)
        
        # Botón Short
        self.short_button = tk.Button(buttons_frame, 
                                     text="📉 SHORT (Vender)", 
                                     bg=self.bg_tertiary,
                                     fg=self.text_primary,
                                     font=self.label_font,
                                     relief='flat',
                                     cursor='hand2',
                                     command=lambda: self.select_position("Short"))
        self.short_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=10)
        
    def create_results_panel(self, parent):
        # Card para resultados
        results_card = tk.Frame(parent, bg=self.bg_secondary, relief='solid', bd=1)
        results_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=10)
        
        # Padding interno
        results_frame = tk.Frame(results_card, bg=self.bg_secondary)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Título de resultados
        results_title = tk.Label(results_frame, 
                                text="💰 Análisis de Resultados", 
                                font=self.heading_font,
                                bg=self.bg_secondary, 
                                fg=self.text_secondary)
        results_title.pack(anchor=tk.W, pady=(0, 20))
        
        # Área de resultados con scroll
        self.create_results_area(results_frame)
        
    def create_results_area(self, parent):
        # Frame contenedor con scroll
        results_container = tk.Frame(parent, bg=self.bg_secondary)
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Text widget para resultados
        self.resultado_text = tk.Text(results_container, 
                                    bg=self.bg_tertiary, 
                                    fg=self.text_primary,
                                    font=self.result_font,
                                    relief='flat',
                                    wrap=tk.WORD,
                                    padx=15,
                                    pady=15,
                                    state=tk.DISABLED,
                                    cursor="arrow")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=self.resultado_text.yview)
        self.resultado_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.resultado_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mensaje inicial
        self.show_welcome_message()
        
    def show_welcome_message(self):
        welcome_msg = """
🎯 ¡Bienvenido a la Calculadora de Apalancamiento!

📋 Instrucciones:
├─ Ingresa tu capital inicial
├─ Define el precio de entrada
├─ Establece tu precio objetivo
├─ Selecciona el apalancamiento
└─ Elige tipo de posición (Long/Short)

💡 Consejos:
├─ Usa apalancamiento moderado (5x-20x)
├─ Siempre establece stop-loss
├─ No arriesges más del 2% de tu capital
└─ El trading conlleva riesgos

🚀 ¡Presiona "CALCULAR GANANCIAS" para comenzar!
        """
        
        self.resultado_text.config(state=tk.NORMAL)
        self.resultado_text.delete(1.0, tk.END)
        self.resultado_text.insert(1.0, welcome_msg)
        self.resultado_text.config(state=tk.DISABLED)
    
    # Funciones de utilidad
    def get_placeholder_text(self, label):
        placeholders = {
            "Capital Inicial ($)": "Ej: 1000",
            "Precio de Entrada ($)": "Ej: 45000.50",
            "Precio Objetivo ($)": "Ej: 47000.00"
        }
        return placeholders.get(label, "")
    
    def add_placeholder_effect(self, entry, var, placeholder):
        def on_focus_in(event):
            if var.get() == placeholder:
                var.set("")
                entry.configure(foreground=self.text_primary)
        
        def on_focus_out(event):
            if not var.get():
                var.set(placeholder)
                entry.configure(foreground="#888888")
        
        var.set(placeholder)
        entry.configure(foreground="#888888")
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
    
    def set_leverage(self, value):
        self.apalancamiento_var.set(str(value))
    
    def select_position(self, position):
        self.posicion_var.set(position)
        if position == "Long":
            self.long_button.configure(bg=self.success_color, fg='white')
            self.short_button.configure(bg=self.bg_tertiary, fg=self.text_primary)
        else:
            self.short_button.configure(bg=self.danger_color, fg='white')
            self.long_button.configure(bg=self.bg_tertiary, fg=self.text_primary)
    
    def clear_fields(self):
        fields = [self.capital_var, self.precio_entrada_var, self.precio_objetivo_var]
        placeholders = ["Ej: 1000", "Ej: 45000.50", "Ej: 47000.00"]
        
        for field, placeholder in zip(fields, placeholders):
            field.set(placeholder)
        
        self.apalancamiento_var.set("10")
        self.select_position("Long")
        self.show_welcome_message()
    
    def calcular_ganancias(self):
        try:
            # Obtener y validar valores
            capital_str = self.capital_var.get()
            precio_entrada_str = self.precio_entrada_var.get()
            precio_objetivo_str = self.precio_objetivo_var.get()
            apalancamiento_str = self.apalancamiento_var.get()
            
            # Limpiar placeholders
            if capital_str.startswith("Ej:"):
                capital_str = capital_str.replace("Ej: ", "")
            if precio_entrada_str.startswith("Ej:"):
                precio_entrada_str = precio_entrada_str.replace("Ej: ", "")
            if precio_objetivo_str.startswith("Ej:"):
                precio_objetivo_str = precio_objetivo_str.replace("Ej: ", "")
            
            capital = float(capital_str)
            precio_entrada = float(precio_entrada_str)
            precio_objetivo = float(precio_objetivo_str)
            apalancamiento = int(float(apalancamiento_str))
            posicion = self.posicion_var.get()
            
            # Validaciones
            if capital <= 0 or precio_entrada <= 0 or precio_objetivo <= 0:
                raise ValueError("Todos los valores deben ser positivos")
            
            if apalancamiento < 1 or apalancamiento > 125:
                raise ValueError("El apalancamiento debe estar entre 1x y 125x")
            
            if precio_entrada == precio_objetivo:
                raise ValueError("El precio objetivo debe ser diferente al precio de entrada")
            
            # Cálculos
            if posicion == "Long":
                cambio_porcentual = ((precio_objetivo - precio_entrada) / precio_entrada) * 100
            else:
                cambio_porcentual = ((precio_entrada - precio_objetivo) / precio_entrada) * 100
            
            ganancia_porcentual = cambio_porcentual * apalancamiento
            ganancia_dinero = capital * (ganancia_porcentual / 100)
            capital_final = capital + ganancia_dinero
            
            # Cálculos adicionales
            tamaño_posicion = capital * apalancamiento
            
            # Precio de liquidación (aproximado)
            if posicion == "Long":
                precio_liquidacion = precio_entrada * (1 - (1 / apalancamiento) * 0.9)
            else:
                precio_liquidacion = precio_entrada * (1 + (1 / apalancamiento) * 0.9)
            
            # Formatear resultados con estilo mejorado
            self.mostrar_resultados(capital, precio_entrada, precio_objetivo, apalancamiento, 
                                  posicion, cambio_porcentual, ganancia_porcentual, 
                                  ganancia_dinero, capital_final, tamaño_posicion, precio_liquidacion)
            
        except ValueError as e:
            self.mostrar_error("Error en los datos", str(e))
        except Exception as e:
            self.mostrar_error("Error inesperado", str(e))
    
    def mostrar_resultados(self, capital, precio_entrada, precio_objetivo, apalancamiento, 
                          posicion, cambio_porcentual, ganancia_porcentual, ganancia_dinero, 
                          capital_final, tamaño_posicion, precio_liquidacion):
        
        # Determinar color del resultado
        color_resultado = self.success_color if ganancia_dinero >= 0 else self.danger_color
        emoji_resultado = "📈" if ganancia_dinero >= 0 else "📉"
        
        resultado = f"""
{emoji_resultado} RESULTADO DE LA OPERACIÓN
{'═' * 50}

💼 PARÁMETROS:
├─ Capital: ${capital:,.2f}
├─ Entrada: ${precio_entrada:,.4f}
├─ Objetivo: ${precio_objetivo:,.4f}
├─ Apalancamiento: {apalancamiento}x
└─ Posición: {posicion}

💰 ANÁLISIS FINANCIERO:
├─ Cambio de precio: {cambio_porcentual:+.2f}%
├─ ROE: {ganancia_porcentual:+.2f}%
├─ P&L: ${ganancia_dinero:+,.2f}
├─ Capital final: ${capital_final:,.2f}
├─ Tamaño posición: ${tamaño_posicion:,.2f}
└─ Precio liquidación: ${precio_liquidacion:,.4f}

⚡ ANÁLISIS DE RIESGO:
"""
        
        # Análisis de riesgo
        if abs(ganancia_porcentual) > 100:
            resultado += "├─ 🔴 RIESGO EXTREMO - Posible pérdida total\n"
            resultado += "├─ ⚠️  Considere reducir el apalancamiento\n"
        elif abs(ganancia_porcentual) > 50:
            resultado += "├─ 🟠 RIESGO ALTO - Gran volatilidad\n"
            resultado += "├─ 💡 Use stop-loss estricto\n"
        elif abs(ganancia_porcentual) > 25:
            resultado += "├─ 🟡 RIESGO MEDIO - Monitorear de cerca\n"
        else:
            resultado += "├─ 🟢 RIESGO BAJO - Operación conservadora\n"
        
        # Recomendaciones específicas
        if ganancia_dinero < 0:
            resultado += f"├─ 📉 Pérdida potencial: {abs(ganancia_dinero/capital)*100:.1f}% del capital\n"
        else:
            resultado += f"├─ 📈 Ganancia potencial: {(ganancia_dinero/capital)*100:.1f}% del capital\n"
        
        # Stop loss recomendado
        if posicion == "Long":
            stop_loss = precio_liquidacion * 1.1
        else:
            stop_loss = precio_liquidacion * 0.9
            
        resultado += f"└─ 🛡️  Stop-loss sugerido: ${stop_loss:,.4f}\n"
        
        resultado += f"\n{'═' * 50}"
        resultado += "\n💡 RECORDATORIO:"
        resultado += "\n├─ Este es un cálculo estimativo"
        resultado += "\n├─ No incluye comisiones (~0.1%)"
        resultado += "\n├─ Considere el funding rate"
        resultado += "\n└─ Opere siempre con gestión de riesgo"
        resultado += f"\n{'═' * 50}"
        
        # Mostrar resultados
        self.resultado_text.config(state=tk.NORMAL)
        self.resultado_text.delete(1.0, tk.END)
        self.resultado_text.insert(1.0, resultado)
        self.resultado_text.config(state=tk.DISABLED, fg=self.text_primary)
        
    def mostrar_error(self, titulo, mensaje):
        messagebox.showerror(titulo, f"{mensaje}\n\nPor favor, verifique los datos ingresados.")

def main():
    root = tk.Tk()
    app = BinanceLeverageCalculator(root)
    
    # Establecer icono si existe
    try:
        root.iconbitmap("binance.ico")  # Opcional
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()