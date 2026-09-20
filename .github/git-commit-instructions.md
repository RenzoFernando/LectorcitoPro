# git-commit-instructions.md

---

## Formato del commit

type: short description

### Ejemplos válidos

- feat: add login endpoint
- fix: validate jwt token
- docs: update setup instructions
- test: add user service tests
- refactor: simplify auth middleware
- chore: add gitignore file

## Tipos permitidos

- feat: nueva funcionalidad
- fix: corrección de error
- docs: cambios en documentación
- test: pruebas unitarias o de integración
- refactor: mejora interna sin cambiar comportamiento esperado
- chore: tareas de mantenimiento o configuración
- style: cambios de formato sin alterar lógica
- build: cambios relacionados con build o dependencias
- perf: mejora de rendimiento

## Reglas para la descripción

1. Usar verbo en presente:
    - add
    - update
    - remove
    - fix
    - create
    - validate
2. No terminar con punto final.
3. Debe describir el cambio principal, no una historia larga.
4. Idealmente mantenerla entre 2 y 10 palabras.

## Ejemplos recomendados para este proyecto

### Configuración inicial

chore: initialize typescript project
build: add express dependencies
chore: add environment configuration

### Usuarios

feat: add user model
feat: create user controller
feat: add user crud routes
fix: validate user email uniqueness
test: add user integration tests

### Autenticación

feat: add login service
feat: generate jwt token
fix: protect private routes
refactor: simplify auth validation
test: add auth middleware tests

### Módulos del dominio

feat: add vault model
feat: add transaction endpoints
fix: validate vault ownership
test: add transaction service tests

### Documentación

docs: add postman usage guide
docs: update readme deployment section

## Plantilla rápida

- feat: add ...
- fix: fix ...
- docs: update ...
- test: add ...
- refactor: improve ...
- chore: configure ...

## Decisión final

- Idioma de commits: English
- Formato obligatorio: type: short description

---
