# Versioning (SCD2)

Columns:

- id
- row_hash
- date_created
- date_loaded
- is_current

Logic:

- new id → insert
- same id + same hash → skip
- same id + changed hash:
  - old row → is_current = false
  - new row → is_current = true
