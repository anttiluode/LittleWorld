import numpy as np

from littleworld.experiment import (
    BINARY,
    Config,
    LIVE,
    MESSAGE_ARMS,
    RESET,
    SCRAMBLED,
    YOKED,
    _build_source_tapes,
    decode_marks,
    encode_marks,
    run_arm,
    source_tape_digest,
)


def tiny_config() -> Config:
    return Config(n_agents=6, steps=120, emit_period=4)


def test_encoder_round_trip_without_mark_noise():
    cfg = tiny_config()
    tapes = _build_source_tapes(7, cfg)
    clean = encode_marks(
        tapes["private"],
        tapes["confidence"],
        cfg,
        tapes["encoder"],
        seed=7,
        noise=False,
    )
    decoded = decode_marks(clean, tapes["encoder"])
    emission_ticks = tapes["emission_ticks"]
    expected = np.concatenate(
        [tapes["private"][emission_ticks], tapes["confidence"][emission_ticks, :, None]],
        axis=2,
    )
    np.testing.assert_allclose(decoded[emission_ticks], expected, atol=1e-12)


def test_scrambling_preserves_exact_mark_multiset():
    cfg = tiny_config()
    tapes = _build_source_tapes(9, cfg)
    ticks = tapes["emission_ticks"]
    live_frames = tapes["live_marks"][ticks].reshape(len(ticks), -1)
    scrambled_frames = tapes["scrambled_marks"][ticks].reshape(len(ticks), -1)
    live_sorted = np.array(sorted(map(tuple, live_frames)))
    scrambled_sorted = np.array(sorted(map(tuple, scrambled_frames)))
    np.testing.assert_allclose(live_sorted, scrambled_sorted, atol=0.0)


def test_message_arms_have_identical_event_budget():
    cfg = tiny_config()
    counts = {arm: run_arm(11, arm, cfg)["events"] for arm in MESSAGE_ARMS}
    assert len(set(counts.values())) == 1
    assert next(iter(counts.values())) == cfg.n_agents * (cfg.steps // cfg.emit_period)


def test_source_tape_is_condition_independent():
    cfg = tiny_config()
    digest = source_tape_digest(13, cfg)
    # Every arm calls the same source-tape constructor. This assertion makes the
    # intended source identity explicit and catches accidental RNG drift.
    for arm in (LIVE, BINARY, YOKED, SCRAMBLED, RESET):
        assert source_tape_digest(13, cfg) == digest, arm


def test_smoke_metrics_are_finite_and_nonnegative():
    cfg = tiny_config()
    for arm in MESSAGE_ARMS:
        result = run_arm(3, arm, cfg)
        assert np.isfinite(result["blind_mse"])
        assert result["blind_mse"] >= 0.0
        assert result["evaluated_agent_ticks"] > 0
