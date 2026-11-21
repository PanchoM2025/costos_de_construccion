# Pestaña «5. Ejecución»

Sirve para seguir la obra a medida que se construye. La obra se divide en **etapas**, y cada etapa se registra como una **Versión XX** con lo ejecutado y a qué precio. Al final se compara todo lo ejecutado contra el presupuesto contratado, que en la pestaña se llama **Original**.

Está en la ventana de la obra, después de «4. Presupuesto».

---

## 1. Conceptos

| Concepto | Qué es |
|---|---|
| **Original** | La versión del presupuesto que se contrató (un `obraNNN.json`). Queda **congelada**: guarda las tareas, las cantidades y el precio unitario (PU) de cada tarea, calculado con los precios de esa versión. Los cambios posteriores al presupuesto no lo modifican. |
| **Estado de una tarea** | Hay tres estados: **A realizar** (blanco), **En curso** (amarillo) y **Realizada** (verde). |
| **Versión XX (etapa)** | Lo ejecutado en un período: qué tareas, en qué cantidad y a qué PU. Puede usar un archivo de precios distinto al del Original. |
| **Adicional** | Una tarea que no estaba en el Original. Lleva clave `A01`, `A02`… y se muestra en violeta. |

Una tarea puede repartirse en varias versiones: por ejemplo, 300 m² en la V01 y 330 m² en la V02. Pasa a **Realizada** cuando se marca «Finaliza» en alguna versión.

---

## 2. Cómo se usa

### Paso 1 — Definir el Original
1. Antes, **guardá la obra** («Guardar obra»), porque se toma lo que está guardado en el archivo.
2. Hacé clic en **«Definir Original…»** y elegí la versión contratada (`obra000.json`, `obra001.json`…). La lista muestra la fecha y la nota de cada versión.
3. Todas las tareas quedan en **A realizar**. Si alguna tiene insumos sin precio, aparece un aviso.

> Redefinir el Original reinicia los estados de todas las tareas. Si ya hay versiones cargadas, pueden dejar de coincidir con las tareas nuevas. La app pide confirmación antes de hacerlo.

### Paso 2 — Marcar qué tareas arrancan
- Seleccioná una o varias tareas (con Ctrl o Shift + clic) y usá los botones **«Marcar selección como»**. También podés hacer clic derecho sobre las tareas.
- El filtro **«Ver»** muestra todas las tareas o solo las de un estado.

La tabla principal muestra, por cada tarea: la cantidad, el PU y el total del Original; lo **Ejecutado** (la suma de todas las versiones); el **Saldo** y el **Estado**. Abajo aparece cuántas tareas hay en cada estado y los totales Original y Ejecutado.

### Paso 3 — Crear una Versión (etapa)
Hacé clic en **«+ Nueva Versión»**. La versión arranca así:
- Con las tareas que están **En curso**.
- Con la **cantidad propuesta = saldo** (cantidad original menos lo ejecutado en otras versiones).
- Con el PU calculado con los precios del Original, completados con los precios actuales de la obra (pestaña 3).

Dentro de la versión podés:

| Acción | Cómo |
|---|---|
| Ponerle nombre y fecha | Campos de arriba |
| Usar otro archivo de precios | **«Cargar archivo de precios…»**: recalcula el PU de todas las tareas. Los insumos que no están en el archivo conservan el precio anterior. |
| Cambiar la cantidad | Doble clic en «Cantidad» |
| Fijar un PU a mano | Doble clic en «P. Unit.». Si lo dejás vacío, se vuelve a calcular con los precios. |
| Dar la tarea por terminada | Clic en la columna «Finaliza» (✔) |
| Agregar tareas del Original | **«+ Agregar tarea»** |
| Cargar una tarea no prevista | **«+ Adicional (no prevista)»**: ver la sección 3 |
| Sacar una tarea de la versión | Seleccionala y usá **«Quitar tarea»** |

Colores de las filas: **amarillo** = la tarea tiene insumos sin precio; **celeste** = PU puesto a mano.

La columna «Ejec. otras V.» muestra cuánto de la tarea ya se ejecutó en las demás versiones.

Al tocar **«Guardar Versión XX»**:
- Las tareas con «Finaliza» pasan a **Realizada**.
- Las tareas que estaban en **A realizar** y aparecen en la versión pasan a **En curso**.
- Se guardan solo los precios de los insumos que usa la versión, para que la versión no cambie aunque después se cambien los precios de la obra.

### Paso 4 — Gestionar las versiones
En la lista de abajo:
- **Abrir / Editar** (o doble clic): reabre la versión. Si agregás tareas, toman los precios guardados en la versión y, para el resto de los insumos, los del Original y la obra.
- **Exportar Excel**: genera una planilla de la versión con las tareas, cantidades, PU y totales por rubro, y los adicionales en una sección aparte.
- **Eliminar**: borra la versión. Las tareas que esa versión daba por finalizadas vuelven a **En curso**, salvo que otra versión también las finalice. Los adicionales que no aparecen en ninguna otra versión desaparecen. No se puede deshacer.

### Paso 5 — Cierre / Comparación
El botón **«Cierre / Comparación»** suma todas las versiones y las compara con el Original:

- **Diferencia** = total ejecutado − total original
- **Efecto cantidad** = (cantidad ejecutada − cantidad original) × PU original
- **Efecto precio** = total ejecutado − cantidad ejecutada × PU original

En cada tarea, los dos efectos suman la diferencia.

El informe muestra lo siguiente:
- El total de cada versión y cuánto corresponde a adicionales.
- Las tareas del Original, agrupadas por rubro, con la variación %. Se marcan en rojo las que costaron más y en verde las que costaron menos.
- Los adicionales aparte: como no estaban previstos, todo lo ejecutado en ellos es diferencia.
- El **TOTAL GENERAL** (Original + adicionales), con la diferencia separada por cantidades, por precios y por adicionales.

La opción **«Solo tareas con avance»** deja afuera las tareas «A realizar» sin nada ejecutado. Se activa sola mientras quedan tareas sin empezar, para que la comparación no muestre como «ahorro» lo que todavía no se hizo.

**«Exportar Excel»** genera dos hojas:
- **Resumen**: las versiones y los totales.
- **Comparacion**: el detalle por tarea, con la cantidad de cada versión en su propia columna.

---

## 3. Adicionales (tareas no previstas)

Desde una versión, con **«+ Adicional (no prevista)»**, hay dos formas de cargarlos:

1. **Del catálogo de la obra:** buscás la tarea por código o nombre. El PU se calcula con los precios de la versión, aunque también se puede poner a mano.
2. **Sin tarea del catálogo** (precio a mano): escribís la descripción y la unidad. El PU a mano es obligatorio.

En los dos casos elegís el rubro: uno de los rubros del Original o **«AD – Adicionales varios»**.

Un adicional queda registrado al guardar la primera versión que lo usa. Después puede seguir en versiones siguientes («+ Agregar tarea») y tener estado como cualquier otra tarea.

---

## 4. Archivos

Todo se guarda en `Obras/ObraNNN/data/`:

| Archivo | Contenido |
|---|---|
| `ejecucion.json` | El Original congelado (tareas, cantidades, PU, precios), el estado de cada tarea y el registro de adicionales |
| `etapa01.json`, `etapa02.json`… | Una por versión: nombre, fecha, archivo de precios, precios usados, tareas con cantidad, PU y si finaliza, y el total |

El código está en `Scripts/core/etapas.py` (la lógica y los Excel) y en `Scripts/ui/tab_ejecucion.py` (la pantalla).

---

## 5. Al ingresar números

- Coma decimal: `1,5` = 1,5; `1.234,56` = 1234,56.
- Un punto seguido de 3 dígitos se toma como separador de miles: `850.000` = 850000 y `1.250` = 1250.
- Si la parte entera es 0, el punto es decimal: `0.125` = 0,125.
- Para cantidades con decimales conviene usar siempre la coma: `1,25`.
