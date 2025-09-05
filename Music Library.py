# Music Management CLI — MySQL + Python (mysql-connector)
import mysql.connector as myst
from mysql.connector import Error

# ====== CLI Colors (ANSI) ======
RESET = "\033[0m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
DIM = "\033[2m"

# ====== Configuration Placeholders ======
HOST = "localhost"         # e.g., "localhost"
USER = "root"     # e.g., "root"
PASSWORD = "54@30#ROOT" # e.g., "rootpassword"
DB_NAME = "music_db"         # confirmed
TABLE_NAME = "collection"    # confirmed

# Whitelist of columns for safe updates/selections
COLUMNS = ["track", "album", "artist", "year", "genre", "comment"]

# ====== Banner ======
def print_banner():
    print(CYAN + "=" * 50 + RESET)
    print(CYAN + "🎵  MUSIC LIBRARY MANAGER — MySQL CLI".center(50) + RESET)
    print(CYAN + "=" * 50 + RESET)

# ====== Connection and Setup ======
def create_server_connection():
    try:
        conn = myst.connect(
            host=HOST,
            user=USER,
            password=PASSWORD
            # Note: no database here on purpose
        )
        return conn
    except Error as e:
        print(RED + f"Connection error: {e}" + RESET)
        return None

def create_database_if_needed():
    server_conn = create_server_connection()
    if not server_conn:
        return False
    try:
        cur = server_conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        server_conn.commit()
        cur.close()
        server_conn.close()
        return True
    except Error as e:
        print(RED + f"DB create error: {e}" + RESET)
        return False

def create_db_connection():
    try:
        conn = myst.connect(
            host=HOST,            # e.g., "localhost"
            user=USER,            # e.g., "root"
            password=PASSWORD,
            database=DB_NAME
        )
        return conn
    except Error as e:
        print(RED + f"Connection error (DB): {e}" + RESET)
        return None

def create_table_if_needed(conn):
    try:
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                track VARCHAR(255) NOT NULL,
                album VARCHAR(255),
                artist VARCHAR(255),
                year YEAR,
                genre VARCHAR(100),
                comment TEXT
            )
        """)
        conn.commit()
        cur.close()
    except Error as e:
        print(RED + f"Table create error: {e}" + RESET)

# ====== Utilities ======
def confirm(prompt="Are you sure? [y/N]: "):
    ans = input(YELLOW + prompt + RESET).strip().lower()
    return ans in ("y", "yes")

def input_optional(prompt):
    val = input(prompt).strip()
    return val if val != "" else None

def print_rows(rows):
    if not rows:
        print(DIM + "No records found." + RESET)
        return
    # Simple fixed-width table for readability
    headers = ["ID", "Track", "Album", "Artist", "Year", "Genre", "Comment"]
    widths = [5, 22, 20, 20, 6, 12, 24]
    line = "+".join("-" * w for w in widths)
    def fmt_row(r):
        out = []
        for i, w in enumerate(widths):
            cell = "" if r[i] is None else str(r[i])
            if len(cell) > w - 2:
                cell = cell[: w - 5] + "..."
            out.append(cell.ljust(w - 1))
        return "|".join(out)

    print(DIM + line + RESET)
    print("|".join(h.ljust(w - 1) for h, w in zip(headers, widths)))
    print(DIM + line + RESET)
    for r in rows:
        print(fmt_row(r))
    print(DIM + line + RESET)

def get_all(conn):
    cur = conn.cursor()
    cur.execute(f"SELECT id, track, album, artist, year, genre, comment FROM {TABLE_NAME} ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_by_id(conn, rec_id):
    cur = conn.cursor()
    cur.execute(
        f"SELECT id, track, album, artist, year, genre, comment FROM {TABLE_NAME} WHERE id = %s",
        (rec_id,)
    )
    row = cur.fetchone()
    cur.close()
    return row

# ====== Features ======
def add_track(conn):
    print_banner()
    print(YELLOW + "Add a new track" + RESET)
    track = input("Track: ").strip()
    album = input_optional("Album (optional): ")
    artist = input_optional("Artist (optional): ")
    year = input_optional("Year (YYYY, optional): ")
    genre = input_optional("Genre (optional): ")
    comment = input_optional("Comment (optional): ")

    if year and not year.isdigit():
        print(RED + "Year must be numeric (e.g., 1997). Leaving it empty." + RESET)
        year = None

    print(DIM + "\nReview entry:" + RESET)
    preview = [(None, track, album, artist, year, genre, comment)]
    print_rows(preview)
    if not confirm("Save this entry? [y/N]: "):
        print(RED + "Add cancelled." + RESET)
        return

    try:
        cur = conn.cursor()
        cur.execute(
            f"""INSERT INTO {TABLE_NAME} (track, album, artist, year, genre, comment)
                VALUES (%s, %s, %s, %s, %s, %s)""",
            (track, album, artist, year, genre, comment)
        )
        conn.commit()
        cur.close()
        print(GREEN + "Track added successfully!" + RESET)
    except Error as e:
        print(RED + f"Insert error: {e}" + RESET)

def view_tracks(conn):
    print_banner()
    print(YELLOW + "All tracks" + RESET)
    rows = get_all(conn)
    print_rows(rows)
    input(DIM + "Press Enter to return to menu..." + RESET)

def search_tracks(conn):
    print_banner()
    print(YELLOW + "Search tracks" + RESET)
    print(DIM + "Type a keyword to search in track/album/artist/genre." + RESET)
    keyword = input("Keyword: ").strip()
    cur = conn.cursor()
    like = f"%{keyword}%"
    cur.execute(
        f"""SELECT id, track, album, artist, year, genre, comment
            FROM {TABLE_NAME}
            WHERE track LIKE %s OR album LIKE %s OR artist LIKE %s OR genre LIKE %s
            ORDER BY id""",
        (like, like, like, like)
    )
    rows = cur.fetchall()
    cur.close()
    print_rows(rows)
    input(DIM + "Press Enter to return to menu..." + RESET)

def edit_track(conn):
    print_banner()
    print(YELLOW + "Edit a track" + RESET)
    rows = get_all(conn)
    print_rows(rows)
    rec_id = input("Enter ID to edit: ").strip()
    if not rec_id.isdigit():
        print(RED + "Invalid ID." + RESET)
        return
    record = get_by_id(conn, rec_id)
    if not record:
        print(RED + "No record with that ID." + RESET)
        return

    # Show fields to edit with numbers to minimize typing
    print(DIM + "\nChoose a field to edit:" + RESET)
    for idx, col in enumerate(COLUMNS, start=1):
        print(f"{idx}. {col}")
    choice = input("Field number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(COLUMNS)):
        print(RED + "Invalid choice." + RESET)
        return

    col = COLUMNS[int(choice) - 1]
    new_val = input(f"New value for {col} (leave empty to set NULL): ").strip()
    val = new_val if new_val != "" else None

    print(DIM + "\nBefore:" + RESET)
    print_rows([record])
    # Create a preview of the "after" row
    rec_list = list(record)
    col_index_map = { "track":1, "album":2, "artist":3, "year":4, "genre":5, "comment":6 }
    rec_list[col_index_map[col]] = val
    print(DIM + "After:" + RESET)
    print_rows([tuple(rec_list)])

    if not confirm("Apply this change? [y/N]: "):
        print(RED + "Edit cancelled." + RESET)
        return

    try:
        cur = conn.cursor()
        # Use whitelist for column to avoid injection; value is parameterized
        cur.execute(f"UPDATE {TABLE_NAME} SET {col} = %s WHERE id = %s", (val, rec_id))
        conn.commit()
        cur.close()
        print(GREEN + "Track updated successfully!" + RESET)
    except Error as e:
        print(RED + f"Update error: {e}" + RESET)

def delete_track(conn):
    print_banner()
    print(YELLOW + "Delete a track" + RESET)
    rows = get_all(conn)
    print_rows(rows)
    rec_id = input("Enter ID to delete: ").strip()
    if not rec_id.isdigit():
        print(RED + "Invalid ID." + RESET)
        return
    record = get_by_id(conn, rec_id)
    if not record:
        print(RED + "No record with that ID." + RESET)
        return

    print(DIM + "\nYou are about to delete:" + RESET)
    print_rows([record])
    if not confirm("This cannot be undone. Proceed? [y/N]: "):
        print(RED + "Delete cancelled." + RESET)
        return

    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {TABLE_NAME} WHERE id = %s", (rec_id,))
        conn.commit()
        cur.close()
        print(GREEN + "Track deleted." + RESET)
    except Error as e:
        print(RED + f"Delete error: {e}" + RESET)

# ====== Main Menu ======
def main_menu(conn):
    while True:
        print_banner()
        print(YELLOW + "Choose an option by number:" + RESET)
        print("1. Add track")
        print("2. View tracks")
        print("3. Search tracks")
        print("4. Edit track")
        print("5. Delete track")
        print("6. Exit")
        choice = input("Your choice: ").strip()
        if choice == "1":
            add_track(conn)
        elif choice == "2":
            view_tracks(conn)
        elif choice == "3":
            search_tracks(conn)
        elif choice == "4":
            edit_track(conn)
        elif choice == "5":
            delete_track(conn)
        elif choice == "6":
            print(GREEN + "Goodbye!" + RESET)
            break
        else:
            print(RED + "Invalid choice. Please select 1–6." + RESET)

# ====== Entry Point ======
def main():
    print_banner()
    print(DIM + "Initializing database..." + RESET)
    if not create_database_if_needed():
        print(RED + "Could not ensure database exists. Check your connection settings." + RESET)
        return
    conn = create_db_connection()
    if not conn:
        print(RED + "Could not connect to database. Check your connection settings." + RESET)
        return
    create_table_if_needed(conn)
    print(GREEN + "Ready." + RESET)
    main_menu(conn)
    try:
        conn.close()
    except:
        pass

if __name__ == "__main__":
    main()