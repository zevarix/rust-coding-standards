"""Synthetic SQLite tests supporting RCS-DB-001 and RCS-DB-002.

These test SQLite's documented transaction/schema properties, not a consumer
application's complete durability or physical-file safety contract.
No user databases, credentials, external services or third-party packages.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path


class SQLiteSafetyBoundaries(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="rcs-sqlite-fixture-")
        self.path = Path(self.temp.name) / "synthetic.db"
        self.db = sqlite3.connect(self.path, isolation_level=None)
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(
            "CREATE TABLE jobs (id INTEGER PRIMARY KEY, state TEXT NOT NULL, "
            "revision INTEGER NOT NULL);"
            "CREATE TABLE receipts (job_id INTEGER PRIMARY KEY "
            "REFERENCES jobs(id), proof BLOB NOT NULL);"
            "INSERT INTO jobs VALUES (1, 'verified', 2);"
        )

    def tearDown(self) -> None:
        self.db.close()
        self.temp.cleanup()

    def test_failed_second_statement_rolls_back_all_related_writes(self) -> None:
        self.db.execute("BEGIN IMMEDIATE")
        self.db.execute(
            "UPDATE jobs SET state='completed', revision=revision+1 "
            "WHERE id=1 AND state='verified' AND revision=2"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO receipts VALUES (?, ?)", (1, None))
        self.db.rollback()

        with closing(sqlite3.connect(self.path)) as reopened:
            self.assertEqual(
                reopened.execute(
                    "SELECT state, revision FROM jobs WHERE id=1"
                ).fetchone(),
                ("verified", 2),
            )
            self.assertEqual(
                reopened.execute("SELECT count(*) FROM receipts").fetchone()[0],
                0,
            )

    def test_stale_revision_cannot_silently_complete_again(self) -> None:
        self.db.execute("BEGIN IMMEDIATE")
        first = self.db.execute(
            "UPDATE jobs SET state='completed', revision=revision+1 "
            "WHERE id=1 AND state='verified' AND revision=2"
        )
        self.assertEqual(first.rowcount, 1)
        self.db.execute("INSERT INTO receipts VALUES (1, X'4142')")
        self.db.commit()

        self.db.execute("BEGIN IMMEDIATE")
        stale = self.db.execute(
            "UPDATE jobs SET state='completed', revision=revision+1 "
            "WHERE id=1 AND state='verified' AND revision=2"
        )
        self.assertEqual(stale.rowcount, 0)
        self.db.rollback()
        self.assertEqual(
            self.db.execute("SELECT revision FROM jobs WHERE id=1").fetchone(),
            (3,),
        )
        self.assertEqual(
            self.db.execute("SELECT proof FROM receipts WHERE job_id=1").fetchone(),
            (b"AB",),
        )

    def test_migration_history_does_not_prove_live_trigger(self) -> None:
        self.db.executescript(
            "CREATE TABLE migrations (version INTEGER PRIMARY KEY);"
            "INSERT INTO migrations VALUES (1);"
            "CREATE TRIGGER completion_guard BEFORE UPDATE ON jobs "
            "WHEN NEW.state='completed' AND NEW.revision <= OLD.revision "
            "BEGIN SELECT RAISE(ABORT, 'revision must advance'); END;"
        )
        self.assertIsNotNone(
            self.db.execute(
                "SELECT sql FROM sqlite_schema "
                "WHERE type='trigger' AND name='completion_guard'"
            ).fetchone()
        )
        self.db.execute("DROP TRIGGER completion_guard")
        self.assertEqual(
            self.db.execute("SELECT version FROM migrations").fetchall(), [(1,)]
        )
        self.assertIsNone(
            self.db.execute(
                "SELECT sql FROM sqlite_schema "
                "WHERE type='trigger' AND name='completion_guard'"
            ).fetchone()
        )

    def test_integrity_check_is_not_foreign_key_check(self) -> None:
        self.db.execute("PRAGMA foreign_keys = OFF")
        self.db.execute("INSERT INTO receipts VALUES (99, X'01')")
        self.db.execute("PRAGMA foreign_keys = ON")
        self.assertEqual(
            self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok"
        )
        self.assertNotEqual(
            self.db.execute("PRAGMA foreign_key_check").fetchall(), []
        )


if __name__ == "__main__":
    unittest.main()
