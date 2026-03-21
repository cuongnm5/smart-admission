# Smart Admission: University Candidate Matching (v1)

Production-oriented deterministic-first matching module for a Smart University Suggestion System.

## What this module does

- Accepts a minimal student profile payload
- Retrieves relevant US universities from a structured datastore (mock JSON repository in v1)
- Applies deterministic hard filters (eligibility and affordability)
- Computes deterministic comparison features
- Uses a bounded LLM evaluator/reranker input contract (with deterministic fallback)
- Returns top 20 candidates with score breakdown, reasons, and traceability
- Produces downstream consultant-friendly JSON payload

## Architecture summary

Layered design with strict responsibility boundaries:

- `app/api/`: FastAPI routes only (no business logic)
- `app/components/`: system components grouped by responsibility
	- `matching/`: stage-1 matching component (top-20 university IDs)
	- `summary/`: stage-2 analysis component (moved from top-level `summary/`)
	- `pipeline/`: orchestration component combining stage 1 + stage 2
- `app/schemas/`: request/response contracts (Pydantic)
- `app/domain/`: internal typed models and enums
- `app/repositories/`: datastore abstraction + mock repository implementation
- `app/services/`: deterministic pipeline stages + orchestration
- `app/prompts/`: isolated LLM prompt templates
- `app/data/`: mock universities and rubric config
- `app/tests/`: unit tests for core behavior

Main orchestration is in `app/services/matching_service.py`.

## Why deterministic-first + bounded LLM

- Deterministic code computes facts: eligibility, thresholds, budget checks, and numeric feature comparisons.
- This prevents LLM hallucinations in areas where exact computation is required.
- The LLM is bounded to holistic evaluation/reranking from provided evidence only.
- Strict JSON schema + parser + fallback ensure robust production behavior.
- If LLM is unavailable or returns invalid output, deterministic scoring continues service operation.

## Pipeline stages

1. `profile_normalizer`
2. `candidate_retrieval`
3. `hard_filter_engine`
4. `feature_builder`
5. `expert_rubric`
6. `llm_scorer` (bounded, replaceable)
7. `reranker`
8. `consultant_payload_builder`

## Run locally

```zsh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Health check:

```zsh
curl http://127.0.0.1:8000/health
```

Merged system pipeline endpoint:

```zsh
curl -X POST http://127.0.0.1:8000/v1/pipeline/match-and-analyze \
	-H "Content-Type: application/json" \
	-d @app/data/sample.json
```

Matching request:

```zsh
curl -X POST http://127.0.0.1:8000/v1/matching/universities \
	-H "Content-Type: application/json" \
	-d '{
		"student_id": "u001",
		"gpa": 3.6,
		"gpa_scale": 4.0,
		"ielts": 7.0,
		"intended_major": "Computer Science",
		"profile_text": "Won a provincial math prize, leader of coding club, volunteer teaching children.",
		"annual_budget_usd": 30000
	}'
```

## Example response (shape)

```json
{
	"top_candidates": [
		{
			"university_id": "asu",
			"name": "Arizona State University",
			"overall_match": 79,
			"bucket": "target",
			"score_breakdown": {
				"academic_fit": 82,
				"competitiveness_fit": 55,
				"affordability_fit": 70,
				"profile_alignment": 60
			},
			"strengths": [
				"Student meets academic threshold for the university"
			],
			"concerns": [
				"Program competitiveness creates significant admission uncertainty"
			],
			"hard_filter_trace": [
				{
					"rule": "international_allowed",
					"pass": true
				}
			]
		}
	],
	"meta": {
		"retrieved_count": 12,
		"hard_filter_pass_count": 8,
		"scored_count": 8,
		"returned_count": 8,
		"rubric_version": "v1"
	}
}
```

## Testing

```zsh
pytest -q
```

Covered tests include:

- input validation
- profile normalization
- hard filter rules
- feature calculation
- ranking and consultant payload
- LLM JSON parsing and validation
- route-level integration check

## Downstream consultant integration notes

The response contract in `app/schemas/response.py` is directly usable by consultant components:

- `top_candidates[*].score_breakdown` for explanation UI
- `strengths` / `concerns` for counseling narratives
- `hard_filter_trace` for transparent audit and objection handling
- `meta` for analytics and monitoring

## Future extension: richer student profile, optional MCP wrapper, and optional RAG support

- Add richer input fields (SAT/GRE, coursework rigor, target states, preferred climate, deadlines)
- Wrap `MatchingService` as an MCP tool without changing core internals
- Add optional RAG for expert guidance retrieval or supplemental school facts while keeping core deterministic pipeline unchanged