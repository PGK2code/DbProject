# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- ลูกค้า (customer) ----------
def search_customers(filters):
    """ค้นหา ลูกค้า ตามเงื่อนไข (name, email, tier)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM customer WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    sql = "SELECT * FROM customer WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("email"):
        sql += " AND email = %s"
        params.append(filters["email"])
    if filters.get("tier"):
        sql += " AND tier = %s"
        params.append(filters["tier"])
    sql += " ORDER BY customer_id"
    return run_query(sql, params)


def get_customer(customer_id):
    """ดึง ลูกค้า 1 รายการตาม cust_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
    return rows[0] if rows else None


def create_customer(data):
    """เพิ่มลูกค้าใหม่ โดย referred_by ว่างได้และจะบันทึกเป็น SQL NULL"""

    sql = """INSERT INTO customer (name, email, Address, tier,  referred_by)
            VALUES (%s, %s, %s, %s, %s)"""
    return run_command(sql, (data["name"], data["email"], data["Address"], data["tier"],
                            blank_to_none(data.get("referred_by"))))


def update_customer(customer_id, data):
    sql = """UPDATE customer
            SET name = %s, email = %s, Address = %s, tier = %s, referred_by = %s
            WHERE customer_id = %s"""
    return run_command(sql, (data["name"], data["email"], data["Address"], data["tier"],
                            blank_to_none(data.get("referred_by")), customer_id))


def delete_customer(customer_id):
    return run_command("DELETE FROM customer WHERE customer_id = %s", (customer_id,))


# ---------- สินค้า (product) ----------
def search_products(filters):
    """ค้นหา สินค้า ตามเงื่อนไข (name, category)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM product WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    
    sql = "SELECT * FROM product WHERE 1=1"
    params = []
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append("%" + filters["name"] + "%")
    if filters.get("category"):
        sql += " AND category LIKE %s"
        params.append("%" + filters["category"] + "%")
    sql += " ORDER BY name"
    return run_query(sql, params)




def get_product(product_id):
    """ดึง สินค้า 1 รายการตาม product_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query("SELECT * FROM product WHERE product_id = %s", (product_id,))
    return rows[0] if rows else None
    


def create_product(data):
    """เพิ่ม สินค้า ใหม่ — data มีคีย์: name, category, price, stock"""
    sql = """INSERT INTO product (name, category, description, price, stock)
                VALUES (%s, %s, %s, %s, %s)"""
    return run_command(sql, (
        data["name"], data["category"], data.get("description"),
        data["price"], data["stock"],
    ))


def update_product(product_id, data):
    """แก้ไข สินค้า ตาม product_id"""
    sql = """UPDATE product
             SET name = %s, category = %s, price = %s, stock = %s
             WHERE product_id = %s"""
    return run_command(sql, (
        data["name"], data["category"], data["price"], data["stock"], product_id,
    ))


def delete_product(product_id):
    """ลบ สินค้า ตาม product_id"""
    return run_command("DELETE FROM product WHERE product_id = %s", (product_id,))

# ---------- ออเดอร์ (shop_order) ----------
def search_orders(filters):
    """ค้นหา ออเดอร์ ตามเงื่อนไข (cust_id, status)
    ต้องแสดงคอลัมน์: order_id, cust_id, ชื่อลูกค้า, order_date, status, total (ยอดรวม)
    คำใบ้:
      - JOIN customer เพื่อแสดงชื่อลูกค้า
      - total ไม่ได้เก็บเป็นคอลัมน์ → คำนวณ = SUM(qty × unit_price) จาก order_line
        LEFT JOIN กับ subquery ที่รวมยอดของแต่ละ order_id แล้วใช้ IFNULL(..., 0)
      - เงื่อนไขทุกตัวใช้ = %s"""
    
    sql = "SELECT * FROM shop_order WHERE 1=1"
    params = []
    if filters.get("customer_id"):
        sql += " AND customer_id = %s"
        params.append(filters["customer_id"])
    if filters.get("status"):
        sql += " AND status = %s"
        params.append(filters["status"])
    sql += " ORDER BY customer_id"
    return run_query(sql, params)


def get_order(order_id):
    """ดึง ออเดอร์ 1 รายการตาม order_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    rows = run_query("SELECT * FROM shop_order WHERE order_id = %s", (order_id,))
    return rows[0] if rows else None


def check_can_ship(order_id):
    """ตรวจก่อนเปลี่ยนสถานะเป็น 'shipped' — ถ้าไม่ผ่านให้ raise ValueError("ข้อความ")
    (หน้าเว็บจะแสดงข้อความนั้นเป็น alert ให้ผู้ใช้เห็น และไม่บันทึกข้อมูล)
    กฎ: จัดส่งได้เฉพาะออเดอร์ที่ชำระเงินแล้ว = มีแถวในตาราง payment ของออเดอร์นี้
       → SELECT EXISTS (SELECT 1 FROM payment WHERE order_id = %s) AS paid
         (หรือ SELECT COUNT(*) ... ก็ได้)
    ตัวอย่าง: raise ValueError("ออเดอร์นี้ยังไม่ได้ชำระเงิน จัดส่งไม่ได้")"""
    # TODO: เขียนการตรวจตามคำใบ้
    _todo("check_can_ship")


def create_order(data):
    """เพิ่ม ออเดอร์ ใหม่ — data มีคีย์: cust_id, order_date, status
    คำใบ้:
      1) ออเดอร์ใหม่ยังไม่มีการชำระเงิน → ถ้า status = 'shipped' ให้ raise ValueError ได้เลย
      2) INSERT INTO shop_order (...) VALUES (%s, ...)"""
    # TODO: เขียนตามคำใบ้
    
    status = data.get("status") or "pending"
    if status == "shipped":
        raise ValueError("ออเดอร์ใหม่ยังไม่มีการชำระเงิน จึงตั้งเป็น shipped ไม่ได้")

    sql = """INSERT INTO shop_order (customer_id, order_date, status)
             VALUES (%s, COALESCE(%s, CURRENT_TIMESTAMP), %s)"""
    return run_command(sql, (
        data["customer_id"],
        blank_to_none(data.get("order_date")),
        status,
    ))


def update_order(order_id, data):
    """แก้ไข ออเดอร์ ตาม order_id
    คำใบ้:
      1) ถ้า status ใหม่ = 'shipped' → เรียก check_can_ship(order_id) ก่อน
      2) UPDATE shop_order SET ... WHERE order_id=%s"""
    # TODO: เขียนตามคำใบ้
    sql = """UPDATE shop_order
                 SET customer_id = %s, order_date = %s, status = %s
                 WHERE order_id = %s"""
    return run_command(sql, (
            data["customer_id"], data["order_date"], data["status"], order_id,
        ))


def delete_order(order_id):
    """ลบ ออเดอร์ ตาม order_id
    คำใบ้:
      1) ห้ามลบออเดอร์ที่ชำระเงินแล้ว → ตรวจด้วย EXISTS (SELECT 1 FROM payment WHERE order_id = %s)
         ถ้ามี → raise ValueError("ออเดอร์นี้ชำระเงินแล้ว ลบไม่ได้")
      2) ลบแถวลูกใน order_line ก่อน (FK) แล้วจึง DELETE FROM shop_order WHERE order_id=%s"""
    # TODO: เขียนตามคำใบ้
    return run_command("DELETE FROM shop_order WHERE order_id = %s", (order_id,))


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — คืน dict {ชื่อการ์ด: ตัวเลข}  (1 คีย์ = 1 การ์ด)
    ตอนนี้ยังไม่ได้เขียน SQL → คืนค่า None ทุกการ์ด หน้าเว็บจึงแสดง "—" รอไว้
    ★ งานของนิสิต: เขียน SQL ตามตัวอย่างด้านล่าง (1 คอลัมน์ใน SELECT = 1 การ์ด
      ชื่อหลัง AS = ข้อความใต้ตัวเลข) แล้วลบ return {...} ชุดล่างสุดทิ้ง
    ★ การ์ด "คิดเพิ่มเอง" 2 ใบ: ตั้งชื่อการ์ดใหม่ แล้วเขียน SQL เอง
    ★ ผลรวมเงินใช้ IFNULL(SUM(...), 0) — ถ้ายังไม่มีข้อมูล SUM จะได้ NULL"""
    # ---- ตัวอย่างเมื่อเขียน SQL แล้ว (เอา # ข้างหน้าออก แล้วเติมให้ครบทุกการ์ด) ----
    # sql = """SELECT
    #            (SELECT COUNT(*) FROM ...) AS 'ลูกค้า',
    #            (SELECT ...)               AS 'สินค้า',
    #            ...
    #          """
    # return run_query(sql)[0]      ← [0] = เอาแถวแรก (ผลมีแถวเดียว) ได้เป็น dict

    # TODO: ระหว่างที่ยังไม่ได้เขียน SQL คืนค่า None ให้การ์ดแสดง "—" รอไว้
    return {
        "ลูกค้า":         None,   # (SELECT COUNT(*) FROM customer)
        "สินค้า":         None,   # นับสินค้าทั้งหมด
        "ออเดอร์":        None,   # นับออเดอร์ทั้งหมด
        "รีวิว":          None,   # นับรีวิวทั้งหมด
        "คิดเพิ่มเอง 1":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
        "คิดเพิ่มเอง 2":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
    }

def report_best_selling():
    """📈 สินค้าขายดี (Best Sellers)
    คำใบ้: JOIN order_line→product, GROUP BY product, SUM(qty), ORDER BY DESC, LIMIT 5"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_best_selling")

def report_customers_above_avg():
    """🏅 ลูกค้าที่ซื้อมากกว่าค่าเฉลี่ย (Above Average)
    คำใบ้: JOIN shop_order→order_line, GROUP BY customer, HAVING SUM(qty*unit_price) > (subquery AVG)"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_customers_above_avg")

def report_high_rated():
    """⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4 (HAVING)
    คำใบ้: JOIN review→product, GROUP BY product, HAVING AVG(rating) >= 4"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_high_rated")

# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("best-selling",  "📈 สินค้าขายดี (Best Sellers)",                    report_best_selling),
    ("top-customers", "🏅 ลูกค้าที่ซื้อมากกว่าค่าเฉลี่ย (Above Average)", report_customers_above_avg),
    ("high-rated",    "⭐ สินค้าคะแนนรีวิวเฉลี่ย ≥ 4 (HAVING)",           report_high_rated),
    # ("my-report", "📋 รายงานของฉัน", report_my_report),   ← ตัวอย่างการเพิ่มรายงานที่ 4
]
