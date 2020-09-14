# El Esquema de Tesseract

Con la data necesaria ingestada correctamente en la base de datos, podemos escribir el esquema de Tesseract con ayuda de nuestro modelo relacional. El esquema es un archivo `xml` o `json` que define la estructura del cubo OLAP para que Tesseract pueda interpretarlo y retornar los datos correspondientes al hacer diferentes drilldowns o cortes. La estructura del esquema es sencilla y debe incluir:

* Schema (name)
    * Cube (name)
        * Table (name): Para la tabla de hechos.
        * Dimension (name, foreign_key): Para cada dimensión.
            * Hierarchy (hasAll)
                * Table (name): Para la tabla de dimensión específica.
                * Level (name, key_column, name_column, key_type): Para cada nivel de la jerarquía.
                * InlineTable (alias)
                    * ColumnDefs -> ColumnDef (name, type)
                    * Rows -> Row
                        * Value (column)
        * Measure (name, column, aggregator, visible)


En los niveles, sólo se incluye `key_type` cuando la columna es de texto. El esquema para nuestro caso de estudio se encuentra en `schema.xml`, sin embargo, no ha sido testeado y puede tener errores al implementarlo. Al tener el esquema en el servidor correspondiente y reiniciar Tesseract, podremos realizar queries con drilldowns y cortes, y el proceso de ETL habrá finalizado.