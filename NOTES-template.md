## Feature: Alembic Migration

### What does it do?
Allows for hotswap of the database schema without needing to wipe the entire database.

### What needs to change?
- [ ] Database: allow for hotswap
- [ ] Model: database needs to be hotswappable
- [ ] Route: no change
- [x] Template: no change
- [ ] Tests: adding/subtracting of columns, hotswap modify column type successful

### Edge cases
- migration fails halfway - database left in inconsistent state
- downgrading a migration that deleted data - data is gone forever
- two developers creating migration at the same time - conflict in version chain
- migrating a table that has existing data - must hand null for new columns
- SQLite has limited ALTER TABLE support - can't drop or rename column directly,Alembic works around this by recreating the table 

### What does done look like?
- Alembic installed and initialized in project
- existing schema converted to initial migration
- new columns/tables can be added via migration files instead of wiping DB
- `alembic upgrade head` applies all pending migrations
- `alembic downgrade -1` rolls back one migration
- CI runs migrations before tests