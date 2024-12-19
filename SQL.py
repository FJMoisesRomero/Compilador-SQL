def generar_sql_code(instructions):
    """
    Genera código SQL a partir de las instrucciones procesadas.
    Filtra las instrucciones vacías y maneja correctamente las condiciones.
    """
    sql_code = []
    
    for instruction in instructions:
        if instruction:
            # Si es una tupla o lista, la convertimos a string
            if isinstance(instruction, (tuple, list)):
                instruction = ' '.join(str(x) for x in instruction if x is not None)
            
            # Solo agregamos la instrucción si no está vacía después de procesarla
            if instruction.strip():
                sql_code.append(instruction.strip())
    
    return "\n".join(sql_code)
