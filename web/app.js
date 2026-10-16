const $ = (id) => document.getElementById(id);
let contacts = [], previews = [], revision = 0, reviewedRevision = -1;
const selected = () => contacts.filter((c) => c.selected).map(({ selected, ...c }) => c);
function feedback(message, error = false) { $('feedback').textContent = message; $('feedback').classList.toggle('error', error); }
function invalidate() {
  revision++; reviewedRevision = -1; previews = [];
  $('download').disabled = true; $('preview-content').hidden = true; $('preview-empty').hidden = false;
}
async function api(path, data, binary = false) {
  const response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  if (!response.ok) { const error = await response.json(); throw new Error(error.error || 'The request failed.'); }
  return binary ? response.blob() : response.json();
}
function download(blob, name) {
  const url = URL.createObjectURL(blob), link = document.createElement('a');
  link.href = url; link.download = name; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function renderContacts() {
  const list = $('contact-list'); list.replaceChildren();
  $('count').textContent = `${selected().length} / ${contacts.length}`;
  $('select-all').checked = contacts.length > 0 && contacts.every((c) => c.selected);
  $('select-all').indeterminate = contacts.some((c) => c.selected) && !contacts.every((c) => c.selected);
  $('contacts-export').disabled = selected().length === 0;
  if (!contacts.length) { const empty = document.createElement('p'); empty.className = 'empty'; empty.textContent = 'Add a source to begin your contact list.'; list.append(empty); }
  contacts.forEach((contact) => {
    const card = document.createElement('div'); card.className = 'contact-card';
    const head = document.createElement('div'); head.className = 'contact-head';
    const check = document.createElement('input'); check.type = 'checkbox'; check.checked = contact.selected;
    check.setAttribute('aria-label', `Select ${contact.email}`);
    check.addEventListener('change', () => { contact.selected = check.checked; invalidate(); renderContacts(); });
    const heading = document.createElement('div'); heading.className = 'contact-heading';
    const title = document.createElement('strong'); title.textContent = contact.organization;
    const email = document.createElement('p'); email.textContent = contact.email;
    const source = document.createElement('a'); source.href = contact.source_url; source.textContent = 'View source ↗'; source.target = '_blank'; source.rel = 'noopener';
    heading.append(title, email, source);
    const remove = document.createElement('button'); remove.className = 'text-button remove'; remove.textContent = '×'; remove.setAttribute('aria-label', `Remove ${contact.email}`);
    remove.addEventListener('click', () => { contacts = contacts.filter((c) => c !== contact); invalidate(); renderContacts(); });
    head.append(check, heading, remove);
    const noteLabel = document.createElement('label'); noteLabel.textContent = 'Research note';
    const note = document.createElement('input'); note.type = 'text'; note.value = contact.note; note.maxLength = 2000; note.placeholder = 'A detail to personalize the message';
    noteLabel.append(note); note.addEventListener('input', () => { contact.note = note.value; invalidate(); });
    card.append(head, noteLabel); list.append(card);
  });
}
function addContacts(incoming, note = '') {
  const keys = new Set(contacts.map((c) => c.email.toLowerCase()));
  let added = 0;
  for (const contact of incoming) {
    if (!keys.has(contact.email.toLowerCase()) && contacts.length < 500) {
      keys.add(contact.email.toLowerCase()); contacts.push({ ...contact, note, selected: true }); added++;
    }
  }
  invalidate(); renderContacts(); return added;
}
function renderPreview() {
  const draft = previews[Number($('draft-select').value)];
  if (!draft) return;
  $('preview-to').textContent = `TO ${draft.contact.email}`;
  $('preview-subject').textContent = draft.subject; $('preview-body').textContent = draft.body;
}
$('source-form').addEventListener('submit', async (event) => {
  event.preventDefault(); $('extract').disabled = true; const requestRevision = revision;
  try {
    const { contacts: found } = await api('/api/extract', { text: $('source-text').value, url: $('source-url').value, organization: $('organization').value });
    if (requestRevision !== revision) { feedback('Workspace changed. Extract this source again.'); return; }
    const count = addContacts(found);
    feedback(found.length ? `${count} new contacts added. ${found.length - count} duplicate or over-limit addresses skipped. Review the source before using an address.` : 'No visible email addresses found. Try the contact section or a saved HTML page.');
  } catch (error) { feedback(error.message, true); } finally { $('extract').disabled = false; }
});
$('search-form').addEventListener('submit', (event) => { event.preventDefault(); window.open('https://www.google.com/search?' + new URLSearchParams({ q: $('query').value.trim() }), '_blank', 'noopener'); });
$('import-page').addEventListener('click', () => $('html-file').click());
$('html-file').addEventListener('change', async (event) => {
  const file = event.target.files[0]; if (!file) return;
  if (file.size > 500000) { feedback('Choose a saved page under 500 KB.', true); event.target.value = ''; return; }
  try { $('source-text').value = await file.text(); feedback(`Loaded ${file.name}. Add its source URL, then extract contacts.`); } catch { feedback('This page could not be read.', true); }
  event.target.value = '';
});
$('select-all').addEventListener('change', () => { contacts.forEach((c) => c.selected = $('select-all').checked); invalidate(); renderContacts(); });
for (const id of ['subject', 'message']) $(id).addEventListener('input', invalidate);
$('sample').addEventListener('click', async () => {
  $('sample').disabled = true; const requestRevision = revision;
  try {
    const samples = await (await fetch('/sample.json')).json();
    const groups = await Promise.all(samples.map(async (sample) => ({ ...(await api('/api/extract', sample)), note: sample.note })));
    if (requestRevision !== revision) { feedback('Workspace changed. Load the example again.'); return; }
    let count = 0; for (const group of groups) count += addContacts(group.contacts, group.note);
    feedback(`Added ${count} fictional example contacts. All example addresses use reserved example.org domains.`);
  } catch (error) { feedback(error.message, true); } finally { $('sample').disabled = false; }
});
$('clear').addEventListener('click', () => { contacts = []; invalidate(); renderContacts(); $('source-form').reset(); feedback('Workspace cleared.'); });
$('review').addEventListener('click', async () => {
  invalidate(); const requestRevision = revision; $('review').disabled = true;
  try {
    const result = await api('/api/preview', { contacts: selected(), subject: $('subject').value, body: $('message').value });
    if (requestRevision !== revision) return;
    previews = result.drafts; reviewedRevision = revision; $('draft-select').replaceChildren();
    previews.forEach((draft, index) => { const option = document.createElement('option'); option.value = index; option.textContent = draft.contact.email; $('draft-select').append(option); });
    $('preview-content').hidden = false; $('preview-empty').hidden = true; $('download').disabled = false; renderPreview();
    feedback(`${previews.length} drafts ready to review. Editing contacts or templates requires a fresh review.`);
  } catch (error) { feedback(error.message, true); } finally { $('review').disabled = false; }
});
$('draft-select').addEventListener('change', renderPreview);
$('download').addEventListener('click', async () => {
  if (reviewedRevision !== revision) return;
  const requestRevision = revision; $('download').disabled = true;
  try {
    const blob = await api('/api/export', { contacts: selected(), subject: $('subject').value, body: $('message').value }, true);
    if (requestRevision !== revision) return;
    download(blob, 'research-drafts.zip'); feedback(`Exported ${previews.length} individual drafts. No messages sent.`);
  } catch (error) { feedback(error.message, true); } finally { $('download').disabled = reviewedRevision !== revision; }
});
$('contacts-export').addEventListener('click', async () => { try { download(await api('/api/contacts', { contacts: selected() }, true), 'reviewed-contacts.csv'); } catch (error) { feedback(error.message, true); } });
