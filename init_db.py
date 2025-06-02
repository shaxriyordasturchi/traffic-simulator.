import sqlite3
from datetime import datetime
import random

def init_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS foydalanuvchilar (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ism TEXT NOT NULL,
        familiya TEXT,
        telefon TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voip_qongiroqlar (
        call_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        ip_manzil TEXT,
        boshlanish_vaqti TEXT,
        tugash_vaqti TEXT,
        ovoz_sifati INTEGER CHECK(ovoz_sifati >= 1 AND ovoz_sifati <= 10),
        FOREIGN KEY (user_id) REFERENCES foydalanuvchilar(user_id)
    )
    """)

    conn.commit()

    # Demo foydalanuvchilar
    ismlar = ['Ali', 'Laylo', 'Sardor', 'Gulnoza', 'Jamshid']
    familiyalar = ['Karimov', 'Xoliqova', 'Aliyev', 'Qodirova', 'Murodov']
    ip_lar = ['192.168.0.1', '10.0.0.5', '172.16.1.1', '192.168.1.2']

    for i in range(5):
        cursor.execute("INSERT OR IGNORE INTO foydalanuvchilar (ism, familiya, telefon) VALUES (?, ?, ?)",
                       (ismlar[i], familiyalar[i], f"+99890123456{i}"))

    for _ in range(50):
        user_id = random.randint(1, 5)
        ip = random.choice(ip_lar)
        bosh_vaqt = datetime(2024, 6, random.randint(1, 28), random.randint(0, 23), random.randint(0, 59))
        tug_vaqt = bosh_vaqt.replace(minute=(bosh_vaqt.minute + random.randint(1, 5)) % 60)
        ovoz = random.randint(3, 10)
        cursor.execute("""
        INSERT INTO voip_qongiroqlar (user_id, ip_manzil, boshlanish_vaqti, tugash_vaqti, ovoz_sifati)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, ip, bosh_vaqt.isoformat(), tug_vaqt.isoformat(), ovoz))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("✅ Bazaga test ma’lumotlari qo‘shildi.")
