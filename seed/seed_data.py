import mysql.connector
from mysql.connector import Error


def main():
    conn = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Qwerty@69",
            database="crm_db"
        )
        cursor = conn.cursor()

        # Truncate all tables to keep ids predictable and avoid FK issues
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        for tbl in [
            "activities",
            "opportunity_stage_history",
            "opportunities",
            "leads",
            "contacts",
            "customers",
            "stages",
            "sources",
            "users",
        ]:
            cursor.execute(f"TRUNCATE TABLE {tbl}")
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        conn.commit()

        # ========== Users ==========
        users_data = [
            ("Alice Rep", "alice.rep@example.com", "REP"),
            ("Bob Rep", "bob.rep@example.com", "REP"),
            ("Carol Manager", "carol.manager@example.com", "MANAGER"),
            ("Dave Manager", "dave.manager@example.com", "MANAGER"),
            ("Eve Admin", "eve.admin@example.com", "ADMIN"),
        ]
        user_ids = []
        for row in users_data:
            cursor.execute(
                "INSERT INTO users (name, email, role) VALUES (%s, %s, %s)",
                row,
            )
            user_ids.append(cursor.lastrowid)
        conn.commit()

        # ========== Sources ==========
        sources_data = [("Web",), ("Referral",), ("Outbound",), ("Event",), ("Partner",)]
        source_ids = []
        for row in sources_data:
            cursor.execute("INSERT INTO sources (name) VALUES (%s)", row)
            source_ids.append(cursor.lastrowid)
        conn.commit()

        # ========== Stages ==========
        stages_data = [
            ("Prospecting", 1),
            ("Qualification", 2),
            ("Proposal", 3),
            ("Negotiation", 4),
            ("Closed", 5),
        ]
        stage_ids = []
        for row in stages_data:
            cursor.execute(
                "INSERT INTO stages (name, stage_order) VALUES (%s, %s)", row
            )
            stage_ids.append(cursor.lastrowid)
        conn.commit()

        # ========== Customers ==========
        customers_data = [
            ("Acme Corp", "Acme Industries", "contact@acme.com", "1111111111", user_ids[0]),
            ("Globex LLC", "Globex", "sales@globex.com", "2222222222", user_ids[1]),
            ("Initech", "Initech Ltd", "info@initech.com", "3333333333", user_ids[2]),
            ("Umbrella Co", "Umbrella Co", "hello@umbrella.com", "4444444444", user_ids[3]),
            ("Soylent", "Soylent Corp", "team@soylent.com", "5555555555", user_ids[0]),
        ]
        customer_ids = []
        for row in customers_data:
            cursor.execute(
                "INSERT INTO customers (name, company, email, phone, owner_id) VALUES (%s, %s, %s, %s, %s)",
                row,
            )
            customer_ids.append(cursor.lastrowid)
        conn.commit()

        # ========== Contacts ==========
        contacts_data = [
            (customer_ids[0], "John Doe", "john.doe@acme.com", "1111000001", "CTO"),
            (customer_ids[0], "Jane Roe", "jane.roe@acme.com", "1111000002", "PM"),
            (customer_ids[1], "Mike Swift", "mike.swift@globex.com", "2222000001", "CFO"),
            (customer_ids[2], "Pam Beez", "pam.beez@initech.com", "3333000001", "Director"),
            (customer_ids[3], "Luke Shaw", "luke.shaw@umbrella.com", "4444000001", "Engineer"),
            (customer_ids[4], "Nina Park", "nina.park@soylent.com", "5555000001", "Head of Ops"),
            (customer_ids[2], "Oscar Diaz", "oscar.diaz@initech.com", "3333000002", "VP Sales"),
        ]
        for row in contacts_data:
            cursor.execute(
                "INSERT INTO contacts (customer_id, name, email, phone, role) VALUES (%s, %s, %s, %s, %s)",
                row,
            )
        conn.commit()

        # ========== Leads ==========
        leads_data = [
            ("Lead A", "lead.a@example.com", "9000000001", user_ids[0], source_ids[0], "QUALIFIED", 72),
            ("Lead B", "lead.b@example.com", "9000000002", user_ids[1], source_ids[1], "CONTACTED", 45),
            ("Lead C", "lead.c@example.com", "9000000003", user_ids[0], source_ids[2], "QUALIFIED", 80),
            ("Lead D", "lead.d@example.com", "9000000004", user_ids[2], source_ids[3], "NEW", 20),
            ("Lead E", "lead.e@example.com", "9000000005", user_ids[3], source_ids[4], "QUALIFIED", 65),
            ("Lead F", "lead.f@example.com", "9000000006", user_ids[1], source_ids[0], "CONTACTED", 50),
        ]
        lead_ids = []
        for row in leads_data:
            cursor.execute(
                "INSERT INTO leads (name, email, phone, owner_id, source_id, status, lead_score) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                row,
            )
            lead_ids.append(cursor.lastrowid)
        conn.commit()

        # ========== Opportunities ==========
        opportunities_data = [
            (lead_ids[0], customer_ids[0], user_ids[0], stage_ids[2], 15000.00, "OPEN", None),
            (lead_ids[1], customer_ids[1], user_ids[1], stage_ids[3], 25000.00, "OPEN", None),
            (lead_ids[2], customer_ids[2], user_ids[0], stage_ids[4], 50000.00, "WON", "2025-03-15 10:00:00"),
            (lead_ids[3], customer_ids[3], user_ids[2], stage_ids[4], 18000.00, "LOST", "2025-04-02 15:30:00"),
            (lead_ids[4], customer_ids[4], user_ids[3], stage_ids[1], 20000.00, "OPEN", None),
            (lead_ids[5], customer_ids[0], user_ids[1], stage_ids[2], 30000.00, "OPEN", None),
        ]
        opportunity_ids = []
        for row in opportunities_data:
            cursor.execute(
                "INSERT INTO opportunities (lead_id, customer_id, owner_id, stage_id, value, status, closed_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                row,
            )
            opportunity_ids.append(cursor.lastrowid)
        conn.commit()

        # ========== Opportunity Stage History ==========
        osh_rows = []
        osh_rows += [
            (opportunity_ids[0], stage_ids[0], "2025-01-01 09:00:00", "2025-01-05 10:00:00"),
            (opportunity_ids[0], stage_ids[1], "2025-01-05 10:00:00", "2025-01-10 11:00:00"),
            (opportunity_ids[0], stage_ids[2], "2025-01-10 11:00:00", None),
        ]
        osh_rows += [
            (opportunity_ids[1], stage_ids[0], "2025-02-01 09:00:00", "2025-02-03 10:00:00"),
            (opportunity_ids[1], stage_ids[1], "2025-02-03 10:00:00", "2025-02-05 12:00:00"),
            (opportunity_ids[1], stage_ids[3], "2025-02-05 12:00:00", None),
        ]
        osh_rows += [
            (opportunity_ids[2], stage_ids[0], "2025-01-10 11:00:00", "2025-01-12 13:00:00"),
            (opportunity_ids[2], stage_ids[1], "2025-01-12 13:00:00", "2025-01-14 14:00:00"),
            (opportunity_ids[2], stage_ids[2], "2025-01-14 14:00:00", "2025-01-20 10:00:00"),
            (opportunity_ids[2], stage_ids[3], "2025-01-20 10:00:00", "2025-03-15 10:00:00"),
            (opportunity_ids[2], stage_ids[4], "2025-03-15 10:00:00", "2025-03-15 10:00:00"),
        ]
        osh_rows += [
            (opportunity_ids[3], stage_ids[0], "2025-03-15 09:00:00", "2025-03-20 09:00:00"),
            (opportunity_ids[3], stage_ids[1], "2025-03-20 09:00:00", "2025-04-02 15:30:00"),
            (opportunity_ids[3], stage_ids[4], "2025-04-02 15:30:00", "2025-04-02 15:30:00"),
        ]
        osh_rows += [
            (opportunity_ids[4], stage_ids[0], "2025-04-01 08:00:00", "2025-04-03 09:00:00"),
            (opportunity_ids[4], stage_ids[1], "2025-04-03 09:00:00", None),
        ]
        for row in osh_rows:
            cursor.execute(
                "INSERT INTO opportunity_stage_history (opportunity_id, stage_id, entered_at, left_at) VALUES (%s, %s, %s, %s)",
                row,
            )
        conn.commit()

        # ========== Activities ==========
        activities_data = [
            (lead_ids[0], opportunity_ids[0], user_ids[0], "CALL", "Intro Call", "Discussed needs.", "2025-05-01 10:00:00"),
            (lead_ids[1], opportunity_ids[1], user_ids[1], "EMAIL", "Send Brochure", "Emailed product brochure.", "2025-05-02 11:00:00"),
            (lead_ids[2], opportunity_ids[2], user_ids[0], "MEETING", "Demo", "Scheduled solution demo.", "2025-05-03 15:00:00"),
            (lead_ids[3], opportunity_ids[3], user_ids[2], "NOTE", "Internal Note", "Lead seems budget constrained.", "2025-05-04 09:00:00"),
            (lead_ids[4], opportunity_ids[4], user_ids[3], "TASK", "Prepare Quote", "Prepare pricing options.", "2025-05-05 13:00:00"),
            (lead_ids[5], opportunity_ids[5], user_ids[1], "EMAIL", "Follow-up", "Followed up after demo.", "2025-05-06 10:30:00"),
            (None,          opportunity_ids[0], user_ids[0], "CALL", "Negotiation Call", "Discussed terms.", "2025-05-07 16:00:00"),
            (lead_ids[0],   None,               user_ids[0], "NOTE", "Scoring", "Increased lead score.", "2025-05-08 12:00:00"),
            (lead_ids[2],   opportunity_ids[2], user_ids[0], "MEETING", "Contract Review", "Reviewed contract clauses.", "2025-05-09 14:00:00"),
            (lead_ids[1],   None,               user_ids[1], "TASK", "Schedule Next Call", "Set up next touchpoint.", "2025-05-10 09:30:00"),
        ]
        for row in activities_data:
            cursor.execute(
                "INSERT INTO activities (lead_id, opportunity_id, user_id, activity_type, subject, notes, due_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                row,
            )
        conn.commit()

        print("✅ Seed data inserted successfully!")

    except Error as e:
        if conn:
            conn.rollback()
        print(f"❌ Error: {e}")

    finally:
        try:
            if conn and conn.is_connected():
                conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
