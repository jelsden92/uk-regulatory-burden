"""
analyser.py — Local prescriptive requirement analyser
Usage: python analyser.py --stream <A|B|C>

Zero AI API calls — pure Python + local spaCy only.
"""

import argparse
import hashlib
import logging
import re
import sqlite3
import unicodedata
from datetime import datetime

import nltk
import spacy

from word_list import (
    ACTIVE_COMPLIANCE_MARKERS,
    DEFINITIONAL_PATTERNS,
    IMPLIED_OBLIGATION_WORDS,
    OCR_CORRECTIONS,
    PENALTY_ONLY_TERMS,
    POSITIVE_ID_REQUIRED_TERMS,
    PRESCRIPTIVE_WORDS,
    PRIVATE_ACTOR_SUBJECTS,
    PUBLIC_BODY_SUBJECTS,
    REFERENCE_SCHEDULE_KEYWORDS,
    STRUCTURAL_SUBJECTS,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename='analysis.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
DB_PATH = "legislation.db"

RESULTS_DDL = """
CREATE TABLE IF NOT EXISTS results (
    id                                  INTEGER PRIMARY KEY AUTOINCREMENT,
    legislation_id                      INTEGER UNIQUE,
    item_url                            TEXT,
    title                               TEXT,
    year                                INTEGER,
    legislation_type                    TEXT,
    originating_legislature             TEXT,
    territorial_extent                  TEXT,
    stream                              TEXT,
    main_body_words                     INTEGER,
    prescriptive_schedule_words         INTEGER,
    total_analysed_words                INTEGER,
    reference_schedule_words_excluded   INTEGER,
    total_prescriptive_sentences        INTEGER,
    private_actor_count                 INTEGER,
    private_actor_count_excl_schedules  INTEGER,
    private_actor_count_incl_schedules  INTEGER,
    public_body_count                   INTEGER,
    ambiguous_count                     INTEGER,
    conditional_burden_count            INTEGER,
    regulatory_density_excl_schedules   REAL,
    regulatory_density_incl_schedules   REAL,
    ocr_correction_count                INTEGER,
    lower_confidence                    INTEGER,
    section_subject_inheritance_count   INTEGER,
    implied_burden_count                INTEGER,
    implied_burden_active_count         INTEGER,
    high_confidence_count               INTEGER,
    medium_confidence_count             INTEGER,
    low_confidence_count                INTEGER,
    FOREIGN KEY (legislation_id) REFERENCES legislation(id)
)
"""

SENTENCES_DDL = """
CREATE TABLE IF NOT EXISTS sentences (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    legislation_id          INTEGER,
    sentence_text           TEXT,
    matched_word            TEXT,
    classification          TEXT,
    is_in_schedule          INTEGER,
    sentence_hash           TEXT,
    subject_source          TEXT,
    is_amendment_insertion  INTEGER DEFAULT 0,
    confidence_flag         TEXT,
    FOREIGN KEY (legislation_id) REFERENCES legislation(id)
)
"""

AMBIGUOUS_DDL = """
CREATE TABLE IF NOT EXISTS ambiguous_review (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    legislation_id  INTEGER,
    sentence_text   TEXT,
    matched_word    TEXT,
    is_in_schedule  INTEGER,
    subject_source  TEXT,
    FOREIGN KEY (legislation_id) REFERENCES legislation(id)
)
"""


def init_db(conn):
    conn.execute(RESULTS_DDL)
    conn.execute(SENTENCES_DDL)
    conn.execute(AMBIGUOUS_DDL)
    try:
        conn.execute("ALTER TABLE sentences ADD COLUMN is_amendment_insertion INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # column already exists in existing databases
    try:
        conn.execute("ALTER TABLE results ADD COLUMN conditional_burden_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE results ADD COLUMN implied_burden_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE results ADD COLUMN implied_burden_active_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE sentences ADD COLUMN confidence_flag TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE results ADD COLUMN high_confidence_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE results ADD COLUMN medium_confidence_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE results ADD COLUMN low_confidence_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()


def already_analysed(conn, legislation_id):
    row = conn.execute(
        "SELECT 1 FROM results WHERE legislation_id = ?", (legislation_id,)
    ).fetchone()
    return row is not None

# ---------------------------------------------------------------------------
# Step 1 — OCR correction (pre-1963 text)
# ---------------------------------------------------------------------------
_ocr_pattern = re.compile(
    r'\b(' + '|'.join(re.escape(k) for k in OCR_CORRECTIONS) + r')\b',
    re.IGNORECASE,
)

def apply_ocr_corrections(text):
    count = 0
    def replacer(m):
        nonlocal count
        count += 1
        return OCR_CORRECTIONS.get(m.group(0).lower(), m.group(0))
    corrected = _ocr_pattern.sub(replacer, text)
    return corrected, count

# ---------------------------------------------------------------------------
# Step 2 — Schedule separation (already done in DB; we use the fields)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Preamble stripping
# ---------------------------------------------------------------------------
# UK primary legislation preambles end with "as follows:" before operative
# provisions begin. Stripping this prevents the enacting formula
# ("Be it enacted...as follows:") from merging with section 1 into one giant
# sentence that confuses both prescriptive-word matching and subject detection.
_PREAMBLE_END = re.compile(r'^.{0,2000}?as follows:\s*', re.IGNORECASE | re.DOTALL)

def strip_preamble(text):
    """Remove enacting preamble up to and including 'as follows:' if found within the first 2000 chars."""
    if not text:
        return text
    m = _PREAMBLE_END.match(text)
    return text[m.end():] if m else text

# ---------------------------------------------------------------------------
# Step 3 — Sentence splitting
# ---------------------------------------------------------------------------
# Pre-splitter: em-dash variants (■ U+FFFD/U+25A0, — U+2014, – U+2013) followed
# by a lettered subclause marker ("a ", "b ", "c "...) are converted to ". "
# so NLTK sees a sentence boundary after the parent provision.
# This splits "A person commits an offence if— a the person supplies..."
# into "A person commits an offence if." + "a the person supplies..."
# preserving both the subject ("a person") and the prescriptive word in one sentence.
# U+2012 figure dash, U+2013 en dash, U+2014 em dash,
# U+FFFD replacement char (garbled XML dash), U+25A0 black square.
# String concatenation used so Python processes \uXXXX escapes at parse time.
_LIST_BREAK_CHARS = '‒–—�■'
_LIST_BREAK = re.compile(
    '(?<!\\s)[' + _LIST_BREAK_CHARS + ']\\s+(?=[a-z]\\s)',
    re.UNICODE,
)

def split_sentences(text):
    try:
        text = _LIST_BREAK.sub('. ', text)
        return nltk.sent_tokenize(text)
    except Exception:
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

# ---------------------------------------------------------------------------
# Step 4 — Definitional filtering
# ---------------------------------------------------------------------------
_def_pattern = re.compile(
    '|'.join(re.escape(p) for p in DEFINITIONAL_PATTERNS),
    re.IGNORECASE,
)

def is_definitional(sentence):
    return bool(_def_pattern.search(sentence))

# ---------------------------------------------------------------------------
# Step 5 — Section-level subject persistence
# ---------------------------------------------------------------------------
_section_heading = re.compile(
    r'^\s*(\d+[\.\d]*)\s*[\.\)]?\s*(.{0,100})',
    re.IGNORECASE,
)
_list_item = re.compile(r'^\s*[\(\[]?[a-z]{1,3}[\)\]]\s+', re.IGNORECASE)
# Bare-letter list items produced by _LIST_BREAK converting "—\s+a " → ". a ":
# matches "a to take...", "b as regards...", etc. but not "a person..." (noun not in list)
_bare_list_item = re.compile(
    r'^\s*[a-z]\s+(?:to|as|in|with|by|for|that|where|unless|if|on|from)\b',
    re.IGNORECASE,
)


def extract_subject_from_sentence(sentence_lower):
    """Return (subject_text, source) where source is 'direct' or None.

    Uses first-occurrence position to determine the subject: whichever known
    term appears earliest in the sentence wins.  In English the grammatical
    subject almost always precedes objects and complements, so this correctly
    resolves 'A firm must notify the FCA' (firm at 0 beats FCA at 20) while
    preserving 'The FCA must ensure that a firm...' (FCA at 0 beats firm at 25)
    and clause-opener sentences like 'If the regulator decides... a person must'
    (regulator at 3 beats person at 30).
    """
    best_pos = len(sentence_lower) + 1
    best_subj = None

    for pb in sorted(PUBLIC_BODY_SUBJECTS, key=len, reverse=True):
        idx = sentence_lower.find(pb.lower())
        if 0 <= idx < best_pos:
            best_pos = idx
            best_subj = pb

    for pa in sorted(PRIVATE_ACTOR_SUBJECTS, key=len, reverse=True):
        idx = sentence_lower.find(pa.lower())
        if 0 <= idx < best_pos:
            best_pos = idx
            best_subj = pa

    return (best_subj, 'direct') if best_subj else (None, None)


class SectionSubjectTracker:
    """Carry subject forward through list structures within a section."""

    def __init__(self):
        self.current_subject = None
        self.current_subject_type = None
        self.source = 'ambiguous'
        self.inheritance_count = 0
        self._universal_lead_in = False  # True when subject is "every X" / "any X"

    def update(self, sentence):
        sentence_lower = sentence.lower()

        # New numbered section resets context
        if _section_heading.match(sentence):
            self.current_subject = None
            self.current_subject_type = None
            self.source = 'ambiguous'
            self._universal_lead_in = False

        subject, src = extract_subject_from_sentence(sentence_lower)
        if subject:
            self.current_subject = subject
            self.current_subject_type = self._classify_subject(subject)
            self.source = src or 'direct'
            self._universal_lead_in = bool(
                re.search(r'\b(?:every|any)\b', subject.lower())
            )
            return self.current_subject_type, self.source

        # Carry forward for bracketed list items: (a) text, [a] text
        if _list_item.match(sentence) and self.current_subject:
            self.inheritance_count += 1
            return self.current_subject_type, 'inherited'

        # Carry forward for bare-letter list items (a to..., b as...) that
        # _LIST_BREAK produces when splitting "every X while at work—\na to..."
        if (_bare_list_item.match(sentence) and self.current_subject
                and self._universal_lead_in):
            self.inheritance_count += 1
            return self.current_subject_type, 'inherited'

        # Lookback: short sentence with no new subject
        if len(sentence.split()) < 15 and self.current_subject:
            self.inheritance_count += 1
            return self.current_subject_type, 'lookback'

        return None, 'ambiguous'

    @staticmethod
    def _classify_subject(subject):
        subj_lower = subject.lower()
        for pb in PUBLIC_BODY_SUBJECTS:
            if pb.lower() == subj_lower or pb.lower() in subj_lower:
                return 'public_body'
        return 'private_actor'

# ---------------------------------------------------------------------------
# Step 6 — Prescriptive word matching
# ---------------------------------------------------------------------------
_all_prescriptive = []
for _category, _terms in PRESCRIPTIVE_WORDS.items():
    for _t in _terms:
        _all_prescriptive.append((re.compile(r'\b' + re.escape(_t) + r'\b', re.IGNORECASE), _t))
# PENALTY_ONLY_TERMS participate in the same pool so their longer phrases win
# longest-first matching over embedded terms like 'shall' or 'is to'.
for _t in PENALTY_ONLY_TERMS:
    _all_prescriptive.append((re.compile(r'\b' + re.escape(_t) + r'\b', re.IGNORECASE), _t))

# Sort longest first so multi-word phrases match before single words
_all_prescriptive.sort(key=lambda x: len(x[1]), reverse=True)

# ---------------------------------------------------------------------------
# Hierarchical prescriptive filtering — penalty-only terms
# ---------------------------------------------------------------------------
_PENALTY_ONLY_SET = set(PENALTY_ONLY_TERMS)

# Cross-reference markers: when a PENALTY_ONLY_TERMS match fires and the sentence
# contains one of these markers, it is a pure penalty-quantum clause (specifying
# punishment for an obligation stated elsewhere) → ambiguous/penalty_only.
# Absence of these markers means the penalty clause IS the obligation → normal classification.
_XREF_PENALTY_RE = re.compile(
    r'\b(?:guilty of an offence under|convicted under|in respect of that offence'
    r'|in respect of an offence under|liable under section|punishable under)\b',
    re.IGNORECASE,
)

# Guilt-phrase cross-reference check: 'is guilty of an offence', 'shall be guilty of an
# offence', and 'guilty of an offence if' sentences are standalone primary obligations when
# they state the conduct inline, but are criminal enforcement back-references when they
# reference a prior prohibition via a cross-reference marker.
# Cross-reference present → double-count → penalty_only/ambiguous.
# Cross-reference absent → standalone obligation → normal classification.
_GUILT_OFFENCE_SET = {
    'is guilty of an offence',
    'shall be guilty of an offence',
    'guilty of an offence if',
}

_GUILT_XREF_RE = re.compile(
    r'\b(?:'
    r'in contravention of|'
    r'in breach of (?:this section|this Act|subsection|section)|'
    r'contrary to (?:this section|this Act|subsection|section)|'
    r'a person contravenes|contravenes subsection|contravenes section|'
    r'is so emitted|is so used|'
    r'is used in contravention of'
    r')\b',
    re.IGNORECASE,
)

# Co-present prohibition: when a guilt-phrase sentence also contains a 'shall not'/
# 'must not' prohibition, the sentence is a combined clause (prohibition + enforcement
# in one sentence, e.g. Clean Air Act "shall not be emitted... shall be guilty of an
# offence if so emitted").  The prohibition is the primary match — don't suppress it.
_GUILT_PROHIBITION_RE = re.compile(r'\b(?:shall not|must not|may not)\b', re.IGNORECASE)

# Primary obligation terms used as secondary check when a penalty-only term fires.
# 'is guilty of an offence' is included: it creates the restriction, not just its consequence.
_PRIMARY_OBLIGATION_TERMS = [
    'must not', 'shall not', 'may not',
    'is required to', 'is prohibited',
    'is guilty of an offence',
    'must', 'shall', 'is to', 'are to',
]
_primary_obligation_patterns = [
    (re.compile(r'\b' + re.escape(t) + r'\b', re.IGNORECASE), t)
    for t in _PRIMARY_OBLIGATION_TERMS
]


def _find_primary_obligation(sentence):
    """Return the first PRIMARY_OBLIGATION term found in the sentence, or None."""
    for pattern, term in _primary_obligation_patterns:
        if pattern.search(sentence):
            return term
    return None


# Terms that require positive subject identification — tier-4 default is suppressed.
_POSITIVE_ID_REQUIRED_SET = set(POSITIVE_ID_REQUIRED_TERMS)

# Implied-term prescriptive words that create obligations even when the sentence
# starts with a prepositional phrase ('In a lease there is implied a covenant by
# the landlord').  CLAUSE_OPENER_RE would normally mark these as ambiguous; the
# post-classification override below reverses that for this specific term set.
_IMPLIED_TERM_SET = {
    'there is implied', 'there shall be implied', 'there is to be implied',
    'there is an implied term', 'there is an implied condition', 'there is an implied warranty',
}


# Purpose-clause filter for 'is to' / 'are to':
# these terms trigger on "purpose of which is to", "designed is to", etc.
_PURPOSE_PRECURSORS = re.compile(
    r'\b(?:purposes?|objects?|aims?|designed|intended|in order|so as|whether)\b',
    re.IGNORECASE,
)

def _is_purpose_clause(sentence, match_start):
    """True if 'is to'/'are to' at match_start follows a purpose/intent word within 5 words.
    5 words catches 'purpose of which is to' (gap=3) but not 'In order to ..., X is to'
    where the purpose clause is a separate adverbial and the gap is much larger.
    """
    words = sentence[:match_start].split()
    window = ' '.join(words[-5:])
    return bool(_PURPOSE_PRECURSORS.search(window))


def find_prescriptive_word(sentence):
    """Return first matching prescriptive term or None."""
    for pattern, term in _all_prescriptive:
        m = pattern.search(sentence)
        if m:
            if term in ('is to', 'are to') and _is_purpose_clause(sentence, m.start()):
                continue
            return term
    return None


def find_conditional_burden(sentence):
    """Return 'is to'/'are to' if it fires as a purpose clause (anti-avoidance conditional).
    Called only when find_prescriptive_word returned None."""
    for pattern, term in _all_prescriptive:
        if term not in ('is to', 'are to'):
            continue
        m = pattern.search(sentence)
        if m and _is_purpose_clause(sentence, m.start()):
            return term
    return None

# ---------------------------------------------------------------------------
# Step 6b — Implied burden detection
# ---------------------------------------------------------------------------
# Sentences containing an implied-obligation phrase (burden-of-proof / duty to
# demonstrate) where the subject is a private actor are classified as
# implied_burden.  If the sentence also references an active-compliance
# standard (adequate procedures, due diligence, etc.) the sub-classification
# is implied_burden_active.

_implied_obligation_patterns = [
    (re.compile(r'\b' + re.escape(t) + r'\b', re.IGNORECASE), t)
    for t in sorted(IMPLIED_OBLIGATION_WORDS, key=len, reverse=True)
]

_active_compliance_lower = [m.lower() for m in ACTIVE_COMPLIANCE_MARKERS]


def find_implied_obligation(sentence):
    """Return the first IMPLIED_OBLIGATION_WORDS term found in sentence, or None."""
    for pattern, term in _implied_obligation_patterns:
        if pattern.search(sentence):
            return term
    return None


def _has_active_compliance(sentence_lower):
    """True if sentence contains any ACTIVE_COMPLIANCE_MARKERS term."""
    return any(m in sentence_lower for m in _active_compliance_lower)


# ---------------------------------------------------------------------------
# Step 6c — Defined single-letter variable tracking
# ---------------------------------------------------------------------------
# UK primary legislation frequently defines shorthand variables with notation
# like 'A relevant commercial organisation ("C") is guilty...', then uses the
# bare letter C throughout the section.  When spaCy sees C as an nsubj it fires
# the single-letter → ambiguous rule, which would suppress implied_burden hits.
# We detect the defining sentence and propagate the type to the usage sentences.

_DEF_VAR_RE = re.compile(r'\([“"]([A-Z])[”"]\)')

_PA_DEFVAR_WORDS = {
    'organisation', 'company', 'person', 'employer', 'employee', 'worker',
    'operator', 'contractor', 'individual', 'business', 'firm', 'trader',
    'supplier', 'producer', 'manufacturer', 'retailer', 'provider',
    'importer', 'exporter', 'landlord', 'tenant', 'carrier',
}
_PB_DEFVAR_WORDS = {
    'authority', 'minister', 'secretary', 'commission', 'agency', 'court',
    'tribunal', 'regulator', 'inspector', 'board', 'officer', 'government',
}


# ---------------------------------------------------------------------------
# Step 8 — Subject classification via spaCy
# ---------------------------------------------------------------------------
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load('en_core_web_sm')
    return _nlp


# Strip a leading section/subsection number ("2 ", "3A ", "12.1 ") so that
# "2 The FCA must..." is tested as "The FCA must..." for start-of-sentence checks.
_LEADING_SECTION_NUM = re.compile(r'^(?:\s*\d[\w.\-]*\s+)+')

_CLAUSE_OPENER_RE = re.compile(
    r'^(?:if|where|when|in|for|but|unless|until|references|subject|notwithstanding|whether)\b',
    re.IGNORECASE,
)

_STRUCTURAL_OPENER_RE = re.compile(
    r'^(?:' + '|'.join(re.escape(s) for s in sorted(STRUCTURAL_SUBJECTS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

# GDPR-style recital paragraphs: "(118) The independence..." — preamble text, not operative provisions.
_RECITAL_RE = re.compile(r'^\s*\(\d+\)\s')

def _starts_with_public_body(sentence):
    """True if the sentence opens with a PUBLIC_BODY_SUBJECTS term (after any leading
    section number is stripped).  Checked longest-first to avoid partial matches."""
    s = _LEADING_SECTION_NUM.sub('', sentence).strip().lower()
    for pb in sorted(PUBLIC_BODY_SUBJECTS, key=len, reverse=True):
        if s.startswith(pb.lower()):
            return True
    return False


def classify_subject_spacy(sentence, tracker_result, tracker_source):
    """
    Combine section tracker result with spaCy dependency parse.
    Returns (classification, subject_source, confidence_flag).
    classification: 'private_actor' | 'public_body' | 'ambiguous'
    confidence_flag: 'high' | 'medium' | 'low'
    """
    # Recital paragraphs: "(NNN) Text..." — preamble soft-law, never a binding obligation.
    if _RECITAL_RE.match(sentence):
        return 'ambiguous', 'recital', 'medium'

    # Pre-check: sentence-opening public body term overrides tracker and spaCy.
    if _starts_with_public_body(sentence):
        return 'public_body', 'direct', 'high'

    # Strip leading section number and article once; used by all subsequent checks.
    s_stripped = _LEADING_SECTION_NUM.sub('', sentence).strip()
    s_no_article = re.sub(r'^(?:the|a|an)\s+', '', s_stripped, flags=re.IGNORECASE)

    # Contractual/inanimate nsubj check: runs BEFORE the tracker result so that PA
    # terms appearing as grammatical objects (e.g. 'an occupier' in 'shall not …
    # of making an occupier answerable') cannot override the true grammatical subject.
    # Prefix gate is deliberately narrow ('contract' only) to avoid over-firing on
    # 'term of employment', 'agreement between parties' etc. in other Acts.
    if re.match(r'^contract\b', s_no_article, re.IGNORECASE):
        for _tok in get_nlp()(sentence[:512]):
            if _tok.dep_ in ('nsubj', 'nsubjpass'):
                if _tok.lemma_.lower() in {'contract', 'term', 'provision', 'agreement', 'arrangement'}:
                    return 'ambiguous', 'ambiguous', 'medium'
                break

    if tracker_result in ('private_actor', 'public_body'):
        _trk_conf = 'low' if tracker_source == 'inherited' else (
            'high' if tracker_source == 'direct' else 'medium'
        )
        return tracker_result, tracker_source, _trk_conf

    # Tier 2/3: structural checks run BEFORE first-occurrence competition (Fix 3).
    # A sentence opening with a clause opener ("where", "if", "whether") or a
    # structural noun ("proceedings", "a fine", "subsection") is ambiguous even
    # if a PRIVATE_ACTOR_SUBJECTS term appears later in the sentence body.
    # s_no_article strips a leading article so "a whether X…" → "whether X…" fires.
    if _CLAUSE_OPENER_RE.match(s_stripped) or _CLAUSE_OPENER_RE.match(s_no_article):
        return 'ambiguous', 'ambiguous', 'medium'

    if _STRUCTURAL_OPENER_RE.match(s_no_article):
        return 'ambiguous', 'ambiguous', 'medium'

    # First-occurrence competition: whichever known PUBLIC_BODY or PRIVATE_ACTOR
    # term appears earliest in the sentence wins.
    sentence_lower = sentence.lower()
    best_pos = len(sentence_lower) + 1
    best_cls = None
    for pb in sorted(PUBLIC_BODY_SUBJECTS, key=len, reverse=True):
        idx = sentence_lower.find(pb.lower())
        if 0 <= idx < best_pos:
            best_pos = idx
            best_cls = 'public_body'
    for pa in sorted(PRIVATE_ACTOR_SUBJECTS, key=len, reverse=True):
        idx = sentence_lower.find(pa.lower())
        if 0 <= idx < best_pos:
            best_pos = idx
            best_cls = 'private_actor'
    if best_cls:
        return best_cls, 'direct', 'high'

    # spaCy nominal-subject check (only reached when first-occurrence finds nothing)
    nlp = get_nlp()
    doc = nlp(sentence[:512])
    for token in doc:
        if token.dep_ in ('nsubj', 'nsubjpass'):
            # Single uppercase letter = defined variable (P, R, C, A …) in
            # criminal-offence sub-clauses.  Treat as ambiguous rather than
            # defaulting to private_actor.
            if re.match(r'^[A-Z]$', token.text):
                return 'ambiguous', 'ambiguous', 'medium'
            tok_text = token.text.lower()
            if token.pos_ in ('PRON', 'DET') or len(tok_text) < 3:
                continue
            _spacy_conf = 'high' if len(tok_text) > 3 else 'medium'
            for pb in PUBLIC_BODY_SUBJECTS:
                if pb.lower() in tok_text or tok_text in pb.lower():
                    return 'public_body', 'spacy', _spacy_conf
            for pa in PRIVATE_ACTOR_SUBJECTS:
                if pa.lower() in tok_text or tok_text in pa.lower():
                    return 'private_actor', 'spacy', _spacy_conf

    # Tier 4: no structural reason to withhold — default private_actor.
    # Returns 'tier4_default' (not 'direct') so callers can detect this path
    # and suppress it for POSITIVE_ID_REQUIRED_TERMS.
    return 'private_actor', 'tier4_default', 'medium'

# ---------------------------------------------------------------------------
# Word counting
# ---------------------------------------------------------------------------
def count_words(text):
    if not text:
        return 0
    return len(text.split())

# ---------------------------------------------------------------------------
# Sentence normalisation for deduplication
# ---------------------------------------------------------------------------
# Strips parenthetical territorial markers like (NI), (E+W), (S).
_TERRITORIAL_MARKER = re.compile(
    r'\s*\((?:NI|GB|E\+W(?:\+S)?(?:\+N\.I\.)?|E|W|S|N\.I\.)\)',
    re.IGNORECASE,
)

# Collapses inline "Great Britain" / "Northern Ireland" to a common token so that
# amendment Acts which insert the same text twice — once for SSCBA 1992 (GB) and
# once for SSCB(NI)A 1992 — hash identically and count as one requirement.
_JURISDICTION_VARIANT = re.compile(
    r'\b(?:great britain|northern ireland)\b',
    re.IGNORECASE,
)

# Strips the numeric paragraph number from cross-references like "9(g)" → "(g)".
# The GB and NI versions of the same Act place equivalent provisions at different
# paragraph numbers (e.g. para 9 in SSCBA 1992 vs para 7 in SSCB(NI)A 1992),
# so stripping the number before the letter sub-reference makes them hash equally.
_CROSSREF_NUM = re.compile(r'\b(\d+)(\([a-z]\))', re.IGNORECASE)

def normalise_for_hash(sentence):
    """Normalise for deduplication: NFKC, lowercase, strip territorial markers,
    collapse GB/NI jurisdiction variants, strip paragraph cross-reference numbers,
    collapse whitespace."""
    s = unicodedata.normalize('NFKC', sentence)
    s = s.strip().lower()
    s = _TERRITORIAL_MARKER.sub('', s)
    s = _JURISDICTION_VARIANT.sub('the jurisdiction', s)
    s = _CROSSREF_NUM.sub(r'\2', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# ---------------------------------------------------------------------------
# Main analysis function for one legislation item
# ---------------------------------------------------------------------------
def analyse_item(conn, leg_row, stream):
    leg_id = leg_row['id']
    year = leg_row['year'] or 0
    full_text = leg_row['full_text'] or ''
    prescriptive_sched_text = leg_row['schedule_text_prescriptive'] or ''
    reference_sched_text = leg_row['schedule_text_reference'] or ''

    # Strip enacting preamble so it doesn't merge with section 1 into one giant sentence
    full_text = strip_preamble(full_text)

    # Step 1 — OCR correction for pre-1963
    ocr_count = 0
    lower_confidence = False
    if year and year < 1963:
        full_text, ocr_count = apply_ocr_corrections(full_text)
        prescriptive_sched_text, _ = apply_ocr_corrections(prescriptive_sched_text)
        if ocr_count > 50:
            lower_confidence = True

    # Step 2 — combine main + prescriptive schedule for analysis
    combined_text = full_text
    if prescriptive_sched_text:
        combined_text = full_text + ' ' + prescriptive_sched_text

    main_body_words = count_words(full_text)
    prescriptive_sched_words = count_words(prescriptive_sched_text)
    reference_sched_words = count_words(reference_sched_text)
    total_analysed_words = main_body_words + prescriptive_sched_words

    # Determine which sentences are in schedule
    sched_sentences_set = set(split_sentences(prescriptive_sched_text))

    # Build set of normalised amendment-insertion sentences for tagging
    amendment_text = leg_row.get('amendment_insertion_text') or ''
    amendment_hashes = set()
    if amendment_text:
        for sent in split_sentences(amendment_text):
            norm = normalise_for_hash(sent)
            if norm:
                amendment_hashes.add(norm)

    # Step 3 — sentence splitting
    all_sentences = split_sentences(combined_text)

    # Step 5 — section subject tracker
    tracker = SectionSubjectTracker()

    # Step 7 — deduplication set (keyed on normalised form)
    counted_hashes = set()

    # Accumulators
    total_prescriptive = 0
    private_actor_excl = 0   # excluding schedules
    private_actor_incl = 0   # including schedules
    public_body_count = 0
    ambiguous_count = 0
    conditional_burden_count = 0
    implied_burden_count = 0
    implied_burden_active_count = 0
    high_confidence_count = 0
    medium_confidence_count = 0
    low_confidence_count = 0

    # Defined single-letter variable map {letter: 'private_actor'|'public_body'}
    # Pre-scanned from the full text so that paragraph-number resets (e.g.
    # "2 It is a defence for C to prove...") don't erase definitions set by
    # the preceding paragraph ("1 A relevant commercial organisation ("C")...").
    defined_variables = {}
    for _m in _DEF_VAR_RE.finditer(combined_text):
        _letter = _m.group(1)
        _ctx = combined_text.lower()[:_m.start()][-100:]
        if any(_w in _ctx for _w in _PA_DEFVAR_WORDS):
            defined_variables[_letter] = 'private_actor'
        elif any(_w in _ctx for _w in _PB_DEFVAR_WORDS):
            defined_variables[_letter] = 'public_body'

    sentence_rows = []
    ambiguous_rows = []

    for sentence in all_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        is_in_schedule = sentence in sched_sentences_set

        # Step 4 — skip definitional
        if is_definitional(sentence):
            continue

        # Step 6 — prescriptive word match
        matched_word = find_prescriptive_word(sentence)
        is_conditional = False
        is_implied = False
        is_penalty_only = False
        if matched_word:
            # Hierarchical filter: when a PENALTY_ONLY_TERMS match fires:
            #   1. Co-present primary obligation (must/shall/…) → use it, classify normally.
            #   2. Cross-reference marker (guilty of an offence under / convicted under / …)
            #      → pure penalty-quantum clause → penalty_only/ambiguous.
            #   3. Neither → penalty IS the obligation (e.g. Victorian 'shall be liable') →
            #      fall through to normal subject classification.
            if matched_word in _PENALTY_ONLY_SET:
                # Strip all penalty-only phrases before checking for co-present primary
                # obligations, so that 'shall' embedded inside 'shall be liable to' does
                # not falsely satisfy the check.
                _stripped_for_primary = sentence
                for _pot in PENALTY_ONLY_TERMS:
                    _stripped_for_primary = re.sub(
                        r'\b' + re.escape(_pot) + r'\b', '',
                        _stripped_for_primary, flags=re.IGNORECASE
                    )
                primary = _find_primary_obligation(_stripped_for_primary)
                if primary:
                    matched_word = primary
                elif _XREF_PENALTY_RE.search(sentence):
                    is_penalty_only = True
                # else: no cross-reference → penalty IS the obligation → normal classification
            # Guilt-phrase cross-reference check: when the matched word is an offence-
            # creation phrase, classify as penalty_only if a cross-reference marker is
            # present (the sentence is a criminal enforcement clause for a prior prohibition).
            # Exception: if the sentence also contains a co-present prohibition ('shall not'/
            # 'must not'), it is a combined clause with the prohibition embedded — keep as PA.
            # No cross-reference → standalone obligation → normal classification.
            if not is_penalty_only and matched_word in _GUILT_OFFENCE_SET:
                if _GUILT_XREF_RE.search(sentence):
                    if not _GUILT_PROHIBITION_RE.search(sentence):
                        is_penalty_only = True
            # If matched_word is a generic prescriptive term and an implied obligation
            # term is present, route to the IB path. This catches 'it shall be a
            # defence to show' before it reaches the normal classification path.
            if not is_penalty_only and matched_word in ('shall', 'is to'):
                _iob = find_implied_obligation(sentence)
                if _iob:
                    matched_word = _iob
                    is_implied = True
        else:
            matched_word = find_conditional_burden(sentence)
            if matched_word:
                is_conditional = True
            else:
                # Step 6b — implied burden (burden-of-proof / demonstrate)
                matched_word = find_implied_obligation(sentence)
                if matched_word:
                    is_implied = True
                else:
                    continue

        # Step 7 — deduplication on normalised form (catches territorial variants)
        norm = normalise_for_hash(sentence)
        sent_hash = hashlib.md5(norm.encode('utf-8')).hexdigest()
        if sent_hash in counted_hashes:
            continue
        counted_hashes.add(sent_hash)

        # Amendment insertion detection
        is_amendment = norm in amendment_hashes

        if is_penalty_only:
            classification = 'ambiguous'
            subject_source = 'penalty_only'
            confidence_flag = 'medium'
        elif is_conditional:
            # Anti-avoidance conditional — classify without subject detection
            classification = 'conditional_burden'
            subject_source = 'conditional'
            confidence_flag = 'high'
            conditional_burden_count += 1
        elif is_implied:
            # Implied burden — only counts when subject is a private actor
            tracker_type, tracker_source = tracker.update(sentence)
            classification, subject_source, confidence_flag = classify_subject_spacy(
                sentence, tracker_type, tracker_source
            )
            # If ambiguous due to single-letter defined variable, look up its type
            if classification == 'ambiguous' and defined_variables:
                for _lm in re.finditer(r'\b([A-Z])\b', sentence):
                    if defined_variables.get(_lm.group(1)) == 'private_actor':
                        classification = 'private_actor'
                        subject_source = 'defined_variable'
                        confidence_flag = 'high'
                        break
            if classification != 'private_actor':
                continue  # public body / ambiguous implied obligations not counted
            if _has_active_compliance(sentence.lower()):
                classification = 'implied_burden_active'
                implied_burden_active_count += 1
            else:
                classification = 'implied_burden'
            implied_burden_count += 1
        else:
            # Step 5 — subject tracking
            tracker_type, tracker_source = tracker.update(sentence)

            # Step 8 — spaCy classification
            classification, subject_source, confidence_flag = classify_subject_spacy(
                sentence, tracker_type, tracker_source
            )

            # Implied-term override: 'In a lease there is implied a covenant by the
            # landlord' starts with 'In' so CLAUSE_OPENER_RE marks it ambiguous, but
            # these formulations are always obligation-creating, never definitional.
            # Override ambiguous→private_actor when matched via an implied-term word.
            if (matched_word in _IMPLIED_TERM_SET
                    and classification == 'ambiguous'
                    and subject_source == 'ambiguous'):
                classification = 'private_actor'
                subject_source = 'implied_term'
                confidence_flag = 'high'

            # Positive-ID gate: for terms in POSITIVE_ID_REQUIRED_TERMS, suppress the
            # tier-4 default private_actor classification.  If subject detection did not
            # positively identify a private actor (via first-occurrence string match or
            # spaCy nsubj), treat as ambiguous to avoid silently absorbing public-body
            # duty provisions where subject detection happens to fail.
            if (matched_word in _POSITIVE_ID_REQUIRED_SET
                    and classification == 'private_actor'
                    and subject_source == 'tier4_default'):
                classification = 'ambiguous'
                subject_source = 'positive_id_required'
                confidence_flag = 'medium'

        total_prescriptive += 1

        if confidence_flag == 'high':
            high_confidence_count += 1
        elif confidence_flag == 'low':
            low_confidence_count += 1
        else:
            medium_confidence_count += 1

        sentence_rows.append({
            'legislation_id': leg_id,
            'sentence_text': sentence[:2000],
            'matched_word': matched_word,
            'classification': classification,
            'is_in_schedule': int(is_in_schedule),
            'sentence_hash': sent_hash,
            'subject_source': subject_source,
            'is_amendment_insertion': int(is_amendment),
            'confidence_flag': confidence_flag,
        })

        if classification == 'private_actor':
            private_actor_incl += 1
            if not is_in_schedule:
                private_actor_excl += 1
        elif classification == 'public_body':
            public_body_count += 1
        elif classification in ('conditional_burden', 'implied_burden', 'implied_burden_active'):
            pass  # counted in their own accumulators above
        else:
            ambiguous_count += 1
            ambiguous_rows.append({
                'legislation_id': leg_id,
                'sentence_text': sentence[:2000],
                'matched_word': matched_word,
                'is_in_schedule': int(is_in_schedule),
                'subject_source': subject_source,
            })

    # Density = private_actor per 1000 words
    density_excl = (
        (private_actor_excl / main_body_words * 1000)
        if main_body_words > 0 else 0.0
    )
    density_incl = (
        (private_actor_incl / total_analysed_words * 1000)
        if total_analysed_words > 0 else 0.0
    )

    # Step 10 — save results
    conn.execute("""
        INSERT OR REPLACE INTO results (
            legislation_id, item_url, title, year, legislation_type,
            originating_legislature, territorial_extent, stream,
            main_body_words, prescriptive_schedule_words,
            total_analysed_words, reference_schedule_words_excluded,
            total_prescriptive_sentences,
            private_actor_count,
            private_actor_count_excl_schedules,
            private_actor_count_incl_schedules,
            public_body_count, ambiguous_count, conditional_burden_count,
            regulatory_density_excl_schedules,
            regulatory_density_incl_schedules,
            ocr_correction_count, lower_confidence,
            section_subject_inheritance_count,
            implied_burden_count, implied_burden_active_count,
            high_confidence_count, medium_confidence_count, low_confidence_count
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        leg_id, leg_row['item_url'], leg_row['title'], leg_row['year'],
        leg_row['legislation_type'], leg_row['originating_legislature'],
        leg_row['territorial_extent'], stream,
        main_body_words, prescriptive_sched_words,
        total_analysed_words, reference_sched_words,
        total_prescriptive,
        private_actor_incl,        # private_actor_count = incl (overall)
        private_actor_excl,
        private_actor_incl,
        public_body_count, ambiguous_count, conditional_burden_count,
        round(density_excl, 4), round(density_incl, 4),
        ocr_count, int(lower_confidence),
        tracker.inheritance_count,
        implied_burden_count, implied_burden_active_count,
        high_confidence_count, medium_confidence_count, low_confidence_count,
    ))

    # Clear prior sentences so re-runs don't accumulate stale rows
    conn.execute("DELETE FROM sentences WHERE legislation_id = ?", (leg_id,))
    conn.execute("DELETE FROM ambiguous_review WHERE legislation_id = ?", (leg_id,))

    # Step 11 — save sentences
    conn.executemany("""
        INSERT INTO sentences (
            legislation_id, sentence_text, matched_word, classification,
            is_in_schedule, sentence_hash, subject_source, is_amendment_insertion,
            confidence_flag
        ) VALUES (:legislation_id, :sentence_text, :matched_word, :classification,
                  :is_in_schedule, :sentence_hash, :subject_source, :is_amendment_insertion,
                  :confidence_flag)
    """, sentence_rows)

    # Step 12 — save ambiguous
    conn.executemany("""
        INSERT INTO ambiguous_review (
            legislation_id, sentence_text, matched_word,
            is_in_schedule, subject_source
        ) VALUES (:legislation_id, :sentence_text, :matched_word,
                  :is_in_schedule, :subject_source)
    """, ambiguous_rows)

    conn.commit()

    return {
        'private_actor_excl': private_actor_excl,
        'private_actor_incl': private_actor_incl,
        'public_body': public_body_count,
        'ambiguous': ambiguous_count,
        'density_excl': density_excl,
        'implied_burden': implied_burden_count,
        'implied_burden_active': implied_burden_active_count,
        'high_confidence': high_confidence_count,
        'medium_confidence': medium_confidence_count,
        'low_confidence': low_confidence_count,
    }

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stream', required=True, choices=['A', 'B', 'C'])
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    init_db(conn)

    rows = conn.execute(
        "SELECT * FROM legislation WHERE stream = ?", (args.stream,)
    ).fetchall()

    total = len(rows)
    print(f"Analysing {total} items for stream {args.stream}")

    done = 0
    skipped = 0
    errors = 0

    for row in rows:
        done += 1
        leg_id = row['id']

        if already_analysed(conn, leg_id):
            skipped += 1
            if done % 100 == 0:
                print(f"  {done}/{total} (skipped={skipped})")
            continue

        try:
            analyse_item(conn, dict(row), args.stream)
        except Exception as e:
            errors += 1
            logging.error(f"Error analysing {row['item_url']}: {e}")

        if done % 100 == 0 or done == total:
            pct = 100 * done / total
            print(
                f"  {done}/{total} ({pct:.1f}%) | "
                f"skipped={skipped} errors={errors}"
            )
            logging.info(f"Analysis progress {done}/{total} errors={errors}")

    conn.close()
    print(f"\nDone. Total={total} Skipped={skipped} Errors={errors}")


if __name__ == '__main__':
    main()
