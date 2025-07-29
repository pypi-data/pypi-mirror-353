"""
Clases core para la configuración de conexiones.
"""
from __future__ import annotations
import os
from typing import Optional, Literal, ClassVar
from urllib.parse import urlparse, parse_qs
from sqlalchemy import URL
from sqlalchemy.util import EMPTY_DICT
from pathlib import Path
import inspect
from textwrap import dedent

from tai_sql import db
from .generators import BaseGenerator


class Provider:
    """
    Class to manage database connection parameters.
    """

    # Variable de clase para identificar el tipo de origen de datos
    source_input_type: ClassVar[Optional[Literal['env', 'connection_string', 'params']]] = None
    var_name: ClassVar[Optional[str]] = None
    
    def __repr__(self) -> str:
        """Return a string representation of the Provider instance."""
        return f"Provider(DRIVER={self.drivername}, HOST={self.host}:{self.port}, DB={self.database})"

    @classmethod
    def from_environment(cls, var_name: str = 'DATABASE_URL') -> Provider:
        """
        Crea un Provider desde una variable de entorno.
        
        Args:
            variable_name: Nombre de la variable de entorno
            fallback: URL de fallback si la variable no existe
            
        Returns:
            Instancia de Provider configurada desde entorno
        """
        connection_string = os.getenv(var_name)
        if connection_string is None:
            raise ValueError(f'Debes añadir "{var_name}" como variable de entorno')
        
        instance = cls.from_connection_string(connection_string)
        instance.source_input_type = 'env'
        instance.var_name = var_name
        return instance
    
    @classmethod
    def from_connection_string(cls, connection_string: str) -> Provider:
        """
        Crea un Provider desde un string de conexión directo.
        
        ADVERTENCIA: Este método expone credenciales en el código fuente.
        
        Args:
            connection_string: String de conexión completo
            
        Returns:
            Instancia de Provider configurada desde string
        """
        try:
            instance = cls()
            parse = urlparse(connection_string)
            instance.url = URL.create(
                drivername=parse.scheme,
                username=parse.username,
                password=parse.password,
                host=parse.hostname,
                port=parse.port,
                database=parse.path[1:],  # Remove leading '/'
                query=parse_qs(parse.query)
            )
            instance.source_input_type = 'connection_string'
            return instance
        except Exception as e:
            raise ValueError(f"Error parsing connection string: {e}")
    
    @classmethod
    def from_params(
            cls,
            drivername: str,
            username: str,
            password: str,
            host: str,
            port: int,
            database: str,
            query: dict = EMPTY_DICT
    ) -> Provider:
        """
        Crea un Provider desde parámetros individuales.
        
        ADVERTENCIA: Este método expone credenciales en el código fuente.
        
        Args:
            host: Servidor de base de datos
            database: Nombre de la base de datos
            username: Usuario de conexión
            password: Contraseña de conexión
            port: Puerto de conexión
            driver: Driver de base de datos
            
        Returns:
            Instancia de Provider configurada desde parámetros
        """
        instance = cls()
        instance.url = URL.create(
            drivername=drivername,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            query=query
        )
        instance.source_input_type = 'params'
        return instance

    @property
    def url(self) -> URL:
        """Get the URL object."""
        return self._url
    
    @url.setter
    def url(self, value: URL):
        """Set the URL object."""
        self._url = value
    
    def get_url(self) -> str:
        """Get the connection string."""
        return self.url.render_as_string(hide_password=False)
    
    def get_connection_params(self) -> dict:
        """
        Get the connection parameters as a dictionary.
        
        Returns:
            Dictionary with connection parameters
        """
        return {
            'drivername': self.drivername,
            'username': self.username,
            'password': self.password,
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'query': self.query
        }

    @property
    def drivername(self) -> str:
        """Get the driver name."""
        return self.url.drivername
    
    @property
    def username(self) -> Optional[str]:
        """Get the username."""
        return self.url.username
    
    @property
    def password(self) -> str:
        """Get the password."""
        return self.url.password
    
    @property
    def host(self) -> Optional[str]:
        """Get the host."""
        return self.url.host
    
    @property
    def port(self) -> Optional[int]:
        """Get the port."""
        return self.url.port
    
    @property
    def database(self) -> Optional[str]:
        """Get the database name."""
        return self.url.database
    
    @property
    def query(self) -> dict:
        """Get the query parameters."""
        return self.url.query


def datasource(
    provider: Provider,
    schema: Optional[str] = 'public',
    sqlalchemy_logs: bool = False,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
    pool_size: int = 5,
    max_overflow: int = 5,
    pool_timeout: int = 30
) -> bool:
    """
    Configura el proveedor de base de datos y los parámetros de conexión del motor SQLAlchemy.
    
    Esta función establece la configuración global del datasource que será utilizada
    por el sistema para conectarse a la base de datos. Configura tanto el proveedor
    de base de datos como los parámetros del pool de conexiones.
    
    Args:
        provider (Provider): Datos de conexión. Usa env, connection_string o params para crear un Provider.
        schema (Optional[str], optional): Esquema de base de datos a utilizar por defecto. 
            Defaults to 'public'.
        sqlalchemy_logs (bool, optional): Habilita o deshabilita los logs de SQLAlchemy 
            para debugging. Defaults to False.
        pool_pre_ping (bool, optional): Verifica la conexión antes de usarla del pool.
            Útil para detectar conexiones perdidas. Defaults to True.
        pool_recycle (int, optional): Tiempo en segundos después del cual una conexión
            será reciclada. Previene timeouts de conexiones inactivas. Defaults to 3600.
        pool_size (int, optional): Número de conexiones que mantendrá el pool.
            Defaults to 5.
        max_overflow (int, optional): Número máximo de conexiones adicionales que se pueden
            crear más allá del pool_size cuando sea necesario. Defaults to 5.
        pool_timeout (int, optional): Tiempo máximo en segundos para esperar una conexión
            disponible del pool antes de generar un timeout. Defaults to 30.
    
    Returns:
        bool: True si la configuración se estableció correctamente.
        
    Example:
        >>> from tai_sql import env
        >>> datasource(
        ...     provider=env('DATABASE_URL'),
        ...     schema='mi_esquema',
        ...     pool_size=10,
        ...     pool_recycle=7200
        ... )
        True
        
    Note:
        Esta función debe llamarse antes de realizar cualquier operación con la base
        de datos. Los parámetros del pool son especialmente importantes para aplicaciones
        con alta concurrencia.
    """
    caller_frame = inspect.currentframe().f_back
    caller_file = caller_frame.f_code.co_filename

    db.provider = provider
    db.schema = schema
    db.filename = Path(caller_file).name  # Guardar el nombre del archivo que llama
    db.engine_params.sqlalchemy_logs = sqlalchemy_logs
    db.engine_params.pool_pre_ping = pool_pre_ping
    db.engine_params.pool_recycle = pool_recycle
    db.engine_params.pool_size = pool_size
    db.engine_params.max_overflow = max_overflow
    db.engine_params.pool_timeout = pool_timeout
    return True

def env(variable_name: str = 'DATABASE_URL') -> Provider:
    """
    Crea un Provider desde una variable de entorno (método recomendado).
    
    Args:
        variable_name: Nombre de la variable de entorno
        fallback: URL de fallback si la variable no existe
        
    Returns:
        Provider configurado desde variable de entorno
        
    Example:
        ```python
        from tai_sql import env, datasource
        
        # Leer desde DATABASE_URL
        datasource(provider=env())
        
        # Leer desde variable personalizada
        datasource(provider=env('MY_DB_URL'))
        ```
    """
    return Provider.from_environment(variable_name)


def connection_string(connection_string: str) -> Provider:
    """
    Crea un Provider desde un string de conexión directo.
    
    ⚠️  ADVERTENCIA: Este método expone credenciales en el código fuente.
    Se recomienda usar env() en su lugar.
    
    Args:
        connection_string: String de conexión completo
        
    Returns:
        Provider configurado desde string de conexión
        
    Example:
        ```python
        from tai_sql import connection_string, datasource
        
        # ❌ NO recomendado - credenciales expuestas
        datasource(provider=connection_string('driver://user:pass@host/db'))
        ```
    """
    return Provider.from_connection_string(connection_string)

def params(
        host: str,
        database: str,
        username: str,
        password: str,
        port: int = 5432,
        driver: str = 'postgresql',
        query: dict = EMPTY_DICT
) -> Provider:
    """
    Crea un Provider desde parámetros individuales de conexión.
    
    ⚠️  ADVERTENCIA DE SEGURIDAD: Este método expone credenciales en el código fuente.
    Se recomienda usar env() en su lugar.
    
    Args:
        host: Servidor de base de datos
        database: Nombre de la base de datos
        username: Usuario de conexión
        password: Contraseña de conexión
        port: Puerto de conexión (default: 5432)
        driver: Driver de base de datos (default: 'postgresql')
        
    Returns:
        Provider configurado desde parámetros
        
    Example:
        ```python
        from tai_sql import params, datasource
        
        # ❌ NO recomendado - credenciales expuestas
        datasource(provider=params(
            host='localhost',
            database='mydb',
            username='user',
            password='secret'
        ))
        ```
    """    
    return Provider.from_params(driver, username, password, host, port, database, query)

def generate(*generators) -> bool:
    """
    Configura los generadores a utilizar para la generación de recursos.
    
    Args:
        *generators: Funciones generadoras a configurar
    
    Custom:
    -
        Puedes crear tus propios generadores heredando de BaseGenerator y pasarlos aquí.
    
    Returns:
        bool: True si la configuración se estableció correctamente.
    
    Example:
        >>> from tai_sql.generators import ModelsGenerator, CRUDGenerator
        >>> generate(
        ...     ModelsGenerator(output_dir='models'),
        ...     CRUDGenerator(output_dir='crud', models_import_path='database.models')
        ... )
        True
    """
    for gen in generators:
        if not isinstance(gen, BaseGenerator):
            raise ValueError(f"{gen.__class__.__name__} debe heredar de BaseGenerator")

    db.generators = generators
    return True


class ViewLoader:
    """
    Clase para cargar vistas SQL desde archivos organizados por schema.
    
    Esta clase permite cargar vistas SQL desde archivos ubicados en subcarpetas
    organizadas por el nombre del archivo que las llama, facilitando la gestión
    de consultas complejas y reutilizables.
    
    Estructura esperada:
        ```
        project/
        ├── schemas/
        │   ├── blog.py          # ← Archivo de schema
        │   └── analytics.py     # ← Otro archivo de schema
        └── views/               # ← Carpeta base de vistas
            ├── blog/            # ← Subcarpeta para blog.py
            │   ├── user_stats.sql
            │   └── post_summary.sql
            └── analytics/       # ← Subcarpeta para analytics.py
                ├── sales_report.sql
                └── monthly_summary.sql
        ```
    
    Ejemplo de uso:
        ```python
        # En schemas/blog.py
        from tai_sql import query
        
        class UserStats(View):
            __viewname__ = "user_stats"
            __query__ = query("user_stats.sql")  # Lee views/blog/user_stats.sql
        ```
    """
    
    def __init__(self, name: str, caller_file: str):
        # Obtener el archivo que está llamando a esta función
        caller_path = Path(caller_file).resolve()
        
        # Obtener el nombre del archivo sin extensión (será la subcarpeta)
        schema_name = caller_path.stem  # blog.py -> blog
        
        # Encontrar la carpeta views/ relativa al archivo que llama
        views_base_path = self.find_views_directory(caller_path)
        
        # Crear la ruta específica para este schema
        schema_views_path = views_base_path / schema_name
        
        # Crear la subcarpeta si no existe
        if not schema_views_path.exists():
            schema_views_path.mkdir(parents=True, exist_ok=True)
            # Opcional: crear un archivo README explicativo
            readme_content = dedent(f"""
                # Vistas SQL para {schema_name}

                Este directorio contiene las consultas SQL para las vistas definidas en schemas/{caller_path.name}

                Estructura:
                - Cada archivo .sql debe contener una consulta SELECT válida
                - Los nombres de archivo deben coincidir con el parámetro pasado a query()
                - Las consultas pueden usar WITH, subconsultas y JOINs complejos

                Ejemplo:
                ```sql
                -- user_stats.sql
                SELECT 
                    u.id,
                    u.name,
                    COUNT(p.id) as post_count
                FROM users u
                LEFT JOIN posts p ON u.id = p.author_id
                GROUP BY u.id, u.name
                ORDER BY post_count DESC
                ```
            """).strip()
            readme_file = schema_views_path / "README.md"
            readme_file.write_text(readme_content, encoding='utf-8')
        
        # Normalizar el nombre del archivo
        self.sql_filename = name if name.endswith('.sql') else f"{name}.sql"
        self.sql_file_path = schema_views_path / self.sql_filename
        self.schema_name = schema_name
        self.schema_views_path = schema_views_path
        
        # Verificar que el archivo existe
        if not self.sql_file_path.exists():
            self._handle_file_not_found(name)
    
    def _handle_file_not_found(self, name: str):
        """Maneja el caso cuando no se encuentra el archivo SQL"""
        # Intentar búsqueda más flexible en la subcarpeta del schema
        possible_files = list(self.schema_views_path.glob(f"*{name}*"))
        
        if possible_files:
            suggestion = ", ".join([f.name for f in possible_files[:3]])
            raise FileNotFoundError(
                f"Archivo SQL '{self.sql_filename}' no encontrado en 'views/{self.schema_name}/'.\n"
                f"Archivos similares encontrados: {suggestion}\n"
                f"Ruta completa buscada: {self.sql_file_path}"
            )
        else:
            # Listar archivos disponibles en la subcarpeta
            available_files = list(self.schema_views_path.glob("*.sql"))
            if available_files:
                available_names = [f.name for f in available_files]
                available_list = "\n  - ".join(available_names)
                raise FileNotFoundError(
                    f"Archivo SQL '{self.sql_filename}' no encontrado en 'views/{self.schema_name}/'.\n"
                    f"Archivos disponibles:\n  - {available_list}\n"
                    f"Ruta completa buscada: {self.sql_file_path}"
                )
            else:
                raise FileNotFoundError(
                    f"Archivo SQL '{self.sql_filename}' no encontrado en 'views/{self.schema_name}/'.\n"
                    f"La carpeta está vacía. Crea el archivo '{self.sql_filename}' en:\n"
                    f"  {self.schema_views_path}\n"
                    f"\nEstructura esperada:\n"
                    f"  project/\n"
                    f"  ├── schemas/{self.schema_name}.py    ← Tu archivo de schema\n"
                    f"  └── views/{self.schema_name}/        ← Carpeta para tus archivos SQL\n"
                    f"      └── {self.sql_filename}          ← Tu archivo SQL aquí"
                )
    
    def load_view(self) -> str:
        """Carga el contenido del archivo SQL"""
        try:
            content = self.sql_file_path.read_text(encoding='utf-8').strip()
            
            if not content:
                raise ValueError(f"El archivo '{self.sql_filename}' está vacío")
            
            # Validación básica de SQL
            content_upper = content.upper().strip()
            if not any(content_upper.startswith(keyword) for keyword in ['SELECT', 'WITH', '(']):
                raise ValueError(
                    f"El archivo '{self.sql_filename}' no parece contener una consulta SELECT válida.\n"
                    f"Las vistas deben empezar con SELECT, WITH o '('.\n"
                    f"Archivo: {self.sql_file_path}"
                )
            
            return content
            
        except UnicodeDecodeError as e:
            raise ValueError(f"Error de codificación al leer '{self.sql_filename}': {e}")
        except Exception as e:
            raise ValueError(f"Error leyendo el archivo '{self.sql_filename}': {e}")
    
    def find_views_directory(self, caller_path: Path) -> Path:
        """
        Encuentra la carpeta views/ base relativa al archivo que llama a query().
        
        Busca en este orden:
        1. views/ en el mismo directorio que el archivo caller
        2. views/ en el directorio padre del archivo caller
        3. views/ subiendo hasta encontrarla o llegar a la raíz
        
        Args:
            caller_path: Path del archivo que llama a query()
            
        Returns:
            Path: Ruta a la carpeta views/ base
            
        Raises:
            FileNotFoundError: Si no encuentra la carpeta views/
        """
        current_dir = caller_path.parent
        max_levels = 5  # Limitar búsqueda para evitar ir demasiado arriba
        
        for level in range(max_levels):
            views_candidate = current_dir / 'views'
            
            if views_candidate.exists() and views_candidate.is_dir():
                return views_candidate
            
            # Subir un nivel
            parent = current_dir.parent
            if parent == current_dir:  # Llegamos a la raíz
                break
            current_dir = parent
        
        # No encontrada, crear estructura sugerida
        original_dir = caller_path.parent
        schema_name = caller_path.stem
        
        raise FileNotFoundError(
            f"Carpeta 'views/' no encontrada.\n"
            f"Buscado desde: {original_dir}\n"
            f"Estructura esperada para '{schema_name}.py':\n"
            f"  project/\n"
            f"  ├── schemas/\n"
            f"  │   └── {schema_name}.py     ← Tu archivo está aquí\n"
            f"  └── views/                   ← Debe estar aquí (carpeta base)\n"
            f"      └── {schema_name}/       ← Subcarpeta para tus archivos SQL\n"
            f"          └── mi_vista.sql\n"
            f"\n"
            f"Crea la carpeta 'views/' en el directorio apropiado."
        )
    
    def view_exists(self, name: str) -> bool:
        """
        Verifica si existe un archivo de vista SQL sin cargar su contenido.
        
        Args:
            name (str): Nombre del archivo SQL (con o sin extensión .sql)
            
        Returns:
            bool: True si el archivo existe, False en caso contrario
        """
        try:
            sql_filename = name if name.endswith('.sql') else f"{name}.sql"
            sql_file_path = self.schema_views_path / sql_filename
            return sql_file_path.exists()
        except:
            return False

    def list_views(self) -> list[str]:
        """
        Lista todos los archivos SQL disponibles en la subcarpeta del schema.
        
        Returns:
            list[str]: Lista de nombres de archivos (sin extensión .sql)
        """
        try:
            if not self.schema_views_path.exists():
                return []
            
            sql_files = self.schema_views_path.glob('*.sql')
            return [f.stem for f in sql_files if f.is_file()]
        except:
            return []
    
    def get_schema_info(self) -> dict:
        """
        Obtiene información sobre el schema y sus vistas disponibles.
        
        Returns:
            dict: Información del schema y vistas
        """
        return {
            'schema_name': self.schema_name,
            'schema_views_path': str(self.schema_views_path),
            'views_available': self.list_views(),
            'total_views': len(self.list_views()),
            'path_exists': self.schema_views_path.exists()
        }


def query(name: str) -> str:
    """
    Carga una sentencia SQL desde un archivo en la subcarpeta correspondiente al schema.
    
    Esta función está diseñada para ser utilizada dentro de archivos de schema
    ubicados en schemas/ y busca archivos SQL en views/<nombre_del_archivo_schema>/
    
    Args:
        name (str): Nombre del archivo SQL (con o sin extensión .sql)
        
    Returns:
        str: Contenido del archivo SQL como string
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo está vacío o no contiene SQL válido
        
    Example:
        ```python
        # En schemas/blog.py
        from tai_sql import query
        from tai_sql.orm import View
        
        class UserStats(View):
            __viewname__ = "user_stats"
            __query__ = query("user_stats.sql")  # Lee views/blog/user_stats.sql
            
            # Definir columnas...
            id: int
            name: str
            post_count: int
        
        # O sin extensión
        class PostSummary(View):
            __viewname__ = "post_summary"
            __query__ = query("post_summary")  # Lee views/blog/post_summary.sql
        ```
        
    Directory Structure:
        ```
        project/
        ├── schemas/
        │   ├── blog.py          # ← Archivo de schema que llama query()
        │   └── analytics.py     # ← Otro archivo de schema
        └── views/               # ← Carpeta base de vistas
            ├── blog/            # ← Subcarpeta para blog.py
            │   ├── user_stats.sql
            │   └── post_summary.sql
            └── analytics/       # ← Subcarpeta para analytics.py
                ├── sales_report.sql
                └── monthly_summary.sql
        ```
        
    File Content Example:
        ```sql
        -- views/blog/user_stats.sql
        SELECT 
            u.id,
            u.name,
            u.email,
            COUNT(p.id) as post_count,
            MAX(p.created_at) as last_post_date
        FROM users u
        LEFT JOIN posts p ON u.id = p.author_id
        GROUP BY u.id, u.name, u.email
        ORDER BY post_count DESC
        ```
    """
    caller_frame = inspect.currentframe().f_back
    caller_file = caller_frame.f_code.co_filename

    loader = ViewLoader(name, caller_file)
    return loader.load_view()

