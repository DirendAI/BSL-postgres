# BSL-PSQL: PostgreSQL Wire Protocol Adapter for Boring Semantic Layer

**BSL-PSQL** is a PostgreSQL wire protocol adapter that exposes Boring Semantic Layer (BSL) semantic tables as PostgreSQL tables. It translates SQL queries to BSL semantic queries and returns results in PostgreSQL-compatible format.

## Features

- ✅ **PostgreSQL Wire Protocol**: Speaks native PostgreSQL protocol
- ✅ **SQL to BSL Translation**: Converts SQL queries to BSL semantic queries
- ✅ **Semantic Catalog**: Maps SQL table names to BSL semantic tables
- ✅ **Automatic GROUP BY**: Infers GROUP BY from dimensions in SELECT
- ✅ **Type Mapping**: Converts BSL results to PostgreSQL-compatible rows

## Architecture

```
PostgreSQL Client (psql, BI tools, etc.)
        ↓ PostgreSQL Wire Protocol
BSL-PSQL Server (this project)
        ↓ SQL → BSL Translation
Boring Semantic Layer
        ↓ Semantic Queries
Underlying Data (DuckDB, Pandas, Arrow, etc.)
```

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/bsl-psql.git
cd bsl-psql

# Install dependencies
uv sync
```

## Quick Start

### 1. Create Semantic Tables

```python
import pandas as pd
from boring_semantic_layer import to_semantic_table

# Sample data
flights_data = pd.DataFrame({
    'origin': ['SFO', 'SFO', 'LAX', 'JFK'],
    'destination': ['LAX', 'JFK', 'SFO', 'ORD'],
    'passengers': [150, 200, 120, 180]
})

# Create semantic table
flights_table = (
    to_semantic_table(flights_data, name="flights")
    .with_dimensions(
        origin=lambda t: t['origin'],
        destination=lambda t: t['destination']
    )
    .with_measures(
        total_passengers=lambda t: t['passengers'].sum(),
        flight_count=lambda t: len(t)
    )
)
```

### 2. Start the Server

```python
from bsl_psql.server import BSLPostgresServer

# Create and configure server
server = BSLPostgresServer("localhost", 5432)
server.register_semantic_table("flights", flights_table)

# Start server
server.serve()
```

### 3. Query with PostgreSQL Client

```bash
# Connect with psql
psql -h localhost -p 5432 -U postgres

# Run SQL queries
SELECT origin, total_passengers FROM flights;
SELECT destination, flight_count FROM flights;
```

## SQL Support

BSL-PSQL supports a restricted SQL dialect that maps directly to BSL semantics:

```sql
-- Basic query with automatic GROUP BY inference
SELECT dimension_one, measure_one FROM my_table

-- Multiple dimensions and measures
SELECT dim1, dim2, measure1, measure2 FROM my_table
```

### Supported SQL Features

- ✅ `SELECT` with dimensions and measures
- ✅ `FROM` with semantic table names
- ✅ `GROUP BY` (explicit or inferred)
- ✅ Column aliases
- ❌ Joins (planned for future)
- ❌ WHERE clauses (planned for future)
- ❌ Subqueries

## Configuration

### Semantic Catalog

```python
from bsl_psql.server import BSLSemanticCatalog

catalog = BSLSemanticCatalog()
catalog.register_table("flights", flights_table)
catalog.register_table("sales", sales_table)

# Use catalog with server
server = BSLPostgresServer(..., catalog=catalog)
```

## Examples

See [example_usage.py](example_usage.py) for a complete working example with sample semantic tables.

### Example Queries

```sql
-- Simple aggregation
SELECT origin, total_passengers FROM flights

-- Multiple measures
SELECT product, total_sales, total_units FROM sales

-- Multiple dimensions
SELECT region, product, total_sales FROM sales
```

## Development

### Running the Server

```bash
# Run the server with sample data
uv run example_usage.py

# Test with psql in another terminal (You can specify different username and password when initializing BSLPostgresServer)
psql -h localhost -p 5432 -U postgres
# Password: postgres
```

### Project Structure

```
├── bsl_psql/                  # Main package
│   └── server.py             # PostgreSQL server implementation
├── example_usage.py          # Example usage
├── pyproject.toml            # Project configuration
└── README.md                 # Documentation
```

## Roadmap

- [ ] Metadata exposure via information_schema
- [ ] WHERE clause support with BSL filters
- [ ] JOIN support between semantic tables
- [ ] Performance optimization and caching

## Contributing

Contributions are welcome! Please open issues and pull requests on GitHub.

## License

MIT License - see LICENSE file for details.

## Related Projects

- [Boring Semantic Layer](https://github.com/boringdata/boring-semantic-layer) - The semantic layer this adapter connects to
- [riffq](https://github.com/ybrs/riffq) - PostgreSQL wire protocol implementation used by this project
- [sqlglot](https://github.com/tobymao/sqlglot) - SQL parsing library used for query translation