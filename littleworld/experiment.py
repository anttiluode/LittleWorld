"""LittleWorld v0: marked-event communication in a matched dynamical world.

The scientific gate is intentionally smaller than the browser ecology.  A hidden
2-D world direction evolves on a fixed tape. Twelve agents observe it
intermittently and noisily. Their private estimator is condition-independent.
Every four ticks every agent emits one event. In the marked arm the event carries
three continuous coordinates produced by a fixed mixing of the sender's private
state and confidence. Receivers decode those marks and integrate them through a
state-dependent susceptibility. Controls keep the event schedule fixed while
removing contingency, mark content, or receiver memory.

This is a constructed proof-of-mechanism, not a claim of biological realism or
emergent language.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterable, Mapping

import numpy as np


LIVE = "live_marked_stateful"
BINARY = "live_binary_stateful"
YOKED = "yoked_marked_stateful"
SCRAMBLED = "scrambled_marked_stateful"
RESET = "live_marked_reset"
NO_MESSAGE = "no_message_stateful"
MESSAGE_ARMS = (LIVE, BINARY, YOKED, SCRAMBLED, RESET)
ALL_ARMS = MESSAGE_ARMS + (NO_MESSAGE,)


@dataclass(frozen=True)
class Config:
    n_agents: int = 12
    steps: int = 1200
    emit_period: int = 4
    observation_probability: float = 0.28
    observation_noise: float = 0.35
    private_decay: float = 0.90
    confidence_decay: float = 0.94
    social_decay: float = 0.90
    social_gain: float = 0.55
    jump_probability: float = 0.018
    angle_noise: float = 0.045
    mark_noise: float = 0.04

    def to_dict(self) -> dict:
        return asdict(self)


def _world_tape(rng: np.random.Generator, cfg: Config) -> np.ndarray:
    """Return a unit-vector hidden-world tape of shape [steps, 2]."""
    angles = np.empty(cfg.steps, dtype=float)
    angle = rng.uniform(-np.pi, np.pi)
    for tick in range(cfg.steps):
        if rng.random() < cfg.jump_probability:
            angle = rng.uniform(-np.pi, np.pi)
        else:
            angle += rng.normal(0.0, cfg.angle_noise)
        angles[tick] = angle
    return np.column_stack((np.cos(angles), np.sin(angles)))


def _private_tape(
    seed: int,
    cfg: Config,
    world: np.ndarray,
    noise_offset: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate condition-independent local observations and private sender state."""
    rng = np.random.default_rng(seed + noise_offset)
    masks = rng.random((cfg.steps, cfg.n_agents)) < cfg.observation_probability
    noise = rng.normal(
        0.0,
        cfg.observation_noise,
        size=(cfg.steps, cfg.n_agents, 2),
    )

    private = np.zeros((cfg.n_agents, 2), dtype=float)
    confidence = np.zeros(cfg.n_agents, dtype=float)
    private_tape = np.zeros((cfg.steps, cfg.n_agents, 2), dtype=float)
    confidence_tape = np.zeros((cfg.steps, cfg.n_agents), dtype=float)

    for tick in range(cfg.steps):
        private *= cfg.private_decay
        confidence *= cfg.confidence_decay
        visible = masks[tick]
        if np.any(visible):
            observations = world[tick] + noise[tick]
            private[visible] += (1.0 - cfg.private_decay) * observations[visible]
            confidence[visible] += 1.0 - cfg.confidence_decay
        private_tape[tick] = private
        confidence_tape[tick] = np.clip(confidence, 0.0, 1.0)

    return masks, private_tape, confidence_tape


def _orthogonal_encoder(seed: int) -> np.ndarray:
    """A deterministic non-identity three-coordinate sender transform."""
    rng = np.random.default_rng(seed + 999)
    matrix = rng.normal(size=(3, 3))
    q, _ = np.linalg.qr(matrix)
    return q


def encode_marks(
    private_tape: np.ndarray,
    confidence_tape: np.ndarray,
    cfg: Config,
    encoder: np.ndarray,
    seed: int,
    noise: bool = True,
) -> np.ndarray:
    """Encode [private_x, private_y, confidence] into emitted three-mark packets."""
    rng = np.random.default_rng(seed + 888)
    marks = np.zeros((cfg.steps, cfg.n_agents, 3), dtype=float)
    for tick in range(0, cfg.steps, cfg.emit_period):
        sender_state = np.column_stack(
            (private_tape[tick], confidence_tape[tick])
        )
        mark = sender_state @ encoder.T
        if noise:
            mark += rng.normal(0.0, cfg.mark_noise, size=mark.shape)
        marks[tick] = mark
    return marks


def decode_marks(marks: np.ndarray, encoder: np.ndarray) -> np.ndarray:
    """Invert the fixed orthogonal sender transform."""
    return marks @ encoder


def _build_source_tapes(seed: int, cfg: Config) -> dict:
    """Build all source tapes once so communication arms cannot alter senders."""
    world = _world_tape(np.random.default_rng(seed + 1), cfg)
    masks, private, confidence = _private_tape(seed, cfg, world, noise_offset=100)
    encoder = _orthogonal_encoder(seed)
    live_marks = encode_marks(private, confidence, cfg, encoder, seed)

    donor_world = _world_tape(np.random.default_rng(seed + 5001), cfg)
    _, donor_private, donor_confidence = _private_tape(
        seed, cfg, donor_world, noise_offset=5100
    )
    donor_marks = encode_marks(
        donor_private,
        donor_confidence,
        cfg,
        encoder,
        seed + 5200,
    )

    emission_ticks = np.arange(0, cfg.steps, cfg.emit_period)
    permutation = np.random.default_rng(seed + 7000).permutation(len(emission_ticks))
    scrambled_marks = np.zeros_like(live_marks)
    for destination_index, source_index in enumerate(permutation):
        scrambled_marks[emission_ticks[destination_index]] = live_marks[
            emission_ticks[source_index]
        ]

    return {
        "world": world,
        "masks": masks,
        "private": private,
        "confidence": confidence,
        "encoder": encoder,
        "live_marks": live_marks,
        "donor_marks": donor_marks,
        "scrambled_marks": scrambled_marks,
        "emission_ticks": emission_ticks,
    }


def source_tape_digest(seed: int, cfg: Config | None = None) -> dict:
    """Small test/debug view proving all arms can share the exact source tape."""
    cfg = cfg or Config()
    tapes = _build_source_tapes(seed, cfg)
    return {
        "world_sum": float(np.sum(tapes["world"])),
        "mask_count": int(np.sum(tapes["masks"])),
        "private_sum": float(np.sum(tapes["private"])),
        "confidence_sum": float(np.sum(tapes["confidence"])),
        "live_mark_sum": float(np.sum(tapes["live_marks"])),
    }


def run_arm(seed: int, arm: str, cfg: Config | None = None) -> dict:
    """Run one communication arm on one deterministic world/source tape."""
    cfg = cfg or Config()
    if arm not in ALL_ARMS:
        raise ValueError(f"unknown arm: {arm}")

    tapes = _build_source_tapes(seed, cfg)
    world = tapes["world"]
    masks = tapes["masks"]
    private = tapes["private"]
    confidence = tapes["confidence"]
    encoder = tapes["encoder"]
    live_marks = tapes["live_marks"]
    donor_marks = tapes["donor_marks"]
    scrambled_marks = tapes["scrambled_marks"]

    social = np.zeros((cfg.n_agents, 2), dtype=float)
    squared_error_sum = 0.0
    evaluated_coordinates = 0
    evaluated_agent_ticks = 0
    event_count = 0

    for tick in range(cfg.steps):
        if arm == RESET:
            social[:] = 0.0
        else:
            social *= cfg.social_decay

        if tick % cfg.emit_period == 0:
            if arm == BINARY:
                marks = np.zeros_like(live_marks[tick])
                event_count += cfg.n_agents
            elif arm == YOKED:
                marks = donor_marks[tick]
                event_count += cfg.n_agents
            elif arm == SCRAMBLED:
                marks = scrambled_marks[tick]
                event_count += cfg.n_agents
            elif arm == NO_MESSAGE:
                marks = None
            else:
                marks = live_marks[tick]
                event_count += cfg.n_agents

            if marks is not None:
                decoded = decode_marks(marks, encoder)
                sender_estimate = decoded[:, :2]
                sender_confidence = np.clip(decoded[:, 2], 0.0, 1.0)
                weighted_total = np.sum(
                    sender_estimate * sender_confidence[:, None], axis=0
                )
                confidence_total = float(np.sum(sender_confidence))

                for receiver in range(cfg.n_agents):
                    denominator = confidence_total - float(sender_confidence[receiver])
                    if denominator > 1e-9:
                        message_estimate = (
                            weighted_total
                            - sender_estimate[receiver]
                            * float(sender_confidence[receiver])
                        ) / denominator
                    else:
                        message_estimate = np.zeros(2, dtype=float)

                    # The same packet acts differently depending on current receiver
                    # confidence: low-confidence receivers are more susceptible.
                    receiver_confidence = float(confidence[tick, receiver])
                    susceptibility = 1.0 / (
                        1.0 + np.exp(6.0 * (receiver_confidence - 0.45))
                    )
                    social[receiver] += (
                        cfg.social_gain * susceptibility * message_estimate
                    )

        private_weight = confidence[tick, :, None]
        response = private_weight * private[tick] + (1.0 - private_weight) * social

        blind = ~masks[tick]
        if np.any(blind):
            residual = response[blind] - world[tick]
            squared_error_sum += float(np.sum(residual * residual))
            evaluated_agent_ticks += int(np.sum(blind))
            evaluated_coordinates += int(np.sum(blind)) * 2

    return {
        "seed": seed,
        "arm": arm,
        "blind_mse": squared_error_sum / evaluated_coordinates,
        "evaluated_agent_ticks": evaluated_agent_ticks,
        "events": event_count,
    }


def run_panel(
    seeds: Iterable[int],
    cfg: Config | None = None,
    arms: Iterable[str] = MESSAGE_ARMS,
) -> dict:
    cfg = cfg or Config()
    seed_list = list(seeds)
    arm_list = list(arms)
    runs: Dict[str, list[dict]] = {arm: [] for arm in arm_list}
    for seed in seed_list:
        for arm in arm_list:
            runs[arm].append(run_arm(seed, arm, cfg))
    return {
        "config": cfg.to_dict(),
        "seeds": seed_list,
        "arms": arm_list,
        "runs": runs,
    }


def summarize(panel: Mapping) -> dict:
    runs = panel["runs"]
    medians = {
        arm: float(np.median([row["blind_mse"] for row in rows]))
        for arm, rows in runs.items()
    }
    event_counts = {
        arm: sorted({int(row["events"]) for row in rows})
        for arm, rows in runs.items()
    }

    live = np.array([row["blind_mse"] for row in runs[LIVE]], dtype=float)
    comparisons = {}
    for arm in (BINARY, YOKED, SCRAMBLED, RESET):
        other = np.array([row["blind_mse"] for row in runs[arm]], dtype=float)
        comparisons[arm] = {
            "median_relative_improvement": float(np.median((other - live) / other)),
            "paired_seed_wins": int(np.sum(live < other)),
            "seed_count": int(len(live)),
        }

    return {
        "median_blind_mse": medians,
        "event_counts": event_counts,
        "comparisons_to_live": comparisons,
    }


def frozen_gate(summary: Mapping) -> dict:
    """Return the v0 decision from protocol-frozen thresholds."""
    cmp = summary["comparisons_to_live"]
    thresholds = {
        BINARY: 0.20,
        YOKED: 0.15,
        SCRAMBLED: 0.15,
        RESET: 0.10,
    }
    checks = {}
    for arm, minimum in thresholds.items():
        checks[f"improvement_vs_{arm}"] = (
            cmp[arm]["median_relative_improvement"] >= minimum
        )
        checks[f"paired_wins_vs_{arm}"] = cmp[arm]["paired_seed_wins"] >= 9

    message_event_sets = [summary["event_counts"][arm] for arm in MESSAGE_ARMS]
    checks["matched_event_budget"] = all(
        counts == message_event_sets[0] for counts in message_event_sets[1:]
    )

    return {
        "thresholds": {
            "minimum_relative_improvement": thresholds,
            "minimum_paired_seed_wins": "9/12",
            "matched_event_budget": True,
        },
        "checks": checks,
        "pass": bool(all(checks.values())),
    }
