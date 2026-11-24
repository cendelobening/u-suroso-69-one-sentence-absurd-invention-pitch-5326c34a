"""One-Sentence Absurd Invention Pitch entry.

Writes a single original one-sentence pitch to <output dir>/entry.txt
and verifies the file afterwards. Pure standard library.

The pitch itself imagines the Wifisitter, a tiny traffic cop for home
Wi-Fi who waves video calls through with a white glove and fines a
smart fridge for buffering the meeting. The program validates that
the sentence is exactly one sentence within the 220-character limit,
writes it atomically, and reads it back to prove the file on disk is
byte-for-byte the sentence that was validated.
"""

import os
import stat
import tempfile

# The one line: a tiny traffic cop for your home Wi-Fi.
LINE = (
    "The Wifisitter is a tiny traffic cop for your home Wi-Fi "
    "who waves your video calls through with a white glove "
    "and fines your smart fridge for buffering the meeting."
)

MAX_CHARS = 220


def describe():
    """Return a one-line summary of what this program does."""
    return "Writes one absurd one-sentence invention pitch to entry.txt."


def check_line(line):
    """Make sure the line is a single clean sentence within the limit."""
    if not isinstance(line, str):
        raise ValueError("line must be a string")
    if not line.strip():
        raise ValueError("line must not be only whitespace")
    if line != line.strip():
        raise ValueError("line must have no leading or trailing whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("line must be a single line")
    if any(ord(ch) < 0x20 for ch in line):
        raise ValueError("line must not contain control characters")
    if not 1 <= len(line) <= MAX_CHARS:
        raise ValueError("line must be 1-220 characters, got %d" % len(line))
    if not line.endswith("."):
        raise ValueError("line must end with a single period")
    if line.count(".") != 1:
        raise ValueError("line must contain exactly one period")
    if "?" in line or "!" in line:
        raise ValueError("line must contain no other sentence-ending punctuation")
    if line.endswith(".."):
        raise ValueError("line must not end with a doubled period")


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    check_line(LINE)
    out_dir = output_dir()
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")

    # Write to a temp file in the same directory, then atomically
    # move it into place so the entry is never seen half-written.
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(LINE)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    os.chmod(target, 0o644)

    # Read it back and confirm it is exactly what we meant to write,
    # byte for byte, with no stray newline or encoding surprise.
    with open(target, "rb") as handle:
        raw = handle.read()
    if raw != LINE.encode("utf-8"):
        raise ValueError("verification failed: entry.txt does not match the line")
    if raw.decode("utf-8") != LINE:
        raise ValueError("verification failed: entry.txt is not valid UTF-8 text")
    if raw.endswith(b"\n"):
        raise ValueError("verification failed: entry.txt has a trailing newline")
    mode = stat.S_IMODE(os.stat(target).st_mode)
    if mode != 0o644:
        raise ValueError("verification failed: entry.txt mode is %o" % mode)
    print(
        "%s Wrote %d characters (%d bytes) to %s: %s"
        % (describe(), len(LINE), len(raw), target, LINE)
    )


if __name__ == "__main__":
    main()
