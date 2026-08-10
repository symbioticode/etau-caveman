#!/usr/bin/env python3
"""Interface web minimale, locale uniquement, pour ETAU-CAVEMAN."""
from __future__ import annotations

import argparse
import asyncio
import html
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestrator import ETAUOrchestrator  # noqa: E402

HOST = "127.0.0.1"
DEFAULT_PORT = 8766
FAMILIES = ["na", "asia", "eu"]
OMNIROUTE_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
REFORMULATION_MODELS = [
    "mistral/mistral-small-latest",
    "cerebras/gemma-4-31b",
    "groq/llama-3.3-70b-versatile",
]


PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ETAU-CAVEMAN</title>
<style>
body { font: 16px/1.5 sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
textarea { box-sizing: border-box; width: 100%; min-height: 7rem; padding: .6rem; }
button { margin-top: .6rem; padding: .55rem 1rem; }
#status { margin: 1rem 0; }
section { margin: 1.5rem 0; }
details { margin: .7rem 0; padding: .5rem; border: 1px solid #bbb; }
summary { cursor: pointer; font-weight: bold; }
.error { color: #a00; white-space: pre-wrap; }
.meta { color: #555; }
</style></head><body>
<h1>ETAU-CAVEMAN</h1>
<form id="run-form">
  <label for="question">Question de recherche</label>
  <textarea id="question" name="question" required></textarea>
  <button type="submit">Lancer</button>
</form>
<p id="status" aria-live="polite"></p>
<main id="result"></main>
<script>
const form = document.getElementById('run-form');
const status = document.getElementById('status');
const result = document.getElementById('result');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  status.textContent = 'En cours…';
  result.replaceChildren();
  form.querySelector('button').disabled = true;
  try {
    const response = await fetch('/run', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: new URLSearchParams(new FormData(form))
    });
    const body = await response.text();
    if (!response.ok) throw new Error(body);
    result.innerHTML = body;
    status.textContent = 'Terminé.';
  } catch (error) {
    status.textContent = 'Échec.';
    result.innerHTML = '<p class="error"></p>';
    result.querySelector('p').textContent = error.message;
  } finally {
    form.querySelector('button').disabled = false;
  }
});
</script></body></html>"""


def _items(values: list[str]) -> str:
    if not values:
        return "<p>Aucun élément.</p>"
    return "<ul>" + "".join(f"<li>{html.escape(str(v))}</li>" for v in values) + "</ul>"


def render_result(result, research_prompt: str = "", reformulation_model: str = "") -> str:
    """Transforme PipelineResult en HTML lisible, jamais en JSON brut."""
    synth = result.synthesis
    sections = [
        ("Points communs", synth.common_ground),
        ("Désaccords", synth.disagreements),
        ("Angles morts", synth.blind_spots),
        ("Zones ouvertes", synth.open_zones),
        ("Hypothèses", synth.hypotheses),
    ]
    synthesis_html = "".join(
        f"<h3>{title}</h3>{_items(values)}" for title, values in sections
    )
    if synth.graded_findings:
        graded = [
            f"{item.get('confidence', '—')} — {item.get('text', '')}"
            for item in synth.graded_findings
        ]
        synthesis_html += f"<h3>Constats gradués</h3>{_items(graded)}"

    response_html = []
    for family in FAMILIES:
        response = result.responses.get(family)
        if response is None:
            response_html.append(
                f"<details><summary>{html.escape(family)} — sans réponse</summary></details>"
            )
            continue
        findings = []
        for finding in response.findings:
            line = f"[{finding.epistemic_state.value}] {finding.text}"
            if finding.reasoning:
                line += f" — {finding.reasoning}"
            findings.append(line)
        error = f'<p class="error">{html.escape(response.error)}</p>' if response.error else ""
        response_html.append(
            "<details><summary>"
            f"{html.escape(family)} — {html.escape(response.model or 'modèle inconnu')}"
            "</summary>"
            f"{error}{_items(findings)}"
            f'<p class="meta">Latence : {html.escape(str(response.latency_s))} s · '
            f"Tokens : {response.tokens_in} entrée / {response.tokens_out} sortie</p>"
            "</details>"
        )

    metadata = result.metadata
    preflight = metadata.get("preflight_error") or metadata.get("synthesis_error")
    warning = f'<p class="error">{html.escape(str(preflight))}</p>' if preflight else ""
    reformulation = ""
    if research_prompt:
        reformulation = (
            "<details><summary>Question reformulée pour la recherche"
            f" — {html.escape(reformulation_model)}</summary>"
            f"<p>{html.escape(research_prompt)}</p></details>"
        )
    return (
        f"{reformulation}<section><h2>Synthèse</h2>{warning}{synthesis_html}</section>"
        "<section><h2>Réponses des trois substrats</h2>"
        + "".join(response_html)
        + "</section>"
        f'<p class="meta">Durée : {html.escape(str(metadata.get("total_latency_s", "—")))} s · '
        f'Coût estimé : ${html.escape(str(metadata.get("estimated_cost_usd", "—")))}</p>'
    )


def reformulate(question: str) -> tuple[str, str]:
    """LLM A prépare le prompt; l'orchestrateur existant reste inchangé."""
    client = OpenAI(base_url=OMNIROUTE_BASE_URL, api_key="local")
    instruction = f"""Tu prépares une recherche approfondie multi-modèles.
Reformule la demande en un prompt autonome et investigable. Inclus le périmètre,
les questions secondaires, les preuves attendues, les contre-arguments et les
incertitudes. Ne réponds pas à la demande. Retourne uniquement le prompt.

DEMANDE :
{question}
"""
    errors = []
    for model in REFORMULATION_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": instruction}],
                max_tokens=900,
                timeout=60,
            )
            content = (response.choices[0].message.content or "").strip()
            if content:
                return content, model
            errors.append(f"{model}: réponse vide")
        except Exception as exc:
            errors.append(f"{model}: {type(exc).__name__}")
    raise RuntimeError("reformulation impossible : " + ", ".join(errors))


async def _run_pipeline(question: str) -> str:
    research_prompt, model = await asyncio.to_thread(reformulate, question)
    result = await ETAUOrchestrator(include_deepseek=False).run(research_prompt, FAMILIES)
    return render_result(result, research_prompt, model)


def run_pipeline(question: str) -> str:
    return asyncio.run(_run_pipeline(question))


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: str, content_type: str = "text/html; charset=utf-8") -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            self._send(200, PAGE)
        elif self.path == "/health":
            self._send(200, "ok", "text/plain; charset=utf-8")
        else:
            self._send(404, "Introuvable", "text/plain; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/run":
            self._send(404, "Introuvable", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 32_768:
                self._send(413, "Question trop longue", "text/plain; charset=utf-8")
                return
            form = parse_qs(self.rfile.read(length).decode("utf-8"))
            question = form.get("question", [""])[0].strip()
            if not question:
                self._send(400, "La question est obligatoire.", "text/plain; charset=utf-8")
                return
            self._send(200, run_pipeline(question))
        except Exception as exc:
            self._send(500, f"Le pipeline a échoué : {exc}", "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    server = ThreadingHTTPServer((HOST, args.port), Handler)
    print(f"ETAU-CAVEMAN : http://{HOST}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
