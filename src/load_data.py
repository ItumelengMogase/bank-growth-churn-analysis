# src/load_data.py
import pandas as pd
from sqlalchemy import create_engine, text

DB_USER = "itumeleng"
DB_PASSWORD = "libra"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "bank_analytics"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# files to load (adjust paths if necessary)
files = {
    "raw.churn": "../data/churn.csv",
    "raw.transactions": "../data/transactions.csv",
    "raw.user_acquisition": "../data/user_acquisition.csv",
    "raw.user_activity": "../data/user_activity.csv"
}


def create_raw_schema():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()


def drop_dependent_views(table_name):
    """Drop views that depend on the specified table."""
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Identify and drop dependent views in the 'presentation' schema
            # This specific example handles the known view 'presentation.churn_crisis'
            # You might need to adjust this if other tables also have dependent views
            # or if you have a more general way to find them via information_schema
            if table_name == "churn":
                view_name = "presentation.churn_crisis"
                # Check if the specific view exists
                result = conn.execute(text("""
                                           SELECT 1
                                           FROM information_schema.views
                                           WHERE table_schema = 'presentation'
                                             AND table_name = 'churn_crisis';
                                           """))
                if result.fetchone():
                    print(f"  Dropping dependent view: {view_name}")
                    conn.execute(text(f"DROP VIEW IF EXISTS {view_name} CASCADE;"))

            # Add similar checks for other tables if they have known dependent views
            # Example for transactions (adjust if you know the view names):
            # elif table_name == "transactions":
            #     # Add specific view drops for transactions if needed

            trans.commit()
        except Exception as e:
            trans.rollback()
            print(f"  Error dropping dependent views for {table_name}: {e}")
            raise  # Re-raise the exception to stop the process


def load_csv_to_table(full_table_name, csv_path):  # Changed parameter name for clarity
    print(f"Loading {csv_path} -> {full_table_name}")

    # Extract schema and table name
    schema_name, table_name = full_table_name.split(".", 1)  # Split only on the first dot

    # Drop dependent views BEFORE attempting to replace the table
    drop_dependent_views(table_name)

    df = pd.read_csv(csv_path)
    df = df.replace({"": pd.NA, "NA": pd.NA})

    # Handle date columns that might be in YYYY-MM format
    for col in df.columns:
        if 'month' in col.lower() or 'date' in col.lower():
            print(f"  Processing date column: {col}")
            df[col] = df[col].astype(str).str.strip()

            # Check for YYYY-MM format and convert to YYYY-MM-DD
            mask = df[col].str.match(r'^\d{4}-\d{2}$', na=False)
            if mask.any():
                df.loc[mask, col] = df.loc[mask, col] + '-01'
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
                print(f"    ✓ Normalized '{col}' column to full YYYY-MM-DD format")
            else:
                # Try to convert existing dates (in case they're already in different formats)
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date

    # Use the extracted table_name, not the full name
    # Pass the schema via the schema parameter
    df.to_sql(table_name, engine, schema=schema_name, if_exists="replace", index=False)
    print(f"  ✅ Written {full_table_name} ({len(df)} rows)")


if __name__ == "__main__":
    create_raw_schema()
    for tbl, path in files.items():
        load_csv_to_table(tbl, path)
    print("Finished loading CSVs into raw.*")