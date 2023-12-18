import sqlite3
from langchain.llms import Ollama

def get_unprocessed_count(cursor):
    cursor.execute("SELECT COUNT(*) FROM phrases WHERE processed = 0")
    return cursor.fetchone()[0]

def get_unprocessed_phrases(cursor, batch_size):
    cursor.execute("SELECT phrase FROM phrases WHERE processed = 0 LIMIT ?", (batch_size,))
    return cursor.fetchall()

def get_definition_from_llm(phrase, ollama):
    try:
        return ollama("Please provide a concise definition of the phrase " + phrase)
    except Exception as e:
        print(f"Error getting definition for {phrase}: {e}")
        return None

def update_definition_in_db(phrase, definition, cursor):
    try:
        cursor.execute("UPDATE phrases SET llm_definition = ?, processed = 1 WHERE phrase = ?", (definition, phrase))
        print(f"Updated {phrase}")
    except sqlite3.Error as e:
        print(f"Database error for {phrase}: {e}")

def process_batch(cursor, ollama, batch_size):
    unprocessed_phrases = get_unprocessed_phrases(cursor, batch_size)
    for phrase_tuple in unprocessed_phrases:
        phrase = phrase_tuple[0]
        definition = get_definition_from_llm(phrase, ollama)
        if definition:
            update_definition_in_db(phrase, definition, cursor)

def main(db_path, batch_size):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        ollama = Ollama(base_url="http://localhost:11434", model="mistral")
        
        while True:
            unprocessed_count = get_unprocessed_count(cursor)
            if unprocessed_count == 0:
                print("All phrases have been processed.")
                break

            process_batch(cursor, ollama, batch_size)
            conn.commit()

            # Prompt the user to continue with the next batch
            cont = input("Process next batch? (y/n): ")
            if cont.lower() != 'y':
                print("Batch processing stopped.")
                break

if __name__ == "__main__":
    db_path = 'phrases.sqlite3'
    batch_size = 1000  # Adjust batch size as needed
    main(db_path, batch_size)
