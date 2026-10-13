"""Automatic STE metrics for one markdown reply, or for every output.md under a runs folder.

Prose only: fenced code, inline code, URLs, table rows and headings are removed first.
Usage:
  metrics.py FILE.md              print metrics for one file as JSON
  metrics.py RUNS_DIR OUT.csv     walk RUNS_DIR/**/output.md and write one CSV row per run
"""
import csv
import json
import re
import sys
from pathlib import Path

import spacy
import textstat

NLP = spacy.load("en_core_web_sm")

HEDGES = {"might", "may", "could", "perhaps", "possibly", "probably", "likely", "unlikely",
          "arguably", "somewhat", "generally", "typically", "usually", "often"}
EM_DASH = "—"


def to_prose(md: str) -> list[str]:
    """Return prose blocks (paragraphs and list items) with code and markup removed."""
    md = re.sub(r"```.*?```", " ", md, flags=re.S)
    md = re.sub(r"~~~.*?~~~", " ", md, flags=re.S)
    md = re.sub(r"`[^`\n]+`", "CODE", md)
    md = re.sub(r"https?://\S+", "URL", md)
    blocks, cur = [], []
    for line in md.splitlines():
        s = line.strip()
        if not s or s.startswith("|") or s.startswith("#") or re.fullmatch(r"[-*_]{3,}", s):
            if cur:
                blocks.append(" ".join(cur))
                cur = []
            continue
        item = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if item:
            if cur:
                blocks.append(" ".join(cur))
            cur = [item.group(3)]
        else:
            cur.append(s)
    if cur:
        blocks.append(" ".join(cur))
    clean = []
    for b in blocks:
        b = re.sub(r"\*\*|__|\*|_", "", b)
        b = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b)
        b = b.strip()
        if re.search(r"[A-Za-z]", b):
            clean.append(b)
    return clean


def words(span) -> list:
    return [t for t in span if t.is_alpha or t.like_num or t.text == "CODE"]


def analyze(md: str) -> dict:
    blocks = to_prose(md)
    sent_lens, passive, ing, clusters, long_paras = [], 0, 0, 0, 0
    hedges, total_words = 0, 0
    perfect, progressive, may_should = 0, 0, 0
    for block in blocks:
        doc = NLP(block)
        sents = list(doc.sents)
        if len(sents) > 6:
            long_paras += 1
        for s in sents:
            w = words(s)
            if not w:
                continue
            sent_lens.append(len(w))
            if any(t.dep_ in ("nsubjpass", "auxpass", "csubjpass") for t in s):
                passive += 1
        for t in doc:
            if t.tag_ == "VBG" and t.text != "CODE":
                ing += 1
            if t.lower_ in HEDGES:
                hedges += 1
            if t.lower_ in ("may", "should"):
                may_should += 1
            if t.tag_ == "VBN" and any(c.dep_ == "aux" and c.lemma_ == "have" for c in t.children):
                perfect += 1
            if t.tag_ == "VBG" and any(c.dep_ == "aux" and c.lemma_ == "be" for c in t.children):
                progressive += 1
        total_words += len(words(doc))
        run = 0
        for t in doc:
            if t.pos_ in ("NOUN", "PROPN") and t.text not in ("CODE", "URL"):
                run += 1
            else:
                if run > 3:
                    clusters += 1
                run = 0
        if run > 3:
            clusters += 1
    n = len(sent_lens) or 1
    prose = " ".join(blocks)
    sorted_lens = sorted(sent_lens) or [0]
    return {
        "chars_raw": len(md),
        "words_prose": total_words,
        "sentences": len(sent_lens),
        "wps_mean": round(sum(sent_lens) / n, 2),
        "wps_p90": sorted_lens[max(0, -(-9 * len(sorted_lens) // 10) - 1)],
        "wps_max": max(sorted_lens),
        "pct_over_20": round(100 * sum(l > 20 for l in sent_lens) / n, 1),
        "pct_over_25": round(100 * sum(l > 25 for l in sent_lens) / n, 1),
        "pct_passive": round(100 * passive / n, 1),
        "ing_per_100w": round(100 * ing / (total_words or 1), 2),
        "noun_clusters_gt3": clusters,
        "paras_gt6_sents": long_paras,
        "hedges_per_100w": round(100 * hedges / (total_words or 1), 2),
        "em_dashes": md.count(EM_DASH),
        "semicolons": prose.count(";"),
        "contractions": len(re.findall(r"\w+(?:n't|'re|'ve|'ll|'m|'d)", prose.replace("’", "'"))),
        "perfect_tense": perfect,
        "progressive_tense": progressive,
        "may_should_per_100w": round(100 * may_should / (total_words or 1), 2),
        "flesch_ease": round(textstat.flesch_reading_ease(prose), 1) if prose else None,
        "fk_grade": round(textstat.flesch_kincaid_grade(prose), 1) if prose else None,
    }


def main() -> None:
    target = Path(sys.argv[1])
    if target.is_file():
        print(json.dumps(analyze(target.read_text()), indent=2))
        return
    rows = []
    for out in sorted(target.rglob("output.md")):
        meta_path = out.with_name("meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        row = {k: meta.get(k) for k in ("model", "arm", "task", "type", "rep")}
        row["path"] = str(out.relative_to(target))
        row.update(analyze(out.read_text()))
        rows.append(row)
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {sys.argv[2]}")


if __name__ == "__main__":
    main()
