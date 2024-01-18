DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS business_hours;
DROP TABLE IF EXISTS attractions;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  preferences JSON
);

-- Business hours table
CREATE TABLE business_hours (
    id INTEGER PRIMARY KEY,
    business_id INTEGER,
    day_of_week VARCHAR(10),
    open_time TIME,
    close_time TIME,
    FOREIGN KEY (business_id) REFERENCES attractions(attractionID)
);

CREATE TABLE attractions (
    attractionID INTEGER PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(50),
    location VARCHAR(255),
    coordinates VARCHAR(30),
    popularity_rank INTEGER,
    price REAL,
    culture INTEGER,
    history INTEGER,
    food INTEGER,
    scenic INTEGER
);

-- Attractions table
INSERT INTO attractions (attractionID, name, type, location, popularity_rank, price, coordinates, culture, history, food, scenic)
VALUES
    (1, 'Grand Place', 'Landmark', 'Brussels, Belgium', 1, 0, '50.8466,4.3528', 1, 1, 1, 1),
    (2, 'The Canals of Bruges', 'Scenic', 'Bruges, Belgium', 2, 0, '51.2093,3.2247', 1, 1, 1, 1),
    (3, 'The Battlefields of Flanders', 'Historical', 'Flanders, Belgium', 3, 0, '50.8503,2.9146', 1, 1, 1, 1),
    (4, 'The Belfry of Bruges', 'Landmark', 'Bruges, Belgium', 4, 5.00, '51.2086,3.2247', 1, 1, 1, 1),
    (5, 'Ghents Gravensteen and Old Town', 'Historical', 'Ghent, Belgium', 5, 10.00, '51.0539,3.7250', 1, 1, 1, 1),
    (6, 'Basilica of the Holy Blood', 'Religious', 'Bruges, Belgium', 6, 0, '51.2095,3.2247', 1, 1, 1, 1),
    (7, 'Meuse Valley', 'Scenic', 'Meuse Valley, Belgium', 7, 0, '50.2766,5.6777', 1, 1, 1, 1),
    (8, 'Mechelen Old Town', 'Historical', 'Mechelen, Belgium', 8, 0, '51.0259,4.4773', 1, 1, 1, 1),
    (9, 'Ghents Canals', 'Scenic', 'Ghent, Belgium', 9, 0, '51.0543,3.7174', 1, 1, 1, 1),
    (10, 'Waterloo', 'Historical', 'Waterloo, Belgium', 10, 15.00, '50.7091,4.4044', 1, 1, 1, 1),
    (11, 'Grand Place (Grote Markt)', 'Landmark', 'Antwerp, Belgium', 11, 0, '51.2217,4.3997', 1, 1, 1, 1),
    (12, 'Semois Valley', 'Scenic', 'Semois Valley, Belgium', 12, 0, '49.8758,4.9304', 1, 1, 1, 100),
    (13, 'Mons Old Town', 'Historical', 'Mons, Belgium', 13, 0, '50.4547,3.9513', 1, 1, 100, 1),
    (14, 'St. Peters Church', 'Religious', 'Leuven, Belgium', 14, 0, '50.8774,4.7018', 1, 100, 1, 1),
    (15, 'Castle of Vêves', 'Historical', 'Castle of Vêves, Belgium', 15, 8.00, '50.2450,5.2006', 100, 1, 1, 1),
    (16, 'Raversyde Atlantikwall', 'Historical', 'Raversyde Atlantikwall, Belgium', 16, 7.50, '51.1734,2.7923', 1, 1, 1, 10),
    (17, 'Cathedral of Saint Bavo', 'Religious', 'Ghent, Belgium', 17, 0, '51.0543,3.7174', 1, 1, 10, 1),
    (18, 'Antwerps Art Museums', 'Museum', 'Antwerp, Belgium', 18, 12.00, '51.2194,4.4025', 1, 10, 1, 1),
    (19, 'Horta Museum and Town Houses', 'Museum', 'Brussels, Belgium', 19, 10.00, '50.8253,4.3632', 10, 1, 1, 1);



--Test data


-- Create a temporary table for days
CREATE TEMPORARY TABLE IF NOT EXISTS temp_days (day VARCHAR(9));

-- Insert days into the temporary table
INSERT INTO temp_days (day)
VALUES ('Monday'), ('Tuesday'), ('Wednesday'), ('Thursday'), ('Friday'), ('Saturday'), ('Sunday');

-- Inserting data into the business_hours table (Monday-Sunday, 9am-5pm) with unique id
INSERT INTO business_hours (id, business_id, day_of_week, open_time, close_time)
SELECT
    ROW_NUMBER() OVER () AS id,
    a.attractionID AS business_id,
    td.day,
    '09:00:00' AS open_time,
    '17:00:00' AS close_time
FROM
    attractions a
CROSS JOIN
    temp_days td;

-- Drop the temporary table
DROP TABLE IF EXISTS temp_days;

DELETE FROM business_hours
WHERE id > 133;
