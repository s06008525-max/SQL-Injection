# Tarea.- Seguridad y Vulnerabilidades en Bases de Datos: SQL Injection

**Instituto Politécnico Nacional - ESCOM** **Ingeniería en Inteligencia Artificial (3er Semestre)** **Alumnos:** Calvario Santiago Derek  
Barrios Torres Jesús Alfonso
**Aguilar López Minerva
 

## 1. ¿Qué es SQL Injection (SQLi)?
La inyección SQL es una vulnerabilidad de seguridad web que permite a un atacante interferir en las consultas que una aplicación realiza a su base de datos. Ocurre cuando los datos ingresados por el usuario se concatenan directamente en la consulta SQL sin ser validados o sanitizados previamente. Esto permite alterar la lógica booleana de la instrucción o ejecutar comandos arbitrarios (como la eliminación de tablas o extracción de información sensible).

## 2. Descripción de la Demostración Práctica
Para esta investigación, se implementó un entorno contenedorizado con Docker que levanta una API en FastAPI. El sistema divide la arquitectura en dos bases de datos SQLite independientes para contrastar directamente las malas y buenas prácticas de seguridad.

### 🔴 Entorno Vulnerable (vulnerable.db)
Simula un sistema con brechas de seguridad críticas:
* **Concatenación Directa:** El código utiliza `f-strings` en Python para insertar los inputs directamente en el `SELECT`.
* **Almacenamiento en Texto Plano:** Las contraseñas de los usuarios se guardan sin ningún tipo de cifrado.
* **Ataque de Evasión de Autenticación:** Al ingresar el payload `admin' --`, el comentario (`--`) anula la comprobación de la contraseña, permitiendo el acceso.
* **Ataque de Destrucción (Stacked Queries):** Al ingresar `admin'; DROP TABLE users; --`, la aplicación ejecuta ambas sentencias, eliminando la tabla completa de la base de datos y simulando una pérdida total de información.

### 🟢 Entorno Seguro (seguro.db)
Implementa las contramedidas estándar de la industria:
* **Consultas Parametrizadas (Prepared Statements):** Se utilizan marcadores de posición (`?`). El motor de la base de datos compila la estructura SQL antes de insertar los datos, tratando cualquier intento de inyección estrictamente como una cadena de texto inofensiva.
* **Hashing Criptográfico:** Las contraseñas se almacenan utilizando el algoritmo de hash SHA-256 (`hashlib.sha256`). Si la base de datos es expuesta, las contraseñas originales permanecen ilegibles.
* **Aislamiento de Configuración (.env):** Las credenciales de conexión al motor de la base de datos no están hardcodeadas en el código fuente, sino que se inyectan a través de variables de entorno para prevenir fugas de información.

## 3. Guía de Ejecución
Para correr de forma local, es necesario contar con Docker y Docker Compose instalados.

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/s06008525-max/SQL-Injection.git](https://github.com/s06008525-max/SQL-Injection.git)
   cd SQL-Injection
   ```
2. Ejecutar el siguiente comando en la raíz del proyecto para construir y levantar el contenedor:
   ```bash
   docker compose up --build
   ```
3. Acceder desde el navegador web a `http://localhost:8000`.
4. Seguir las instrucciones en pantalla para probar los payloads en ambos entornos.
