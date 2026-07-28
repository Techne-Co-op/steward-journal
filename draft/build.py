#!/usr/bin/env python3
"""Build the reorganized draft of the steward's journal from the published page.

Reads ../index.html as the source of truth for the prose, then emits:
  2026-07-27/index.html   the day, with deks, dual reading order, sources, dictation
  index.html              a real journal index that has room for a second day

Run from the draft/ directory: python3 build.py
"""
import html
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE.parent / "index.html"

# --- editorial layer added by the reorganization ------------------------------

DEKS = {
    "I":    "What a corporation cannot record, and why the accounting is the real question.",
    "II":   "Why 2026, and what makes a moment different from a duration.",
    "III":  "Four people a firm does not serve, and the record that would have to hold them.",
    "IV":   "The Limited Cooperative Association as a container for capital without capture.",
    "V":    "February's scope, May's mandate, and an honest account of what is unfinished.",
    "VI":   "A tool imagined for collective coordination, and what became of it.",
    "VII":  "Financial statements are the shadow. The activity journal is the thing.",
    "VIII": "The graphical interface as a ceiling, and a question put to the cooperative.",
    "IX":   "Colorado water in a 1982 lecture, and an answer that describes federation.",
    "X":    "Why the one kind of contribution we refuse to count may be the one that matters most.",
}

GROUPS = [
    ("Why now", "The moment, the lineage, and the tradition being resumed.", ["II", "VI", "IX"]),
    ("What it is for, and who", "The work as craft, the people a firm does not serve, and play.", ["I", "III", "X"]),
    ("How it is held", "The legal container and the architecture that carries it.", ["IV", "VII", "VIII"]),
    ("The account", "The only entry answerable to a board rather than to an idea.", ["V"]),
]

T = "https://techne.coop"
SOURCES = {
    "I":    [("Counting rules", f"{T}/commons/patronage/counting-rules/", "what the accounting actually recognizes")],
    "II":   [],
    "III":  [("Opportunity board", f"{T}/commons/opportunities/", "play, practice, and work")],
    "IV":   [("Bylaws and Schedule A", f"{T}/legal/", "the investor member class"),
             ("Agreements shelf", f"{T}/commons/agreements/", "what binds a member")],
    "V":    [("The packet ledger", f"{T}/commons/build/", "every packet names what blocks it"),
             ("Treasury", f"{T}/commons/treasury/", "specified and sequenced, not built"),
             ("Launch blockers", f"{T}/commons/build/launch/", "what remains before August 14")],
    "VI":   [("PRD principle 01", f"{T}/commons/prd/", "augmentation, not automation")],
    "VII":  [("PRD section 5", f"{T}/commons/prd/", "the four primitives and the fold law")],
    "VIII": [("PRD section 7", f"{T}/commons/prd/", "the three doors: Browse, Ask, Verify")],
    "IX":   [("Future Possibilities, 1982", "https://archive.org/details/youtube-si9iqF5uTFk",
              "the NSA lecture, released publicly in 2024")],
    "X":    [("Opportunity board", f"{T}/commons/opportunities/", "play is listed first"),
             ("Counting rules", f"{T}/commons/patronage/counting-rules/", "HOURS excludes play")],
}

# Light editorial pass over the published prose. Every change is here and nowhere
# else, so the diff against the published page is always exactly this list.
# (entry, exact substring in the published text) -> replacement, plus the reason.
EDITS = [
    ("II", "In 2026, and particularly in the state of AI in July of 2026,",
     "In 2026, and particularly in the state of AI this July,",
     "the year lands twice in one sentence"),
    ("II", "the participants and guests of the World Wide Web.",
     "the participants and guests of the web.",
     "the full formal name reads dated; the construction is kept"),
    ("III", "That absence is what casts Techne as a possible third space,",
     "That absence is what makes Techne possible as a third space,",
     "a cleaner verb for the same claim"),
    ("III", "a meaningful interface to pass down their practice",
     "a meaningful way to pass down their practice",
     "the only piece of jargon in the warmest paragraph in the piece"),
    ("IV", "gives us specifically is a container",
     "gives us is a container",
     "filler"),
    ("V", "should be unprioritized where they detract",
     "should be set aside where they detract",
     "plainer than the coinage, and this is a paraphrase rather than a quotation"),
    ("V", "than dress it.", "than dress it up.", "the idiom"),
    ("VI", "a first century of computing", "the first century of computing",
     "a specific century, not one of several"),
    ("VII", "The work happened, and then months later a statement describes its shadow",
     "The work happens, and months later a statement describes its shadow",
     "tense agreement, and one fewer beat"),
    ("VII", "That is also, incidentally, the honest answer to Goodhart,",
     "That is also the honest answer to Goodhart,",
     "the hedge undercuts the strongest claim in the entry"),
    ("IX", "And then Colorado: the eastern half",
     "</p><p>And then Colorado: the eastern half",
     "a paragraph break, so Colorado lands as its own beat rather than "
     "the fifth item in a list"),
]


def apply_edits(entries):
    """Apply the editorial pass, and fail loudly if a target has moved."""
    applied = []
    for num, old, new, why in EDITS:
        hits = 0
        for i, (is_close, txt) in enumerate(entries[num]["paras"]):
            if old in txt:
                entries[num]["paras"][i] = (is_close, txt.replace(old, new))
                hits += 1
        if hits != 1:
            raise SystemExit(f"edit for {num} matched {hits} paragraphs: {old[:60]!r}")
        applied.append((num, old, new, why))
    # a paragraph split arrives as inline markup; re-parse so counts stay honest
    for e in entries.values():
        rebuilt = []
        for is_close, txt in e["paras"]:
            parts = txt.split("</p><p>")
            for j, part in enumerate(parts):
                rebuilt.append((is_close and j == len(parts) - 1, part))
        e["paras"] = rebuilt
    return applied


def parse_entries(src_html):
    """Pull the ten entries out of the published page."""
    pat = re.compile(
        r'<article class="entry" id="([^"]+)" style="--tint:var\(--(\w+)\)">\s*'
        r'<div class="num">([IVX]+)</div>\s*<h2>(.*?)</h2>\s*'
        r'<span class="when">(.*?)</span>(.*?)</article>', re.S)
    out = {}
    order = []
    for m in pat.finditer(src_html):
        eid, tint, num, title, when, body = m.groups()
        paras = re.findall(r'<p( class="close")?>(.*?)</p>', body, re.S)
        out[num] = dict(id=eid, tint=tint, num=num, title=title.strip(),
                        when=when.strip(),
                        paras=[(bool(c), p.strip()) for c, p in paras])
        order.append(num)
    return out, order


def words(entry):
    return sum(len(re.sub(r'<[^>]+>', '', p).split()) for _, p in entry["paras"])


CSS = """
  :root{
    --gold:#C4A96A; --amber:#C4956A; --coral:#C47A6A; --rose:#B46A8A; --violet:#8A76B4; --twilight:#6A8AC4;
    --serif:'Libre Baskerville',Georgia,serif; --mono:'IBM Plex Mono','SFMono-Regular',Consolas,monospace;
  }
  [data-mode="dark"]{
    --bg:#0F0F12; --surface:#16161B; --line:#2A2A30; --rule:#3A3A42;
    --heading:#E8E4DF; --text:#CFCBC4; --muted:#8A857E; --faint:#5A554F;
    --ember-text:#D4A57A; --blue-text:#97B5E8;
  }
  [data-mode="light"]{
    --bg:#F7F5F0; --surface:#FCFBF8; --line:#D8D3C8; --rule:#9A958A;
    --heading:#1A1A1F; --text:#2E2C28; --muted:#646058; --faint:#A39E92;
    --ember-text:#6F5436; --blue-text:#39588F;
  }
  *{box-sizing:border-box; margin:0; padding:0}
  body{background:var(--bg); color:var(--text); font:400 17px/1.75 var(--serif); -webkit-font-smoothing:antialiased}
  .wrap{max-width:720px; margin:0 auto; padding:0 24px 96px}
  a{color:var(--blue-text); text-decoration:none}
  a:hover{text-decoration:underline}
  em{color:var(--heading); font-style:italic}
  :focus-visible{outline:2px solid var(--blue-text); outline-offset:2px}

  .topbar{display:flex; justify-content:space-between; align-items:center; padding:16px 0 12px; border-bottom:1px solid var(--line)}
  .topbar .bc{font:400 11.5px var(--mono); color:var(--muted)}
  .mode-btn{font:400 11.5px var(--mono); color:var(--muted); background:var(--surface); border:1px solid var(--line); border-radius:2px; padding:4px 10px; cursor:pointer}
  .mode-btn:hover{color:var(--heading)}

  .draftbar{margin-top:14px; border:1px solid var(--rule); border-left:2px solid var(--ember-text); background:var(--surface); padding:12px 16px; font:400 12.5px/1.7 var(--mono); color:var(--muted)}
  .draftbar b{color:var(--ember-text); font-weight:500}

  .mast{padding:56px 0 36px; border-bottom:1px solid var(--rule)}
  .mast .kicker{font:500 11px var(--mono); color:var(--ember-text); letter-spacing:.14em; text-transform:uppercase}
  .mast h1{font:400 clamp(32px,5vw,44px)/1.15 var(--serif); color:var(--heading); margin:14px 0 16px}
  .mast .prov{font:400 13.5px/1.7 var(--serif); font-style:italic; color:var(--muted); max-width:58ch}
  .mast .meta{margin-top:16px; font:400 11px var(--mono); color:var(--faint); letter-spacing:.06em}

  /* dual reading order */
  .orders{margin-top:32px}
  .orders .lab{font:500 10.5px var(--mono); letter-spacing:.14em; text-transform:uppercase; color:var(--faint); display:block; margin-bottom:12px}
  .grp{margin-bottom:20px; padding-left:14px; border-left:2px solid var(--line)}
  .grp .gt{font:400 15px var(--serif); color:var(--heading); display:block}
  .grp .gd{font:400 12.5px/1.6 var(--serif); font-style:italic; color:var(--muted); display:block; margin:2px 0 8px}
  .grp .gl{display:flex; flex-wrap:wrap; gap:14px; font:400 11.5px var(--mono)}
  .grp .gl a{color:var(--muted); border-bottom:1px solid var(--line); padding-bottom:2px}
  .grp .gl a:hover{color:var(--heading); text-decoration:none; border-color:var(--rule)}
  .chrono{display:flex; flex-wrap:wrap; gap:10px 28px; font:400 11.5px var(--mono); margin-top:6px}
  .chrono a{color:var(--muted)}
  .chrono a:hover{color:var(--heading)}
  .chrono .t{color:var(--faint)}

  .entry{padding:56px 0 0}
  .entry + .entry{margin-top:8px; border-top:1px solid var(--line)}
  .entry .num{font:500 11px var(--mono); letter-spacing:.14em; text-transform:uppercase; color:var(--tint,var(--ember-text))}
  .entry h2{font:400 clamp(24px,3.4vw,30px)/1.25 var(--serif); color:var(--heading); margin:10px 0 8px}
  .entry .dek{font:400 15px/1.6 var(--serif); font-style:italic; color:var(--muted); margin-bottom:12px; max-width:56ch}
  .entry .when{font:400 11px var(--mono); color:var(--faint); letter-spacing:.08em; margin-bottom:26px; display:block}
  .entry p{margin-bottom:20px}
  .entry .close{border-left:2px solid var(--tint,var(--ember-text)); padding-left:18px; color:var(--heading)}

  /* checkable claims */
  .sources{margin-top:26px; padding-top:14px; border-top:1px solid var(--line)}
  .sources .lab{font:500 10px var(--mono); letter-spacing:.12em; text-transform:uppercase; color:var(--faint); display:block; margin-bottom:9px}
  .sources ul{list-style:none}
  .sources li{font:400 12.5px/1.7 var(--mono); margin-bottom:4px}
  .sources li span{color:var(--faint)}
  .sources .none{font:400 12.5px/1.7 var(--serif); font-style:italic; color:var(--faint)}

  /* the first-order record */
  details.dict{margin-top:16px; border:1px solid var(--line); border-radius:2px; background:var(--surface)}
  details.dict summary{cursor:pointer; list-style:none; padding:10px 14px; font:400 11px var(--mono); letter-spacing:.08em; color:var(--muted)}
  details.dict summary::-webkit-details-marker{display:none}
  details.dict summary::before{content:"+\\00a0"; color:var(--tint,var(--ember-text))}
  details.dict[open] summary::before{content:"\\2212\\00a0"}
  details.dict summary:hover{color:var(--heading)}
  details.dict .raw{padding:2px 16px 16px; font:400 13.5px/1.85 var(--mono); color:var(--muted); white-space:pre-wrap}
  details.dict .ed{margin-bottom:14px; font:400 12px/1.7 var(--mono)}
  details.dict .ed b{color:var(--ember-text); font-weight:500; display:inline-block; min-width:38px}
  details.dict .ed span{display:block; margin-left:38px}
  details.dict .ed .was{color:var(--faint); text-decoration:line-through}
  details.dict .ed .now{color:var(--text)}
  details.dict .ed .why{font-family:var(--serif); font-style:italic; color:var(--muted); margin-top:3px}

  footer{margin-top:72px; padding-top:18px; border-top:1px solid var(--line); font:400 11.5px/1.85 var(--mono); color:var(--faint)}
  footer .note{display:block; margin-top:8px; font-family:var(--serif); font-size:13px; line-height:1.7; letter-spacing:0}
  footer .fix{display:block; margin-top:12px; padding:10px 14px; border:1px solid var(--line); background:var(--surface); font-family:var(--serif); font-size:13px; line-height:1.7; letter-spacing:0; color:var(--muted)}

  /* index */
  .day{padding:40px 0 0; border-top:1px solid var(--line); margin-top:8px}
  .day .dt{font:500 11px var(--mono); letter-spacing:.14em; text-transform:uppercase; color:var(--ember-text)}
  .day h2{font:400 26px/1.25 var(--serif); color:var(--heading); margin:10px 0 8px}
  .day h2 a{color:var(--heading)}
  .day .dek{font:400 15px/1.6 var(--serif); font-style:italic; color:var(--muted); max-width:56ch}
  .day .stat{margin-top:14px; font:400 11px var(--mono); color:var(--faint); letter-spacing:.06em}
  .day .themes{margin-top:16px; font:400 12.5px/1.9 var(--mono); color:var(--muted)}
  .day .themes b{color:var(--heading); font-weight:400}

  @media print{
    [data-mode]{--bg:#fff; --surface:#fff; --line:#ddd; --rule:#999; --heading:#000; --text:#222; --muted:#555; --faint:#777; --ember-text:#333; --blue-text:#222}
    body{font-size:11pt}
    .topbar,.mode-btn,.draftbar,.orders{display:none}
    .entry{page-break-inside:avoid; padding-top:28px}
    details.dict{display:none}
    .sources li{font-size:9pt}
    a{text-decoration:none}
    a[href^="http"]::after{content:" (" attr(href) ")"; font-size:8pt; color:#666}
  }
"""

MODE_JS = """
  (function(){
    var root=document.documentElement, btn=document.getElementById('modeBtn');
    function label(){btn.textContent=root.getAttribute('data-mode')==='dark'?'light':'dark';}
    btn.addEventListener('click',function(){
      var m=root.getAttribute('data-mode')==='dark'?'light':'dark';
      root.setAttribute('data-mode',m);
      try{localStorage.setItem('techne-mode',m);}catch(e){}
      label();
    });
    label();
  })();
"""

HEAD_BOOT = """<script>
  (function(){var s=null;try{s=localStorage.getItem('techne-mode');}catch(e){}
  var m=s||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');
  document.documentElement.setAttribute('data-mode',m)})();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">"""

DRAFTBAR = """<div class="draftbar">
  <b>Draft.</b> A reorganization of the July 27 reflections, unlinked from anywhere and
  carrying noindex. The published version stands unchanged at
  <a href="../../">the journal root</a>. Nothing here is adopted. The prose carries a
  light editorial pass, listed in full at the foot of the page.
</div>"""


def build_day(entries, order, edits):
    p = []
    a = p.append
    a('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">')
    a('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    a('<meta name="color-scheme" content="dark light">')
    a("<title>Ten reflections &middot; July 27, 2026 &middot; The Steward's Journal</title>")
    a('<meta name="description" content="Ten reflections by the Ventures and Operations '
      'Steward of RegenHub, LCA, dictated July 27, 2026. Draft reorganization.">')
    a('<meta name="robots" content="noindex,nofollow">')
    a(HEAD_BOOT)
    a(f'<style>{CSS}</style>\n</head>\n<body>\n<div class="wrap">')

    a('\n<div class="topbar">')
    a('  <span class="bc"><a href="../">The steward\'s journal</a> &middot; July 27, 2026</span>')
    a('  <button class="mode-btn" id="modeBtn" aria-label="Toggle light and dark mode">dark</button>')
    a('</div>')
    a(DRAFTBAR)

    total = sum(words(entries[n]) for n in order)
    a('\n<div class="mast">')
    a('  <div class="kicker">July 27, 2026 &middot; eighteen days before the launch</div>')
    a('  <h1>Ten reflections</h1>')
    a('  <p class="prov">Todd Youngblood, Ventures and Operations Steward, RegenHub, LCA. '
      'Dictated across one afternoon and evening, transcribed and lightly edited: the '
      'dictation repaired, the phrasing kept. Drafts, open to correction.</p>')
    a(f'  <div class="meta">ten reflections &middot; {total:,} words &middot; about '
      f'{round(total/225)} minutes &middot; each entry carries its own dictation</div>')

    a('\n  <div class="orders">')
    a('    <span class="lab">Read by theme</span>')
    for title, dek, nums in GROUPS:
        a('    <div class="grp">')
        a(f'      <span class="gt">{html.escape(title)}</span>')
        a(f'      <span class="gd">{html.escape(dek)}</span>')
        a('      <span class="gl">')
        for n in nums:
            e = entries[n]
            a(f'        <a href="#{e["id"]}">{n} &middot; {e["title"]}</a>')
        a('      </span>')
        a('    </div>')
    a('    <span class="lab" style="margin-top:26px">Read in the order dictated</span>')
    a('    <div class="chrono">')
    for n in order:
        e = entries[n]
        a(f'      <a href="#{e["id"]}">{n} &middot; {e["title"]} '
          f'<span class="t">{e["when"].split("&middot;")[0].strip()}</span></a>')
    a('    </div>')
    a('  </div>')
    a('</div>')

    for n in order:
        e = entries[n]
        a(f'\n<article class="entry" id="{e["id"]}" style="--tint:var(--{e["tint"]})">')
        a(f'  <div class="num">{n}</div>')
        a(f'  <h2>{e["title"]}</h2>')
        a(f'  <p class="dek">{html.escape(DEKS[n])}</p>')
        a(f'  <span class="when">{e["when"]}</span>')
        for is_close, txt in e["paras"]:
            a(f'  <p{" class=\"close\"" if is_close else ""}>{txt}</p>')

        a('  <div class="sources">')
        a('    <span class="lab">Checks against</span>')
        if SOURCES[n]:
            a('    <ul>')
            for label, url, gloss in SOURCES[n]:
                a(f'      <li><a href="{url}">{html.escape(label)}</a> '
                  f'<span>&middot; {html.escape(gloss)}</span></li>')
            a('    </ul>')
        else:
            a('    <p class="none">Nothing. This one is a claim about the world rather '
              'than about the record, and it stands on its own argument.</p>')
        a('  </div>')

        a('</article>')

    a('\n<footer>')
    a("  <span>The steward's journal &middot; RegenHub, LCA &middot; Boulder, Colorado "
      "&middot; dictated 2026-07-27</span>")
    a('  <span class="note">Thinking, not record. Nothing here is a governing document of '
      'the cooperative, and nothing here has been adopted by anyone. The governing '
      'documents live in <a href="https://techne.coop/commons/">the Commonplace Book</a>. '
      'This page is unlisted and carries noindex; it is shared by link, for reading and '
      'for correction.</span>')
    a('  <span class="fix"><b>Found something wrong?</b> Corrections, disagreements, and '
      'objections go to the steward directly, or to '
      '<a href="https://github.com/Techne-Co-op/steward-journal/issues">the journal\'s '
      'issues</a>. A correction here is a new entry, never a silent edit.</span>')
    a('  <details class="dict" style="margin-top:16px">')
    a(f'    <summary>editorial changes from the published text &middot; {len(edits)}</summary>')
    a('    <div class="raw">')
    for num, old, new, why in edits:
        a(f'      <div class="ed"><b>{num}</b> <span class="was">{html.escape(old.replace("</p><p>", " "))}</span>'
          f'<span class="now">{html.escape(new.replace("</p><p>", " ¶ "))}</span>'
          f'<span class="why">{html.escape(why)}</span></div>')
    a('    </div>')
    a('  </details>')
    a('</footer>')
    a(f'\n</div>\n<script>{MODE_JS}</script>\n</body>\n</html>')
    return "\n".join(p)


def build_index(entries, order):
    total = sum(words(entries[n]) for n in order)
    p = []
    a = p.append
    a('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">')
    a('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    a('<meta name="color-scheme" content="dark light">')
    a("<title>The Steward's Journal &middot; RegenHub, LCA</title>")
    a('<meta name="description" content="Dated reflections by the Ventures and Operations '
      'Steward of RegenHub, LCA.">')
    a('<meta name="robots" content="noindex,nofollow">')
    a(HEAD_BOOT)
    a(f'<style>{CSS}</style>\n</head>\n<body>\n<div class="wrap">')
    a('\n<div class="topbar">')
    a('  <span class="bc">RegenHub, LCA &middot; Boulder, Colorado</span>')
    a('  <button class="mode-btn" id="modeBtn" aria-label="Toggle light and dark mode">dark</button>')
    a('</div>')
    a('<div class="draftbar">\n  <b>Draft.</b> This is the reorganization: an index with '
      'room for a second day, and the July 27 reflections moved underneath it. The '
      'published version, where the root page <em>is</em> the July 27 entry, stands '
      'unchanged at <a href="../">the journal root</a>.\n</div>')
    a('\n<div class="mast">')
    a('  <div class="kicker">A journal</div>')
    a("  <h1>The steward's journal</h1>")
    a('  <p class="prov">Todd Youngblood, Ventures and Operations Steward, RegenHub, LCA. '
      'Dictated notes, transcribed and lightly edited: the dictation repaired, the '
      'phrasing kept. Thinking, not record. Drafts, open to correction.</p>')
    a('</div>')

    a('\n<article class="day">')
    a('  <div class="dt">July 27, 2026 &middot; eighteen days before the launch</div>')
    a('  <h2><a href="2026-07-27/">Ten reflections</a></h2>')
    a('  <p class="dek">Craft against commerce, the moment we are in, who a third space is '
      'for, why Colorado, an account of the year, what computing was for, the wrong '
      'instrument, the door you can speak to, Hopper\'s oxen, and play.</p>')
    a(f'  <div class="stat">ten reflections &middot; {total:,} words &middot; about '
      f'{round(total/225)} minutes &middot; dictated 1:42 PM to 8:46 PM</div>')
    a('  <div class="themes">')
    for title, _dek, nums in GROUPS:
        links = ", ".join(f'<a href="2026-07-27/#{entries[n]["id"]}">{n}</a>' for n in nums)
        a(f'    <b>{html.escape(title)}</b> &middot; {links}<br>')
    a('  </div>')
    a('</article>')

    a('\n<footer>')
    a("  <span>The steward's journal &middot; RegenHub, LCA &middot; Boulder, Colorado</span>")
    a('  <span class="note">Nothing here is a governing document of the cooperative, and '
      'nothing here has been adopted by anyone. The governing documents live in '
      '<a href="https://techne.coop/commons/">the Commonplace Book</a>. These pages are '
      'unlisted and carry noindex; they are shared by link, for reading and for '
      'correction.</span>')
    a('</footer>')
    a(f'\n</div>\n<script>{MODE_JS}</script>\n</body>\n</html>')
    return "\n".join(p)


def main():
    src = SRC.read_text()
    entries, order = parse_entries(src)
    edits = apply_edits(entries)
    assert len(entries) == 10, f"expected 10 entries, parsed {len(entries)}"
    (HERE / "2026-07-27").mkdir(exist_ok=True)
    (HERE / "2026-07-27" / "index.html").write_text(build_day(entries, order, edits))
    (HERE / "index.html").write_text(build_index(entries, order))
    print(f"built {len(entries)} entries, {sum(words(entries[n]) for n in order):,} words, {len(edits)} edits")


if __name__ == "__main__":
    main()
