# Lab_Progra3  
**Primer Laboratorio de Programación 3: Implementación FIFO, API y Base de Datos**

## Objetivo  
Desarrollar una aplicación que integre conceptos clave de programación, incluyendo:  
- Implementar y aplicar el TDA Cola (FIFO) en un contexto real.  
- Integrar estructuras de datos con persistencia en una base de datos.  
- Manejar relaciones muchos-a-muchos con priorización.  
- Desarrollar una API REST con operaciones CRUD básicas.

---

## Requisitos Técnicos  

### 1. Estructura de Datos Obligatoria (TDA Cola)  
Implementar una cola para gestionar el orden FIFO de misiones asignadas a cada personaje. La cola debe incluir, como mínimo, las siguientes operaciones:  
- **`enqueue(mission)`**: Añade una misión al final de la cola.  
- **`dequeue()`**: Elimina y retorna la primera misión de la cola.  
- **`first()`**: Devuelve la primera misión sin removerla.  
- **`is_empty()`**: Verifica si la cola está vacía.  
- **`size()`**: Retorna la cantidad de misiones en la cola.

### 2. Endpoints Requeridos (FastAPI)  
Desarrollar una API REST con los siguientes endpoints:  

| Método | Ruta                            | Descripción                              |  
|--------|---------------------------------|------------------------------------------|  
| POST   | `/personajes`                  | Crear un nuevo personaje.               |  
| POST   | `/misiones`                    | Crear una nueva misión.                 |  
| POST   | `/personajes/{id}/misiones/{id}` | Aceptar una misión (encolar).          |  
| POST   | `/personajes/{id}/completar`   | Completar una misión (desencolar + sumar XP). |  
| GET    | `/personajes/{id}/misiones`    | Listar las misiones en orden FIFO.      |  

---

## Notas Adicionales  
- La implementación debe reflejar un contexto realista donde los personajes gestionan misiones en orden de llegada (FIFO).  
- Asegúrate de que la base de datos soporte las relaciones muchos-a-muchos entre personajes y misiones, priorizando el orden de las misiones asignadas.  