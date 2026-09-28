# CONTEXT.md — Eyes-Backend (las manos)

Contexto completo del proyecto para agentes de IA. Cubre este repo Y el repo hermano (`Eyes`).
Última actualización: 2026-09-27 (añadidos eventos y heartbeat)

## Visión

**Eyes** es una herramienta de escritorio, de uso personal o de desarrollador, para dos cosas:

1. **Web scraping** con foco en páginas dinámicas (React/Angular, HTML inicial mínimo).
2. **Detección de vulnerabilidades en redes propias**, con foco en experiencia de usuario.

### Uso ético (importante)
La herramienta está pensada **exclusivamente para software y redes propios del usuario**. No implementar ni proponer evasión de anti-bot, CAPTCHAs u otras protecciones de sitios que no son del usuario, ni técnicas contra redes ajenas.

### Problema que resuelve
Las herramientas actuales son fragmentadas, engorrosas, requieren instalaciones pesadas y no guían al usuario. Eyes apuesta por ser ligera, fácil de entender y didáctica: el usuario debe **entender** lo que pasa, no que se lo den resuelto.

## Filosofía de diseño

- **El sistema nunca decide por el usuario, pero reduce la carga cognitiva** necesaria para que decida bien.
- **Sin IA/LLM en el producto.** Heurísticas y reglas escritas a mano. (La IA se usa solo como ayuda de desarrollo.)
- **Ligereza de recursos.** No asumir que el usuario tiene una máquina potente.
- **Proporcionalidad de la ayuda:** en scraping solo señales; en redes (dominio plural y complejo) el sistema puede alertar y recomendar más, con reglas y bases de vulnerabilidades conocidas (tipo CVE).

## Arquitectura: el cuerpo y las manos

```
┌──────────────────────── Eyes (repo hermano) ────────────────────────────┐
│  React (WebView)  ── ojos y cara: UI, Zod                               │
│  Rust / Tauri     ── sistema nervioso: ciclo de vida, permisos,         │
│                      datos del usuario, token de sesión                  │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │  HTTP local (127.0.0.1) + token
┌─────────────────────────────────▼───────────────────────────────────────┐
│  Eyes-Backend (ESTE repo) — las manos                                    │
│  FastAPI + Playwright/Selenium (scraping) + Nmap/Wireshark (redes)      │
└──────────────────────────────────────────────────────────────────────────┘
```

Reglas de la relación:
- La app de escritorio **lanza y mata** este backend (sidecar). No existe fuera de la app.
- El frontend llama a este backend **directo por `fetch`**.
- Este backend **no tiene voluntad propia** ni **datos del usuario**. Mínimo privilegio.
- Los resultados que entrega los persiste el lado Tauri; aquí solo hay un búfer temporal de trabajo (escritura incremental para no perder progreso si algo falla).

## Por qué un proceso Python separado (y no PyO3 ni DLL)

- Playwright y Selenium necesitan el intérprete de Python corriendo; no existe una forma de tener sus capacidades sin el runtime.
- PyO3 embebido mezcla el ciclo de vida de dos runtimes: un crash de Python tumbaría toda la app.
- Python no se compila a una DLL ligera con funciones exportables mediante PyInstaller.
- Proceso separado + HTTP local da aislamiento de fallos, un canal maduro y una implementación simple.

## Flujo del eje de scraping (lo que este backend soporta)

1. Request HTTP crudo (ligero, sin navegador) y devolver el HTML.
2. Un **filtro ligero** resalta señales de página dinámica: tamaño del HTML, contenedores vacíos tipo `<div id="root">`, scripts de bundler, ausencia de texto real.
3. Solo si el usuario lo ordena, se activa el **modo navegador** (Playwright/Selenium) para renderizar JS.
4. Se extraen y devuelven los datos.

## Eje de redes

El desarrollador no tiene experiencia previa en redes y aprende mientras construye. Las reglas de análisis se escriben a mano y se apoyan en bases de vulnerabilidades conocidas. Las herramientas previstas (Nmap, Wireshark) son fragmentadas de por sí; el valor de Eyes es integrarlas y explicarlas de forma guiada y ligera.

## Eventos, logs y heartbeat (lo que este backend debe hacer)

**Principio:** los logs son memoria y viven en el cuerpo (app de escritorio). Este backend **no guarda logs**: solo reporta.

- **Emitir cada evento como una línea JSON por salida estándar.** La app de escritorio la captura, la registra y la muestra. No hay endpoint ni puerto adicional para logs.
- **Formato:** `ts`, `nivel` (info/warning/error), `modulo`, `evento` (nombre corto y fijo), `mensaje` (legible), `detalle` opcional.
- **Reglas de contenido:** registrar qué se hizo, no el contenido obtenido (URL sí, cuerpo de la página no; credenciales nunca). El token de sesión jamás aparece.
- **Evento `backend_listo`:** emitirlo al terminar de levantar FastAPI y empezar a escuchar; es la señal de que la app ya puede llamar a la API.
- **`/health` ligero:** la app lo consulta cada pocos segundos como heartbeat. Debe devolver un JSON mínimo y no depender de nada pesado (ni navegador ni red). El trabajo pesado no debe bloquear la atención de `/health`, o la app lo tomará como una caída falsa.
- **Sin auto-reinicio ni recuperación propia:** si el backend cae, la app avisa al usuario y este decide. A revisar con escenarios reales.

Implementación prevista después del Sprint 0. Lo único que se fija desde ya es el formato de evento.

## Stack de este repo

| Pieza | Elección |
|---|---|
| Lenguaje | Python 3.14 |
| Entorno y paquetes | uv |
| Servidor | FastAPI + Uvicorn |
| Automatización | Playwright, Selenium |
| Layout | `src/eyes_backend/` |
| Empaquetado futuro | Nuitka (candidato) o PyInstaller, como sidecar de Tauri (inclinación: one-dir) |

## Contrato con el frontend (borrador)

- Base: `http://127.0.0.1:<puerto>` (puerto dinámico objetivo; en desarrollo, 8000).
- Autenticación: token de sesión por arranque (nombre del header por definir).
- Endpoints actuales: `GET /` y `GET /health`.
- Endpoints previstos: `/scrape`, `/scan`, `/status`, `/results`.
- Los esquemas de respuesta deben ser estables: el frontend los valida con Zod.
- Cualquier cambio de contrato se refleja en el `CONTEXT.md` de **ambos** repos.

## Estado actual

- ✅ Proyecto `eyes-backend` inicializado con uv (layout `src/`, paquete `eyes_backend`).
- ✅ Instalados: fastapi, uvicorn, playwright, selenium. Navegadores de Playwright descargados.
- ✅ Servidor levanta con `uv run uvicorn eyes_backend.main:app --reload`.
- ⬜ Estructura por módulos con registro por decorador.
- ⬜ Blindaje (127.0.0.1 fijo, CORS, token).
- ⬜ Endpoints reales de scraping/redes.

## Sprint 0 — parte del backend

- Estructura modular: cada capacidad es una clase decorada que se registra sola; el enrutador la expone sin editar un archivo central.
- Endpoints mínimos: `/health` y un módulo de prueba registrado con el decorador.
- Blindaje básico: enlace a `127.0.0.1`, CORS restrictivo, diseño del token.

## Notas de entorno

- Windows. Python 3.14 es muy reciente: si una librería con extensiones nativas falla, sospechar primero de compatibilidad de versión.
- El proyecto uv usa layout `src/`; por eso se importa `eyes_backend.main:app`.
- `[project.scripts]` en `pyproject.toml` trae un script `eyes-backend` de plantilla, sin uso por ahora.

## Preferencias del desarrollador (para tus respuestas)

- Idioma: español.
- Prefiere explicaciones que enseñen el porqué, no solo el resultado.
- Prefiere que se le planteen las decisiones para pensarlas él antes de recibir una recomendación cerrada.
- Es autodidacta en redes: explicar conceptos de red con claridad, sin asumir conocimiento previo.
