"""Emergency Detection Engine.

Three-layer rule-based detection — no LLM, sub-millisecond execution.

Architecture
------------
Layer 1 – Category matchers  : per-emergency-type phrase lists with scores
Layer 2 – Score aggregation  : combine triggered categories into a total score
Layer 3 – Override rules     : certain phrases unconditionally force Critical

Scoring
-------
Each primary phrase match  → base_score (10–30 pts, set per phrase severity)
Amplifier phrase match     → multiplies the category sub-total by 1.5×
Override phrase match      → forces EmergencyLevel.CRITICAL regardless of score

Total score thresholds (see settings.py):
    ≥ 60  → CRITICAL   (call 911 immediately)
    ≥ 30  → HIGH       (go to ER now)
    ≥ 10  → MODERATE   (seek same-day care)
    <  10 → NONE
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

from config.settings import (
    EMERGENCY_SCORE_CRITICAL,
    EMERGENCY_SCORE_HIGH,
    EMERGENCY_SCORE_MODERATE,
)

logger = logging.getLogger(__name__)


# ── Data models ───────────────────────────────────────────────────────────────

class EmergencyLevel(str, Enum):
    NONE = "None"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class CategoryResult:
    """Result for a single emergency category."""
    name: str
    matched_phrases: list[str]
    score: float
    immediate_actions: list[str]


@dataclass
class EmergencyResult:
    """Full output of the Emergency Detection Engine."""
    level: EmergencyLevel
    score: float
    alert_message: str
    immediate_actions: list[str]
    triggered_categories: list[str]
    matched_phrases: list[str]
    override_triggered: bool
    detection_time_ms: float  # execution time for observability

    @property
    def is_emergency(self) -> bool:
        return self.level != EmergencyLevel.NONE

    @property
    def requires_911(self) -> bool:
        return self.level == EmergencyLevel.CRITICAL


# ── Phrase rule structures ─────────────────────────────────────────────────────

class PhraseRule(NamedTuple):
    pattern: str   # regex pattern
    score: int     # base score contribution on match


class CategoryRule(NamedTuple):
    name: str
    display_name: str
    primary_rules: list[PhraseRule]    # each match adds score
    amplifiers: list[str]              # if any match → multiply category score × 1.5
    override_phrases: list[str]        # any match → force CRITICAL immediately
    immediate_actions: list[str]       # shown to user when category triggers


# ── Rule definitions ──────────────────────────────────────────────────────────

_CATEGORIES: list[CategoryRule] = [

    # ── 1. Chest Pain / Cardiac ───────────────────────────────────────────────
    CategoryRule(
        name="chest_pain",
        display_name="Chest Pain / Cardiac Emergency",
        primary_rules=[
            PhraseRule(r"chest\s+pain", 25),
            PhraseRule(r"heart\s+attack", 30),
            PhraseRule(r"crushing\s+chest", 30),
            PhraseRule(r"chest\s+tightness", 20),
            PhraseRule(r"chest\s+pressure", 20),
            PhraseRule(r"chest\s+heaviness", 20),
            PhraseRule(r"pain\s+radiating\s+to\s+(arm|jaw|shoulder|back)", 25),
            PhraseRule(r"radiating\s+to\s+(left\s+arm|arm|jaw|shoulder|back)", 25),
            PhraseRule(r"left\s+arm\s+pain", 20),
            PhraseRule(r"jaw\s+pain", 15),
            PhraseRule(r"myocardial\s+infarction", 30),
            PhraseRule(r"cardiac\s+arrest", 30),
        ],
        amplifiers=["severe", "crushing", "sudden", "radiating", "sweating", "nausea"],
        override_phrases=[
            "cardiac arrest", "heart stopped", "no pulse", "myocardial infarction",
            "heart attack", "crushing chest",
        ],
        immediate_actions=[
            "Call 911 / 112 immediately.",
            "Chew an aspirin (325 mg) if not allergic and conscious.",
            "Loosen any tight clothing.",
            "Keep the person calm and still — do not let them walk.",
            "Be ready to perform CPR if the person becomes unresponsive.",
        ],
    ),

    # ── 2. Breathing Difficulty ───────────────────────────────────────────────
    CategoryRule(
        name="breathing_difficulty",
        display_name="Breathing Difficulty / Respiratory Emergency",
        primary_rules=[
            PhraseRule(r"(can'?t|cannot|unable\s+to)\s+breathe", 30),
            PhraseRule(r"difficulty\s+breathing", 25),
            PhraseRule(r"not\s+breathing", 30),
            PhraseRule(r"stopped\s+breathing", 30),
            PhraseRule(r"shortness\s+of\s+breath", 20),
            PhraseRule(r"choking", 25),
            PhraseRule(r"gasping\s+for\s+(air|breath)", 25),
            PhraseRule(r"respiratory\s+distress", 25),
            PhraseRule(r"airway\s+(blocked|obstructed)", 25),
            PhraseRule(r"blue\s+(lips|fingers|face|skin)", 20),
            PhraseRule(r"cyanosis", 25),
            PhraseRule(r"wheezing\s+severely", 20),
        ],
        amplifiers=["severe", "sudden", "worsening", "rapidly", "extreme"],
        override_phrases=["not breathing", "stopped breathing", "no breath", "airway blocked"],
        immediate_actions=[
            "Call 911 / 112 immediately.",
            "If choking: perform Heimlich maneuver (abdominal thrusts).",
            "If not breathing and unresponsive: begin CPR.",
            "Sit the person upright or in a comfortable position.",
            "Loosen tight clothing around the neck and chest.",
            "Do NOT leave the person alone.",
        ],
    ),

    # ── 3. Heavy / Severe Bleeding ────────────────────────────────────────────
    CategoryRule(
        name="heavy_bleeding",
        display_name="Heavy / Uncontrolled Bleeding",
        primary_rules=[
            PhraseRule(r"heavy\s+bleeding", 25),
            PhraseRule(r"uncontrolled\s+bleeding", 30),
            PhraseRule(r"uncontrollable\s+bleeding", 30),
            PhraseRule(r"bleeding\s+won.?t\s+stop", 30),
            PhraseRule(r"bleeding\s+that\s+won.?t\s+stop", 30),
            PhraseRule(r"bleeding\s+that\s+won\s+t\s+stop", 30),
            PhraseRule(r"profuse\s+bleeding", 25),
            PhraseRule(r"spurting\s+blood", 30),
            PhraseRule(r"blood\s+spurting", 30),
            PhraseRule(r"hemorrhage", 30),
            PhraseRule(r"arterial\s+bleeding", 30),
            PhraseRule(r"soaking\s+through\s+(bandage|cloth|dressing)", 20),
            PhraseRule(r"blood\s+loss", 20),
        ],
        amplifiers=["severe", "massive", "uncontrolled", "profuse", "arterial", "spurting", "won't stop"],
        override_phrases=[
            "spurting blood", "arterial bleeding", "hemorrhage",
            "uncontrolled bleeding", "uncontrollable bleeding",
            "heavy bleeding", "bleeding won't stop", "bleeding wont stop",
        ],
        immediate_actions=[
            "Call 911 / 112 immediately.",
            "Apply firm, direct pressure to the wound with a clean cloth.",
            "Do NOT remove the cloth — add more on top if it soaks through.",
            "If on a limb, elevate above heart level.",
            "Apply a tourniquet only if bleeding is life-threatening and from a limb.",
            "Keep the person warm and lying down to prevent shock.",
        ],
    ),

    # ── 4. Unconsciousness / Unresponsiveness ─────────────────────────────────
    CategoryRule(
        name="unconsciousness",
        display_name="Unconsciousness / Unresponsiveness",
        primary_rules=[
            PhraseRule(r"unconscious", 30),
            PhraseRule(r"unresponsive", 30),
            PhraseRule(r"passed\s+out", 25),
            PhraseRule(r"fainted", 15),
            PhraseRule(r"not\s+responding", 25),
            PhraseRule(r"won'?t\s+wake\s+up", 25),
            PhraseRule(r"can'?t\s+wake\s+(him|her|them|up)", 25),
            PhraseRule(r"lost\s+consciousness", 25),
            PhraseRule(r"blacked\s+out", 20),
            PhraseRule(r"collapse[ds]?", 20),
            PhraseRule(r"no\s+response", 20),
        ],
        amplifiers=["completely", "suddenly", "not waking", "won't respond", "unresponsive"],
        override_phrases=["unconscious", "unresponsive", "not responding", "lost consciousness"],
        immediate_actions=[
            "Call 911 / 112 immediately.",
            "Check for breathing — if absent, begin CPR.",
            "Place in recovery position (on their side) if breathing.",
            "Do NOT give anything by mouth.",
            "Check for a medical alert bracelet.",
            "Stay with the person until help arrives.",
        ],
    ),

    # ── 5. Seizure ────────────────────────────────────────────────────────────
    CategoryRule(
        name="seizure",
        display_name="Seizure / Convulsion",
        primary_rules=[
            PhraseRule(r"seizure", 25),
            PhraseRule(r"convulsion", 25),
            PhraseRule(r"convulsing", 25),
            PhraseRule(r"fitting", 20),
            PhraseRule(r"epileptic\s+(fit|episode|attack)", 25),
            PhraseRule(r"shaking\s+uncontrollably", 20),
            PhraseRule(r"body\s+(jerking|twitching)\s+(violently|uncontrollably)", 20),
            PhraseRule(r"grand\s+mal", 25),
            PhraseRule(r"tonic.clonic", 25),
        ],
        amplifiers=["prolonged", "first time", "not stopping", "minutes", "back to back", "wont stop", "won't stop"],
        override_phrases=[
            "prolonged seizure", "seizure not stopping", "status epilepticus",
            "seizure", "convulsion",
        ],
        immediate_actions=[
            "Call 911 / 112 if seizure lasts more than 5 minutes or is the first ever.",
            "Clear the area of hard or sharp objects.",
            "Do NOT restrain the person or put anything in their mouth.",
            "Gently cushion the head with something soft.",
            "Time the seizure — note start and end time.",
            "After the seizure: place in recovery position and stay until fully conscious.",
        ],
    ),

    # ── 6. Stroke Symptoms ────────────────────────────────────────────────────
    CategoryRule(
        name="stroke",
        display_name="Stroke Symptoms",
        primary_rules=[
            PhraseRule(r"\bstroke\b", 25),
            PhraseRule(r"facial\s+drooping", 25),
            PhraseRule(r"face\s+(drooping|droop|numb|numbness)", 20),
            PhraseRule(r"arm\s+weakness", 20),
            PhraseRule(r"one\s+side\s+(weak|numb|paralyz)", 25),
            PhraseRule(r"slurred\s+speech", 20),
            PhraseRule(r"sudden\s+(numbness|weakness|confusion|headache|vision)", 20),
            PhraseRule(r"can'?t\s+(speak|talk|see|walk|move)", 20),
            PhraseRule(r"sudden\s+severe\s+headache", 20),
            PhraseRule(r"thunderclap\s+headache", 25),
            PhraseRule(r"brain\s+attack", 25),
            PhraseRule(r"tia\b", 20),
            PhraseRule(r"transient\s+ischemic", 20),
        ],
        amplifiers=["sudden", "severe", "one side", "rapidly", "getting worse"],
        override_phrases=["stroke", "brain attack", "thunderclap headache", "facial drooping"],
        immediate_actions=[
            "Call 911 / 112 immediately — time is critical for stroke treatment.",
            "Use the FAST test: Face drooping, Arm weakness, Speech difficulty, Time to call.",
            "Note the exact time symptoms started — doctors need this.",
            "Do NOT give food, water, or medication.",
            "Keep the person calm and lying down with head slightly elevated.",
            "Do NOT let the person 'sleep it off'.",
        ],
    ),

    # ── 7. Severe Burns ───────────────────────────────────────────────────────
    CategoryRule(
        name="severe_burns",
        display_name="Severe Burns",
        primary_rules=[
            PhraseRule(r"severe\s+burn", 25),
            PhraseRule(r"third.degree\s+burn", 30),
            PhraseRule(r"third\s+degree\s+burn", 30),
            PhraseRule(r"deep\s+burn", 20),
            PhraseRule(r"large\s+(area\s+)?burn", 20),
            PhraseRule(r"burn\s+(over|covering)\s+large", 20),
            PhraseRule(r"chemical\s+burn", 20),
            PhraseRule(r"electrical\s+burn", 25),
            PhraseRule(r"burn\s+on\s+(face|hands|genitals|feet|joints)", 20),
            PhraseRule(r"charred\s+skin", 25),
            PhraseRule(r"skin\s+melting", 25),
            PhraseRule(r"inhalation\s+burn", 25),
            PhraseRule(r"burned\s+(airway|lungs|inside)", 25),
        ],
        amplifiers=["severe", "large", "chemical", "electrical", "inhalation", "deep"],
        override_phrases=["third degree burn", "chemical burn face", "inhalation burn", "charred skin"],
        immediate_actions=[
            "Call 911 / 112 immediately for severe, large, or chemical/electrical burns.",
            "Cool the burn with cool (not ice cold) running water for 20 minutes.",
            "Do NOT use ice, butter, or toothpaste.",
            "Remove clothing and jewelry near the burn — unless stuck to skin.",
            "Cover loosely with a clean, non-fluffy material (cling film is ideal).",
            "Treat for shock: keep person warm and lying down.",
        ],
    ),

    # ── 8. Anaphylaxis / Severe Allergic Reaction ─────────────────────────────
    CategoryRule(
        name="anaphylaxis",
        display_name="Anaphylaxis / Severe Allergic Reaction",
        primary_rules=[
            PhraseRule(r"anaphylaxis", 30),
            PhraseRule(r"anaphylactic\s+(shock|reaction)", 30),
            PhraseRule(r"severe\s+allergic\s+reaction", 25),
            PhraseRule(r"epipen", 20),
            PhraseRule(r"throat\s+(swelling|closing|tightening)", 25),
            PhraseRule(r"tongue\s+swelling", 20),
            PhraseRule(r"hives\s+and\s+(breathing|swallowing)", 20),
            PhraseRule(r"allergic\s+reaction\s+with\s+(breathing|swelling)", 20),
        ],
        amplifiers=["severe", "cannot breathe", "throat", "swelling", "bee sting"],
        override_phrases=["anaphylaxis", "anaphylactic shock", "throat closing", "throat swelling"],
        immediate_actions=[
            "Call 911 / 112 immediately.",
            "Use an epinephrine auto-injector (EpiPen) if available — inject into outer thigh.",
            "Lay the person flat with legs raised (unless breathing is difficult — then sit up).",
            "A second EpiPen dose can be given after 5-15 minutes if no improvement.",
            "Do NOT give antihistamines as the primary treatment — they are too slow.",
            "Be prepared to perform CPR if the person becomes unresponsive.",
        ],
    ),

    # ── 9. Overdose / Poisoning ───────────────────────────────────────────────
    CategoryRule(
        name="overdose",
        display_name="Drug Overdose / Poisoning",
        primary_rules=[
            PhraseRule(r"overdose", 25),
            PhraseRule(r"took\s+too\s+many\s+(pills|tablets|drugs|medications)", 25),
            PhraseRule(r"swallowed\s+(poison|bleach|chemical|cleaning)", 25),
            PhraseRule(r"poisoning", 20),
            PhraseRule(r"drug\s+overdose", 25),
            PhraseRule(r"opioid\s+overdose", 30),
            PhraseRule(r"heroin\s+overdose", 30),
            PhraseRule(r"naloxone", 20),
            PhraseRule(r"carbon\s+monoxide", 25),
            PhraseRule(r"toxic\s+(ingestion|exposure)", 20),
        ],
        amplifiers=["unconscious", "not breathing", "blue lips", "unresponsive", "opioid"],
        override_phrases=["opioid overdose", "heroin overdose", "not breathing overdose"],
        immediate_actions=[
            "Call 911 / 112 immediately.",
            "Call Poison Control: 1-800-222-1222 (US) or national equivalent.",
            "Do NOT induce vomiting unless directed by Poison Control.",
            "If opioid overdose is suspected, administer Naloxone (Narcan) if available.",
            "Keep the person awake and on their side if breathing.",
            "Note what was taken, how much, and when.",
        ],
    ),
]

# ── Override phrases (unconditional Critical triggers) ─────────────────────────
# Collected from all categories for a single fast O(n) scan.
_ALL_OVERRIDE_PATTERNS: list[tuple[re.Pattern, str]] = []
for _cat in _CATEGORIES:
    for _phrase in _cat.override_phrases:
        _ALL_OVERRIDE_PATTERNS.append(
            (re.compile(re.escape(_phrase), re.IGNORECASE), _cat.display_name)
        )

# Pre-compile all primary and amplifier patterns per category
@dataclass
class _CompiledCategory:
    rule: CategoryRule
    primary_compiled: list[tuple[re.Pattern, int]]   # (pattern, score)
    amplifier_compiled: list[re.Pattern]


_COMPILED: list[_CompiledCategory] = []
for _cat in _CATEGORIES:
    _COMPILED.append(
        _CompiledCategory(
            rule=_cat,
            primary_compiled=[
                (re.compile(pr.pattern, re.IGNORECASE), pr.score)
                for pr in _cat.primary_rules
            ],
            amplifier_compiled=[
                re.compile(re.escape(amp), re.IGNORECASE)
                for amp in _cat.amplifiers
            ],
        )
    )


# ── Alert messages by level ────────────────────────────────────────────────────

_ALERT_MESSAGES: dict[EmergencyLevel, str] = {
    EmergencyLevel.CRITICAL: (
        "🚨 CRITICAL EMERGENCY DETECTED — Call 911 / 112 immediately. "
        "This situation is potentially life-threatening. Do not wait."
    ),
    EmergencyLevel.HIGH: (
        "⚠️ HIGH-RISK EMERGENCY — Go to the nearest Emergency Room immediately. "
        "Do not drive yourself — call for help."
    ),
    EmergencyLevel.MODERATE: (
        "⚡ URGENT MEDICAL CONCERN — Seek medical attention today. "
        "Call your doctor or visit an urgent care clinic as soon as possible."
    ),
    EmergencyLevel.NONE: "",
}


# ── Core detection logic ───────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lowercase and collapse extra whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _evaluate_category(
    compiled: _CompiledCategory,
    normalized_text: str,
) -> CategoryResult | None:
    """Evaluate one category against input text.

    Returns a CategoryResult if any primary phrase matched, else None.
    """
    matched_phrases: list[str] = []
    raw_score: float = 0.0

    for pattern, score in compiled.primary_compiled:
        if pattern.search(normalized_text):
            matched_phrases.append(pattern.pattern)
            raw_score += score

    if not matched_phrases:
        return None

    # Check amplifiers — if any match, multiply this category's score
    amplified = any(amp.search(normalized_text) for amp in compiled.amplifier_compiled)
    final_score = raw_score * 1.5 if amplified else raw_score

    return CategoryResult(
        name=compiled.rule.name,
        matched_phrases=matched_phrases,
        score=final_score,
        immediate_actions=list(compiled.rule.immediate_actions),
    )


def _check_overrides(normalized_text: str) -> list[str]:
    """Return display names of categories whose override phrases matched."""
    triggered = []
    for pattern, display_name in _ALL_OVERRIDE_PATTERNS:
        if pattern.search(normalized_text):
            triggered.append(display_name)
    # Deduplicate while preserving order
    return list(dict.fromkeys(triggered))


def _score_to_level(score: float, override_triggered: bool) -> EmergencyLevel:
    if override_triggered or score >= EMERGENCY_SCORE_CRITICAL:
        return EmergencyLevel.CRITICAL
    if score >= EMERGENCY_SCORE_HIGH:
        return EmergencyLevel.HIGH
    if score >= EMERGENCY_SCORE_MODERATE:
        return EmergencyLevel.MODERATE
    return EmergencyLevel.NONE


def _build_actions(category_results: list[CategoryResult]) -> list[str]:
    """Merge immediate actions from all triggered categories, deduplicated."""
    seen: set[str] = set()
    actions: list[str] = []
    # Always put 911 call first
    call_911 = "Call 911 / 112 immediately."
    actions.append(call_911)
    seen.add(call_911)
    for cat in category_results:
        for action in cat.immediate_actions:
            if action not in seen:
                seen.add(action)
                actions.append(action)
    return actions


# ── Public API ─────────────────────────────────────────────────────────────────

def detect_emergency(text: str) -> EmergencyResult:
    """Run the full emergency detection pipeline on input text.

    This is the primary public function. Call this from analyzers and the UI.

    Args:
        text: Raw user input — symptom description, free text, etc.

    Returns:
        EmergencyResult with level, score, actions, and all matched evidence.
    """
    t_start = time.perf_counter()

    if not text or not text.strip():
        return EmergencyResult(
            level=EmergencyLevel.NONE,
            score=0.0,
            alert_message="",
            immediate_actions=[],
            triggered_categories=[],
            matched_phrases=[],
            override_triggered=False,
            detection_time_ms=0.0,
        )

    normalized = _normalize(text)

    # Layer 3: override check first (fastest exit path for severe cases)
    override_categories = _check_overrides(normalized)
    override_triggered = bool(override_categories)

    # Layer 1 + 2: evaluate all categories, aggregate scores
    category_results: list[CategoryResult] = []
    all_matched: list[str] = []

    for compiled in _COMPILED:
        result = _evaluate_category(compiled, normalized)
        if result:
            category_results.append(result)
            all_matched.extend(result.matched_phrases)

    total_score = sum(r.score for r in category_results)

    # Apply override multiplier to ensure score clears Critical threshold
    if override_triggered and total_score < EMERGENCY_SCORE_CRITICAL:
        total_score = float(EMERGENCY_SCORE_CRITICAL)

    level = _score_to_level(total_score, override_triggered)
    triggered_names = [r.name for r in category_results]

    # Build immediate actions only when there's an emergency
    actions = _build_actions(category_results) if level != EmergencyLevel.NONE else []

    t_end = time.perf_counter()
    elapsed_ms = (t_end - t_start) * 1000

    if level != EmergencyLevel.NONE:
        logger.warning(
            "Emergency detected: level=%s score=%.1f categories=%s time=%.2fms",
            level.value,
            total_score,
            triggered_names,
            elapsed_ms,
        )

    return EmergencyResult(
        level=level,
        score=round(total_score, 1),
        alert_message=_ALERT_MESSAGES[level],
        immediate_actions=actions,
        triggered_categories=triggered_names,
        matched_phrases=list(dict.fromkeys(all_matched)),
        override_triggered=override_triggered,
        detection_time_ms=round(elapsed_ms, 3),
    )


# ── Backward-compatible shim ───────────────────────────────────────────────────
# The original analyzer.py calls is_emergency(text) → (bool, list[str]).
# Keep this working without touching the existing caller.

def is_emergency(text: str) -> tuple[bool, list[str]]:
    """Backward-compatible wrapper around detect_emergency().

    Returns:
        (triggered: bool, matched_phrases: list[str])
    """
    result = detect_emergency(text)
    return result.is_emergency, result.matched_phrases
