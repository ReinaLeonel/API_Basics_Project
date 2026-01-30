from flask import Flask
from flask import request
from flask import Request
from flask import jsonify
import re

# --------------- Correción de error en DELETE ------------------- #
# Descripcion del error:
#                       Al borrar actividades por categoria, no borró todas las actividades que tenían esa categoría.
# Bloque del error: 
#                   Lineas de la 371 a la 374
# Detección del error: 
#             Al iterar y eliminar elementos de la lista "actividades" al mismo tiempo,
#             se generan problemas ya que la lista cambia de tamaño y los índices se desincronizan 
# Corrección:
#             Se creo una copia de la lista "actividades" en la linea 370 y se itero en la copia de la lista, 
#             eliminando los elementos de la lista original. 
#             Esto evita problemas al modificar la lista mientras se itera sobre ella. 
#             Finalmente, se borra la copia para liberar memoria.
# Código del error:
#                   for actividad in actividades:
#                       if actividad["categoria"] == categoriaBorrar:
#                           encontreCategoria = True
#                           actividades.remove(actividad)
# Código resultante:  
#                   actividadesCopy = actividades.copy()
#                       for actividad in actividadesCopy:
#                           if actividad["categoria"] == categoriaBorrar:
#                               encontreCategoria = True
#                               actividades.remove(actividad)
#                   actividadesCopy.clear()
# --------------- ---------------------------- ------------------- #

# Inicializacion de parametros
actividades = []

# Crear la primer app en flask
app = Flask(__name__)

# ------------------------- Funciones -------------------------- #
def validarDatoNumerico(dato):
    regex = r'^\d+$'
    if re.match(regex, dato):
        return True
    return False

def validarCategoria(categoria):
    # Explicacion categorias:
    # 1 - Quiere decir que la actividad no ha comenzado.
    # 2 - Quiere decir que la actividad esta en progreso.
    # 3 - Quiere decir que la actividad ha concluido.
    categoriasValidas = [1,2,3]
    if categoria in categoriasValidas:
        return True
    return False

# ------------------------- --------- -------------------------- #

# Esto por defecto es una peticion get
@app.route("/")
def holaMundo():
    return "Hola mundo!"

# ------------------------- Crear actividades -------------------------- #
# Este enpoint solo va a aceptar una peticion POST
# El body tiene que ser un json con un titulo, una descripcion y una categoria
@app.post("/actividades")
def crearActividad():
    global idUnico # Variable global

    json_repuesta = request.json

    # Validacion recepcion de datos del body
    if 'titulo' not in json_repuesta or 'descripcion' not in json_repuesta or 'categoria' not in json_repuesta:
        return jsonify({
            "respuesta": "titulo, descripcion o categoria no encontrados"
        }), 400

    titulo = json_repuesta["titulo"]
    descripcion = json_repuesta["descripcion"]
    categoria = json_repuesta["categoria"]
    
    # Validacion de datos no vacios
    if titulo == None or descripcion == None or categoria == None or titulo == "" or descripcion == "" or categoria == "":
        return jsonify({
            "respuesta": "titulo, descripcion y categoría no deben de ser vacios"
        }), 400
    
    # Validacion de categoria correcta
    if validarCategoria(categoria) == False:
        return jsonify({
            "respuesta": "Valor de categoria invalido"
        }), 400

    # Agregamos la actividad
    actividades.append({
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "id": idUnico
    })

    idUnicoParaRespuesta = idUnico
    idUnico += 1

    return jsonify({
            "respuesta": "Elemento creado",
            "id": idUnicoParaRespuesta
        }), 201


# ------------------------- Leer actividades -------------------------- #
# Este endpoint solo va a aceptar una peticion GET
# Regresar todas las actividades o una actividad dado un id
@app.get("/actividades")
def leerActividades():
    idPorEncontrar = request.args.get("id") # Cargamos el id
    categoriaEncontrar = request.args.get("categoria") # Cargamos la categoria

     # Arreglo de actividades de acuerdo a categoria
    arregloCategoria = []
    
    # Si no se recibe id ni categoria, se regresan todas las actividades
    if idPorEncontrar == None and categoriaEncontrar == None:
        return jsonify({
            "actividades": actividades
        }), 200
    
    # Validaciones
    # Validacion al tipo de dato del id (Asegurarnos que el id es numerico "1212", "hola")
    if idPorEncontrar != None and validarDatoNumerico(idPorEncontrar) == False:
        return jsonify({
            "respuesta": "El id debe ser numerico"
        }), 400

    # Validacion del tipo de dato de categoria (Asegurarnos que la categoria es numerico)
    if categoriaEncontrar != None and validarDatoNumerico(categoriaEncontrar) == False:
        return jsonify({
            "respuesta": "La categoria debe ser numerica"
        }), 400
    
    # Validacion del tipo de categoria (1 a 3)
    if categoriaEncontrar != None and validarCategoria(int(categoriaEncontrar)) == False:
        return jsonify({
            "respuesta": "Algo salio mal - Categoria erronea"
        }), 400

    ########### Busqueda por ID ###########
    if idPorEncontrar != None:
        idPorEncontrar = int(idPorEncontrar)

        # Buscar la actividad
        encontreElId = False
        indiceDeActividades = 0
        encontreCategoria_ID = False

        # Buscar el id en actividades
        for actividad in actividades:
            if actividad["id"] == idPorEncontrar:
                encontreElId = True
                if categoriaEncontrar != None and actividad["categoria"] == int(categoriaEncontrar):
                    encontreCategoria_ID = True
                break
            indiceDeActividades += 1 

        # Se entrega la actividad con ese id
        if encontreElId == True:
            if categoriaEncontrar == None:
                return jsonify({
                    "respuesta": "id encontrado",
                    "actividad": actividades[indiceDeActividades]
                }), 200 
            
            # Si tambien viene el parametro de categoria
            if categoriaEncontrar != None and encontreCategoria_ID == True: # Si la categoria es correcta
                return jsonify({
                    "respuesta": "ID y categoria encontrados",
                    "actividad": actividades[indiceDeActividades]
                }), 200 

            # Si ese ID no tiene esa categoria
            elif encontreCategoria_ID == False:
                return jsonify({
                    "respuesta": "No se encontraron coincidencias"
                }), 400 
    
    ########### ############# ###########

    ########### Busqueda por categoria ###########
    if categoriaEncontrar != None:
        categoriaEncontrar = int(categoriaEncontrar)
        # Buscar la actividad
        encontreCategoria = False
        
        # Buscar la categoria en actividades
        for actividad in actividades:
            if actividad["categoria"] == categoriaEncontrar:
                encontreCategoria = True
                arregloCategoria.append(actividad)

        # Se entrega lista de actividades con esa categoria
        if encontreCategoria == True:
            return jsonify({
                "respuesta": "Categoria encontrada",
                "actividades": arregloCategoria
            }), 200 
    
    ########### ############# ###########
    
    return jsonify({
                "respuesta": "Algo salio mal - ID o categoria no encontrado"
            }), 400

# ------------------------- Actualizar actividades -------------------------- #
# Este endpoint solo va a aceptar peticiones PATCH
# Actualizar una actividad
# url/actividades?id=
@app.patch("/actividades")
def actualizarActividad():
    json_repuesta = request.json
    idPorActualizar = request.args.get("id")
    actualizarTodo = True

    if idPorActualizar == None:
        return jsonify({
            "respuesta": "No se tiene el ID"
        }), 400

    # Requisito es que nos manden el json que quiera actualizar, con: Titulo, descripcion y categoria o con: Categoria
    # Validar siempre los datos
    if 'titulo' not in json_repuesta and 'descripcion' not in json_repuesta:
        if 'categoria' in json_repuesta:
            categoria = json_repuesta["categoria"]
            actualizarTodo = False

    if 'titulo' in json_repuesta or 'descripcion' in json_repuesta:
        if 'categoria' not in json_repuesta:
            return jsonify({
                "respuesta": "Categoria no encontrada"
            }), 400
        if 'categoria' in json_repuesta and ('titulo' not in json_repuesta or 'descripcion' not in json_repuesta):
            return jsonify({
                "respuesta": "Titulo o descripcion no encontrados"
            }), 400
        else:
            titulo = json_repuesta["titulo"]
            descripcion = json_repuesta["descripcion"]
            categoria = json_repuesta["categoria"]
            actualizarTodo = True
    
    
    if actualizarTodo == True and (titulo == None or descripcion == None or categoria == None or titulo == "" or descripcion == "" or categoria == ""):
        return jsonify({
            "respuesta": "Titulo, descripcion y categoria no deben de ser vacios"
        }), 400
    
    if actualizarTodo == False and (categoria == None or categoria == ""):
        return jsonify({
            "respuesta": "Categoria no debe ser vacio"
        }), 400
    
    # Validacion de categoria correcta
    if validarCategoria(categoria) == False:
        return jsonify({
            "respuesta": "Valor de categoria invalido"
        }), 400
    
    idPorActualizar = int(idPorActualizar)
    encontreElId = False
    indiceDeActividades = 0

    #Buscar el id en actividades
    for actividad in actividades:
        if actividad["id"] == idPorActualizar:
            encontreElId = True
            break
        indiceDeActividades += 1

    if encontreElId == True:
        actividad = actividades[indiceDeActividades]
        if actualizarTodo == True:
            actividad["titulo"] = titulo
            actividad["descripcion"] = descripcion
        
        actividad["categoria"] = categoria
        return jsonify({
                "respuesta": "Actividad actualizada"
            }), 200
    
    return jsonify({
                "respuesta": "Algo salio mal"
            }), 400 

# ------------------------- Borrar actividades -------------------------- #
# Este endpoint es para peticiones DELETE
# Borrar todas las actividades, una sola dado un ID o todas las actividades dada una categoria
@app.delete("/actividades")
def borrarActividades():
    # Obtencion de parametros
    idPorBorrar = request.args.get("id") 
    categoriaBorrar = request.args.get("categoria")

    # Borrar todo (Si no hay id ni categoria)
    if idPorBorrar == None and categoriaBorrar == None:
        actividades.clear()
        return jsonify({
            "respuesta": "Elementos eliminados"
        }), 200
    
    # Validaciones
    # Validacion al tipo de dato del id (Asegurarnos que el id es numerico "1212", "hola")
    if idPorBorrar != None and validarDatoNumerico(idPorBorrar) == False:
        return jsonify({
            "respuesta": "El id debe ser numerico"
        }), 400

    # Validacion del tipo de dato de categoria (Asegurarnos que la categoria es numerico)
    if categoriaBorrar != None and validarDatoNumerico(categoriaBorrar) == False:
        return jsonify({
            "respuesta": "La categoria debe ser numerica"
        }), 400
    
    # Validacion del tipo de categoria (1 a 3)
    if categoriaBorrar != None and validarCategoria(int(categoriaBorrar)) == False:
        return jsonify({
            "respuesta": "Algo salio mal - Categoria erronea"
        }), 400

    ########### Borrar por ID ###########
    if idPorBorrar != None:
        # Buscar la actividad
        idPorBorrar = int(request.args.get("id"))
        encontreElId = False
        indiceDeActividades = 0
        encontreCategoria_ID = False

        # Buscar el id en actividades
        for actividad in actividades:
            if actividad["id"] == idPorBorrar:
                encontreElId = True
                if categoriaBorrar != None and actividad["categoria"] == int(categoriaBorrar):
                    encontreCategoria_ID = True
                break
            indiceDeActividades += 1

        if encontreElId == True and categoriaBorrar != None and encontreCategoria_ID == False:
            return jsonify({
                "respuesta": "ID y categoria no coinciden"
            }), 400 

        if encontreElId == True:
            actividades.pop(indiceDeActividades)
            return jsonify({
                "respuesta": "Actividad borrada con exito"
            }), 200 
        if encontreElId == False:
            return jsonify({
                "respuesta": "ID no encontrado"
            }), 400 
        
    ########### ############# ###########
    
    ########### Borrar por categoria ###########
    if categoriaBorrar != None:
        categoriaBorrar = int(categoriaBorrar)
        # Buscar la actividad
        encontreCategoria = False
        
        # Buscar la categoria en actividades
        actividadesCopy = actividades.copy() # Creacion de copia para evitar problemas al borrar mientras se itera
        for actividad in actividadesCopy:
            if actividad["categoria"] == categoriaBorrar:
                encontreCategoria = True
                actividades.remove(actividad)
        actividadesCopy.clear() # Borrando la copia

        # Categoria borrada con exito
        if encontreCategoria == True:
            return jsonify({
                "respuesta": "Actividades eliminadas con exito"
            }), 200 
        
        if encontreCategoria == False:
            return jsonify({
                "respuesta": "Ninguna actividad fue eliminada, no hay elementos con la categoria indicada"
            }), 200 
    
    ########### ############# ###########
    
    return jsonify({
                "respuesta": "Algo salio mal - Error al borrar"
            }), 400

idUnico = 0 # Inicializacion de la variable global
app.run(debug=True)