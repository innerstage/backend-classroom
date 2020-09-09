# El Pipeline de Bamboo

Bamboo o `bamboo-lib` es una librería de Python desarrollada en Datawheel por @jspeis, con el objetivo de estandarizar la forma en que escribimos ETL. El formato específico de un pipeline de Bamboo permite identificar fácilmente los pasos que se están llevando a cabo, y posee poderosas clases especiales como `ExtractStep` o `LoadStep` que entablan una conexión con fuentes de datos online, y bases de datos online o locales, evitando tener que escribir estas conexiones manualmente en un script de Python, para utilizarlos sólo se requiere un archivo de conexiones bien configurado (`conns.yaml`) que puede incluir variables de entorno.

<img src="img/bamboo_parts.png" style="border:2px">

Como se puede ver en este diagrama, la fuente de datos puede ser online o local, una carpeta con archivos en tu disco duro, archivos en Google Cloud, una API, etc. Los datos transformados se pueden ingestar en cualquier base de datos soportada por Bamboo (PostgreSQL, MonetDB y ClickHouse).