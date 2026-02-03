import os
import sys

# Allow running this script directly: `python scripts/seed_students.py`
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from db.students import bulk_upsert_students
from db.database import init_db


def main() -> None:
    init_db()

    students = [
        ("karmugilan g r", "2303737720521032", "B.TECH (IT)-III"),
        ("abinithi g", "2303737724422038", "B.TECH (CSBS)-III"),
        ("mathiarasi e", "2303737724422047", "B.TECH (CSBS)-III"),
        ("sri vishnu t s", "2303737724421030", "B.TECH (CSBS)-III"),
        ("charan b", "2303737724421004", "B.TECH (CSBS)-III"),
        ("jevithesh s", "2303737714821015", "B.E CSE (AIML)-III"),
        ("shivani d a", "2303737714822057", "B.E CSE (AIML)-III"),
        ("narendra a", "2303737714821025", "B.E CSE (AIML)-III"),
        ("sandhya", "2303737714822055", "B.E CSE (AIML)-III"),
        ("kavin kumar s", "2303737714821017", "B.E CSE (AIML)-III"),
        ("nidish m i", "2303737710621045", "B.E ECE-III"),
        ("saran g", "2303737724321033", "B.TECH (AI & DS)-III"),
        ("dhiranesh k m", "2303737724321009", "B.TECH (AI & DS)-III"),
        ("ramalingam t", "2303737724321030", "B.TECH (AI & DS)-III"),
        ("rethies ragavendira m", "2303737724321032", "B.TECH (AI & DS)-III"),
        ("varshini devi d k", "2303737724322062", "B.TECH (AI & DS)-III"),
        ("surya a", "2303737724321036", "B.TECH (AI & DS)-III"),
        ("nivetha rajan", "2303737710422100", "B.E (CSE)-III"),
        ("hema shree", "2303737710422085", "B.E (CSE)-III"),
        ("afrin s", "2303737710422071", "B.E (CSE)-III"),
        ("kanikshaa r", "2403737714822048", "B.E CSE (AIML)-II"),
    ]

    processed = bulk_upsert_students(students)
    print(f"Seeded {processed} students into PostgreSQL")


if __name__ == "__main__":
    main()
