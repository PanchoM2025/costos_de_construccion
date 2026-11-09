# Registro de correcciones — Master_FINAL.db

Revisión de incidencias rubro por rubro (iniciada 2026-11-06).
Copia previa a la migración a Id: `Costos/Data/Master_FINAL_antes_IDs_2026-11-06.db`.

Modalidades: sin letra = personal propio · S = subcontrato MdeO, materiales del comitente · E = hormigón elaborado · X = H° elaborado + subcontrato MdeO, madera/clavos/alambre del comitente · T = subcontrato total.

## Rubro 1 — Trabajos preparatorios (2026-11-06)

| Tarea | Antes | Después |
|---|---|---|
| 0140 Replanteo | Oficial 3,8 h/m2 | Oficial 0,38 h/m2 (Ayudante 0,33 sin cambio) |
| Cerco perimetral olímpico | código 0160S; insumo 0500 en gl | código **0160T**; insumo 0500 en ml |
| Demolición mamposterías | código 0211S; insumo 000211 en gl | código **0211T**; insumo 000211 en m2 |
| Demolición entrepisos | código 0212S; insumo 000212 en m3 | código **0212T**; insumo 000212 en m2 |
| 0311 Supervisión oficina central | tarea en gl | tarea en mes |
| 0312 Dirección de obras | tarea en gl | tarea en mes |
| 0121 Casilla obrador | tablas cepilladas (1322) 3,5 m2 | tablas sin cepillar (1311) 3,5 m2 — la casilla oficina mantiene cepilladas |

Los Id (Base36) de las tareas renombradas no cambian: 0005, KA00, KA01.

## Rubro 2 — Movimiento de suelos (desde 2026-11-07)

| Tarea | Antes | Después |
|---|---|---|
| 0110 Limpieza superficial | Oficial 0,1 h/m2 + Ayudante 0,1 h/m2 | Ayudante 0,2 h/m2 (sin Oficial). 0110S sin cambio |
| 0220 Desmontes | Ayudante 3,5 h/m3 | sin cambio |
| Desmonte a máquina | código 0230S (chocaba con 0230 Terraplenamientos), tarea en m2, subcontrato en m3 | código **0220T**, variante de 0220 Desmontes, tarea en m3. Id 0K04 sin cambio |
| 0251 / 0251S Excavación de bases | Ayudante 5,8 h/m3 | sin cambio |
| 0252 / 0252S Excavación vigas de encadenado | Ayudante 2,5 h/m3 | sin cambio (se evaluó igualar a zanjas 3,4; se mantiene) |
| 0253 Excavación pozos romanos | Ayudante 5,8 h/m3 (igual que bases) | Ayudante 7 h/m3 |
| Excavación pilotines | código 0254S | código **0254T** (subcontrato con perforadora incluida). Id 0U05 sin cambio |
| 0255 / 0255S Excavación cámaras | Ayudante 4,4 h/m3 | sin cambio |
| 0256 / 0256S Excavación zanjas | Ayudante 3,4 h/m3 | sin cambio |
| 0257 Excavación sótanos | Ayudante 3,12 h/m3 | Ayudante 7,5 h/m3 (valor anterior al 20/10) |
| Excavación sótanos subcontratada | código 0257S | código **0257T** (subcontrato con máquina). Id 0U0B sin cambio |
| 0230 Terraplenamientos | Ayudante 2,5 h/m3, sin material | Ayudante 2,5 h/m3 + **Tosca 1,30 m3/m3** (esponjamiento) |
| 0240S Relleno, nivelación y compactación | tarea en m2, subcontrato en m3, sin material | tarea en **m3** + **Tosca 1,30 m3/m3** (material del comitente) |
| **0240T** Relleno, nivelación y compactación (NUEVA) | no existía | Id KK02, m3, variante T de 0240S: 1 m3 de "Mat. y MdeO. para Relleno, Nivelación y Compactación." (0T0240) |
| Subrubro 2.a | "Rellenos" (repetido con 2.b) | **"Limpieza y desmontes"**. 2.b sigue "Rellenos" |

Rubro 2 terminado. La base de tosca bajo plateas/pisos se cotiza con 0230 / 0240S / 0240T en m3 (sin tarea aparte).

**Insumos nuevos (2026-11-07)** — falta cargarles precio en la planilla PUnitarios:
- 1640 Tosca, m3, Id 1RUM.
- 0T0240 Mat. y MdeO. para Relleno, Nivelación y Compactación., m3, Id 0AZU.

## Rubro 3 — Estructuras resistentes (desde 2026-11-07)

| Tarea | Antes | Después |
|---|---|---|
| 1171 Pocetes con H° ciclópeo | Arena 0,8 m3 + Piedra 0,8 m3 por m3 | Arena **0,55** m3 + Piedra **0,90** m3 (incluye piedra bola). 1171T sin cambio |
| 1172 / 1172S H° de limpieza bajo bases | Arena 0,8 + Piedra 0,8 m3 por m3 | Arena **0,70** + Piedra **0,70** m3 (H° pobre: arena y piedra similares; se probó 0,50/0,85 y se corrigió). 1172T sin cambio |
| 1173 / 1173S H° de limpieza bajo vigas encadenado | Arena 0,8 + Piedra 0,8 m3 por m3 | Arena **0,70** + Piedra **0,70** m3. 1173T sin cambio |
| 1173 H° de limpieza bajo vigas encadenado | Oficial 4 h + Ayudante 15 h por m3 | Oficial **1,5** h + Ayudante **11** h |
| 1174 / 1174S Relleno de cimientos | Arena 0,8 + Piedra 0,8 m3 por m3 | Arena **0,70** + Piedra **0,70** m3. 1174T sin cambio |
| 1174 Relleno de cimientos | Oficial 4,7 h + Ayudante 4,5 h por m3 | Oficial **1,5** h + Ayudante **8** h |
| 1111 / 1111S / 1111E Bases centradas | Hierro 90 / 60 / 45 kg/m3; alambre solo en 1111 (0,45) | Hierro **60 kg/m3** en las tres; alambre **0,3 kg/m3** en las tres. 1111T sin cambio |
| 1112S / 1112E Bases medianeras | sin alambre | alambre **0,38 kg/m3** (igual que 1112). Hierro 75 kg/m3 en todas, sin cambio |
| 1113 / 1113E / 1113S Bases esquineras | Hierro 45 / 45 / 80 kg/m3; alambre solo en 1113 | Hierro **80 kg/m3** y alambre **0,40 kg/m3** en las tres. 1113T sin cambio |
| 1120 / 1120E / 1120S Tensores | Hierro 1 / 116 / 60 kg/m3; alambre solo en 1120 (0,4) | Hierro **100 kg/m3** y alambre **0,50 kg/m3** en las tres. 1120T sin cambio |
| 1120 Tensores | Oficial 1 h + Ayudante 9,9 h por m3 | Oficial **4 h** (Ayudante 9,9 sin cambio) |
| 1132 / E / S / X Viga portamuros | Hierro 178 / 178 / 180 / 1 kg/m3; alambre 0,45 / falta / 0,9 / 0,8 | Hierro **180 kg/m3** y alambre **0,90 kg/m3** en las cuatro. 1132T sin cambio |
| 1132E / 1132S Viga portamuros | sin encofrado | agregado clavos **1,5 kg**, tablas **3 m2**, tirante 3x3 **1,4 ml** (igual que 1132 y 1132X) |
| 1132 Viga portamuros | Oficial 1 h + Ayudante 15 h por m3 | Oficial **8 h** (Ayudante 15 sin cambio) |
| 1150S Pilotes y/o pilotines | sin alambre | alambre **0,30 kg/m3** (igual que 1150) |
| **1150E** Pilotes y/o pilotines (NUEVA) | no existía | Id 1M10: Subcontrato tipo E (102150) 1 m3 + hierro 55 kg + alambre 0,30 kg + H° elaborado 1,05 m3 |
| **1150X** Pilotes y/o pilotines (NUEVA) | no existía | Id 1M11: Subcontrato tipo X (103150) 1 m3 + hierro 55 kg + alambre 0,30 kg + H° elaborado 1,05 m3 (sin encofrado) |
| 1162T Platea 0,15 m | insumo 104162 (subcontrato T) en m3, tarea en m2 | insumo 104162 en **m2** |
| 1162E / 1162S Platea 0,15 m | sin alambre | alambre **0,02 kg/m2** (igual que 1162) |
| 1162 Platea 0,15 m | Oficial 1,34 h + Ayudante 1,0 h por m2 | Oficial **1,1 h** + Ayudante **1,8 h** |
| **1162X** Platea 0,15 m (NUEVA) | no existía | Subcontrato tipo X (103162) 1 m2 + malla 3,3 kg + alambre 0,02 kg + H° elaborado 0,16 m3 |
| 1163T Platea 0,20 m | insumo 104163 (subcontrato T) en m3, tarea en m2 | insumo 104163 en **m2** |
| 1163 / 1163E / 1163S Platea 0,20 m | malla Q188 3,3 kg (simple); alambre 0,04 solo en 1163 | **armadura doble** (desde 0,20 m de espesor): malla **6,6 kg/m2** y alambre **0,04 kg/m2** en todas |
| 1163 / 1163S Platea 0,20 m | cemento 75 / 66 kg/m2 | cemento **75 kg/m2** en las dos |
| 1163 Platea 0,20 m | Oficial 1,0 h + Ayudante 2,2 h | Oficial **1,5 h** + Ayudante **2,5 h** (por la doble malla) |
| **1163X** Platea 0,20 m (NUEVA) | no existía | Subcontrato tipo X (103163) 1 m2 + malla 6,6 kg + alambre 0,04 kg + H° elaborado 0,21 m3 |
| 1210E / 1210S Tronco de columnas | sin encofrado ni alambre | agregado alambre **0,80 kg**, clavos **2 kg**, tablas **2,5 m2**, tirante 3x3 **0,4 ml** (igual que 1210) |
| 1210E Tronco de columnas | H° elaborado 1811 p/Bases asent. 5 | H° elaborado **1821 p/Estructuras as. 15** (1,05 m3) |
| 1210S Tronco de columnas | piedra 0,70 m3 | piedra **0,65 m3** (igual que 1210) |
| **1210X** Tronco de columnas (NUEVA) | no existía | Subcontrato tipo X (103210) 1 m3 + hierro 100 kg + alambre 0,80 + clavos 2 + tablas 2,5 + tirante 0,4 + H° elaborado 1821 1,05 m3 |
| **1111X / 1112X / 1113X / 1120X** (NUEVAS) | no existían | Subcontrato tipo X (1031xx) 1 m3 + mismo hierro, alambre y H° elaborado que su variante E. Sin encofrado (las propias no llevan). Id 1M15–1M18 |
| 1221E / 1221S / 1221X Columnas normales | E y S sin encofrado ni alambre; X con alambre 0,77, clavos 2, tablas 7 m2 | igual que 1221 en todas: alambre **0,63 kg**, clavos **2,1 kg**, tablas **2,625 m2**, tirante **0,6 ml** |
| 1221 / 1221S Columnas normales | piedra 0,70 m3 | piedra **0,65 m3** |
| 1222E / 1222S Columnas a la vista | sin encofrado ni alambre | agregado alambre **0,77 kg**, clavos **2 kg**, tablas cepilladas **7 m2**, tirante **0,6 ml** (igual que 1222 y 1222X) |
| 1222 / 1222S Columnas a la vista | piedra 0,70 m3 | piedra **0,65 m3** |
| 1222 Columnas a la vista | Oficial 15 h + Ayudante 18 h | Oficial **19 h** + Ayudante **21 h** (más que columnas normales) |
| 1223X Columnas independientes | hierro 90 kg/m3 | hierro **120 kg/m3** (igual que 1223 y 1223S) |
| 1223S Columnas independientes | sin encofrado ni alambre | agregado alambre **0,80 kg**, clavos **2 kg**, tablas cepilladas **7 m2**, tirante **0,6 ml** |
| 1223 / 1223S Columnas independientes | piedra 0,70 m3 | piedra **0,65 m3** |
| **1223E** Columnas independientes (NUEVA) | no existía | Subcontrato tipo E (102223) 1 m3 + hierro 120 kg + alambre 0,80 + clavos 2 + tablas cepilladas 7 + tirante 0,6 + H° elaborado 1,05 m3 |
| 1231X Vigas normales | hierro 110 kg/m3 | hierro **135 kg/m3** (igual que el resto) |
| 1231E / 1231S Vigas normales | sin encofrado ni alambre | agregado alambre **0,90 kg**, clavos **1,5 kg**, tablas **5 m2**, tirante **11 ml** (igual que 1231) |
| 1231 / 1231S Vigas normales | piedra 0,70 m3 | piedra **0,65 m3** |
| 1232 / E / S / X Vigas a la vista | hierro 150 / 135 / 135 / 110 kg; alambre 0,85 (sin alambre en E y S) | hierro **135 kg** y alambre **0,90 kg** en las cuatro (igual que vigas normales) |
| 1232E / 1232S / 1232X Vigas a la vista | E y S sin encofrado; X con tirante 1,8 ml | clavos **1,5 kg**, tablas cepilladas **5 m2**, tirante **11 ml** en todas (igual que 1232) |
| 1232 Vigas a la vista | Oficial 32 h + Ayudante 20 h | Oficial **38 h** + Ayudante **22 h** (más que vigas normales) |
| 1233E Vigas a la vista independientes | horas propias (Oficial 32 + Ayudante 22), sin subcontrato | **Subcontrato tipo E (102233) 1 m3** en lugar de las horas; materiales sin cambio |
| 1233 Vigas a la vista independientes | Oficial 35 h + Ayudante 24 h | Oficial **42 h** + Ayudante **26 h** |
| **1233S** Vigas a la vista independientes (NUEVA) | no existía | Id 241H: Subcontrato tipo S (101233) 1 m3 + hierro 150 + alambre 0,85 + clavos 1,5 + tablas cepilladas 5 + tirante 11 + cemento 330 / arena 0,65 / piedra 0,65 |
| Orden 1233 / 1233E | al final del subrubro, separadas de 1233T/X | ubicadas después de 1232X, junto a sus variantes |

**Insumos nuevos (2026-11-08)** — falta cargarles precio en la planilla PUnitarios:
- 101233 Subcontrato tipo S, Vigas a la vista independientes, m3, Id 0HXU.
- 102233 Subcontrato tipo E, Vigas a la vista independientes, m3, Id 0TII.
| 1241X Losas macizas normales | H° elaborado 0,15 m3/m3 | H° elaborado **1,05 m3/m3** |
| 1241 / E / S / X Losas macizas normales | E y S sin encofrado ni alambre; X con alambre 0,6, clavos 1, tablas 4; tirante 2,5 ml | en las cuatro: alambre **0,63 kg**, clavos **1,05 kg**, tablas **3,15 m2**, tirante (puntales) **12 ml** |
| 1241 / 1241S Losas macizas normales | piedra 0,60 m3 | piedra **0,65 m3** |
| 1242E Losas macizas a la vista | tenía Subcontrato tipo S (101242) **y** tipo E | quitado el Subcontrato tipo S (quedaba cobrada dos veces la MdeO) |
| 1242X Losas macizas a la vista | H° elaborado 0,15 m3/m3 | H° elaborado **1,05 m3/m3** |
| 1242 / E / S / X Losas macizas a la vista | hierro 80, alambre 0,8, tirante 3 ml; E y S sin encofrado | en las cuatro: hierro **84 kg**, alambre **0,63 kg**, clavos **1 kg**, tablas cepilladas **4 m2**, puntales **12 ml** (igual que losa normal salvo madera cepillada) |
| 1242 / 1242S Losas macizas a la vista | arena 0,60 + piedra 0,60 | arena **0,65** + piedra **0,65** |
| 1242 Losas macizas a la vista | Oficial 19 h + Ayudante 18 h | Oficial **26 h** + Ayudante **24 h** |
| 1243E Losas macizas en balcones | hierro 80 kg; sin encofrado ni alambre | hierro **100 kg** (voladizo), alambre **0,75**, clavos **1,2**, tablas **4 m2**, puntales **12 ml** |
| **1243** Losas macizas en balcones (NUEVA, propia) | no existía | Id 241I: Oficial 28 h + Ayudante 26 h + mismos hierro/encofrado + cemento 330 / arena 0,65 / piedra 0,65. Pasa a ser la base de la 1243E |
| **1243S / 1243T / 1243X** (NUEVAS) | no existían | Id 241J / 241K / 241L. S: subcontrato S (insumo nuevo 101243) + materiales y mezcla; T: subcontrato T (104243); X: subcontrato X (103243) + materiales + H° elaborado 1,05 |

- Insumo nuevo 101243 Subcontrato tipo S, Losas macizas en balcones., m3, Id 0IWK — falta precio en PUnitarios.
| 1244S Losas cerámicas | mezcla de obra **y** H° elaborado 0,08 m3 (hormigón doble) | quitado el H° elaborado; queda la mezcla de obra |
| 1244T Losas cerámicas | insumo 104244 (subcontrato T) en m3, tarea en m2 | insumo 104244 en **m2** |
| 1244E / 1244S Losas cerámicas | sin alambre ni puntales | alambre **0,10 kg** + tirante (puntales) **1,4 ml** por m2 (igual que 1244) |
| 1244 / 1244S Losas cerámicas | cemento 22 kg + arena 0,03 + piedra 0,04 (≈0,06 m3) | cemento **25 kg** + arena **0,05** + piedra **0,05** (≈0,08 m3, igual que el elaborado) |
| 1245X Losas macizas Sistema Prenova esp. 0,22 | tarea (Id 2416) con 8 incidencias | **ELIMINADA** la tarea y sus incidencias (pedido del usuario). El insumo 1170 Discos Sistema Prenova queda sin uso |
| 1246 Losas premoldeadas SHAP | subcontratos 102246 / 103246 / 104246 en m3, tarea en m2 | los tres en **m2** |
| 1246 / 1246X Losas premoldeadas SHAP | malla 3,5 / 2,5 kg; grúa 0,03 h | malla **3,5 kg** y grúa **0,06 h/m2** en todas (dato del usuario) |
| 1246 Losas premoldeadas SHAP | H° elaborado 0,06 m3 (personal propio) | mezcla de obra: cemento **20 kg** + arena **0,04** + piedra **0,04** |
| **1246E / 1246S** (NUEVAS) | no existían | E (Id 2416, reutiliza el Id libre de la 1245X borrada): subcontrato E + loseta + malla + alambre + puntales + grúa + H° elaborado 0,06. S (Id 241M): subcontrato S (insumo nuevo 101246) + mismos materiales + mezcla de obra |

- Insumo nuevo 101246 Subcontrato tipo S, Losas premoldeadas SHAP 0,60, m2, Id 0JVA — falta precio en PUnitarios.
| 1247X Losas placa colaborante Steel Deck | subcontrato X (103247) en m3, tarea en m2 | subcontrato en **m2**. Se deja solo la variante X (no se generan las otras, decisión del usuario) |
| 1248 Malla s/losas premoldeadas SHAP | Oficial 0,05 + Ayudante 0,1 h, malla 3,5, alambre 0,06 | sin cambio. Las desglosadas (1248–1250) quedan solo propias, sin variantes (decisión del usuario) |
| 1249 Hormigón s/losetas SHAP | H° elaborado 0,06 m3 (personal propio) | mezcla de obra: cemento **20 kg** + arena **0,04** + piedra **0,04** (igual que 1246) |
| **1249X** Hormigón s/losetas SHAP (NUEVA) | no existía | Id 241N: Subcontrato tipo X de MdeO (insumo nuevo 103249) 1 m2 + H° elaborado 0,06 m3 |

- Insumo nuevo 103249 Subcontrato tipo X, Hormigon s/losetas premoldeadas SHAP 0,60, m2, Id 17SE — falta precio en PUnitarios.
| 1250 Colocación losas SHAP | grúa 0,12 h; sin puntales; Oficial 0,5 + Ayudante 0,7 h | grúa **0,06 h**, tirante (puntales) **0,6 ml**, Oficial **1,65 h** + Ayudante **1,2 h** → 1248 + 1249 + 1250 suman igual que la 1246 (1,8 + 1,9 h) |
| 1321E / 1321S Tanques prismáticos de bombeo | sin encofrado ni alambre | agregado alambre **0,60 kg**, clavos **1,7 kg**, tablas **3,3 m2**, tirante **0,26 ml** (igual que 1321) |
| 1321 / 1321S Tanques prismáticos de bombeo | arena 0,70 m3 | arena **0,65 m3**. Sin hidrófugo en la mezcla (decisión del usuario) |
| 1323E / 1323S Tanques prismáticos elevados | sin encofrado ni alambre | agregado alambre **0,60 kg**, clavos **1,7 kg**, tablas **3,3 m2** (igual que 1323) |
| 1323 / E / S / X Tanques prismáticos elevados | tirante 0,26 ml/m3 | puntales **12 ml/m3** en las cuatro (fondo en altura, igual que losas) |
| 1323 / 1323S Tanques prismáticos elevados | arena 0,70 m3 | arena **0,65 m3** |
| 1331 / E / S Escaleras macizas rectas | hierro 60 / 80 / 60 kg; alambre 0,45 solo en 1331; E y S sin encofrado; tirante 1,2 ml | hierro **80 kg**, alambre **0,60 kg**, clavos **1,5 kg**, tablas **3,8 m2**, puntales **12 ml** en todas |
| **1331X** Escaleras macizas rectas (NUEVA) | no existía | Subcontrato tipo X (103331) 1 m3 + mismos hierro/encofrado + H° elaborado 1,05 m3 |
| 1342 / 1342S Encadenados y/o dinteles | cemento 315 + arena 0,525 + piedra 0,735; sin clavos; S sin tablas | cemento **330** + arena **0,65** + piedra **0,65**; clavos **1,5 kg** y tablas **2,625 m2** en ambas |
| **1342E / 1342X** Encadenados y/o dinteles (NUEVAS) | no existían | subcontrato E (102342) / X (103342) 1 m3 + hierro 52,5 + alambre 0,42 + clavos 1,5 + tablas 2,625 + H° elaborado 1,05 m3 |
| 1351E Tabique H°A° 0,15 m | sin encofrado ni alambre | agregado alambre **0,525**, clavos **1,785**, tablas cepilladas **3,465 m2**, tirante **0,3 ml** (igual que 1351); orden corregido (antes de la S) |
| 1351 / 1351S Tabique H°A° 0,15 m | arena 0,66 + piedra 0,66 | arena **0,65** + piedra **0,65** |
| **1351X** Tabique H°A° 0,15 m (NUEVA) | no existía | Subcontrato tipo X (103351) 1 m3 + hierro 73,5 + mismo encofrado + H° elaborado 1,05 m3 |
| 1352E Tabique H°A° 0,15 m en submuración | subcontrato 101352 (código S con descripción "tipo E"); sin encofrado ni alambre | subcontrato **102352** (E); hierro 100 + alambre **0,70** + clavos **0,9** + tablas **1,75 m2** (una cara) + puntales **3 ml** |
| Insumo 101352 | "Subcontrato tipo E, tabiques de Hormigón Armado 0.15m." | "**Subcontrato tipo S**, Tabique de Hormigón Armado 0.15m en submuración." (revisar su precio en PUnitarios) |
| **1352 / 1352S / 1352T / 1352X** submuración (NUEVAS) | no existían | Id 2M0R (propia, pasa a ser la base) / 2M0S / 2M0T / 2M0U. Propia: Oficial 40 h + Ayudante 36 h + materiales + mezcla 330/0,65/0,65. S: 101352 + materiales + mezcla. T: 104352. X: 103352 + materiales + H° elaborado 1,05 |
| 1353 Dinteles de hormigón armado | tarea (Id 2M0M) superpuesta con 1342 "Encadenados y/o dinteles" | **ELIMINADA** con sus incidencias (decisión del usuario): los dinteles se cotizan con la 1342 |

Subrubro 3.b.3 Tanques y escaleras terminado.

## Rubro 3 — 3.c Tareas desglosadas

| Tarea | Antes | Después |
|---|---|---|
| 1354 Hormigón puesto sobre encofrado | cemento 315 + arena 0,6825 + piedra 0,6825 | cemento **330** + arena **0,65** + piedra **0,65** |
| **1354X** Hormigón puesto sobre encofrado (NUEVA) | no existía | Subcontrato tipo X de MdeO (insumo nuevo 103354) 1 m3 + H° elaborado 1,05 m3 |

- Insumo nuevo 103354 Subcontrato tipo X, Hormigón, puesto sobre encofrado, m3, Id 1A3Q — falta precio en PUnitarios.
| 1355 Hierro redondo sobre encofrado (Tn) | hierro 1000 kg/Tn | hierro **1050 kg/Tn** (5 % desperdicio por recortes y empalmes) |
| **1355X** Hierro redondo sobre encofrado (NUEVA) | no existía | Subcontrato tipo X de MdeO (insumo nuevo 103355, Tn) 1 Tn + hierro 1050 kg + alambre 10 kg |
- Insumo nuevo 103355 Subcontrato tipo X, Hierro redondo, sobre encofrado, por tonelada, Tn, Id 1A77 — falta precio en PUnitarios.

Rubro 3: 1360 (metálicas) y 0258S (gaviones) quedan como están por ser genéricas. Pendientes para el final: variantes E/X de 1171–1174 (y S de 1171); desperdicio H° 1111E/1111X 1,10 → 1,05.

## Rubro 4 — Mamposterías y tabiques (desde 2026-11-08)

En mamposterías solo aplican las variantes S y T (no llevan hormigón).

| Tarea | Antes | Después |
|---|---|---|
| 2110S Mampostería ladrillos comunes 0,45 m (submuración) | ladrillo común 380 un/m3 | **400 un/m3** (igual que 2110) |
| Insumos 202210 / 2T2210 (panderete 2210) | descripción "asfalalto" | corregido a "asfalto". Cantidades sin cambio (el asfalto se cotiza con la 2340 Capa asfáltica vertical) |
| 2220 / 2220S Mampostería ladrillos comunes 0,30 m (sótanos) | ladrillo común 380 un/m3 | **400 un/m3** (criterio 5 % rotura, igual que 2110) |
| 2310 / 2310S Mampostería ladrillos comunes 0,45 m (cimientos) | ladrillo común 420 un/m3 | **400 un/m3** |
| 2320 / 2320S Mampostería ladrillos comunes 0,30 m (cimientos) | ladrillo común 380 un/m3 | **400 un/m3** |
| 2411 Ladrillos comunes 0,15 m (elevación) | Oficial 6,2 h + Ayudante 6,5 h por m3 (igual que 0,30 m) | Oficial **7,5 h** + Ayudante **7,5 h** (≈2,2 h/m2) |
| Insumo 2T2411 | "Mat. y MdeO. para  para ladrillos…" | "Mat. y MdeO. para ladrillos…" |
| 2412S / 2412T Ladrillos comunes 0,30 m (elevación) | subcontratos 202412 y 2T2412 en hs, tarea en m3 | ambos en **m3**; nombre del 2T2412 sin "para" repetido |
| 2412 / 2412S Ladrillos comunes 0,30 m (elevación) | cal 53 kg/m3 | cal **38 kg/m3** (mismo mortero que la de 0,15 m) |
| Insumo 2T2413 | "Mat. y MdeO. para  para Ladrillos vista…" | sin "para" repetido. Cantidades de 2413 sin cambio |
| 14 insumos "Mat. y MdeO." (2T2330, 2T2340, 2T2414, 2T2415, 2T2418, 2T2430, 2T2524, 2T2615, 2T2623, 2T2663, 5T5171, 5T5212, 5T5221, 5T5231) | descripción con "para para" | sin "para" repetido (solo nombre; códigos y cantidades sin cambio) |
| 2414 / 2414S Ladrillos vista 0,30 m (elevación) | ladrillo para vista 420 un/m3 | **440 un/m3** (mismo criterio que 0,15 m: 10 % descarte por selección) |
| 2418 / 2418S Tabique de panderete | ladrillos 27, cemento 1,8, cal 1,5, arena 0,01 (S 0,02) | igual que 2210: ladrillos **28**, cemento **2 kg**, cal **2 kg**, arena **0,01 m3** por m2. Horas sin cambio |
| 2422 / 2422S / 2422T Ladrillos huecos 12/18/33 | tarea en m2 con cantidades por m3 (110 ladrillos, 8,4+8 h, cemento 15,2, cal 10,6, arena 0,09); subcontratos en m3 | por **m2**: ladrillos **16,5**, cemento **3 kg**, cal **2 kg**, arena **0,015 m3**, Oficial **1,0 h** + Ayudante **0,95 h**; subcontratos 202422 y 2T2422 en **m2** |
| 2423 / 2423S / 2423T Ladrillos huecos 18/18/33 | tarea en m2 con cantidades por m3 (74 ladrillos, 8,3+8 h, cemento 15,2, cal 10,6, arena 0,09); subcontratos en m3 | por **m2**: ladrillos **16,5**, cemento **4 kg**, cal **2,5 kg**, arena **0,02 m3**, Oficial **1,1 h** + Ayudante **1,05 h**; subcontratos 202423 y 2T2423 en **m2** |
| 2424 / 2424S Ladrillos huecos portantes | cemento 5,88, cal 6,09, arena gruesa 0,064 + arena fina 0,0147 m3/m2; Oficial 0,96 + Ayudante 0,84 h | mortero igual que 2423: cemento **4 kg**, cal **2,5 kg**, arena mediana **0,02 m3** (sin arena gruesa ni fina); Oficial **1,2 h** + Ayudante **1,1 h** |
| 2425S Bloques hormigón 10/20/40 | subcontrato 202424 (de ladrillos portantes) | subcontrato **202425** |
| Insumo 202425 | "M. de Obra Bloques huecos de hormigón 20/20/40" (lo usaba la 2426S) | "M. de Obra Bloques huecos de hormigón **10/20/40**" (revisar precio en PUnitarios) |
| Insumo 2T2425 (2425T) | "…Bloques huecos de hormigón 20/20/40", en m3 | "…**10/20/40**", en **m2** (revisar precio) |
| 2426S Bloques hormigón 20/20/40 | subcontrato 202425 | subcontrato **202426** (insumo nuevo) |
| 2425 / 2425S Bloques hormigón 10/20/40 | arena 0,03 m3/m2 | arena **0,01 m3/m2** |

- Insumo nuevo 202426 M. de Obra Bloques huecos de hormigón 20/20/40, m2 — falta precio en PUnitarios.
| 2426 / 2426S Bloques hormigón 20/20/40 | cemento 2,1 kg, cal aérea 1,14 kg, arena 0,0105 m3 | cemento **4 kg**, cal **hidráulica 2 kg**, arena **0,02 m3** (mortero de muro de 18-20 cm) |
| **2426T** Bloques hormigón 20/20/40 (NUEVA) | no existía | Mat. y MdeO. (insumo nuevo 2T2426) 1 m2 |

- Insumo nuevo 2T2426 Mat. y MdeO. para Bloques huecos de hormigón 20/20/40, m2 — falta precio en PUnitarios.

| Tarea | Antes | Después |
|---|---|---|
| Insumos 202460 / 202470 | nombres cruzados (202460 decía "SI Panel", 202470 "Steel Frame") | 202460 "Subcontrato M. de O. Estructuras **Steel Frame**"; 202470 "…**SI Panel**" |
| 2460S Steel Frame | cinta tramada 50 ml/m2 | **1,5 ml/m2** |
| **2460** Steel Frame (NUEVA, propia) | no existía | Id 6402 (pasa a ser la base de 2460S/T): Oficial **1,2 h** + Ayudante **1,0 h** (estimado) + mismos materiales que 2460S |
| 2470S SI Panel | tarea en gl; sin material | tarea en **m2**; agregado **Panel SIP (OSB + EPS) 1,05 m2/m2** (insumo nuevo 2471) |
| 2470T SI Panel | descripción "Subcontrato estructura SI Panel" | "Provision y montaje de estructuras SI Panel" (igual que la S) |

- Insumo nuevo 2471 Panel SIP (OSB + EPS), m2 — falta precio en PUnitarios.
| 2415S / 2415T Ladrillones macizos | subcontratos 202415 y 2T2415 en hs, tarea en m3 | ambos en **m3** |
| 2430 / 2430S / 2430T Dinteles de ladrillo a la vista | tareas en m2 (cantidades por ml); S con subcontrato de panderete (202418); arena 0,04 / 0,01; sin hierro | tareas en **ml**; 2430S con subcontrato **202430** (MdeO dinteles); arena **0,01 m3/ml**; agregado hierro **0,8 kg/ml** (2 Ø8) en propia y S |
| 2440 De Aldrillo | tarea a medio cargar (subcontrato MdeO + 1 ladrillo vista/m2) | **ELIMINADA** con sus incidencias (decisión del usuario). Insumos 202850 y 2T2850 quedan sin uso |
| 2450 Ladrillos refractarios | sin cambio de cantidades | — |
| **2450S / 2450T** Ladrillos refractarios (NUEVAS) | no existían | S (Id 6O06): MdeO (insumo nuevo 202450) 1 m3 + ladrillos refractarios 451,5 + tierra refractaria 210 kg. T (Id 6O08): Mat. y MdeO. (insumo nuevo 2T2450) 1 m3 |

- Insumos nuevos 202450 (MdeO refractarios, m3, Id 2PSU) y 2T2450 (Mat. y MdeO. refractarios, m3, Id 3AW3) — falta precio en PUnitarios.

Rubro 4 terminado (2026-11-08).

## Rubro 5 — Revoques y terminaciones (desde 2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| Nombres de tareas e insumos (toda la base) | 41 tareas y 56 insumos con espacios dobles | espacios dobles y de los extremos limpiados (solo nombres; códigos y cantidades sin cambio) |
| 2612 Toma de juntas ladrillos macizos | — | sin cambio |
| 2613 Toma de juntas ladrillos cerámicos | — | sin cambio |
| 2615 / 2615S Bolseado ladrillos macizos | arena mediana 0,01 m3 | **arena fina** 0,01 m3 |
| 2616 / 2616S Azotado en muros (común) | con hidrófugo 0,13 kg (igual que el impermeable 2622) | **sin hidrófugo** |
| 2617T Picado de revoques | — | sin cambio (solo T; el insumo 202617 sigue sin uso) |
| 2621 Revoque impermeable vertical alisado | — | sin cambio |
| 2622 / 2622S Azotado impermeable | cemento 1,7 kg/m2 (≈1:6, igual que el común) | cemento **3,5 kg/m2** (≈1:3 con hidrófugo) |
| 2623 Tanques de agua al cucharín | — | sin cambio |
| 2653 / 2653S Revoque completo exterior PB | cemento 4,62, cal hidr. 2,84, cal aérea 0,42, arena med. 0,023, arena fina 0,0046, hidrófugo 0,14 | suma azotado imp. + grueso + fino: cemento **7**, cal hidr. **4,4**, cal aérea **0,65**, arena med. **0,02**, arena fina **0,02**, hidrófugo **0,13**. Horas sin cambio |
| 2654 / 2654S Revoque completo exterior PA | mismos materiales cortos que tenía la 2653; Oficial 2,0291 h | materiales iguales a 2653 (cemento 7, cal hidr. 4,4, cal aérea 0,65, arena med. 0,02, fina 0,02, hidrófugo 0,13); Oficial **2,05 h** |
| 2661 Revoque de frente salpicado | Oficial 0,15 + Ayudante 0,3 h | Oficial **0,3 h** + Ayudante **0,15 h** |
| **2661S / 2661T** Salpicado (NUEVAS) | no existían | S (Id 6Y0X): MdeO (insumo nuevo 202661) 1 m2 + salpicrete 4 kg. T (Id 6Y0Y): Mat. y MdeO. (insumo nuevo 2T2661) 1 m2 |

- Insumos nuevos 202661 y 2T2661 (salpicado, m2) — falta precio en PUnitarios.
| 2662 Revoque de frente símil piedra | Oficial 0,85 + Ayudante 1,65 h | Oficial **1,65 h** + Ayudante **0,85 h** |
| **2662S / 2662T** Símil piedra (NUEVAS) | no existían | S: MdeO (insumo nuevo 202662) 1 m2 + símil piedra 10 kg. T: Mat. y MdeO. (insumo nuevo 2T2662) 1 m2 |

- Insumos nuevos 202662 y 2T2662 (símil piedra, m2) — falta precio en PUnitarios.
| 2663 Revoque de frente tipo IGGAM | — | sin cambio |
| 2625 / 2625S Revoque hidrófugo bajo bañeras | cemento 22,89, arena 0,0315, hidrófugo 0,7875 (2621 × 1,05) | cemento **22 kg**, arena **0,03 m3**, hidrófugo **0,75 kg** (igual que 2621). Horas sin cambio |
| 2631 / 2631S Revoque grueso a la cal PB | mortero para ~2 cm: cemento 2,5, cal hidr. 4,4, arena 0,02 | mortero para **3 cm** (criterio del usuario): cemento **3,75 kg**, cal hidr. **6,6 kg**, arena **0,03 m3**. Horas sin cambio |
| 2632 / 2632S Grueso PA y 2634 / 2634S Grueso bajo revestimientos | mortero para ~2 cm (cemento 2,5, cal 4,4, arena 0,02) | grueso de **3 cm**: cemento **3,75**, cal hidr. **6,6**, arena **0,03** |
| 2653 / 2653S y 2654 / 2654S Revoque completo exterior PB / PA | componente grueso de 2 cm | grueso de 3 cm: cemento **8,2** (3,5 azotado + 3,75 grueso + 0,95 fino), cal hidr. **6,6**, arena mediana **0,03**; resto sin cambio |
| 2632 Revoque grueso PA (horas) | Oficial 0,8 + Ayudante 0,7 h | sin cambio (más que PB por andamio) |
| 2634 Revoque grueso bajo revestimientos (horas) | Oficial 0,55 + Ayudante 0,55 h | sin cambio |
| 2641 Revoque fino a la cal fratazado PB | — | sin cambio |
| 2642 Revoque fino a la cal fratazado PA | — | sin cambio (mismos materiales que PB, un poco más de horas) |
| 2643 / 2643S Revoque fino al fieltro | arena fina 0,02 m3 | arena fina **0,01 m3** (mismo espesor que el fratazado) |
| 2651 / 2651S Revoque completo interior PB | cemento 3,5, cal hidr. 5,05, cal aérea 0,74, arena med. 0,02, fina 0,01 | suma grueso 3 cm + fino: cemento **4,7**, cal hidr. **6,6**, cal aérea **0,65**, arena med. **0,03**, fina **0,01**. Horas sin cambio (ya eran la suma) |
| 2652 / 2652S Revoque completo interior PA | materiales con grueso de 2 cm; Oficial 1,3 + Ayudante 0,9 h | materiales = 2651 (grueso 3 cm + fino); Oficial **1,4 h** + Ayudante **1,15 h** (suma 2632 + 2642) |
| 2635S Revoque grueso en cielorrasos | cemento 3,5, cal hidr. 5,05, arena med. 0,02 + arena fina 0,01 | grueso 3 cm: cemento **3,75**, cal hidr. **6,6**, arena med. **0,03** (sin arena fina) |
| **2635** Revoque grueso en cielorrasos (NUEVA, propia) | no existía | Id 7O0A (base de 2635S/T): Oficial **0,9 h** + Ayudante **0,6 h** + mismos materiales. Nombre de 2635T con punto final, igual que las otras |
| 2644 / 2644S Revoque fino en cielorrasos | cemento 1,05, cal aérea 0,71, arena fina 0,02 | igual que 2641: cemento **0,95**, cal aérea **0,65**, arena fina **0,01**. Horas sin cambio |
| 2671 Cielorraso aplicado completo | Oficial 1,3 + Ayudante 0,9 h; cemento 3,5, cal hidr. 5,05, aérea 0,5, arena med. 0,02, fina 0,01 | suma 2635 + 2644: Oficial **1,78 h** + Ayudante **1,26 h**; cemento **4,7**, cal hidr. **6,6**, aérea **0,65**, arena med. **0,03**, fina **0,01** |
| **2671S** Cielorraso aplicado completo (NUEVA) | no existía | subcontrato 202671 (ya existía sin uso) 1 m2 + mismos materiales |
| 2672 / 2672S Cielorraso suspendido completo | mortero ~2 cm con cal aérea × 1,05 (cemento 2,31, aérea 3,885, arena med. 0,0168, fina 0,0084) | mortero igual que 2671 (grueso 3 cm + fino): cemento **4,7**, cal hidr. **6,6**, aérea **0,65**, arena med. **0,03**, fina **0,01**. Estructura y horas sin cambio |

Rubro 5 terminado (2026-11-08).

## Rubro 6 — Contrapisos y capas aisladoras (desde 2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 2511 / 2511S Contrapiso s/terreno de cascotes 0,12 m | cascote 0,09 m3/m2 | cascote **0,12 m3/m2** (≈1 m3 por m3 de contrapiso) |
| 2512 / 2512S Contrapiso s/terreno de H° pobre 0,12 m | arena 0,11 + piedra 0,11 m3/m2 | arena **0,085** + piedra **0,085** m3/m2 (criterio H° pobre 0,70 + 0,70 por m3) |
| 2521 / 2521S Contrapiso s/losa de cascotes 0,08 m | cascote 0,06 m3/m2 | cascote **0,08 m3/m2** |
| 2522 Contrapiso s/losa de H° pobre 0,08 m | cemento 15,12, arena 0,15 + piedra 0,15 m3/m2 | cemento **17,5 kg**, arena **0,056** + piedra **0,056** m3/m2 (= 2512 en proporción a 8 cm) |
| **2522S / 2522T** (NUEVAS) | no existían | S: MdeO (insumo nuevo 202522) 1 m2 + mismos materiales. T: Mat. y MdeO. (insumo nuevo 2T2522) 1 m2 |

- Insumos nuevos 202522 y 2T2522 (contrapiso s/losa H° pobre, m2) — falta precio en PUnitarios.
| 2523 Contrapiso s/losa de arcilla 0,08 m | — | sin cambio |
| 2524 Relleno de losas bajas | cemento 20 + cal 14 kg (S: 34 + 4,5) | cemento **34 kg** + cal **4,5 kg** (igual que la S) |
| 2531 / 2531S Contrapiso s/azotea de cascotes 0,18 m | cascotes 0,14; arena 0,09 (S 0,10) | cascotes **0,18 m3/m2**, arena **0,09 m3/m2** en ambas |
| 2533 Contrapiso s/azotea de arcilla 0,18 m | Oficial 0,4 + Ayudante 0,45 h (igual que el de 8 cm) | Oficial **0,9 h** + Ayudante **1,0 h** |
| **2533S / 2533T** (NUEVAS) | no existían | S: MdeO (insumo nuevo 202533) 1 m2 + arcilla 0,2 + cemento 40,5 + cal 5,4. T: Mat. y MdeO. (insumo nuevo 2T2533) 1 m2 |

- Insumos nuevos 202533 y 2T2533 (contrapiso s/azotea de arcilla, m2) — falta precio en PUnitarios.
| 2330S y subcontratos 202330 / 2T2330 | nombre "Capa aisladora doble en muros" | "Capa aisladora **horizontal** en muros" (es la simple; materiales y horas sin cambio) |
| 2340 Capa asfáltica vertical en muro | Oficial 0,7 + Ayudante 0,6 h | Oficial **0,2 h** + Ayudante **0,1 h** (pintura asfáltica 2 manos) |
| 2350 / 2350S Capa aisladora vertical de concreto con panderete | Oficial 1,2 + Ayudante 0,75; cemento 13, cal 8, arena fina 0,03, ladrillos 26, hidrófugo 0,25 | suma 2330 + 2210: Oficial **1,5** + Ayudante **1,1**; cemento **12,5**, cal **2**, arena fina **0,03** + mediana **0,01**, ladrillos **28**, hidrófugo **0,25** |
| 2620 Capa horizontal de concreto s/contrapiso | cemento 5 kg (≈1:6), arena 0,03, hidrófugo 0,5 | mortero igual que 2330: cemento **10,5 kg**, arena **0,03**, hidrófugo **0,25** |
| **2620S / 2620T** (NUEVAS) | no existían | S: MdeO (insumo nuevo 202620) 1 m2 + mismos materiales. T: Mat. y MdeO. (insumo nuevo 2T2620) 1 m2 |

- Insumos nuevos 202620 y 2T2620 (capa horizontal s/contrapiso, m2) — falta precio en PUnitarios.

Rubro 6 terminado (2026-11-08).

## Rubro 7 — Revestimientos y accesorios (desde 2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 5311 Revestimiento cerámico 20/20 h<1,80 | Oficial 0,85 + Ayudante 1,7 h; sin pastina | Oficial **1,2 h** + Ayudante **0,6 h**; pastina **0,3 kg/m2** (propia y S) |

- Insumo nuevo 2242 Pastina para juntas, Kg — falta precio en PUnitarios.
| 5312T Revestimiento cerámico 20/20 h>1,80 | subcontrato 5T5313 (de cielorrasos) | subcontrato **5T5312** (insumo nuevo) |
| 5312 / 5312S | Oficial 1,5 + Ayudante 1,5 h; cerámico 1,1 m2; sin pastina; nombre 505312 "h>r 1,8" | Oficial **1,4 h** + Ayudante **0,8 h**; cerámico **1,05 m2**; pastina **0,3 kg**; nombre "h>1,8" |

- Insumo nuevo 5T5312 Mat. y MdeO. para Revest. cerámico esmaltado 20/20 h>1,8, m2 — falta precio en PUnitarios.
| 5313S Revestimiento cerámico 20/20 cielorrasos | cerámico de piso (5122); sin pastina | cerámico de pared **5311** 1,05 m2; pastina **0,3 kg** |
| 5313T | nombre abreviado "Revest. … cielor" | "Revestimiento cerámico esmaltado 20/20 cielorrasos" |
| **5313** (NUEVA, propia) | no existía | Oficial **1,8 h** + Ayudante **0,9 h** + cerámico 1,05 + adhesivo 4,5 + pastina 0,3. Pasa a ser la base de 5313S/T |
| 5321 / 5321S Azulejos lisos 15/15 h<1,80 | azulejos 1,09 / 1,1 m2; sin pastina | azulejos **1,05 m2**; pastina **0,4 kg/m2** |
| 5322S Azulejos lisos 15/15 h>1,80 | azulejos 1,1 m2; sin pastina | azulejos **1,05**; pastina **0,4 kg** |
| 5322T | nombre abreviado | "Revestimiento de azulejos lisos 15/15 h > 1,80m." |
| **5322** (NUEVA, propia) | no existía | Oficial **1,6 h** + Ayudante **0,9 h** + mismos materiales que la S; base de 5322S/T |
| 5323S Azulejos lisos 15/15 cielorrasos | azulejos 1,2 m2; sin pastina | azulejos **1,05**; pastina **0,4 kg** (adhesivo 5 kg sin cambio) |
| 5323T | nombre abreviado | "Revestimiento de azulejos lisos 15/15 cielorrasos." |
| **5323** (NUEVA, propia) | no existía | Oficial **2,1 h** + Ayudante **1,0 h** + mismos materiales que la S; base de 5323S/T |
| 5325S Porcellanato | — | sin cambios por ahora (pendiente: adhesivo, pastina, nombre, propia y T con 5T5185) |
| 5330S / 5330T Microcemento | nombre "Microcemento"; S con subcontrato de piso (505190) y sin material | nombre "**Revestimiento de microcemento**"; S con subcontrato nuevo **505330** + **Microcemento (sistema completo) 2 kg/m2** (insumo nuevo 5330) |

- Insumos nuevos 505330 (MdeO revestimiento microcemento, m2) y 5330 (Microcemento sistema completo, Kg) — falta precio en PUnitarios.
| Ladrillitos tejuela | código **5331S** con horas propias y sin subcontrato | renombrada a **5331** (propia, Id 8M0I sin cambio); base de 5331S/T |
| Insumo 5331 Ladrillito 5x27 | unidad m2, 66 por m2 | unidad **un**, **58 un/m2** |
| **5331S** (NUEVA) | no existía | Id 8M0O: subcontrato nuevo 505331 (MdeO) 1 m2 + mismos materiales |

- Insumo nuevo 505331 M. de Obra Revestimiento de frentes con ladrillitos tejuela, m2 — falta precio en PUnitarios.
| 5344 Revestimiento de escaleras en cerámico | sin pastina | pastina **0,3 kg/m2** |
| **5344S / 5344T** (NUEVAS) | no existían | S: MdeO (insumo nuevo 505344) 1 m2 + mismos materiales. T: Mat. y MdeO. (insumo nuevo 5T5344) 1 m2 |

- Insumos nuevos 505344 y 5T5344 (revestimiento de escaleras cerámico, m2) — falta precio en PUnitarios.
| 5411–5416 Accesorios de baño (jaboneras, perchas, portarrollos, toallero) | Oficial 0,8 + Ayudante 0,2 h + 1 un | sin cambio |

Rubro 7 terminado (2026-11-08), salvo 5325S Porcellanato pendiente.

## Rubro 8 — Yesería (desde 2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 17 tareas T de yesería (3210T–3270T, 3110T–3130T, 3310T–3450T) | subcontrato total 1 unidad, unidades coinciden | sin cambio |
| 3141 Estructura de sostén para cielorrasos | — | sin cambio |
| Cielorraso Durlock | código **3141S** "Subcontrato cielorraso Durlock", solo materiales, sin MdeO | código **3150S** "Cielorraso de placas de yeso (Durlock)" (Id 9C05 sin cambio) + subcontrato MdeO **303150** (nuevo) |
| **3150 / 3150T** (NUEVAS) | no existían | 3150 propia (Id 9C06, base): Oficial **0,6 h** + Ayudante **0,3 h** + mismos materiales. 3150T (Id 9C07): Mat. y MdeO. (nuevo 3T3150) 1 m2 |

- Insumos nuevos 303150 y 3T3150 (cielorraso Durlock, m2) — falta precio en PUnitarios.

Rubro 8 terminado (2026-11-08).

## Rubro 9 — Pisos y zócalos (desde 2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 5111 Piso de cemento alisado con carpeta 3 cm | — | sin cambio |
| 5112 Carpeta de cemento bajo pisos cerámicos | — | sin cambio |
| 5113 Carpeta de cemento bajo pisos de madera | — | sin cambio |
| 5114 Carpeta hidrófuga sobre contrapisos | arena mediana 0,03 + arena fina 0,03 (≈1:6) | sin arena mediana (igual que la S, ≈1:3). Ojo: casi igual a la 2620 del rubro 6 |
| 5121 / 5121S Piso cerámico 30/30 | S con Ayudante 0,95 h además del subcontrato; cerámico 1,1; sin pastina; nombre 505121 "cerá,micos" | S sin horas propias; cerámico **1,05 m2**; pastina **0,25 kg/m2**; nombre "Subcontrato colocación pisos cerámicos" |
| 5122 / 5122S Piso cerámico 20/20 | cal 3,25 (S 5,8); cerámico 1,1; sin pastina | cal **5,8 kg** (igual que el resto de pisos cerámicos); cerámico **1,05 m2**; pastina **0,3 kg/m2** |
| 5121 / 5121S Piso cerámico 30/30 | cal 3,25 kg | cal **5,8 kg** (mismo mortero de asiento que el resto) |
| 5123 / 5123S Piso cerámico común 08/16 | propia sin arena; cerámico 1,1; sin pastina | arena **0,03 m3** en la propia; cerámico **1,05 m2**; pastina **0,5 kg/m2** |
| 5124 / 5124S Piso cerámico común antideslizante 08/16 | cerámico 1,1; sin pastina | cerámico **1,05 m2**; pastina **0,5 kg/m2** |
| 5125 / 5125S Baldosa cerámica de azotea 20/20 | baldosa 1,1; sin junta | baldosa **1,05 m2**; pastina **0,4 kg/m2** |
| 5132 Piso de mosaico granítico 30/30 | pulido (505139) incluido en propia y S | sin cambio: el pulido queda incluido (decisión del usuario); la 5139 queda para pulir pisos existentes |
| 5134 Piso de mosaico granítico 40/40 | — | sin cambio (pulido incluido, mismo criterio que 5132) |
| 5139S / 5139T Pulido de pisos graníticos | — | sin cambio (para pisos existentes) |
| Piso falso técnico | **5140** sin letra (con subcontrato MdeO) | renombrada **5140S** (Id 9Q0Z sin cambio) |
| Piso técnico T | **5180T** "Piso Tecnico" en rubro 10 (Id AU01), compartía número con 5180S granitullo | **5140T** "Piso falso (técnicos elevados)", movida a 9.a Pisos, **Id nuevo 9Q15**; variante de 5140S. 5180S granitullo queda sola. Subcontratos 505180 / 5T5180 conservan su código |
| 5151S Parquet eucalipto | solo subcontrato MdeO, sin materiales | + **Parquet de eucalipto 1,05 m2** (insumo nuevo 5151) + **Adhesivo para parquet 1 kg** (insumo nuevo 5152) |

- Insumos nuevos 5151 Parquet de eucalipto (m2) y 5152 Adhesivo para parquet (Kg) — falta precio en PUnitarios.
| 5171 / 5171S Losetas de vereda 40/60 | sin junta | pastina **0,3 kg/m2** |
| 5212 / 5212S Zócalo de cemento alisado h=10 cm | arena fina 0,01 m3/ml | arena fina **0,003 m3/ml** |
| 5221 / 5221S Zócalo cerámico 10/20 | arena fina 0,01 m3/ml; sin pastina | arena fina **0,002 m3/ml**; pastina **0,03 kg/ml** |
| 5222 Zócalo cerámico 10/30 | arena fina 0,01 m3/ml; sin pastina | arena fina **0,002**; pastina **0,02 kg/ml** |
| **5222S / 5222T** (NUEVAS) | no existían | S: MdeO (insumo nuevo 505222) 1 ml + mismos materiales. T: Mat. y MdeO. (insumo nuevo 5T5222) 1 ml |

- Insumos nuevos 505222 y 5T5222 (zócalo cerámico 10/30, ml) — falta precio en PUnitarios.
| 5231 / 5231S Zócalo granítico 10/30 | arena 0,01; zócalo 1,1 ml; sin pastina | arena **0,002 m3**; zócalo **1,05 ml**; pastina **0,02 kg** por ml |
| 5251 Zócalo de madera | nombre "Zócalo de Cedro." con material de eucalipto; Oficial 0,6 + Ayudante 0,4 h/ml | nombre "**Zócalo de madera (eucalipto) h=10cm**"; Oficial **0,2 h** + Ayudante **0,1 h** por ml |

Rubro 9 terminado (2026-11-08).

## Rubro 10 — Pavimentos (desde 2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 1161T Platea 0,12 m | insumo 104161 en m3 | **m2** |
| 1161E / 1161S | sin alambre; nombre E "Subcontrato Platea…" | alambre **0,02 kg/m2**; nombre "Platea de 0,12m de espesor." |
| 1161 | Oficial 1,27 + Ayudante 1,56 h | Oficial **1,0 h** + Ayudante **1,5 h** (escala con 0,15 y 0,20 m) |
| **1161X** (NUEVA) | no existía | Subcontrato X (103161) 1 m2 + malla 3,3 + alambre 0,02 + H° elaborado 0,13 m3 |
| 1160E Platea 0,12 m con Mapefibre | solo Mapefibre 1 kg/m2 (sin hormigón ni subcontrato) | completada: Subcontrato tipo E (insumo nuevo 102160) 1 m2 + H° elaborado **0,13 m3** + Mapefibre **0,5 kg/m2** (≈4 kg/m3), sin malla. Nombre "Platea de 0,12m de espesor c/MAPEFIBRE (sin malla)." |

- Insumo nuevo 102160 Subcontrato tipo E, Platea de 0,12m de espesor c/fibra., m2 — falta precio en PUnitarios.
| 5162 Piso H°A° fratazado 0,15 m | Oficial 0,48 + Ayudante 1,0 h; cemento 45, arena 0,05, piedra 0,07; sin alambre | Oficial **1,3 h** + Ayudante **2,0 h** (más que la platea: terminación de piso, criterio usuario); materiales = platea 1162: cemento **55**, arena **0,10**, piedra **0,10**, malla 3,3, alambre **0,02** |
| **5162S / 5162T** (NUEVAS) | no existían | S: MdeO (insumo nuevo 505162) + mismos materiales. T: Mat. y MdeO. (insumo nuevo 5T5162) 1 m2 |

- Insumos nuevos 505162 y 5T5162 (piso H°A° fratazado 0,15 m, m2) — falta precio en PUnitarios.
| 5163 / 5163S Piso H°A° fratazado 0,20 m | malla simple 3,3/3,4; sin alambre; cemento 60, arena 0,07, piedra 0,09; Oficial 0,7 + Ayudante 1,2 h | materiales = platea 1163 (doble malla **6,6**, alambre **0,04**, cemento **75**, arena **0,13**, piedra **0,13**); Oficial **1,7 h** + Ayudante **2,7 h** |
| 5164 / 5164S Piso H°A° alisado mecánico color 0,12 m | propia: Oficial 0,3 + Ayudante 0,6 h, cemento 50, arena 0,06, piedra 0,09, malla 3,3, sin alambre ni endurecedor ni alisadora; S: solo subcontrato | materiales = platea 0,12 (cemento **45**, arena **0,08**, piedra **0,08**, malla 3,3, alambre **0,02**) + **endurecedor color 4 kg/m2** en propia y S; propia + **alisadora 0,05 h/m2**, Oficial **1,2 h** + Ayudante **1,7 h** |

- Insumos nuevos 5169 Endurecedor no metálico color para pisos (Kg) y 5172 Alquiler alisadora mecánica (hs) — falta precio en PUnitarios.
| 5165 / 5165S Piso H°A° alisado mecánico color 0,15 m | Oficial 0,24 + Ayudante 0,72 h; cemento 63, arena 0,08, piedra 0,11; malla 3,2/3,3; sin alambre, endurecedor ni alisadora | materiales = platea 0,15 (cemento **55**, arena **0,10**, piedra **0,10**, malla **3,3**, alambre **0,02**) + endurecedor **4 kg**; propia + alisadora **0,05 h**, Oficial **1,3** + Ayudante **2,0 h** |
| 5166 / 5166S Piso H°A° alisado mecánico color 0,20 m | Oficial 0,39 + Ayudante 0,88 h; cemento 83, arena 0,10, piedra 0,15; malla 3,3/4,2; sin alambre, endurecedor ni alisadora | materiales = platea 0,20 (doble malla **6,6**, alambre **0,04**, cemento **75**, arena **0,13**, piedra **0,13**) + endurecedor **4 kg**; propia + alisadora **0,05 h**, Oficial **1,7** + Ayudante **2,7 h** |
| 5167S / 5167T Aserrado de juntas | S en m2 (subcontrato en ml); nombres distintos | S en **ml**; T con el mismo nombre que la S |
| 5168 Juntas de dilatación | tarea en m2 (cantidades por ml de junta) | tarea en **ml**; cantidades sin cambio |
| Insumo 5160 Granitullo 10x10 | unidad m2 (90 por m2) | unidad **un** (90 piezas por m2) |
| Granitullo | código **5180S** con horas propias y sin subcontrato | renombrada **5180** (propia, Id AU00 sin cambio) |
| **5180S / 5180T** Granitullo (NUEVAS) | no existían | S (Id AU01): MdeO (insumo nuevo 505181) + mismos materiales. T (Id AU04): Mat. y MdeO. (insumo nuevo 5T5181) 1 m2 |

- Insumos nuevos 505181 y 5T5181 (pavimento de granitullo, m2) — falta precio en PUnitarios.
| Insumo 5170 Pavimento Articulado | unidad m2 (53 por m2) | unidad **un** (53 piezas por m2) |
| Bloques articulados | código **5190S** con horas propias y sin subcontrato | renombrada **5190** (propia, Id AU02) |
| **5190S / 5190T** Bloques articulados (NUEVAS) | no existían | S (Id AU05): MdeO (insumo nuevo 505191) + mismos materiales. T (Id AU06): Mat. y MdeO. (insumo nuevo 5T5191) |
| Piso de microcemento | código **5190T** "de Microcemento" (compartía número con bloques) | código **5195T** "Piso de microcemento" (Id AU03 sin cambio) |
| **5195S** Piso de microcemento (NUEVA) | no existía | Id AU07: subcontrato existente 505190 (estaba sin uso) + Microcemento (5330) 2 kg/m2; base de 5195T |

- Insumos nuevos 505191 y 5T5191 (bloques articulados, m2) — falta precio en PUnitarios.

Rubro 10 terminado (2026-11-08).

## Pendientes resueltos (2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 5325S Porcellanato | nombre "Porcellanato"; solo subcontrato + porcellanato | "**Revestimiento de porcellanato**"; + adhesivo **6 kg** + pastina **0,2 kg** |
| **5325 / 5325T** (NUEVAS) | no existían | 5325 propia (Id 8M0R, base): Oficial **1,5 h** + Ayudante **0,75 h** + mismos materiales. 5325T (Id 8M0S): 5T5185 (existía sin uso) 1 m2 |
| **1171E / 1171S / 1171X** Pocetes H° ciclópeo (NUEVAS) | no existían | E y X: subcontrato (nuevos 102171 / 103171) + H° elaborado pobre (1810) **0,65 m3** + piedra bola **0,4 m3**. S: subcontrato (nuevo 101171) + mismos materiales que la propia |
| **1172E/X, 1173E/X, 1174E/X** (NUEVAS) | no existían | subcontrato E / X (102172-4 / 103172-4, ya existían) + H° elaborado pobre (1810) **1,05 m3** |
| 1111E / 1111X Bases centradas | H° elaborado 1,10 m3 | **1,05 m3** (igual que el resto de las E) |

- Insumos nuevos 101171, 102171, 103171 (pocetes H° ciclópeo, m3) — falta precio en PUnitarios.
| 2620 / 2620S / 2620T Capa horizontal de concreto s/contrapiso | duplicaba la 5114 Carpeta hidrófuga sobre contrapisos | **ELIMINADAS** con sus incidencias (decisión del usuario); se usa la 5114. Insumos 202620 y 2T2620 quedan sin uso |

## Rubro 13 — Cubiertas (desde 2026-11-08). Rubros 11 y 12 sin tareas.

| Tarea | Antes | Después |
|---|---|---|
| 4111 / 4111S Azotea inaccesible completa con techado asfáltico | Oficial 1,1 + Ayudante 1,65 h; cemento 38,2, arena 0,03, sin cal; membrana 1,3 m2; sin imprimación | suma de capas (contrapiso 2531 + EPS + carpeta 5112 + membrana): cemento **21**, cal **14**, arena **0,12**, cascote 0,18, EPS 1,05, membrana **1,15 m2**, imprimación asfáltica (2701) **0,3 kg**; Oficial **2,3** + Ayudante **2,2 h** |
| 4112 / 4112S Azotea inaccesible con techado y aluminio | mismos números que tenía la 4111; subcontratos 404112 / 4T4112 decían "accesible" | materiales y horas = 4111 (membrana con aluminio **1,15 m2**); nombres de subcontratos con "**inaccesible**…y aluminio" |
| 4121 Azotea accesible con baldosas cerámicas | Oficial 2,2 + Ayudante 1,65 h; cemento 41, arena 0,06, sin cal; membrana 1,3; baldosa 1,1; sin imprimación ni pastina | suma 4111 + 5125: cemento **24,3**, cal **19,8**, arena **0,15**, cascote 0,18, EPS 1,05, membrana **1,15**, imprimación **0,3**, baldosa **1,05**, pastina **0,4**; Oficial **3,4** + Ayudante **3,0 h** |
| **4121S / 4121T** (NUEVAS) | no existían | S: MdeO (insumo nuevo 404121) + mismos materiales. T: Mat. y MdeO. (insumo nuevo 4T4121) 1 m2 |

- Insumos nuevos 404121 y 4T4121 (azotea accesible, m2) — falta precio en PUnitarios.
| 4131S Cubierta con membrana 4 mm con aluminio | solo subcontrato | + **membrana 4 mm con aluminio 1,15 m2** (insumo nuevo 4113) + imprimación asfáltica **0,3 kg**; nombre de 4131T completo |

- Insumo nuevo 4113 Membrana asfáltica 4mm con aluminio, m2 — falta precio en PUnitarios.
| 4132S Cubierta con membrana 4 mm sin aluminio | solo subcontrato | + **membrana 4 mm 1,15 m2** (insumo nuevo 4114) + imprimación **0,3 kg**; nombre de 4132T completo |

- Insumo nuevo 4114 Membrana asfáltica 4mm, m2 — falta precio en PUnitarios.
| **4210** Cubierta de tejas francesas (NUEVA, propia) | no existía | Oficial **1,4 h** + Ayudante **1,5 h** + mismos materiales que 4210S; base de 4210S/T |
| 4220 / 4220S Cubierta de tejas españolas | caballete de pino 4,6 ml/m2 | caballete **0,2 ml/m2** (solo va en la cumbrera) |
| 4230 Cubierta de chapas onduladas galvanizadas | chapa 4 kg/m2; Oficial 0,6 + Ayudante 0,95 h | chapa **4,5 kg/m2** (solapes); Oficial **0,3** + Ayudante **0,3 h** (sin estructura) |
| **4230S / 4230T** (NUEVAS) | no existían | S: MdeO (insumo nuevo 404230) + chapa 4,5 + ferretería 0,2. T: Mat. y MdeO. (insumo nuevo 4T4230) 1 m2 |

- Insumos nuevos 404230 y 4T4230 (cubierta de chapa ondulada, m2) — falta precio en PUnitarios.
| 4310S Cubierta metálica c/aislación Roll 25 mm | chapa 4 kg; sin ferretería | chapa **4,5 kg**; ferretería **0,2 kg** |
| **4310** (NUEVA, propia) | no existía | Oficial **0,6 h** + Ayudante **0,6 h** + correas 1,5 ml + lana de vidrio 1,1 m2 + chapa 4,5 kg + ferretería 0,2 kg; base de 4310S/T |

Rubro 13 terminado (2026-11-08).

## Rubro 14 — Marmolería (2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 5511 Mesada de granito Gris Mara 2 cm | Oficial 4 + Ayudante 4 h/m2 | Oficial **2 h** + Ayudante **2 h** |
| **5511S / 5511T** (NUEVAS) | no existían | S: colocación (insumo nuevo 505511) + granito 1,2 m2. T: provisión y colocación (insumo nuevo 5T5511) 1 m2 |

- Insumos nuevos 505511 y 5T5511 (mesada de granito, m2) — falta precio en PUnitarios.

Rubro 14 terminado.

## Rubro 15 — Conductos, humeros y ventilaciones (2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 2720 Conducto unificado para baños | sin mano de obra | Oficial **0,4 h** + Ayudante **0,4 h** por ml |
| 2710T, 2720T, 2730T | — | sin cambio |

Rubro 15 terminado.

## Rubro 16 — Barandas y balcones (2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 6151 Baranda para balcones | tarea en un; Oficial 0,7 + Ayudante 1,4 h | tarea en **ml**; Oficial **1,4 h** + Ayudante **0,7 h** |
| 6152 Baranda para escaleras | tarea en un; Oficial 0,8 + Ayudante 1,6 h | tarea en **ml**; Oficial **1,6 h** + Ayudante **0,8 h** |

Rubro 16 terminado.

## Rubro 17 — Carpintería de madera y muebles (desde 2026-11-08)

| Tarea | Antes | Después |
|---|---|---|
| 6211 Puerta entrada madera, marco BWG 0,90 | Oficial 4,6 h; sin ayudante ni mortero | Oficial **3 h** + Ayudante **2 h**; mortero de amurado cemento **5 kg** + arena **0,01 m3** |
| 6212 Puerta placa pino 2", marco BWG 0,80 | Oficial 4 h; sin ayudante ni mortero | Oficial **3 h** + Ayudante **2 h**; mortero de amurado cemento **5 kg** + arena **0,01 m3** (= 6211) |
| 6213 Puerta placa pino 2", marco BWG 0,60-0,70 | Oficial 4,6 h; insumo puerta de 0,80 (6212); sin ayudante ni mortero | insumo nuevo **6213** Puerta placa pino 2", marco BWG 0,70m. (Id 5CPI, sin precio); Oficial **3 h** + Ayudante **2 h**; cemento **5 kg** + arena **0,01 m3** (= 6211) |

- Insumo nuevo 6213 Puerta placa pino 2", marco BWG 0,70m., un — falta precio en PUnitarios.
| 6216 Puerta placa cedro 2", marco BWG 0,60-0,70 | Oficial 4,26 h; sin ayudante ni mortero | Oficial **3 h** + Ayudante **2 h**; cemento **5 kg** + arena **0,01 m3** (= 6211) |
| 6217 Puerta corrediza 2 hojas (cedro) 2,15x2,00 | Oficial 4,6 h; sin ayudante ni mortero | Oficial **5 h** + Ayudante **3 h**; cemento **7 kg** + arena **0,015 m3** (marco más largo, guía y regulación de hojas) |
| 6390 Herrajes | 1 gl de herrajes (6700) | sin cambio (tarea genérica; la colocación va en las horas de cada puerta) |

Subrubro 17.a terminado.
| 6317 Cortina de enrollar plástico reforzado 2,10x1,10 | tarea en m2 (insumo 1 un); Oficial 5 h | tarea en **un**; Oficial **2,5 h** + Ayudante **1,5 h** |
| 6318 Cortina de enrollar plástico reforzado 2,40x1,10 | tarea en m2 (insumo 1 un); Oficial 5 h | tarea en **un**; Oficial **2,5 h** + Ayudante **1,5 h** (= 6317) |
| 6251T Mueble bajo mesada | tarea en m2; insumo Alacena (6252) 1 ml | tarea en **ml**; insumo **6251 Mueble bajo mesada** 1 ml (estaba sin uso) |
| 6252T Alacena | tarea en m2 (insumo en ml) | tarea en **ml** |

- Insumo 6251 Mueble bajo mesada (estaba sin uso) — verificar precio en PUnitarios.

Rubro 17 terminado (2026-11-09).

## Rubro 18 — Carpintería metálica y herrería (desde 2026-11-09)

| Tarea | Antes | Después |
|---|---|---|
| 6112 / 6113 / 6114 Puertas metálicas ciegas de chapa (0,90 ext., 0,80 ext., 0,80 int.) | Oficial 4 / 4,26 / 4,26 h; sin ayudante ni mortero | Oficial **3 h** + Ayudante **2 h**; cemento **5 kg** + arena **0,01 m3** (= 6211) |
| 6115 / 6116 / 6117 Puerta balcón corrediza BWG 18 (1,80 / 2,10 / 2,40 x 2,00) | Oficial 6,4 h; sin ayudante ni mortero | Oficial **5 h** + Ayudante **3 h**; cemento **7 kg** + arena **0,015 m3** (= 6217) |
| 6118 Frente vidriado para locales | Oficial 2 h/m2; sin ayudante | Oficial **1 h** + Ayudante **1 h** por m2 (sin mortero: se fija con tornillos y sellador) |
| **6118T** Frente vidriado para locales (NUEVA) | no existía | Id DM0D, m2: Mat. y MdeO. (insumo nuevo 6T6118, Id 5FSM) 1 m2 |

- Insumo nuevo 6T6118 Mat. y MdeO. para Frente vidriado para locales, m2 — falta precio en PUnitarios.
| 6121 / 6123 / 6124 Ventanas corredizas (1,50x1,10 c/mosquitero, 1,50x1,10 y 1,80x1,10 simples) | Oficial 5 / 4 / 6 h (6124 con Ayudante 4 h); sin mortero | Oficial **3 h** + Ayudante **2 h**; cemento **5 kg** + arena **0,01 m3** (= puertas de marco metálico) |
| 6131 Ventiluz 6 hojas, 3 paños 2,00x0,90 | Oficial 6 h; sin ayudante ni mortero | Oficial **3,5 h** + Ayudante **2 h**; cemento **5 kg** + arena **0,01 m3** |
| 6134 Ventiluz 2 hojas 0,60x0,90 | Oficial 2 h; sin ayudante ni mortero | Oficial **1,5 h** + Ayudante **1 h**; cemento **3 kg** + arena **0,006 m3** (marco ≈ mitad) |
| 6141 Portón metálico corredizo | nombre sin medida; Oficial 8 h; sin ayudante ni mortero | nombre "**Portón metálico corredizo completo 3,00x3,00m.**"; Oficial **6 h** + Ayudante **6 h**; cemento **15 kg** + arena **0,03 m3** (amurado de riel y guía) |

Subrubro 18.a terminado.
| 6153 Reja recta simple en herrería | tarea en un (insumo en m2); sin MdeO ni mortero | tarea en **m2**; Oficial **1 h** + Ayudante **0,5 h**; cemento **2 kg** + arena **0,004 m3** por m2 |

Rubro 18 terminado (2026-11-09).

**Variantes T del rubro 18 (2026-11-09)** — creadas a pedido del usuario para todas las tareas que no tenían: 6112T, 6113T, 6114T, 6115T, 6116T, 6117T, 6121T, 6123T, 6124T, 6131T, 6134T, 6141T (un) y 6153T (m2). Cada una lleva 1 un/m2 de su insumo nuevo **6T<tarea>** "Mat. y MdeO. para <tarea>" (13 insumos nuevos, 6T6112 a 6T6153) — falta precio en PUnitarios. Ids de tarea DM0E-DM0P y DW01.

## Rubro 19 — Obras sanitarias (desde 2026-11-09)

| Tarea | Antes | Después |
|---|---|---|
| Agua fría y caliente | código 7103S con insumo de subcontrato total; insumo 7T7103 "…Distribución de Agua Fría" | código **7103T** (Id EG00 sin cambio); insumo 7T7103 renombrado "**Mat. y MdeO. para Agua fría y caliente**" |
| Artefactos y broncería | código 7105 (propia) con insumo de subcontrato total; insumo 7T7105 "…Desagues Cloacales" | código **7105T** (Id EG01 sin cambio); insumo 7T7105 renombrado "**Mat. y MdeO. para Artefactos y broncería**" |
| Equipo de bombeo | código 7106S con insumo de subcontrato total; insumo 7T7106 "…Desagues Pluviales" | código **7106T** (Id EG02 sin cambio); insumo 7T7106 renombrado "**Mat. y MdeO. para Equipo de bombeo**" |
| Instalaciones especiales | código 7107S con dos subcontratos (707120 MdeO + 7T7107 Mat. y MdeO.) | código **7107T** (Id EG03 sin cambio) solo con 7T7107 1 gl; sin variante S (usuario). Insumo 707120 queda sin uso |
| Distribución de agua caliente | código 7194S con insumo 7T7192 (alimentación a tanques) | código **7194T** (Id EG04 sin cambio) con insumo **7T7194** "Mat. y MdeO para Distribución de agua caliente" 1 ml (existía sin uso) |
| Alimentación a tanques, Bajada de tanques, Tanque de bombeo, Tanque de reserva | códigos 7192S, 7193S, 7195S, 7196S con insumos de subcontrato total | códigos **7192T, 7193T, 7195T, 7196T** (Id EG05-EG08 sin cambio); insumos sin cambio |

Subrubro 19.a terminado.
| Cámaras inspección, pozos negros, etc. | código 7108S con dos subcontratos (707130 MdeO + 7T7108 Mat. y MdeO.) | código **7108T** (Id EQ00 sin cambio) solo con 7T7108 1 gl. Insumo 707130 queda sin uso |

Subrubro 19.b terminado.
| Desagües pluviales y cloacales | código 7104S con insumo de subcontrato total; insumo 7T7104 "…Distribución de Agua Caliente" | código **7104T** (Id F000 sin cambio); insumo 7T7104 renombrado "**Mat. y MdeO. para Desagües pluviales y cloacales**" |

Subrubro 19.c terminado.
| 7165S Unidad Lavadero | sin subcontrato de MdeO; agua con caño HB 1/2" 6,5 ml + accesorios H.Br. 0,5 + soldadura estaño 0,15 kg + llave de paso H.Br. | + **Subcontrato MdeO Unidad Lavadero** (insumo nuevo 707165) 1 un; agua en **termofusión**: caño 20 mm 6,5 ml + accesorios termofusión 0,5 gl + llave de paso termofusión 1 un; sin soldadura |
| **7165T** Unidad Lavadero (NUEVA) | no existía | Id FA0E: Mat. y MdeO (7T7165, existía sin uso) 1 un |

**Criterio 19.d (usuario, 2026-11-09):** actualizar materiales antiguos — agua fría/caliente en termofusión (en lugar de HB/H.Br. + soldadura de estaño), desagües en PVC (en lugar de plomo y hierro fundido). Cada S lleva su subcontrato de MdeO (707xxx) y cada unidad tiene su T (7T7xxx).

- Insumos nuevos (falta precio en PUnitarios): 7114 Caño termofusión 20 mm (ml, Id 5L72), 7115 Caño termofusión 25 mm (ml, 5LAJ), 7170 Accesorios termofusión p/baño (gl, 5VZY), 7172 Accesorios termofusión p/cocina y lavadero (gl, 5WDU), 7192 Llave de paso termofusión 20 mm (un, 60MM), 707165 Subcontrato MdeO Unidad Lavadero (un, 5JNI).
| 7171S Unidad Baño completo | sin subcontrato de MdeO; HB 1/2" 19,6 ml + accesorios H.Br. 1 + llave de paso H.Br. 2 + soldadura estaño 0,08+0,35 kg; caño de plomo 1 1/2" 2,9 kg; PVC 1 1/2" 4,2 ml | + **Subcontrato MdeO Unidad Baño completo** (insumo nuevo 707171, Id 5JQZ) 1 un; **termofusión** 20 mm 19,6 ml + accesorios termofusión p/baño 1 gl + llave de paso termofusión 2 un; sin soldadura ni plomo; PVC 1 1/2" **5,2 ml** |
| Insumo 7131 Inodoro pedestal blanco | unidad gl | unidad **un** (insumo y las 3 incidencias) |
| **7171T** Unidad Baño completo (NUEVA) | no existía | Id FA0F: Mat. y MdeO (7T7171, existía sin uso) 1 un |

- Insumo nuevo 707171 Subcontrato MdeO Unidad Baño completo, un — falta precio en PUnitarios.
| 7172S Unidad Baño toilete | sin subcontrato de MdeO; jabonera c/agarradera; HB 1/2" 4 ml + llave H.Br. + soldadura 0,3+0,5 kg; HF 4" 3 ml, HF 3" 1 ml, plomo 11 kg, accesorios F.F. 3 gl | + **Subcontrato MdeO Unidad Baño toilete** (insumo nuevo 707172) 1 un; sin jabonera c/agarradera; **termofusión** 20 mm 4 ml + accesorios termofusión 0,2 gl + llave de paso termofusión 1; **PVC 4"** 3 ml, **PVC 2"** 1 ml, **PVC 1 1/2"** 2 ml, accesorios PVC p/baño **0,6 gl**; + accesorios colocación artefactos baño **0,4 gl** |
| **7172T** Unidad Baño toilete (NUEVA) | no existía | Mat. y MdeO (7T7172, existía sin uso) 1 un |

**Criterio 19.d desagües (2026-11-09):** HF 4" → PVC 4" (mismos ml), HF 3" → Caño PVC 2" (mismos ml), plomo → PVC 1 1/2", accesorios F.F. → accesorios PVC.

- Insumo nuevo 707172 Subcontrato MdeO Unidad Baño toilete, un — falta precio en PUnitarios.
| 7173S Unidad inodoro | sin subcontrato de MdeO; HB 1/2" 3 ml + llave H.Br. 0,25 + soldadura 0,2+0,2 kg; HF 4" 2 ml, plomo 7,6 kg, accesorios F.F. 2 gl | + **Subcontrato MdeO Unidad inodoro** (insumo nuevo 707173) 1 un; **termofusión** 20 mm 3 ml + accesorios 0,15 gl + llave de paso 0,25; **PVC 4" 2,5 ml** (plomo era la curva de 4"); accesorios PVC p/baño **0,3 gl**; + accesorios colocación artefactos **0,2 gl** |
| **7173T** Unidad inodoro (NUEVA) | no existía | Id FA0H: Mat. y MdeO (7T7173) 1 un |

- Insumo nuevo 707173 Subcontrato MdeO Unidad inodoro, un — falta precio en PUnitarios.
| 7174S Unidad mingitorio | sin subcontrato de MdeO; HB 1/2" 2 ml + llave H.Br. 0,25 + soldadura 0,2+0,2 kg; HF 3" 2 ml, plomo 11,4 kg, accesorios F.F. 2 gl | + **Subcontrato MdeO Unidad mingitorio** (insumo nuevo 707174) 1 un; **termofusión** 20 mm 2 ml + accesorios 0,1 gl + llave de paso 0,25; **PVC 2" 2 ml**, **PVC 1 1/2" 1,5 ml**, accesorios PVC p/baño **0,3 gl**; + accesorios colocación artefactos **0,2 gl** |
| **7174T** Unidad mingitorio (NUEVA) | no existía | Mat. y MdeO (7T7174) 1 un |

- Insumo nuevo 707174 Subcontrato MdeO Unidad mingitorio, un — falta precio en PUnitarios.
| 7175S Unidad ducha | sin subcontrato de MdeO; HB 1/2" 5 ml + llave H.Br. 0,5 + soldadura 0,3+0,25 kg; HF 3" 2 ml, plomo 15,2 kg, accesorios F.F. 2 gl | + **Subcontrato MdeO Unidad ducha** (insumo nuevo 707175) 1 un; **termofusión** 20 mm 5 ml + accesorios 0,25 gl + llave de paso 0,5; **PVC 2" 2 ml**, **PVC 1 1/2" 2 ml**, accesorios PVC p/baño **0,3 gl**; + accesorios colocación artefactos **0,2 gl** |
| **7175T** Unidad ducha (NUEVA) | no existía | Mat. y MdeO (7T7175) 1 un |

- Insumo nuevo 707175 Subcontrato MdeO Unidad ducha, un — falta precio en PUnitarios.
| 7176S Unidad bacha (de cocina) | mezclaba cocina y baño: bacha de cocina con grifería de lavatorio, jabonera, percha y rejilla de piso; HB 4 ml + llave H.Br. + soldadura; HF 3" 2 ml, plomo 8,2 kg, accesorios F.F. 2 gl; sin subcontrato | bacha de cocina: **grifería pileta de cocina** (7165); sin jabonera, percha ni rejilla; **termofusión** 20 mm 4 ml + accesorios termofusión p/cocina **0,3 gl** + llave de paso 0,5; **PVC 2" 2 ml**, **PVC 1 1/2" 1,5 ml**, accesorios PVC p/cocina **0,5 gl**, accesorios colocación cocina **0,5 gl**; + **Subcontrato MdeO Unidad bacha** (insumo nuevo 707176) 1 un |
| **7176T** Unidad bacha (NUEVA) | no existía | Mat. y MdeO (7T7176) 1 un |

- Insumo nuevo 707176 Subcontrato MdeO Unidad bacha, un — falta precio en PUnitarios.
| 7178S Unidad lavatorio | jabonera c/agarradera; sin llave de paso ni subcontrato; HB 1/2" 4 ml + soldadura 0,2+0,4 kg; HF 3" 2 ml, plomo 11,4 kg, accesorios F.F. 3 gl | **jabonera simple**; + **Subcontrato MdeO Unidad lavatorio** (insumo nuevo 707178) 1 un; **termofusión** 20 mm 4 ml + accesorios 0,2 gl + **llave de paso 0,5**; **PVC 2" 2 ml**, **PVC 1 1/2" 1,5 ml**, accesorios PVC p/baño **0,3 gl**; + accesorios colocación artefactos **0,2 gl** |
| **7178T** Unidad lavatorio (NUEVA) | no existía | Mat. y MdeO (7T7178) 1 un |

- Insumo nuevo 707178 Subcontrato MdeO Unidad lavatorio, un — falta precio en PUnitarios.
| 7179S Unidad Cocina | sin subcontrato de MdeO; HB 3/4" 1,2 ml + HB 1/2" 12,3 ml + accesorios H.Br. 1 gl + llave H.Br. 4 + soldadura 0,3 kg (desagüe ya en PVC) | + **Subcontrato MdeO Unidad Cocina** (insumo nuevo 707179) 1 un; **termofusión** 25 mm 1,2 ml + 20 mm 12,3 ml + accesorios termofusión p/cocina 1 gl + llave de paso 4; sin soldadura |
| **7179T** Unidad Cocina (NUEVA) | no existía | Mat. y MdeO (7T7179) 1 un |

- Insumo nuevo 707179 Subcontrato MdeO Unidad Cocina, un — falta precio en PUnitarios.
| Unidad cámara de inspección 60x60 | código 7183S con horas propias (Oficial 10 + Ayudante 12 h), sin subcontrato; artefacto = Cámara Séptica (7182); cemento 105 kg, arena 0,35, hidrófugo 2,1, cascote 0,1 | código **7183** propia (Id FA09 sin cambio): Oficial **3 h** + Ayudante **4 h**; insumo nuevo **7183 Cámara de inspección premoldeada 60x60 con marco y tapa** (Id 5ZGY); cemento **15 kg**, arena **0,04 m3**, cascote **0,05 m3**, sin hidrófugo (excavación aparte con 0255) |
| **7183S** (NUEVA) | no existía | Id FA0N: Subcontrato MdeO (insumo nuevo 707183, Id 7LX4) 1 un + mismos materiales |
| **7183T** (NUEVA) | no existía | Id FA0O: Mat. y MdeO (7T7183) 1 un |

- Insumos nuevos 7183 (cámara premoldeada) y 707183 (subcontrato) — falta precio en PUnitarios. Insumo 7182 Cámara Séptica queda sin uso.
| 7184S Unidad desagüe cloacal horizontal | tarea en un; PVC 2 1/2" 1,2 ml; sin subcontrato | tarea en **ml**; **PVC 4"** 1,2 ml (recibe inodoro); + **Subcontrato MdeO** (insumo nuevo 707184, ml) 1 ml; accesorios PVC 0,4 gl sin cambio |
| **7184T** (NUEVA) | no existía | ml: Mat. y MdeO (7T7184, unidad pasada de un a ml) 1 ml |

- Insumo nuevo 707184 Subcontrato MdeO Unidad desague cloacal horizontal, ml — falta precio en PUnitarios.
| 7185S Unidad desagüe cloacal vertical | tarea en un; HF 4" 1,1 ml + HF 3" 0,2 ml + accesorios F.F. 0,3 gl; sin subcontrato | tarea en **ml**; **PVC 4"** 1,1 ml + **PVC 2"** 0,2 ml + accesorios PVC 0,3 gl; + **Subcontrato MdeO** (insumo nuevo 707185, ml) 1 ml |
| **7185T** (NUEVA) | no existía | ml: Mat. y MdeO (7T7185, pasado a ml) 1 ml |

- Insumo nuevo 707185 Subcontrato MdeO Unidad desague cloacal vertical, ml — falta precio en PUnitarios.
| 7186S / 7187S Unidad desagüe pluvial horizontal / vertical | tarea en un; sin subcontrato (materiales ya en PVC 4") | tarea en **ml**; + **Subcontrato MdeO** (insumos nuevos 707186 / 707187, ml) 1 ml; materiales sin cambio |
| **7186T / 7187T** (NUEVAS) | no existían | ml: Mat. y MdeO (7T7186 / 7T7187, pasados a ml) 1 ml |

- Insumos nuevos 707186 y 707187 (ml) — falta precio en PUnitarios.

Subrubro 19.d terminado. Rubro 19 terminado (2026-11-09).

## Rubro 20 — Instalación de gas (desde 2026-11-09)

| Tarea | Antes | Después |
|---|---|---|
| 8330T Instalación de gas completa | insumo 8330 "Instalacion de Gas completa" | insumo 8330 renombrado "**Mat. y MdeO. para Instalación de gas completa**". Insumos 7T7310, 7T7320, 707310, 707320 siguen sin uso (se dejan) |
| 8331, 8332, 8333, 8335, 8337, 8338, 8339 Artefactos de gas (cocina, anafe, termotanques 90/150, calefón, estufas) | solo el artefacto, sin MdeO de conexión | + **Subcontrato gasista conexión de artefacto de gas** (insumo nuevo 808330, común a todos) 1 un |
| Insumo 8331 Cocina | "hornalllas … parilla" | "Cocina blanca tres **hornallas** con horno y **parrilla**." |

- Insumo nuevo 808330 Subcontrato gasista conexión de artefacto de gas, un — falta precio en PUnitarios.
| 8341 Medidor de gas | tarea "Medidores de Gas" (un) con insumo en gl | tarea e insumo "**Medidor de gas**"; insumo en **un** (cargo de conexión por medidor; sin MdeO, lo coloca la distribuidora) |

Rubro 20 terminado (2026-11-09).

## Rubro 21 — Instalación eléctrica (desde 2026-11-09)

| Tarea | Antes | Después |
|---|---|---|
| 8200T Instalación eléctrica completa | insumo 8200 "Subcontrato Instalación Eléctrica" | insumo 8200 renombrado "**Mat. y MdeO. para Instalación eléctrica completa**". Insumo duplicado 8T0000 sigue sin uso (se deja) |
| 8241T Medidor eléctrico | tarea "Medidores Electricos" (un) con insumo en gl | tarea e insumo "**Medidor eléctrico**"; insumo en **un** (cargo de conexión por medidor) |
| 8251T Toma de Energía | — | sin cambio (8T7202 duplicado sigue sin uso) |
| Tareas fuera de su subrubro | 8281T Tablero General en 21.a (Id G403); 8282T Tablero Secundario en 21.b (GE02); 8263T Artefactos en 21.e (L400) | 8281T y 8282T movidas a **21.e Tableros y protecciones**; 8263T movida a **21.d Artefactos**. Cambian los Id (ver tabla de Ids nuevos abajo); código y contenido sin cambio |

- Ids nuevos: 8263T **GY00** (antes L400), 8281T **L400** (antes G403), 8282T **L401** (antes GE02). Ojo: L400 pasó de Artefactos a Tablero General.
| 8271T / 8272T Boca de iluminación vivienda / fábrica | — | sin cambio (8T7205 / 8T7206 duplicados siguen sin uso) |
| 8252T Instalación telefónica | tarea e insumo 8T8252 "Instalación Telefónica" | "**Instalación de telefonía y datos.**" (tarea e insumo) |
| 8264T Luces emergencia | tarea e insumo 8T8264 en gl | "**Luz de emergencia**", tarea e insumo en **un** (por equipo) |
| 8253T, 8254T, 8260T, 8261T, 8262T | — | sin cambio |

Subrubro 21.c terminado.
| 8263T Artefactos | tarea e insumo "Artefactos" | "**Artefactos de iluminación**" (tarea e insumo 8T8263), gl |
| 8281T / 8282T Tablero General / Secundario | — | sin cambio de contenido (solo movidas a 21.e) |

Rubro 21 terminado (2026-11-09).

---
**Fin de sesión 2026-11-09.** Copia: `Costos/Data/Master_FINAL_cierre_2026-11-09.db` (689 tareas, 2672 incidencias, sincronizadas). Se retoma por el rubro 22 Calefacción.
