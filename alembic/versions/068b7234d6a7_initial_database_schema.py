"""Initial database schema

Revision ID: 068b7234d6a7
Revises: 
Create Date: 2025-05-30 10:08:37.259497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '068b7234d6a7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Product Context
    op.execute("""
        CREATE TABLE product_context (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            content TEXT NOT NULL DEFAULT '{}'
        )
    """)
    op.execute("INSERT OR IGNORE INTO product_context (id, content) VALUES (1, '{}')")

    # Active Context
    op.execute("""
        CREATE TABLE active_context (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            content TEXT NOT NULL DEFAULT '{}'
        )
    """)
    op.execute("INSERT OR IGNORE INTO active_context (id, content) VALUES (1, '{}')")

    # Decisions (including tags directly)
    op.execute("""
        CREATE TABLE decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            summary TEXT NOT NULL,
            rationale TEXT,
            implementation_details TEXT,
            tags TEXT -- JSON stringified list of tags
        )
    """)
    # FTS5 table for decisions
    op.execute("""
        CREATE VIRTUAL TABLE decisions_fts USING fts5(
            summary,
            rationale,
            implementation_details,
            tags,
            tokenize = 'porter unicode61'
        )
    """)
    # Triggers to keep decisions_fts synchronized with decisions table
    op.execute("""
        CREATE TRIGGER decisions_ai AFTER INSERT ON decisions BEGIN
            INSERT INTO decisions_fts (rowid, summary, rationale, implementation_details, tags)
            VALUES (new.id, new.summary, new.rationale, new.implementation_details, new.tags);
        END;
    """)
    op.execute("""
        CREATE TRIGGER decisions_ad AFTER DELETE ON decisions BEGIN
            DELETE FROM decisions_fts WHERE rowid=old.id;
        END;
    """)
    op.execute("""
        CREATE TRIGGER decisions_au AFTER UPDATE ON decisions BEGIN
            UPDATE decisions_fts SET
                summary = new.summary,
                rationale = new.rationale,
                implementation_details = new.implementation_details,
                tags = new.tags
            WHERE rowid=new.id;
        END;
    """)

    # Progress Entries
    op.execute("""
        CREATE TABLE progress_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            status TEXT NOT NULL,
            description TEXT NOT NULL,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES progress_entries(id) ON DELETE SET NULL
        )
    """)

    # System Patterns (including tags directly)
    op.execute("""
        CREATE TABLE system_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            tags TEXT -- JSON stringified list of tags
        )
    """)

    # Custom Data (including timestamp, as per the fix)
    op.execute("""
        CREATE TABLE custom_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Added timestamp
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL, -- Store as JSON string
            UNIQUE(category, key)
        )
    """)
    # General FTS5 table for custom_data
    op.execute("""
        CREATE VIRTUAL TABLE custom_data_fts USING fts5(
            category,
            key,
            value_text, -- Stores the content of custom_data.value for FTS
            tokenize = 'porter unicode61'
        )
    """)
    # Triggers to keep general custom_data_fts synchronized
    op.execute("""
        CREATE TRIGGER custom_data_ai_generic
        AFTER INSERT ON custom_data
        BEGIN
            INSERT INTO custom_data_fts (rowid, category, key, value_text)
            VALUES (new.id, new.category, new.key, new.value);
        END;
    """)
    op.execute("""
        CREATE TRIGGER custom_data_ad_generic
        AFTER DELETE ON custom_data
        BEGIN
            DELETE FROM custom_data_fts WHERE rowid=old.id;
        END;
    """)
    op.execute("""
        CREATE TRIGGER custom_data_au_generic
        AFTER UPDATE ON custom_data
        BEGIN
            UPDATE custom_data_fts SET
                category = new.category,
                key = new.key,
                value_text = new.value
            WHERE rowid=new.id;
        END;
    """)

    # Context Links
    op.execute("""
        CREATE TABLE context_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            workspace_id TEXT NOT NULL,
            source_item_type TEXT NOT NULL,
            source_item_id TEXT NOT NULL,
            target_item_type TEXT NOT NULL,
            target_item_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            description TEXT
        )
    """)

    # Product Context History
    op.execute("""
        CREATE TABLE product_context_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            version INTEGER NOT NULL,
            content TEXT NOT NULL,
            change_source TEXT
        )
    """)
    op.execute("CREATE INDEX idx_product_context_history_version ON product_context_history (version)")

    # Active Context History
    op.execute("""
        CREATE TABLE active_context_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            version INTEGER NOT NULL,
            content TEXT NOT NULL,
            change_source TEXT
        )
    """)
    op.execute("CREATE INDEX idx_active_context_history_version ON active_context_history (version)")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order of creation to respect foreign keys
    op.drop_table("active_context_history")
    op.drop_table("product_context_history")
    op.drop_table("context_links")

    # Drop FTS triggers first, then FTS tables, then source tables
    op.execute("DROP TRIGGER IF EXISTS custom_data_au_generic")
    op.execute("DROP TRIGGER IF EXISTS custom_data_ad_generic")
    op.execute("DROP TRIGGER IF EXISTS custom_data_ai_generic")
    op.execute("DROP VIRTUAL TABLE custom_data_fts")
    op.drop_table("custom_data")

    op.drop_table("system_patterns")
    op.drop_table("progress_entries")

    op.execute("DROP TRIGGER IF EXISTS decisions_au")
    op.execute("DROP TRIGGER IF EXISTS decisions_ad")
    op.execute("DROP TRIGGER IF EXISTS decisions_ai")
    op.execute("DROP VIRTUAL TABLE decisions_fts")
    op.drop_table("decisions")

    op.drop_table("active_context")
    op.drop_table("product_context")
