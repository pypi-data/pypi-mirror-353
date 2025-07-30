# MySQL MCP Server

A MySQL server implementation for the MCP (Model Control Protocol) framework. This server allows you to interact with MySQL databases through the MCP protocol.

## Features

- Execute SQL queries
- List MySQL tables as resources
- Get table schemas
- Configurable through environment variables
- Supports various MySQL character sets and collations

## Installation

You can install the package directly from PyPI:

```bash
pip install mysql-server
```

Or install from source:

```bash
git clone https://github.com/yourusername/mysql-server.git
cd mysql-server
pip install .
```

## Configuration

The server is configured through environment variables:

- `MYSQL_HOST`: MySQL server host (default: "localhost")
- `MYSQL_PORT`: MySQL server port (default: 3306)
- `MYSQL_USER`: MySQL username (required)
- `MYSQL_PASSWORD`: MySQL password (required)
- `MYSQL_DATABASE`: MySQL database name (required)
- `MYSQL_CHARSET`: MySQL character set (default: "utf8mb4")
- `MYSQL_COLLATION`: MySQL collation (default: "utf8mb4_unicode_ci")
- `MYSQL_SQL_MODE`: MySQL SQL mode (default: "TRADITIONAL")

## Usage

1. Set up your environment variables:

```bash
export MYSQL_USER="your_user"
export MYSQL_PASSWORD="your_password"
export MYSQL_DATABASE="your_database"
```

2. Run the server:

```bash
mysql-server
```

Or use it with an MCP client like Claude Desktop or Cursor by adding this to your MCP configuration:

```json
{
  "mcpServers": {
    "mysql-server": {
      "command": "mysql-server",
      "env": {
        "MYSQL_USER": "your_user",
        "MYSQL_PASSWORD": "your_password",
        "MYSQL_DATABASE": "your_database"
      }
    }
  }
}
```

## Available Tools

### execute_sql

Execute an SQL query on the MySQL server.

Example:
```sql
SELECT * FROM users LIMIT 10;
```

## Available Resources

### mysql://tables

List all tables in the database.

### mysql://table/{table_name}

Get the schema of a specific table.

Example: `mysql://table/users`

## Development

To run the server in development mode:

```bash
mcp dev mysql_server_launcher.py
```

This will start the MCP Inspector interface where you can test the tools and resources.

## License

MIT License
