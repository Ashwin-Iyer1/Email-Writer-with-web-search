"""Contact extraction and draft generation. No network or credential side effects."""
from __future__ import annotations
import csv
from email.message import EmailMessage
from email.policy import SMTP
from html.parser import HTMLParser
import io
import re
from urllib.parse import unquote, urlsplit, urlunsplit
import zipfile

EMAIL = re.compile(r"(?<![\w.+-])([A-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?\.)+[A-Z]{2,63})(?![\w-]|\.[A-Z0-9])", re.I)
TOKEN = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")
FIELDS = {"organization", "email", "source_url", "note"}

class ContactError(ValueError):
    pass

def source_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        raise ContactError("Enter a source URL up to 2,048 characters.")
    try:
        parsed = urlsplit(value.strip())
        parsed.port
    except ValueError as exc:
        raise ContactError("Invalid source URL.") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or any(c.isspace() for c in value):
        raise ContactError("Use an http or https source URL without credentials or spaces.")
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path or "/", parsed.query, ""))

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.mailtos, self.hidden = [], [], 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template"}:
            self.hidden += 1
        if not self.hidden and tag == "a":
            href = dict(attrs).get("href") or ""
            if href.lower().startswith("mailto:"):
                self.mailtos.append(unquote(href[7:].split("?", 1)[0]))
        if tag in {"p", "div", "br", "li"}:
            self.parts.append(" ")
    def handle_endtag(self, tag):
        if tag in {"script", "style", "template"} and self.hidden:
            self.hidden -= 1
        self.parts.append(" ")
    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)

def extract_contacts(text, url, organization=""):
    if not isinstance(text, str) or not text.strip() or len(text) > 500_000:
        raise ContactError("Paste page text or HTML between 1 and 500,000 characters.")
    url = source_url(url)
    if not isinstance(organization, str) or len(organization) > 160 or "\n" in organization or "\r" in organization:
        raise ContactError("Use an organization name up to 160 characters on one line.")
    parser = VisibleText()
    parser.feed(text)
    content = " ".join(parser.parts + parser.mailtos)
    contacts, seen = [], set()
    for match in EMAIL.finditer(content):
        email = match.group(1)
        key = email.casefold()
        if len(email) > 254 or len(email.split("@")[0]) > 64 or key.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")) or key in seen:
            continue
        seen.add(key)
        contacts.append({"email": email, "organization": organization.strip() or urlsplit(url).hostname, "source_url": url, "note": ""})
    return contacts

def validate_contacts(contacts):
    if not isinstance(contacts, list) or not 1 <= len(contacts) <= 500:
        raise ContactError("Select between 1 and 500 contacts.")
    seen, result = set(), []
    for contact in contacts:
        if not isinstance(contact, dict):
            raise ContactError("Each contact must be an object.")
        clean = {field: contact.get(field, "") for field in FIELDS}
        if any(not isinstance(v, str) for v in clean.values()):
            raise ContactError("Contact fields must be text.")
        email = clean["email"].strip()
        if not EMAIL.fullmatch(email) or len(email) > 254 or len(email.split("@")[0]) > 64:
            raise ContactError("Every contact must have a valid email address.")
        if email.casefold() in seen:
            continue
        seen.add(email.casefold())
        clean["email"] = email
        clean["source_url"] = source_url(clean["source_url"])
        if len(clean["organization"]) > 160 or len(clean["note"]) > 2000:
            raise ContactError("Organization or note is too long.")
        if any("\r" in clean[f] or "\n" in clean[f] for f in ("email", "organization")):
            raise ContactError("Email and organization must fit on one line.")
        result.append(clean)
    return result

def render(template, contact):
    if not isinstance(template, str) or len(template) > 20_000:
        raise ContactError("Templates must be text up to 20,000 characters.")
    tokens = set(TOKEN.findall(template))
    unknown = tokens - FIELDS
    if unknown:
        raise ContactError("Unknown template field: " + ", ".join(sorted(unknown)))
    remainder = TOKEN.sub("", template)
    if "{{" in remainder or "}}" in remainder:
        raise ContactError("A template field has incomplete braces or an invalid name.")
    for name in tokens:
        if not contact.get(name, "").strip():
            raise ContactError(f"Fill {name} for {contact.get('email', 'this contact')} before export.")
    return TOKEN.sub(lambda match: contact[match.group(1)], template)

def drafts(contacts, subject, body):
    if not isinstance(subject, str) or not subject.strip() or not isinstance(body, str) or not body.strip():
        raise ContactError("Add a subject and message before export.")
    result = []
    for contact in validate_contacts(contacts):
        title, message = render(subject, contact), render(body, contact)
        if "\n" in title or "\r" in title or len(title) > 200:
            raise ContactError("Keep every rendered subject on one line, under 201 characters.")
        result.append({"contact": contact, "subject": title, "body": message})
    return result

def csv_export(contacts):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["email", "organization", "source_url", "note"])
    writer.writeheader()
    for contact in validate_contacts(contacts):
        writer.writerow({k: ("'" + v if v.lstrip().startswith(("=", "+", "-", "@")) else v) for k, v in contact.items()})
    return output.getvalue().encode("utf-8-sig")

def draft_archive(contacts, subject, body):
    output = io.BytesIO()
    items = drafts(contacts, subject, body)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for index, item in enumerate(items, 1):
            msg = EmailMessage(policy=SMTP)
            msg["To"], msg["Subject"], msg["X-Unsent"] = item["contact"]["email"], item["subject"], "1"
            msg.set_content(item["body"])
            archive.writestr(f"draft-{index:03}.eml", msg.as_bytes())
        archive.writestr("contacts.csv", csv_export([item["contact"] for item in items]))
    return output.getvalue()
