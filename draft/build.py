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

# Raw dictation, recovered verbatim from the session transcripts. Unpunctuated,
# unrepaired. Two were truncated by WhatsApp when the batch was forwarded.
DICTATION = {
    "I": ("1:42 PM", False, """I would like to record another voice note that enables me to articulate and contextualize more considerations for my role as the LCA Steward supporting ventures and operations at regen hub and techni so this consideration is that of what techna co-op could be as a soil and substrate for art for craft and for science as a cooperative that is distinct from a corporation which treats the work the craft and the outputs of Labor as merely commerce and not craft and thereby the bases the work the labor from an elevated form to a base form I believe that this container is unique as many incubators and accelerators for founders treat the founders work as an opportunity for commerce and profit which defines the end goal in north star of that work rather than craft where craft returns what some might call sacred relationship to the work that enables it to become what it could and should be in its highest purpose and not a lower or more base purpose which is commerce profit and Gain"""),
    "II": ("1:51 PM", False, """I want to record yet another voice note that continues to enable me to document and articulate my thoughts and reflections as the steward of the co-op for record-keeping purposes so the consideration now is the moment we find ourselves in I believe that the ancient Greeks had another language and terminology for this but I think it was Kairos where the moment needs to be considered for the right action and I think in 2026 in the state of AI especially in July 2026 we find ourselves at a time where knowledge workers and the sector of the economy that is dependent on their knowledge and intellectual capacities for labor find themselves at risk and now in 2026 offers us the opportunity very few populations are offered in their time which is a fundamental shift that could enable the cooperative and common control and operation of the means of production where in this articulation ai-enables a transition opportunity where digital infrastructure becomes a public good and balances the current over concentration of privately controlled platforms offering a more plural ecosystem that doesn't lock in participants and guests of the world wide Web so this point in time I consider Kairos as a moment speaking to us to embrace the means of production and to embrace the work that is ahead of us in governing and collectively benefiting from Commons of digital infrastructure held by a decentralized network of cooperatives organized and self-organized according to art craft and science each has intersectional fields"""),
    "III": ("2:04 PM", False, """this next voice note articulates a consideration of ownership of work similar and maybe complementary to previous voice note about the basing of Labor and craft by the corporate form this consideration also recognizes the corporate form and the inability of traditional firms to honor work as craft and honor the worker as a crafts person an artist or a scientist dependent on the field and this consideration casts Technic co-op as potentially a third space distinct from traditional corporate work where a number of populations and identities could find meaningful engagement within techni whether you're a student wanting to practice or play with new ideas maybe someone who's in between jobs who wants to stay relevant wants to learn or wants to teach or help educate or maybe your a mid-age professional who was laid off and is seeking to transition to another type of work but not yet considering retirement I think Technic could also be attracted to a retirement age class of population where it provides them a meaningful interface to pass down their practice their wisdom their inherited knowledge through the distinct lens of their identity and generation and history"""),
    "IV": ("3:18 PM", False, """this is yet another voice note and consideration I hold as Steward of the LCA this consideration is that of place and why I think Colorado is a legislative and policy frontier among the United States specifically in economic and cooperative law and it exists among siblings with it Wyoming in DAO law and South Dakota in trust law that makes Colorado a unique birthplace of the Technic co-op I think the LCA as a container that can build a right relationship with her invest members enables technique to be a meaningful Commons that can partner with capital but not be dependent on it"""),
    "V": ("3:26 PM", False, """for my next voice note and reflection I wanted to share about the job description and role responsibilities including scope of work that informed the title of ventures and operations Steward that emerged from my conversation with Kevin I will attach a statement of work following this voice note and I want to intersect the statement of work as developed in February and the feedback received mid workflow this summer to set context and background for the information system I present on launch day also called The Commons the role and scope emphasized legibility of The entity recognition of the work completed thus far and access to Capital all of which the common information system or the CIS as proposed on techne.coop/commons provides a road map for"""),
    "VI": ("4:17 PM", False, """want to share yet another voice note that is a long consideration of mine for the past year and that is the lineage of computing and information technology and how it has been drifted and captured by corporate structures for profit maximization and has lost its soul which was primarily conceptualized as a tool enabling humanity to address its most pressing challenges collectively through knowledge information sharing and systems building I think in the time of the eye ai and collective intelligence we have the ability to build real cybernetic systems and organizations that in a plus to transform corporate structures into responsive human and disease that address systemic risks harms and enables us to adopt a more humanist and mindful approach to change that is not systemically forced but rather locally organic"""),
    "VII": ("4:23 PM", True, """I want to share yet another voice note to articulate and communicate something that I know was identified in one of our early formation meetings but that is the errand value proposition of modern corporations as perceived through the resources events and agents language where modern corporations are primarily driven by shareholder primacy and reported on according to financial statements which serve as lagging indicators of value creation and Rea system inheriting cybernetic principles would enable first order value creation information and aggregation within the organization where traditional corporations rely on financial statements which are second order and byproducts of the first order value creative activities that would be notated in an activity journal and enables the more automated and auditable second order report generation as a secondary activity"""),
    "VIII": ("8:32 PM", True, """I'd like to articulate yet another voice note that considers the current limitations of human computer interaction and the opportunity of large models to enable a more natural language interface with a more robust feature set I think that natural language systems replacing or augmenting graphical user interfaces could enable more mass access to distinct and diverse types of compute and information services that would have otherwise through a GUI then inaccessible or potentially incomprehensible I propose that natural language interfaces either direct or agent mediated could be a key opportunity and value proposition for technique cooperative in the spirit of Wikipedia and Craigslist as information services infrastructure I want to open the question to the co"""),
    "IX": ("8:34 PM", False, """another voice note I find myself often considering a grandmother of computing Grace Hopper and her conceptualization of systems of computers and her articulation during a speech which has been recorded by a US military group but released publicly in which she talked about how systems of computers could be used to understand things like water shortages especially along and in the west and Colorado River"""),
    "X": ("8:46 PM", False, """another voice note reflecting on my role as Steward and the potential importance of play as we begin to define new systems for individual and collective self organizing I think play is a pre-requisite to cycles of feedback and learning important for growth and how a digital environment and supportive infrastructure could create the opportunity for play and practice across arts crafts and sciences"""),
}

NOTE_V = ("This one diverged furthest. The dictation names the two role documents and the "
          "three emphases; the reflection above was rewritten on 2026-07-28 after the May "
          "board thread arrived, and it now carries material the voice note never did.")


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
  details.dict .trunc{display:block; margin-top:10px; font:400 12px/1.6 var(--serif); font-style:italic; color:var(--faint)}

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
  <a href="../../">the journal root</a>. Nothing here is adopted, and the prose is
  identical to the published text: only the apparatus around it is new.
</div>"""


def build_day(entries, order):
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

        when, truncated, raw = DICTATION[n]
        a('  <details class="dict">')
        a(f'    <summary>the dictation, unrepaired &middot; {when}</summary>')
        a(f'    <div class="raw">{html.escape(raw)}')
        if truncated:
            a('      <span class="trunc">The forwarded transcript cut off here. The '
              'original voice note ran longer.</span>')
        if n == "V":
            a(f'      <span class="trunc">{html.escape(NOTE_V)}</span>')
        a('    </div>')
        a('  </details>')
        a('</article>')

    a('\n<footer>')
    a("  <span>The steward's journal &middot; RegenHub, LCA &middot; Boulder, Colorado "
      "&middot; dictated 2026-07-27</span>")
    a('  <span class="note">Thinking, not record. Nothing here is a governing document of '
      'the cooperative, and nothing here has been adopted by anyone. The governing '
      'documents live in <a href="https://techne.coop/commons/">the Commonplace Book</a>. '
      'This page is unlisted and carries noindex; it is shared by link, for reading and '
      'for correction.</span>')
    a('  <span class="fix"><b>Found something wrong?</b> Every reflection above opens to '
      'the dictation it came from, so you can check the edit against the words. '
      'Corrections, disagreements, and objections go to the steward directly, or to '
      '<a href="https://github.com/Techne-Co-op/steward-journal/issues">the journal\'s '
      'issues</a>. A correction here is a new entry, never a silent edit.</span>')
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
    assert len(entries) == 10, f"expected 10 entries, parsed {len(entries)}"
    (HERE / "2026-07-27").mkdir(exist_ok=True)
    (HERE / "2026-07-27" / "index.html").write_text(build_day(entries, order))
    (HERE / "index.html").write_text(build_index(entries, order))
    print(f"built {len(entries)} entries, {sum(words(entries[n]) for n in order):,} words")


if __name__ == "__main__":
    main()
