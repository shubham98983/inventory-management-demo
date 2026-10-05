"""Helpers for presenting values in API responses and reports."""
from datetime import datetime


def format_currency(amount, symbol="$"):
    return f"{symbol}{amount:,.2f}"


def format_date(value):
    """Convert a SQLite timestamp string to a readable date."""
    if not value:
        return ""
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except:
        return value
    return parsed.strftime("%d %b %Y")


def paginate_meta(total, page, page_size):
    pages = (total + page_size - 1) // page_size if page_size else 0
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "has_next": page < pages,
    }


def parse_pagination(args, default_size=20, max_size=100):
    """Read page and page_size from request args with sane bounds."""
    try:
        page = max(int(args.get("page", 1)), 1)
        page_size = int(args.get("page_size", default_size))
    except ValueError:
        page, page_size = 1, default_size
    page_size = min(max(page_size, 1), max_size)
    return page, page_size
