# Note on the supplied Gemini waveform demo

The supplied script was useful as an architectural sketch:

`sender state -> marked event -> receiver inverse -> changed receiver state`

but its decoding comparison is not evidence for that architecture. The synthetic waveform generator explicitly makes sharpness, decay and width functions of the hidden drive, and the linear decoder is fitted to the same generated spike samples it is evaluated on. The result therefore largely recovers information that the script itself inserted.

LittleWorld keeps the useful question and discards the circular demonstration. The v0 gate asks whether state-coupled marks remain useful after matched event timing, a causally stale yoked stream, a mark/time scrambling attack, and receiver-memory erasure.

The biological action-potential paper is motivation only. LittleWorld v0 is a synthetic dynamical-system experiment, not a neuron model.
