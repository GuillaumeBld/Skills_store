---
name: succession-bolivard-kb
description: "Access and work with the BOLIVARD family succession knowledge base (Martinique). Use when asked about the succession, the family tree, heirs, properties, or the hermes-succession bot. Trigger phrases: succession bolivard, héritage bolivard, arbre genealogique bolivard, hermes succession, coach succession papa, Vénérand, Pierre-François, Eléonore, Poirier rivière-pilote, SanDisk succession."
---

# Succession BOLIVARD — Knowledge Base Access

Private legal KB for the BOLIVARD family succession (Martinique, France). Jean-Marie BOLIVARD (son of Louis-Félix) is handling the succession of his grandfather Vénérand BOLIVARD's properties, specifically the "biens anciens" at Poirier, Rivière-Pilote.

## System Architecture — Two Agents, One KB

| Agent | Where | Model | User | KB location |
|-------|-------|-------|------|-------------|
| **Hermès** (`@HermesSuccession_bot`) | VPS1 (`/root/projects/hermes-succession/`) | Mistral AI | Guillaume | `kb_context.md` (built from GitHub wiki) |
| **Coach Succession Papa** | SanDisk Chicago Mac | GPT-5.3-codex | Jean-Marie (dad) | `/Volumes/SanDisk/Succession/knowledge-base/` |

Both bots share the same KB source. The GitHub repo is the source of truth.

## Source of Truth Chain

```
GEDCOM (arbre-genealogique-heritage-2026-04-17.ged)
    ↓ ground truth for ALL genealogical facts
GitHub repo (GuillaumeBld/succession-bolivard, PRIVATE)
    ↓ wiki + data files, verified against GEDCOM
SanDisk wiki (/Volumes/SanDisk/Succession/knowledge-base/)
    ↓ local copy, Chicago Mac
VPS1 kb_context.md (/root/projects/hermes-succession/kb_context.md)
    ↓ assembled from GitHub wiki, injected into Hermès bot
```

**Rule:** GEDCOM wins over everything. GitHub wins over local copies.

## Key File Locations

### GEDCOM (genealogy source of truth)
```
/Volumes/SanDisk/Succession/knowledge-base/raw/familiaux/arbre-genealogique-heritage-2026-04-17.ged
```
- 345,519 lines, 12,952 individuals, 3,529 families
- MyHeritage-enriched version of Jean-Marie's Geneatique 2004 tree
- Original 2013 tree (pre-enrichment, 504 individuals): `/Volumes/SanDisk/Cloud_Master/Downloads/MacMini/uu1e39_871883dc6911xg5f133e2r_C.ged`

### GitHub Repository (PRIVATE)
```
https://github.com/GuillaumeBld/succession-bolivard
```
Get token on VPS1: `gh auth token`
Clone: `git clone https://GuillaumeBld:$(gh auth token)@github.com/GuillaumeBld/succession-bolivard.git`

### Wiki Files (on SanDisk Chicago Mac or cloned from GitHub)
```
/Volumes/SanDisk/Succession/knowledge-base/wiki/
├── arbre-genealogique.md   # Family tree — MOST IMPORTANT
├── heritiers.md            # All heirs with legal status
├── blockers.md             # 20 blockers tracking
├── questions-ouvertes.md   # Open questions (Q-NEW-1 to Q-NEW-4)
├── biens-immobiliers.md    # Real estate
├── droits-succession.md    # French succession law
├── cas-poirier.md          # Poirier case (main one)
├── cas-bernard.md          # Bernard case
├── cas-sainte-luce.md      # Sainte-Luce case
├── succession-1-pere.md    # Jean-Marie's father's succession
├── succession-2-tante.md   # Aunt's succession
├── succession-3-biens-anciens.md  # Old properties (Vénérand's)
├── checklist-actions.md    # Action checklist
├── planning.md             # Timeline
└── contacts-cles.md        # Key contacts
```

### Data Files
```
/Volumes/SanDisk/Succession/knowledge-base/data/
├── heritiers.csv           # All heirs as CSV
├── biens.csv               # All properties
├── timeline.csv            # Key dates
├── genealogy.yaml          # Family structure YAML
└── raw-entities-resolved.yaml
```

### VPS1 Bot
```
/root/projects/hermes-succession/
├── hermes_bot.py           # Telegram bot (Mistral AI backend)
├── kb_context.md           # Assembled KB (rebuild after each wiki update)
└── .env                    # Credentials (gitignored)
```
Service: `systemctl status hermes-succession.service`
Restart: `systemctl restart hermes-succession.service`

## Family Tree — Key Facts (GEDCOM-verified)

### Vénérand BOLIVARD (@I23@)
- Born: 4 Jan 1884, Rivière-Pilote — Died: 4 Jan 1977, Rivière-Pilote (age 93)
- Occupation: Cultivateur, Charpentier de marine, quartier Poirier
- Two unions → 9 legitimate children

### Union 1 — × Chlotilde-Etiénise CUTI (@I27@) [Family @F34@]
| ID | Name | Born | Died | Notes |
|----|------|------|------|-------|
| @I33@ | Eléonore BOLIVARD | 16/02/1914 Rivière-Pilote | 25/03/1985 Lamentin | × Norbert Maurille DIAMIN — aucun enfant (GEDCOM F500001 sans CHIL) |
| @I28@ | Juliette Vénérande BOLIVARD | 12/04/1916 | † Sainte-Luce | |
| @I29@ | Gabrielle Emma BOLIVARD | 19/04/1919 | | |
| @I30@ | Emérenthe BOLIVARD | 18/10/1921 | | Orthographe exacte: Emérenthe (avec th) |
| @I31@ | Delphine Romule BOLIVARD | 30/11/1923 | vivante? | Sous curatelle depuis 22/11/2022 |

### Union 2 — × Etienne Blanche Julie BERNARD (@I24@) [Family @F33@, mariés 3 fév 1927]
| ID | Name | Born | Died | Notes |
|----|------|------|------|-------|
| @I2@ | Agnan Louis-Félix BOLIVARD | 17/11/1927 | † Le François | Père de Jean-Marie |
| @I25@ | Auguste Paul Vénérand BOLIVARD | 07/10/1929 | avant 2012 | Décédé sans héritiers — non inclus acte notarial |
| @I26@ | Laurette Raphaëlle BOLIVARD | 10/12/1932 | | |
| @I32@ | Pierre-François BOLIVARD | 01/02/1934 Rivière-Pilote | 08/03/2009 CH Lamentin | × Liette BUSSANT (†12/08/2018) → 5 enfants héritiers actifs |

### Pierre-François's Children (HEIRS ACTIFS — dossier notaire à compléter)
| Name | Born | Lieu |
|------|------|------|
| Thury BOLIVARD | 15/07/1974 | Marin |
| Ariane BOLIVARD | 18/05/1977 | Fort-de-France |
| Jean-François BOLIVARD | 26/12/1978 | Fort-de-France |
| Lunise BOLIVARD | 07/02/1981 | Lamentin |
| Julie BOLIVARD | 26/12/1987 | Lamentin |

**Liette BUSSANT** (épouse de Pierre-François): née 02/05/1954 Rivière-Pilote, décédée 12/08/2018 — ses droits transmis aux 5 enfants.

### Key GEDCOM Warnings
- F500271 = famille vide (Vénérand HUSB uniquement, pas d'enfants) — artefact MyHeritage Smart Match mars 2020
- Blanche BERNARD avait un enfant pré-conjugal: Amantine-Béatrice BERNARD (×Joseph COQ, née 11/07/1925) — PAS un enfant de Vénérand
- @I445@ Eléonore Zéli BOLIVARD = personne différente (mère: Césarine Joséphine BOLIVARD née 1902) — pas de droits dans cette succession

## GEDCOM Query Patterns

```bash
# SSH to Chicago Mac (key: ~/.ssh/macmini_key on VPS1)
SSH="ssh -o BatchMode=yes guillaumebld@100.78.183.61"
GED="/Volumes/SanDisk/Succession/knowledge-base/raw/familiaux/arbre-genealogique-heritage-2026-04-17.ged"

# Find individual by name
$SSH "grep -i 'bolivard' $GED | grep NAME | head -20"

# Get full record for known ID
$SSH "grep -A 40 '^0 @I32@ INDI' $GED"

# Get family record
$SSH "grep -A 20 '^0 @F33@ FAM' $GED"

# Find who has FAMC pointing to a family (children of that family)
$SSH "grep -B 5 'FAMC @F33@' $GED | grep NAME"

# Find all families a person is spouse in
$SSH "grep -A 3 '^0 @I23@ INDI' $GED | grep FAMS"
```

## KB Update Workflow

After any correction:

```bash
# 1. SSH to Chicago and edit wiki files
ssh -o BatchMode=yes guillaumebld@100.78.183.61
# ... edit files in /Volumes/SanDisk/Succession/knowledge-base/wiki/

# 2. Commit and push to GitHub
cd /Volumes/SanDisk/Succession/knowledge-base
git add -A
git commit -m "Description de la correction"
TOKEN=$(ssh -o BatchMode=yes root@100.88.134.79 "gh auth token")
git remote set-url origin https://GuillaumeBld:${TOKEN}@github.com/GuillaumeBld/succession-bolivard.git
git push origin main

# 3. Rebuild VPS1 kb_context.md (run ON VPS1)
GH_TOKEN=$(gh auth token)
git clone https://GuillaumeBld:${GH_TOKEN}@github.com/GuillaumeBld/succession-bolivard.git /tmp/succession-kb-tmp
# ... assemble kb_context.md from wiki files
# ... then:
systemctl restart hermes-succession.service
rm -rf /tmp/succession-kb-tmp
```

## Key Open Questions (as of 2026-06-24)

| ID | Priorité | Question |
|----|----------|----------|
| Q-NEW-1 | P2 MODÉRÉ | Confirmer absence enfants Eléonore DIAMIN (acte décès ou mairie Lamentin) |
| Q-NEW-2 | P2 | Discordance date naissance Pierre-François: 1934 (GEDCOM) vs 1935 (source civile) |
| Q-NEW-3 | P1 IMPORTANT | Coordonnées + documents (CNI/RIB/questionnaire) des 5 enfants Pierre-François |
| Q-NEW-4 | P3 INFO | Famille vide F500271 — artefact MyHeritage, aucune action succession |

## Legal Context (French succession law)

- **Droit de représentation** (art. 751 Code civil): enfants de Pierre-François représentent leur père décédé → héritent de sa part (1/8 Poirier ÷ 5)
- **Indivision**: Poirier n'a jamais été liquidé → tous co-indivisaires doivent signer ou renoncer
- **Trentenaire**: prescription 30 ans — délais à surveiller
- **Curatelle Delphine**: elle ne peut pas signer seule — curateur à identifier
- Notaire dossier réf: 20029499 (Me Californie, Fort-de-France)
