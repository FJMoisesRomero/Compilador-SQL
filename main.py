import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from Lex import lexer, lexical_errors, reset_errors as reset_lexical_errors
from Yacc import parser, sql_instructions, syntax_errors, reset_errors as reset_syntax_errors
from SQL import generar_sql_code
import time

class AnalizadorDFQL:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Analizador DFQL")
        self.ventana.geometry("1200x800")  # Ventana más grande
        self.ventana.minsize(1200, 800)
        self.ventana.configure(bg="#F8F9FA")
        
        self.crear_interfaz()

    def crear_interfaz(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self.ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título principal
        titulo = ttk.Label(
            main_frame,
            text="Analizador de Lenguaje DFQL",
            font=("Helvetica", 20, "bold"),
            foreground="#343A40"
        )
        titulo.pack(pady=10)

        # Botón para cargar archivo
        boton_frame = ttk.Frame(main_frame)
        boton_frame.pack(fill=tk.X, pady=5)
        
        boton_cargar = ttk.Button(
            boton_frame,
            text="Cargar archivo DFQL",
            command=self.cargar_archivo,
            style="Accent.TButton"
        )
        boton_cargar.pack(side=tk.LEFT, padx=5)

        # Panel principal que contiene los tres cuadros de texto
        panel_principal = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        panel_principal.pack(fill=tk.BOTH, expand=True, pady=5)

        # Frame para el área de depuración
        debug_frame = ttk.LabelFrame(panel_principal, text="Proceso de Análisis", padding="5")
        panel_principal.add(debug_frame, weight=2)

        self.debug_text = scrolledtext.ScrolledText(
            debug_frame,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("Consolas", 10),
            bg="#1E1E1E",  # Fondo oscuro para mejor contraste
            fg="#FFFFFF"   # Texto base en blanco
        )
        self.debug_text.pack(fill=tk.BOTH, expand=True)

        # Configurar tags para diferentes tipos de mensajes
        self.debug_text.tag_config("info", foreground="#00B7C3")      # Azul claro
        self.debug_text.tag_config("error", foreground="#FF3333")     # Rojo brillante
        self.debug_text.tag_config("success", foreground="#4EC9B0")   # Verde azulado
        self.debug_text.tag_config("warning", foreground="#FFB700")   # Amarillo
        self.debug_text.tag_config("timestamp", foreground="#569CD6") # Azul para timestamps
        self.debug_text.tag_config("separator", foreground="#569CD6") # Azul para separadores
        self.debug_text.tag_config("code", foreground="#CE9178")      # Naranja para código

        # Panel inferior para código fuente y SQL
        panel_inferior = ttk.PanedWindow(panel_principal, orient=tk.HORIZONTAL)
        panel_principal.add(panel_inferior, weight=1)

        # Frame para el código fuente
        codigo_frame = ttk.LabelFrame(panel_inferior, text="Código DFQL", padding="5")
        panel_inferior.add(codigo_frame, weight=1)

        self.codigo_text = scrolledtext.ScrolledText(
            codigo_frame,
            wrap=tk.NONE,
            width=40,
            height=10,
            font=("Consolas", 10),
            bg="#1E1E1E",  # Fondo oscuro
            fg="#D4D4D4"   # Texto en gris claro
        )
        self.codigo_text.pack(fill=tk.BOTH, expand=True)

        # Frame para el SQL generado
        sql_frame = ttk.LabelFrame(panel_inferior, text="SQL Generado", padding="5")
        panel_inferior.add(sql_frame, weight=1)

        self.sql_text = scrolledtext.ScrolledText(
            sql_frame,
            wrap=tk.NONE,
            width=40,
            height=10,
            font=("Consolas", 10),
            bg="#1E1E1E",  # Fondo oscuro
            fg="#D4D4D4"   # Texto en gris claro
        )
        self.sql_text.pack(fill=tk.BOTH, expand=True)

        # Configurar tags para el SQL
        self.sql_text.tag_config("error", foreground="#FF3333")
        self.sql_text.tag_config("success", foreground="#4EC9B0")
        self.sql_text.tag_config("warning", foreground="#FFB700")

        # Configurar estilos
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Helvetica", 10))

    def log(self, message, level="info"):
        """Agrega un mensaje al área de depuración con formato mejorado"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Agregar separadores para mejor visualización
        if level == "error":
            self.debug_text.insert(tk.END, "\n" + "="*50 + "\n", "separator")
            self.debug_text.insert(tk.END, f"[{timestamp}] ❌ ", "timestamp")
            self.debug_text.insert(tk.END, message + "\n", level)
        elif level == "success":
            self.debug_text.insert(tk.END, "\n" + "-"*50 + "\n", "separator")
            self.debug_text.insert(tk.END, f"[{timestamp}] ✅ ", "timestamp")
            self.debug_text.insert(tk.END, message + "\n", level)
        elif level == "warning":
            self.debug_text.insert(tk.END, "\n" + "-"*50 + "\n", "separator")
            self.debug_text.insert(tk.END, f"[{timestamp}] ⚠️ ", "timestamp")
            self.debug_text.insert(tk.END, message + "\n", level)
        else:  # info
            self.debug_text.insert(tk.END, f"[{timestamp}] ℹ️ ", "timestamp")
            self.debug_text.insert(tk.END, message + "\n", level)
        
        self.debug_text.see(tk.END)
        self.ventana.update()
        time.sleep(0.1)  # Pequeña pausa para mejor visualización del proceso

    def clear_debug(self):
        """Limpia el área de depuración"""
        self.debug_text.delete(1.0, tk.END)

    def mostrar_codigo(self, texto):
        """Muestra el código DFQL"""
        self.codigo_text.delete(1.0, tk.END)
        self.codigo_text.insert(tk.END, texto)

    def mostrar_sql(self, resultado, status):
        """Muestra el SQL generado con formato según el estado"""
        self.sql_text.delete(1.0, tk.END)
        if status == "error":
            self.sql_text.tag_config("error", foreground="#DC3545")
            self.sql_text.insert(tk.END, resultado, "error")
        elif status == "success":
            self.sql_text.tag_config("success", foreground="#28A745")
            self.sql_text.insert(tk.END, resultado, "success")
        else:
            self.sql_text.tag_config("warning", foreground="#FFC107")
            self.sql_text.insert(tk.END, resultado, "warning")

    def analizar_archivo(self, filepath):
        """Analiza un archivo DFQL y genera el código SQL o muestra errores."""
        try:
            self.clear_debug()
            self.log("🔍 Iniciando análisis del archivo...", "info")
            
            with open(filepath, 'r', encoding='utf-8') as file:
                data = file.read()
            
            self.log(f"📂 Archivo cargado: {filepath}", "info")
            self.log("📄 Contenido del archivo:", "info")
            self.log(f"{data}", "code")
            
            # Limpiamos las instrucciones y errores anteriores
            sql_instructions.clear()
            reset_lexical_errors()
            reset_syntax_errors()
            self.log("🧹 Limpieza de errores anteriores completada", "info")
            
            # Preparamos el código
            lines = [line.strip() for line in data.split('\n') if line.strip()]
            tiene_errores_lexicos = False
            tiene_errores_sintacticos = False
            tokens_por_linea = []
            
            # Primer paso: Análisis léxico línea por línea
            self.log("\n🔎 Iniciando análisis léxico línea por línea...", "info")
            
            for i, line in enumerate(lines, 1):
                if line.startswith('//'):
                    continue
                
                self.log(f"\n{'='*50}", "separator")
                self.log(f"Analizando línea {i}:", "info")
                self.log(line, "code")
                
                # Análisis léxico de la línea
                lexer.lineno = i
                lexer.input(line)
                tokens_linea = []
                tiene_error_lexico = False
                
                while True:
                    try:
                        tok = lexer.token()
                        if not tok:
                            break
                        if hasattr(tok, 'error'):
                            tiene_error_lexico = True
                            tiene_errores_lexicos = True
                            self.log(f"{'~' * tok.lexpos}^", "error")
                            self.log(f"❌ Error léxico: carácter inválido '{tok.value}'", "error")
                        else:
                            tokens_linea.append(tok)
                    except Exception as e:
                        tiene_error_lexico = True
                        tiene_errores_lexicos = True
                        self.log(f"❌ Error léxico inesperado: {str(e)}", "error")
                        break
                
                if not tiene_error_lexico:
                    self.log("✅ Análisis léxico de línea completado", "success")
                    tokens_por_linea.append((i, line, tokens_linea))
            
            if tiene_errores_lexicos:
                self.log("\n❌ Se encontraron errores léxicos", "error")
                if lexical_errors:
                    self.log("\nResumen de Errores Léxicos:", "error")
                    for error in lexical_errors:
                        self.log(str(error), "error")
                return data, "Se encontraron errores léxicos", "error"
            
            # Segundo paso: Análisis sintáctico línea por línea
            self.log("\n🔍 Iniciando análisis sintáctico línea por línea...", "info")
            
            instrucciones_sql = []
            
            for i, line, tokens in tokens_por_linea:
                if line.strip().upper() in ['BEGIN', 'END']:
                    continue
                
                self.log(f"\n{'='*50}", "separator")
                self.log(f"Analizando sintaxis de línea {i}:", "info")
                self.log(line, "code")
                
                try:
                    # Verificar si la línea termina con punto y coma
                    line_sin_comentarios = line.split('//')[0].strip()
                    if not line_sin_comentarios.endswith(';') and not line_sin_comentarios.endswith(']'):
                        line = line + ';'
                    
                    # Agregamos BEGIN y END temporalmente para cada línea
                    line_completa = f"BEGIN\n{line}\nEND"
                    
                    # Intentamos parsear la línea
                    result = parser.parse(line_completa)
                    
                    # Si llegamos aquí, no hubo errores sintácticos
                    if sql_instructions:
                        # Tomamos solo la última instrucción SQL generada
                        ultima_sql = sql_instructions[-1]
                        instrucciones_sql.append(ultima_sql)
                        sql_instructions.clear()  # Limpiamos para la siguiente línea
                        self.log(f"✅ SQL generado: {ultima_sql}", "success")
                    
                except Exception as e:
                    tiene_errores_sintacticos = True
                    error_msg = str(e)
                    self.log(f"❌ Error sintáctico: {error_msg}", "error")
                    
                    # Mostrar posición del error si está disponible
                    if hasattr(parser, 'error_pos'):
                        self.log(f"{'~' * parser.error_pos}^", "error")
                    
                    # Mostrar tokens esperados si están disponibles
                    if hasattr(parser, 'expected'):
                        self.log(f"Se esperaba: {parser.expected}", "warning")
            
            # Resumen final
            if tiene_errores_sintacticos:
                self.log("\n❌ Se encontraron errores sintácticos", "error")
                if syntax_errors:
                    self.log("\nResumen de Errores Sintácticos:", "error")
                    for error in syntax_errors:
                        self.log(str(error), "error")
                return data, "Se encontraron errores sintácticos", "error"
            else:
                if instrucciones_sql:
                    sql_code = "\n".join(instrucciones_sql)
                    self.log("\n✨ Análisis completado exitosamente", "success")
                    self.log("🎉 SQL Generado:", "success")
                    self.log(sql_code, "code")
                    return data, sql_code, "success"
                else:
                    self.log("\n⚠️ No se generaron instrucciones SQL", "warning")
                    return data, "No se generaron instrucciones SQL", "warning"
            
        except FileNotFoundError:
            self.log(f"❌ Error: El archivo '{filepath}' no se encontró.", "error")
            return "", f"El archivo '{filepath}' no se encontró.", "error"
        except Exception as e:
            self.log(f"💥 Error inesperado: {str(e)}", "error")
            return "", f"Error inesperado: {str(e)}", "error"

    def cargar_archivo(self):
        """Abre un cuadro de diálogo para seleccionar un archivo y analiza su contenido."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo DFQL",
            filetypes=(("Archivos DFQL", "*.txt"), ("Todos los archivos", "*.*"))
        )
        if filepath:
            texto_archivo, resultado_sql, status = self.analizar_archivo(filepath)
            self.mostrar_codigo(texto_archivo)
            self.mostrar_sql(resultado_sql, status)

    def iniciar(self):
        """Inicia la aplicación"""
        self.ventana.mainloop()

if __name__ == "__main__":
    app = AnalizadorDFQL()
    app.iniciar()
