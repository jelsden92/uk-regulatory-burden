"""extract_candidates.py — high-recall candidate-sentence extraction for the
regulatory-burden labelling pipeline.

Replaces analyser.py's classification layer. The production classifier is
Legal-BERT (fine-tuned); training labels are produced by the LLM+human layer
reading the rubric. This script's job is the PIPELINE that prepares sentences
for that layer (and, later, for Legal-BERT inference):

    XML ingest (downloader.parse_xml's BeautifulSoup + CLML status filter)
      -> structure-preserving provision walk (heading / section ref / parent)
      -> sentence split
      -> HIGH-RECALL candidate filter (union of all word_list cue sets)
      -> context attachment (preceding clause + definitions of defined terms)
      -> JSONL (one record per candidate) + flat CSV index

RECALL IS THE PRIORITY. The filter is deliberately over-inclusive: it surfaces
anything that MIGHT be a private-actor burden, and the LLM+human layer rejects
the non-operative ones. The filter must NEVER silently drop a possible burden.
Precision signals from the old classifier (definitional / structural / clause-
opener / purpose-clause) are kept only as NON-BLOCKING HINTS, never as drops.
The single mechanical drop is exact-duplicate dedup, which is LOGGED.

candidate_cue / is_in_schedule / is_amendment_insertion are HINTS, not labels.
No category or polarity label is emitted here.
"""
from __future__ import annotations

import re

from word_list import (
    PRESCRIPTIVE_WORDS,
    IMPLIED_OBLIGATION_WORDS,
    PENALTY_ONLY_TERMS,
    RIGHTS_CUES,
    RESTRICTION_PROHIBITION_CUES,
    VOID_CUES,
    RESPONSIBILITY_CUES,
    DEFENCE_CUES,
    PENALTY_OBLIGATION_CUES,
    BARE_REQUIRED_CUES,
    COMPLIANCE_VERB_CUES,
    ENFORCEMENT_POWER_CUES,
    LEADING_DUTY_VERBS,
    DEFINITIONAL_PATTERNS,
    STRUCTURAL_SUBJECTS,
    CLAUSE_OPENERS,
    OCR_CORRECTIONS,
)

# ---------------------------------------------------------------------------
# Candidate cue groups — the UNION high-recall filter
# ---------------------------------------------------------------------------
# Grouped so the matched group is recorded as a hint, but ANY match surfaces the
# sentence. Order/labels are hints only; they are NOT the classification.
CUE_GROUPS = {
    'obligation': (PRESCRIPTIVE_WORDS['obligations'] + RESPONSIBILITY_CUES
                   + BARE_REQUIRED_CUES + PENALTY_OBLIGATION_CUES + COMPLIANCE_VERB_CUES),
    'prohibition': (PRESCRIPTIVE_WORDS['prohibitions'] + RESTRICTION_PROHIBITION_CUES
                    + VOID_CUES),
    'right': RIGHTS_CUES,
    'implied': IMPLIED_OBLIGATION_WORDS + DEFENCE_CUES,
    'penalty': PENALTY_ONLY_TERMS,
    'enforcement_submit': ENFORCEMENT_POWER_CUES,
}


def _compile_group(terms):
    # Longest-first alternation with word boundaries; case-insensitive.
    pat = '|'.join(re.escape(t) for t in sorted(set(terms), key=len, reverse=True))
    return re.compile(r'\b(?:' + pat + r')\b', re.IGNORECASE)


_CUE_RES = {g: _compile_group(terms) for g, terms in CUE_GROUPS.items()}

# General "no <noun> shall/may/is to/are to" prohibition (beyond "no person").
_NO_X_RE = re.compile(
    r'\bno\s+[a-z][a-z\-]*(?:\s+[a-z][a-z\-]*){0,2}\s+(?:shall|may|is\s+to|are\s+to)\b',
    re.IGNORECASE)

# Active "require/requiring <someone> to <act>" — imposes a duty to act on the
# named party (e.g. "may require the organisation to supply …").
_REQUIRE_TO_RE = re.compile(
    r'\brequir(?:e|es|ed|ing)\s+(?:\w+\s+){1,4}?to\b', re.IGNORECASE)

# Leading imperative duty-verb (list-item fragment whose modal is in the parent
# stem). Fires only when the sentence BEGINS with one of these after numbering is
# stripped — the list-item signature — to limit false fires on normal sentences.
_LEADING_VERB_RE = re.compile(
    r'^(?:' + '|'.join(re.escape(v) for v in sorted(set(LEADING_DUTY_VERBS), key=len, reverse=True))
    + r')\b', re.IGNORECASE)

# Hint matchers (non-blocking).
_DEF_RE = _compile_group(DEFINITIONAL_PATTERNS)
_STRUCT_RE = re.compile(
    r'^(?:the\s+|a\s+|an\s+)?(?:' +
    '|'.join(re.escape(s) for s in sorted(set(STRUCTURAL_SUBJECTS), key=len, reverse=True)) +
    r')\b', re.IGNORECASE)
_CLAUSE_RE = re.compile(
    r'^(?:' + '|'.join(re.escape(c) for c in CLAUSE_OPENERS) + r')\b', re.IGNORECASE)
_LEADING_NUM = re.compile(r'^(?:\s*\d[\w.\-]*\s+)+')
_OCR_RE = re.compile(r'\b(' + '|'.join(re.escape(k) for k in OCR_CORRECTIONS) + r')\b')


def _ocr_fix(text):
    return _OCR_RE.sub(lambda m: OCR_CORRECTIONS[m.group(1)], text)


def candidate_cues(sentence):
    """Return the list of matched cue strings (group:term) for a sentence, or []
    if nothing fires. Non-empty => surface as a candidate. RECALL-oriented."""
    s = _ocr_fix(sentence)
    hits = []
    for group, rx in _CUE_RES.items():
        for m in rx.finditer(s):
            hits.append(f'{group}:{m.group(0).lower()}')
    if _NO_X_RE.search(s):
        hits.append('prohibition:no_<noun>_shall')
    if _REQUIRE_TO_RE.search(s):
        hits.append('obligation:require_<x>_to')
    # Leading imperative verb: only on a list-item fragment (verb at the start
    # after stripping leading numbering/letters).
    if _LEADING_VERB_RE.match(_LEADING_NUM.sub('', s).strip()):
        hits.append('obligation:leading_imperative_verb')
    # de-dup preserving order
    seen = set()
    return [h for h in hits if not (h in seen or seen.add(h))]


def hint_flags(sentence):
    """Non-blocking precision hints (NEVER cause a drop). These help the LLM+human
    layer spot likely non-operative sentences without the filter removing them."""
    s = _LEADING_NUM.sub('', sentence).strip()
    flags = []
    if _DEF_RE.search(sentence):
        flags.append('non_operative_suspect')
    if _STRUCT_RE.match(s):
        flags.append('structural_subject_suspect')
    if _CLAUSE_RE.match(s):
        flags.append('clause_opener')
    # Recital / soft-law suspect (esp. retained-EU): "should" as the modal with no
    # binding shall/must, or a numbered recital paragraph. Surfaced for recall but
    # flagged so the reviewer can fast-reject soft-law.
    if (re.search(r'\bshould\b', s, re.I) and not re.search(r'\b(shall|must)\b', s, re.I)) \
            or re.match(r'^\(?\d{1,4}\)?\s+[A-Z]', s):
        flags.append('recital_suspect')
    return flags


def is_candidate(sentence):
    return bool(candidate_cues(sentence))


# ---------------------------------------------------------------------------
# Structure-preserving parse — walk the CLML provision tree for context
# ---------------------------------------------------------------------------
import collections
import csv
import hashlib
import json

import nltk
from bs4 import BeautifulSoup

import downloader  # reuse fetch_xml + strip_metadata + strip_no_force_provisions

_P_LEVELS = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7']
_DEF_TERM_RE = re.compile(r'[“"“]([^”"”]{2,60})[”"”]\s+(?:means|includes)\b', re.I)
_INLINE_DEF_RE = re.compile(r'\([“"“]([^”"”]{2,60})[”"”]\)')


def _split(text):
    try:
        return [s.strip() for s in nltk.sent_tokenize(text) if s.strip()]
    except Exception:
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def _ref_for(node):
    """Hierarchical provision reference, bracket-formatted so it is an unambiguous
    JOIN KEY: section/article bare, deeper levels in parens -> '7(2)(a)',
    'Article 25(d)'. P-levels take priority; EU Division/Para Number is a
    fallback only when there is no P-level number (recitals/annexes), so good
    article refs are never corrupted by an enclosing chapter number."""
    parts = []
    for anc in node.find_parents(_P_LEVELS):
        pn = anc.find('Pnumber')
        if pn:
            parts.append(pn.get_text(strip=True).strip('()').strip())
    if not parts:
        for anc in node.find_parents(['Para', 'Division']):
            num = anc.find('Number')
            if num:
                parts.append(num.get_text(strip=True).strip('()').strip())
                break
    parts.reverse()
    if not parts:
        return ''
    return parts[0] + ''.join(f'({p})' for p in parts[1:] if p)


def _heading_for(node):
    for anc in node.find_parents(['P1group', 'Pblock', 'Part', 'Chapter', 'Division']):
        t = anc.find('Title')
        if t:
            return t.get_text(' ', strip=True)
    return ''


def _in_schedule(node):
    return bool(node.find_parent(['Schedule', 'ScheduleBody', 'Schedules']))


def _in_amendment(node):
    return bool(node.find_parent(['Addition', 'ins', 'InF']))


# Generic self-references that are not real defined terms — exclude from the
# definitions index (they match the "( … )" / "means" patterns but carry no
# definitional content and add noise to every candidate).
_DEF_STOPTERMS = {
    'this act', 'the act', 'this regulation', 'the regulation', 'this section',
    'this subsection', 'this paragraph', 'this part', 'this schedule', 'this order',
    'this chapter', 'these regulations', 'the regulations', 'the schedule',
    'a', 'an', 'the', 'it', 'he', 'she', 'they', 'such', 'that', 'this',
}


def build_definitions(soup):
    """{lower_term: (definition_sentence, ref)} from interpretation provisions."""
    defs = {}
    for tx in soup.find_all('Text'):
        s = tx.get_text(' ', strip=True)
        terms = [m.group(1) for m in _DEF_TERM_RE.finditer(s)] + _INLINE_DEF_RE.findall(s)
        for raw in terms:
            term = raw.strip().lower()
            if (term and term not in defs and term not in _DEF_STOPTERMS
                    and len(term) >= 3 and re.search('[a-z]', term)):
                defs[term] = (s[:300], _ref_for(tx))
    return defs


def _defs_in(sentence, defs):
    sl = sentence.lower()
    out = []
    for term, (dtext, dref) in defs.items():
        if re.search(r'\b' + re.escape(term) + r'\b', sl):
            out.append({'term': term, 'definition': dtext, 'ref': dref})
    return out[:8]  # cap


# ---------------------------------------------------------------------------
# Section anchoring — the RATIFIED three-tier unit (see project_decision_log 2026-07-16)
# ---------------------------------------------------------------------------
# Tier 1: outermost P-level (UK section / EU article / schedule P-level). Tier 2:
# innermost NUMBERED Division|Para for non-P-level text (EU recitals/paras,
# schedule paragraphs). Tier 3 (added 2026-07-16): schedule/annex prose-and-list
# content and bare-<P> body tail-clauses that fall outside any numbered tree — routed
# into three NEW material types (uk_schedule_unnumbered / eu_annex / uk_body_tail);
# grain = per-entry (enumerated lists) / whole-form / paragraph-block. Taxonomy semantics
# v2 (2026-07-16): types describe CONTENT — EU-family Schedule-mapped content is eu_annex at
# every tier (not just tier-3). Keyed on DOM node identity, NOT section_ref (which is
# non-unique — "24(1)" maps to five distinct provisions in EP Regs). EU nesting
# grain = innermost numbered unit (one recital/para = one section), matching the
# UK "one numbered provision = one section" grain. Editorial text excluded.
_NUM_LEVELS = _P_LEVELS + ['Division', 'Para']
_SCHED_TAGS = ['Schedule', 'Schedules', 'ScheduleBody']
_EDITORIAL = ('Commentary', 'Commentaries', 'Footnote', 'Footnotes', 'MultilineTitle')

# Tier-3 anchor (ratified 2026-07-16): schedule/annex prose-and-list content and bare-<P>
# body tail-clauses get real anchors in three NEW material types, so the four documented
# tier-1/2 counters (uk_body/uk_schedule/eu_article/eu_recital) are provably untouched.
_TIER3_TYPES = ('uk_schedule_unnumbered', 'eu_annex', 'uk_body_tail')
# Genuine prelims/signature editorial: stays excluded from tier-3 anchoring (as now, orphan/flat).
_PRELIM_EDITORIAL = ('MadeDate', 'ComingIntoForce', 'ComingIntoForcePara', 'Signatory',
                     'SignedSection', 'EnactingText', 'Prelims', 'PrimaryPrelims',
                     'SecondaryPrelims', 'EUPrelims', 'EUPreamble', 'Preamble', 'Approval')


def _own_number(el):
    """The element's OWN provision number (direct Pnumber/Number child), or ''."""
    for tag in ('Pnumber', 'Number'):
        n = el.find(tag, recursive=False)
        if n:
            t = n.get_text(strip=True)
            if t:
                return t
    return ''


def _list_marker(li):
    """Marker for an OrderedList/UnorderedList ListItem — read from list structure
    (NumberOverride attr, else same-level position), formatted by the list's Decoration/Type.
    List numbering lives in list attributes, not a <Number> child (the _own_number blind spot)."""
    ol = li.find_parent(['OrderedList', 'UnorderedList'])
    ov = li.get('NumberOverride')
    if ov:
        n = ov.strip('()').strip()
    else:
        n = str(1 + sum(1 for _ in li.find_previous_siblings('ListItem')))
    typ = ((ol.get('Type') if ol else '') or 'arabic').lower()
    if typ.startswith('alpha'):
        try:
            n = chr(96 + int(n))               # 1 -> a
        except ValueError:
            pass
    deco = ((ol.get('Decoration') if ol else '') or '').lower()
    return f'({n})' if 'paren' in deco else n


def _own_title(anc):
    """The container's OWN heading (direct Title, or Title inside its own TitleBlock) — NOT a
    recursive descendant Title (which would grab a schedule-wide first heading for deep content)."""
    for src in (anc, anc.find('TitleBlock', recursive=False)):
        if src is None:
            continue
        t = src.find('Title', recursive=False)
        if t and t.get_text(strip=True):
            return t.get_text(' ', strip=True)
    return ''


def _tier3_title(el):
    """Nearest GOVERNING heading above a tier-3 anchor: the closest titled block, falling back
    to the enclosing Schedule/annex number (e.g. 'ANNEX III', 'FIFTH SCHEDULE') so no ref is empty."""
    for anc in el.find_parents(['Pblock', 'Division', 'Chapter', 'Part']):
        t = _own_title(anc)
        if t:
            return t
    for anc in el.find_parents(['Schedule', 'Schedules']):
        t = _own_title(anc)
        if t:
            return t
        for src in (anc, anc.find('TitleBlock', recursive=False)):
            if src is None:
                continue
            n = src.find('Number', recursive=False)
            if n and n.get_text(strip=True):
                return n.get_text(' ', strip=True)
    return ''


def _tier3_ref_heading(el):
    """(section_ref, heading) for a tier-3 anchor. Enumerated list entries get a real
    list ref ('FIFTH SCHEDULE para (3)' / 'ANNEX I item 2'); blocks/forms get the block title."""
    title = _tier3_title(el)
    if el.name == 'ListItem':
        word = 'item' if title.upper().startswith('ANNEX') else 'para'
        marker = _list_marker(el)
        ref = f'{title} {word} {marker}'.strip() if title else marker
        return ref, title
    return title, title


def _section_root(tx, is_eu=False):
    """(section_element, material_type, is_tier3) for a Text node, or (None, None, False)
    for genuinely non-sectioned text. `is_tier3` marks anchors found by the tier-3 fallback,
    so ref/heading keys on the ANCHOR TIER, not on material_type (semantics v2 decoupling:
    eu_annex now spans tiers 1-2 numbered annexes AND tier-3 unnumbered annex prose, but only
    the latter uses _tier3_ref_heading). Anchoring/grain unchanged from the tier-3 build."""
    plevels = tx.find_parents(_P_LEVELS)
    in_sched = tx.find_parent(_SCHED_TAGS) is not None
    in_eubody = tx.find_parent('EUBody') is not None
    # Taxonomy semantics v2 (2026-07-16): material_type describes CONTENT, not anchoring history.
    # Schedule-mapped content in EU-family instruments is eu_annex at EVERY tier (legislation.gov.uk
    # maps EU annexes onto Schedule; pre-checked: all EU-family Schedule content is annex, no
    # protocols/appendices). Anchor element, grain, boundaries, refs and headings are unchanged —
    # this is a type LABEL delta only.
    sched_mat = 'eu_annex' if is_eu else 'uk_schedule'
    # --- Tier 1 ---
    if plevels:
        root = plevels[-1]                     # outermost P-level = section/article
        if in_sched:
            return root, sched_mat, False
        if in_eubody:
            return root, 'eu_article', False
        return root, 'uk_body', False
    # --- Tier 2 ---
    for a in tx.find_parents(['Division', 'Para']):   # innermost numbered unit
        if _own_number(a):
            return (a, sched_mat, False) if in_sched else (a, 'eu_recital', False)
    # --- Tier 3 (NEW) — genuinely outside any numbered tree ---
    if tx.find_parent(_PRELIM_EDITORIAL):
        return None, None, False               # editorial prelims/preamble stay excluded (as now)
    if is_eu:
        # EU annex material (annexes map onto Schedule/Division; preamble already excluded above).
        lis = tx.find_parents('ListItem')
        if lis:
            return lis[-1], 'eu_annex', True   # outermost list entry — per-entry grain
        blk = tx.find_parent('Pblock') or tx.find_parent(['P', 'BlockText'])
        if blk:
            return blk, 'eu_annex', True       # paragraph-block grain
        div = tx.find_parent(['Division', 'Schedule', 'Part'])
        if div:
            return div, 'eu_annex', True       # last-resort whole-division/annex
        return None, None, False
    if in_sched:
        lis = tx.find_parents('ListItem')
        if lis:
            return lis[-1], 'uk_schedule_unnumbered', True   # outermost list entry — per-entry grain
        pb = tx.find_parent('Pblock')
        if pb:
            return pb, 'uk_schedule_unnumbered', True        # paragraph-block / whole-form grain
        pp = tx.find_parent(['P', 'BlockText'])
        if pp:
            return pp, 'uk_schedule_unnumbered', True
        sp = tx.find_parent(['Part', 'Schedule'])
        if sp:
            return sp, 'uk_schedule_unnumbered', True        # last-resort whole-Part/Schedule
        return None, None, False
    # main body bare-<P> tail-clause (e.g. Explosives 1875 extent clauses)
    pb = tx.find_parent('Pblock') or tx.find_parent('P')
    if pb:
        return pb, 'uk_body_tail', True
    return None, None, False


def _marker_chain(tx, section_el):
    """Numbered markers from the section root down to this text's innermost
    numbered container (outer->inner). len==1 => chapeau/section-own text."""
    chain = []
    for a in tx.find_parents(_NUM_LEVELS):
        num = _own_number(a)
        if num:
            chain.append(num.strip('()').strip())
        if a is section_el:
            break
    chain.reverse()
    return chain


def _assemble(section_el, texts):
    """Assemble chapeau + leaves into one block with markers/structure preserved
    (NO truncation), plus the leaves as a structured list."""
    lines, leaves = [], []
    for tx in texts:
        block = tx.get_text(' ', strip=True)
        if not block:
            continue
        chain = _marker_chain(tx, section_el)
        if len(chain) >= 2:                       # a leaf beneath the section root
            marker = chain[-1]
            lines.append(f'{"  " * (len(chain) - 1)}({marker}) {block}')
            leaves.append({'marker': marker, 'ref': _ref_for(tx),
                           'text': block, 'own_cue': bool(candidate_cues(block))})
        else:                                     # chapeau / section-own text
            lines.append(block)
    return '\n'.join(lines), leaves


def _dedupe(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]


def extract_from_xml(xml_text, item_url, title, year, leg_type):
    """Return (candidate_records, stats, dropped_dups). ONE record per flagged
    SECTION (Stage-1 unit): a section is flagged if >=1 cue fires anywhere in its
    subtree, so cue-less leaves ride in on the chapeau's cue. Non-P-level /
    non-numbered text keeps the old flat per-sentence behaviour."""
    soup = BeautifulSoup(xml_text, 'lxml-xml')
    downloader.strip_metadata(soup)
    downloader.strip_no_force_provisions(soup)
    defs = build_definitions(soup)

    records, seen_hashes, dropped_dups = [], set(), []
    item_slug = item_url.rstrip('/').split('/')[-1]
    is_eu = leg_type in ('eur', 'eudn')

    # Group Text nodes into sections by DOM identity, in document order.
    sections = collections.OrderedDict()          # id(el) -> {el, material, texts}
    orphan_texts = []
    for tx in soup.find_all('Text'):
        if not tx.get_text(strip=True):
            continue
        if any(tx.find_parent(x) for x in _EDITORIAL):
            continue
        root, material, tier3 = _section_root(tx, is_eu)
        if root is None:
            orphan_texts.append(tx)
            continue
        k = id(root)
        if k not in sections:
            sections[k] = {'el': root, 'material': material, 'tier3': tier3, 'texts': []}
        sections[k]['texts'].append(tx)

    resolved = collections.Counter()
    for idx, sec in enumerate(sections.values()):
        el, material, texts = sec['el'], sec['material'], sec['texts']
        resolved[material] += 1
        assembled, leaves = _assemble(el, texts)
        if not assembled:
            continue
        cues, hints = [], []
        for tx in texts:
            b = tx.get_text(' ', strip=True)
            cues += candidate_cues(b)
            hints += hint_flags(b)
        cues, hints = _dedupe(cues), _dedupe(hints)
        if not cues:                              # Stage-1: no signal anywhere -> not flagged
            continue
        h = hashlib.md5(re.sub(r'\s+', ' ', assembled.strip().lower()).encode()).hexdigest()[:12]
        if h in seen_hashes:
            dropped_dups.append({'hash': h, 'text': assembled[:160], 'section_index': idx})
            continue
        seen_hashes.add(h)
        first = texts[0]
        if sec['tier3']:                       # ref/heading keys on ANCHOR TIER, not material_type
            ref, heading = _tier3_ref_heading(el)
        else:
            ref = _own_number(el) or _ref_for(first)
            heading = _heading_for(first)
        quality = 'full' if (ref or heading) else 'partial'
        in_amend = _in_amendment(el) or any(_in_amendment(t) for t in texts)
        records.append({
            # DOM-identity key: section_index is the document-order position of the
            # section node; the block hash disambiguates. section_ref is display-only
            # and may collide (see decision log) — it is NOT the key.
            'id': f'{leg_type}/{year}/{item_slug}#s{idx}#{h}',
            'item_url': item_url, 'title': title, 'year': year, 'leg_type': leg_type,
            'material_type': material, 'section_index': idx,
            'section_ref': ref, 'heading': heading,
            'text': assembled,                    # FULL assembled block — no truncation
            'n_leaves': len(leaves), 'leaves': leaves,
            'is_in_schedule': material in ('uk_schedule', 'uk_schedule_unnumbered', 'eu_annex'),
            'is_amendment_insertion': in_amend,
            'candidate_cue': cues, 'hints': hints,
            'definitions': _defs_in(assembled, defs),
            'context_quality': quality,
        })

    # Flat fallback — genuinely non-sectioned text (true orphans / irregular tree).
    n_orphan_sents = 0
    orphan_blocks = ([t.get_text(' ', strip=True) for t in orphan_texts]
                     if (sections or orphan_texts) else [soup.get_text(' ', strip=True)])
    for oi, block in enumerate(orphan_blocks):
        for sent in _split(block):
            cues = candidate_cues(sent)
            if not cues:
                continue
            h = hashlib.md5(re.sub(r'\s+', ' ', sent.strip().lower()).encode()).hexdigest()[:12]
            if h in seen_hashes:
                dropped_dups.append({'hash': h, 'text': sent[:160], 'section_index': None})
                continue
            seen_hashes.add(h)
            n_orphan_sents += 1
            records.append({
                'id': f'{leg_type}/{year}/{item_slug}#orphan{oi}#{h}',
                'item_url': item_url, 'title': title, 'year': year, 'leg_type': leg_type,
                'material_type': 'orphan', 'section_index': None,
                'section_ref': '', 'heading': '',
                'text': sent.strip(), 'n_leaves': 0, 'leaves': [],
                'is_in_schedule': False, 'is_amendment_insertion': False,
                'candidate_cue': cues, 'hints': hint_flags(sent),
                'definitions': _defs_in(sent, defs), 'context_quality': 'partial',
            })

    stats = {'item_url': item_url, 'candidates': len(records),
             'definitions': len(defs), 'dropped_duplicates': len(dropped_dups),
             'sections_resolved': dict(resolved), 'orphan_sentences': n_orphan_sents}
    return records, stats, dropped_dups


def run(items, out_jsonl='candidates.jsonl', out_index='candidates_index.csv',
        out_dups='candidates_dropped_dups.jsonl'):
    """items: list of dicts {item_url, title, year, leg_type}. Fetches XML, extracts."""
    all_recs, all_stats, all_dups = [], [], []
    for it in items:
        url = it['item_url'].rstrip('/')
        xml, code = downloader.fetch_xml(f'{url}/data.xml')
        if not xml:
            print(f'  FETCH FAILED ({code}): {url}')
            continue
        recs, stats, dups = extract_from_xml(
            xml, url, it.get('title', ''), it.get('year', ''), it.get('leg_type', ''))
        all_recs += recs
        all_stats.append(stats)
        all_dups += dups
        print(f'  {url}: {stats["candidates"]} candidates, {stats["definitions"]} defs, '
              f'{stats["dropped_duplicates"]} dup-dropped, resolved={stats["sections_resolved"]}')

    with open(out_jsonl, 'w', encoding='utf-8') as f:
        for r in all_recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(out_index, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'item_url', 'material_type', 'section_index', 'section_ref',
                    'heading', 'n_leaves', 'candidate_cue', 'is_in_schedule',
                    'is_amendment_insertion', 'context_quality'])
        for r in all_recs:
            w.writerow([r['id'], r['item_url'], r['material_type'], r['section_index'],
                        r['section_ref'], r['heading'], r['n_leaves'],
                        '|'.join(r['candidate_cue']), int(r['is_in_schedule']),
                        int(r['is_amendment_insertion']), r['context_quality']])
    with open(out_dups, 'w', encoding='utf-8') as f:
        for d in all_dups:
            f.write(json.dumps(d, ensure_ascii=False) + '\n')
    return all_recs, all_stats


if __name__ == '__main__':
    # Seven structurally-diverse Acts (UK primary/secondary/devolved + retained EU
    # regulation + EU decision) — the standing extraction-verification set.
    SAMPLE = [
        {'item_url': 'https://www.legislation.gov.uk/ukpga/2010/23', 'title': 'Bribery Act 2010', 'year': 2010, 'leg_type': 'ukpga'},
        {'item_url': 'https://www.legislation.gov.uk/ukpga/1875/17', 'title': 'Explosives Act 1875', 'year': 1875, 'leg_type': 'ukpga'},
        {'item_url': 'https://www.legislation.gov.uk/uksi/2016/1154', 'title': 'Environmental Permitting (E&W) Regs 2016', 'year': 2016, 'leg_type': 'uksi'},
        {'item_url': 'https://www.legislation.gov.uk/eur/2016/679', 'title': 'UK GDPR', 'year': 2016, 'leg_type': 'eur'},
        {'item_url': 'https://www.legislation.gov.uk/ukpga/1996/18', 'title': 'Employment Rights Act 1996', 'year': 1996, 'leg_type': 'ukpga'},
        {'item_url': 'https://www.legislation.gov.uk/asp/2003/2', 'title': 'Land Reform (Scotland) Act 2003', 'year': 2003, 'leg_type': 'asp'},
        {'item_url': 'https://www.legislation.gov.uk/eudn/2017/1283', 'title': 'Commission Decision 2017/1283 (Apple)', 'year': 2017, 'leg_type': 'eudn'},
    ]
    print('Extracting candidates from 7 verification Acts...')
    recs, stats = run(SAMPLE)
    print(f'\nTotal candidates: {len(recs)}')
