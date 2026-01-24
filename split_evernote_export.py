#!/usr/bin/env python3
import argparse
import html
import os
import re
from datetime import datetime, timezone
from pathlib import Path


EN_EXPORT_DTD = "http://xml.evernote.com/pub/evernote-export4.dtd"
ISSUES_URL = "https://github.com/dhk/evernote-local-archive/issues"


def utc_timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def parse_export_attrs(text):
    match = re.search(r"<en-export\s+([^>]+)>", text)
    attrs = {}
    if match:
        for key, value in re.findall(r'(\w+)="([^"]*)"', match.group(1)):
            attrs[key] = value
    if "export-date" not in attrs:
        attrs["export-date"] = utc_timestamp()
    if "application" not in attrs:
        attrs["application"] = "evernote-local-vault"
    if "version" not in attrs:
        attrs["version"] = "1.0"
    return attrs


def slugify(text):
    text = html.unescape(text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "untitled"


def date_prefix(created):
    if not created:
        return "unknown-date"
    try:
        dt = datetime.strptime(created, "%Y%m%dT%H%M%SZ")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return created[:10] or "unknown-date"


def humanize_created(created):
    if not created:
        return "unknown"
    try:
        dt = datetime.strptime(created, "%Y%m%dT%H%M%SZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return created


def extract_note_fields(note_inner):
    title_match = re.search(r"<title>(.*?)</title>", note_inner, flags=re.S)
    created_match = re.search(r"<created>(.*?)</created>", note_inner, flags=re.S)
    title = title_match.group(1).strip() if title_match else "Untitled"
    created = created_match.group(1).strip() if created_match else ""
    return title, created


def build_enex(attrs, note_xml):
    attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!DOCTYPE en-export SYSTEM "{EN_EXPORT_DTD}">\n'
        f"<en-export {attrs_str}>\n"
        f"{note_xml}\n"
        "</en-export>\n"
    )


def normalize_folder_uri(folder_uri):
    if folder_uri.endswith("/"):
        return folder_uri
    return f"{folder_uri}/"


def build_index_enml(note_items, index_title, source_name, folder_uri, issues_url):
    folder_uri = normalize_folder_uri(folder_uri)
    rows = "\n".join(
        "\n".join(
            [
                "<tr>",
                f"<td>{html.escape(item['title'])}</td>",
                f"<td>{html.escape(humanize_created(item['created']))}</td>",
                (
                    "<td>"
                    f"<a href=\"{html.escape(item['file_uri'])}\">"
                    f"{html.escape(item['filename'])}"
                    "</a>"
                    "</td>"
                ),
                (
                    "<td>"
                    f"<a href=\"{html.escape(folder_uri)}\">Show in Finder</a>"
                    "</td>"
                ),
                "</tr>",
            ]
        )
        for item in note_items
    )
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">',
            "<en-note>",
            f"<h1>{html.escape(index_title)}</h1>",
            (
                "<p><i>How to use:</i> Click a filename to reveal the file in "
                "Finder, then import the ENEX file via Evernote &rarr; "
                "File &rarr; Import.</p>"
            ),
            (
                "<p>"
                f"Compendium for <b>{html.escape(source_name)}</b>. "
                f"Total notes: <b>{len(note_items)}</b>."
                "</p>"
            ),
            "<table border=\"1\" cellpadding=\"6\" cellspacing=\"0\">",
            "<thead>",
            "<tr>",
            "<th>Title</th>",
            "<th>Created</th>",
            "<th>Filename</th>",
            "<th>Show in Finder</th>",
            "</tr>",
            "</thead>",
            "<tbody>",
            rows,
            "</tbody>",
            "</table>",
            "<hr/>",
            (
                "<p>"
                "<b>About the author:</b> "
                f"<a href=\"{html.escape(issues_url)}\">Issues and Questions</a>"
                " &middot; "
                "<a href=\"https://dhkondata.substack.com/\">DHK On Data and AI</a>"
                " &middot; "
                "<a href=\"https://www.linkedin.com/in/davehk/\">LinkedIn</a>"
                "</p>"
            ),
            "</en-note>",
        ]
    )


def build_index_enex(
    attrs,
    note_items,
    index_title,
    source_name,
    folder_uri,
    issues_url,
):
    created = utc_timestamp()
    enml = build_index_enml(
        note_items,
        index_title,
        source_name,
        folder_uri,
        issues_url,
    )
    note_xml = "\n".join(
        [
            "<note>",
            f"<title>{html.escape(index_title)}</title>",
            "<content><![CDATA[",
            enml,
            "]]></content>",
            f"<created>{created}</created>",
            f"<updated>{created}</updated>",
            "</note>",
        ]
    )
    return build_enex(attrs, note_xml)


def split_enex(source_path, output_dir, dry_run=False):
    text = Path(source_path).read_text(encoding="utf-8", errors="ignore")
    attrs = parse_export_attrs(text)

    note_blocks = re.findall(r"<note>(.*?)</note>", text, flags=re.S)
    if not note_blocks:
        raise ValueError("No <note> blocks found in ENEX file.")

    output_dir.mkdir(parents=True, exist_ok=True)
    used_names = {}

    outputs = []
    for note_inner in note_blocks:
        title, created = extract_note_fields(note_inner)
        filename_base = f"{date_prefix(created)}__{slugify(title)}"
        count = used_names.get(filename_base, 0) + 1
        used_names[filename_base] = count
        filename = f"{filename_base}__{count}.enex" if count > 1 else f"{filename_base}.enex"

        note_xml = f"<note>{note_inner}</note>"
        output_enex = build_enex(attrs, note_xml)
        output_path = output_dir / filename

        outputs.append(
            {
                "title": title,
                "created": created,
                "filename": output_path.name,
                "path": output_path,
                "file_uri": output_path.resolve().as_uri(),
            }
        )
        if not dry_run:
            output_path.write_text(output_enex, encoding="utf-8")

    return attrs, outputs


def main():
    parser = argparse.ArgumentParser(
        description="Split a notebook ENEX into one ENEX file per note."
    )
    parser.add_argument("source", help="Path to the source ENEX file.")
    parser.add_argument(
        "--output-dir",
        help="Directory for output ENEX files (default: sibling folder).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write files.")
    parser.add_argument(
        "--with-index",
        action="store_true",
        help="Write a vault index ENEX in the output directory.",
    )
    parser.add_argument(
        "--index-title",
        default="vault-index",
        help="Title for the index note (default: vault-index).",
    )
    parser.add_argument(
        "--index-name",
        default="vault-index.enex",
        help="Filename for the index ENEX (default: vault-index.enex).",
    )
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    if not source_path.exists():
        raise SystemExit(f"Source ENEX not found: {source_path}")

    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        output_dir = source_path.with_suffix("").with_name(
            f"{source_path.stem}-notes"
        )

    attrs, outputs = split_enex(source_path, output_dir, dry_run=args.dry_run)
    print(f"Wrote {len(outputs)} notes to {output_dir}")

    if args.with_index:
        index_enex = build_index_enex(
            attrs,
            outputs,
            args.index_title,
            source_path.stem,
            output_dir.resolve().as_uri(),
            ISSUES_URL,
        )
        index_path = output_dir / args.index_name
        if not args.dry_run:
            index_path.write_text(index_enex, encoding="utf-8")
        print(f"Wrote index note to {index_path}")


if __name__ == "__main__":
    main()
