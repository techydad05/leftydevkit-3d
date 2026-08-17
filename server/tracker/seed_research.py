"""Research-driven additions (2026-08-16) — new verified incidents + legacy promotions.

Ledger discipline (defensible on stream):
  flow_to_trump   — money that demonstrably landed with Trump / family / their entities.
  cost_to_public  — taxpayer money actually committed / moved.
  deal_value      — context only (contract values, proposed/blocked funds, campaign
                    donations that did NOT go to Trump personally). NEVER in headline.

KEY PRINCIPLE this pass: political-campaign donations (super PAC, inaugural) are NOT
flow_to_trump — that money did not land in Trump's pocket. They are pay-to-play context
(deal_value). Only money that went to Trump/family/entities counts toward flow_to_trump.
Proposed-but-blocked money (weaponization fund) is deal_value, not cost_to_public.

Run:  python -m tracker.seed_research
"""
from __future__ import annotations
import json, sys, datetime
from . import db

TODAY = datetime.date.today().isoformat()

# New verified incidents (money actually landed / taxpayer money moved)
ADD = [
    dict(
        slug="wlf-tahnoon-187m-installment",
        title="$187 million of a UAE prince's World Liberty Financial investment wired to Trump-family entities",
        summary=(
            "Documents reported by the Wall Street Journal show $187 million was wired directly to "
            "Trump-family entities DT Marks DEFI LLC and DT Marks SC LLC as part of the $250 million "
            "upfront payment for Arul Investment 1 (backed by Sheikh Tahnoon bin Zayed Al Nahyan, Abu "
            "Dhabi royal and UAE national-security adviser) buying a 49% stake in World Liberty Financial. "
            "The $500M deal was signed Jan 16, 2025, four days before the inauguration. Within months the "
            "administration pledged 500,000 advanced AI chips to the UAE."),
        event_date="2025-01-16", category="crypto",
        actors=["Donald Trump", "Sheikh Tahnoon bin Zayed", "World Liberty Financial", "United Arab Emirates"],
        flow_to_trump=187_000_000, is_estimated=0, confidence=90,
        amount_basis=("$187,000,000 — WSJ per company documents: 'the buyer paid half the amount upfront, "
                      "with $187 million transferred directly' to DT Marks DEFI LLC and DT Marks SC LLC."),
        legacy_id=19,
        citations=[
            ("https://www.wsj.com/politics/policy/spy-sheikh-secret-stake-trump-crypto-tahnoon-ea4d97e8",
             "wsj.com", "Spy Sheikh Bought Secret Stake in Trump Company", 3),
            ("https://www.cnbc.com/2026/02/01/spy-sheikh-stake-trump-crypto.html",
             "cnbc.com", "Sheikh Tahnoon secret stake in Trump crypto", 3),
        ]),
    dict(
        slug="melania-amazon-10-7m-fee",
        title="$10.71 million Amazon paid for Melania Trump documentary, per Trump's federal disclosure",
        summary=(
            "Amazon MGM paid $40 million for the rights to a documentary about Melania Trump; the "
            "licensing fee paid to Melania — $10.71 million — is listed as her income on Trump's 2025 "
            "federal financial disclosure, along with $521,161 for her memoir and ~$6M in NFTs. The deal "
            "was widely criticized as Amazon currying favor with the White House."),
        event_date="2025-09-05", category="selfdeal",
        actors=["Melania Trump", "Amazon MGM"],
        flow_to_trump=10_710_000, is_estimated=0, confidence=92,
        amount_basis=("$10,710,000 — Melania's licensing fee listed on Trump's 2025 OGE federal financial "
                      "disclosure (Variety, Jul 1 2026). Full $40M rights price in deal_value."),
        legacy_id=44,
        citations=[
            ("https://www.variety.com/2026/film/news/trump-melania-documentary-fee-1236150000",
             "variety.com", "Trumps received $10.7 million fee for Amazon 'Melania' documentary", 3),
            ("https://www.theguardian.com/us-news/2025/jun/16/trump-conflict-of-interest",
             "theguardian.com", "Amazon's $40M Melania documentary deal raises conflict questions", 3),
        ]),
    dict(
        slug="meta-25m-trump-settlement",
        title="$25 million Meta paid Trump to settle his account-suspension lawsuit",
        summary=(
            "Meta agreed to pay $25 million to settle Trump's lawsuit over his account suspension after "
            "the Jan. 6, 2021 attack, in the same period Zuckerberg courted the incoming administration "
            "with an inaugural donation and White House meetings."),
        event_date="2025-01-29", category="selfdeal",
        actors=["Donald Trump", "Meta", "Mark Zuckerberg"],
        flow_to_trump=25_000_000, is_estimated=0, confidence=90,
        amount_basis=("$25,000,000 — settlement amount confirmed by Meta and reported by NPR/WSJ/ABC."),
        citations=[
            ("https://www.npr.org/2025/01/29/nx-s1-5279570/meta-trump-settlement-facebook-instagram-suspensions",
             "npr.org", "Meta to pay Trump $25 million to settle suit", 3),
            ("https://www.wsj.com/us-news/law/trump-signs-agreement-calling-for-meta-to-pay-25-million-to-settle-suit-6f734c8c",
             "wsj.com", "Trump signs agreement for Meta to pay $25 million", 3),
        ]),
    dict(
        slug="reliance-10m-development-fee",
        title="$10 million Reliance paid the Trump Organization for a non-existent Mumbai project, then got a $300B refinery win",
        summary=(
            "ProPublica and CREW reported Reliance Industries paid the Trump Organization $10 million in "
            "2024 as a 'development fee' for a Mumbai project that never happened. The administration "
            "later facilitated a massive America First Refining project in Brownsville, Texas benefiting "
            "the same family, plus oil-license/sanctions waivers."),
        event_date="2025-01-20", date_precision="year", category="contracts",
        actors=["Reliance Industries", "Trump Organization", "Mukesh Ambani"],
        flow_to_trump=10_000_000, deal_value=300_000_000_000, is_estimated=0, confidence=88,
        amount_basis=("$10,000,000 flow_to_trump — documented 'development fee' payment to Trump Org "
                      "(CREW/ProPublica). $300B refinery booked deal_value as context."),
        citations=[
            ("https://www.citizensforethics.org/reports-investigations/crew-investigations/indias-reliance-industries-paid-trump-10-million-before-he-took-office-it-keeps-getting-wins-from-trump/",
             "citizensforethics.org", "Reliance paid Trump $10M before wins", 1),
            ("https://www.propublica.org/article/trump-ambani-reliance-industries-america-first-refining-texas",
             "propublica.org", "Ambani family secured Trump policy wins", 1),
        ]),
    dict(
        slug="dhs-220m-no-bid-border-ad-campaign",
        title="$220 million in no-bid DHS border-ad contracts to newly formed, donor-tied firms",
        summary=(
            "A $220 million DHS 'border ad' campaign was awarded without competitive bidding to firms "
            "tied to the Kristi Noem circle — $143 million to Safe America Media (incorporated ~8 days "
            "before award) and $77 million to People Who Think — with ties to a Noem-aligned firm as an "
            "undisclosed subcontractor. Senate Democrats launched an inquiry."),
        event_date="2025-10-02", date_precision="year", category="contracts",
        actors=["Department of Homeland Security", "Safe America Media", "Kristi Noem"],
        cost_to_public=220_000_000, is_estimated=1, confidence=75,
        amount_basis=("$220,000,000 cost_to_public — total no-bid campaign spend ($143M Safe America "
                      "Media + $77M People Who Think), per ProPublica."),
        legacy_id=11,
        citations=[
            ("https://www.propublica.org/article/kristi-noem-dhs-ad-campaign-strategy-group",
             "propublica.org", "Kristi Noem-tied firm secretly got piece of $220 million DHS campaign", 1),
            ("https://www.notus.org/democrats/senate-democrats-launch-investigation-ad-campaign-kristi-noem",
             "notus.org", "Senate Dems launch investigation into $143M DHS ad contract", 3),
        ]),
    dict(
        slug="lincoln-reflecting-pool-14-7m",
        title="$14.7 million no-bid Lincoln Memorial Reflecting Pool contract to a firm tied to Trump's golf club",
        summary=(
            "The Trump administration awarded a no-bid contract to Atlantic Industrial Coatings to repair "
            "and repaint the Lincoln Memorial Reflecting Pool. President Trump reportedly chose the "
            "company because it had done pool work at his Trump National Golf Club in Virginia. The sum "
            "was more than seven times the initial projected cost. House Oversight Democrats demanded "
            "answers."),
        event_date="2026-05-19", category="contracts",
        actors=["Donald Trump", "Atlantic Industrial Coatings", "National Park Service"],
        cost_to_public=14_700_000, is_estimated=0, confidence=85,
        amount_basis=("$14,700,000 cost_to_public — no-bid federal contract award reported by The Hill/NYT."),
        citations=[
            ("https://www.nytimes.com/2026/05/19/us/politics/reflecting-pool-trump-schutzenhofer.html",
             "nytimes.com", "Trump chose company for reflecting pool work", 3),
            ("https://thehill.com/policy/energy-environment/5930934-reflecting-pool-algae-lincoln-memorial/",
             "thehill.com", "Atlantic Industrial Coatings paid $14.7M for reflecting pool", 3),
        ]),
    dict(
        slug="usaid-15m-vought-security-detail",
        title="$15 million in USAID funds diverted to fund budget director Vought's security detail",
        summary=(
            "Reuters documents showed the White House used USAID operating funds to cover security for "
            "OMB Director Russell Vought — $1.6M in a Sept 2025 agreement plus $13.5M budgeted for the "
            "U.S. Marshals detail through end of 2026 — redirecting foreign-aid money to protect a "
            "domestic executive official."),
        event_date="2026-02-13", category="oversight",
        actors=["Russell Vought", "USAID", "White House"],
        cost_to_public=15_000_000, is_estimated=0, confidence=85,
        amount_basis=("$15,000,000 cost_to_public — Reuters per documents ($1.6M + $13.5M budgeted)."),
        legacy_id=62,
        citations=[
            ("https://www.reuters.com/world/us/white-house-uses-usaid-funds-budget-director-voughts-security-documents-show-2026-02-13/",
             "reuters.com", "White House used USAID funds for Vought's security detail", 3),
            ("https://krishnamoorthi.house.gov/sites/evo-subsites/krishnamoorthi.house.gov/files/evo-media-document/2026.02.25-krishnamoorthi-vought-usaid-letter.pdf",
             "krishnamoorthi.house.gov", "Rep. Krishnamoorthi letter to Vought re: USAID funds", 0),
        ]),
]

# Pay-to-play context rows (deal_value ONLY — donation money did not go to Trump personally,
# or proposed/blocked money). These document corruption but must NOT inflate the headline.
CONTEXT = [
    dict(
        slug="reynolds-5m-flavored-vapes",
        title="$5 million Reynolds American super PAC donation a week before FDA cleared flavored vapes",
        event_date="2026-05-20", category="other",
        actors=["Reynolds American", "FDA"],
        deal_value=5_000_000, confidence=85,
        amount_basis="Context: $5M super PAC donation, not flow_to_trump (did not go to Trump personally).",
        citations=[("https://www.nytimes.com/2026/05/20/us/politics/donation-big-tobacco-vaping.html",
                    "nytimes.com", "Big tobacco donation before flavored-vape guidance", 3)]),
    dict(
        slug="nursing-home-4-8m-staffing-rule",
        title="$4.8 million nursing-home executives gave to Trump's super PAC a month before staffing rule was dropped",
        event_date="2026-01-27", category="other",
        actors=["nursing home executives", "CMS"],
        deal_value=4_800_000, confidence=85,
        amount_basis="Context: $4.8M donation to super PAC (not flow_to_trump).",
        citations=[("https://www.nytimes.com/2026/01/27/us/politics/after-donations-trump-administration-revoked-rule-requiring-more-nursing-home-staff.html",
                    "nytimes.com", "Nursing-home donations before staffing rule dropped", 3)]),
    dict(
        slug="weaponization-fund-1-776b",
        title="$1.776 billion proposed taxpayer fund to reimburse 'unjustly prosecuted' incl. Jan. 6 rioters (blocked in court)",
        event_date="2026-05-20", category="oversight",
        actors=["Donald Trump", "IRS", "U.S. Treasury"],
        deal_value=1_776_000_000, is_estimated=1, confidence=80,
        amount_basis=("Context ONLY: proposed, never paid, blocked by federal judge Jul 13 2026. "
                      "NOT booked cost_to_public."),
        citations=[
            ("https://www.nytimes.com/2026/05/20/us/politics/trump-fund-presidents-self-dealing.html",
             "nytimes.com", "Trump fund and presidential self-dealing", 3),
            ("https://www.theguardian.com/us-news/2026/jul/13/trump-irs-ruling-judge-kathleen-williams",
             "theguardian.com", "Judge blocks Trump 'unjust prosecution' fund", 3)]),
    dict(
        slug="tiktok-400m-beautification",
        title="$400 million TikTok settlement eyed to fund Trump's D.C. 'beautification' projects",
        event_date="2026-05-08", category="selfdeal",
        actors=["TikTok", "Department of Justice"],
        deal_value=400_000_000, is_estimated=1, confidence=75,
        amount_basis=("Context: proposed settlement over child-privacy violations; discretionary use "
                      "earmarked for administration 'beautification' projects. Distinct from the $10B app fee."),
        citations=[
            ("https://abcnews.com/US/trump-administration-eyeing-400m-settlement-tiktok-dc-beautification/story?id=132707914",
             "abcnews.com", "Trump admin eyeing $400M TikTok settlement for D.C. beautification", 3),
            ("https://www.reuters.com/legal/government/us-nears-400-million-settlement-with-tiktok-child-privacy-violations-abc-news-2026-05-08/",
             "reuters.com", "US nears $400M settlement with TikTok", 3)]),
    dict(
        slug="palantir-10b-army-contract",
        title="$10 billion Army contract to Palantir, whose donors backed GOP midterm efforts",
        event_date="2025-07-31", category="contracts",
        actors=["Palantir", "Peter Thiel", "U.S. Army"],
        deal_value=10_000_000_000, is_estimated=1, confidence=80,
        amount_basis=("Context: $10B Army contract; Thiel donated $850K to GOP. deal_value only."),
        citations=[("https://www.washingtonpost.com/technology/2025/07/31/palantir-army-contract-10bn/",
                    "washingtonpost.com", "Palantir wins $10B Army contract", 3)]),
    dict(
        slug="dell-9-7b-pentagon-contract",
        title="$9.7 billion Pentagon contract to Dell after Trump bought up to $5M in Dell stock",
        event_date="2026-05-27", category="contracts",
        actors=["Dell", "Donald Trump", "Pentagon"],
        flow_to_trump=0, deal_value=9_700_000_000, is_estimated=1, confidence=80,
        amount_basis=("Context: $9.7B contract; Trump's Dell holdings were up to $5M (undisclosed profit "
                      "size) — NOT booked as flow_to_trump because portfolio gain is unquantified."),
        citations=[("https://www.nytimes.com/2026/05/28/us/politics/trump-dell-stock-purchases.html",
                    "nytimes.com", "Pentagon Dell contract after Trump bought Dell shares", 3)]),
    dict(
        slug="geo-group-1b-detention-contract",
        title="~$1 billion GEO Group ICE detention contract after ~$2.8M in donations",
        event_date="2025-02-27", category="contracts",
        actors=["GEO Group", "ICE"],
        deal_value=1_000_000_000, is_estimated=1, confidence=78,
        amount_basis=("Context: 15-yr, ~$1B (ACLU-NJ) 1,000-bed Newark ICE contract; GEO gave ~$2.8M to "
                      "Trump efforts. deal_value only."),
        citations=[
            ("https://www.aclu-nj.org/press-releases/aclu-nj-statement-ice-contracting-delaney-hall-immigration-detention/",
             "aclu-nj.org", "ACLU-NJ statement on Delaney Hall ICE contract", 3),
            ("https://www.thecity.nyc/2025/02/27/ice-immigrant-detention-newark-geo-group/",
             "thecity.nyc", "ICE detention Newark GEO Group", 3)]),
]


def run(con=None) -> dict:
    own = con is None
    con = con or db.connect()
    if own:
        db.init(con)
    added = updated = 0

    for s in ADD + CONTEXT:
        s = dict(s)
        cits = s.pop("citations", [])
        s.setdefault("status", "verified")
        s.setdefault("date_precision", "day")
        s.setdefault("notes", "research pass 2026-08-16 (Issue One / Reuters / CREW / ProPublica / NYT)")
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

    # Retire the legacy rows we just promoted into verified duplicates, so nothing double-counts.
    for lid in [s.get("legacy_id") for s in ADD if s.get("legacy_id")]:
        if not lid:
            continue
        # find the legacy row's new canonical incident
        src = con.execute(
            "SELECT id FROM incidents WHERE slug=?",
            (next(s["slug"] for s in ADD if s.get("legacy_id") == lid),)).fetchone()
        if src:
            con.execute(
                "UPDATE incidents SET status='merged', merged_into=?, notes=COALESCE(notes,'')||' ; promoted to verified research incident' "
                "WHERE id=? AND status='unverified' AND merged_into IS NULL",
                (src["id"], lid))
    con.commit()
    return {"added": added, "updated": updated}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
    sys.exit(0)
