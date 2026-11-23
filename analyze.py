import os, re, json, logging, statistics
from pypdf import PdfReader
from collections import Counter
logging.getLogger('pypdf').setLevel(logging.ERROR)

BASE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(BASE, 'fulltext')
IMG = os.path.join(BASE, 'images')
os.makedirs(TXT, exist_ok=True)
os.makedirs(IMG, exist_ok=True)

ABBREV = ['Fig.', 'Figs.', 'Eq.', 'Eqs.', 'e.g.', 'i.e.', 'et al.', 'vs.', 'cf.',
          'Sec.', 'No.', 'Dr.', 'Mr.', 'Prof.', 'approx.', 'esp.', 'etc.', 'viz.',
          'Ref.', 'Refs.', 'Chap.', 'Vol.', 'pp.', 'Jan.', 'Feb.', 'Mar.', 'Apr.',
          'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
          'Ph.D.', 'M.S.', 'B.S.', 'a.m.', 'p.m.', 'St.', 'Mt.']

AI_MARKERS = ['delve', 'moreover', 'furthermore', 'in conclusion', 'it is worth noting',
              'it is important to note', 'crucial', 'comprehensive', 'robust', 'leverage',
              'facilitate', 'seamless', 'pivotal', 'underscore', 'in summary',
              'additionally', 'notably', 'overall', 'a testament to', 'plays a vital role',
              'shed light on', 'holistic', 'intricate', 'myriad', 'tapestry', 'realm',
              'showcase', 'endeavor', 'boasts', 'harness', 'elevate', 'paramount',
              'nuanced', 'multifaceted', 'in today', 'landscape', 'navigate',
              'game-changer', 'cutting-edge', 'state-of-the-art', 'firstly', 'secondly',
              'last but not least', 'in the era of', 'with the development of']

STRUCT_KEYS = {
    'summary': ['summary sheet', 'abstract'],
    'keywords': ['keywords', 'key words'],
    'contents': ['contents', 'table of contents'],
    'restatement': ['problem restatement', 'restatement', 'problem background', 'introduction'],
    'assumptions': ['assumption'],
    'notation': ['notation', 'nomenclature', 'list of symbols', 'symbol description', 'symbols and'],
    'sensitivity': ['sensitivity', 'sensitivities'],
    'validation': ['validation', 'verification', 'model test', 'testing', 'error analysis', 'robustness'],
    'strengths': ['strength', 'weakness', 'advantage', 'disadvantage', 'evaluation of', 'model evaluation'],
    'conclusion': ['conclusion'],
    'references': ['references', 'bibliography'],
    'appendix': ['appendix', 'appendices'],
    'promotion': ['promotion', 'generalization', 'extension', 'future work', 'improvement'],
    'letter': ['letter', 'memo', 'memorandum', 'recommendation'],
}

def split_sentences(text):
    t = re.sub(r'\s+', ' ', text)
    for ab in ABBREV:
        t = t.replace(ab, ab.replace('.', '<D>'))
        cap = ab[0].upper() + ab[1:]
        t = t.replace(cap, cap.replace('.', '<D>'))
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z(0-9"“\'])', t)
    out = []
    for p in parts:
        p = p.replace('<D>', '.').strip()
        words = re.findall(r"[A-Za-z][A-Za-z'\-]*", p)
        if len(words) >= 3 and len(p) < 1200:
            out.append(words)
    return out

def syllables(w):
    w = w.lower()
    w = re.sub(r'[^a-z]', '', w)
    if len(w) <= 3:
        return 1
    groups = re.findall(r'[aeiouy]+', w)
    n = len(groups)
    if w.endswith('e') and not w.endswith(('le', 'ee', 'ye')) and n > 1:
        n -= 1
    return max(1, n)

def analyze_pdf(path):
    r = PdfReader(path)
    pages = []
    img_filters = Counter()
    img_count = 0
    img_sizes = []
    vector_pages = 0
    for pg in r.pages:
        try:
            pages.append(pg.extract_text() or '')
        except Exception:
            pages.append('')
        try:
            res = pg.get('/Resources')
            if res and '/XObject' in res:
                xo = res['/XObject'].get_object()
                for k in xo:
                    obj = xo[k].get_object()
                    if obj.get('/Subtype') == '/Image':
                        img_count += 1
                        img_filters[str(obj.get('/Filter'))] += 1
                        try:
                            img_sizes.append((int(obj.get('/Width')), int(obj.get('/Height'))))
                        except Exception:
                            pass
        except Exception:
            pass
        try:
            data = pg.get_contents().get_data()
            n_path = len(re.findall(rb'\b(re|l|c|v|y)\b', data))
            if n_path > 400:
                vector_pages += 1
        except Exception:
            pass
    return r, pages, img_count, img_filters, img_sizes, vector_pages

def caption_counts(pages):
    fig_caps, tab_caps = [], []
    for i, p in enumerate(pages):
        for line in p.split('\n'):
            l = line.strip()
            if re.match(r'^(Figure|Fig\.?)\s*\d+', l, re.I) and len(l) < 300:
                fig_caps.append((i + 1, l[:90]))
            if re.match(r'^Table\s*\d+', l, re.I) and len(l) < 300:
                tab_caps.append((i + 1, l[:90]))
    return fig_caps, tab_caps

def headings(pages):
    hs = []
    pat = re.compile(r'^\s*(\d+(?:\.\d+){0,2})[\.\)]?\s+([A-Z][A-Za-z][A-Za-z \-/&,\(\)]{2,70})\s*$')
    for i, p in enumerate(pages):
        for line in p.split('\n'):
            l = line.strip()
            m = pat.match(l)
            if m and len(l) < 85 and not l.endswith('.'):
                hs.append((i + 1, m.group(1), m.group(2).strip()))
    return hs

manifest = json.load(open(os.path.join(BASE, 'manifest.json'), encoding='utf-8'))
report = {}
for p in manifest['papers']:
    fn = p['file']
    path = os.path.join(BASE, fn)
    r, pages, img_count, img_filters, img_sizes, vector_pages = analyze_pdf(path)
    tag = p['tag']
    full = '\n\n'.join(pages)
    with open(os.path.join(TXT, tag + '.txt'), 'w', encoding='utf-8') as f:
        for i, pg in enumerate(pages):
            f.write(f'\n===== PDF page {i+1} =====\n{pg}\n')

    # 导出每篇最大的3张位图供抽查图风格
    outdir = os.path.join(IMG, tag)
    os.makedirs(outdir, exist_ok=True)
    try:
        sizes = []
        for pi, pg in enumerate(r.pages):
            res = pg.get('/Resources')
            if res and '/XObject' in res:
                xo = res['/XObject'].get_object()
                for k in xo:
                    obj = xo[k].get_object()
                    if obj.get('/Subtype') == '/Image':
                        w_, h_ = int(obj.get('/Width')), int(obj.get('/Height'))
                        if w_ * h_ > 120000:
                            sizes.append((w_ * h_, pi, k))
        sizes.sort(reverse=True)
        for rank, (_, pi, k) in enumerate(sizes[:3]):
            for im in r.pages[pi].images:
                if im.image.width * im.image.height > 120000:
                    im.image.save(os.path.join(outdir, f'p{pi+1}_{rank}.png'))
                    break
    except Exception:
        pass

    sents = split_sentences(full)
    lens = [len(s) for s in sents]
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", full.lower())
    wc = len(words)
    ns = len(sents)
    syl = sum(syllables(w) for w in words)
    passive = len(re.findall(r'\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?[a-z]+(?:ed|en|wn|ne|nt)\b', full, re.I))
    present = len(re.findall(r'\b(is|are)\b', full, re.I))
    past = len(re.findall(r'\b(was|were)\b', full, re.I))
    first_person = len(re.findall(r'\b(we|our|us)\b', full, re.I))
    low = full.lower()
    ai = Counter({m: low.count(m) for m in AI_MARKERS if low.count(m)})
    fig_caps, tab_caps = caption_counts(pages)
    hs = headings(pages)
    fig_refs = len(re.findall(r'\b(?:Figure|Fig\.?)\s*\d+', full))
    tab_refs = len(re.findall(r'\bTable\s*\d+', full))
    eq_numbers = len(set(re.findall(r'\((\d{1,2})\)\s*$', full, re.M)))
    ref_section = ''
    mref = re.search(r'\n\s*References\s*\n', full)
    if mref:
        ref_section = full[mref.end():]
    n_refs = len(re.findall(r'^\s*\[\d{1,2}\]', ref_section, re.M))
    ref_years = re.findall(r'\b(19[5-9]\d|20[0-2]\d)\b', ref_section)
    code_hits = len(re.findall(r'\b(import\s+\w+|def\s+\w+|function\s+\w+|numpy|pandas|plt\.|for\s+\w+\s+in\s+range|end;|fprintf)\b', full))
    structure = {}
    for key, kws in STRUCT_KEYS.items():
        hits = [i + 1 for i, pg in enumerate(pages) if any(k in pg.lower() for k in kws)]
        structure[key] = hits[:6]
    abstract_words = sum(len(s) for s in split_sentences(pages[0]))
    short = sum(1 for l in lens if l < 12)
    mid = sum(1 for l in lens if 12 <= l <= 25)
    long_ = sum(1 for l in lens if l > 25)
    report[tag] = {
        'file': fn, 'team': p['team'], 'n_pages': p['n_pages'],
        'word_count': wc, 'n_sentences': ns, 'words_per_page': round(wc / p['n_pages'], 0),
        'sent_len_mean': round(statistics.mean(lens), 1) if lens else 0,
        'sent_len_median': statistics.median(lens) if lens else 0,
        'sent_len_max': max(lens) if lens else 0,
        'sent_len_stdev': round(statistics.pstdev(lens), 1) if lens else 0,
        'pct_short_lt12': round(100 * short / ns, 1) if ns else 0,
        'pct_mid_12_25': round(100 * mid / ns, 1) if ns else 0,
        'pct_long_gt25': round(100 * long_ / ns, 1) if ns else 0,
        'passive_per_1000w': round(1000 * passive / wc, 1) if wc else 0,
        'present_is_are': present, 'past_was_were': past,
        'first_person_we_our_us': first_person,
        'first_person_per_1000w': round(1000 * first_person / wc, 1) if wc else 0,
        'flesch_reading_ease': round(206.835 - 1.015 * (wc / ns) - 84.6 * (syl / wc), 1) if ns and wc else None,
        'flesch_kincaid_grade': round(0.39 * (wc / ns) + 11.8 * (syl / wc) - 15.59, 1) if ns and wc else None,
        'ttr': round(len(set(words)) / wc, 3) if wc else 0,
        'img_xobject_count': img_count, 'img_filters': dict(img_filters),
        'img_large_over_600px': sum(1 for w, h in img_sizes if max(w, h) > 600),
        'img_small_under_200px': sum(1 for w, h in img_sizes if max(w, h) < 200),
        'vector_heavy_pages': vector_pages,
        'n_fig_captions': len(fig_caps), 'fig_captions': fig_caps,
        'n_tab_captions': len(tab_caps), 'tab_captions': tab_caps,
        'fig_mentions_total': fig_refs, 'tab_mentions_total': tab_refs,
        'eq_numbered_max': eq_numbers,
        'n_reference_entries': n_refs,
        'ref_year_min': min(ref_years) if ref_years else None,
        'ref_year_max': max(ref_years) if ref_years else None,
        'code_token_hits': code_hits,
        'structure_pages': structure,
        'ai_marker_total': sum(ai.values()),
        'ai_per_1000w': round(1000 * sum(ai.values()) / wc, 2) if wc else 0,
        'ai_markers': dict(ai.most_common()),
        'abstract_page1_words': abstract_words,
        'headings': hs,
    }
    print(f"{tag} {p['n_pages']:3d}p {wc:6d}w {ns:4d}s mean{report[tag]['sent_len_mean']:5.1f} "
          f"med{report[tag]['sent_len_median']:4.0f} S/M/L {report[tag]['pct_short_lt12']:4.1f}/{report[tag]['pct_mid_12_25']:4.1f}/{report[tag]['pct_long_gt25']:4.1f} "
          f"FRE{report[tag]['flesch_reading_ease']} FK{report[tag]['flesch_kincaid_grade']} "
          f"pass{report[tag]['passive_per_1000w']:4.1f} we{report[tag]['first_person_per_1000w']:4.1f} "
          f"fig{len(fig_caps):3d} tab{len(tab_caps):2d} img{img_count:3d} ref{n_refs:2d} ai{sum(ai.values()):3d}")

with open(os.path.join(BASE, 'metrics.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print('\n全文文本 fulltext/，抽查图 images/，指标 metrics.json')
