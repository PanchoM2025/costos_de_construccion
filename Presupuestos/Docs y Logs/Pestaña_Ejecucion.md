# Pestaña «5. Ejecución»

Sirve para seguir la obra por **etapas** (Etapa 01, 02…, por ejemplo una por quincena) y, al final, comparar lo ejecutado con el presupuesto contratado (**Original**).

> No confundir con las **versiones del presupuesto** (`obra000.json`, `obra001.json`…), que se crean con «Guardar obra» → «↑ Nueva versión». Las etapas se crean solo desde esta pestaña, con **«+ Nueva Etapa»**.

## Conceptos

- **Original**: la versión contratada del presupuesto, **congelada** con sus cantidades y PU. Los cambios posteriores al presupuesto no la modifican.
- **Estados de una tarea**: **A realizar** (blanco), **En curso** (amarillo) y **Realizada** (verde).
- **Etapa**: lo ejecutado en un período (tareas, cantidades y PU). Una tarea puede repartirse en varias etapas y pasa a Realizada cuando se marca **«Finaliza»**.
- **Adicional**: una tarea no prevista en el Original (`A01`, `A02`…), en violeta.

## Uso

1. **Definir el Original**: primero «Guardar obra»; después **«Definir Original…»** y elegís la versión contratada. Redefinirlo reinicia los estados.
   - **«Actualizar precios del Original…»**: pasa al Original los precios actuales de la obra (pestaña 3) **sin tocar estados ni etapas**. Muestra qué insumos cambian y permite completar solo los que no tenían precio (No) o actualizar todos (Sí). Recalcula el PU de las tareas (las de precio manual quedan igual) y deja copia previa `ejecucion_antes_precios_<fecha>.json`.
2. **Marcar tareas**: seleccionás tareas y usás **«Marcar selección como»** (o clic derecho). La tabla muestra, para cada tarea, el Original, lo **Ejecutado** (cantidad), el **$ Ejecutado** (lo gastado, sumado entre etapas), el **Saldo** y el **Estado**.
   - Cada tarea **se despliega** (clic en la descripción o en ▸) y muestra **por insumo** lo previsto en el Original, lo ejecutado en las etapas y el **saldo**. En amarillo, lo que falta; en rojo, lo que se usó de más o no estaba previsto. Si a una tarea con avance le faltan insumos, muestra «[faltan N insumo(s)]».
   - El filtro **«Pendientes (lo que falta)»** muestra solo las tareas no Realizadas con algo por hacer, sin desplegar; al desplegar una tarea se ven solo los insumos que faltan.
   - **Precios:** «PU Orig.» y «Total Orig.» son los del Original (lo contratado); «PU actual» y «Total actual» usan los precios actuales de la obra (pestaña 3). En los insumos, un « *» marca los que cambiaron de precio. Al pie, **«Falta»** es el valor de los insumos que faltan a precio actual.
   - En todos los filtros, la última fila **TOTAL** suma el Total Orig., el Total actual y el $ Ejecutado de lo listado (incluidos los adicionales visibles). Los rubros muestran esos mismos montos.
   - El Original guarda su lista de insumos al definirse. En los Originales definidos antes, se toma de la base de la obra.
3. **«+ Nueva Etapa»**: trae las tareas **En curso** con la cantidad propuesta igual al saldo.
   - Si la cantidad de una tarea ya está completa pero **le faltan insumos** (por ejemplo, se proveyó la madera y falta la mano de obra), la tarea viene como fila **«solo insumos pendientes»**: trae solo los insumos que faltan y **no suma m²** a la tarea. Sí suma pesos y consumo de insumos. Su cantidad aparece como «ref.». Con clic derecho sobre la tarea se puede hacer que sume cantidad, o que no sume.

   En la etapa podés:
   - poner **nombre y fecha**;
   - **cargar otro archivo de precios**, que respeta los precios cambiados a mano;
   - editar **Cantidad** o **P. Unit.** con doble clic (el PU vacío se calcula con los insumos);
   - marcar **Finaliza**;
   - **agregar o quitar tareas** y **adicionales**;
   - usar **«Exportar Excel»**, que exporta lo que está en pantalla.
4. **Insumos de cada tarea**: con un clic en la descripción (o en ▸) se despliegan.
   - Con doble clic editás la **Incid.** (por unidad de tarea), la **Cantidad** (total de la etapa) o el **P. Unit.**. Si otras tareas usan el mismo insumo, la app pregunta si el precio se aplica a todas.
   - Con **«+ Insumo a la tarea»** agregás un insumo del catálogo.
   - Con clic derecho: **agregar**, **quitar** (un insumo del análisis queda con incidencia 0) o **restaurar**.
   - Lo modificado se ve en **azul** con `*`, y el PU de la tarea se recalcula solo.
5. **«Guardar Etapa XX»**: las tareas con Finaliza pasan a **Realizada**, y las que estaban en A realizar pasan a **En curso**.
6. **Lista de etapas**: **Abrir / Editar**, **Exportar Excel** (hojas de la etapa e «Insumos», solo con los insumos usados: los quitados no aparecen) y **Eliminar**. Al eliminar, las tareas que esa etapa finalizaba vuelven a En curso, salvo que otra etapa también las finalice.

## Variantes de una etapa

Sirven para comparar alternativas de una etapa ya guardada. **No suman al ejecutado** ni cambian estados, saldos, el Original o la base.

1. **Abrir / Editar** la etapa y hacer clic derecho sobre una tarea: **«Cambiar a S / E / T»** en hormigón (tareas con variante E) y **«Cambiar a S»** en las demás. También se puede volver a **Propio**.
2. Se cargan los insumos del análisis de esa variante. Los precios cambiados a mano se conservan en los insumos que siguen. Si un insumo no tiene precio (frecuente en T), se carga con doble clic.
3. **«Guardar como nueva Variante»** crea `etapaNN_varianteMM.json`, que aparece en la lista como **Etapa NN Variante MM**, con su total. Se puede abrir, exportar y eliminar.

Si hay tareas cambiadas, la etapa real no se puede guardar: solo como variante. Para eliminar una etapa, primero hay que eliminar sus variantes.

## Cierre / Comparación

Suma todas las etapas y las compara con el Original, por tarea, por rubro y en total:

- **Diferencia** = total ejecutado − total original
- **Por cantidad** = (cant. ejecutada − cant. original) × PU original
- **Por precio** = total ejecutado − cant. ejecutada × PU original
- **Adicionales**: todo lo ejecutado en ellos es diferencia.

La opción «Solo tareas con avance» deja afuera lo que todavía no empezó. **Exportar Excel** genera la hoja «Resumen» y la hoja «Comparacion», con una columna por etapa.

**«Incidencias reales → BaseParticular…»**: para las tareas **Realizadas**, la incidencia real = consumo de todas las etapas ÷ cantidad ejecutada (promedio ponderado). Las tareas que comparten código se suman. Muestra una vista previa con la acción para cada insumo (actualizar / nuevo / quitar), y al aplicar hace un backup `BaseParticular_antes_cierre_<fecha>.db` y escribe en la base **de la obra**. El Original no cambia.

## Dónde se guarda cada cosa

Todo se guarda en `Obras/ObraNNN/data/`:

| Archivo | Contenido |
|---|---|
| `ejecucion.json` | El Original congelado (tareas, cantidades, PU, precios), los estados y los adicionales |
| `etapa01.json`, `etapa02.json`… | Una por etapa: nombre, fecha, archivo de precios, tareas con cantidad y PU, sus insumos y el total |

**Los precios cambiados en una etapa no se escriben en el archivo de precios.** El Excel de precios solo se lee, y su nombre queda anotado como referencia. Los cambios quedan solo en el `etapaXX.json`:

| Qué se modifica | Qué guarda |
|---|---|
| PU de la tarea a mano | `pu_manual` y `pu` |
| Precio de un insumo | `precio` (el tuyo), `precio_base` (el del archivo) y `mod_precio: true` |
| Incidencia de un insumo | `incid`, `incid_base` y `mod_incid: true` |
| Insumo agregado | `agregado: true` |

Además, cada etapa guarda en `precios` una copia de los precios **del archivo** que usa, para que no cambie si después se modifica el Excel.

No se tocan la pestaña 3 «Insumos y precios», el presupuesto, el Original, la base general ni la `BaseParticular.db`. La única excepción es «Incidencias reales → BaseParticular» cuando lo aplicás, que escribe **incidencias** (no precios), con backup.

Código: `Scripts/core/etapas.py` (lógica y Excel) y `Scripts/ui/tab_ejecucion.py` (pantalla).

## Números

Se usa coma decimal (`1,5`; `1.234,56`). Un punto seguido de 3 dígitos se toma como miles (`850.000` = 850000), salvo `0.125`, que es 0,125. Para decimales conviene usar siempre la coma.
