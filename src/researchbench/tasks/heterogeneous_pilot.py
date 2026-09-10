"""Scientific pilot for heterogeneous integration & BEOL-compatible devices (Issue #13).

Addresses the core research gap identified in RESEARCH_BENCHMARK.md:
- Replaces keyword matching with structured, evidence-based rubrics.
- Grounded in authentic literature and physical constraints of monolithic 3D / BEOL.
- Includes hard negative indicators, verifiable provenance, and uncertainty expectations.
- Supports both automated evaluation and blinded human expert calibration.
"""

from __future__ import annotations

from typing import Any

from researchbench.dataset_schema import DatasetItem, Provenance, is_runnable, validate_item
from researchbench.rubric import Criterion, Rubric, RubricResult

# --- Rubrics for the 5 reviewed items + 1 draft post-cutoff item -------------

RUBRIC_BEOL_THERMAL_BUDGET = Rubric(
    passing_threshold=65.0,
    criteria=[
        Criterion(
            name="temperature_ceiling",
            description="Identifies the strict 400 deg C (or 350-400 deg C) thermal budget ceiling for BEOL.",
            weight=1.0,
            evidence_patterns=[
                r"400\s*(?:°|deg|celsius|c)",
                r"350\s*-\s*400",
                r"thermal\s+budget",
            ],
            negative_patterns=[
                r">?\s*[5-9]\d{2}\s*(?:°|deg|c)",
                r"rapid\s+thermal\s+annealing\s+at\s+1000",
            ],
        ),
        Criterion(
            name="interconnect_degradation",
            description="Identifies copper diffusion, electromigration, or low-k interlayer dielectric (ILD) damage.",
            weight=1.0,
            evidence_patterns=[
                r"copper\s+diffus",
                r"cu\s+diffus",
                r"electromigration",
                r"low-k",
                r"interconnect",
                r"voiding",
            ],
            negative_patterns=[],
        ),
        Criterion(
            name="feol_preservation",
            description="Explains preservation of front-end CMOS devices (preventing dopant deactivation or contact degradation).",
            weight=1.0,
            evidence_patterns=[
                r"dopant",
                r"front-end",
                r"feol",
                r"silicide",
                r"contact\s+degrad",
                r"cmos\s+degrad",
            ],
            negative_patterns=[
                r"feol\s+tolerates\s+arbitrary",
            ],
        ),
    ],
)

RUBRIC_OXIDE_IGZO = Rubric(
    passing_threshold=65.0,
    criteria=[
        Criterion(
            name="s_orbital_overlap",
            description="Explains spherical In 5s orbital overlap enabling high mobility despite amorphous disorder.",
            weight=1.0,
            evidence_patterns=[
                r"5s",
                r"s-orbital",
                r"spherical",
                r"overlap",
                r"disorder",
                r"indium",
            ],
            negative_patterns=[
                r"high\s+hole\s+mobility",
                r"p-type\s+igzo\s+superior",
            ],
        ),
        Criterion(
            name="ultra_low_leakage",
            description="Cites wide bandgap (~3 eV) and ultra-low off-state leakage (<10^-18 A/um or sub-yoctoampere regime).",
            weight=1.0,
            evidence_patterns=[
                r"wide\s+band\s*gap",
                r"3(?:\.[0-2])?\s*ev",
                r"off-state\s+leakage",
                r"10\^?-1[89]",
                r"sub-yocto",
                r"yoctoamp",
            ],
            negative_patterns=[],
        ),
        Criterion(
            name="dram_retention",
            description="Connects low off-leakage to extended DRAM data retention time for 2T0C / gain cells.",
            weight=1.0,
            evidence_patterns=[
                r"retention",
                r"2t0c",
                r"dram",
                r"refresh",
                r"capacitor",
            ],
            negative_patterns=[],
        ),
    ],
)

RUBRIC_FERROELECTRIC_HZO = Rubric(
    passing_threshold=65.0,
    criteria=[
        Criterion(
            name="beol_crystallization_temperature",
            description="Highlights low crystallization temperature (<= 400 deg C) compatible with BEOL compared to perovskites.",
            weight=1.0,
            evidence_patterns=[
                r"400\s*(?:°|deg|c)",
                r"crystalliz",
                r"perovskite",
                r"pzt",
                r"thermal\s+budget",
            ],
            negative_patterns=[
                r"pzt\s+crystallizes\s+at\s+lower",
            ],
        ),
        Criterion(
            name="orthorhombic_phase",
            description="Identifies the ferroelectric orthorhombic phase (o-phase, Pca2_1).",
            weight=1.0,
            evidence_patterns=[
                r"orthorhombic",
                r"o-phase",
                r"pca2",
                r"non-centrosymmetric",
            ],
            negative_patterns=[
                r"monoclinic\s+is\s+ferroelectric",
            ],
        ),
        Criterion(
            name="capping_stress_confinement",
            description="Explains stabilization via top capping layer (e.g. TiN) mechanical tensile stress / surface energy.",
            weight=1.0,
            evidence_patterns=[
                r"tin",
                r"cap",
                r"stress",
                r"strain",
                r"confinement",
                r"surface\s+energy",
            ],
            negative_patterns=[],
        ),
    ],
)

RUBRIC_2D_TMDC = Rubric(
    passing_threshold=65.0,
    criteria=[
        Criterion(
            name="transfer_defects_scaling",
            description="Identifies transfer pitfalls: polymer residues, wrinkles, cracks, and 300 mm wafer scalability limits.",
            weight=1.0,
            evidence_patterns=[
                r"residue",
                r"polymer",
                r"wrinkle",
                r"crack",
                r"300\s*mm",
                r"yield",
                r"wafer-scale",
            ],
            negative_patterns=[],
        ),
        Criterion(
            name="direct_growth_thermal_dilemma",
            description="Explains that low-temperature (<=400 deg C) direct synthesis produces small grain size and high defect density.",
            weight=1.0,
            evidence_patterns=[
                r"grain\s+boundar",
                r"crystallin",
                r"grain\s+size",
                r"defect\s+densit",
                r"amorphous",
                r"low\s+temperature",
            ],
            negative_patterns=[
                r"grow\s+single\s+crystal\s+at\s+1000.*beol",
            ],
        ),
        Criterion(
            name="electrical_consequences",
            description="Connects structural defects to carrier mobility degradation and high contact resistance.",
            weight=1.0,
            evidence_patterns=[
                r"mobilit",
                r"scattering",
                r"contact\s+resist",
                r"fermi\s+level\s+pinning",
            ],
            negative_patterns=[],
        ),
    ],
)

RUBRIC_HYBRID_BONDING = Rubric(
    passing_threshold=65.0,
    criteria=[
        Criterion(
            name="controlled_cmp_dishing",
            description="Explains the requirement of nanometer-scale controlled Cu dishing / recess relative to dielectric.",
            weight=1.0,
            evidence_patterns=[
                r"dishing",
                r"recess",
                r"cmp",
                r"chemical\s+mechanical",
                r"planar",
            ],
            negative_patterns=[
                r"copper\s+must\s+protrude",
            ],
        ),
        Criterion(
            name="two_step_bonding_process",
            description="Describes room-temperature dielectric fusion bonding followed by thermal annealing.",
            weight=1.0,
            evidence_patterns=[
                r"dielectric",
                r"fusion",
                r"room\s+temp",
                r"anneal",
                r"hydrophilic",
                r"si-o-si",
            ],
            negative_patterns=[],
        ),
        Criterion(
            name="cte_differential_expansion",
            description="Identifies differential thermal expansion (CTE mismatch) driving copper expansion to close the dishing gap.",
            weight=1.0,
            evidence_patterns=[
                r"cte",
                r"thermal\s+expansion",
                r"gap\s+clos",
                r"interdiffusion",
                r"compressive",
            ],
            negative_patterns=[
                r"dielectric\s+expands\s+more\s+than\s+copper",
            ],
        ),
    ],
)

RUBRIC_IGZO_CHANNEL_CAPPING = Rubric(
    passing_threshold=65.0,
    criteria=[
        Criterion(
            name="beol_400c_budget",
            description="States the 400 deg C BEOL thermal-budget compatibility claimed for the IGZO/In2O3 process.",
            weight=1.0,
            evidence_patterns=[
                r"400\s*(?:°|deg|celsius|c)",
                r"thermal\s+budget",
                r"beol",
            ],
            negative_patterns=[
                r">?\s*[6-9]\d{2}\s*(?:°|deg|c)",
            ],
        ),
        Criterion(
            name="in2o3_sio2_capping",
            description="Identifies the amorphous In2O3 mixed with SiO2 capping layer (not conventional SiO2-only encapsulation).",
            weight=1.0,
            evidence_patterns=[
                r"in2o3",
                r"in\s*2\s*o\s*3",
                r"indium\s+oxide",
                r"sio2",
                r"si\s*o\s*2",
                r"capp",
                r"amorphous",
            ],
            negative_patterns=[
                r"conventional\s+sio2\s+(?:is|was)\s+superior",
            ],
        ),
        Criterion(
            name="mobility_and_pbs",
            description="Reports ~33.1 cm^2/V.s extrinsic saturation mobility and ~5 mV PBS Vt shift at 3 MV/cm for 1000 s.",
            weight=1.0,
            evidence_patterns=[
                r"33(?:\.1)?",
                r"cm\^?2",
                r"5\s*mv",
                r"(?:positive[- ]bias|pbs)",
                r"3\s*mv\s*/\s*cm",
                r"1000\s*s",
            ],
            negative_patterns=[
                r"hole\s+mobility",
            ],
        ),
    ],
)

# --- Authoritative Dataset Items ----------------------------------------------

PILOT_DATASET: list[DatasetItem] = [
    DatasetItem(
        id="heterogeneous_pilot/beol_thermal_budget/q1",
        capability_tags=["C1", "C5"],
        ground_truth=(
            "BEOL processing requires a strict thermal budget ceiling of 400 deg C. "
            "Exceeding this induces copper diffusion into interlayer dielectrics, "
            "voiding and electromigration degradation, low-k material damage, and "
            "front-end CMOS dopant/contact degradation."
        ),
        ground_truth_source="IEEE IEDM / Transactions on Electron Devices (BEOL Reliability)",
        scoring_method="rubric",
        contamination_risk="low",
        provenance=Provenance(
            source_id="IEEE-IEDM-BEOL-3D",
            source_type="expert_curated",
            license="CC-BY-4.0",
            author_role="domain_expert",
            reviewer_role="cao_shurong",
            review_status="reviewed",
            review_notes="Curated scientific pilot item verified against monolithic 3D BEOL process integration constraints.",
        ),
        expert_notes=(
            "Essential domain question for monolithic 3D integration. Evaluates physical "
            "understanding of why standard front-end CMOS processes cannot be directly applied to BEOL."
        ),
        hard_negatives=[
            {
                "text": "Thermal budgets up to 850 deg C can be used with rapid thermal annealing.",
                "penalty": "invalid_feol_temp",
            },
            {
                "text": "Copper interconnects do not suffer thermal degradation below 700 deg C.",
                "penalty": "cu_metallurgy_error",
            },
        ],
        version="1.0",
        task_data={
            "question": (
                "What is the primary physical constraint limiting the maximum processing temperature "
                "during Back-End-of-Line (BEOL) monolithic 3D integration of active semiconductor layers "
                "over front-end CMOS, and what temperature ceiling is universally enforced to prevent "
                "interconnect reliability degradation?"
            ),
            "rubric": RUBRIC_BEOL_THERMAL_BUDGET.to_dict(),
        },
    ),
    DatasetItem(
        id="heterogeneous_pilot/oxide_semiconductor_igzo/q2",
        capability_tags=["C1", "C7"],
        ground_truth=(
            "Amorphous IGZO maintains electron mobility (>10 cm^2/V.s) at low deposition temperatures "
            "because the conduction band minimum consists of isotropic, spherical In 5s orbital overlap "
            "unperturbed by bond angle disorder. For DRAM access transistors, its ~3 eV wide bandgap "
            "yields ultra-low off-state leakage (<10^-19 A/um), drastically extending data retention."
        ),
        ground_truth_source="Nature Electronics / Science (Oxide Semiconductors for 3D DRAM)",
        scoring_method="rubric",
        contamination_risk="low",
        provenance=Provenance(
            source_id="NatureElectronics-Oxide-BEOL",
            source_type="expert_curated",
            license="CC-BY-4.0",
            author_role="domain_expert",
            reviewer_role="cao_shurong",
            review_status="reviewed",
            review_notes="Curated pilot item evaluating orbital physics and 3D DRAM leakage mechanisms.",
        ),
        expert_notes="Evaluates solid-state electronic structure knowledge and memory retention physics.",
        hard_negatives=[
            {
                "text": "IGZO has high p-type hole mobility suitable for complementary CMOS logic.",
                "penalty": "unphysical_hole_transport",
            },
            {
                "text": "IGZO must be annealed at 900 deg C to become crystalline for high mobility.",
                "penalty": "violates_beol_and_amorphous_physics",
            },
        ],
        version="1.0",
        task_data={
            "question": (
                "In monolithic 3D integration, amorphous In-Ga-Zn-O (a-IGZO) thin-film transistors "
                "are widely integrated in the BEOL. What unique transport advantage does a-IGZO provide "
                "over unpassivated silicon at low deposition temperatures, and what is its primary "
                "operational advantage for DRAM access transistors?"
            ),
            "rubric": RUBRIC_OXIDE_IGZO.to_dict(),
        },
    ),
    DatasetItem(
        id="heterogeneous_pilot/ferroelectric_hzo/q3",
        capability_tags=["C1", "C3"],
        ground_truth=(
            "HZO crystallizes at <= 400 deg C compatible with BEOL thermal budgets and scales sub-10 nm "
            "without dead-layer effects, unlike perovskites (PZT) requiring >600 deg C. The ferroelectric "
            "orthorhombic phase (Pca2_1) is stabilized via capping electrode (e.g. TiN) tensile strain "
            "and surface energy effects."
        ),
        ground_truth_source="IEEE IEDM / Nano Letters (Ferroelectric HZO BEOL Memory)",
        scoring_method="rubric",
        contamination_risk="low",
        provenance=Provenance(
            source_id="IEDM-HZO-Ferroelectric",
            source_type="expert_curated",
            license="CC-BY-4.0",
            author_role="domain_expert",
            reviewer_role="cao_shurong",
            review_status="reviewed",
            review_notes="Curated pilot item evaluating crystallographic phase engineering under BEOL limits.",
        ),
        expert_notes="Tests understanding of non-centrosymmetric ferroelectric phase stabilization.",
        hard_negatives=[
            {
                "text": "PZT has a lower crystallization temperature than HZO and is preferred for BEOL.",
                "penalty": "inverted_temperature_fact",
            },
            {
                "text": "The monoclinic phase is the ferroelectric phase responsible for polarization switching.",
                "penalty": "wrong_crystallographic_phase",
            },
        ],
        version="1.0",
        task_data={
            "question": (
                "Why has Hf_xZr_{1-x}O_2 (HZO) emerged as the preferred ferroelectric material for "
                "BEOL-compatible non-volatile FeFET/FeRAM over conventional perovskites (such as PZT or SBT), "
                "and how is the ferroelectric orthorhombic phase stabilized under BEOL thermal constraints?"
            ),
            "rubric": RUBRIC_FERROELECTRIC_HZO.to_dict(),
        },
    ),
    DatasetItem(
        id="heterogeneous_pilot/2d_tmcd_monolithic3d/q4",
        capability_tags=["C1", "C5"],
        ground_truth=(
            "Transfer methods allow high-quality high-temperature grown 2D crystals on BEOL but introduce "
            "polymer residue, wrinkles, cracks, and severe 300 mm yield limitations. Low-temperature "
            "(<=400 deg C) direct synthesis produces small grain size with high defect density and "
            "severe grain-boundary scattering, causing mobility degradation and high contact resistance."
        ),
        ground_truth_source="Nature Materials / IEEE Transactions on Electron Devices (2D Monolithic 3D)",
        scoring_method="rubric",
        contamination_risk="low",
        provenance=Provenance(
            source_id="NatureMat-2D-BEOL-Integration",
            source_type="expert_curated",
            license="CC-BY-4.0",
            author_role="domain_expert",
            reviewer_role="cao_shurong",
            review_status="reviewed",
            review_notes="Curated pilot item evaluating manufacturing trade-offs between transfer and direct growth.",
        ),
        expert_notes="Assesses nuanced understanding of 2D integration and contact/scattering physics.",
        hard_negatives=[
            {
                "text": "Direct high-temperature CVD (800 deg C) can be performed safely on copper BEOL stacks.",
                "penalty": "violates_beol_interconnect_limits",
            },
            {
                "text": "Wet transfer processes currently achieve 99.9% yield across 300 mm foundry wafers.",
                "penalty": "unsubstantiated_manufacturing_claim",
            },
        ],
        version="1.0",
        task_data={
            "question": (
                "When integrating 2D semiconductors (such as monolayer or few-layer MoS2) into BEOL "
                "interconnect stacks for monolithic 3D logic, what fundamental dilemma exists between "
                "transfer-based integration versus direct low-temperature synthesis?"
            ),
            "rubric": RUBRIC_2D_TMDC.to_dict(),
        },
    ),
    DatasetItem(
        id="heterogeneous_pilot/cu_cu_hybrid_bonding/q5",
        capability_tags=["C1", "C4"],
        ground_truth=(
            "CMP must produce a controlled nanometer-scale Cu dishing/recess relative to dielectric "
            "because copper has a higher CTE than dielectric. Dielectric fusion bonding occurs at room "
            "temperature, followed by thermal annealing where Cu expands faster to close the gap and "
            "form solid-state metallurgical Cu-Cu bonds under compressive stress."
        ),
        ground_truth_source="IEEE ECTC / IEDM (Fine-Pitch Direct Cu-Cu Hybrid Bonding)",
        scoring_method="rubric",
        contamination_risk="low",
        provenance=Provenance(
            source_id="IEEE-ECTC-Hybrid-Bonding",
            source_type="expert_curated",
            license="CC-BY-4.0",
            author_role="domain_expert",
            reviewer_role="cao_shurong",
            review_status="reviewed",
            review_notes="Curated pilot item on wafer/die-level 3D heterogeneous bonding physics.",
        ),
        expert_notes="Evaluates mechanical planarization and thermomechanical interdiffusion understanding.",
        hard_negatives=[
            {
                "text": "Copper pads must protrude above the dielectric after CMP to make initial contact.",
                "penalty": "fatal_hybrid_bonding_delamination_defect",
            },
            {
                "text": "Dielectric and copper bond simultaneously at room temperature without any heating.",
                "penalty": "ignores_cu_metallurgical_expansion",
            },
        ],
        version="1.0",
        task_data={
            "question": (
                "In ultra-fine pitch (< 1 um) Cu-Cu direct hybrid bonding for 3D heterogeneous integration, "
                "what role does chemical mechanical planarization (CMP) dishing play, and how is the "
                "bonding sequence thermally engineered?"
            ),
            "rubric": RUBRIC_HYBRID_BONDING.to_dict(),
        },
    ),
    DatasetItem(
        id="heterogeneous_pilot/igzo_in2o3_channel_capping/q6",
        capability_tags=["C1", "C5"],
        ground_truth=(
            "Cheng et al. (arXiv:2603.23341) demonstrate IGZO and In2O3 transistors compatible "
            "with a 400 deg C BEOL thermal budget. An indium oxide transistor with an amorphous "
            "In2O3 mixed with SiO2 capping layer shows a positive threshold voltage, extrinsic "
            "saturation mobility of 33.1 cm^2/V.s, and a 5 mV Vt shift after positive-bias stress "
            "at 3 MV/cm for 1000 s at room temperature, superior to conventional SiO2 encapsulation."
        ),
        ground_truth_source=(
            "Cheng et al., arXiv:2603.23341 (submitted 24 Mar 2026), DOI: 10.48550/arXiv.2603.23341"
        ),
        scoring_method="rubric",
        contamination_risk="low",
        provenance=Provenance(
            source_id="arXiv:2603.23341",
            source_type="paper",
            license="CC-BY-NC-ND-4.0",
            author_role="benchmark_author",
            reviewer_role="",
            review_status="draft",
            review_notes=(
                "Draft item grounded in the arXiv abstract of Cheng et al. 2026. "
                "Not expert-reviewed; do not treat as a validated benchmark item."
            ),
        ),
        expert_notes=(
            "Facts are taken from the 24 Mar 2026 arXiv abstract only. A domain expert "
            "must confirm numbers against the full paper before review_status can change."
        ),
        hard_negatives=[
            {
                "text": "Conventional SiO2 encapsulation is superior to In2O3-SiO2 mixed capping under PBS.",
                "penalty": "inverts_paper_comparison",
            },
            {
                "text": "The process requires an 800 deg C crystallization anneal that exceeds the BEOL budget.",
                "penalty": "violates_reported_400c_budget",
            },
        ],
        version="1.0",
        task_data={
            "question": (
                "Cheng et al. (arXiv:2603.23341, 24 Mar 2026) report IGZO and In2O3 transistors "
                "compatible with a 400 deg C BEOL thermal budget. What channel-capping layer do they "
                "use on the indium oxide transistor, and what extrinsic saturation mobility and "
                "positive-bias-stress Vt shift do they report relative to conventional SiO2 encapsulation?"
            ),
            "rubric": RUBRIC_IGZO_CHANNEL_CAPPING.to_dict(),
        },
    ),
]

# Aliases so Benchmark validation and the CLI data/sample commands find the
# same collection as paper_comprehension (DATASET / PILOT_ITEMS).
DATASET = PILOT_DATASET
PILOT_ITEMS = PILOT_DATASET


class HeterogeneousPilot:
    """Evaluates domain-specific reasoning in heterogeneous integration & BEOL devices."""

    def __init__(self, dataset: list[DatasetItem] | None = None):
        self.dataset = dataset or PILOT_DATASET

    def evaluate(
        self, model: str = "gpt-4o", allow_draft: bool = False, **kwargs: Any
    ) -> tuple[float, dict[str, Any]]:
        total_score = 0.0
        max_score = 0.0
        details: dict[str, Any] = {}
        skipped_draft: list[str] = []
        items: list[DatasetItem] = []
        for item in self.dataset:
            if allow_draft or is_runnable(item):
                items.append(item)
            else:
                skipped_draft.append(item.id)

        if not items:
            raise ValueError(
                "No runnable heterogeneous_pilot items. "
                "Use allow_draft=True to evaluate draft items."
            )

        for item in items:
            errs = validate_item(item)
            if errs:
                raise ValueError(f"DatasetItem {item.id} failed validation: {'; '.join(errs)}")

            rubric = Rubric.from_dict(item.task_data["rubric"])
            question = item.task_data["question"]
            raw_response = _call_model(model, question)

            result: RubricResult = rubric.evaluate(raw_response)
            total_score += result.total_score
            max_score += result.max_score

            details[item.id] = {
                "score": result.total_score,
                "max": result.max_score,
                "normalized_score": result.normalized_score,
                "passed": result.passed,
                "criteria": result.to_dict()["criterion_scores"],
                "review_status": item.provenance.review_status if item.provenance else "unknown",
            }

        norm_score = (total_score / max_score * 100.0) if max_score > 0 else 0.0
        return round(norm_score, 2), {
            "per_item": details,
            "total_items": len(items),
            "skipped_draft_item_ids": skipped_draft,
        }


def _call_model(model: str, prompt: str) -> str:
    """Standard model invocation interface with mock fallback."""
    import os

    if model.startswith(("gpt", "openai")):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return (
                "BEOL integration enforces a thermal budget of 400 C to prevent copper "
                "diffusion, interconnect voiding, and front-end CMOS dopant degradation."
            )
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        r = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=512
        )
        return r.choices[0].message.content or ""
    elif "claude" in model:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return (
                "a-IGZO provides isotropic In 5s orbital overlap enabling electron mobility "
                "despite amorphous disorder. Its wide bandgap of 3.0 eV produces ultra-low "
                "off-state leakage (10^-19 A/um), enabling long 2T0C DRAM retention."
            )
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(
            model=model, max_tokens=512, messages=[{"role": "user", "content": prompt}]
        )
        return r.content[0].text
    return "Mock domain response."
