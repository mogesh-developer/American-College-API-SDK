-- Supabase PostgreSQL Database Schema for AMC Telegram Bot

-- 1. Create users table
CREATE TABLE IF NOT EXISTS users (
    telegram_id BIGINT PRIMARY KEY,
    encrypted_reg_no TEXT NOT NULL,
    encrypted_dob TEXT NOT NULL,
    api_token TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create subjects table
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT PRIMARY KEY,
    subject_name TEXT NOT NULL
);

-- 3. Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
    telegram_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    attendance_date TEXT NOT NULL,
    hour_value INT NOT NULL,
    subject_id INT REFERENCES subjects(subject_id) ON DELETE SET NULL,
    PRIMARY KEY (telegram_id, attendance_date, hour_value)
);

-- 4. Create day_orders table
CREATE TABLE IF NOT EXISTS day_orders (
    date TEXT PRIMARY KEY,
    day_value TEXT NOT NULL
);

-- 5. Create student_profiles table
CREATE TABLE IF NOT EXISTS student_profiles (
    telegram_id BIGINT PRIMARY KEY REFERENCES users(telegram_id) ON DELETE CASCADE,
    student_name TEXT,
    register_no TEXT,
    email TEXT,
    mobile TEXT,
    semester INT,
    course_name TEXT,
    department_name TEXT,
    batch TEXT,
    college_year TEXT
);


-- 6. Create weekly_timetable table
CREATE TABLE IF NOT EXISTS weekly_timetable (
    day_order TEXT,
    hour INT,
    code TEXT,
    subject_name TEXT,
    staff TEXT,
    PRIMARY KEY (day_order, hour)
);

-- 7. Seed initial weekly timetable data
INSERT INTO weekly_timetable (day_order, hour, code, subject_name, staff) VALUES
('D1', 1, '24PCS5409', 'Natural Language Processing (NLP)', 'VB'),
('D1', 2, '24PCS5407', 'Advanced Software Engineering (ASE)', 'CM'),
('D1', 3, '24PCS5403', 'Advanced DBMS (ADBMS)', 'KBA'),
('D1', 4, '24PCS5401', 'Data Mining & Warehousing (DMW)', 'KS'),
('D1', 5, '24PCS5405', 'Digital Image Processing (DIP)', 'KB'),

('D2', 1, '24PCS5409', 'Natural Language Processing (NLP)', 'VB'),
('D2', 2, '24PCS5407', 'Advanced Software Engineering (ASE)', 'CM'),
('D2', 3, '24PCS5401', 'Data Mining & Warehousing (DMW)', 'KS'),
('D2', 4, '24PCS5403', 'Advanced DBMS (ADBMS)', 'KBA'),
('D2', 5, '24PCS5405', 'Digital Image Processing (DIP)', 'KB'),

('D3', 1, '24PCS5407', 'Advanced Software Engineering (ASE)', 'CM'),
('D3', 2, '24PCS5403', 'Advanced DBMS (ADBMS)', 'KBA'),
('D3', 3, '24PCS5401', 'Data Mining & Warehousing (DMW)', 'KS'),
('D3', 4, '24PCS5405', 'Digital Image Processing (DIP)', 'KB'),
('D3', 5, '24PCS5409', 'Natural Language Processing (NLP)', 'VB'),

('D4', 1, '24PCS5409', 'Natural Language Processing (NLP)', 'VB'),
('D4', 2, '24PCS5407', 'Advanced Software Engineering (ASE)', 'CM'),
('D4', 3, '24PCS5401', 'Data Mining & Warehousing (DMW)', 'KS'),
('D4', 4, '24PCS5301', 'Advanced DBMS Lab (ADBMS LAB)', 'KBA'),
('D4', 5, '24PCS5301', 'Advanced DBMS Lab (ADBMS LAB)', 'KBA'),

('D5', 1, '24PCS5405', 'Digital Image Processing Lab (DIP LAB)', 'KB'),
('D5', 2, '24PCS5407', 'Advanced Software Engineering (ASE)', 'CM'),
('D5', 3, '24PCS5409', 'Natural Language Processing (NLP)', 'VB'),
('D5', 4, '24PCS5301', 'Advanced DBMS Lab (ADBMS LAB)', 'KBA'),
('D5', 5, '24PCS5301', 'Advanced DBMS Lab (ADBMS LAB)', 'KBA'),

('D6', 1, '24PCS5405', 'Digital Image Processing Lab (DIP LAB)', 'KB'),
('D6', 2, '24PCS5401', 'Data Mining & Warehousing (DMW)', 'KS'),
('D6', 3, '24PCS5409', 'Natural Language Processing (NLP)', 'VB'),
('D6', 4, '24PCS5403', 'Advanced DBMS (ADBMS)', 'KBA'),
('D6', 5, '24PCS5403', 'Advanced DBMS (ADBMS)', 'KBA')
ON CONFLICT (day_order, hour) DO NOTHING;
