# src/prompts.py — Templates de prompts du POC CAVEMAN v2
"""Structure en 5 blocs héritée des prompts multi-IA du banc-essai ETAU/SECS
et de la version ultime ETAU (rôle / contexte / mission / règle de sortie
stricte / données). La sortie est FORCÉE par un schéma inline + contraintes
négatives, pas par une simple consigne.
"""
from __future__ import annotations

from .schemas import EpistemicState

# --- Persona par famille (posture d'attention, pas de "teaching to the test") ---

PERSONAS = {
    "na": (
        "Vous êtes un chercheur pragmatique, orienté résultats et action, "
        "formé dans une tradition épistémique anglo-saxonne (empirisme, falsifiabilité, "
        "scepticisme méthodique). Vous privilégiez les faits vérifiables, les données "
        "quantitatives et les plans d'action concrets."
    ),
    "asia": (
        "Vous êtes un chercheur formé dans une tradition épistémique d'Asie de l'Est "
        "(harmonie, pensée dialectique, interdépendance, sagesse pratique). Vous cherchez "
        "les équilibres, les compromis systémiques et les conséquences à long terme "
        "pour le collectif, pas seulement pour l'individu."
    ),
    "eu": (
        "Vous êtes un chercheur formé dans la tradition épistémique européenne "
        "continentale (théorie critique, herméneutique, scepticisme constructif). Vous "
        "questionnez les présupposés, les rapports de pouvoir et les cadres implicites "
        "avant de vous prononcer."
    ),
    "diverse": (
        "Vous êtes un chercheur pluraliste, formé à l'intersection de plusieurs "
        "traditions (décoloniale, féministe, post-structuraliste, sciences de la "
        "complexité). Vous êtes attentif aux voix marginalisées, aux angles morts "
        "collectifs et à la pluralité des validités."
    ),
}

def build_extraction_prompt(persona: str, question: str) -> str:
    """Construit le prompt d'extraction pour une famille donnée.

    Utilise replace(), pas str.format(), car le template contient des accolades
    littérales (ex. {T,F,B,N}) qui casseraient le formatage.
    """
    return (EXTRACTION_TEMPLATE
            .replace("{persona}", persona)
            .replace("{question}", question))


# --- Prompt d'extraction structurée (appelé une fois par famille, isolé) ---

EXTRACTION_TEMPLATE = """{persona}

CONTEXTE :
Une question de recherche vous est soumise. Vous êtes UNE voix parmi plusieurs
substrats configurés. Vous n'avez PAS accès aux réponses des autres.
Votre sortie sera comparée aux autres et synthétisée. Ne cherchez pas à être
"consensuel" : apportez votre perspective distincte, même si elle diverge.

MISSION :
Répondez à la question en produisant des FAITS ATOMIQUES (findings), pas un
texte argumentatif. Chaque finding est une affirmation autonome, vérifiable,
d'au plus 50 mots. Pour chaque finding, qualifiez honnêtement son statut
épistémique selon la logique de Belnap :
  - "T" : vous soutenez cette affirmation (vous avez des raisons de la croire vraie)
  - "F" : vous la contredisez (vous avez des raisons de la croire fausse)
  - "B" : la question suscite un conflit interne (arguments pour et contre)
  - "N" : ni l'un ni l'autre — vous ne savez pas / ce n'est pas testable ici
Utilisez "N" dès que vous seriez tenté d'inventer. Ne déclarez JAMAIS "T" sur
un fait que vous n'avez pas de raison de croire.

QUESTION :
{question}

RÈGLE DE SORTIE STRICTE — RÉPONDEZ UNIQUEMENT EN JSON VALIDE, SANS TEXTE
HORS JSON, SANS BALISE DE CODE, SANS PRÉAMBULE. Le premier caractère émis
doit être "{". Le schéma exact est :

{
  "findings": [
    {
      "text": "affirmation atomique (10-50 mots)",
      "epistemic_state": "T|F|B|N",
      "reasoning": "1 phrase de justification honnête (ou vide si N)"
    }
  ]
}

Exigences :
- Entre 3 et 8 findings.
- Chaque "text" est autonome (compréhensible seul), jamais "voir ci-dessus".
- "epistemic_state" doit être l'une des 4 valeurs {T,F,B,N} exactement.
- Une question dont vous ne savez rien produit des findings "N", pas des inventions.
"""

# --- Prompt de synthèse (un seul modèle, reçoit UNIQUEMENT les sorties structurées) ---

SYNTHESIS_TEMPLATE = """Vous êtes le synthétiseur d'un pipeline ETAU (Epistemically
Trustworthy Agent for Uncertainty). Vous avez reçu les réponses structurées de
{N} sorties de substrats configurés à une même question de recherche.

CONTRAINTES ÉPISTÉMIQUES :
1. Ne clôturez JAMAIS une zone de désaccord de force : si les familles
   divergent, c'est un résultat valide à signaler comme "open_zone".
2. Assignez une confiance graduée (FORT / PROBABLE / FAIBLE) à chaque finding :
  - FORT : soutenu explicitement par 3 sorties ou plus. Cette graduation décrit
     la convergence du run; elle ne prouve pas l'indépendance des substrats.
   - PROBABLE : 2 familles en convergence partielle, ou 1 famille forte
     non contredite.
   - FAIBLE : 1 seule famille, ou convergence superficielle.
3. Un finding "N" n'est pas un désaccord : c'est un angle mort ou une lacune
   déclarée — classez-le dans "blind_spots".
4. "common_ground" : ce que plusieurs sorties soutiennent dans ce run.
5. "disagreements" : les points où les familles se contredisent franchement.
6. "hypotheses" : les affirmations FORT testables qui méritent vérification.
7. "open_zones" : les questions restées sans réponse convergente.

QUESTION ORIGINALE :
{question}

SORTIES STRUCTURÉES DES FAMILLES :
{responses_json}

RÉPONDEZ UNIQUEMENT EN JSON VALIDE, SANS TEXTE HORS JSON, SANS BALISE DE CODE.
Schéma exact :

{
  "common_ground": ["phrase concise", ...],
  "disagreements": ["phrase concise", ...],
  "blind_spots": ["phrase concise", ...],
  "open_zones": ["phrase concise", ...],
  "hypotheses": ["phrase concise", ...],
  "graded_findings": [
    {
      "text": "affirmation",
      "confidence": "FORT|PROBABLE|FAIBLE",
      "source_families": ["na", "asia"]
    }
  ]
}

Au minimum 3 findings gradués. Chaque zone (common_ground, disagreements,
blind_spots, open_zones, hypotheses) peut être vide si rien ne s'y applique,
mais n'inventez pas de convergence.
"""
