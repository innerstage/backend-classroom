# I. Análisis Exploratorio de Datos

Para comenzar el proceso de escribir scripts de ETL, realizaremos un análisis exploratorio de datos para familiarizarnos con la data. En esta etapa necesitamos contestar varias preguntas:

* ¿Cuántos archivos tengo?
* ¿Qué formato poseen? ¿Están en el mismo formato?
* ¿Los formatos pueden ser leídos directamente por `pandas`?
* ¿Cuántas filas y columnas posee cada archivo?
* ¿Qué tipos de dato posee cada columna? ¿Son consistentes?
* ¿Tenemos valores nulos (`NaN`) en ciertas columnas? ¿Cuál es la mejor estrategia para este conjunto de datos?
* ¿Los archivos se encuentran en formato Tidy? Si no, ¿Qué operaciones debo efectuar para que lo esté?

Estas respuestas se encuentran en el Jupyter Notebook llamado `analisis_exploratorio.ipynb`, si clonaste este repositorio, te recomiendo crear un entorno virtual de Python primero y ejecutar Jupyter Notebook desde ahí (Los comandos en Windows no están testeados).


<details>
<summary>Linux/MacOS</summary>

```bash
cd etl-classroom
virtualenv -p python3 venv
source venv/bin/activate
jupyter-notebook
```
</details>

<details>
<summary>Windows</summary>

```bash
cd etl-classroom
conda create --name venv python=3.6
activate venv
jupyter-notebook
```
</details>