# AGENTS.md — Eyes-Backend (las manos)

Instrucciones para agentes de IA (OpenCode, Antigravity, etc.) que trabajen en este repo.
Lee primero `CONTEXT.md` y `DECISIONS.md`. Este archivo dice CÓMO trabajar; los otros dicen QUÉ es el proyecto y POR QUÉ.

## Qué es este repo

Backend de módulos de **Eyes**: un servidor FastAPI que ejecuta scraping (Playwright/Selenium) y análisis de red (Nmap/Wireshark) cuando la app de escritorio se lo ordena.
La app de escritorio (Tauri + React) vive en el repo hermano `Eyes`. Este backend son **las manos**: ejecuta, no decide.

## Stack y versiones

- Python 3.14 (`requires-python = ">=3.14"`)
- Gestor de paquetes y entorno: **uv** (no pip, no venv manual)
- FastAPI + Uvicorn
- Playwright y Selenium para automatización de navegador
- Layout `src/`: el paquete es `eyes_backend` en `src/eyes_backend/`
- Build backend: `uv_build`
- Sistema de desarrollo: Windows

## Comandos

```bash
uv add <paquete>                                  # agregar dependencia
uv sync                                           # sincronizar entorno
uv run playwright install                         # binarios de navegadores
uv run uvicorn eyes_backend.main:app --reload     # servidor de desarrollo
```

Nota: el módulo se importa como `eyes_backend.main:app`, no `main:app`.

## Reglas de arquitectura (no negociables)

1. **Este backend no tiene voluntad propia.** Solo ejecuta la orden recibida y devuelve el resultado. No inicia tareas por su cuenta.
2. **No accede ni guarda datos del usuario** (cuentas, configuración, historial, base de datos del usuario). Solo puede mantener un **búfer temporal de trabajo** del scraping/escaneo en curso.
3. **El ciclo de vida lo controla la app de escritorio.** Este servidor no debe diseñarse como servicio independiente que siga corriendo por su cuenta.
4. **Enlace solo a `127.0.0.1`.** Nunca `0.0.0.0`. Fijarlo explícitamente en el código de arranque.
5. **Toda petición requiere el token de sesión** (header por definir) que la app entrega en cada arranque; sin token, responder 401.
6. **CORS restrictivo:** no permitir orígenes web arbitrarios.
7. **Sin IA/LLM.** Ni llamadas a APIs de IA ni modelos embebidos. Solo lógica determinista y reglas.
8. **Uso ético:** solo objetivos propios del usuario. No implementar evasión de anti-bot, CAPTCHAs ni técnicas contra sitios o redes de terceros.
9. **Ligereza.** El modo navegador (Playwright/Selenium) es costoso: solo se activa cuando el usuario lo pide explícitamente.

## Patrón de módulos (objetivo del Sprint 0)

Cada capacidad (un módulo de scraping, un módulo de red) es una **clase decorada** que se **registra sola** en un registro central; el enrutador expone cada módulo como una rama de la API sin editar un archivo central.

- Agregar un módulo nuevo = crear una clase decorada. No se modifica `main.py`.
- Es el mismo concepto que un Component Registry.
- En Python esto se hace con decoradores (`@algo`), no con anotaciones.

## Convenciones de código

- Type hints en todo. Modelos de entrada/salida con Pydantic.
- Un endpoint = una responsabilidad; nada de lógica de negocio dentro del handler, va en el módulo.
- Respuestas con esquema estable: el frontend las valida con Zod, así que cambiar un esquema es cambiar el contrato.
- Errores: devolver errores estructurados y claros, nunca dejar que un fallo de scraping tumbe el servidor.
- Escritura incremental del búfer de trabajo: no acumular todo en memoria hasta el final.

## Qué NO hacer

- No agregar una base de datos de usuario ni persistencia permanente aquí.
- No exponer endpoints que devuelvan configuración o datos del usuario.
- No enlazar a interfaces distintas de localhost.
- No introducir GraphQL ni una API amplia: esto es una herramienta para orquestar Selenium/Playwright y herramientas de red, con pocos endpoints.
- No agregar dependencias pesadas sin registrarlo en `DECISIONS.md`.

## Antes de dar por terminada una tarea

1. El servidor arranca con `uv run uvicorn eyes_backend.main:app --reload` sin errores.
2. Si cambió un endpoint o un esquema, actualizar la sección "Contrato" de `CONTEXT.md` en AMBOS repos.
3. Si se tomó una decisión de diseño, registrarla en `DECISIONS.md`.

## Estado del proyecto

Ver la sección "Estado actual" de `CONTEXT.md`.
