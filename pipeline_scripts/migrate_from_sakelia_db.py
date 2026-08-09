import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DB = os.path.join(ROOT_DIR, "Claudeから移行", "sakelia-pipeline", "db", "sakelia.db")
DST_DB = os.path.join(ROOT_DIR, "database", "sake_database.db")

print(f"=== 📦 Migration from sakelia.db to sake_database.db ===")
print(f"Source DB: {SRC_DB}")
print(f"Destination DB: {DST_DB}\n")

if not os.path.exists(SRC_DB):
    print(f"❌ Error: Source DB does not exist at {SRC_DB}")
    sys.exit(1)

conn_src = sqlite3.connect(SRC_DB)
conn_dst = sqlite3.connect(DST_DB)

cur_src = conn_src.cursor()
cur_dst = conn_dst.cursor()

# 1. Create missing tables in destination DB if needed
tables_to_migrate = [
    'sources',
    'breweries',
    'brewery_aliases',
    'brands',
    'competitions',
    'competition_events',
    'awards',
    'merge_candidates'
]

for tbl in tables_to_migrate:
    # Get table schema from source
    cur_src.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{tbl}'")
    row = cur_src.fetchone()
    if row and row[0]:
        create_sql = row[0]
        cur_dst.execute(f"CREATE TABLE IF NOT EXISTS {tbl} " + create_sql[create_sql.find('('):])

conn_dst.commit()

# 2. Migrate breweries (UPSERT by id)
cur_src.execute("SELECT id, corporate_no, name, name_norm, kura_name, prefecture, city, address, founded_year, website, category, description, description_generated, status, confidence, source_id, evidence, created_at, updated_at FROM breweries")
b_rows = cur_src.fetchall()
print(f"Migrating {len(b_rows)} breweries...")

cur_dst.executemany("""
    INSERT INTO breweries (id, corporate_no, name, name_norm, kura_name, prefecture, city, address, founded_year, website, category, description, description_generated, status, confidence, source_id, evidence, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        corporate_no=excluded.corporate_no,
        name=excluded.name,
        name_norm=excluded.name_norm,
        kura_name=excluded.kura_name,
        prefecture=excluded.prefecture,
        city=excluded.city,
        address=excluded.address,
        founded_year=excluded.founded_year,
        website=excluded.website,
        category=excluded.category,
        description=excluded.description,
        description_generated=excluded.description_generated,
        status=excluded.status,
        confidence=excluded.confidence,
        source_id=excluded.source_id,
        evidence=excluded.evidence,
        created_at=excluded.created_at,
        updated_at=excluded.updated_at
""", b_rows)
print(f" ✅ Breweries upserted: {len(b_rows)} rows")

# 3. Migrate brands (Replace/UPSERT by id)
cur_src.execute("SELECT id, brewery_id, name, name_kana, name_en, status, confidence, source_id, evidence FROM brands")
brand_rows = cur_src.fetchall()
print(f"Migrating {len(brand_rows)} brands...")

cur_dst.executemany("""
    INSERT INTO brands (id, brewery_id, name, name_kana, name_en, status, confidence, source_id, evidence)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        brewery_id=excluded.brewery_id,
        name=excluded.name,
        name_kana=excluded.name_kana,
        name_en=excluded.name_en,
        status=excluded.status,
        confidence=excluded.confidence,
        source_id=excluded.source_id,
        evidence=excluded.evidence
""", brand_rows)
print(f" ✅ Brands upserted: {len(brand_rows)} rows")

# 4. Migrate competitions
cur_src.execute("SELECT id, name, country, website, founded_year, organizer, description FROM competitions")
c_rows = cur_src.fetchall()
cur_dst.executemany("""
    INSERT INTO competitions (id, name, country, website, founded_year, organizer, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name=excluded.name, country=excluded.country, website=excluded.website,
        founded_year=excluded.founded_year, organizer=excluded.organizer, description=excluded.description
""", c_rows)

# 5. Migrate competition_events
cur_src.execute("SELECT id, competition_id, year, edition_label, held_start, held_end, announced_date, venue, country, entries_total, countries_count, judges_count, judges_note, trophy_count, platinum_count, gold_count, website, status, confidence, source_id, evidence FROM competition_events")
ce_rows = cur_src.fetchall()
cur_dst.executemany("""
    INSERT INTO competition_events (id, competition_id, year, edition_label, held_start, held_end, announced_date, venue, country, entries_total, countries_count, judges_count, judges_note, trophy_count, platinum_count, gold_count, website, status, confidence, source_id, evidence)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        competition_id=excluded.competition_id, year=excluded.year, edition_label=excluded.edition_label,
        held_start=excluded.held_start, held_end=excluded.held_end, announced_date=excluded.announced_date,
        venue=excluded.venue, country=excluded.country, entries_total=excluded.entries_total,
        countries_count=excluded.countries_count, judges_count=excluded.judges_count, judges_note=excluded.judges_note,
        trophy_count=excluded.trophy_count, platinum_count=excluded.platinum_count, gold_count=excluded.gold_count,
        website=excluded.website, status=excluded.status, confidence=excluded.confidence,
        source_id=excluded.source_id, evidence=excluded.evidence
""", ce_rows)

# 6. Migrate awards
cur_src.execute("SELECT id, competition_id, year, category, prize, entry_name, brand_id, product_id, brewery_id, status, confidence, source_id, evidence FROM awards")
a_rows = cur_src.fetchall()
cur_dst.executemany("""
    INSERT INTO awards (id, competition_id, year, category, prize, entry_name, brand_id, product_id, brewery_id, status, confidence, source_id, evidence)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        competition_id=excluded.competition_id, year=excluded.year, category=excluded.category,
        prize=excluded.prize, entry_name=excluded.entry_name, brand_id=excluded.brand_id,
        product_id=excluded.product_id, brewery_id=excluded.brewery_id, status=excluded.status,
        confidence=excluded.confidence, source_id=excluded.source_id, evidence=excluded.evidence
""", a_rows)

# 7. Migrate sources
cur_src.execute("SELECT id, name, url, fetched_at, raw_path, license_note FROM sources")
s_rows = cur_src.fetchall()
cur_dst.executemany("""
    INSERT INTO sources (id, name, url, fetched_at, raw_path, license_note)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name=excluded.name, url=excluded.url, fetched_at=excluded.fetched_at, raw_path=excluded.raw_path, license_note=excluded.license_note
""", s_rows)

# 8. Migrate merge_candidates & brewery_aliases
cur_src.execute("SELECT id, entity, keep_id, merge_id, reason, score, decided FROM merge_candidates")
mc_rows = cur_src.fetchall()
cur_dst.executemany("""
    INSERT INTO merge_candidates (id, entity, keep_id, merge_id, reason, score, decided)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        entity=excluded.entity, keep_id=excluded.keep_id, merge_id=excluded.merge_id,
        reason=excluded.reason, score=excluded.score, decided=excluded.decided
""", mc_rows)

cur_src.execute("SELECT id, brewery_id, alias, alias_type, source_id FROM brewery_aliases")
ba_rows = cur_src.fetchall()
cur_dst.executemany("""
    INSERT INTO brewery_aliases (id, brewery_id, alias, alias_type, source_id)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        brewery_id=excluded.brewery_id, alias=excluded.alias, alias_type=excluded.alias_type, source_id=excluded.source_id
""", ba_rows)

conn_dst.commit()
print(" ✅ Synchronized competitions, events, awards, sources, merge_candidates, and aliases successfully!")

# Summary of destination DB
print("\n=== 🏛️ Destination DB Summary after Migration ===")
cur_dst.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables_dst = [r[0] for r in cur_dst.fetchall()]
for t in tables_dst:
    cur_dst.execute(f"SELECT count(*) FROM {t}")
    print(f" - {t:<20}: {cur_dst.fetchone()[0]} rows")

conn_src.close()
conn_dst.close()
print("\n✨ Migration completed successfully!")
