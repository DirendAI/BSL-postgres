"""
Example usage for BSL-PSQL - PostgreSQL wire protocol adapter for Boring Semantic Layer.
"""

import logging
import ibis
from bsl_psql.server import BSLPostgresServer
from boring_semantic_layer import to_semantic_table

def create_sample_semantic_tables():
    """Create sample semantic tables for demonstration."""
    
    # Sample flight data
    con = ibis.duckdb.connect(":memory:")
    flights_data = con.create_table("flights_data", {
        'origin': ['SFO', 'SFO', 'LAX', 'JFK', 'ORD'],
        'destination': ['LAX', 'JFK', 'SFO', 'ORD', 'SFO'],
        'distance': [337, 2586, 337, 740, 1846],
        'passengers': [150, 200, 120, 180, 190],
        'delay': [15, 30, 10, 25, 20]
    })
    
    # Create semantic table for flights
    flights_table = (
        to_semantic_table(flights_data, name="flights")
        .with_dimensions(
            origin=lambda t: t['origin'],
            destination=lambda t: t['destination'],
            route=lambda t: t['origin'] + "-" + t['destination']
        )
        .with_measures(
            total_passengers=lambda t: t.passengers.sum(),
            avg_delay=lambda t: t.delay.mean(),
            total_distance=lambda t: t.distance.sum(),
            flight_count=lambda t: t.count()
        )
    )
    
    # Sample sales data
    sales_data = con.create_table("sales_data", {
        'product': ['A', 'A', 'B', 'B', 'C'],
        'region': ['West', 'East', 'West', 'North', 'South'],
        'sales': [1000, 1500, 800, 1200, 900],
        'units': [50, 75, 40, 60, 1]
    })
    
    # Create semantic table for sales
    sales_table = (
        to_semantic_table(sales_data, name="sales")
        .with_dimensions(
            product=lambda t: t['product'],
            region=lambda t: t['region']
        )
        .with_measures(
            total_sales=lambda t: t['sales'].sum(),
            total_units=lambda t: t['units'].sum(),
            avg_price=lambda t: (t['sales'] / t['units']).mean()
        )
    )
    
    return {
        'flights': flights_table,
        'sales': sales_table
    }


def main():
    """Main function to start the BSL PostgreSQL server."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("BSL-PSQL - PostgreSQL wire protocol adapter for Boring Semantic Layer")
    print("Creating sample semantic tables...")
    
    # Create sample semantic tables
    semantic_tables = create_sample_semantic_tables()
    
    # Create and run the server
    server = BSLPostgresServer(host="localhost", port=5432, user="postgres", password="postgres")
    
    # Register semantic tables
    print("Registering semantic tables with PostgreSQL server...")
    for table_name, semantic_table in semantic_tables.items():
        server.register_semantic_table(table_name, semantic_table)
        print(f"  - Registered '{table_name}' table")
    
    print("\nExample queries you can try:")
    print("  SELECT origin, total_passengers FROM flights GROUP BY origin")
    print("  SELECT product, total_sales FROM sales GROUP BY product")
    print("  SELECT region, total_units FROM sales GROUP BY region")
    print()
    print("Starting BSL-PSQL server on localhost:5432...")
    print("Connect using: psql -h localhost -p 5432 -U postgres")
    print("Press Ctrl+C to stop the server")
    
    try:
        server.serve()
    except KeyboardInterrupt:
        print("\nServer shutdown by user")
    except Exception as e:
        print(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()
