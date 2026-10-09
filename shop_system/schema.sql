

    /*
    DROP TABLE IF EXISTS payment;
    DROP TABLE IF EXISTS review;
    DROP TABLE IF EXISTS order_line;
    DROP TABLE IF EXISTS shop_order;
    DROP TABLE IF EXISTS product;
    DROP TABLE IF EXISTS customer;
    */

    CREATE TABLE customer (
        customer_id  INT AUTO_INCREMENT PRIMARY KEY,
        name         VARCHAR(150) NOT NULL,
        email        VARCHAR(100) UNIQUE NOT NULL,
        phone        VARCHAR(20),
        tier         ENUM('normal', 'silver', 'gold', 'vip') DEFAULT 'normal',
        Address      VARCHAR(100) NOT NULL, 
        referred_by  INT, -- Self-reference: ลูกค้าที่แนะนำมา
        FOREIGN KEY (referred_by) REFERENCES customer(customer_id)
    );

    -- 2. PRODUCT (สินค้า)    
    CREATE TABLE product (
        product_id   INT AUTO_INCREMENT PRIMARY KEY,
        name         VARCHAR(255) NOT NULL,
        description  TEXT,
        category     VARCHAR(100) NOT NULL,
        price        DECIMAL(10,2) NOT NULL,
        stock        INT NOT NULL DEFAULT 0
    );

    -- 3. SHOP_ORDER (ออเดอร์)
    CREATE TABLE shop_order (
        order_id     INT AUTO_INCREMENT PRIMARY KEY,
        customer_id  INT NOT NULL,
        order_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
        status       ENUM('pending', 'processing', 'shipped', 'cancelled') DEFAULT 'pending',
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
    );

    -- 4. ORDER_LINE (รายการสินค้าในออเดอร์ - M:N #1)
    CREATE TABLE order_line (
        order_line_id INT AUTO_INCREMENT PRIMARY KEY,
        order_id      INT NOT NULL,
        product_id    INT NOT NULL,
        quantity      INT NOT NULL,
        unit_price    DECIMAL(10,2) NOT NULL, -- ล็อกราคาขณะสั่ง
        FOREIGN KEY (order_id) REFERENCES shop_order(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES product(product_id)
    );

    -- 5. REVIEW (รีวิวสินค้า - M:N #2)
    CREATE TABLE review (
        review_id    INT AUTO_INCREMENT PRIMARY KEY,
        customer_id  INT NOT NULL,
        product_id   INT NOT NULL,
        rating       INT NOT NULL CHECK(rating BETWEEN 1 AND 5),
        comment      TEXT,
        review_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
        FOREIGN KEY (product_id) REFERENCES product(product_id)
    );

    -- 6. PAYMENT (การชำระเงิน - Weak entity ของ shop_order)
    CREATE TABLE payment (
        payment_id   INT AUTO_INCREMENT PRIMARY KEY,
        order_id     INT NOT NULL UNIQUE, -- Weak Entity ผูกกับ order_id แบบ 1:1
        payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        amount       DECIMAL(10,2) NOT NULL,
        status       ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
        FOREIGN KEY (order_id) REFERENCES shop_order(order_id) ON DELETE CASCADE
    );


    -- =====================================================

-- ลูกค้า
INSERT INTO customer (name, email, phone, tier, Address, referred_by) VALUES

('Aiden Cross', 'aiden.cross@email.com', '+81-90-1234-0001', 'vip',
 '12 Sakura Street, Tokyo', NULL),

('Yuki Amamiya', 'yuki.amamiya@email.com', '+81-90-1234-0002', 'gold',
 '45 Moonlight Avenue, Kyoto', 1),

('Ren Takahashi', 'ren.takahashi@email.com', '+81-90-1234-0003', 'silver',
 '78 Star Road, Osaka', 1),

('Aria White', 'aria.white@email.com', '+81-90-1234-0004', 'normal',
 '21 Crystal Lane, Tokyo', NULL),

('Luna Hart', 'luna.hart@email.com', '+81-90-1234-0005', 'normal',
 '63 Rose Street, Kyoto', 3);


-- สินค้า
INSERT INTO product (name, description, category, price, stock) VALUES

('Aether Smartphone X',
 'A high-performance smartphone with advanced features',
 'Smartphones',
 25000.00, 10),

('Shadow Guard Case',
 'A durable protective case designed for smartphones',
 'Accessories',
 500.00, 50),

('Moonlight Wireless Headphones',
 'Wireless headphones with high-quality noise cancellation',
 'Audio',
 3500.00, 20),

('Arc Power Bank',
 '10000mAh portable power bank with fast charging',
 'Accessories',
 800.00, 30),

('Starlight Type-C Cable',
 'High-speed Type-C charging and data cable',
 'Accessories',
 300.00, 100);


-- ออเดอร์
INSERT INTO shop_order (customer_id, status) VALUES

(1, 'shipped'),
(2, 'shipped'),
(3, 'processing'),
(4, 'pending'),
(1, 'shipped');



-- รายการสินค้าในออเดอร์
INSERT INTO order_line (order_id, product_id, quantity, unit_price) VALUES

(1, 1, 1, 25000.00),
(1, 2, 2, 500.00),

(2, 3, 1, 3500.00),
(2, 5, 2, 300.00),

(3, 4, 1, 800.00),
(3, 5, 1, 300.00),

(4, 5, 2, 300.00),

(5, 3, 2, 3500.00);




-- รีวิวสินค้า
INSERT INTO review (customer_id, product_id, rating, comment) VALUES

(1, 1, 5, 'Excellent performance and beautiful design.'),

(1, 2, 4, 'The case fits perfectly and feels durable.'),

(2, 3, 5, 'The sound quality is amazing and the noise cancellation works very well.'),

(3, 4, 3, 'The capacity is slightly lower than I expected.'),

(4, 5, 4, 'Good quality cable and charges quickly.'),

(1, 3, 5, 'I really love these headphones. Highly recommended.');



-- การชำระเงิน
INSERT INTO payment (order_id, amount, status) VALUES

(1, 26000.00, 'completed'),

(2, 4100.00, 'completed'),

(3, 1100.00, 'completed'),

(4, 600.00, 'pending'),

(5, 7000.00, 'completed');

    
    
    
    
    
    
    
    
    
    
    
    