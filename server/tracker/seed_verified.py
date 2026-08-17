"""Hand-curated, high-confidence incidents where the money IS assignable.

These are the ones we can put a dollar on and defend on stream. Each carries an
explicit `amount_basis` naming the document or forensic analysis the number came
from, and each dollar is placed in the correct ledger:

  flow_to_trump  — dollars that demonstrably landed with Trump / family / their
                   entities. Preferred evidence: Trump's OWN federal financial
                   disclosure (OGE), which is a primary government document he
                   signed. You cannot call your own filing fake news.
  cost_to_public — taxpayer dollars committed / misdirected.
  deal_value     — context only. Never in the headline.

The Vulcan case is the model for why the ledgers are separate: $620M of public
money went to a COMPANY, and the Trump-family benefit is an equity stake of
undisclosed size. Booking $620M as "money Trump took" would be wrong and would
lose the argument. Booking it as $620M cost_to_public + a documented stake is
correct and unanswerable.

Run:  python -m tracker.seed_verified
"""
from __future__ import annotations
import json, re, sys
from . import db

SEED = [
    dict(
        slug="oge-2025-disclosure-memecoin-royalties",
        title="$635 million in $TRUMP memecoin royalties, per Trump's own federal disclosure",
        summary=(
            "Trump's 927-page annual financial disclosure for 2025, released by the "
            "U.S. Office of Government Ethics on June 30, 2026, reports more than "
            "$635 million in royalties from the $TRUMP memecoin. The coin was launched "
            "days before his inauguration; Trump Organization affiliates CIC Digital "
            "and Fight Fight Fight LLC control 80% of supply."),
        event_date="2026-06-30", category="crypto",
        actors=["Donald Trump", "CIC Digital", "Fight Fight Fight LLC"],
        flow_to_trump=635_000_000, is_estimated=0, confidence=98,
        amount_basis=("$635,000,000 — stated in Trump's own OGE annual financial "
                      "disclosure for calendar year 2025 (primary government document)."),
        citations=[
            ("https://www.oge.gov/Web/OGE.nsf/News%20Releases/B8B9EA45F5EB86EC85258E2600701B77?opendocument",
             "oge.gov", "U.S. Office of Government Ethics — 2025 annual disclosure release", 0),
            ("https://time.com/article/2026/07/01/trump-2025-financial-disclosure-crypto-world-liberty-financial/",
             "time.com", "Trump Earned Over $1 Billion From Crypto Ventures, New Filings Show", 3),
        ]),
    dict(
        slug="oge-2025-disclosure-wlf-token-sales",
        title="$799 million from World Liberty Financial token sales, per Trump's own federal disclosure",
        summary=(
            "The same 2025 OGE disclosure lists $799 million in token sales and other "
            "income from World Liberty Financial, the Trump-family crypto venture. "
            "Crypto was the single largest source of Trump's income in 2025, dwarfing "
            "real estate. WLF took investment from foreign-linked buyers including "
            "Justin Sun and UAE-backed entities while Trump set U.S. crypto policy."),
        event_date="2026-06-30", category="crypto",
        actors=["Donald Trump", "World Liberty Financial", "Justin Sun"],
        flow_to_trump=799_000_000, is_estimated=0, confidence=98,
        amount_basis=("$799,000,000 — stated in Trump's own OGE annual financial "
                      "disclosure for calendar year 2025 (primary government document)."),
        citations=[
            ("https://www.oge.gov/Web/OGE.nsf/News%20Releases/B8B9EA45F5EB86EC85258E2600701B77?opendocument",
             "oge.gov", "U.S. Office of Government Ethics — 2025 annual disclosure release", 0),
            ("https://www.cnbc.com/amp/2026/06/30/trump-financial-disclosure-released.html",
             "cnbc.com", "Trump's annual financial disclosure shows crypto income", 3),
            ("https://en.wikipedia.org/wiki/World_Liberty_Financial",
             "wikipedia.org", "World Liberty Financial — profits and ownership", 3),
        ]),
    dict(
        slug="memecoin-retail-investor-losses",
        title="Roughly 813,000 wallets lost about $2 billion trading $TRUMP while insiders took fees",
        summary=(
            "A forensic analysis commissioned by The New York Times found 813,294 "
            "wallets lost $2 billion trading the $TRUMP coin, while the president's "
            "company and partners profited about $100 million in trading fees in the "
            "first two weeks alone. For every $1 in fees the creators took, investors "
            "lost $20. Later analysis put cumulative retail losses at $3.81 billion."),
        event_date="2025-02-03", category="crypto",
        actors=["Donald Trump", "CIC Digital"],
        flow_to_trump=100_000_000, cost_to_public=0, deal_value=2_000_000_000,
        is_estimated=1, confidence=90,
        amount_basis=("$100M fees to Trump entities — Reuters, from three independent "
                      "blockchain-analytics firms (Chainalysis $94M, Merkle Science $86M, "
                      "third firm ~$100M). $2B booked as deal_value = retail investor "
                      "losses, NOT money Trump received."),
        citations=[
            ("https://www.reuters.com/markets/currencies/trumps-meme-coin-made-nearly-100-million-trading-fees-small-traders-lost-money-2025-02-03/",
             "reuters.com", "Trump's meme coin made nearly $100 million in trading fees", 3),
            ("https://en.wikipedia.org/wiki/$Trump",
             "wikipedia.org", "$Trump — NYT-commissioned forensic analysis", 3),
        ]),
    dict(
        slug="vulcan-elements-620m-pentagon-loan",
        title="$620 million Pentagon loan to Vulcan Elements after Trump Jr.'s firm took a stake",
        summary=(
            "ProPublica found Peter Navarro, the president's senior counselor for trade "
            "and manufacturing and a friend of Donald Trump Jr., intervened to secure a "
            "$620 million Pentagon loan to Vulcan Elements, a small North Carolina "
            "rare-earth startup — about three months after Trump Jr.'s venture capital "
            "firm took a stake of undisclosed size. Of dozens of companies the Pentagon "
            "was considering, Vulcan's was the only deal initiated by a top White House "
            "aide. A Pentagon official: 'The call came from the White House: We have to "
            "get this done.' Warren, Blumenthal, Hirono, Crow and Levin have demanded answers."),
        event_date="2026-06-03", category="contracts",
        actors=["Donald Trump Jr.", "Peter Navarro", "Vulcan Elements", "Department of Defense"],
        flow_to_trump=0, cost_to_public=620_000_000, deal_value=700_000_000,
        is_estimated=0, confidence=95,
        amount_basis=("$620,000,000 booked as cost_to_public — public money committed to "
                      "the company, confirmed by the Pentagon's own release (joint $700M "
                      "conditional loan commitment). flow_to_trump left at $0 ON PURPOSE: "
                      "Trump Jr.'s stake is real but of UNDISCLOSED size, so no dollar "
                      "figure can be honestly assigned to the family yet."),
        citations=[
            ("https://www.propublica.org/article/donald-trump-jr-vulcan-deal-white-house",
             "propublica.org", "The White House Intervened to Get a $620 Million Deal for a Company Tied to Donald Trump Jr.", 1),
            ("https://www.propublica.org/article/donald-trump-jr-vulcan-lawmakers-letter",
             "propublica.org", "Lawmakers Demand Answers After White House Intervened in $620M Deal", 1),
            ("https://www.war.gov/News/Releases/Release/Article/4339788/office-of-strategic-capital-agrees-to-joint-700m-conditional-loan-commitment-wi/",
             "war.gov", "Office of Strategic Capital — $700M conditional loan commitment", 0),
        ]),
    dict(
        slug="qatar-400m-jet",
        title="$400 million jet accepted from the government of Qatar",
        summary=(
            "Trump accepted a luxury jet from the Qatari government valued at roughly "
            "$400 million for use as Air Force One, despite warnings it violated the "
            "Constitution's Foreign Emoluments Clause, which bars officeholders from "
            "accepting gifts from foreign states without the consent of Congress."),
        event_date="2025-05-21", category="emoluments",
        actors=["Donald Trump", "Government of Qatar"],
        flow_to_trump=400_000_000, is_estimated=1, confidence=90,
        amount_basis=("$400,000,000 — widely reported valuation of the aircraft "
                      "(NPR). Booked to flow_to_trump as a thing of value transferred "
                      "from a foreign state for the president's use."),
        citations=[
            ("https://www.npr.org/2025/05/21/nx-s1-5406420/trump-accepts-qatar-plane-air-force-one",
             "npr.org", "Trump accepts Qatar plane for Air Force One", 3),
        ]),
    dict(
        slug="white-house-ballroom-taxpayer-half",
        title="Taxpayers to fund about half of the $600 million White House ballroom Trump said donors would pay for",
        summary=(
            "Records obtained by The Washington Post reveal a roughly $600 million "
            "estimate for Trump's White House ballroom project, with about half the "
            "cost falling to taxpayers — despite the president's earlier assurances "
            "that private donors would pay for the construction. Separately, a no-bid "
            "contract went to the ballroom's builder for a nearby Lafayette Park "
            "project, driving costs from $3.3M to over $17M."),
        event_date="2026-06-16", category="selfdeal",
        actors=["Donald Trump", "The White House"],
        cost_to_public=300_000_000, deal_value=600_000_000,
        is_estimated=1, confidence=85,
        amount_basis=("~$300,000,000 cost_to_public = about half of the $600M project "
                      "estimate in records obtained by the Washington Post. Full $600M "
                      "kept in deal_value as project scope."),
        citations=[
            ("https://www.washingtonpost.com/investigations/2026/06/16/records-reveal-600m-estimate-trumps-ballroom-project-with-half-taxpayers/",
             "washingtonpost.com", "Records reveal $600M estimate for Trump's ballroom, with half from taxpayers", 3),
            ("https://www.nytimes.com/2026/04/25/us/politics/lafayette-park-fountains-trump-contract.html",
             "nytimes.com", "Lafayette Park fountains no-bid contract", 3),
        ]),
    dict(
        slug="dhs-143m-ad-firm-formed-8-days-prior",
        title="$143 million DHS ad contract to a firm formed eight days before the deal",
        summary=(
            "The Department of Homeland Security awarded a $143 million advertising "
            "contract to a company that had been formed only eight days earlier."),
        event_date="2025-01-01", date_precision="year", category="contracts",
        actors=["Department of Homeland Security"],
        cost_to_public=143_000_000, is_estimated=1, confidence=60,
        amount_basis=("$143,000,000 carried over from the legacy list; cost_to_public "
                      "because it is a federal contract award. NEEDS a hard citation "
                      "before it can be promoted to verified."),
        status="unverified",
        citations=[]),
]


def run(con=None) -> dict:
    own = con is None
    con = con or db.connect()
    if own:
        db.init(con)
    added = updated = 0
    for s in SEED:
        s = dict(s)
        cits = s.pop("citations", [])
        s.setdefault("status", "verified")
        s.setdefault("date_precision", "day")
        s.setdefault("notes", "hand-curated seed; money assigned by ledger with basis")
        row = con.execute("SELECT id FROM incidents WHERE slug=?", (s["slug"],)).fetchone()
        if row:
            inc_id = row["id"]
            fields = {k: (json.dumps(v) if isinstance(v, list) else v)
                      for k, v in s.items() if k != "slug"}
            fields["updated_at"] = db.now()
            con.execute(f"UPDATE incidents SET {','.join(k+'=?' for k in fields)} WHERE id=?",
                        (*fields.values(), inc_id))
            updated += 1
        else:
            inc_id = db.upsert_incident(con, **s)
            added += 1
        for url, pub, title, tier in cits:
            db.add_citation(con, inc_id, url, publisher=pub, title=title, tier=tier,
                            published_at=s.get("event_date"))
    # retire legacy duplicates now superseded by curated records
    con.execute("""UPDATE incidents SET status='merged', merged_into=(
                     SELECT id FROM incidents WHERE slug='oge-2025-disclosure-memecoin-royalties')
                   WHERE status='unverified' AND legacy_id IS NOT NULL
                     AND (title LIKE '%TRUMP memecoin%' OR title LIKE '%MELANIA coin%')""")
    con.commit()
    return {"seeded": added, "updated": updated}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
    sys.exit(0)
