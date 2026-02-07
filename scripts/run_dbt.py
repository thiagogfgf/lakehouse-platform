#!/usr/bin/env python3
"""Run dbt via Python API"""

import os
import sys

# Set working directory
os.chdir('/opt/airflow/dbt')

# Import dbt programmatic invocation
from dbt.cli.main import dbtRunner, dbtRunnerResult

# Initialize dbt runner
dbt = dbtRunner()

# Run dbt with arguments
cli_args = ["run", "--profiles-dir", "."]
res: dbtRunnerResult = dbt.invoke(cli_args)

# Check result
if res.success:
    print("✓ dbt run succeeded")
    sys.exit(0)
else:
    print(f"✗ dbt run failed")
    if res.exception:
        print(f"Exception: {res.exception}")
    sys.exit(1)
