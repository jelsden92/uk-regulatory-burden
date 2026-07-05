PRESCRIPTIVE_WORDS = {
    'obligations': [
        'shall', 'must', 'is required to', 'are required to',
        'is to', 'are to',
        'has a duty to', 'have a duty to', 'it is the duty of',
        'it shall be the duty of', 'is under a duty to',
        'is obliged to', 'are obliged to', 'it is mandatory',
        'must ensure', 'must comply with', 'must notify',
        'must inform', 'must report', 'must obtain',
        'must apply for', 'must keep', 'must maintain', 'must retain',
        'shall ensure', 'take reasonable care', 'to take reasonable care',
        'has the right to be given', 'have the right to be given',
        'has the right not to be subjected', 'have the right not to be subjected',
        'has the right not to be dismissed', 'have the right not to be dismissed',
        'has the right not to be treated',
        'owes a duty', 'owe a duty', 'owes the same duty',
        'there shall be implied', 'there is to be implied', 'there is implied',
        'there is an implied condition', 'there is an implied warranty', 'there is an implied term',
        'it is an implied term',
        'is under an obligation to', 'are under an obligation to',
        'is subject to a duty',
        'shall take all practicable steps', 'shall take all reasonably practicable',
        'shall disclose', 'shall declare',
    ],
    'prohibitions': [
        'must not', 'shall not', 'may not',
        'is prohibited', 'are prohibited',
        'is forbidden', 'are forbidden',
        'it is an offence to', 'it shall be an offence to',
        'commits an offence if',
        'is guilty of an offence', 'shall be guilty of an offence', 'guilty of an offence if',
        'it is unlawful to', 'it shall be unlawful',
        'shall not be lawful',
        'no person shall', 'no person may',
        'is not permitted to', 'are not permitted to',
        'is restricted from', 'are restricted from',
        'it is illegal to',
        'cannot',
        'shall be guilty of a misdemeanour', 'shall be guilty of a felony',
    ]
}

# Penalty-consequence terms that match PRESCRIPTIVE_WORDS but describe outcomes, not obligations.
# When one of these is the only prescriptive match, a secondary check for a PRIMARY_OBLIGATION
# term is performed; if none found, the sentence is classified ambiguous/penalty_only.
PENALTY_ONLY_TERMS = [
    'shall be liable to',
    'is liable to',
    'are liable to',
    'shall each be liable',
    'shall be recoverable',
]

# Terms that require POSITIVE subject identification — the tier-4 default private_actor
# classification is suppressed for these.  A sentence matching one of these terms is
# classified ambiguous unless the subject is positively identified as a private actor
# via first-occurrence string match or spaCy nsubj detection.
# Rationale: 'owes a duty' sentences include public-body duty provisions; if subject
# detection fails we must not silently absorb them as private-actor obligations.
POSITIVE_ID_REQUIRED_TERMS = {
    'owes a duty',
    'owe a duty',
    'owes the same duty',
}

PUBLIC_BODY_SUBJECTS = [
    'Secretary of State', 'the Minister', 'a Minister', 'the Crown',
    'local authority', 'public authority', 'the council', 'the court',
    'the tribunal', 'the magistrate', 'the regulator', 'the Board',
    'a sheriff', 'the sheriff',
    'the Commission', 'the Agency', 'the Authority', 'the Director',
    'the Inspector', 'Welsh Ministers', 'the Welsh Ministers', 'Scottish Ministers',
    'the Scottish Ministers', 'a Scottish Minister', 'the First Minister', 'the Presiding Officer',
    'the Presiding Officer of the Senedd', 'a member of the Scottish Parliament', 'a member of the Senedd',
    'a member of the Welsh Government', 'an Assembly member',
    'the Senedd', 'the Scottish Parliament', 'the Northern Ireland Assembly',
    'the Treasury', 'HM Treasury', 'HMRC', 'Member States',
    'a Member State', 'the Member State', 'the Bank of England', 'the FCA',
    'the PRA', 'the CMA', 'the Environment Agency', 'the Health and Safety Executive',
    'the Office for', 'the National Health Service', 'a fire and rescue authority', 'a police authority',
    'a planning authority', 'Scottish Natural Heritage', 'Natural Resources Wales', 'Historic Environment Scotland',
    'the appropriate regulator', 'the appropriate authority', 'the relevant regulator', 'the relevant authority',
    'the Cabinet Office', 'the Home Office', 'the Foreign Office', 'the Foreign, Commonwealth and Development Office',
    'the Ministry of Defence', 'the Ministry of Justice', 'the Department for Transport', 'the Department of Health',
    'the Department for Health and Social Care', 'the Department for Education', 'the Department for Work and Pensions', 'the Department for Business',
    'the Department for Energy Security', 'the Department for Environment', 'MHCLG', 'HM Revenue and Customs',
    'HM Revenue & Customs', 'the Driver and Vehicle Licensing Agency', 'the DVLA', 'the Driver and Vehicle Standards Agency',
    'the DVSA', 'the Land Registry', 'HM Land Registry', 'the Insolvency Service',
    'the Planning Inspectorate', 'the Highways Agency', 'National Highways', 'the Medicines and Healthcare products Regulatory Agency',
    'the MHRA', 'the Intellectual Property Office', 'Companies House', 'the Met Office',
    'the National Archives', 'the Valuation Office Agency', 'the Vehicle Certification Agency', 'the Rural Payments Agency',
    'the Animal and Plant Health Agency', 'the Food and Environment Research Agency', 'the Health and Safety Laboratory', 'the Veterinary Medicines Directorate',
    'the Gangmasters and Labour Abuse Authority', 'the GLAA', 'the HSE', 'the Financial Conduct Authority',
    'the Prudential Regulation Authority', 'the Competition and Markets Authority', 'the Payment Systems Regulator', 'the Financial Ombudsman Service',
    'the Financial Services Compensation Scheme', 'the FSCS', 'the Pension Protection Fund', 'the Pensions Regulator',
    'the Pensions Ombudsman', 'the Information Commissioner', "the Information Commissioner's Office", 'the ICO',
    'the Office of Rail and Road', 'the ORR', 'the Civil Aviation Authority', 'the CAA',
    'the Office of Gas and Electricity Markets', 'Ofgem', 'the Water Services Regulation Authority', 'Ofwat',
    'the Office of Communications', 'Ofcom', 'the Nuclear Decommissioning Authority', 'the Office for Nuclear Regulation',
    'the ONR', 'the Food Standards Agency', 'the FSA', 'the Food Standards Scotland',
    'Natural England', 'the Joint Nature Conservation Committee', 'the JNCC', 'the Marine Management Organisation',
    'the Forestry Commission', 'the Coal Authority', 'the Oil and Gas Authority', 'the North Sea Transition Authority',
    'the Health Research Authority', 'the Care Quality Commission', 'the CQC', 'the Human Fertilisation and Embryology Authority',
    'the HFEA', 'the Human Tissue Authority', 'NHS England', 'NHS Improvement',
    'NHS Resolution', 'NHS Blood and Transplant', 'the National Institute for Health and Care Excellence', 'NICE',
    'the National Institute for Health Research', 'Public Health England', 'the UK Health Security Agency', 'the UKHSA',
    'the Charity Commission', 'the Charity Commission for England and Wales', 'the Office for Students', 'the Higher Education Funding Council',
    'HEFCE', 'the Research Councils UK', 'UK Research and Innovation', 'UKRI',
    'the Arts Council', 'Sport England', 'UK Sport', 'the British Film Institute',
    'the Heritage Lottery Fund', 'the National Lottery Community Fund', 'Historic England', 'Cadw',
    'the Crown Estate', 'the Crown Estate Commissioners', 'the Boundary Commission', 'the Electoral Commission',
    'the Committee on Standards in Public Life', 'the Advisory Committee on Business Appointments', 'the Independent Parliamentary Standards Authority', 'the IPSA',
    'the National Audit Office', 'the NAO', 'the Comptroller and Auditor General', 'the National Infrastructure Commission',
    'the Infrastructure and Projects Authority', 'the Office for Budget Responsibility', 'the OBR', 'the UK Statistics Authority',
    'the Office for National Statistics', 'the ONS', 'the Office for Environmental Protection', 'the OEP',
    'the Committee on Climate Change', 'the Climate Change Committee', 'the CCC', 'the Low Pay Commission',
    'the Migration Advisory Committee', 'the Gangmasters Licensing Authority', 'the Equality and Human Rights Commission', 'the EHRC',
    'the Independent Office for Police Conduct', 'the IOPC', 'the Independent Police Complaints Commission', 'the IPCC',
    'the Crown Prosecution Service', 'the CPS', 'the Serious Fraud Office', 'the SFO',
    'the National Crime Agency', 'the NCA', 'the Security Industry Authority', 'the SIA',
    'the Gambling Commission', 'the Homes England', 'the Housing Ombudsman', 'the Property Ombudsman',
    'the Trade Remedies Authority', 'the TRA', 'the Competition Appeal Tribunal', 'the CAT',
    'the Financial List', 'the Takeover Panel', 'the Takeover Appeal Board', 'the Listing Authority',
    'the UK Listing Authority', 'the Advertising Standards Authority', 'the ASA', 'the Payments Council',
    'the Open Banking Implementation Entity', 'the Financial Policy Committee', 'the Monetary Policy Committee', 'the Prudential Regulation Committee',
    'the Financial Stability Board', 'the Scottish Environment Protection Agency', 'SEPA', 'NatureScot',
    'Natural Resources Body for Wales', 'the Supreme Court', 'the Court of Appeal', 'the High Court',
    'the Crown Court', 'the County Court', 'the Magistrates Court', "His Majesty's Courts",
    "Her Majesty's Courts", 'the Employment Tribunal', 'the Employment Appeal Tribunal', 'the Upper Tribunal',
    'the First-tier Tribunal', 'the Lands Tribunal', 'the Financial Services Tribunal', 'the Investigatory Powers Tribunal',
    'the Special Immigration Appeals Commission', 'the Parole Board', 'the Mental Health Review Tribunal', 'the Asylum and Immigration Tribunal',
    'the Information Tribunal', 'the Tax Tribunal', 'the Land Registration Adjudicator', 'the Adjudicator',
    'the Arbitral Tribunal', 'a court', 'a tribunal', 'the Scottish Government',
    'Audit Scotland', 'Accounts Commission', 'Healthcare Improvement Scotland', 'Social Care and Social Work Improvement Scotland',
    'Scottish Social Services Council', 'Standards in Scotland', 'the Care Inspectorate', 'Education Scotland',
    "Her Majesty's Inspectors of Education", 'HM Inspectorate of Education', 'Scottish Qualifications Authority', 'the SQA',
    'Skills Development Scotland', 'Scottish Enterprise', 'Highlands and Islands Enterprise', 'South of Scotland Enterprise',
    'Scottish Funding Council', 'Transport Scotland', 'Scottish Water', 'the Water Industry Commission for Scotland',
    'Homes for Scotland', 'the Scottish Housing Regulator', 'Crown Office and Procurator Fiscal Service', 'the Lord Advocate',
    'the Procurator Fiscal', 'the Keeper of the Registers of Scotland', 'Registers of Scotland', 'the Assessors',
    'the Crofting Commission', 'Bòrd na Gàidhlig', 'Visit Scotland', 'Creative Scotland',
    'sportscotland', 'the Welsh Government', 'the Senedd Cymru', 'Audit Wales',
    'Healthcare Inspectorate Wales', 'Care Inspectorate Wales', 'Estyn', 'Historic Wales',
    'Sport Wales', 'Arts Council of Wales', 'National Library of Wales', 'National Museum Wales',
    'Qualifications Wales', 'Transport for Wales', 'the Higher Education Funding Council for Wales', 'the Welsh Revenue Authority',
    'Tai Cymru', 'Community Housing Cymru', 'the Northern Ireland Executive', 'Northern Ireland Ministers',
    'the Northern Ireland Audit Office', 'the Comptroller and Auditor General for Northern Ireland', 'the NI Audit Office', 'the Education Authority',
    'the Public Health Agency', 'the Health and Social Care Board', 'the Patient and Client Council', 'the Regulation and Quality Improvement Authority',
    'Invest Northern Ireland', 'Tourism Ireland', 'the Northern Ireland Housing Executive', 'the Police Service of Northern Ireland',
    'the PSNI', 'the Police Ombudsman for Northern Ireland', 'the Northern Ireland Ombudsman', 'the Electoral Office for Northern Ireland',
    'the Boundary Commission for Northern Ireland', 'the Equality Commission for Northern Ireland', 'the Human Rights Commission', 'the Northern Ireland Human Rights Commission',
    'the Utility Regulator', 'the Consumer Council for Northern Ireland', 'the Northern Ireland Environment Agency', 'Her Majesty',
    'His Majesty', 'the Privy Council', 'the Privy Councillor', 'Parliament',
    'the Houses of Parliament', 'the House of Commons', 'the House of Lords', 'a Select Committee',
    'the Speaker', 'the Lord Chancellor', 'the Secretary of State', 'the Ministers',
    'the Lord Privy Seal', 'the Solicitor General', 'the Attorney General', 'the Advocate General',
    'the Registrar General', 'the Registrar of Companies', 'the Keeper of Public Records', 'the Chief Land Registrar',
    'the Official Receiver', 'the Official Custodian', 'the Public Trustee', 'the Chief Coroner',
    'the Returning Officer', 'the Counting Officer', 'the Electoral Registration Officer', 'the Law Commission',
    'the Scottish Law Commission', 'the Boundary Commission for England', 'the Boundary Commission for Scotland', 'the Boundary Commission for Wales',
    'the Independent Review Body', 'the Advisory Conciliation and Arbitration Service', 'ACAS', 'the Central Arbitration Committee',
    'the CAC', 'a constable', 'a police constable', 'the chief constable',
    'a chief constable', 'the Commissioner of Police', 'the Commissioner of the Metropolitan Police', 'the police',
    'a police officer', 'an authorised officer', 'the authorised officer', 'an inspector', 'an enforcement officer',
    'the enforcement authority', 'an enforcement authority', 'the enforcement authorities',
    'a food analyst', 'a food examiner', 'an examiner',
    'a trading standards officer', 'a customs officer', 'an immigration officer', 'a clinical commissioning group',
    'an NHS trust', 'an NHS foundation trust', 'the NHS', 'a health authority',
    'a primary care trust', 'a strategic health authority', 'a local authority', 'a local planning authority',
    'a highway authority', 'a housing authority', 'a billing authority', 'a precepting authority',
    'a levying body', 'a waste disposal authority', 'a waste collection authority', 'a county council',
    'a district council', 'a borough council', 'a unitary authority', 'a metropolitan council',
    'a parish council', 'a community council', 'a town council', 'a combined authority',
    'a mayoral combined authority', 'the Greater London Authority', 'the GLA', 'Transport for London',
    'TfL', 'the supervisory authority', 'a supervisory authority', 'the competent authority',
    'a competent authority', 'the lead regulator', 'the General Medical Council', 'the GMC',
    'the Nursing and Midwifery Council', 'the NMC', 'the General Dental Council', 'the GDC',
    'the General Pharmaceutical Council', 'the GPhC', 'the General Optical Council', 'the General Osteopathic Council',
    'the General Chiropractic Council', 'the Health and Care Professions Council', 'the HCPC', 'the Solicitors Regulation Authority',
    'the SRA', 'the Bar Standards Board', 'the BSB', 'the Legal Services Board',
    'the Council for Licensed Conveyancers', 'the CLC', 'the Intellectual Property Regulation Board', 'CILEx Regulation',
    'the Costs Lawyer Standards Board', 'the Master of the Faculties', 'the Office for Standards in Education', 'Ofsted',
    'the Office of Qualifications and Examinations Regulation', 'Ofqual', 'Social Work England', 'the Teaching Regulation Agency',
    'the Financial Reporting Council', 'the FRC', 'the Institute of Chartered Accountants in England and Wales', 'the ICAEW',
    'the Institute of Chartered Accountants of Scotland', 'the ICAS', 'the Association of Chartered Certified Accountants', 'the ACCA',
    'the Building Safety Regulator', 'the BSR', 'the Architects Registration Board', 'the ARB',
    'the Regulator of Social Housing', 'the British Board of Film Classification', 'the BBFC', 'the Games Rating Authority',
    'the Independent Football Regulator', 'the Sports Grounds Safety Authority', 'the SGSA', 'the Maritime and Coastguard Agency',
    'the MCA', 'the Traffic Commissioners', 'a Traffic Commissioner', 'the Traffic Commissioner',
    'the Disclosure and Barring Service', 'the DBS', 'the Forensic Science Regulator', 'the Groceries Code Adjudicator',
    'the Pubs Code Adjudicator', 'the Civil Service Commission', 'the Commissioner for Public Appointments', 'the Immigration Advice Authority',
    'the Immigration Services Commissioner', 'the Defence Safety Authority', 'the Drinking Water Inspectorate', 'the Office for Product Safety and Standards',
    'the Employment Agency Standards Inspectorate', 'the Animals in Science Regulation Unit', 'the Offshore Petroleum Regulator', 'the Adjudicator for HM Revenue and Customs',
    'an authority',
    'the Judicial Appointments Commission', 'the Legal Ombudsman', 'the Financial Ombudsman', 'the Parliamentary and Health Service Ombudsman',
    'the Local Government Ombudsman', 'the Energy Ombudsman', 'the Health and Safety Executive for Northern Ireland', 'the HSENI',
    'the NIEA', 'Building Control Northern Ireland', 'the Charity Commission for Northern Ireland', 'the Driver and Vehicle Agency Northern Ireland',
    'the DVA', 'the Northern Ireland Social Care Council', 'the General Teaching Council for Northern Ireland', 'the Pharmaceutical Society of Northern Ireland',
    'the Law Society of Northern Ireland', 'the Northern Ireland Practise and Education Council', 'the Parades Commission', 'the Rail Safety Authority',
    'the Public Services Ombudsman for Northern Ireland', 'the Office of the Scottish Charity Regulator', 'the OSCR', 'the Accountant in Bankruptcy',
    'the AiB', 'the Faculty of Advocates', 'the Law Society of Scotland', 'the General Teaching Council for Scotland',
    'the Drinking Water Quality Regulator for Scotland', 'the DWQR', 'the Scottish Biometrics Commissioner', 'the Scottish Information Commissioner',
    'the Scottish Human Rights Commission', 'Social Care Wales', 'Medr', 'the Agricultural Land Tribunal',
    'the Public Services Ombudsman for Wales', 'the Welsh Language Commissioner', 'the Future Generations Commissioner for Wales',
]

PRIVATE_ACTOR_SUBJECTS = [
    'a person', 'any person', 'an employer', 'an employee',
    'every employer', 'every employee',
    'a worker', 'the worker', 'every worker',
    'an operator', 'an occupier', 'a company', 'a business',
    'a contractor', 'an individual', 'a licensee', 'a trader',
    'an owner', 'a supplier', 'a producer', 'a manufacturer',
    'a retailer', 'a provider', 'an importer', 'an exporter',
    'a landlord', 'a tenant', 'a driver', 'a carrier',
    'a financial institution', 'a credit institution',
    'an authorised person', 'a PRA-authorised person', 'a firm', 'an approved person',
    'the controller', 'a controller', 'the processor', 'a processor',
    'the data controller', 'a data controller', 'the data processor', 'a data processor',
    'joint controllers', 'the joint controllers',
    'an economic operator', 'economic operators', 'the economic operator',
    'an undertaking', 'the undertaking', 'undertakings',
    'a distributor', 'the distributor',
    'a fulfilment service provider', 'an authorised representative',
    'economic operator', 'market operator',
    'a registered person', 'a certified person',
    'the directors', 'every director', 'the secretary',
    'the parties',
]

OCR_CORRECTIONS = {
    'shali': 'shall', 'sball': 'shall', 'sliall': 'shall',
    'niust': 'must', 'rniist': 'must', 'rnust': 'must',
    'rnay': 'may', 'inay': 'may',
    'liave': 'have', 'bave': 'have',
    'dutv': 'duty', 'oflence': 'offence', 'oftence': 'offence'
}

DEFINITIONAL_PATTERNS = [
    'means ', 'includes ',
    # Narrow scope: 'for the purposes of this Act/section/subsection' is definitional;
    # 'for the purposes of criminal conduct / tax avoidance' is substantive and must not be filtered.
    'for the purposes of this',
    'for the purposes of section',
    'for the purposes of subsection',
    'is to be construed', 'are to be construed', 'is to have effect', 'is to be read', 'shall be deemed',
    'shall be construed', 'shall not be construed as', 'shall have effect',
    'shall cease to have effect', 'cease to have effect', 'shall no longer have effect',
    'shall come into force', 'shall apply',
    # Scope clarifications (not obligations): e.g. Bribery Act s.1(4)
    'it does not matter whether',
    # Structural provisions about an Act's own legal effect: e.g. OLA 1957 s.1(2)-(3)
    'rules so enacted', 'rules enacted',
    # Cross-reference labels: 'the X which is required to be prepared under para Z is referred to as...'
    'which is required to be',
    # Evidentiary presumptions (conduct standard borderline cases handled at caller level)
    'is to be presumed', 'is to be taken as',
    # Bribery Act-style numbered case definitions: "Case 1 is where..."
    'case 1 is where', 'case 2 is where', 'case 3 is where',
    'case 4 is where', 'case 5 is where', 'case 6 is where',
    # Cross-references to those definitions: "In cases 1, 3 and 4..."
    'in cases 1', 'in cases 3', 'in cases 4',
    # Disregard clauses — structural/scope, not obligations
    'is to be disregarded', 'are to be disregarded', 'shall be disregarded',
    # Treatment clauses — structural redirects, not new obligations
    'is to be treated as', 'are to be treated as',
    # Payment direction clauses — administrative mechanics, not private-actor duties
    'is to be paid', 'are to be paid',
    # Limitation/non-imposition clauses — structural qualifications, not new obligations (e.g. OLA 1957 s.1)
    'does not impose', 'shall not impose',
    'nothing in this section imposes', 'does not require a person',
    # Void/no-effect clauses — describe legal status of a term, not a duty on an actor (e.g. UCTA 1977)
    'shall be void', 'shall be of no effect', 'shall have no effect',
    'is void', 'is of no effect',
    # Soft-law recital formulations (GDPR) — "should in principle" marks a recommendation, not a binding duty
    'should in principle',
    # Impossibility conditions — "cannot be fulfilled" states a logical condition, not an obligation
    'cannot be fulfilled',
    # Jurisdictional extension clauses in criminal Acts — territorial scope, not substantive offence
    'triable by virtue of', 'triable by virtue',
    # Penalty consequence fragments — sentence splitter detaches "shall be liable" from its qualifier sub-items
    'guilty of an offence under this section shall be liable',
    # Legislative amendment insertions — amending another Act's text, not a new obligation
    'shall be inserted after',
    # Jurisdiction clauses — procedural court competence, not private-actor duty
    'shall have jurisdiction',
    # Penalty cap clauses — limits on consequence, not an obligation
    'only to the penalties',
    # Interpretation/reading clauses — same family as existing 'is to be read', 'shall be construed'
    'shall be read',
    # Territorial extent clauses in SIs — structural, not an obligation
    'shall extend to',
    # Cross-reference interpretation clauses in SIs — 'a reference to reg X is to the regulation...'
    'is to the regulation', 'is to the regulations',
    # Scope/transitional continuation clauses — 'The 1981 Regulations shall continue to apply'
    'shall continue to apply',
    # Scope-exception clauses — 'Paragraph (1) shall not apply'; distinct from prohibitions ('shall not' + verb)
    'shall not apply',
    # Double-jeopardy protections — legal immunity, not an obligation
    'cannot be convicted',
    # Definitional labelling clauses — 'shall be known as an action of harassment'
    'shall be known as',
    # Pure liability-quantum sentences — specify punishment for an already-counted offence, no new obligation
    'person guilty of an offence under',
    'person guilty of any other offence under',
    'person guilty of an offence under section',
    # Appointment restriction clauses — public body governance, not a private actor obligation
    'no person shall be appointed',
    # Permission clauses — grant authority to public bodies/courts, not private-actor duties
    'it shall be lawful for', 'it shall be lawful to',
    # Ministerial/court procedural restriction clauses — constrain Minister or court powers,
    # not private-actor obligations (e.g. NMW Act s.2: 'No provision shall be made...which treats persons differently')
    'no provision shall be made', 'no order shall be made', 'no regulations shall be made',
    'no amendment shall be made', 'no direction shall be given', 'no notice shall be given',
]

STRUCTURAL_SUBJECTS = [
    'case 1', 'case 2', 'case 3', 'case 4', 'case 5', 'case 6',
    'notice', 'application', 'order', 'direction', 'statement',
    'scheme', 'rules', 'standing orders', 'draft', 'notification',
    'proceedings', 'period', 'arrangement', 'provision', 'regulation',
    'section', 'subsection', 'paragraph', 'sub-paragraph', 'copy', 'report', 'decision',
    'bill', 'act of', 'no recommendation',
    'path order', 'path agreement', 'byelaws',
    'warning notice', 'decision notice', 'final notice',
    'penalty notice', 'supervisory notice',
    'date', 'validity', 'preparation and', 'environmental permit', 'permit',
    'poll', 'votes', 'seat', 'seats', 'ballot', 'vacancy', 'allocation',
    'return', 'figure', 'list', 'candidates', 'recalculation', 'electorate',
    'constituency', 'register',
]

CLAUSE_OPENERS = [
    'if', 'where', 'when', 'in', 'for', 'but',
    'unless', 'until', 'references', 'subject', 'notwithstanding',
]

REFERENCE_SCHEDULE_KEYWORDS = [
    'list of chemicals', 'schedule of fees', 'schedule of charges',
    'prescribed form', 'form of ', 'enactments repealed',
    'amendments to', 'transitional provisions',
    'consequential amendments'
]

IMPLIED_OBLIGATION_WORDS = [
    'prove that', 'prove he', 'prove she', 'prove it', 'prove the',
    'to prove', 'show that', 'show he', 'show she', 'to show',
    'demonstrate that', 'establish that',
]

ACTIVE_COMPLIANCE_MARKERS = [
    'adequate procedures', 'due diligence', 'reasonable precautions',
    'all reasonable steps', 'reasonable care', 'management system',
    'compliance with',
]

# ---------------------------------------------------------------------------
# Recall additions for the high-recall candidate filter (extract_candidates.py)
# ---------------------------------------------------------------------------
# These close recall HOLES the precision-tuned classifier missed. They are NOT
# used by the legacy analyser (its PRESCRIPTIVE_WORDS is unchanged); the
# candidate filter unions them in. The candidate filter's job is RECALL — surface
# anything that MIGHT be a private-actor burden; the LLM+human layer rejects
# non-operative ones. Never use these to drop.

# #1 Rights / entitlements — a substantive right on a private actor creates a
# correlative private duty (rubric §5B), a real burden. The legacy list had only
# 4 hyper-specific 'has the right not to be…' phrases; these generalise it.
RIGHTS_CUES = [
    'has the right to', 'have the right to', 'has a right to', 'have a right to',
    'is entitled to', 'are entitled to', 'shall be entitled to',
    'has the right not to', 'have the right not to',
]

# #2 Restriction-as-prohibition — "may only X" forbids all other conduct. (The
# general "no <noun> shall/may" pattern is handled by a regex in the filter.)
RESTRICTION_PROHIBITION_CUES = [
    'may only', 'shall only', 'must only', 'is not to', 'are not to',
    'shall refrain from', 'must refrain from', 'is not entitled to', 'are not entitled to',
]

# #3 Void / contracting-out — "terms are void unless…" is a prohibition on
# contracting out (rubric §3.4). These currently sit in DEFINITIONAL_PATTERNS and
# are wrongly DROPPED; the candidate filter surfaces them (cue match wins).
VOID_CUES = [
    'is void', 'are void', 'shall be void', 'is of no effect', 'are of no effect',
    'shall be of no effect', 'has no effect', 'have no effect',
]

# #4 Responsibility / obligation framing without shall/must.
RESPONSIBILITY_CUES = [
    'is responsible for', 'are responsible for', 'shall be responsible',
    'it is the responsibility of', 'is bound to', 'are bound to',
    'is liable for', 'are liable for',
]

# #5 Defence framing as a standalone cue — catches defences with no prove/show
# verb (those are caught by IMPLIED_OBLIGATION_WORDS).
DEFENCE_CUES = [
    'it is a defence', 'it shall be a defence', 'is a defence for', 'a defence for',
    'the burden of proof', 'burden of proof is on', 'unless he proves',
    'unless the person shows', 'unless it is proved', 'unless it is shown',
]

# #6 Penalty-as-obligation (Victorian) — the penalty clause IS the primary
# obligation. 'shall forfeit' was entirely absent.
PENALTY_OBLIGATION_CUES = [
    'shall forfeit', 'shall forfeit and pay', 'shall pay a penalty',
    'liable to a penalty', 'shall be answerable', 'shall make good',
]

# #7 Bare passive 'is required' (no "to") — e.g. "a licence is required".
BARE_REQUIRED_CUES = [
    'is required', 'are required',
]

# #8 Bare 'comply with' (no "must") — list-item fragments under a parent "shall—".
COMPLIANCE_VERB_CUES = [
    'comply with', 'complies with', 'complied with', 'in compliance with',
]

# #9 Enforcement powers creating a correlative SUBMIT duty on a private actor
# (rubric Cat 5 — the actor must submit when the authority acts). Recall hole:
# these are phrased as the authority's power, but impose a private-actor burden.
ENFORCEMENT_POWER_CUES = [
    'stop and search', 'search and seize', 'seize and detain', 'enter and inspect',
    'enter and search', 'may require', 'may direct', 'may seize', 'may enter',
    'may inspect', 'may demand', 'may detain', 'board and search', 'may by notice require',
]

# #10 Leading imperative duty-verbs — list items in isolation ("(b) produce the
# certificate…") carry their modal in the parent stem. The context parse
# reattaches the parent ("Every employer shall— …"), but as a recall backstop for
# context_quality=partial cases we also surface a fragment that BEGINS with one of
# these compliance verbs. Tagged 'leading_imperative_verb' so the catch is visible.
LEADING_DUTY_VERBS = [
    'produce', 'permit', 'furnish', 'display', 'keep', 'maintain', 'retain',
    'notify', 'submit', 'supply', 'deliver', 'provide', 'prepare', 'record',
    'send', 'obtain', 'register', 'report', 'inform', 'disclose', 'declare',
    'exhibit', 'affix', 'label', 'mark', 'post', 'pay', 'ensure', 'take',
]

# Non-blocking HINT lists (rubric: surface then human-reject; never drop). The
# candidate filter still surfaces a sentence even if it matches one of these; the
# match is attached as a hint flag so the LLM+human layer can weigh it.
#   - DEFINITIONAL_PATTERNS  -> hint 'non_operative_suspect'
#   - STRUCTURAL_SUBJECTS    -> hint 'structural_subject_suspect'
#   - CLAUSE_OPENERS         -> hint 'clause_opener'
