import ply.lex as lex
from tkinter import messagebox

# Lista de tokens
tokens = [
    'tk_begin', 'tk_end', 'tk_pick', 'tk_make', 'tk_table', 'tk_with', 
    'tk_from', 'tk_when', 'tk_modify', 'tk_set', 'tk_where', 
    'tk_remove', 'tk_permanently', 'tk_ints', 'tk_chars', 
    'tk_timed', 'tk_asign', 'tk_closing', 'tk_separator', 
    'tk_comment', 'tk_corchOpen', 'tk_corchClose', 
    'tk_operator', 'tk_ID', 'tk_num', 'tk_cadena'
]

# Diccionario de palabras reservadas
reserved = {
    'BEGIN': 'tk_begin',
    'END': 'tk_end',  # Asegúrate de que esto esté presente
    'PICK': 'tk_pick',
    'MAKE': 'tk_make',
    'TABLE': 'tk_table',
    'WITH': 'tk_with',
    'FROM': 'tk_from',
    'WHEN': 'tk_when',
    'MODIFY': 'tk_modify',
    'SET': 'tk_set',
    'WHERE': 'tk_where',
    'REMOVE': 'tk_remove',
    'PERMANENTLY': 'tk_permanently',
    'INTS': 'tk_ints',
    'CHARS': 'tk_chars',
    'TIMED': 'tk_timed'
}

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Definición de tokens con expresiones regulares
t_tk_asign = r'='
t_tk_closing = r';'
t_tk_separator = r',' 
t_tk_corchOpen = r'\['
t_tk_corchClose = r'\]'
t_tk_operator = r'(>|<|==|>=|<=|!=)'

# Comentarios
def t_tk_comment(t):
    r'//.*'
    pass  # Ignorar comentarios

# Identificadores y palabras reservadas
def t_tk_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.upper(), 'tk_ID')  # Verificar si es palabra reservada
    return t

# Cadenas de texto (eliminamos las comillas)
def t_tk_cadena(t):
    r'\'[^\']*\''  # Coincide con cadenas entre comillas simples
    t.value = t.value[1:-1]  # Eliminamos las comillas alrededor de la cadena
    return t

# Números
def t_tk_num(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Manejo de nuevas líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Lista de errores léxicos
lexical_errors = []

# Clase para manejar errores léxicos
class LexicalError:
    def __init__(self, char, line, position, message):
        self.char = char
        self.line = line
        self.position = position
        self.message = message

    def __str__(self):
        return f"Error en línea {self.line}: Carácter ilegal '{self.char}'"

# Manejo de errores
def t_error(t):
    global lexical_errors
    # Obtener contexto del error (5 caracteres antes y después)
    start = max(0, t.lexpos - 5)
    end = min(len(t.lexer.lexdata), t.lexpos + 6)
    context = t.lexer.lexdata[start:end]
    
    # Marcar la posición del error en el contexto
    pos_in_context = min(5, t.lexpos - start)
    marked_context = f"{context[:pos_in_context]}→{t.value[0]}←{context[pos_in_context+1:]}"
    
    # Obtener la línea completa donde ocurrió el error
    lines = t.lexer.lexdata.split('\n')
    error_line = lines[t.lineno - 1] if t.lineno <= len(lines) else ""
    
    # Crear mensaje de error detallado
    error_msg = (
        f"Error léxico en línea {t.lineno}:\n"
        f"Carácter ilegal '{t.value[0]}' encontrado\n"
        f"Línea completa: {error_line}\n"
        f"Posición: {' ' * t.lexpos}^\n"
        f"Contexto: {marked_context}"
    )
    
    error = LexicalError(
        t.value[0],
        t.lineno,
        t.lexpos,
        error_msg
    )
    lexical_errors.append(error)
    
    # Marcar el token como error para que el analizador principal lo detecte
    t.error = True
    return t

# Construcción del lexer
lexer = lex.lex(debug=True)

# Función para reiniciar errores
def reset_errors():
    global lexical_errors
    lexical_errors = []
