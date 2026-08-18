# Bibliométrico

> Aplicación de escritorio para análisis bibliométrico de exportaciones CSV de Scopus y Web of Science.

Desarrollada en Python con interfaz gráfica Tkinter, permite a investigadores explorar métricas de productividad e impacto de un corpus de publicaciones científicas sin necesidad de escribir código.

---

## Funcionalidades

| Módulo | Descripción |
|---|---|
| **Carga de datos** | Importa CSV de Scopus/WoS con previsualización y validación de columnas |
| **Métricas generales** | Total de publicaciones, autores únicos y artículos de un solo autor |
| **Estadísticas de autoría** | Mínimo, máximo y promedio de autores por artículo |
| **Universidades** | Lista por frecuencia con filtro por país y detalle de artículos |
| **Lista de países** | Países contribuyentes ordenados por número de publicaciones |
| **Trabajos más citados** | Lista APA completa ordenada por citas, con búsqueda integrada |
| **Promedio anual de citas** | Impacto normalizado por año de publicación |
| **Top 10 autores** | Autores más productivos con detalle de artículos |
| **Top 10 universidades** | Instituciones con mayor presencia, incluyendo país de origen |
| **Top 10 países** | Ranking con porcentaje sobre el total del corpus |
| **Top 10 trabajos** | Artículos más citados con DOI accesible |
| **Exportación** | Exporta cualquier resultado a Word (.docx) o Excel (.xlsx) |
| **Gestión de proyectos** | Guarda, abre y administra análisis de forma independiente |

---

## 🛠️ Stack

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-informational?style=flat-square)
![pandas](https://img.shields.io/badge/pandas-data-150458?style=flat-square&logo=pandas&logoColor=white)

| Librería | Propósito |
|---|---|
| `tkinter` | Interfaz gráfica de escritorio (incluida en Python) |
| `pandas` | Lectura y procesamiento del CSV |
| `python-docx` | Exportación a Word (.docx) |
| `openpyxl` | Exportación a Excel (.xlsx) |
| `collections` | Conteos de frecuencia |
| `re` | Extracción de países e instituciones desde el campo Affiliations |

---

## Instalación

### Requisitos previos

- Python 3.13 instalado en el sistema

### 1. Clona el repositorio

```bash
git clone https://github.com/lenivyy03/bibliometrico.git
cd bibliometrico
```

### 2. Instala las dependencias

```bash
pip install pandas python-docx openpyxl
```

### 3. Ejecuta la aplicación

```bash
python main.py
```

---

## Formato del archivo CSV

La aplicación acepta exportaciones directas de **Scopus** o **Web of Science**. El archivo debe contener las siguientes columnas:

```
Authors | Title | Year | Source title | Volume | Issue | Page start | Page end | DOI | Cited by | Affiliations | Art. No.
```

> Las columnas faltantes no impiden la carga — la aplicación indica qué métricas quedarán deshabilitadas.

---

## 📖 Uso básico

1. Abre la aplicación con `python main.py`
2. Haz clic en **Cargar archivo CSV** y selecciona tu exportación de Scopus
3. Confirma la carga tras previsualizar las primeras filas
4. Navega por el panel lateral para explorar cada módulo de análisis
5. Usa el botón **Exportar** en cualquier vista para generar un informe en Word o Excel

---

## Equipo

Proyecto desarrollado para la materia **Ingeniería de Software I**  
Universidad de Sonora · Semestre 2026-1  
Profesor: Gabriel Alberto García Mireles

| Integrante | GitHub | Módulos |
|---|---|---|
| Ángel David Ortega Félix | [@lenivyy03](https://github.com/lenivyy03) | Carga de datos · Trabajos citados · Gestión de proyectos |
| Daniel Leinad Domínguez Calvario | — | Conteo de publicaciones · Promedio anual · Exportación |
| María Fernanda Hernández García | — | Estadísticas de autoría · Top autores · Exportación |
| Marco Antonio Tadeo Munro Flores | — | Lista de países · Top trabajos · Gestión de proyectos |
| Mario Alberto Ocejo Quijada | — | Universidades · Top universidades · Top países |

---

## Documentación

- [`docs/ERS.pdf`](docs/) — Especificación de Requisitos de Software
- [`docs/Casos_de_Prueba.docx`](docs/) — 60 casos de prueba de aceptación (PA-01 a PA-60)

---

<p align="center">
  Hecho con Python · Universidad de Sonora · 2026
</p>
