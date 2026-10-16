import importlib
import io
import json
from email import policy
from email.parser import BytesParser
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import zipfile

from contact_core import ContactError, extract_contacts, drafts, draft_archive, csv_export
from studio import Handler

CONTACT = {"email": "hello@example.org", "organization": "Juniper", "source_url": "https://example.org/contact", "note": "Saturday mornings"}


class ContactTests(unittest.TestCase):
    def test_visible_text_mailto_entities_and_deduplication(self):
        content = '<p>HELLO@example.org</p><a href="mailto:hello@example.org?subject=Hi">contact</a><a href="mailto:team%2Bvolunteer%40example.co.uk">Mail</a><p>reading&#64;example.edu</p>'
        result = extract_contacts(content, "https://EXAMPLE.org/contact#top", "Juniper")
        self.assertEqual([r["email"] for r in result], ["HELLO@example.org", "reading@example.edu", "team+volunteer@example.co.uk"])
        self.assertEqual(result[0]["source_url"], "https://example.org/contact")

    def test_scripts_styles_images_are_not_contacts(self):
        content = '<script>secret@example.org</script><style>x:asset@example.org</style><img src="asset@example.org"><p>icon@2x.png</p><a href="mailto:good@example.org">Contact</a>'
        self.assertEqual([r["email"] for r in extract_contacts(content, "https://example.org")], ["good@example.org"])

    def test_sentence_punctuation_does_not_hide_addresses(self):
        self.assertEqual([r["email"] for r in extract_contacts("Write to hello@example.org. Or ask team@example.co.uk!", "https://example.org")], ["hello@example.org", "team@example.co.uk"])

    def test_unknown_missing_and_malformed_fields_fail(self):
        for body in ["{{name}}", "{{note}}", "{{organization", "{{organization-name}}"]:
            with self.subTest(body=body), self.assertRaises(ContactError):
                drafts([{**CONTACT, "note": ""}], "Hello", body)

    def test_subject_header_injection_fails(self):
        with self.assertRaises(ContactError):
            drafts([CONTACT], "Hello\r\nBcc: hidden@example.org", "Message")
        with self.assertRaises(ContactError):
            drafts([{**CONTACT, "organization": "Name\nBcc: no"}], "{{organization}}", "Message")

    def test_export_mime_roundtrip_and_one_recipient_per_draft(self):
        contacts = [CONTACT, {**CONTACT, "email": "other@example.org", "organization": "Café"}]
        blob = draft_archive(contacts, "Meet {{organization}}", "Hello {{organization}} — {{note}}")
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            self.assertEqual(archive.namelist(), ["draft-001.eml", "draft-002.eml", "contacts.csv"])
            message = BytesParser(policy=policy.default).parsebytes(archive.read("draft-002.eml"))
            self.assertEqual(str(message["To"]), "other@example.org")
            self.assertEqual(str(message["Subject"]), "Meet Café")
            self.assertEqual(str(message["X-Unsent"]), "1")
            self.assertIn("Hello Café — Saturday mornings", message.get_content())
            self.assertNotIn("Bcc", message)

    def test_contact_deduplication_is_case_insensitive(self):
        self.assertEqual(len(drafts([CONTACT, {**CONTACT, "email": "HELLO@example.org"}], "Hello", "Hi")), 1)

    def test_csv_formula_cells_escaped(self):
        csv = csv_export([{**CONTACT, "organization": "=SUM(1,2)", "note": "+cmd"}]).decode("utf-8-sig")
        self.assertIn("'=SUM", csv)
        self.assertIn("'+cmd", csv)

    def test_source_urls_reject_active_schemes_and_credentials(self):
        for url in ["javascript:alert(1)", "https://user:pass@example.org", "https://example.org:bad", "https://example.org/a b", None]:
            with self.subTest(url=url), self.assertRaises(ContactError):
                extract_contacts("hello@example.org", url)

    def test_limits_and_invalid_input(self):
        for contacts in [None, [], [CONTACT] * 501, ["bad"], [{**CONTACT, "email": "not-an-email"}]]:
            with self.subTest(contacts=type(contacts)), self.assertRaises(ContactError):
                drafts(contacts, "Hello", "Hello")
        with self.assertRaises(ContactError):
            extract_contacts("x" * 500001, "https://example.org")

    def test_imports_do_not_connect_or_start_ui(self):
        with patch("socket.socket.connect", side_effect=AssertionError("network on import")), patch("builtins.input", side_effect=AssertionError("input on import")):
            for name in ["mail", "scraper", "subdirectory_finder", "window"]:
                importlib.import_module(name)


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, payload=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port)
        connection.request("POST" if payload is not None else "GET", path, json.dumps(payload) if payload is not None else None, headers or {"Content-Type": "application/json"})
        response = connection.getresponse()
        result = response.status, response.read()
        connection.close()
        return result

    def test_complete_extract_preview_export_flow(self):
        status, raw = self.request("/api/extract", {"text": "hello@example.org", "url": "https://example.org", "organization": "Example"})
        self.assertEqual(status, 200)
        payload = {"contacts": json.loads(raw)["contacts"], "subject": "Hello {{organization}}", "body": "Found you at {{source_url}}"}
        status, raw = self.request("/api/preview", payload)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)["drafts"][0]["subject"], "Hello Example")
        status, raw = self.request("/api/export", payload)
        self.assertEqual(status, 200)
        self.assertTrue(zipfile.is_zipfile(io.BytesIO(raw)))

    def test_assets_are_allowlisted(self):
        for path in ["/contact_core.py", "/.git/config", "/../README.md", "/login.txt"]:
            self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request("/")[0], 200)

    def test_foreign_origin_and_host_are_rejected(self):
        self.assertEqual(self.request("/api/preview", {}, {"Content-Type": "application/json", "Origin": "https://example.com"})[0], 403)
        self.assertEqual(self.request("/", headers={"Host": "malicious.example"})[0], 403)

    def test_bad_payloads_return_useful_errors(self):
        self.assertEqual(self.request("/api/extract", {"text": ""})[0], 400)
        self.assertEqual(self.request("/api/export", {"contacts": [], "subject": "", "body": ""})[0], 400)


if __name__ == "__main__":
    unittest.main()
