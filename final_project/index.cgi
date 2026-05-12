#!/usr/local/bin/python3

import cgi
import json
import mysql.connector
import jinja2
import sys

# Template setup
templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
env = jinja2.Environment(loader=templateLoader)

# Standard codon table (DNA codons -> amino acids)
CODON_TABLE = {
    'TTT': 'F', 'TTC': 'F',
    'TTA': 'L', 'TTG': 'L', 'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I',
    'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S', 'AGT': 'S', 'AGC': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y',
    'TAA': '*', 'TAG': '*', 'TGA': '*',
    'CAT': 'H', 'CAC': 'H',
    'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N',
    'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D',
    'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C',
    'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
}

# Create and return database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='kpablic1',
        password='St4r032907!x2',
        database='kpablic1'
    )
    return conn

# Remove whitespace and convert to uppercase
def sanitize_sequence(sequence):
    return ''.join(sequence.split()).upper()

# Validate the sequence and detect if DNA or RNA
# Returns (is_valid, seq_type, error_message)
def validate_sequence(sequence):
    if not sequence:
        return False, None, "No sequence provided."
    
    if len(sequence) > 300:
        return False, None, "Sequence exceeds maximum length of 300 characters."
    
    dna_bases = set('ATCG')
    rna_bases = set('AUCG')
    seq_bases = set(sequence)
    
    if 'T' in seq_bases and 'U' not in seq_bases:
        if seq_bases.issubset(dna_bases):
            return True, 'DNA', None
        else:
            invalid = seq_bases - dna_bases
            return False, None, f"Invalid DNA characters: {', '.join(invalid)}"
    
    elif 'U' in seq_bases and 'T' not in seq_bases:
        if seq_bases.issubset(rna_bases):
            return True, 'RNA', None
        else:
            invalid = seq_bases - rna_bases
            return False, None, f"Invalid RNA characters: {', '.join(invalid)}"
    
    elif 'T' in seq_bases and 'U' in seq_bases:
        return False, None, "Sequence contains both T and U. Please use only DNA (ATCG) or RNA (AUCG)."
    
    else:
        if seq_bases.issubset(dna_bases):
            return True, 'DNA', None
        else:
            invalid = seq_bases - dna_bases
            return False, None, f"Invalid characters: {', '.join(invalid)}"

# Convert RNA sequence to DNA by replacing U with T
def rna_to_dna(sequence):
    return sequence.replace('U', 'T')

# Translate DNA/RNA sequence to amino acid sequence
# Returns (protein, warning_message)
def translate_sequence(sequence, seq_type):
    if seq_type == 'RNA':
        sequence = rna_to_dna(sequence)
    
    warning = None
    remainder = len(sequence) % 3
    
    if remainder != 0:
        warning = f"Note: {remainder} nucleotide(s) at the end were not translated (incomplete codon)."
    
    protein = []
    for i in range(0, len(sequence) - remainder, 3):
        codon = sequence[i:i+3]
        amino_acid = CODON_TABLE.get(codon, 'X')
        protein.append(amino_acid)
    
    return ''.join(protein), warning

# Save translation to database, maintaining max 5 entries
def save_to_database(input_seq, seq_type, seq_length, output_protein):
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO translations (input_seq, seq_type, seq_length, output_protein)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (input_seq, seq_type, seq_length, output_protein))
        
        delete_query = """
            DELETE FROM translations 
            WHERE id NOT IN (
                SELECT id FROM (
                    SELECT id FROM translations 
                    ORDER BY id DESC 
                    LIMIT 5
                ) AS recent
            )
        """
        cursor.execute(delete_query)
        
        conn.commit()
        return True
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}", file=sys.stderr)
        return False
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Retrieve up to 5 most recent translations
def get_history():
    conn = None
    cursor = None
    results = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT id, input_seq, seq_type, seq_length, output_protein 
            FROM translations 
            ORDER BY id DESC 
            LIMIT 5
        """
        cursor.execute(query)
        results = cursor.fetchall()
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}", file=sys.stderr)
        results = []
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return results

# Clear all translation history from database
def clear_history():
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM translations")
        conn.commit()
        return True
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}", file=sys.stderr)
        return False
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Retrieve a specific history entry by ID
def get_history_entry(entry_id):
    conn = None
    cursor = None
    result = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM translations WHERE id = %s"
        cursor.execute(query, (entry_id,))
        result = cursor.fetchone()
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}", file=sys.stderr)
        result = None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return result

# Send JSON response with appropriate headers
def send_json_response(data):
    print("Content-Type: application/json")
    print()
    print(json.dumps(data))


def main():
    # Get form data
    form = cgi.FieldStorage()
    action = form.getvalue('action', '')
    
    # Handle AJAX requests (return JSON)
    if action:
        if action == 'translate':
            sequence = form.getvalue('sequence', '')
            sequence = sanitize_sequence(sequence)
            
            is_valid, seq_type, error_message = validate_sequence(sequence)
            
            if not is_valid:
                send_json_response({
                    'success': False,
                    'error': error_message
                })
                return
            
            protein, warning = translate_sequence(sequence, seq_type)
            save_to_database(sequence, seq_type, len(sequence), protein)
            history = get_history()
            
            send_json_response({
                'success': True,
                'input_sequence': sequence,
                'seq_type': seq_type,
                'seq_length': len(sequence),
                'protein': protein,
                'warning': warning,
                'history': history
            })
        
        elif action == 'get_history':
            history = get_history()
            send_json_response({
                'success': True,
                'history': history
            })
        
        elif action == 'clear_history':
            success = clear_history()
            send_json_response({
                'success': success,
                'message': 'History cleared' if success else 'Failed to clear history'
            })
        
        elif action == 'get_entry':
            entry_id = form.getvalue('id')
            if entry_id:
                entry = get_history_entry(int(entry_id))
                if entry:
                    send_json_response({
                        'success': True,
                        'entry': entry
                    })
                else:
                    send_json_response({
                        'success': False,
                        'error': 'Entry not found'
                    })
            else:
                send_json_response({
                    'success': False,
                    'error': 'No entry ID provided'
                })
        
        else:
            send_json_response({
                'success': False,
                'error': 'Unknown action'
            })
        
        return
    
    # Handle regular page load (return HTML)
    print("Content-Type: text/html")
    print()
    
    history = []
    error_message = None
    
    try:
        history = get_history()
    except Exception as e:
        error_message = f"An error occurred loading history: {str(e)}"
    
    template = env.get_template('main.html')
    html_output = template.render(
        history=history,
        history_count=len(history),
        error_message=error_message
    )
    
    print(html_output)


if __name__ == '__main__':
    main()