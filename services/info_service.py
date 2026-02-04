from __future__ import annotations

from typing import Optional
import psycopg2.extras

from db.database import get_conn, init_db


def _fetch_one(query: str, params: tuple = ()) -> Optional[dict]:
    init_db()
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_trait_response(field: str | None = None) -> str:
    info = _fetch_one(
        """
        SELECT title, description, vision, mission, location, contact_email
        FROM trait_info
        ORDER BY id DESC
        LIMIT 1
        """
    )

    if not info:
        return "Trait center information is not available."

    title = info.get("title") or "Trait Center"
    description = info.get("description") or ""
    vision = info.get("vision") or ""
    mission = info.get("mission") or ""
    location = info.get("location") or ""
    contact_email = info.get("contact_email") or ""

    if field == "vision":
        return f"{title} vision: {vision or 'not provided.'}"
    if field == "mission":
        return f"{title} mission: {mission or 'not provided.'}"
    if field == "location":
        return f"{title} location: {location or 'not provided.'}"
    if field == "contact":
        return f"{title} contact email: {contact_email or 'not provided.'}"

    parts = [title]
    if description:
        parts.append(description)
    if location:
        parts.append(f"Location: {location}.")
    if contact_email:
        parts.append(f"Contact: {contact_email}.")
    return " ".join(parts).strip()


def get_guest_welcome_note(name: str | None = None) -> str:
    if name:
        info = _fetch_one(
            """
            SELECT name, welcome_note, organization, designation, visit_purpose, visit_date
            FROM guests
            WHERE name ILIKE %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (f"%{name}%",),
        )
    else:
        info = _fetch_one(
            """
            SELECT name, welcome_note, organization, designation, visit_purpose, visit_date
            FROM guests
            ORDER BY id DESC
            LIMIT 1
            """
        )

    if not info:
        return "Guest information is not available."

    guest_name = info.get("name") or "Guest"
    welcome_note = info.get("welcome_note") or "Welcome"
    org = info.get("organization")
    designation = info.get("designation")
    purpose = info.get("visit_purpose")

    extra = []
    if designation:
        extra.append(designation)
    if org:
        extra.append(org)
    if purpose:
        extra.append(f"Purpose: {purpose}")

    extra_text = ", ".join(extra)
    if extra_text:
        return f"Welcome note for {guest_name}: {welcome_note}. {extra_text}."

    return f"Welcome note for {guest_name}: {welcome_note}."


def get_projects_summary() -> str:
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT title
        FROM projects
        WHERE status = 'ONGOING'
        ORDER BY id DESC
        """
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "There are no ongoing projects."

    titles = [r[0] for r in rows]
    return "Ongoing projects: " + ", ".join(titles)


def get_project_details(title: str) -> str:
    info = _fetch_one(
        """
        SELECT title, description, domain, status, mentor, start_date, end_date
        FROM projects
        WHERE title ILIKE %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (f"%{title}%",),
    )

    if not info:
        return f"I couldn't find a project named {title}."

    parts = [info.get("title") or "Project"]
    if info.get("description"):
        parts.append(info["description"])
    if info.get("domain"):
        parts.append(f"Domain: {info['domain']}")
    if info.get("status"):
        parts.append(f"Status: {info['status']}")
    if info.get("mentor"):
        parts.append(f"Mentor: {info['mentor']}")
    if info.get("start_date"):
        parts.append(f"Start date: {info['start_date']}")
    if info.get("end_date"):
        parts.append(f"End date: {info['end_date']}")

    return ". ".join(parts).strip() + "."
