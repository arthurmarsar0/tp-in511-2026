"""
Tool definitions: Database wrapper, SQL tools, Calculator.
"""

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .data import init_demo_db


# ============================================================
# Database wrapper (auto-creates DB if missing)
# ============================================================


class Database:
    """SQLite wrapper. Creates the database with demo data if missing."""

    def __init__(self, path: str = "library.db"):
        self.path = path
        # Auto-create database if missing
        if not Path(path).exists():
            init_demo_db(path)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row

    def execute(self, query: str) -> str:
        """Execute any SQL query and return results as JSON."""
        try:
            cursor = self.conn.execute(query)
            if cursor.description:  # SELECT query
                rows = cursor.fetchall()
                return json.dumps([dict(row) for row in rows], default=str)
            else:  # INSERT, UPDATE, DELETE, etc.
                self.conn.commit()
                return json.dumps({"rowcount": cursor.rowcount})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_tables(self) -> str:
        """List all tables."""
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return json.dumps([row[0] for row in cursor.fetchall()])

    def describe_table(self, table_name: str) -> str:
        """Describe a table structure."""
        cursor = self.conn.execute(f"PRAGMA table_info({table_name})")
        return json.dumps([dict(row) for row in cursor.fetchall()])


# ============================================================
# SQL Tools
# ============================================================


def make_sql_tools(db: Database):
    """Create SQL tools bound to a database."""

    @dataclass
    class SQLQuery:
        """Execute a SQL query on the database. Returns results as JSON."""

        query: str

        def __call__(self) -> str:
            return db.execute(self.query)

    @dataclass
    class ListTables:
        """List all tables in the database."""

        def __call__(self) -> str:
            return db.list_tables()

    @dataclass
    class DescribeTable:
        """Get the structure (columns) of a table."""

        table_name: str

        def __call__(self) -> str:
            return db.describe_table(self.table_name)

    return [SQLQuery, ListTables, DescribeTable]


# ============================================================
# Calculator Tool (simple example)
# ============================================================


@dataclass
class Calculator:
    """Perform a simple mathematical operation.

    Operations: add, subtract, multiply, divide
    """

    operation: Literal["add", "subtract", "multiply", "divide"]
    a: float
    b: float

    def __call__(self) -> float:
        """Execute the calculation and return the result."""
        ops = {
            "add": lambda: self.a + self.b,
            "subtract": lambda: self.a - self.b,
            "multiply": lambda: self.a * self.b,
            "divide": lambda: (
                self.a / self.b
                if self.b != 0
                else (_ for _ in ()).throw(ValueError("Division by zero"))
            ),
        }
        return ops[self.operation]()
