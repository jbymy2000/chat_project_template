--    CREATE DATABASE chat_history;
--    \c chat_history
--    CREATE TABLE messages (
--        id SERIAL PRIMARY KEY,
--        session_id VARCHAR(50),
--        sender VARCHAR(10),
--        message TEXT,
--        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--    );

CREATE TABLE auth_users (
    user_id SERIAL PRIMARY KEY,                -- 用户ID，自动增长
    username VARCHAR(255) UNIQUE NOT NULL,     -- 用户名，唯一
    email VARCHAR(255) UNIQUE,                 -- 用户邮箱，唯一
    phone_number VARCHAR(20),                  -- 用户手机号
    password_hash VARCHAR(255) NOT NULL,       -- 用户密码（经过哈希存储）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 用户创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 用户更新时间
    UNIQUE (phone_number)                      -- 确保手机号唯一
);


CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,                     -- 用户ID，外键关联到 auth_users 表
    gender VARCHAR(50) DEFAULT 'other',  -- 性别
    province VARCHAR(100),                       -- 所在省份
    exam_year INT,                               -- 考试年份（例如高考年份）
    subject_choice TEXT[],                       -- 选科，数组类型，存储多个科目
    score INT,                                   -- 分数
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 更新时间
    FOREIGN KEY (user_id) REFERENCES auth_users(user_id)  -- 外键关联到 auth_users 表
);



CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,             -- 消息ID，自动增长
    topic_id INT,                              -- 话题ID，外键关联到 topics 表
    user_id INT,                               -- 用户ID，外键关联到 auth_users 表
    message_type message_type_enum NOT NULL,    -- 使用 ENUM 类型存储消息类型
    content TEXT NOT NULL,                     -- 消息内容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 消息创建时间
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),  -- 外键关联到 topics 表
    FOREIGN KEY (user_id) REFERENCES auth_users(user_id)  -- 外键关联到 auth_users 表
);


CREATE TABLE topics (
    topic_id SERIAL PRIMARY KEY,         -- 话题ID，自动增长
    user_id INT NOT NULL,                -- 用户ID，外键关联到 auth_users 表
    topic VARCHAR(255) NOT NULL,         -- 话题名称或标题
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 对话开始时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 最后更新时间
    FOREIGN KEY (user_id) REFERENCES auth_users(user_id)  -- 外键关联到 auth_users 表
);



