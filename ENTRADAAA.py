import time
from tkinter import *
from datetime import datetime
import psycopg2

# Configuración de conexión
conn = psycopg2.connect(
    dbname="tiendagalletas",
    user="postgres",
    password="002223",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

def set_current_date():
    fecha_ticket_var.set(datetime.now().strftime("%d-%m-%y"))  # Establece la fecha actual en el campo de fecha

# Función para mover el enfoque al siguiente campo
def focus_next(event, next_widget):
    next_widget.focus_set()

def save_ticket_header():
    try:
        cursor.execute(
            """
            INSERT INTO tg.enc_tick (fol_tick, id_empl, fec, rs)
            VALUES (%s, %s, %s, %s)
            """,
            (folio_ticket_var.get(), clave_empleado_var.get(), fecha_ticket_var.get(), razon_social_var.get())
        )
        conn.commit()
        print("Encabezado de ticket guardado en la base de datos.")
    except Exception as e:
        print(f"Error al guardar encabezado de ticket: {e}")
        conn.rollback()
        

def save_ticket_item():
    try:
        cursor.execute(
            """
            INSERT INTO tg.des_tick (fol_tickt, id_prod, cant)
            VALUES (%s, %s, %s)
            """,
            (folio_ticket_var.get(), clave_producto_var.get(), cantidad_var.get())
        )
        conn.commit()
        print("Artículo guardado en la base de datos.")
    except Exception as e:
        print(f"Error al guardar artículo: {e}")
        conn.rollback()

# Función para guardar los datos de la ticket o producto
def save_data(entry_widget, var_name, is_product):
    var_name.set(entry_widget.get())  # Guardar el dato
    if is_product:
        print(f"Producto Guardado: {var_name.get()}")  # Verificar artículo guardado
    else:
        print(f"ticket Guardada: {var_name.get()}")  # Verificar ticket guardada

# Función para bloquear los campos del encabezado (ticket)
def lock_header_fields():
    save_ticket_header()  # Guardar el encabezado en la base de datos
    clave_empleado_entry.config(state="disabled")
    folio_ticket_entry.config(state="disabled")
    razon_social_entry.config(state="disabled")
    print("Campos del encabezado bloqueados.")


# Función para habilitar los campos para ingresar los productos
def enable_inferior_frame():
    clave_producto_entry.focus_set()  # Mover el enfoque al primer campo del frame inferior


# Variables para controlar el doble Enter
last_enter_time = 0  # Guardará el tiempo de la última pulsación de Enter
double_enter_threshold = 0.5  # Tiempo máximo entre pulsaciones para considerar doble Enter (en segundos)

# Función para manejar el doble Enter en "Razón social"
def on_double_enter(event):
    global last_enter_time
    current_time = time.time()  # Tiempo actual

    # Si el tiempo entre el último Enter y este es menor que el umbral, se considera un doble Enter
    if current_time - last_enter_time < double_enter_threshold:
        # Bloqueamos los campos del encabezado
        lock_header_fields()
        # Habilitamos el frame inferior y movemos el enfoque
        enable_inferior_frame()
        # Guardamos la ticket
        save_data(razon_social_entry, razon_social_var, is_product=False)
        # Ocultamos el mensaje de "Doble enter para guardar"
        mensaje_label.grid_forget()
    else:
        # Si es la primera pulsación, solo actualizamos el tiempo
        last_enter_time = current_time
        # Mostramos el mensaje "Doble enter para guardar"
        mensaje_label.grid(row=6, column=2, columnspan=2, pady=5, sticky="w")

# Función para manejar el evento de Enter en el campo de cantidad (Agregar producto)
def on_cantidad_enter(event):
    save_data(cantidad_entry, cantidad_var, is_product=True)  # Guardamos el producto
    instrucciones_label.grid(row=3, column=0, columnspan=4, pady=10, sticky="w")  # Mostrar instrucciones para agregar otro artículo
    clear_fields()  # Limpiar los campos del producto para agregar otro
    

# Función para limpiar todos los campos de la interfaz
def clear_fields():
    
    # Limpiar los campos de los productos
    clave_producto_var.set("")
    nombre_producto_var.set("")
    cantidad_var.set("")
    
    # Volver al primer campo de la interfaz (clave de producto)
    clave_producto_entry.focus_set()

def nuevo_folio():
    # Desbloqueamos los campos del encabezado
    folio_ticket_entry.config(state="normal")
    clave_empleado_entry.config(state="normal")
    razon_social_entry.config(state="normal")
    
    # Limpiamos los campos del encabezado y el cuerpo del ticket
    folio_ticket_var.set("")
    clave_empleado_var.set("")
    razon_social_var.set("")
    instrucciones_label.grid_forget()  # Ocultar las instrucciones después de mostrar
    
    # Volver al primer campo del encabezado
    folio_ticket_entry.focus_set()
    print("Nuevo folio: Campos desbloqueados y limpios.")

# Función para manejar el doble clic en el campo de cantidad
def on_double_click_cantidad(event):
    clear_fields()  # Limpiar todos los campos cuando se hace doble clic en "Cantidad"
    print("Campos limpiados por doble clic en Cantidad.")

# Crear la ventana principal
raiz = Tk()
raiz.title("Catalogo de tickets")
raiz.iconbitmap("t_icon.ico")
raiz.config(bg="lemonchiffon1")
raiz.state("zoomed")  # Esto hace que la ventana se inicie maximizada
raiz.minsize(1000, 650)

imagen_icono = PhotoImage(file="Ticket_logo.png")

# Frame del encabezado de ticket
frame_superior = Frame(raiz, bg="lemonchiffon1", pady=0)
frame_superior.grid(row=0, column=0, sticky="nsew", padx=0)

# Título
titulo = Label(frame_superior, text="       Catálogo de tickets", font=("Book Antiqua", 24, "bold"), bg="darkolivegreen3", fg="black")
titulo.grid(row=0, column=0, columnspan=29, sticky="nsew")

# Imagen
icono = Label(frame_superior, bg="lemonchiffon1", width=200, height=200, image=imagen_icono)
icono.grid(row=2, column=1, rowspan=4, padx=(10, 30), sticky="w")

# Variables para los campos de texto
fecha_ticket_var = StringVar()
folio_ticket_var = StringVar()
clave_empleado_var = StringVar()
razon_social_var = StringVar()

# Campos de entrada del encabezado
Label(frame_superior, text="                              Captura de ticket", font=("Book Antiqua", 12, "bold"), bg="lemonchiffon1").grid(row=1, column=2, sticky="w")
Label(frame_superior, text="Fecha ticket:", font=("Book Antiqua", 12), bg="lemonchiffon1").grid(row=2, column=3, sticky="e")
fecha_ticket_entry = Entry(frame_superior, width=20, textvariable=fecha_ticket_var,state="disabled")
fecha_ticket_entry.grid(row=2, column=4, padx=10, pady=5, sticky="w")

# Llamamos a la función para rellenar la fecha actual
set_current_date()

Label(frame_superior, text="Folio:", font=("Book Antiqua", 12), bg="lemonchiffon1").grid(row=3, column=1, sticky="e")
folio_ticket_entry = Entry(frame_superior, width=30, textvariable=folio_ticket_var)
folio_ticket_entry.grid(row=3, column=2, columnspan=2, padx=10, pady=5, sticky="w")
folio_ticket_entry.bind("<Return>", lambda event: focus_next(event, clave_empleado_entry))  # Moverse al siguiente campo

# Colocar el enfoque en el campo Folio al iniciar
folio_ticket_entry.focus_set()

Label(frame_superior, text="Clave empleado:", font=("Book Antiqua", 12), bg="lemonchiffon1").grid(row=4, column=1, sticky="e")
clave_empleado_entry = Entry(frame_superior, width=30, textvariable=clave_empleado_var)
clave_empleado_entry.grid(row=4, column=2, columnspan=2, padx=10, pady=5, sticky="w")
clave_empleado_entry.bind("<Return>", lambda event: focus_next(event, razon_social_entry))  # Moverse al siguiente campo

Label(frame_superior, text="Razón social", font=("Book Antiqua", 12), bg="lemonchiffon1").grid(row=5, column=1, sticky="e")
razon_social_entry = Entry(frame_superior, width=50, textvariable=razon_social_var)
razon_social_entry.grid(row=5, column=2, columnspan=2, padx=10, pady=5, sticky="w")

# Crear el Label para mostrar el mensaje "Doble enter para guardar"
mensaje_label = Label(frame_superior, text="Doble enter para guardar", font=("Book Antiqua", 12), fg="red", bg="lemonchiffon1")
# Inicialmente no mostramos el mensaje
mensaje_label.grid_forget()

# Aquí asignamos el evento para el doble Enter en el campo de "Razón social"
razon_social_entry.bind("<Return>", on_double_enter)

# Division
linea_divisoria = Frame(raiz, bg="lemonchiffon2", height=2)
linea_divisoria.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

# Frame para la descripción de artículos
frame_inferior = Frame(raiz, bg="lemonchiffon1", pady=10)
frame_inferior.grid(row=2, column=0, sticky="nsew", padx=20)

# Etiqueta
Label(frame_inferior, text="Descripción de los artículos", font=("Book Antiqua", 12, "bold"), bg="lemonchiffon1").grid(row=0, column=0, columnspan=4, pady=(10, 15))

# Variables para los campos de los artículos
clave_producto_var = StringVar()
nombre_producto_var = StringVar()
cantidad_var = StringVar()

# Campos de entrada del cuerpo de la ticket
Label(frame_inferior, text="Clave de producto", font=("Book Antiqua", 12), bg="lemonchiffon1").grid(row=1, column=0, padx=10, pady=5, sticky="e")
clave_producto_entry = Entry(frame_inferior, width=20, textvariable=clave_producto_var)
clave_producto_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
clave_producto_entry.bind("<Return>", lambda event: focus_next(event, cantidad_entry))  # Moverse al siguiente campo

# Función para obtener el nombre del producto basado en la clave
def fetch_product_name(event):
    clave_producto = clave_producto_var.get()  # Obtén el valor de la clave del producto ingresada
    try:
        # Realiza una consulta en la base de datos para obtener el nombre del producto
        cursor.execute("SELECT nom FROM tg.cat_prod WHERE id_prod = %s", (clave_producto,))
        result = cursor.fetchone()
        
        # Si se encuentra el producto, actualiza el campo de nombre
        if result:
            nombre_producto_var.set(result[0])  # Asigna el nombre encontrado al campo de nombre
        else:
            nombre_producto_var.set("Producto no encontrado")  # Mensaje si no se encuentra la clave
    except Exception as e:
        print(f"Error al buscar el nombre del producto: {e}")

# Asigna el evento de 'Return' para activar la búsqueda del nombre del producto
clave_producto_entry.bind("<Return>", fetch_product_name, lambda event: focus_next(event, cantidad_entry) )

Label(frame_inferior, text="Nombre de producto", font=("Book Antiqua", 12), bg="lemonchiffon1").grid(row=1, column=2, padx=10, pady=5, sticky="e")
nombre_producto_entry = Entry(frame_inferior, width=20, textvariable=nombre_producto_var, state="disabled")
nombre_producto_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

Label(frame_inferior, text="Cantidad", font=("Book Antiqua", 12), bg="lemonchiffon1").grid(row=2, column=1, padx=10, pady=5, sticky="e")
cantidad_entry = Entry(frame_inferior, width=20, textvariable=cantidad_var)
cantidad_entry.grid(row=2, column=2, padx=10, pady=5, sticky="w")#
cantidad_entry.bind("<Return>", on_cantidad_enter)  # Guardar y mostrar mensaje

# Aquí asignamos el doble clic en "Cantidad" para limpiar los campos
cantidad_entry.bind("<Double-1>", on_double_click_cantidad)

# Crear el Label para las instrucciones
instrucciones_label = Label(frame_inferior, text="Articulo agreagado", font=("Book Antiqua", 12), fg="blue", bg="lemonchiffon1")
# Inicialmente no mostramos el mensaje
instrucciones_label.grid_forget()

# Botón para crear un nuevo folio (debajo de la sección de cantidad)
boton_nuevo_folio = Button(raiz, text="Nuevo Folio", font=("Book Antiqua", 14), bg="darkolivegreen3", fg="black", padx=20, pady=10, command=nuevo_folio)
boton_nuevo_folio.grid(row=3, column=0, pady=(20, 20), sticky=" ")

# Botón de regresar
boton_regresar = Button(raiz, text="Regresar al menú", font=("Book Antiqua", 14), bg="darkolivegreen3", fg="black", padx=20, pady=10)
boton_regresar.grid(row=4, column=0, pady=(20, 20), sticky=" ")

# Expandir las filas y columnas para que ocupen todo el espacio
raiz.grid_rowconfigure(0, weight=1)  # Primera fila (encabezado)
raiz.grid_rowconfigure(1, weight=0)  
raiz.grid_rowconfigure(2, weight=1)  # Fila de los artículos
raiz.grid_rowconfigure(3, weight=0)  

raiz.grid_columnconfigure(0, weight=1)  # Expandir la columna principal

frame_superior.grid_columnconfigure((0, 1, 2, 3), weight=1)  # Expandir las columnas dentro del frame superior
frame_inferior.grid_columnconfigure((0, 1, 2, 3), weight=1)  # Expandir las columnas dentro del frame inferior

lblt = Label(frame_superior,font=("Book Antiqua", 18), bg="darkolivegreen3",fg="black")
lblt.grid(row=0, column=5, columnspan=1, sticky="nsew")  # Colocada en la fila 0 y centrada
def actualizar_hora():
    lblt.config(text=time.strftime("%H:%M"))
    frame_superior.after(1000, actualizar_hora)
    
actualizar_hora()

# Ejecutar la ventana principal
raiz.mainloop()