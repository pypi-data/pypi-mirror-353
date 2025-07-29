# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Server
```bash
# Run directly without installation
uvx oriona-database-tools

# Or install and run
pip install oriona-database-tools
```

### Testing
```bash
# Run all tests with coverage
pytest tests/ -v --cov=database_tools --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=80

# Run specific test categories
python tests/test_runner.py security      # Security tests only
python tests/test_runner.py integration   # Integration tests only
python tests/test_runner.py test_tools.py # Specific test file

# Run a single test
pytest tests/test_tools.py::test_specific_function -v
```

### Environment Setup
```bash
# Required
export DATABASE_URL="postgresql://user:password@localhost:5432/mydb"

# Optional
export DATABASE_TOOLS_LOG_LEVEL="INFO"
export DATABASE_TOOLS_MAX_CONNECTIONS="5"
export TABLE_WHITELIST="users,orders,products"  # Only allow these tables
export TABLE_BLACKLIST="secrets,api_keys"       # Block these tables
```

## Architecture Overview

This is a Model Context Protocol (MCP) server that provides safe database access to AI assistants. It follows a layered architecture:

### Core Components
- **server.py**: FastMCP server implementation exposing three database tools
- **repository.py**: Repository pattern for all database operations with connection pooling
- **query_builder.py**: SQL query validation and safety checks
- **config.py**: Pydantic-based configuration management
- **exceptions.py**: Custom exception hierarchy for meaningful error handling

### MCP Tools Exposed
1. **list_tables**: Returns all tables/views in the database
2. **explore_table**: Provides detailed schema info and sample data for a specific table
3. **query_database_readonly**: Executes safe SELECT queries with timeout and row limits

### Security Architecture
- Only SELECT and WITH queries allowed (enforced in query_builder.py)
- Query timeout protection (default 30s, configurable)
- Row limit controls (default 100 rows, configurable)
- Connection pooling with automatic recycling
- Table access filtering via whitelist/blacklist (TableFilterConfig)
- All database operations go through the repository layer

### Testing Strategy
The project uses comprehensive testing with pytest:
- **Unit tests**: Mock database interactions, test individual components
- **Integration tests**: Use SQLite for real database operations
- **Security tests**: Validate SQL injection prevention and query restrictions
- **Property-based tests**: Use Hypothesis for query validation edge cases
- **Benchmarks**: Performance testing for critical operations

Coverage target is 80% with HTML reports generated in htmlcov/

### Error Handling Pattern
Different error formats for different tools:
- Simple errors for list_tables and explore_table
- Detailed errors with recommendations for query_database_readonly
- All errors include error_type for debugging

### Key Development Patterns
1. **Repository Pattern**: All database operations go through DatabaseRepository
2. **Configuration**: Environment variables → Pydantic Settings → Validated config
3. **Connection Management**: SQLAlchemy engine with connection pooling and pre-ping
4. **Query Safety**: sqlparse for validation, custom checks for dangerous operations
5. **Error Sanitization**: Database URLs stripped from error messages for security

## BigQuery Support

### Enhanced STRUCT Type Handling

The MCP now has improved support for BigQuery STRUCT types:

1. **Column Information**: The `get_table_columns` method now uses BigQuery's INFORMATION_SCHEMA.COLUMNS directly instead of SQLAlchemy's inspector for BigQuery tables. This provides accurate type information for complex types:
   - Simple STRUCT: `STRUCT<field1 STRING, field2 INT64>`
   - Nested STRUCT: `STRUCT<data STRUCT<key STRING, value FLOAT64>>`
   - Arrays of STRUCT: `ARRAY<STRUCT<name STRING, id INT64>>`
   - Complex nested structures with multiple levels

2. **Sample Data**: STRUCT values in sample data and query results are now automatically converted to nested dictionary representations for better readability. For example:
   ```json
   {
     "address": {
       "street": "123 Main St",
       "city": "San Francisco",
       "zip_code": 94105
     }
   }
   ```

3. **Error Messages**: Enhanced error handling provides specific recommendations for common BigQuery STRUCT issues:
   - Direct STRUCT comparisons: "Use dot notation to access individual fields"
   - Missing fields: "Use explore_table to see available fields"
   - Array handling: "Use UNNEST() to access array elements"

### BigQuery Limitations

1. **Primary/Foreign Keys**: BigQuery doesn't support traditional primary keys or foreign key constraints. The methods `get_primary_keys()` and `get_foreign_keys()` return empty lists for BigQuery tables.

2. **Table Naming**: BigQuery tables can be referenced either as `table_name` (using the default dataset) or `dataset.table_name` (explicit dataset specification).

### Querying STRUCT Fields

When querying BigQuery tables with STRUCT columns:
- Access nested fields with dot notation: `SELECT address.city FROM table`
- Compare individual fields, not entire STRUCTs: `WHERE address.zip_code = 94105`
- Use UNNEST for arrays: `SELECT * FROM table, UNNEST(tags) AS tag`

### Environment Variables for BigQuery
```bash
# Required for BigQuery
export BIGQUERY_PROJECT_ID="my-project"

# Optional
export BIGQUERY_DATASET="my_dataset"          # Default dataset
export BIGQUERY_CREDENTIALS_BASE64="..."      # Base64 encoded service account JSON
export BIGQUERY_LOCATION="US"                 # Data location (default: US)
```