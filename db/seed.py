#!/usr/bin/env python3
"""
Seed StarRocks with the OBT schema and dummy data.
Waits for StarRocks to become healthy, then runs db/init.sql.

Usage:
    python db/seed.py
    python db/seed.py --host localhost --port 9030
"""
import argparse
import time
import sys
import os

def wait_for_starrocks(host, port, user, max_retries=30, delay=5):
    """Wait for StarRocks FE to accept MySQL connections."""
    import pymysql
    for attempt in range(1, max_retries + 1):
        try:
            conn = pymysql.connect(host=host, port=port, user=user, connect_timeout=5)
            conn.cursor().execute("SELECT 1")
            conn.close()
            print(f"✅ StarRocks is ready (attempt {attempt})")
            return True
        except Exception as e:
            print(f"⏳ Waiting for StarRocks... attempt {attempt}/{max_retries} ({e})")
            time.sleep(delay)
    print("❌ StarRocks did not become ready in time")
    return False


def run_sql_file(host, port, user, sql_path):
    """Execute a .sql file against StarRocks."""
    import pymysql
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split on semicolons, filtering empty statements
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]

    conn = pymysql.connect(host=host, port=port, user=user, connect_timeout=10)
    cursor = conn.cursor()

    for i, stmt in enumerate(statements, 1):
        # Skip pure comments
        lines = [l for l in stmt.split("\n") if not l.strip().startswith("--")]
        clean = "\n".join(lines).strip()
        if not clean:
            continue
        try:
            cursor.execute(stmt)
            conn.commit()
            # Show first 80 chars of each statement
            preview = stmt.replace("\n", " ")[:80]
            print(f"  [{i}/{len(statements)}] ✓ {preview}...")
        except Exception as e:
            print(f"  [{i}/{len(statements)}] ✗ Error: {e}")
            print(f"    Statement: {stmt[:120]}...")

    cursor.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Seed StarRocks with dummy data")
    parser.add_argument("--host", default="localhost", help="StarRocks FE host")
    parser.add_argument("--port", type=int, default=9030, help="StarRocks FE MySQL port")
    parser.add_argument("--user", default="root", help="StarRocks user")
    parser.add_argument("--sql", default=None, help="Path to SQL file")
    parser.add_argument("--wait", action="store_true", help="Wait for StarRocks to be ready")
    args = parser.parse_args()

    # Find the SQL file
    sql_path = args.sql
    if not sql_path:
        # Look relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_path = os.path.join(script_dir, "init.sql")
    
    if not os.path.exists(sql_path):
        print(f"❌ SQL file not found: {sql_path}")
        sys.exit(1)

    print(f"📄 SQL file: {sql_path}")
    print(f"🔌 Target: {args.user}@{args.host}:{args.port}")

    if args.wait:
        if not wait_for_starrocks(args.host, args.port, args.user):
            sys.exit(1)

    print("\n🚀 Running init.sql...")
    run_sql_file(args.host, args.port, args.user, sql_path)
    print("\n✅ Seed complete!")

    # Quick verification
    import pymysql
    conn = pymysql.connect(host=args.host, port=args.port, user=args.user, database="stats_center", connect_timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_analytics")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT region) FROM sales_analytics")
    regions = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT product_name) FROM sales_analytics")
    products = cursor.fetchone()[0]
    cursor.execute("SELECT MIN(order_date), MAX(order_date) FROM sales_analytics")
    date_range = cursor.fetchone()
    conn.close()

    print(f"\n📊 Verification:")
    print(f"   Rows:     {count}")
    print(f"   Regions:  {regions}")
    print(f"   Products: {products}")
    print(f"   Dates:    {date_range[0]} → {date_range[1]}")


if __name__ == "__main__":
    main()
