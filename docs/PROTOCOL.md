# LittleWorld v0 protocol freeze

## Question

Can a population of stateful receivers use **small continuous event marks that are coupled to sender state** to predict a hidden dynamical world better than matched controls when every communicating arm has the same event schedule?

This is a computational mechanism test. It does **not** test whether biological action potentials use these exact coordinates, whether language emerges, or whether the fixed sender/receiver transform evolved.

## Construction

- 12 agents.
- 1,200 ticks per seed.
- Hidden world is a 2-D unit direction with slow drift and occasional jumps.
- Each agent receives a noisy direct observation on 28% of ticks.
- Private sender state is a leaky local estimator and confidence trace. It is built once per seed and is **independent of communication condition**.
- Every four ticks every agent emits exactly one event.
- A marked event contains three continuous coordinates: a fixed orthogonal mixing of `[private_x, private_y, confidence]` plus small noise.
- Receivers invert that fixed transform and integrate peer estimates into a social state.
- Receiver susceptibility is state-dependent: low private confidence increases the gain applied to an incoming peer estimate.
- Primary score is mean squared error on **blind agent-ticks** only, when that receiver has no direct observation on the current tick.

## Matched controls

1. `live_marked_stateful` — current sender marks, persistent social receiver state.
2. `live_binary_stateful` — identical sender/event timing, mark coordinates removed.
3. `yoked_marked_stateful` — identical event timing, marked packets taken from an independent hidden-world trajectory.
4. `scrambled_marked_stateful` — exact live marked-packet multiset, permuted across emission times.
5. `live_marked_reset` — live marks, but social receiver state is erased each tick.

The first four communication controls preserve the same number of emitted events. The scrambled arm preserves the exact marked-packet multiset.

## Development/canonical separation

Development used seeds below 200. The canonical panel is **12 untouched seeds, 200–211**. This file and the implementation are committed before that panel is run.

## Frozen v0 pass rule

`live_marked_stateful` must satisfy all of the following on the 12 canonical seeds:

- median blind-MSE improvement vs binary >= 20%;
- median blind-MSE improvement vs yoked >= 15%;
- median blind-MSE improvement vs scrambled >= 15%;
- median blind-MSE improvement vs reset >= 10%;
- at least 9/12 paired-seed wins against each control;
- identical event budgets across all five communicating arms.

No threshold or model parameter is to be changed after the canonical panel is inspected. A failed criterion remains a failed result.

## Why this is stricter than the supplied waveform demo

The supplied Gemini script writes the latent drive directly into synthetic waveform features and then fits the inverse decoder on those same generated examples. That is useful as a picture of the hypothesis but it cannot establish that waveform geometry carries independently useful state. LittleWorld instead keeps a fixed event budget and attacks **contingency**, **mark content**, **mark/state correspondence**, and **receiver memory** separately.
