import sqlite3
import os
from datetime import datetime

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_db_path = os.path.join(base_dir, "移行前データ", "sakelia.db")
    target_db_path = os.path.join(base_dir, os.path.join("..", "database", "sake_database.db"))
    
    if not os.path.exists(source_db_path):
        print(f"Error: Source DB not found at {source_db_path}")
        return
        
    print(f"Connecting to source: {source_db_path}")
    source_conn = sqlite3.connect(source_db_path)
    source_conn.row_factory = sqlite3.Row
    
    print(f"Connecting to target: {target_db_path}")
    target_conn = sqlite3.connect(target_db_path)
    target_conn.row_factory = sqlite3.Row
    
    # 1. Ensure breweries table exists in target db
    target_conn.execute("""
    CREATE TABLE IF NOT EXISTS breweries (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        corporate_no   TEXT UNIQUE,
        name           TEXT NOT NULL,
        name_norm      TEXT NOT NULL,
        kura_name      TEXT,
        prefecture     TEXT NOT NULL,
        city           TEXT,
        address        TEXT,
        founded_year   INTEGER,
        website        TEXT,
        category       TEXT DEFAULT 'sake',
        description    TEXT,
        description_generated INTEGER DEFAULT 0,
        status         TEXT DEFAULT 'draft',
        confidence     REAL DEFAULT 0.0,
        source_id      TEXT,
        evidence       TEXT,
        created_at     TEXT,
        updated_at     TEXT,
        UNIQUE(name_norm, prefecture)
    )
    """)
    target_conn.commit()
    
    # 2. Import breweries
    print("Importing breweries...")
    source_cur = source_conn.cursor()
    source_cur.execute("SELECT * FROM breweries")
    breweries = source_cur.fetchall()
    
    for b in breweries:
        target_conn.execute("""
            INSERT INTO breweries (
                id, corporate_no, name, name_norm, kura_name, prefecture, city, 
                address, founded_year, website, category, description, 
                description_generated, status, confidence, source_id, evidence, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name_norm, prefecture) DO UPDATE SET
                name=excluded.name,
                corporate_no=excluded.corporate_no,
                kura_name=excluded.kura_name,
                city=excluded.city,
                address=excluded.address,
                founded_year=excluded.founded_year,
                website=excluded.website,
                category=excluded.category,
                description=excluded.description,
                status=excluded.status,
                confidence=excluded.confidence,
                updated_at=excluded.updated_at
        """, (
            b['id'], b['corporate_no'], b['name'], b['name_norm'], b['kura_name'], 
            b['prefecture'], b['city'], b['address'], b['founded_year'], b['website'], 
            b['category'], b['description'], b['description_generated'], b['status'], 
            b['confidence'], b['source_id'], b['evidence'], b['created_at'], b['updated_at']
        ))
    target_conn.commit()
    print(f"Imported/Updated {len(breweries)} breweries.")
    
    # 3. Build memory index of existing target products
    print("Indexing existing products in target DB...")
    target_cur = target_conn.cursor()
    target_cur.execute("SELECT id, brand_name, brewery_name, spec_name FROM products")
    existing_products = target_cur.fetchall()
    
    existing_by_brand_brewery = {}
    existing_by_brand_spec = {}
    existing_by_brand = {}
    
    for p in existing_products:
        pid = p['id']
        b_name = p['brand_name'] or ''
        br_name = p['brewery_name'] or ''
        s_name = p['spec_name'] or ''
        
        if b_name:
            existing_by_brand.setdefault(b_name, pid)
            if br_name:
                existing_by_brand_brewery[(b_name, br_name)] = pid
            if s_name:
                existing_by_brand_spec[(b_name, s_name)] = pid

    # 4. Import all 6,769 brands (with specs if present) from sakelia.db
    print("Importing brands & products from sakelia.db...")
    query = """
    SELECT 
        b.id as brand_id,
        b.name as brand_name,
        br.name as brewery_name,
        p.spec_name,
        p.category,
        p.ingredients,
        p.polish_ratio,
        p.rice_variety,
        p.yeast,
        p.alcohol,
        p.smv,
        p.acidity,
        p.amino_acidity,
        COALESCE(p.status, b.status, 'draft') as status,
        COALESCE(p.confidence, b.confidence, 0.8) as confidence,
        COALESCE(p.source_id, b.source_id, 'migrated_brands_only') as source_id,
        COALESCE(p.evidence, b.evidence, 'imported brand names from sakelia.db') as evidence
    FROM brands b
    LEFT JOIN breweries br ON b.brewery_id = br.id
    LEFT JOIN products p ON p.brand_id = b.id
    """
    source_cur.execute(query)
    all_brands = source_cur.fetchall()
    
    inserted_count = 0
    updated_count = 0
    now = datetime.now().isoformat()
    
    for r in all_brands:
        brand_name = r['brand_name'] or ''
        brewery_name = r['brewery_name'] or ''
        spec_name = r['spec_name'] if r['spec_name'] else brand_name
        
        # Match existing PID
        existing_id = None
        if (brand_name, brewery_name) in existing_by_brand_brewery:
            existing_id = existing_by_brand_brewery[(brand_name, brewery_name)]
        elif (brand_name, spec_name) in existing_by_brand_spec:
            existing_id = existing_by_brand_spec[(brand_name, spec_name)]
        elif brand_name in existing_by_brand:
            existing_id = existing_by_brand[brand_name]
            
        polish_str = str(r['polish_ratio']) if r['polish_ratio'] is not None else None
        smv_str = str(r['smv']) if r['smv'] is not None else None
        acidity_str = str(r['acidity']) if r['acidity'] is not None else None
        amino_str = str(r['amino_acidity']) if r['amino_acidity'] is not None else None
        
        if existing_id:
            # Update
            try:
                target_cur.execute("""
                    UPDATE products SET
                        brewery_name = COALESCE(NULLIF(?, ''), brewery_name),
                        category = COALESCE(?, category),
                        ingredients = COALESCE(?, ingredients),
                        polish_ratio = COALESCE(?, polish_ratio),
                        rice_variety = COALESCE(?, rice_variety),
                        yeast = COALESCE(?, yeast),
                        alcohol = COALESCE(?, alcohol),
                        smv = COALESCE(?, smv),
                        acidity = COALESCE(?, acidity),
                        amino_acidity = COALESCE(?, amino_acidity)
                    WHERE id = ?
                """, (
                    brewery_name, r['category'], r['ingredients'],
                    polish_str, r['rice_variety'], r['yeast'], r['alcohol'],
                    smv_str, acidity_str, amino_str,
                    existing_id
                ))
                updated_count += 1
            except Exception as e:
                pass
        else:
            # Insert
            target_cur.execute("""
                INSERT OR IGNORE INTO products (
                    spec_name, brand_name, brewery_name, category, ingredients, polish_ratio,
                    rice_variety, yeast, alcohol, smv, acidity, amino_acidity, status,
                    confidence, source_id, evidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                spec_name, brand_name, brewery_name, r['category'], r['ingredients'],
                polish_str, r['rice_variety'], r['yeast'], r['alcohol'],
                smv_str, acidity_str, amino_str, r['status'],
                r['confidence'], r['source_id'], r['evidence'], now
            ))
            inserted_count += 1
            
    target_conn.commit()
    print(f"Import complete! Total sakelia entries: {len(all_brands)}")
    print(f"Inserted new: {inserted_count}, Updated existing: {updated_count}")
    
    # 5. Import Competitions, Competition Events, and Awards
    print("Importing competitions & awards...")
    target_conn.execute("""
    CREATE TABLE IF NOT EXISTS competitions (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT NOT NULL UNIQUE,
        country  TEXT,
        website  TEXT,
        founded_year INTEGER,
        organizer TEXT,
        description TEXT
    )
    """)
    target_conn.execute("""
    CREATE TABLE IF NOT EXISTS competition_events (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        competition_id  INTEGER NOT NULL,
        year            INTEGER NOT NULL,
        edition_label   TEXT,
        held_start      TEXT,
        held_end        TEXT,
        announced_date  TEXT,
        venue           TEXT,
        country         TEXT,
        entries_total   INTEGER,
        countries_count INTEGER,
        judges_count    INTEGER,
        judges_note     TEXT,
        trophy_count    INTEGER,
        platinum_count  INTEGER,
        gold_count      INTEGER,
        website         TEXT,
        status          TEXT DEFAULT 'draft',
        confidence      REAL DEFAULT 0.0,
        source_id       TEXT,
        evidence        TEXT,
        UNIQUE(competition_id, year)
    )
    """)
    target_conn.execute("""
    CREATE TABLE IF NOT EXISTS awards (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        competition_id  INTEGER NOT NULL,
        year            INTEGER NOT NULL,
        category        TEXT,
        prize           TEXT NOT NULL,
        entry_name      TEXT NOT NULL,
        brand_id        INTEGER,
        product_id      INTEGER,
        brewery_id      INTEGER,
        status          TEXT DEFAULT 'draft',
        confidence      REAL DEFAULT 0.0,
        source_id       TEXT,
        evidence        TEXT,
        UNIQUE(competition_id, year, prize, entry_name)
    )
    """)
    target_conn.commit()

    # Copy Competitions
    source_cur.execute("SELECT * FROM competitions")
    for c in source_cur.fetchall():
        target_conn.execute("""
            INSERT INTO competitions (id, name, country, website, founded_year, organizer, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                country=excluded.country, website=excluded.website,
                founded_year=excluded.founded_year, organizer=excluded.organizer, description=excluded.description
        """, (c['id'], c['name'], c['country'], c['website'], c['founded_year'], c['organizer'], c['description']))

    # Copy Competition Events
    source_cur.execute("SELECT * FROM competition_events")
    for ce in source_cur.fetchall():
        target_conn.execute("""
            INSERT INTO competition_events (
                id, competition_id, year, edition_label, held_start, held_end, announced_date,
                venue, country, entries_total, countries_count, judges_count, judges_note,
                trophy_count, platinum_count, gold_count, website, status, confidence, source_id, evidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(competition_id, year) DO UPDATE SET
                edition_label=excluded.edition_label, venue=excluded.venue, entries_total=excluded.entries_total,
                gold_count=excluded.gold_count, website=excluded.website
        """, (
            ce['id'], ce['competition_id'], ce['year'], ce['edition_label'], ce['held_start'], ce['held_end'],
            ce['announced_date'], ce['venue'], ce['country'], ce['entries_total'], ce['countries_count'],
            ce['judges_count'], ce['judges_note'], ce['trophy_count'], ce['platinum_count'], ce['gold_count'],
            ce['website'], ce['status'], ce['confidence'], ce['source_id'], ce['evidence']
        ))

    # Copy Awards
    source_cur.execute("SELECT * FROM awards")
    awards_rows = source_cur.fetchall()
    for a in awards_rows:
        target_conn.execute("""
            INSERT INTO awards (
                id, competition_id, year, category, prize, entry_name, brand_id, product_id, brewery_id, status, confidence, source_id, evidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(competition_id, year, prize, entry_name) DO UPDATE SET
                category=excluded.category, brand_id=excluded.brand_id, product_id=excluded.product_id
        """, (
            a['id'], a['competition_id'], a['year'], a['category'], a['prize'], a['entry_name'],
            a['brand_id'], a['product_id'], a['brewery_id'], a['status'], a['confidence'], a['source_id'], a['evidence']
        ))

    target_conn.commit()
    print(f"Competitions, events, and {len(awards_rows)} awards imported successfully!")
    
    # Final count check
    target_cur.execute("SELECT COUNT(*) FROM products")
    total_products = target_cur.fetchone()[0]
    print(f"Final products count in sake_database.db: {total_products}")
    
    source_conn.close()
    target_conn.close()

if __name__ == "__main__":
    main()
