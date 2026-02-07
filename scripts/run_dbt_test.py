#!/usr/bin/env python3
"""Run dbt test"""

import os
import sys

os.chdir('/opt/airflow/dbt')

from dbt.cli.main import dbtRunner

dbt = dbtRunner()
res = dbt.invoke(["test", "--profiles-dir", "."])

if res.success:
    print("✓ dbt test succeeded")
    sys.exit(0)
else:
    print(f"✗ dbt test failed")
    if res.exception:
        print(f"Exception: {res.exception}")
    sys.exit(1)
