# Contributing to Distributed Lakehouse

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Test locally
6. Submit a pull request

## Development Workflow

```bash
# Start services
make up

# Run pipeline
make airflow-trigger

# Run tests
make dbt-test
```

## Code Style

- SQL: Lowercase keywords, 4-space indentation
- Python: Follow PEP 8
- YAML: 2-space indentation

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Request review from maintainers

## Questions?

Open an issue on GitHub!
