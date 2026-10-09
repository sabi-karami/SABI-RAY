# Safe configuration changes

This release targets a NEW installation, not migration of existing SuperJinx databases.

SABI-RAY stores an installation identifier, selected profiles, domain and deployment role on the volume. On restart it refuses to silently change these; it never rewrites an existing owner's password. Do not delete state files to bypass this check on an active installation.

Before a change:
1. Back up the database consistently and separately back up the complete volume (including node keys and deployment state) while stopped. Keep backups private and encrypted.
2. Rehearse restoration into an isolated NEW volume using the same image and domain configuration. Do not point a test clone at production nodes.
3. For domains/core changes in this alpha, use a new installation and explicitly recreate users or wait for a tested migration tool. Automatic migration and rollback across database schema versions are NOT implemented.
4. Do not restore an old image onto a database already migrated by a newer upstream release without a matching database backup.

`python -m sabi_ray.backup --output /var/lib/pasarguard/backups/database-YYYYMMDD.sqlite3` creates a verified SQLite database copy. It is not a full-volume or off-site backup, and it is not automatically scheduled.
