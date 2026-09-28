# DECISIONS.md — Eyes-Backend (las manos)

Registro de decisiones de arquitectura (formato ADR corto).
Estados: **Aceptada** · **Pendiente** · **Reemplazada**.
Regla: toda decisión de diseño nueva se agrega aquí. Si una decisión cambia, no se borra: se marca como Reemplazada y se enlaza la nueva.
Las decisiones compartidas con el frontend están en `DECISIONS.md` del repo `Eyes`; aquí se resumen las que afectan a este backend.

---

## B-001 — Backend Python separado, comunicado por HTTP local
**Estado:** Aceptada (equivale a D-002 y D-003 en `Eyes`)
**Contexto:** Se quiere usar Selenium/Playwright sin reescribirlos en Rust.
**Alternativas descartadas:** PyO3 embebido (frágil, un crash de Python tumba la app); inyección de DLL (Python no se compila a una DLL ligera con funciones exportables).
**Decisión:** Proceso independiente con FastAPI; el frontend le habla directo por `fetch`.
**Consecuencias:** Aislamiento de fallos y canal maduro. Dos runtimes que empaquetar.

## B-002 — Este backend son "las manos"
**Estado:** Aceptada (equivale a D-004)
**Decisión:** Sin voluntad propia; solo ejecuta órdenes y devuelve resultados. No accede a datos del usuario. Solo mantiene un búfer temporal de trabajo con escritura incremental. La app de escritorio controla su ciclo de vida.

## B-003 — Blindaje de la API local
**Estado:** Parcialmente decidida (equivale a D-005)
**Decisión:** Enlace explícito a `127.0.0.1`; CORS restrictivo; token de sesión aleatorio por arranque; puerto dinámico.
**Pendiente:** nombre del header, mecanismo por el que Tauri entrega token y puerto (argumento de línea de comandos o variable de entorno).
**Motivo:** Con localhost solo procesos de la misma máquina pueden conectarse, pero otro programa local o una página web maliciosa en el navegador aún podría intentarlo; el token y el CORS lo cierran.

## B-004 — Gestión de entorno con uv
**Estado:** Aceptada
**Decisión:** uv para dependencias y entorno (`pyproject.toml` + `uv.lock`); se ejecuta todo con `uv run`. Sin `requirements.txt` ni venv manual.

## B-005 — Layout `src/` y punto de entrada
**Estado:** Aceptada
**Contexto:** `uv init` generó un paquete con layout `src/`; el archivo real está en `src/eyes_backend/main.py`.
**Decisión:** Mantener el layout `src/` (práctica moderna que evita bugs sutiles de import). El servidor se lanza con `eyes_backend.main:app`.

## B-006 — Patrón de módulos por registro con decoradores
**Estado:** Aceptada (implementación pendiente, Sprint 0 issues #7 y #8)
**Contexto:** No se quiere concentrar las rutas en un solo archivo; cada capacidad debe ser una rama más.
**Decisión:** Cada módulo es una clase decorada que se registra sola en un registro central; el enrutador expone los módulos sin editar `main.py`. Equivale al Component Registry usado en App-2027.
**Nota:** En Python se usan decoradores (`@algo`), no anotaciones.

## B-007 — Sin IA/LLM
**Estado:** Aceptada (equivale a D-006)
**Decisión:** Ni APIs de IA ni modelos embebidos. Lógica determinista, heurísticas y reglas escritas a mano, apoyadas en bases de vulnerabilidades conocidas (tipo CVE) para redes.

## B-008 — Scraping: request crudo primero, navegador solo bajo orden
**Estado:** Aceptada (equivale a D-008)
**Decisión:** El backend ofrece primero la petición HTTP cruda, más el filtro ligero de señales de página dinámica. El modo navegador (Playwright/Selenium) solo se ejecuta si el usuario lo pide, por costo de recursos.

## B-009 — Uso ético
**Estado:** Aceptada (equivale a D-009)
**Decisión:** Solo objetivos propios del usuario. No se implementa evasión de anti-bot ni de protecciones de terceros, ni técnicas contra redes ajenas.

## B-010 — API pequeña y enfocada
**Estado:** Aceptada
**Decisión:** Pocos endpoints (`/scrape`, `/scan`, `/status`, `/results`). Sin GraphQL, sin base de datos propia, sin cuentas. Es una herramienta de orquestación, no un servicio completo.

## B-011 — Empaquetado como sidecar
**Estado:** Pendiente (pospuesta a propósito; equivale a D-013)
**Candidato:** Nuitka (compila a nativo, arranque más rápido, mejor protección del código) sobre PyInstaller.
**Restricciones conocidas:** sin cross-compilation (compilar en cada SO); el binario debe nombrarse con sufijo de target triple; Playwright/Selenium pueden requerir flags de inclusión al compilar.
**Nota:** No se decide hasta tener algo real que empaquetar.

## B-012 — Versión de Python
**Estado:** Aceptada, con vigilancia
**Decisión:** Python 3.14 (`requires-python = ">=3.14"`).
**Riesgo:** versión muy reciente; ante fallos de librerías con extensiones nativas, revisar compatibilidad de versión primero.

## B-013 — El backend reporta eventos por salida estándar
**Estado:** Aceptada (implementación pendiente; equivale a D-016, D-017 y D-018 en `Eyes`)
**Decisión:** El backend no guarda logs. Emite cada evento como una línea JSON en stdout, y la app de escritorio la captura, la registra y la muestra. Esto no abre ningún puerto ni endpoint adicional.
**Formato:** `ts`, `nivel` (info/warning/error), `modulo`, `evento` (nombre corto y fijo), `mensaje` (legible), `detalle` opcional.
**Reglas de contenido:** registrar qué se hizo, no el contenido obtenido (URL sí, cuerpo de la página no; credenciales nunca). El token de sesión jamás aparece en un evento.
**Motivo de stdout:** los eventos llegan mientras ocurren, aunque el proceso falle después.

## B-014 — Evento `backend_listo` como señal de arranque
**Estado:** Aceptada (equivale a D-021)
**Decisión:** Al terminar de levantar FastAPI y empezar a escuchar, el backend emite el evento `backend_listo`. La app lo usa como señal de que ya se puede llamar a la API.

## B-015 — `/health` ligero y siempre disponible
**Estado:** Aceptada (equivale a D-021)
**Decisión:** La app hace ping periódico a `/health` como heartbeat. Este endpoint debe devolver un JSON mínimo y **no depender de nada pesado**: no toca el navegador ni la red. Si el trabajo de scraping bloquea el servidor y `/health` deja de responder, la app lo tomaría como una caída falsa.
**Consecuencia de diseño:** el trabajo pesado debe ejecutarse de forma que no impida atender `/health` (por ejemplo, tareas en segundo plano o hilos/procesos aparte), no en el hilo que atiende las peticiones.

## B-016 — Ante una caída, no hay auto-reinicio
**Estado:** Aceptada, a revisar con escenarios reales (equivale a D-022)
**Decisión:** El backend no se reinicia solo ni tiene lógica de recuperación propia. Si cae, la app avisa al usuario y este decide.
