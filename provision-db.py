import sqlite3

def get_phrases_from_file(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

def provision_database(file_path, db_path):
    phrases = get_phrases_from_file(file_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS phrases
                          (phrase TEXT PRIMARY KEY, llm_definition TEXT, processed INTEGER DEFAULT 0)''')

        for phrase in phrases:
            cursor.execute("INSERT OR IGNORE INTO phrases (phrase) VALUES (?)", (phrase,))
            print("Inserted into database ", phrase)
        conn.commit()

if __name__ == "__main__":
    file_path = './mit-phrase-clean.txt'
    db_path = 'phrases.sqlite3'
    provision_database(file_path, db_path)
