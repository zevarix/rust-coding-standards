# SQLite state and native filesystem paths

These rules matter when an application persists consequential state or translates filesystem paths into identities. They are **conditional**; a pure calculation crate has no need to adopt a SQLite persistence contract.

## RCS-DB-001 — Commit related state transitions atomically {#rcs-db-001--commit-related-state-transitions-atomically}

**Level:** Required when a database operation must change several records together, preserve a previous state on error, or prevent a stale writer from completing an effect.

**Enforcement:** Trace the full write transaction and expected-state guard; test concurrent/stale revisions, failure between statements and reopened state.

### Requirement

Group one logical effect's related writes in one transaction with an explicit success condition. Check expected version/state and affected-row counts; a successful SQL statement is not proof that it updated the intended record. If a statement fails or a compare-and-swap guard does not match, fail the transition without persisting a partial completion. Choose `BEGIN IMMEDIATE` when competing SQLite writers make early reservation of the write transaction appropriate; do not mandate it for every read-only query.

**Avoid** committing the completion claim separately from its evidence:

```rust
connection.execute("UPDATE jobs SET state='completed' WHERE id=?1", [job_id])?;
connection.execute("INSERT INTO receipts (job_id, proof) VALUES (?1, ?2)", (job_id, proof))?;
// The first update may already be committed if the second insert fails.
```

**Prefer** an application transaction with an expected-state guard (illustrative `rusqlite` example; table definitions and domain errors belong to the consumer):

```rust
use rusqlite::{params, Connection, TransactionBehavior};

fn record_completion(
    connection: &mut Connection,
    job_id: i64,
    expected_revision: i64,
    proof: &[u8],
) -> Result<(), Box<dyn std::error::Error>> {
    let tx = connection.transaction_with_behavior(TransactionBehavior::Immediate)?;
    let changed = tx.execute(
        "UPDATE jobs SET state='completed', revision=revision+1
         WHERE id=?1 AND state='verified' AND revision=?2",
        params![job_id, expected_revision],
    )?;
    if changed != 1 {
        return Err("stale or unknown job state".into()); // tx rolls back when dropped
    }
    tx.execute(
        "INSERT INTO receipts (job_id, proof) VALUES (?1, ?2)",
        params![job_id, proof],
    )?;
    tx.commit()?;
    Ok(())
}
```

The example establishes **atomic database recording**, not physical output integrity. The caller still must prove that `proof` represents the current verified effect and that a completion claim cannot outlive its required physical evidence.

### Reviewer check

Trace every database write for one operation, including helper calls. Verify one owning transaction, expected-generation/state guard, uniqueness constraints, error rollback, and durable readback where required. With synthetic SQLite, inject an error after the first statement; reopen and prove neither completion nor an orphan receipt survived. Exercise two writers with the same prior generation: one may succeed but the stale second must not silently overwrite it.

**Exceptions:** Independent idempotent updates need not share a transaction solely because they happen in the same function. The owning application decides when a multi-record invariant exists.

**Source:** [SQLite transactions](https://www.sqlite.org/lang_transaction.html).

## RCS-DB-002 — Qualify the live schema and recovery invariants {#rcs-db-002--qualify-the-live-schema-and-recovery-invariants}

**Level:** Required when program correctness or durability relies on SQLite migrations, triggers, constraints, indexes, foreign keys or persisted receipts.

**Enforcement:** Open/reopen tests against fresh, migrated, incomplete and deliberately modified test databases; schema introspection and constraint checks.

### Requirement

Recording migration numbers or checksums proves migration history, **not necessarily that the current database still contains the required enforcement objects**. When correctness relies on a trigger, index, table or particular DDL shape, inspect the live reopened SQLite schema and fail on missing or incompatible definitions. Enable foreign-key enforcement on each connection **outside a transaction**, verify that it is active, and independently inspect foreign-key violations when the application requires it. Preserve durable user truth and recover or reject unknown states explicitly.

**Avoid** treating migration history alone as proof that a required trigger still exists:

```rust
if migrations_match_history(&db)? {
    mark_schema_safe(&db)?; // The trigger might have been dropped later.
}
```

**Prefer** the following sequence (application pseudocode, not a universal schema fingerprint):

```text
open connection -> configure required SQLite PRAGMAs outside transactions
  -> validate recorded migration lineage and integrity
  -> inspect sqlite_schema for exact required tables/indexes/triggers/DDL
  -> check enabled foreign keys and foreign_key_check where relevant
  -> reject missing, weakened or ambiguous schema
  -> only then permit protected persistence operations
```

An index that serves only performance may be an optimization rather than a hard recovery gate; qualify the exact schema objects that actually enforce safety or correctness. SQLite `PRAGMA integrity_check` does **not** substitute for `PRAGMA foreign_key_check`, and integrity tests cannot establish application-level semantics by themselves.

### Reviewer check

Identify the source of each invariant (DDL, transaction, application check, or physical file). In a **temporary synthetic database**, initialize and reopen it, then drop or weaken one required trigger/index; verify a subsequent application open refuses unsafe work even if the migration table still looks valid. Test foreign keys off, corrupt or orphan records, failed migrations and newer unknown schema versions. Never mutate a real user's database to perform these checks.

**Exception:** A disposable rebuildable cache that does not rely on such schema objects may require much lighter qualification. Do not demand archive-grade migration provenance for every small SQLite application.

**Sources:** [SQLite schema table](https://www.sqlite.org/schematab.html), [SQLite PRAGMAs and foreign-key checks](https://www.sqlite.org/pragma.html).

## RCS-PATH-001 — Do not confuse pathname text with filesystem identity {#rcs-path-001--do-not-confuse-pathname-text-with-filesystem-identity}

**Level:** Required when native filesystem paths select consequential sources/targets, determine ownership, or drive deduplication and no-clobber decisions.

**Enforcement:** Platform-aware review, synthetic Unicode/invalid-name/symlink/case tests and fresh native object/namespace identity checks where necessary.

### Requirement

Preserve filenames as `Path`, `PathBuf`, `OsStr` or `OsString` across native filesystem boundaries. Do not use lossy Unicode conversion, manual `to_lowercase` or ad hoc slash replacement as proof two paths identify the same physical object. Case behavior, normalization, mounted namespaces, symbolic links and reparse points differ by filesystem and can change between observation and effect.

**Avoid** treating a display label as an authoritative path key:

```rust
let key = path.to_string_lossy().to_lowercase();
// Different paths may collapse to one lossy string; one path may refer to changing objects.
```

**Prefer** preserving the original native representation separately from portable labels or database IDs:

<!-- rcs-example: test -->
```rust
use std::{ffi::OsStr, path::{Path, PathBuf}};

pub struct SourceLocation {
    original_path: PathBuf,
}

impl SourceLocation {
    pub fn new(path: PathBuf) -> Self {
        Self { original_path: path }
    }

    pub fn native_path(&self) -> &Path {
        &self.original_path
    }
}

#[test]
fn preserves_native_components_without_text_rewriting() {
    let original = PathBuf::from("synthetic").join("item.dat");
    let source = SourceLocation::new(original.clone());
    assert_eq!(source.native_path().file_name(), Some(OsStr::new("item.dat")));
    assert_eq!(source.native_path(), original.as_path());
}
```

Retaining the original native path is a **representation property, not a physical identity proof**. A safe read or write still needs the platform-appropriate currently held file handle, file identity, parent namespace and collision guarantees required by its owning product. `canonicalize` resolves a pathname at one moment; it does not make a future operation race-free.

### Reviewer check

Trace user input → path storage → logical/portable IDs → actual filesystem call. Look for lossy conversions, guessed lowercasing, stale canonical paths, ancestor replacement and incorrect case assumptions. Use synthetic fixture names and platform-appropriate checks to validate actual Windows/Unix behavior; do not declare cross-platform acceptance from one OS.

**Exception:** Lossy formatting may be acceptable in non-authoritative logs or UI where the original native path is still retained separately. Portable display aliases can be normalized as long as they are never substituted for filesystem identity.

**Sources:** [Rust `std::path`](https://doc.rust-lang.org/std/path/), [Rust `OsString`](https://doc.rust-lang.org/std/ffi/struct.OsString.html).

[Back to standards index](../standards.md).
