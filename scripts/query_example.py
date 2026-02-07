#!/usr/bin/env python3
"""Exemplo de queries com Python + Trino"""

import trino
import pandas as pd
from tabulate import tabulate

def get_connection():
    """Criar conexão com Trino"""
    return trino.dbapi.connect(
        host='localhost',
        port=8080,
        user='admin',
        catalog='iceberg',
        schema='marts',
        http_scheme='http'
    )

def query_daily_stats():
    """Estatísticas diárias de viagens"""
    conn = get_connection()

    query = """
    SELECT
        pickup_date_key as date,
        COUNT(*) as trips,
        ROUND(AVG(fare_amount), 2) as avg_fare,
        ROUND(AVG(trip_distance), 2) as avg_distance,
        ROUND(AVG(tip_percentage), 2) as avg_tip_pct
    FROM fct_trips
    GROUP BY pickup_date_key
    ORDER BY pickup_date_key DESC
    LIMIT 10
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print("\n📊 Estatísticas Diárias - Top 10 Dias")
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    return df

def query_payment_analysis():
    """Análise por tipo de pagamento"""
    conn = get_connection()

    query = """
    SELECT
        payment_type_desc as payment_type,
        COUNT(*) as total_trips,
        ROUND(AVG(fare_amount), 2) as avg_fare,
        ROUND(AVG(tip_percentage), 2) as avg_tip_pct
    FROM fct_trips
    GROUP BY payment_type_desc
    ORDER BY total_trips DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print("\n💳 Análise por Tipo de Pagamento")
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    return df

def query_distance_categories():
    """Distribuição por categoria de distância"""
    conn = get_connection()

    query = """
    SELECT
        trip_distance_category as category,
        COUNT(*) as trips,
        ROUND(AVG(trip_duration_minutes), 2) as avg_duration_min,
        ROUND(AVG(fare_amount), 2) as avg_fare
    FROM fct_trips
    GROUP BY trip_distance_category
    ORDER BY
        CASE trip_distance_category
            WHEN 'Short' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Long' THEN 3
            ELSE 4
        END
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print("\n🚕 Distribuição por Categoria de Distância")
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    return df

if __name__ == "__main__":
    print("=" * 80)
    print("NYC TAXI - ANÁLISE DE DADOS")
    print("=" * 80)

    # Executar análises
    query_daily_stats()
    query_payment_analysis()
    query_distance_categories()

    print("\n✓ Análise concluída!")
