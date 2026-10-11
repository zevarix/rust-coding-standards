# Filesystem identity and completed effects

These rules apply when an application makes consequential changes to mutable external state. They do not require a pure library or a read-only parser to invent an approval system.

## RCS-FS-001 — Recheck mutable filesystem targets before consequential effects {#rcs-fs-001--recheck-mutable-filesystem-targets-before-consequential-effects}

**Level:** Required when an earlier filesystem observation is relied on to create, replace, rename, publish, or remove user-owned data.

**Enforcement:** Trace the observation → actual file operation call path; platform-specific identity/namespace tests and collision/race tests when appropriate.

### Requirement

A path or metadata observation can become stale before a later operation. Check the **actual object, containing namespace and intended target identity** at the point the owning project's safety contract requires. A name or existence check alone is not permission to overwrite. Use native handles or platform-specific operations when required by the threat model.

**Avoid** treating two separate operations as an atomic no-clobber action:

```rust
if !path.exists() {
    std::fs::write(path, bytes)?;
}
```

**Prefer** an exclusive creation primitive for the narrow case of creating a new file where its parent and permission are already trusted:

```rust
use std::{fs::{File, OpenOptions}, io, path::Path};

pub fn create_absent(path: &Path) -> io::Result<File> {
    OpenOptions::new().write(true).create_new(true).open(path)
}
```

**This is not a complete secure archive writer.** Even a successful `create_new` call does not prove that the ancestry is trusted, an archive has sufficient space, the final output is durable, or the user approved a consequential operation. Those are separate duties where the application requires them.

### Reviewer check

- Identify the exact target and which prior observation supposedly authorizes it.
- Look for a mutable pathname, symlink, mount, case-folding or parent replacement between observation and effect.
- Check that necessary native object/path revalidation is retained; do not introduce redundant full-file hashes when identity can be safely established through a held native object.
- Test an existing destination, redirected parent or changed source using owned synthetic fixtures. Do not run destructive probes on users' real collections.

**Source:** [`OpenOptions::create_new` and its atomic creation guarantee](https://doc.rust-lang.org/std/fs/struct.OpenOptions.html#method.create_new).

## RCS-STATE-001 — Do not register an effect as complete before verification {#rcs-state-001--do-not-register-an-effect-as-complete-before-verification}

**Level:** Required for workflows where downstream consumers rely on recorded completion of a file write, export, migration, or other externally observable effect.

**Enforcement:** Review the state transition and receipt semantics; focused interruption and corruption tests.

### Requirement

Separate **requested**, **staged**, **verified**, and **completed/registered** states to the extent the effect actually needs them. A successful write call is not proof that bytes are correct, persisted, or safe to publish. When the product requires content identity, verify the actual output before persisting a completion claim.

**Avoid:**

```rust
copy_file(source, destination)?;
mark_completed(destination)?; // No output validation happened.
```

**Prefer the explicit sequence** below (illustrative application calls, not a standalone library):

```rust
let staged = copy_to_staging(source, destination)?;
let verified = verify_staged_output(staged, expected_sha256)?;
register_completed_output(verified)?;
```

The verifier must produce evidence from the **current output bytes**, not from the intended plan, cached source hash, or a caller-supplied boolean. Registering and publishing may need further crash-consistency guarantees owned by the product.

### Reviewer check

Find the earliest point downstream code can observe `Complete`. Prove the code cannot reach it through an error, partial write, canceled operation, or unverifiable output. Test corruption or interruption between staging and registration, and verify that false completion is not persisted.

**Exception:** A best-effort, reversible cache with no meaningful completion contract may have a simpler lifecycle; reviewers should not force archive-grade machinery onto it.

## RCS-STATE-002 — Reconcile uncertain effects before retrying them {#rcs-state-002--reconcile-uncertain-effects-before-retrying-them}

**Level:** Required when a failed/expired acknowledgment may conceal an already-performed consequential operation.

**Enforcement:** Fault injection or synthetic interruption tests; audit of replay and durable receipt handling.

### Requirement

An error, timeout, process exit, or missing response is not automatically proof that no effect occurred. Before retrying a potentially destructive or non-idempotent operation, inspect durable state under current identity constraints and distinguish **confirmed complete**, **confirmed absent**, and **uncertain** outcomes.

**Avoid** immediately replaying solely because a request returned an error:

```rust
if send_write_request().is_err() {
    send_write_request()?; // The first request may already have succeeded.
}
```

**Prefer a reconciliation decision** (illustrative pseudocode):

```rust
match inspect_actual_effect(effect_id)? {
    Effect::Verified(receipt) => reuse_verified_receipt(receipt),
    Effect::Absent => apply_once_and_verify(),
    Effect::Uncertain => Err(Error::NeedsReconciliation),
}
```

A retried operation can also be safe when the operation is *proven idempotent* and its invariants hold for replays; document that proof rather than forcing an unnecessary elaborate recovery state machine.

### Reviewer check

Identify the acknowledgment boundary, what might have happened before failure, whether a durable receipt exists, and whether a duplicate effect would corrupt state. Test interruption on both sides of the consequential effect and verify that an unknown outcome never becomes automatic success.

**Exception:** A genuinely read-only observation or proven replay-safe action has different retry requirements.
