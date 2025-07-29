# StarRocks MCP Server Release Notes

## Version 0.1.3

1. refactor using fastmcp
2. add new config STARROCKS_MYSQL_AUTH_PLUGIN

## Version 0.1.2

Fix accidental extra import of sqlalalchemy

## Version 0.1.1

1. add new tool query_and_plotly_chart
2. add new tool table_overview & db_overview
3. add env config STARROCKS_DB and STARROCKS_OVERVIEW_LIMIT, both optional


## Version 0.1.0 (Initial Release)

We are excited to announce the first release of the StarRocks MCP (Model Context Protocol) Server. This server enables AI assistants to interact directly with StarRocks databases, providing a seamless interface for executing queries and retrieving database information.

### Description

The StarRocks MCP Server acts as a bridge between AI assistants and StarRocks databases, allowing for direct SQL execution and database exploration without requiring complex setup or configuration. This initial release provides essential functionality for database interaction while maintaining security and performance.

### Features

- **SQL Query Execution**
  - `read_query` tool for executing SELECT queries and commands that return result sets
  - `write_query` tool for executing DDL/DML statements and other StarRocks commands
  - Proper error handling and connection management

- **Database Exploration**
  - List all databases in a StarRocks instance
  - View table schemas using SHOW CREATE TABLE
  - List all tables within a specific database

- **System Information Access**
  - Access to StarRocks internal system information via proc-like interface
  - Visibility into FE nodes, BE nodes, CN nodes, databases, tables, partitions, transactions, jobs, and more

- **Flexible Configuration**
  - Configurable connection parameters (host, port, user, password)
  - Support for both package installation and local directory execution

### Requirements

- Python 3.10 or higher
- Dependencies:
  - mcp >= 1.0.0
  - mysql-connector-python >= 9.2.0

### Configuration

The server can be configured through environment variables:

- `STARROCKS_HOST` (default: localhost)
- `STARROCKS_PORT` (default: 9030)
- `STARROCKS_USER` (default: root)
- `STARROCKS_PASSWORD` (default: empty)
- `STARROCKS_MYSQL_AUTH_PLUGIN` (default: mysql_native_password) user can also pass different auth plugins like `mysql_clear_password`

### Installation

The server can be installed as a Python package:

```bash
pip install mcp-server-starrocks
```

Or run directly from the source:

```bash
uv --directory path/to/mcp-server-starrocks run mcp-server-starrocks
```

### MCP Integration

Add the following configuration to your MCP settings file:

```json
{
  "mcpServers": {
    "mcp-server-starrocks": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-server-starrocks",
        "mcp-server-starrocks"
      ],
      "env": {
        "STARROCKS_HOST": "localhost",
        "STARROCKS_PORT": "9030",
        "STARROCKS_USER": "root",
        "STARROCKS_PASSWORD": "",
        "STARROCKS_MYSQL_AUTH_PLUGIN":"mysql_clear_password"
      }
    }
  }
}
```

---

We welcome feedback and contributions to improve the StarRocks MCP Server. Please report any issues or suggestions through our GitHub repository.
