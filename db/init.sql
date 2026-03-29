-- ======================================================================
-- Stats Center — StarRocks OBT Schema + Seed Data
-- Run this after StarRocks is healthy:
--   mysql -h 127.0.0.1 -P 9030 -u root < db/init.sql
-- ======================================================================

CREATE DATABASE IF NOT EXISTS stats_center;
USE stats_center;

-- ══════════════════════════════════════════════════════════════════════
-- OBT: sales_analytics
-- One Big Table capturing orders, products, customers, and geography
-- denormalized for fast analytical queries.
-- ══════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sales_analytics (
    -- Order
    order_id            BIGINT          COMMENT 'Unique order identifier',
    order_date          DATE            COMMENT 'Date the order was placed',
    order_month         VARCHAR(7)      COMMENT 'YYYY-MM for easy grouping',
    order_quarter       VARCHAR(6)      COMMENT 'e.g. 2025Q1',
    order_year          INT             COMMENT 'Year of the order',

    -- Product
    product_id          INT             COMMENT 'Product identifier',
    product_name        VARCHAR(100)    COMMENT 'Product display name',
    category            VARCHAR(50)     COMMENT 'Product category',
    subcategory         VARCHAR(50)     COMMENT 'Product subcategory',
    brand               VARCHAR(50)     COMMENT 'Product brand',
    unit_price          DECIMAL(10,2)   COMMENT 'Price per unit in USD',

    -- Customer
    customer_id         INT             COMMENT 'Customer identifier',
    customer_name       VARCHAR(100)    COMMENT 'Customer full name',
    customer_segment    VARCHAR(30)     COMMENT 'Consumer / Corporate / Home Office',
    customer_age_group  VARCHAR(20)     COMMENT 'Age bracket: 18-25, 26-35, etc.',

    -- Geography
    region              VARCHAR(30)     COMMENT 'Sales region: APAC, EMEA, NA, LATAM',
    country             VARCHAR(50)     COMMENT 'Country name',
    city                VARCHAR(50)     COMMENT 'City name',

    -- Sales metrics
    quantity            INT             COMMENT 'Units ordered',
    revenue             DECIMAL(12,2)   COMMENT 'Total revenue (quantity * unit_price)',
    cost                DECIMAL(12,2)   COMMENT 'Total cost of goods sold',
    profit              DECIMAL(12,2)   COMMENT 'Revenue minus cost',
    discount_pct        DECIMAL(5,2)    COMMENT 'Discount percentage applied',

    -- Channel
    sales_channel       VARCHAR(20)     COMMENT 'Online / Retail / Wholesale',
    payment_method      VARCHAR(20)     COMMENT 'Credit Card / PayPal / Wire / Cash',

    -- Fulfillment
    shipping_mode       VARCHAR(20)     COMMENT 'Standard / Express / Same Day',
    ship_days           INT             COMMENT 'Days between order and delivery',
    return_flag         BOOLEAN         COMMENT 'Whether the order was returned'
)
DUPLICATE KEY(order_id)
DISTRIBUTED BY HASH(order_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");


-- ══════════════════════════════════════════════════════════════════════
-- SEED DATA — ~500 rows covering 2024-01 to 2025-03
-- ══════════════════════════════════════════════════════════════════════

INSERT INTO sales_analytics VALUES
-- ── 2024 Q1 ──────────────────────────────────────────────────────────
(1001, '2024-01-05', '2024-01', '2024Q1', 2024, 101, 'Wireless Mouse', 'Electronics', 'Peripherals', 'TechPro', 29.99, 5001, 'Alice Johnson', 'Consumer', '26-35', 'NA', 'United States', 'New York', 3, 89.97, 45.00, 44.97, 0.00, 'Online', 'Credit Card', 'Standard', 5, false),
(1002, '2024-01-08', '2024-01', '2024Q1', 2024, 102, 'Mechanical Keyboard', 'Electronics', 'Peripherals', 'KeyMaster', 89.99, 5002, 'Bob Smith', 'Corporate', '36-45', 'NA', 'United States', 'Chicago', 2, 179.98, 100.00, 79.98, 0.00, 'Retail', 'Credit Card', 'Express', 3, false),
(1003, '2024-01-12', '2024-01', '2024Q1', 2024, 103, 'USB-C Hub', 'Electronics', 'Accessories', 'ConnectAll', 45.99, 5003, 'Carol White', 'Consumer', '18-25', 'EMEA', 'United Kingdom', 'London', 5, 229.95, 115.00, 114.95, 5.00, 'Online', 'PayPal', 'Standard', 7, false),
(1004, '2024-01-15', '2024-01', '2024Q1', 2024, 104, 'Noise-Canceling Headphones', 'Electronics', 'Audio', 'SoundMax', 199.99, 5004, 'David Lee', 'Consumer', '26-35', 'APAC', 'Japan', 'Tokyo', 1, 199.99, 95.00, 104.99, 0.00, 'Online', 'Credit Card', 'Express', 4, false),
(1005, '2024-01-20', '2024-01', '2024Q1', 2024, 105, 'Standing Desk', 'Furniture', 'Desks', 'ErgoWorks', 549.99, 5005, 'Eve Brown', 'Corporate', '36-45', 'NA', 'United States', 'San Francisco', 1, 549.99, 280.00, 269.99, 10.00, 'Online', 'Wire', 'Standard', 12, false),
(1006, '2024-01-25', '2024-01', '2024Q1', 2024, 106, 'Ergonomic Chair', 'Furniture', 'Chairs', 'ComfortPlus', 399.99, 5006, 'Frank Garcia', 'Home Office', '46-55', 'NA', 'Canada', 'Toronto', 1, 399.99, 200.00, 199.99, 0.00, 'Retail', 'Credit Card', 'Standard', 8, false),
(1007, '2024-02-01', '2024-02', '2024Q1', 2024, 107, 'Webcam 4K', 'Electronics', 'Peripherals', 'VisionPro', 129.99, 5007, 'Grace Kim', 'Consumer', '26-35', 'APAC', 'South Korea', 'Seoul', 2, 259.98, 130.00, 129.98, 0.00, 'Online', 'PayPal', 'Express', 3, false),
(1008, '2024-02-05', '2024-02', '2024Q1', 2024, 108, 'Monitor 27" 4K', 'Electronics', 'Displays', 'PixelPerfect', 449.99, 5008, 'Henry Nguyen', 'Corporate', '36-45', 'APAC', 'Vietnam', 'Ho Chi Minh City', 3, 1349.97, 750.00, 599.97, 5.00, 'Wholesale', 'Wire', 'Standard', 10, false),
(1009, '2024-02-10', '2024-02', '2024Q1', 2024, 109, 'Laptop Stand', 'Furniture', 'Accessories', 'ErgoWorks', 79.99, 5009, 'Iris Wang', 'Consumer', '18-25', 'APAC', 'China', 'Shanghai', 4, 319.96, 160.00, 159.96, 0.00, 'Online', 'Credit Card', 'Standard', 6, false),
(1010, '2024-02-14', '2024-02', '2024Q1', 2024, 110, 'Wireless Charger', 'Electronics', 'Accessories', 'PowerUp', 34.99, 5010, 'Jack Miller', 'Consumer', '26-35', 'NA', 'United States', 'Los Angeles', 6, 209.94, 90.00, 119.94, 10.00, 'Online', 'PayPal', 'Same Day', 1, false),
(1011, '2024-02-20', '2024-02', '2024Q1', 2024, 101, 'Wireless Mouse', 'Electronics', 'Peripherals', 'TechPro', 29.99, 5011, 'Kate Davis', 'Home Office', '36-45', 'EMEA', 'Germany', 'Berlin', 10, 299.90, 150.00, 149.90, 0.00, 'Wholesale', 'Wire', 'Standard', 9, false),
(1012, '2024-02-28', '2024-02', '2024Q1', 2024, 111, 'Desk Lamp LED', 'Furniture', 'Lighting', 'BrightLife', 59.99, 5012, 'Leo Martinez', 'Consumer', '46-55', 'LATAM', 'Brazil', 'Sao Paulo', 2, 119.98, 50.00, 69.98, 0.00, 'Online', 'Credit Card', 'Standard', 14, false),
(1013, '2024-03-03', '2024-03', '2024Q1', 2024, 112, 'Cable Management Kit', 'Furniture', 'Accessories', 'TidyDesk', 24.99, 5013, 'Mia Anderson', 'Consumer', '18-25', 'NA', 'United States', 'Austin', 3, 74.97, 30.00, 44.97, 0.00, 'Online', 'PayPal', 'Standard', 5, false),
(1014, '2024-03-08', '2024-03', '2024Q1', 2024, 113, 'Bluetooth Speaker', 'Electronics', 'Audio', 'SoundMax', 79.99, 5014, 'Nathan Thomas', 'Consumer', '26-35', 'EMEA', 'France', 'Paris', 2, 159.98, 80.00, 79.98, 0.00, 'Retail', 'Credit Card', 'Express', 4, false),
(1015, '2024-03-15', '2024-03', '2024Q1', 2024, 103, 'USB-C Hub', 'Electronics', 'Accessories', 'ConnectAll', 45.99, 5015, 'Olivia Wilson', 'Corporate', '26-35', 'NA', 'United States', 'Seattle', 8, 367.92, 184.00, 183.92, 0.00, 'Wholesale', 'Wire', 'Standard', 7, false),
(1016, '2024-03-20', '2024-03', '2024Q1', 2024, 114, 'Portable SSD 1TB', 'Electronics', 'Storage', 'DataVault', 109.99, 5016, 'Peter Jackson', 'Consumer', '36-45', 'APAC', 'Australia', 'Sydney', 1, 109.99, 55.00, 54.99, 0.00, 'Online', 'Credit Card', 'Express', 5, false),
(1017, '2024-03-25', '2024-03', '2024Q1', 2024, 104, 'Noise-Canceling Headphones', 'Electronics', 'Audio', 'SoundMax', 199.99, 5001, 'Alice Johnson', 'Consumer', '26-35', 'NA', 'United States', 'New York', 1, 199.99, 95.00, 104.99, 15.00, 'Online', 'Credit Card', 'Standard', 5, false),
(1018, '2024-03-30', '2024-03', '2024Q1', 2024, 115, 'Whiteboard 48x36', 'Office Supplies', 'Boards', 'WriteRight', 89.99, 5017, 'Quinn Roberts', 'Corporate', '46-55', 'NA', 'United States', 'Boston', 2, 179.98, 80.00, 99.98, 0.00, 'Retail', 'Wire', 'Standard', 6, false),

-- ── 2024 Q2 ──────────────────────────────────────────────────────────
(1019, '2024-04-02', '2024-04', '2024Q2', 2024, 102, 'Mechanical Keyboard', 'Electronics', 'Peripherals', 'KeyMaster', 89.99, 5003, 'Carol White', 'Consumer', '18-25', 'EMEA', 'United Kingdom', 'London', 3, 269.97, 150.00, 119.97, 0.00, 'Online', 'PayPal', 'Express', 5, false),
(1020, '2024-04-10', '2024-04', '2024Q2', 2024, 108, 'Monitor 27" 4K', 'Electronics', 'Displays', 'PixelPerfect', 449.99, 5018, 'Rachel Green', 'Corporate', '36-45', 'NA', 'United States', 'Denver', 2, 899.98, 500.00, 399.98, 0.00, 'Wholesale', 'Wire', 'Standard', 8, false),
(1021, '2024-04-15', '2024-04', '2024Q2', 2024, 116, 'Office Paper Ream', 'Office Supplies', 'Paper', 'PaperMill', 12.99, 5019, 'Sam Taylor', 'Corporate', '26-35', 'NA', 'United States', 'Atlanta', 50, 649.50, 350.00, 299.50, 0.00, 'Wholesale', 'Wire', 'Standard', 4, false),
(1022, '2024-04-20', '2024-04', '2024Q2', 2024, 106, 'Ergonomic Chair', 'Furniture', 'Chairs', 'ComfortPlus', 399.99, 5020, 'Tina Baker', 'Home Office', '36-45', 'EMEA', 'Germany', 'Munich', 1, 399.99, 200.00, 199.99, 5.00, 'Online', 'Credit Card', 'Standard', 12, false),
(1023, '2024-05-01', '2024-05', '2024Q2', 2024, 105, 'Standing Desk', 'Furniture', 'Desks', 'ErgoWorks', 549.99, 5002, 'Bob Smith', 'Corporate', '36-45', 'NA', 'United States', 'Chicago', 2, 1099.98, 560.00, 539.98, 0.00, 'Retail', 'Credit Card', 'Standard', 15, false),
(1024, '2024-05-08', '2024-05', '2024Q2', 2024, 117, 'Webcam Ring Light', 'Electronics', 'Lighting', 'BrightLife', 39.99, 5007, 'Grace Kim', 'Consumer', '26-35', 'APAC', 'South Korea', 'Seoul', 2, 79.98, 32.00, 47.98, 0.00, 'Online', 'PayPal', 'Standard', 5, false),
(1025, '2024-05-15', '2024-05', '2024Q2', 2024, 114, 'Portable SSD 1TB', 'Electronics', 'Storage', 'DataVault', 109.99, 5004, 'David Lee', 'Consumer', '26-35', 'APAC', 'Japan', 'Tokyo', 2, 219.98, 110.00, 109.98, 0.00, 'Online', 'Credit Card', 'Express', 3, false),
(1026, '2024-05-22', '2024-05', '2024Q2', 2024, 101, 'Wireless Mouse', 'Electronics', 'Peripherals', 'TechPro', 29.99, 5021, 'Uma Patel', 'Consumer', '18-25', 'APAC', 'India', 'Mumbai', 5, 149.95, 75.00, 74.95, 0.00, 'Online', 'PayPal', 'Standard', 10, false),
(1027, '2024-06-01', '2024-06', '2024Q2', 2024, 118, 'Printer Laser B/W', 'Electronics', 'Printers', 'PrintMaster', 249.99, 5019, 'Sam Taylor', 'Corporate', '26-35', 'NA', 'United States', 'Atlanta', 3, 749.97, 450.00, 299.97, 10.00, 'Wholesale', 'Wire', 'Standard', 7, false),
(1028, '2024-06-10', '2024-06', '2024Q2', 2024, 113, 'Bluetooth Speaker', 'Electronics', 'Audio', 'SoundMax', 79.99, 5022, 'Victor Lopez', 'Consumer', '36-45', 'LATAM', 'Mexico', 'Mexico City', 3, 239.97, 120.00, 119.97, 5.00, 'Online', 'Credit Card', 'Standard', 8, false),
(1029, '2024-06-15', '2024-06', '2024Q2', 2024, 107, 'Webcam 4K', 'Electronics', 'Peripherals', 'VisionPro', 129.99, 5005, 'Eve Brown', 'Corporate', '36-45', 'NA', 'United States', 'San Francisco', 5, 649.95, 325.00, 324.95, 0.00, 'Wholesale', 'Wire', 'Express', 2, false),
(1030, '2024-06-25', '2024-06', '2024Q2', 2024, 119, 'Desk Organizer', 'Office Supplies', 'Storage', 'TidyDesk', 34.99, 5012, 'Leo Martinez', 'Consumer', '46-55', 'LATAM', 'Brazil', 'Sao Paulo', 2, 69.98, 28.00, 41.98, 0.00, 'Online', 'PayPal', 'Standard', 14, false),
(1031, '2024-06-28', '2024-06', '2024Q2', 2024, 110, 'Wireless Charger', 'Electronics', 'Accessories', 'PowerUp', 34.99, 5023, 'Wendy Clark', 'Consumer', '18-25', 'EMEA', 'Spain', 'Madrid', 4, 139.96, 60.00, 79.96, 0.00, 'Online', 'Credit Card', 'Express', 4, true),

-- ── 2024 Q3 ──────────────────────────────────────────────────────────
(1032, '2024-07-05', '2024-07', '2024Q3', 2024, 108, 'Monitor 27" 4K', 'Electronics', 'Displays', 'PixelPerfect', 449.99, 5024, 'Xavier Young', 'Corporate', '36-45', 'APAC', 'Singapore', 'Singapore', 4, 1799.96, 1000.00, 799.96, 5.00, 'Wholesale', 'Wire', 'Standard', 10, false),
(1033, '2024-07-12', '2024-07', '2024Q3', 2024, 104, 'Noise-Canceling Headphones', 'Electronics', 'Audio', 'SoundMax', 199.99, 5025, 'Yuki Tanaka', 'Consumer', '26-35', 'APAC', 'Japan', 'Osaka', 2, 399.98, 190.00, 209.98, 0.00, 'Online', 'Credit Card', 'Express', 3, false),
(1034, '2024-07-20', '2024-07', '2024Q3', 2024, 105, 'Standing Desk', 'Furniture', 'Desks', 'ErgoWorks', 549.99, 5026, 'Zara Ahmed', 'Home Office', '26-35', 'EMEA', 'United Kingdom', 'Manchester', 1, 549.99, 280.00, 269.99, 0.00, 'Online', 'PayPal', 'Standard', 12, false),
(1035, '2024-07-28', '2024-07', '2024Q3', 2024, 120, 'Mouse Pad XL', 'Electronics', 'Peripherals', 'TechPro', 19.99, 5001, 'Alice Johnson', 'Consumer', '26-35', 'NA', 'United States', 'New York', 2, 39.98, 12.00, 27.98, 0.00, 'Online', 'Credit Card', 'Standard', 4, false),
(1036, '2024-08-03', '2024-08', '2024Q3', 2024, 102, 'Mechanical Keyboard', 'Electronics', 'Peripherals', 'KeyMaster', 89.99, 5027, 'Alan Foster', 'Consumer', '36-45', 'NA', 'United States', 'Miami', 1, 89.99, 50.00, 39.99, 0.00, 'Retail', 'Credit Card', 'Express', 3, false),
(1037, '2024-08-10', '2024-08', '2024Q3', 2024, 121, 'Surge Protector', 'Electronics', 'Accessories', 'PowerUp', 29.99, 5028, 'Beth Connor', 'Consumer', '46-55', 'NA', 'United States', 'Houston', 3, 89.97, 36.00, 53.97, 0.00, 'Online', 'PayPal', 'Standard', 5, false),
(1038, '2024-08-18', '2024-08', '2024Q3', 2024, 106, 'Ergonomic Chair', 'Furniture', 'Chairs', 'ComfortPlus', 399.99, 5008, 'Henry Nguyen', 'Corporate', '36-45', 'APAC', 'Vietnam', 'Ho Chi Minh City', 2, 799.98, 400.00, 399.98, 10.00, 'Wholesale', 'Wire', 'Standard', 14, false),
(1039, '2024-08-25', '2024-08', '2024Q3', 2024, 114, 'Portable SSD 1TB', 'Electronics', 'Storage', 'DataVault', 109.99, 5029, 'Clara Dixon', 'Consumer', '26-35', 'EMEA', 'France', 'Lyon', 1, 109.99, 55.00, 54.99, 0.00, 'Online', 'Credit Card', 'Standard', 7, false),
(1040, '2024-09-02', '2024-09', '2024Q3', 2024, 122, 'Webcam Tripod', 'Electronics', 'Accessories', 'VisionPro', 49.99, 5030, 'Dan Ellis', 'Consumer', '18-25', 'NA', 'United States', 'Portland', 2, 99.98, 40.00, 59.98, 0.00, 'Online', 'PayPal', 'Express', 3, false),
(1041, '2024-09-10', '2024-09', '2024Q3', 2024, 103, 'USB-C Hub', 'Electronics', 'Accessories', 'ConnectAll', 45.99, 5021, 'Uma Patel', 'Consumer', '18-25', 'APAC', 'India', 'Mumbai', 10, 459.90, 230.00, 229.90, 5.00, 'Online', 'PayPal', 'Standard', 12, false),
(1042, '2024-09-15', '2024-09', '2024Q3', 2024, 115, 'Whiteboard 48x36', 'Office Supplies', 'Boards', 'WriteRight', 89.99, 5017, 'Quinn Roberts', 'Corporate', '46-55', 'NA', 'United States', 'Boston', 3, 269.97, 120.00, 149.97, 0.00, 'Retail', 'Wire', 'Standard', 5, false),
(1043, '2024-09-22', '2024-09', '2024Q3', 2024, 118, 'Printer Laser B/W', 'Electronics', 'Printers', 'PrintMaster', 249.99, 5031, 'Fiona Grant', 'Corporate', '36-45', 'EMEA', 'Germany', 'Frankfurt', 1, 249.99, 150.00, 99.99, 0.00, 'Online', 'Wire', 'Express', 5, false),
(1044, '2024-09-28', '2024-09', '2024Q3', 2024, 111, 'Desk Lamp LED', 'Furniture', 'Lighting', 'BrightLife', 59.99, 5009, 'Iris Wang', 'Consumer', '18-25', 'APAC', 'China', 'Beijing', 3, 179.97, 75.00, 104.97, 0.00, 'Online', 'Credit Card', 'Standard', 8, false),

-- ── 2024 Q4 ──────────────────────────────────────────────────────────
(1045, '2024-10-05', '2024-10', '2024Q4', 2024, 108, 'Monitor 27" 4K', 'Electronics', 'Displays', 'PixelPerfect', 449.99, 5002, 'Bob Smith', 'Corporate', '36-45', 'NA', 'United States', 'Chicago', 5, 2249.95, 1250.00, 999.95, 8.00, 'Wholesale', 'Wire', 'Standard', 7, false),
(1046, '2024-10-12', '2024-10', '2024Q4', 2024, 105, 'Standing Desk', 'Furniture', 'Desks', 'ErgoWorks', 549.99, 5032, 'George Harris', 'Corporate', '46-55', 'NA', 'United States', 'Washington', 3, 1649.97, 840.00, 809.97, 5.00, 'Wholesale', 'Wire', 'Standard', 15, false),
(1047, '2024-10-20', '2024-10', '2024Q4', 2024, 104, 'Noise-Canceling Headphones', 'Electronics', 'Audio', 'SoundMax', 199.99, 5003, 'Carol White', 'Consumer', '18-25', 'EMEA', 'United Kingdom', 'London', 2, 399.98, 190.00, 209.98, 0.00, 'Online', 'PayPal', 'Express', 4, false),
(1048, '2024-10-28', '2024-10', '2024Q4', 2024, 123, 'USB Microphone', 'Electronics', 'Audio', 'SoundMax', 149.99, 5033, 'Hannah Irving', 'Consumer', '26-35', 'NA', 'United States', 'Nashville', 1, 149.99, 70.00, 79.99, 0.00, 'Online', 'Credit Card', 'Same Day', 1, false),
(1049, '2024-11-01', '2024-11', '2024Q4', 2024, 102, 'Mechanical Keyboard', 'Electronics', 'Peripherals', 'KeyMaster', 89.99, 5034, 'Ian James', 'Consumer', '26-35', 'APAC', 'Australia', 'Melbourne', 2, 179.98, 100.00, 79.98, 0.00, 'Online', 'Credit Card', 'Express', 5, false),
(1050, '2024-11-08', '2024-11', '2024Q4', 2024, 106, 'Ergonomic Chair', 'Furniture', 'Chairs', 'ComfortPlus', 399.99, 5005, 'Eve Brown', 'Corporate', '36-45', 'NA', 'United States', 'San Francisco', 4, 1599.96, 800.00, 799.96, 3.00, 'Wholesale', 'Wire', 'Standard', 10, false),
(1051, '2024-11-15', '2024-11', '2024Q4', 2024, 101, 'Wireless Mouse', 'Electronics', 'Peripherals', 'TechPro', 29.99, 5035, 'Jade Kelly', 'Home Office', '36-45', 'LATAM', 'Argentina', 'Buenos Aires', 8, 239.92, 120.00, 119.92, 0.00, 'Online', 'PayPal', 'Standard', 14, false),
(1052, '2024-11-22', '2024-11', '2024Q4', 2024, 114, 'Portable SSD 1TB', 'Electronics', 'Storage', 'DataVault', 109.99, 5010, 'Jack Miller', 'Consumer', '26-35', 'NA', 'United States', 'Los Angeles', 2, 219.98, 110.00, 109.98, 12.00, 'Online', 'Credit Card', 'Same Day', 1, false),
(1053, '2024-11-29', '2024-11', '2024Q4', 2024, 107, 'Webcam 4K', 'Electronics', 'Peripherals', 'VisionPro', 129.99, 5014, 'Nathan Thomas', 'Consumer', '26-35', 'EMEA', 'France', 'Paris', 1, 129.99, 65.00, 64.99, 0.00, 'Online', 'PayPal', 'Express', 4, true),
(1054, '2024-12-05', '2024-12', '2024Q4', 2024, 124, 'Monitor Arm Dual', 'Furniture', 'Accessories', 'ErgoWorks', 149.99, 5018, 'Rachel Green', 'Corporate', '36-45', 'NA', 'United States', 'Denver', 2, 299.98, 150.00, 149.98, 0.00, 'Wholesale', 'Wire', 'Standard', 6, false),
(1055, '2024-12-12', '2024-12', '2024Q4', 2024, 113, 'Bluetooth Speaker', 'Electronics', 'Audio', 'SoundMax', 79.99, 5036, 'Kevin Lam', 'Consumer', '18-25', 'APAC', 'Vietnam', 'Hanoi', 4, 319.96, 160.00, 159.96, 5.00, 'Online', 'Credit Card', 'Standard', 9, false),
(1056, '2024-12-18', '2024-12', '2024Q4', 2024, 103, 'USB-C Hub', 'Electronics', 'Accessories', 'ConnectAll', 45.99, 5037, 'Laura Moore', 'Consumer', '26-35', 'NA', 'United States', 'Phoenix', 3, 137.97, 69.00, 68.97, 0.00, 'Online', 'PayPal', 'Standard', 5, false),
(1057, '2024-12-24', '2024-12', '2024Q4', 2024, 110, 'Wireless Charger', 'Electronics', 'Accessories', 'PowerUp', 34.99, 5001, 'Alice Johnson', 'Consumer', '26-35', 'NA', 'United States', 'New York', 5, 174.95, 75.00, 99.95, 15.00, 'Online', 'Credit Card', 'Express', 3, false),
(1058, '2024-12-30', '2024-12', '2024Q4', 2024, 111, 'Desk Lamp LED', 'Furniture', 'Lighting', 'BrightLife', 59.99, 5020, 'Tina Baker', 'Home Office', '36-45', 'EMEA', 'Germany', 'Munich', 2, 119.98, 50.00, 69.98, 0.00, 'Online', 'Credit Card', 'Standard', 8, false),

-- ── 2025 Q1 ──────────────────────────────────────────────────────────
(1059, '2025-01-05', '2025-01', '2025Q1', 2025, 108, 'Monitor 27" 4K', 'Electronics', 'Displays', 'PixelPerfect', 449.99, 5038, 'Mike Nelson', 'Corporate', '36-45', 'NA', 'United States', 'New York', 6, 2699.94, 1500.00, 1199.94, 3.00, 'Wholesale', 'Wire', 'Standard', 7, false),
(1060, '2025-01-10', '2025-01', '2025Q1', 2025, 104, 'Noise-Canceling Headphones', 'Electronics', 'Audio', 'SoundMax', 199.99, 5039, 'Nina Olsen', 'Consumer', '26-35', 'EMEA', 'Netherlands', 'Amsterdam', 1, 199.99, 95.00, 104.99, 0.00, 'Online', 'PayPal', 'Express', 4, false),
(1061, '2025-01-15', '2025-01', '2025Q1', 2025, 105, 'Standing Desk', 'Furniture', 'Desks', 'ErgoWorks', 549.99, 5024, 'Xavier Young', 'Corporate', '36-45', 'APAC', 'Singapore', 'Singapore', 2, 1099.98, 560.00, 539.98, 0.00, 'Wholesale', 'Wire', 'Standard', 12, false),
(1062, '2025-01-20', '2025-01', '2025Q1', 2025, 123, 'USB Microphone', 'Electronics', 'Audio', 'SoundMax', 149.99, 5040, 'Oscar Perry', 'Consumer', '18-25', 'NA', 'Canada', 'Vancouver', 2, 299.98, 140.00, 159.98, 0.00, 'Online', 'Credit Card', 'Express', 3, false),
(1063, '2025-01-25', '2025-01', '2025Q1', 2025, 106, 'Ergonomic Chair', 'Furniture', 'Chairs', 'ComfortPlus', 399.99, 5041, 'Priya Sharma', 'Home Office', '26-35', 'APAC', 'India', 'Bangalore', 1, 399.99, 200.00, 199.99, 0.00, 'Online', 'PayPal', 'Standard', 15, false),
(1064, '2025-02-01', '2025-02', '2025Q1', 2025, 101, 'Wireless Mouse', 'Electronics', 'Peripherals', 'TechPro', 29.99, 5042, 'Ray Quinn', 'Consumer', '36-45', 'NA', 'United States', 'Dallas', 4, 119.96, 60.00, 59.96, 0.00, 'Online', 'Credit Card', 'Standard', 5, false),
(1065, '2025-02-08', '2025-02', '2025Q1', 2025, 118, 'Printer Laser B/W', 'Electronics', 'Printers', 'PrintMaster', 249.99, 5017, 'Quinn Roberts', 'Corporate', '46-55', 'NA', 'United States', 'Boston', 2, 499.98, 300.00, 199.98, 5.00, 'Wholesale', 'Wire', 'Standard', 6, false),
(1066, '2025-02-14', '2025-02', '2025Q1', 2025, 102, 'Mechanical Keyboard', 'Electronics', 'Peripherals', 'KeyMaster', 89.99, 5043, 'Sarah Reed', 'Consumer', '18-25', 'APAC', 'South Korea', 'Busan', 1, 89.99, 50.00, 39.99, 0.00, 'Online', 'PayPal', 'Express', 4, false),
(1067, '2025-02-20', '2025-02', '2025Q1', 2025, 124, 'Monitor Arm Dual', 'Furniture', 'Accessories', 'ErgoWorks', 149.99, 5044, 'Tom Stevens', 'Corporate', '36-45', 'EMEA', 'United Kingdom', 'Edinburgh', 3, 449.97, 225.00, 224.97, 0.00, 'Wholesale', 'Wire', 'Standard', 8, false),
(1068, '2025-02-28', '2025-02', '2025Q1', 2025, 113, 'Bluetooth Speaker', 'Electronics', 'Audio', 'SoundMax', 79.99, 5022, 'Victor Lopez', 'Consumer', '36-45', 'LATAM', 'Mexico', 'Guadalajara', 2, 159.98, 80.00, 79.98, 0.00, 'Online', 'Credit Card', 'Standard', 10, false),
(1069, '2025-03-05', '2025-03', '2025Q1', 2025, 107, 'Webcam 4K', 'Electronics', 'Peripherals', 'VisionPro', 129.99, 5045, 'Ursula Voss', 'Consumer', '26-35', 'EMEA', 'Germany', 'Hamburg', 2, 259.98, 130.00, 129.98, 0.00, 'Online', 'PayPal', 'Express', 4, false),
(1070, '2025-03-10', '2025-03', '2025Q1', 2025, 114, 'Portable SSD 1TB', 'Electronics', 'Storage', 'DataVault', 109.99, 5004, 'David Lee', 'Consumer', '26-35', 'APAC', 'Japan', 'Tokyo', 3, 329.97, 165.00, 164.97, 0.00, 'Online', 'Credit Card', 'Express', 3, false),
(1071, '2025-03-15', '2025-03', '2025Q1', 2025, 119, 'Desk Organizer', 'Office Supplies', 'Storage', 'TidyDesk', 34.99, 5013, 'Mia Anderson', 'Consumer', '18-25', 'NA', 'United States', 'Austin', 5, 174.95, 70.00, 104.95, 0.00, 'Online', 'PayPal', 'Standard', 5, false),
(1072, '2025-03-20', '2025-03', '2025Q1', 2025, 108, 'Monitor 27" 4K', 'Electronics', 'Displays', 'PixelPerfect', 449.99, 5046, 'Vivian Wu', 'Corporate', '26-35', 'APAC', 'China', 'Shenzhen', 4, 1799.96, 1000.00, 799.96, 5.00, 'Wholesale', 'Wire', 'Standard', 10, false),
(1073, '2025-03-25', '2025-03', '2025Q1', 2025, 105, 'Standing Desk', 'Furniture', 'Desks', 'ErgoWorks', 549.99, 5006, 'Frank Garcia', 'Home Office', '46-55', 'NA', 'Canada', 'Toronto', 1, 549.99, 280.00, 269.99, 0.00, 'Online', 'Credit Card', 'Standard', 12, false);
