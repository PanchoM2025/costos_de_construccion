# Pestaña «5. Ejecución»

Sirve para seguir la obra a medida que se construye. La obra se divide en **etapas** (Etapa 01, 02…), y cada una registra lo ejecutado y a qué precio. Al final se compara todo lo ejecutado contra el presupuesto contratado, que en la pestaña se llama **Original**.

> No confundir con las **etapas del presupuesto** (`obra000.json`, `obra001.json`…), que se crean con «Guardar obra» → «↑ Nueva etapa». Las etapas se crean solo desde esta pestaña, con **«+ Nueva Etapa»**.

Está en la ventana de la obra, después de «4. Presupuesto».

---

## 1. Conceptos

| Concepto | Qué es |
|---|---|
| **Original** | La versión del presupuesto que se contrató (un `obraNNN.json`). Queda **congelada**: guarda las tareas, las cantidades y el precio unitario (PU) de cada tarea, calculado con los precios de esa versión. Los cambios posteriores al presupuesto no lo modifican. |
| **Estado de una tarea** | Hay tres estados: **A realizar** (blanco), **En curso** (amarillo) y **Realizada** (verde). |
| **Etapa XX** | Lo ejecutado en un período: qué tareas, en qué cantidad y a qué PU. Puede usar un archivo de precios distinto al del Original. |
| **Adicional** | Una tarea que no estaba en el Original. Lleva clave `A01`, `A02`… y se muestra en violeta. |

Una tarea puede repartirse en varias etapas: por ejemplo, 300 m² en la Etapa 01 y 330 m² en la Etapa 02. Pasa a **Realizada** cuando se marca «Finaliza» en alguna etapa.

---

## 2. Cómo se usa

### Paso 1 — Definir el Original
1. Antes, **guardá la obra** («Guardar obra»), porque se toma lo que está guardado en el archivo.
2. Hacé clic en **«Definir Original…»** y elegí la versión contratada (`obra000.json`, `obra001.json`…). La lista muestra la fecha y la nota de cada versión.
3. Todas las tareas quedan en **A realizar**. Si alguna tiene insumos sin precio, aparece un aviso.

> Redefinir el Original reinicia los estados de todas las tareas. Si ya hay etapas cargadas, pueden dejar de coincidir con las tareas nuevas. La app pide confirmación antes de hacerlo.

### Paso 2 — Marcar qué tareas arrancan
- Seleccioná una o varias tareas (con Ctrl o Shift + clic) y usá los botones **«Marcar selección como»**. También podés hacer clic derecho sobre las tareas.
- El filtro **«Ver»** muestra todas las tareas o solo las de un estado.

La tabla principal muestra, por cada tarea: la cantidad, el PU y el total del Original; lo **Ejecutado** (la cantidad sumada de todas las etapas); el **$ Ejecutado** (lo gastado: cantidad × precio de cada etapa, sumado); el **Saldo** y el **Estado**. Las filas de rubro muestran el $ ejecutado del rubro. Abajo aparece cuántas tareas hay en cada estado y los totales Original y Ejecutado.

### Paso 3 — Crear una Etapa
Hacé clic en **«+ Nueva Etapa»**. La etapa arranca así:
- Con las tareas que están **En curso**.
- Con la **cantidad propuesta = saldo** (cantidad original menos lo ejecutado en otras etapas).
- Con el PU calculado con los precios del Original, completados con los precios actuales de la obra (pestaña 3).

Dentro de la etapa podés:

| Acción | Cómo |
|---|---|
| Ponerle nombre y fecha | Campos de arriba |
| Usar otro archivo de precios | **«Cargar archivo de precios…»**: recalcula el PU de todas las tareas. Los insumos que no están en el archivo conservan el precio anterior. |
| Cambiar la cantidad | Doble clic en «Cantidad» |
| Fijar un PU a mano | Doble clic en «P. Unit.». Si lo dejás vacío, se vuelve a calcular con los precios. |
| Dar la tarea por terminada | Clic en la columna «Finaliza» (✔) |
| Agregar tareas del Original | **«+ Agregar tarea»** |
| Cargar una tarea no prevista | **«+ Adicional (no prevista)»**: ver la sección 3 |
| Sacar una tarea de la etapa | Seleccionala y usá **«Quitar tarea»** |
| Exportar la etapa a Excel | **«Exportar Excel»** (arriba a la derecha): exporta lo que está en pantalla, aunque no esté guardado, con las hojas de la etapa y de insumos. Después pregunta si querés abrir el archivo. |

Colores de las filas: **amarillo** = la tarea tiene insumos sin precio; **celeste** = PU puesto a mano.

La columna «Ejec. otras etapas» muestra cuánto de la tarea ya se ejecutó en las demás etapas.

#### Insumos de cada tarea
Cada tarea se despliega para ver sus insumos: con un clic en el rubro, el ítem o la descripción, o con la flecha ▸ de la izquierda. Por cada insumo aparece:

| Columna | En la fila del insumo |
|---|---|
| Ítem | Código del insumo |
| Cant. Orig. / Incid. | **Incidencia**: cantidad de insumo por unidad de tarea (ej. kg por m²) |
| Cantidad | **Cantidad total en la etapa** = incidencia × cantidad de la tarea |
| P. Unit. | Precio del insumo |
| Total | Cantidad total × precio |

Para cambiar un valor, hacé doble clic sobre él:
- **Incidencia** (por unidad de tarea), o **Cantidad** (el total de la etapa: la app calcula la incidencia dividiendo por la cantidad de la tarea).
- **Precio** del insumo. Si otras tareas de la etapa usan el mismo insumo, la app pregunta si el precio nuevo se aplica a todas o solo a esa.

El PU de la tarea se recalcula solo, como la suma de incidencia × precio de sus insumos. Los valores cambiados se ven en **azul** con un `*`, y la tarea muestra «[N insumo(s) modificado(s)]». Si la tarea tenía un PU puesto a mano, al tocar un insumo el PU vuelve a calcularse con los insumos.

Con **clic derecho** se restauran los valores originales, es decir, la incidencia del análisis y el precio del archivo. Se puede hacer con un solo insumo o, desde la fila de la tarea, con todos sus insumos (esto también saca los agregados).

**Agregar un insumo que no está en el análisis:** seleccioná la tarea, o uno de sus insumos, y usá **«+ Insumo a la tarea»**; también podés hacer clic derecho → «Agregar insumo a esta tarea…». Buscás el insumo en el catálogo de la obra por código o nombre, y cargás la **incidencia** por unidad de tarea **o** la **cantidad total** de la etapa. El precio se propone desde el archivo de precios y se puede cambiar. El insumo agregado aparece con **«+»** y la leyenda «(agregado en la etapa)».

**Quitar un insumo** (clic derecho):
- Si es un insumo agregado, se elimina.
- Si es un insumo del análisis, queda con incidencia 0. Se puede recuperar con «Restaurar».

Los cambios valen **solo para esa etapa**: no modifican el análisis de la tarea ni el archivo de precios. Si después cargás otro archivo de precios, se actualizan los precios de los insumos, salvo los que cambiaste a mano.

Al tocar **«Guardar Etapa XX»**:
- Las tareas con «Finaliza» pasan a **Realizada**.
- Las tareas que estaban en **A realizar** y aparecen en la etapa pasan a **En curso**.
- Se guardan solo los precios de los insumos que usa la etapa, para que la etapa no cambie aunque después se cambien los precios de la obra.

### Paso 4 — Gestionar las etapas
En la lista de abajo:
- **Abrir / Editar** (o doble clic): reabre la etapa. Si agregás tareas, toman los precios guardados en la etapa y, para el resto de los insumos, los del Original y la obra.
- **Exportar Excel**: genera una planilla de la etapa con las tareas, cantidades, PU y totales por rubro, y los adicionales en una sección aparte. La hoja **«Insumos»** detalla la composición de cada tarea (incidencia, cantidad, precio, total) y marca los valores modificados.
- **Eliminar**: borra la etapa. Las tareas que esa etapa daba por finalizadas vuelven a **En curso**, salvo que otra etapa también las finalice. Los adicionales que no aparecen en ninguna otra etapa desaparecen. No se puede deshacer.

### Paso 5 — Cierre / Comparación
El botón **«Cierre / Comparación»** suma todas las etapas y las compara con el Original:

- **Diferencia** = total ejecutado − total original
- **Efecto cantidad** = (cantidad ejecutada − cantidad original) × PU original
- **Efecto precio** = total ejecutado − cantidad ejecutada × PU original

En cada tarea, los dos efectos suman la diferencia.

El informe muestra lo siguiente:
- El total de cada etapa y cuánto corresponde a adicionales.
- Las tareas del Original, agrupadas por rubro, con la variación %. Se marcan en rojo las que costaron más y en verde las que costaron menos.
- Los adicionales aparte: como no estaban previstos, todo lo ejecutado en ellos es diferencia.
- El **TOTAL GENERAL** (Original + adicionales), con la diferencia separada por cantidades, por precios y por adicionales.

La opción **«Solo tareas con avance»** deja afuera las tareas «A realizar» sin nada ejecutado. Se activa sola mientras quedan tareas sin empezar, para que la comparación no muestre como «ahorro» lo que todavía no se hizo.

#### Incidencias reales → BaseParticular.db
Desde el cierre, el botón **«Incidencias reales → BaseParticular…»** lleva a la base de la obra lo que realmente se consumió en las tareas **Realizadas**:

- **Incidencia real** de cada insumo = consumo total en todas las etapas ÷ cantidad de tarea ejecutada. Es un promedio ponderado: si en una etapa se usó un 10 % más de oficial y en otra igual cantidad de tarea lo normal, la incidencia real queda un 5 % arriba.
- Las tareas que comparten código (ej. dos carpetas con `1250E`) se suman, porque en la base comparten la misma fila.
- La vista previa muestra, por cada código, la incidencia del análisis, la real, la diferencia % y la acción:
  - **actualizar**: cambia la cantidad.
  - **nuevo**: el insumo se agregó en alguna etapa.
  - **quitar**: el insumo quedó con incidencia 0 en todas las etapas.
  - **sin cambio**.
- Con un clic en ✔ incluís o excluís cada código.
- Al aplicar, primero se guarda un backup `BaseParticular_antes_cierre_<fecha>.db` en la carpeta `data` de la obra, y después se escriben los cambios. Desde ese momento el presupuesto de la obra usa las incidencias nuevas. El **Original** de esta pestaña no cambia, porque está congelado.
- Solo se modifica la base **de la obra**. Si querés llevar alguna incidencia a la base general, hay que hacerlo aparte.

**«Exportar Excel»** genera dos hojas:
- **Resumen**: las etapas y los totales.
- **Comparacion**: el detalle por tarea, con la cantidad de cada etapa en su propia columna.

---

## 3. Adicionales (tareas no previstas)

Desde una etapa, con **«+ Adicional (no prevista)»**, hay dos formas de cargarlos:

1. **Del catálogo de la obra:** buscás la tarea por código o nombre. El PU se calcula con los precios de la etapa, aunque también se puede poner a mano.
2. **Sin tarea del catálogo** (precio a mano): escribís la descripción y la unidad. El PU a mano es obligatorio.

En los dos casos elegís el rubro: uno de los rubros del Original o **«AD – Adicionales varios»**.

Un adicional queda registrado al guardar la primera etapa que lo usa. Después puede seguir en etapas siguientes («+ Agregar tarea») y tener estado como cualquier otra tarea.

---

## 4. Archivos

Todo se guarda en `Obras/ObraNNN/data/`:

| Archivo | Contenido |
|---|---|
| `ejecucion.json` | El Original congelado (tareas, cantidades, PU, precios), el estado de cada tarea y el registro de adicionales |
| `etapa01.json`, `etapa02.json`… | Una por etapa: nombre, fecha, archivo de precios, precios usados, tareas con cantidad, PU, si finaliza y sus insumos (incidencia y precio, con marca de los modificados), y el total |

El código está en `Scripts/core/etapas.py` (la lógica y los Excel) y en `Scripts/ui/tab_ejecucion.py` (la pantalla).

---

## 5. Al ingresar números

- Coma decimal: `1,5` = 1,5; `1.234,56` = 1234,56.
- Un punto seguido de 3 dígitos se toma como separador de miles: `850.000` = 850000 y `1.250` = 1250.
- Si la parte entera es 0, el punto es decimal: `0.125` = 0,125.
- Para cantidades con decimales conviene usar siempre la coma: `1,25`.
