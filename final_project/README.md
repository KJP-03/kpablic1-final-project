# DNA/RNA Sequence Translator

A web-based tool for translating DNA and RNA nucleotide sequences into amino acid (protein) sequences using the standard codon table.


## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [File Structure](#file-structure)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Author](#author)


## Overview

This tool provides a simple, efficient way to translate DNA or RNA sequences to amino acid sequences, with inputs up to 300 characters in length. The program is based on the standard codon table, which it uses to convert three-nucleotide codons into single-letter amino acid codes. The program also stores up to 5 of the most recent translations in a MySQL database for easy reference.


## Features

- DNA/RNA Sequence Detection: Automatically detects if the input is DNA (ATCG) or RNA (AUCG).
- Real-time Input Validation: Client-side validation for immediate feedback on sequence errors, such as invalid characters.
- Codon/Character Count: Real-time display of character and codon count for input.
- Incomplete Codon Handling: Sequences of any length up to 300 are accepted, with translation up to the maximum complete codon count plus a notice for remaining nucleotides.
- Translation History: Stores up to 5 of the most recent translations in database.
- Selectable History: History can be selected to reload input and output into their fields.
- Amino Acid Reference: Reference key for all 20 amino acids, plus stop codon.
- Browser-Based Access: Available at http://bfx3.aap.jhu.edu/kpablic1/final_project/index.cgi 


## File Structure

/var/www/html/kpablic1/final_project/

- index.cgi # Main Python CGI script
- README.md # Documentation final
- templates/
    - main.html # Main page template
    - error.html # Error page template
- static/
    - css/
        - style.css # Page styling
    - jss/
        - translator.js # Client-side JavaScript/jQuery
- sql/
    - schema.sql # Database schema


## Installation

This section provides instructions to install the program in your own directory. 

### Prerequisites

- Apache web server with CGI enabled
- Python 3.x
- MySQL database
- Required Python modules:
  - `mysql-connector-python`
  - `jinja2`

### Step 1: Clone/Copy Files
Copy all project files to your web server directory:
cp -r final_project /var/www/html/[username]/


### Step 2: Set Permissions
cd /var/www/html/[username]/
chmod 755 final_project


## Database Setup

This section goes over setting up the History table in your database, using schema.sql.

### Step 1: Connect to MySQL
mysql -u [username] -p

### Step 2: Create Table
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

### Step 3: Verify
SHOW TABLES LIKE 'translations';
DESCRIBE translations;


## Configuration

Edit the get_db_connection() function in index.cgi to match your database credentials:

def get_db_connection():
    """Create and return database connection."""
    conn = mysql.connector.connect(
        host='localhost',
        user='your_username',
        password='your_password',
        database='your_database'
    )
    return conn


## Usage

Navigate to: http://[server]/[username]/final_project/index.cgi

### Translating A Sequence:
1. Enter a DNA or RNA sequence in the input field
- DNA sequences should contain: A, T, C, G
- RNA sequences should contain: A, U, C, G
- Max length: 300 characters
2. Click the "Translate" button (or press Ctrl+Enter)
3. View the resulting amino acid sequence in the output box

### Output Details:
- Protein sequence: Displayed in green using single-letter amino acid codes
- Stop codons: Represented by asterisk (*)
- Type: Shows whether input was detected as DNA or RNA
- Length: Shows number of nucleotides in input
- Protein length: Shows number of amino acids in output

### Using History:
- Recent translations appear in the History section (up to 5)
- Click any history item to reload it
- Click "Clear History" to remove all saved translations


## Technical Details

### Codon Table
The tool uses the standard genetic code for translation:

- Alanine - A - GCT, GCC, GCA, GCG
- Cysteine - C - TGT, TGC
- Aspartic acid - D - GAT, GAC
- Glutamic acid - E - GAA, GAG
- Phenylalanine - F - TT, TTC
- Glycine - G - GGT, GGC, GGA, GGG
- Histidine - H - CAT, CAC
- Isoleucine - I - ATT, ATC, ATA
- Lysine - K - AAA, AAG
- Leucine - L - TTA, TTG, CTT, CTC, CTA, CTG
- Methionine - M - ATG
- Asparagine - N - AAT, AAC
- Proline - P - CCT, CCC, CCA, CCG
- Glutamine - Q - CAA, CAG
- Arginine - R - CGT, CGC, CGA, CGG, AGA, AGG
- Serine - S - TCT, TCC, TCA, TCG, AGT, AGC
- Threonine - T - ACT, ACC, ACA, ACG
- Valine - V - GTT, GTC, GTA, GTG
- Tryptophan - W - TGG
- Tyrosine - Y - TAT, TAC
- Stop - * - TAA, TAG, TGA

Note: these codons are given in DNA bases; RNA replaces T with U.

### Tech Stack
- Backend: Python 3 CGI
- Frontend: HTML5, CSS3, JavaScript/jQuery
- Database: MySQL
- Templating: Jinja2


## Author
Kristan Jeryc Pablico - kpablic1
AS.410.712.81.SP26 - Advanced Practical Computer Concepts for Bioinformatics

This project was created for educational purposes.