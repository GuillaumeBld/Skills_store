---
name: sop-runbook-writer
description: "Rédige des SOP (procédures opératoires normalisées) et des runbooks opérationnels structurés, prêts à présenter (management) ou à exécuter (équipe). À utiliser quand l'utilisateur demande une SOP, un runbook, une procédure de processus, une documentation opérationnelle pas-à-pas, un mode opératoire, ou la documentation d'un processus métier/technique récurrent. Trigger phrases: 'écris une SOP', 'crée un runbook', 'documente ce processus', 'procédure opératoire', 'mode opératoire', 'standard operating procedure', 'operational runbook'."
license: Proprietary
---

# SOP & Runbook Writer

Produit des documents de processus rigoureux : **SOP** (opérations normales/routinières) et **runbooks** (situations anormales / incidents). Sortie destinée soit au management (présentation), soit à l'exécution (équipe).

## 1. Choisir le bon format (décider d'abord)

| Besoin du lecteur | Format | Focus |
|---|---|---|
| Exécuter une tâche routinière, étapes exactes | **SOP** | opérations *normales*, reproductibilité |
| Réagir quand quelque chose casse/dégrade | **Runbook** | situations *anormales*, diagnostic + remédiation |
| Guidage par scénarios + principes + procédures liées | Playbook | enveloppe de plus haut niveau |

Règle : si le processus est *routinier* → SOP (avec une **annexe dépannage** courte de type runbook). Si le déclencheur est *un incident* → runbook.

## 2. Structure d'une SOP

Sections obligatoires (dans cet ordre) :

1. **En-tête / métadonnées** — Titre, ID/numéro, version, date, auteur, validé par, prochaine revue.
2. **Objet (Purpose)** — pourquoi cette SOP existe, en 1–2 phrases.
3. **Portée (Scope)** — ce qui est couvert / explicitement exclu.
4. **Rôles & responsabilités** — qui fait quoi (table : rôle → responsabilité).
5. **Définitions & prérequis** — termes, accès, licences, outils requis avant de commencer.
6. **Déclencheur (Trigger)** — quand/comment la procédure démarre (événement, fréquence).
7. **Procédure** — étapes **numérotées**, une action par étape, à l'impératif. Utiliser RFC 2119 :
   - **DOIT** (MUST) = obligatoire ; **DEVRAIT** (SHOULD) = recommandé ; **PEUT** (MAY) = optionnel.
   - Après chaque étape **critique**, ajouter un **point de contrôle** (« Résultat attendu : … »).
   - Commandes/valeurs **copiables** telles quelles (pas de paraphrase).
8. **Points de contrôle / validation finale** — comment vérifier que tout le processus a réussi.
9. **Annexe dépannage (mini-runbook)** — table *Symptôme → Cause probable → Action*.
10. **Maintenance & évolutivité** — comment faire évoluer, qui maintient.
11. **Historique des révisions** — table version | date | auteur | changement.

## 3. Structure d'un Runbook (si format incident)

En-tête · **Déclencheur/alerte** · **Diagnostic** (vérifs rapides) · **Remédiation** (start/stop/health/rollback) · **Vérification post-action** · **Escalade** (qui contacter, seuils) · **Post-incident** (notes, mise à jour) · Révisions.

## 4. Check-list qualité (valider avant livraison)

Inspirée de *The Checklist Manifesto* (Gawande), 5W2H (Ishikawa), ISO 9001, Google SRE Workbook :

- [ ] **Un acteur sait l'exécuter sans contexte** (5W2H : Qui, Quoi, Où, Quand, Pourquoi, Comment, Combien).
- [ ] **Une action par étape**, verbe à l'impératif, numérotée.
- [ ] **Commandes/valeurs copiables**, exactes, non paraphrasées.
- [ ] **Point de contrôle après chaque étape critique** (résultat attendu observable).
- [ ] **Prérequis explicites** (accès, licences, droits) listés avant l'étape 1.
- [ ] **Cas d'échec couverts** (annexe dépannage / escalade).
- [ ] **Rôles clairs** (qui est responsable de quoi).
- [ ] **Pas d'ambiguïté** : chaque exigence MUST/SHOULD/MAY explicite.
- [ ] **Cadence de revue** définie (date de prochaine revue dans l'en-tête).
- [ ] **Historique des révisions** présent et daté.

## 5. Production du fichier

- Rédiger en **Markdown** d'abord (structure ci-dessus).
- **Word (.docx)** éditable : `pandoc doc.md -o doc.docx` (idéal pour validation/annotation par un supérieur).
- **PDF** figé (présentation) : rendre un HTML stylé puis Chrome headless `--print-to-pdf`, ou `pandoc doc.md -o doc.pdf` si LaTeX dispo.
- Adapter la langue à la demande (FR/EN). Pour un public **management** : alléger le jargon, garder Objet/Bénéfices/Schéma ; pour un public **exécutant** : maximiser les étapes copiables et les points de contrôle.

## 6. Anti-patterns à éviter

- Étapes vagues (« configurer correctement ») sans valeur exacte.
- Mélanger normal (SOP) et incident (runbook) sans séparation.
- Oublier les prérequis/droits → blocage à l'exécution.
- Pas de point de contrôle → l'exécutant ne sait pas si l'étape a marché.
- Pas d'historique/revue → le document dérive et devient faux.
