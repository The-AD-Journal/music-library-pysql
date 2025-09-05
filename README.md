# 🎵 Music Library Manager (Python + MySQL CLI)

A simple, menu‑driven **command‑line interface** for managing a personal music collection, built with **Python** and **MySQL**.  
Designed for ease of use — no SQL knowledge required — and with a touch of visual flair in the terminal.

---

## ✨ Features

- **Add Tracks** — Store track details including album, artist, year, genre, and optional comments.
- **View All Tracks** — Display your full collection in a clean, tabular format.
- **Search** — Find tracks by partial matches in track, album, artist, or genre.
- **Edit Entries** — Correct typos or update details without re‑entering the whole record.
- **Delete Tracks** — Remove unwanted entries with confirmation prompts.
- **Color‑coded CLI** — ANSI colors and banners for a more pleasant terminal experience.

---

## 🗄 Database Schema

**Database:** `music_db`  
**Table:** `collection`

| Column   | Type           | Notes                          |
|----------|---------------|--------------------------------|
| id       | INT (PK, AI)  | Auto‑increment primary key     |
| track    | VARCHAR(255)  | Track title (required)         |
| album    | VARCHAR(255)  | Album name                     |
| artist   | VARCHAR(255)  | Artist name                    |
| year     | YEAR          | Release year                   |
| genre    | VARCHAR(100)  | Genre                          |
| comment  | TEXT          | Optional notes/comments        |

---

## 📦 Requirements

- **Python** 3.7+
- **MySQL Server** 8.0+ (or MySQL 8.4 LTS)
- **mysql‑connector‑python** (install via pip)

---

## ⚙️ Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/The-AD-Journal/music-library-pysql.git
   cd music-library-pysql
