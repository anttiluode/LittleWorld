# LittleWorld

**A tiny artificial ecology for asking one narrow question:** what happens when a stateful system emits a small state-dependent event into another stateful system, and the receiver's present state changes what that event does?

The working abstraction is:

```text
sender history -> sender state -> marked event
                              |
                              v
receiver state -> susceptibility -> new receiver state -> behavior
```

The long-term idea is an ecology in which behavior changes the world, the changed world changes later behavior, and generations can eventually inherit learning machinery rather than hand-authored messages. **v0 is deliberately smaller.** It isolates the communication mechanism before adding evolution, language, or biological interpretation.

## v0: matched hidden-world prediction gate

Twelve agents live on the same hidden 2-D dynamical world. Their direct sensors are intermittent and noisy. Every four ticks every agent emits one event. In the marked arm that event has three continuous coordinates derived from the sender's private state and confidence. Receivers integrate those packets through a state-dependent susceptibility: when their own confidence is low, the same event has more effect.

The critical point is that the sender/private-state tape is fixed before the communication arm is chosen. The five communicating arms therefore differ only in what crosses the channel or how the receiver retains it:

- **LIVE + MARKED + STATEFUL** — current state-coupled marks.
- **BINARY** — same event times, marks removed.
- **YOKED** — same event times, marked packets from an independent world trajectory.
- **SCRAMBLED** — exact live marked-packet multiset, permuted across emission times.
- **RESET** — current marks, but receiver social state is erased every tick.

The primary metric is prediction MSE on receiver ticks with **no current direct observation**. See [`docs/PROTOCOL.md`](docs/PROTOCOL.md) for the frozen canonical panel and pass rule.

## Run locally

```bash
python -m pip install -e '.[test]'
pytest
python scripts/run_v0.py --out results/v0.json
```

## Canonical v0 result — seeds 200–211

The protocol above was committed before the canonical panel was run. The frozen gate **passed** without changing the model or thresholds afterward.

| Arm | Median blind MSE ↓ | Live relative improvement | Paired live wins |
|---|---:|---:|---:|
| LIVE + marked + stateful | **0.3100** | — | — |
| Binary | 0.4432 | **29.7%** | **12/12** |
| Yoked | 0.4691 | **33.7%** | **12/12** |
| Scrambled | 0.4382 | **29.2%** | **12/12** |
| Reset receiver | 0.4251 | **26.8%** | **12/12** |

Every communicating arm emitted exactly **3,600 events per seed**. Full machine-readable receipt: [`results/v0.json`](results/v0.json).

This is a positive result for the **constructed mechanism**, not evidence that biology or culture uses this exact encoding. In particular, v0 supplies a compatible encoder/decoder rather than learning one.

## Live microscope

The repository is configured for static GitHub Pages:

**https://anttiluode.github.io/LittleWorld/**

`index.html` is a browser-only closed-loop playground using the same conceptual pieces: local sensing, resident state, marked emissions, state-dependent receiver gain, movement, and resource relocation after capture. The browser ecology is an **illustration**, not the frozen scientific receipt. The Python gate above is the evidence layer.

## Gemini waveform demo: retained question, discarded proof

The supplied waveform script was a good picture of `state -> mark -> inverse receiver`, but it generated waveform features directly from the hidden drive and fitted its decoder to those same synthetic samples. That makes the successful inverse decoding largely true by construction. LittleWorld keeps the architectural question and adds destructive controls instead. See [`docs/GEMINI_DEMO_NOTE.md`](docs/GEMINI_DEMO_NOTE.md).

## Claim boundary

If v0 passes, the earned statement is only:

> In this constructed synthetic system, low-dimensional state-coupled event marks plus receiver memory improve hidden-world prediction under matched event budgets, and the advantage depends on current contingency, mark/state correspondence, and persistent receiver state.

It would **not** show that biological spikes carry these exact marks, that receivers literally reconstruct a sender's latent state, that language emerged this way, or that evolution selected this architecture. The fixed mark encoder/decoder is supplied in v0. Learning that transform, then allowing it to survive generations, is later work.
