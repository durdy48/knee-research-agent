# Patient Profile

Your personal context. KRA uses it **only to highlight relevance** — what changed that
matters for *your* case. It never changes a scientific conclusion (Golden Rule 3) and never
prescribes (Golden Rule 5).

Edit `profile.json`. It has two kinds of data (per the design):

- **Estables** (`patient`) — age, sex, injury history, surgeries, diagnoses.
- **Variables** (`variables`) — pain, weight, strength, activity frequency, current
  treatments, last MRI, and an `updated` date. These change over time, so KRA evolves with
  you.

Your goals go under `goals`. Nothing here is filled by KRA — it is yours to complete, and it
stays local. The Personal Insight Engine reads it to produce the monthly
"¿Ha cambiado algo para mí?" view (`reports/YYYY-MM-insights.md`).
