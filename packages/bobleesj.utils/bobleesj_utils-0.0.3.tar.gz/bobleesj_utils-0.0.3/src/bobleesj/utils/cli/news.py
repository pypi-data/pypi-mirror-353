import os
import shutil

from bobleesj.utils.cli import auth

HEADER_MAP = {
    "a": "**Added:**",
    "c": "**Changed:**",
    "d": "**Deprecated:**",
    "r": "**Removed:**",
    "f": "**Fixed:**",
    "s": "**Security:**",
}

TEMPLATE_PATH = "news/TEMPLATE.rst"
NEWS_DIR = "news"


def ensure_news_file(branch):
    path = os.path.join(NEWS_DIR, f"{branch}.rst")
    if not os.path.exists(path):
        shutil.copy(TEMPLATE_PATH, path)
    return path


def read_news_file(path):
    with open(path, "r") as f:
        return f.readlines()


def write_news_file(path, lines):
    with open(path, "w") as f:
        f.writelines(lines)


def insert_message_in_section(lines, section, message):
    new_lines = []
    inserted = False
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        new_lines.append(line)

        if not inserted and stripped == section:
            # Clean out placeholder and blank lines
            j = i + 1
            while j < len(lines) and lines[j].strip() in ("", "* <news item>"):
                j += 1

            new_lines.append("\n")
            new_lines.append(f"* {message}\n")
            if j >= len(lines) or lines[j].strip().startswith("**"):
                new_lines.append("\n")
            inserted = True
            i = j - 1  # Skip cleared lines
        i += 1

    return ensure_section_spacing(new_lines)


def insert_message_multiple_sections(lines, flags, message):
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        new_lines.append(line)

        for flag in flags:
            if stripped == HEADER_MAP[flag]:
                j = i + 1
                while j < len(lines) and lines[j].strip() in (
                    "",
                    "* <news item>",
                ):
                    j += 1

                new_lines.append("\n")
                new_lines.append(f"* {message}\n")
                if j >= len(lines) or lines[j].strip().startswith("**"):
                    new_lines.append("\n")
                i = j - 1
        i += 1

    return ensure_section_spacing(new_lines)


def ensure_section_spacing(lines):
    fixed_lines = []
    for idx, line in enumerate(lines):
        fixed_lines.append(line)
        if line.strip().startswith("**") and idx + 1 < len(lines):
            if lines[idx + 1].strip() != "":
                fixed_lines.append("\n")
    return fixed_lines


def add_news_item(args):
    message = args.message
    flags_used = [flag for flag in HEADER_MAP if getattr(args, flag)]
    branch = auth.get_current_branch()
    path = ensure_news_file(branch)
    lines = read_news_file(path)
    updated = insert_message_multiple_sections(lines, flags_used, message)
    write_news_file(path, updated)

    print(f"Done! Appended news item to {path}")


def add_no_news_item(args):
    message = f"no news added: {args.message}"
    branch = auth.get_current_branch()
    path = ensure_news_file(branch)
    lines = read_news_file(path)
    updated = insert_message_in_section(lines, HEADER_MAP["a"], message)
    write_news_file(path, updated)

    print(f"Done! Appended 'no news' entry to {path}")
