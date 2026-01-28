# Building BSL-PSQL: A PostgreSQL Adapter for Semantic Layers

**Connect your BI tools directly to semantic layers—no custom integrations needed**

---

## The Problem: Your BI Tools Can't Talk to Semantic Layers

Imagine you've built a beautiful semantic layer that defines all your business metrics in one place. Revenue calculations, customer counts, regional breakdowns—everything is standardized and version-controlled in code.

Now you want to visualize this data in your favorite BI tool. But there's a problem: your BI tool speaks SQL and connects to databases like PostgreSQL, while your semantic layer has its own API.

You're faced with a choice:
- Build a custom integration for every tool you use
- Export data to a database and lose the semantic layer benefits
- Write a lot of glue code

**What if your semantic layer could pretend to be a PostgreSQL database?**

That's exactly what BSL-PSQL does. It makes your semantic layer look like a regular PostgreSQL database, so any tool that can connect to Postgres can connect to your metrics.

## Introducing BSL-PSQL

BSL-PSQL is a lightweight server that speaks PostgreSQL's language. It sits between your BI tools and your semantic layer, translating SQL queries into semantic layer queries automatically.

### How It Works

Think of BSL-PSQL as a translator:

```
Your BI Tool (Evidence, Metabase, Tableau, etc.)
        ↓ Sends SQL query
BSL-PSQL Server (the translator)
        ↓ Converts to semantic query
Your Semantic Layer
        ↓ Returns results
Back to Your BI Tool
```

The best part? Your BI tool has no idea it's not talking to a real PostgreSQL database. It just works.

## Getting Started

### Step 1: Define Your Metrics

First, define your business metrics as a semantic table. Here's an example with flight data:

```python
import ibis
from boring_semantic_layer import to_semantic_table

# Create your data source
con = ibis.duckdb.connect(":memory:")
flights_data = con.create_table("flights", {
    'origin': ['SFO', 'LAX', 'JFK'],
    'destination': ['LAX', 'SFO', 'ORD'],
    'passengers': [150, 120, 180]
})

# Define dimensions and measures
flights_table = (
    to_semantic_table(flights_data, name="flights")
    .with_dimensions(
        origin=lambda t: t['origin'],
        destination=lambda t: t['destination']
    )
    .with_measures(
        total_passengers=lambda t: t.passengers.sum(),
        flight_count=lambda t: t.count()
    )
)
```

### Step 2: Start the Server

Next, start the BSL-PSQL server and register your semantic tables:

```python
from bsl_psql.server import BSLPostgresServer

server = BSLPostgresServer(host="localhost", port=5432)
server.register_semantic_table("flights", flights_table)
server.serve()
```

### Step 3: Connect Your BI Tool

Now the magic happens—connect any PostgreSQL-compatible tool and query your metrics:

```sql
-- In any SQL tool
SELECT origin, total_passengers 
FROM flights 
GROUP BY origin;

-- Results:
  origin | total_passengers
---------+------------------
  SFO    |              150
  LAX    |              120
  JFK    |              180
```

That's it! Your semantic layer is now accessible to your entire BI toolstack.

## Real-World Use Cases: Connect Your Favorite Tools

### Evidence.dev - Data Apps and Reports

[Evidence.dev](https://evidence.dev) is a framework for building data apps with Markdown and SQL. With BSL-PSQL, you can connect Evidence directly to your semantic layer:

```yaml
# evidence/sources/semantic_layer.yaml
name: semantic_layer
type: postgres
host: localhost
port: 5432
user: user
password: secret
database: metrics
```

Now write Evidence reports using your semantic metrics:

```markdown
# Sales Dashboard

```sql sales_by_region
SELECT region, total_sales, total_units 
FROM sales 
GROUP BY region
```

<BarChart data={sales_by_region} x=region y=total_sales />
```

Evidence queries your semantic layer just like a database—no special integration needed!

### Metabase - Self-Service Analytics

Connect Metabase to BSL-PSQL:
1. Add a new database connection
2. Select "PostgreSQL" as the database type
3. Enter host: `localhost`, port: `5432`
4. Your team can now build dashboards using semantic metrics

### Tableau, Power BI, and Looker Studio

All major BI platforms support PostgreSQL connections:
- **Tableau**: Use the PostgreSQL connector
- **Power BI**: Use the PostgreSQL connector in "Get Data"
- **Looker Studio**: Add a PostgreSQL data source
- **Superset**: Configure a PostgreSQL connection

Each one connects to BSL-PSQL as if it were a normal database.

### Command-Line Tools

For quick analysis, use `psql` or modern alternatives:

```bash
# Classic psql
psql -h localhost -p 5432 -U user

# Or use pgcli for a better experience
pgcli -h localhost -p 5432 -U user
```

### Programming Languages

Connect from any language with PostgreSQL drivers:

```python
# Python with psycopg2
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="user",
    password="secret"
)
```

```javascript
// Node.js with pg
const { Client } = require('pg');
const client = new Client({
  host: 'localhost',
  port: 5432,
  user: 'user',
  password: 'secret'
});
```

## Why This Matters

### One Definition, Every Tool

Define your metrics once in code, then use them everywhere:
- Evidence reports
- Metabase dashboards  
- Tableau visualizations
- Python notebooks
- Excel via ODBC
- Custom web apps

No more maintaining the same metric calculation in five different places.

### Version Control for Metrics

Your semantic layer lives in Git. Every metric change is tracked, reviewed, and versioned. When you update a metric definition, every dashboard and report automatically uses the new version.

### The Power of Standards

PostgreSQL is everywhere. By speaking PostgreSQL's language, BSL-PSQL works with hundreds of tools without writing a single integration. That's the power of standards.

## Example: Building a Sales Dashboard in Evidence

Here's a complete example of using BSL-PSQL with Evidence:

**1. Define your semantic layer:**
```python
# semantic_layer.py
sales_table = (
    to_semantic_table(sales_data, name="sales")
    .with_dimensions(
        region=lambda t: t['region'],
        product=lambda t: t['product'],
        month=lambda t: t['date'].month()
    )
    .with_measures(
        total_sales=lambda t: t['amount'].sum(),
        avg_order=lambda t: t['amount'].mean(),
        order_count=lambda t: t.count()
    )
)
```

**2. Start BSL-PSQL server:**
```python
server = BSLPostgresServer(host="localhost", port=5432)
server.register_semantic_table("sales", sales_table)
server.serve()
```

**3. Create Evidence report:**
```markdown
# 📊 Sales Performance Dashboard

## Regional Overview
```sql regional_sales
SELECT region, total_sales, order_count
FROM sales
GROUP BY region
ORDER BY total_sales DESC
```

<BarChart data={regional_sales} x=region y=total_sales />

## Monthly Trends  
```sql monthly_trends
SELECT month, total_sales, avg_order
FROM sales  
GROUP BY month
```

<LineChart data={monthly_trends} x=month y=total_sales />
```

Your dashboard now queries the semantic layer directly—always accurate, always up-to-date.

## Current Limitations and Future Work

BSL-PSQL is currently focused on the core semantic layer use case:

**Supported:**
- SELECT with dimensions and measures
- GROUP BY (explicit or inferred)
- Column aliases

**Not Yet Supported:**
- WHERE clauses (filters)
- JOIN operations
- ORDER BY / LIMIT
- Subqueries
- Aggregate functions in SELECT (use semantic measures instead)

These limitations are deliberate—they keep the project focused on semantic queries rather than trying to be a full SQL engine.

## Conclusion

BSL-PSQL solves a real problem: making semantic layers accessible to the tools you already use. No custom integrations, no data copying, no maintaining SQL in multiple places.

Define your metrics once in code, start the BSL-PSQL server, and connect from Evidence, Metabase, Tableau, or any other tool that speaks PostgreSQL. Your semantic layer becomes a universal data API.

The project proves that sometimes the best solution isn't building new integrations—it's speaking a language everyone already understands.

## Try It Yourself

BSL-PSQL is open source and ready to use:

```bash
# Clone the repository
git clone https://github.com/yourusername/BSL-psql.git
cd BSL-psql

# Install dependencies
uv sync

# Run the example
uv run example_usage.py

# In another terminal, connect and query
psql -h localhost -p 5432 -U user
```

## Conclusion

BSL-PSQL demonstrates that you can bridge semantic layers and SQL tooling with a focused, pragmatic approach. By implementing the PostgreSQL wire protocol and translating SQL to semantic queries, it makes semantic layers accessible to the entire PostgreSQL ecosystem.

The project shows how a few hundred lines of Python can create a powerful abstraction layer that connects two different worlds: the declarative elegance of semantic layers and the universal accessibility of SQL.

Whether you're building a metrics layer for your data team or exploring how wire protocols work, BSL-PSQL offers insights into practical API design and protocol implementation.

---

**Get Started:**
- GitHub: [BSL-PSQL Repository](#)
- Boring Semantic Layer: [github.com/boring-works/boring-semantic-layer](https://github.com/boring-works/boring-semantic-layer)

**Compatible Tools:**
- [Evidence.dev](https://evidence.dev) - Build data apps with Markdown and SQL
- [Metabase](https://www.metabase.com/) - Open-source BI platform
- Tableau, Power BI, Looker Studio - All major BI tools
- Any tool with PostgreSQL support!

---

*Questions? Feedback? Open an issue or discussion on GitHub!*
