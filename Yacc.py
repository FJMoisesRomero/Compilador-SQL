import ply.yacc as yacc
from tkinter import messagebox
from Lex import tokens

# Lista para almacenar las instrucciones SQL
sql_instructions = []

# Lista para almacenar errores sintácticos
syntax_errors = []

class SyntaxError:
    def __init__(self, token, line, position, expected=None):
        self.token = token
        self.line = line
        self.position = position
        self.expected = expected

    def __str__(self):
        if self.token:
            if self.expected:
                return f"Error en línea {self.line}: se esperaba {self.expected}"
            return f"Error en línea {self.line}: token inesperado '{self.token}'"
        return f"Error en línea {self.line}: error de sintaxis"

def p_programa(p):
    '''programa : tk_begin instrucciones tk_end programa_fin'''
    p[0] = p[2]  # Guardamos las instrucciones procesadas

def p_instrucciones(p):
    '''instrucciones : instruccion tk_closing instrucciones
                    | empty'''
    if len(p) > 2:
        p[0] = [p[1]] + (p[3] if p[3] is not None else [])
    else:
        p[0] = []

def p_instruccion(p):
    '''instruccion : declaracion_tabla
                  | seleccion_datos
                  | modificacion_datos
                  | eliminacion_tabla
                  | comentario'''
    p[0] = p[1]

def p_declaracion_tabla(p):
    '''declaracion_tabla : tk_make tk_table tk_ID tk_with tk_corchOpen lista_campos tk_corchClose'''
    campos = p[6] if isinstance(p[6], str) else ", ".join(p[6])
    sql_instructions.append(f"CREATE TABLE {p[3]} ({campos})")

def p_eliminacion_tabla(p):
    '''eliminacion_tabla : tk_remove tk_table tk_ID tk_permanently'''
    sql_instructions.append(f"DROP TABLE {p[3]}")

def p_lista_campos(p):
    '''lista_campos : campo tk_separator lista_campos
                   | campo'''
    if len(p) == 4:
        if isinstance(p[3], list):
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1], p[3]]
    else:
        p[0] = [p[1]]

def p_campo(p):
    '''campo : tk_ID tipo_dato'''
    p[0] = f"{p[1]} {p[2]}"

def p_tipo_dato(p):
    '''tipo_dato : tk_ints
                | tk_chars
                | tk_timed'''
    tipo_map = {
        'INTS': 'INT',
        'CHARS': 'VARCHAR(255)',
        'TIMED': 'DATETIME'
    }
    p[0] = tipo_map.get(p[1], p[1])

def p_seleccion_datos(p):
    '''seleccion_datos : tk_pick lista_campos_seleccion tk_from tk_ID condicional_opcional'''
    campos = ", ".join(p[2] if isinstance(p[2], list) else [p[2]])
    sql = f"SELECT {campos} FROM {p[4]}"
    if p[5]:  # Si hay condición WHEN
        sql += f" WHERE {p[5]}"
    sql_instructions.append(sql)

def p_lista_campos_seleccion(p):
    '''lista_campos_seleccion : tk_ID tk_separator lista_campos_seleccion
                             | tk_ID'''
    if len(p) == 4:
        if isinstance(p[3], list):
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1], p[3]]
    else:
        p[0] = [p[1]]

def p_condicional_opcional(p):
    '''condicional_opcional : tk_when condicion
                           | empty'''
    p[0] = p[2] if len(p) == 3 else None

def p_modificacion_datos(p):
    '''modificacion_datos : tk_modify tk_ID tk_set lista_asignaciones condicion_where'''
    # Unir las asignaciones con coma
    sql = f"UPDATE {p[2]} SET {', '.join(p[4])}"  # `p[4]` es la lista de asignaciones
    if p[5]:  # Si hay una condición WHERE
        sql += f" WHERE {p[5]}"
    sql_instructions.append(sql)

def p_lista_asignaciones(p):
    '''lista_asignaciones : asignacion tk_separator lista_asignaciones
                          | asignacion'''
    if len(p) == 4:  # Si hay más de una asignación
        p[0] = [p[1]] + p[3]  # Concatenamos la asignación a la lista
    else:
        p[0] = [p[1]]  # Si solo hay una asignación, lo asignamos como lista

def p_asignacion(p):
    '''asignacion : tk_ID tk_asign valor'''
    # Si es una cadena, la rodeamos de comillas
    if isinstance(p[3], str):
        p[0] = f"{p[1]} = '{p[3]}'"
    else:
        p[0] = f"{p[1]} = {p[3]}"  # Si es número, no se rodea con comillas

def p_condicion_where(p):
    '''condicion_where : tk_where expresion_relacional_where
                       | empty'''
    if len(p) == 3:
        p[0] = p[2]  # Asignamos la condición WHERE
    else:
        p[0] = None  # Si no hay condición, asignamos None

def p_condicion(p):
    '''condicion : expresion_relacional'''
    p[0] = p[1]

def p_expresion_relacional(p):
    '''expresion_relacional : tk_ID tk_operator valor'''
    valor = f"'{p[3]}'" if isinstance(p[3], str) and not str(p[3]).isdigit() else p[3]
    p[0] = f"{p[1]} {p[2]} {valor}"

def p_expresion_relacional_where(p):
    '''expresion_relacional_where : tk_ID tk_asign valor'''
    valor = f"'{p[3]}'" if isinstance(p[3], str) else p[3]  # Si es cadena, la rodeamos con comillas
    p[0] = f"{p[1]} = {valor}"  # En WHERE usamos asignación, por eso usamos '=' en lugar de un operador relacional

def p_valor(p):
    '''valor : tk_num
             | tk_cadena
             | tk_ID'''
    p[0] = p[1]

def p_comentario(p):
    '''comentario : tk_comment'''
    pass

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    global syntax_errors
    if p:
        # Obtener la línea completa donde ocurrió el error
        lines = p.lexer.lexdata.split('\n')
        error_line = lines[p.lineno - 1] if p.lineno <= len(lines) else ""
        
        # Intentar determinar qué se esperaba
        expected = None
        error_pos = p.lexpos
        
        # Diccionario de traducción de tokens a palabras clave
        token_to_keyword = {
            'tk_from': 'FROM',
            'tk_set': 'SET',
            'tk_where': 'WHERE',
            'tk_permanently': 'PERMANENTLY',
            'tk_with': 'WITH',
            'tk_when': 'WHEN',
            'tk_separator': ',',
            'tk_corchClose': ']',
            'tk_closing': ';',
            'tk_table': 'TABLE'
        }

        if hasattr(parser, 'symstack'):
            state = parser.state
            try:
                action = parser.action[state].get(p.type)
                if action is None:
                    # Obtener lista de tokens esperados
                    expected_tokens = [t for t in parser.action[state].keys() if t != '$end']
                    # Traducir tokens a palabras clave
                    expected = ' o '.join(f"'{token_to_keyword.get(t, t)}'" for t in expected_tokens[:3])
            except:
                pass

        # Determinar el tipo de error basado en el contexto y la línea actual
        error_msg = ""
        error_context = error_line.strip().upper()

        # Verificar el contexto específico del error
        if 'MAKE TABLE' in error_context:
            if not error_line.strip().endswith(';'):
                error_msg = "Falta el punto y coma (;) al final"
            if ']' not in error_line and '[' in error_line:
                error_msg = "Falta el corchete de cierre (])"
        elif 'PICK' in error_context and 'FROM' not in error_context:
            error_msg = "Falta la palabra FROM"
        elif 'MODIFY' in error_context and 'SET' not in error_context:
            error_msg = "Falta la palabra SET"
        elif 'REMOVE TABLE' in error_context and 'PERMANENTLY' not in error_context:
            error_msg = "Falta la palabra PERMANENTLY"
        else:
            error_msg = f"Token inesperado '{p.value}'"
            if expected:
                error_msg += f", se esperaba: {expected}"

        # Crear el error
        error = SyntaxError(
            p.value,
            p.lineno,
            error_pos,
            error_msg
        )
        syntax_errors.append(error)
        
        # Guardar información para el analizador principal
        parser.error_pos = error_pos
        parser.expected = expected
        
        # Levantar una excepción con el mensaje de error
        raise Exception(error_msg)

    else:
        error_msg = "Error de sintaxis al final del archivo"
        error = SyntaxError(
            None,
            'final del archivo',
            0,
            error_msg
        )
        syntax_errors.append(error)
        raise Exception(error_msg)

def reset_errors():
    global syntax_errors
    syntax_errors = []

def p_programa_fin(p):
    '''programa_fin : '''
    pass  # Esta regla no hace nada pero permite que el parser termine correctamente

parser = yacc.yacc(debug=False, write_tables=False, errorlog=yacc.NullLogger())
