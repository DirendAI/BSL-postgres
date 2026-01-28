"""
PostgreSQL wire protocol adapter for Boring Semantic Layer (BSL).

This module implements a PostgreSQL proxy server that translates SQL queries
to BSL semantic queries and returns results in PostgreSQL-compatible format.
"""

import logging
from typing import Dict, List, Optional

import sqlglot
from sqlglot import exp
import riffq
from riffq.connection import BaseConnection

# Set up logging first
logger = logging.getLogger(__name__)

# Import riffq components for PostgreSQL wire protocol
try:
    # Define PostgreSQL OIDs (Object IDs) for data types
    TEXT_OID = 25  # text type
    INT8_OID = 20  # bigint type  
    FLOAT8_OID = 701  # double precision type
    BOOL_OID = 16  # boolean type
    DATE_OID = 1082  # date type
    TIMESTAMP_OID = 1114  # timestamp type
    
except ImportError as e:
    raise ImportError(
        "Could not import riffq components. "
        "Please ensure riffq is installed correctly."
    ) from e

from boring_semantic_layer import to_semantic_table
from boring_semantic_layer import SemanticTable

class BSLSemanticCatalog:
    """
    Catalog that maps SQL table names to BSL semantic tables.
    """
    
    def __init__(self):
        self.tables: Dict[str, SemanticTable] = {}
    
    def register_table(self, name: str, semantic_table: SemanticTable):
        """Register a semantic table with a SQL table name."""
        self.tables[name] = semantic_table
    
    def get_table(self, name: str) -> Optional[SemanticTable]:
        """Get a semantic table by SQL table name."""
        return self.tables.get(name)
    
    def list_tables(self) -> List[str]:
        """List all registered table names."""
        return list(self.tables.keys())


class BSLConnection(BaseConnection):
    """
    PostgreSQL connection handler that translates SQL queries to BSL semantic queries.
    """
    catalog: BSLSemanticCatalog = None
    
    def handle_auth(self, user, password, host, database=None, callback=callable):
        # Accept a single demo user
        callback(user == "user" and password == "secret")

    def handle_connect(self, ip, port, callback=callable):
        # allow every incoming connection
        callback(True)

    def handle_disconnect(self, ip, port, callback=callable):
        # invoked when client disconnects
        callback(True)
    
    def handle_query(self, query, callback=callable, **kwargs):
        """
        Handle a SQL query by translating it to BSL and executing it.
        """
        try:
            logger.info(f"Handling query: {query}")
            
            # Parse the SQL query
            ast = sqlglot.parse_one(query)
            
            # Extract table name
            table_node = ast.find(exp.Table)
            if not table_node:
                raise Exception("No table specified in query")
            
            table_name = table_node.name
            
            # Get the semantic table from catalog
            semantic_table = self.catalog.get_table(table_name)
            if semantic_table is None:
                raise Exception(f"Table '{table_name}' not found in semantic catalog")
            
            # Extract SELECT columns
            select_cols = []
            for select_expr in ast.selects:
                if isinstance(select_expr, exp.Alias):
                    select_cols.append(select_expr.alias)
                else:
                    select_cols.append(select_expr.name)
            
            # Extract GROUP BY columns
            group_by_node = ast.args.get("group")
            group_by_cols = []
            if group_by_node:
                for expr in group_by_node.expressions:
                    if isinstance(expr, exp.Identifier):
                        group_by_cols.append(expr.name)
            
            # Classify columns as dimensions or measures
            dimensions = []
            measures = []
            
            for col in select_cols:
                if col in semantic_table.dimensions:
                    dimensions.append(col)
                elif col in semantic_table.measures:
                    measures.append(col)
                else:
                    raise Exception(f"Column '{col}' not found in semantic table '{table_name}'")
            
            # If no explicit GROUP BY, infer from dimensions
            if not group_by_cols and dimensions:
                group_by_cols = dimensions
            
            # Build and execute BSL query
            bsl_query = semantic_table.group_by(*group_by_cols).aggregate(*measures)
            logger.info(f"Executing BSL query for table '{table_name}'")
            logger.info(f"Dimensions: {group_by_cols}, Measures: {measures}")
            logger.info(f"BSL Query: {bsl_query}")

            batch = bsl_query.execute()
            logger.info(f"Query executed successfully, returning results {type(batch)}")
            
            self.send_reader(batch, callback)
            
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            if callback:
                callback(None, None, str(e))
            raise


class BSLPostgresServer:
    """
    PostgreSQL server that exposes BSL semantic tables as SQL tables.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        username: Optional[str] = "postgres",
        password: Optional[str] = "postgres",
        catalog: Optional[BSLSemanticCatalog] = None
    ):
        self.catalog = catalog or BSLSemanticCatalog()
        self.host = host
        self.port = port
        self.user = username
        self.password = password
    
    def register_semantic_table(
        self, 
        name: str, 
        semantic_table: SemanticTable
    ):
        """Register a BSL semantic table with a SQL table name."""
        self.catalog.register_table(name, semantic_table)
        logger.info(f"Registered semantic table '{name}'")
    
    def serve(self):
        """Start the PostgreSQL server."""
        logger.info(f"Starting BSL PostgreSQL server on {self.host}:{self.port}")
        
        # Set the catalog on the connection class
        BSLConnection.catalog = self.catalog
        
        # Start the riffq server using the correct address format
        server = riffq.RiffqServer(
            f"{self.host}:{self.port}", connection_cls=BSLConnection
        )
        
        # riffq server runs synchronously
        logger.info(f"BSL PostgreSQL server listening on {self.host}:{self.port}")
        logger.info("Press Ctrl+C to stop the server")
        
        server.start()