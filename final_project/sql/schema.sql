-- Use existing database
USE kpablic1;

-- Drop table if it exists (for clean setup)
DROP TABLE IF EXISTS translations;

-- Create translations table
CREATE TABLE translations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    input_seq VARCHAR(300) NOT NULL,
    seq_type ENUM('DNA', 'RNA') NOT NULL,
    seq_length INT NOT NULL,
    output_protein TEXT NOT NULL
);