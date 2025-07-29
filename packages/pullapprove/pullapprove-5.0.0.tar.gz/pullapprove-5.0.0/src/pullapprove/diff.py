import re


def parse_diff_file_line(line):
    match = re.match(r"^diff --git a/(.*) b/(.*)", line)
    if match:
        a_path, b_path = match.groups()
        return DiffFile(
            old_path=a_path.strip(),
            new_path=b_path.strip(),
        )
    return None


def parse_diff_hunk_line(line):
    match = re.match(r"^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@", line)
    if match:
        old_line, old_length, new_line, new_length = match.groups()
        return DiffHunk(
            old_line=int(old_line),
            old_length=int(old_length) if old_length else None,
            new_line=int(new_line),
            new_length=int(new_length) if new_length else None,
        )
    return None


def iterate_diff_parts(diff):
    current_file, current_hunk = None, None

    # Keep track of where we are in the hunk as we go
    hunk_minus_line_number, hunk_plus_line_number = 0, 0

    for raw in diff:
        if new_file := parse_diff_file_line(raw):
            current_file = new_file
            current_hunk = None
            yield new_file  # Yield the new file as we go
        elif current_file:
            if new_hunk := parse_diff_hunk_line(raw):
                current_hunk = new_hunk

                hunk_minus_line_number = current_hunk.old_line
                hunk_plus_line_number = current_hunk.new_line
            elif current_hunk:
                if raw.startswith("+"):
                    yield DiffCode(
                        line_number=hunk_plus_line_number,
                        content=raw[1:],
                        change_type="+",
                    )
                    hunk_plus_line_number += 1
                elif raw.startswith("-"):
                    yield DiffCode(
                        line_number=hunk_minus_line_number,
                        content=raw[1:],
                        change_type="-",
                    )
                    hunk_minus_line_number += 1
                elif raw.startswith(" "):
                    yield DiffCode(
                        line_number=hunk_plus_line_number,  # would need plus and minus if we wanted to show split...
                        content=raw[1:],
                        change_type="",
                    )
                    hunk_plus_line_number += 1
                    hunk_minus_line_number += 1
                else:
                    continue
            else:
                # Header/meta lines between file and hunk...
                pass


class DiffFile:
    def __init__(self, *, old_path, new_path):
        self.old_path = old_path
        self.new_path = new_path

    def __repr__(self):
        return f"<DiffFile old_path={self.old_path} new_path={self.new_path}>"

    def is_move(self):
        return self.old_path != self.new_path


class DiffHunk:
    def __init__(self, *, old_line, old_length, new_line, new_length):
        self.old_line = old_line
        self.old_length = old_length
        self.new_line = new_line
        self.new_length = new_length


class DiffCode:
    def __init__(self, *, line_number, content, change_type):
        self.line_number = line_number
        self.content = content
        self.change_type = change_type

    def __str__(self):
        return f"{self.line_number}: {self.change_type or ' '}{self.content}"

    def __repr__(self):
        return f"<DiffCode change_type={self.change_type} line_number={self.line_number} content={self.content}>"

    # def is_change(self):
    #     return self.change_type in ("+", "-")
