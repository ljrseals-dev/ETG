# ⟁ The ETG Grimoire

### *Epistolary Transfer Graph — a spellbook for who-said-what-first*

```
        L1 ═══precedence═══▶ L2
         ▲                    ║
         ║                influence
   precedence                 ▼
         ║                   C1  ◀── embedding ── L1
        L3 ◀══precedence═══ (the circle must not close)
```

> *Every claim has a true name, a lineage, and a voice.*
> *This book teaches you to write the lineage down, catch it lying, and say it aloud.*

**Status:** v0.2.0 · concept + reference implementation · Python · code MIT, concept CC0
**Honest label:** the spectral "voice" (ρ) is an *exploratory* mapping. No listener has been tested. The magic below is a way of *remembering* the math, not a claim about the world.

---

## The Craft in one breath

Scholars argue about priority in prose: letters, footnotes, acknowledgments. The ETG writes those arguments down as a **graph you can query**, with five kinds of thread so that "A cited B" is never confused with "A came before B."

Then, if you wish, it lets you **hear** a thread-path as a vowel.

That is the whole book. Everything else is detail.

---

## Lexicon: the spell and the math

| In the Craft | In the math | Plainly |
|---|---|---|
| **Names** (`V`) | finite vertex set | the things being related: letters, claims, motifs, telemetry packets |
| **Threads** (`E`) | finite *multiset* of directed edges | a relation from one Name to another; two Names may be bound by several threads |
| **Colour of a thread** (`τ`) | map `E → T`, `T` has five elements | *precedence · influence · embedding · citation · modulation* |
| **Mana** (`λ`) | map `E → ℝ≥0` | strength / confidence / count. Compare mana only between threads of the same colour |
| **A Walk** | path `v₀,…,v_k` | follow threads head-to-tail |
| **A Circle** | cycle, `v₀ = v_k` | a Walk that returns to where it began |
| **The Voice** (`ρ`) | partial function paths/cycles → `(F₁,F₂,F₃)` | three formant frequencies, i.e. a vowel-like sound |
| **The Soft Ceiling** | `σ(x) = x/(1+x)` | squeezes `[0,∞)` into `[0,1)`; you can climb toward the top, never touch it |
| **A Sigil** | SHA-256 of the vertex sequence, first 12 hex | a stable *name* for a structure. It identifies; it does not describe |

### The five colours

- 🜂 **precedence** — *u came before v.* Asserted, never assumed transitive.
- 🜄 **influence** — *u shaped v.* Weaker than precedence; may be diffuse or mutual.
- 🜃 **embedding** — *u sits inside v* as a substructure or homomorphic image.
- 🜁 **citation** — *v cites u.* A documentary fact; says nothing about influence.
- ✦ **modulation** — *u is transformed into v* (transposition, inversion…), mostly for motifs.

---

## First rite: bind the Names, tie the Threads

```python
from etg import EpistolaryTransferGraph, Vertex, Edge

g = EpistolaryTransferGraph("ritual-of-three")
for n in ("L1", "L2", "L3"): g.add_vertex(Vertex(n, "letter"))
g.add_vertex(Vertex("C1", "claim"))

g.add_edge(Edge("L1", "L2", "precedence", 0.9))
g.add_edge(Edge("L2", "L3", "precedence", 0.8))
g.add_edge(Edge("L3", "L1", "precedence", 0.7))   # a lie hides here
g.add_edge(Edge("L2", "C1", "influence",  0.6))
g.add_edge(Edge("L1", "C1", "embedding",  0.7))
```

## Second rite: catch the lie

```python
g.precedence_conflicts()
# [['L1', 'L2', 'L3']]
```

*L1 before L2 before L3 before L1* cannot all be true. **A Circle made only of precedence threads is a contradiction in the record.** This is the ETG's most practical spell, and it needs no sound at all. (Circles of *other* colours are fine: mutual influence is ordinary.)

## Third rite: speak the Voice

The Voice reads three things off a Walk and turns each into a formant:

| Feature | Meaning | Becomes | Range |
|---|---|---|---|
| `f_L` | number of threads | `F₁ = 250 + 600·σ(f_L / 10)` | 250–850 Hz |
| `f_W` | total mana | `F₂ = 600 + 1800·σ(f_W / w_max)` | 600–2400 Hz |
| `f_T` | distinct colours used | `F₃ = 2400 + 800·σ(f_T / 5)` | 2400–3200 Hz |

```python
g.rho_cycle(["L1", "L2", "L3"])
# {'f1': 388.46, 'f2': 1909.09, 'f3': 2533.33, 'length': 3, 'weight': 2.4, 'types': 1}
```

Checking it by hand, as any apprentice should:

- `f_L = 3` → `σ(0.3) = 0.3/1.3 ≈ 0.2308` → `F₁ = 250 + 600·0.2308 ≈ 388.46`
- `f_W = 0.9+0.8+0.7 = 2.4`, `w_max = 0.9` → `σ(2.667) ≈ 0.7273` → `F₂ = 600 + 1800·0.7273 ≈ 1909.09`
- `f_T = 1` → `σ(0.2) ≈ 0.1667` → `F₃ = 2400 + 800·0.1667 ≈ 2533.33`

Longer Walks raise F₁. Heavier Walks raise F₂. Walks that mix more colours raise F₃. That monotonicity is the whole spell.

---

## The Laws (theorems, in robes)

1. **Law of Finiteness.** Every finite Walk has a Voice. *(ρ is total on finite paths that exist.)*
2. **Law of Bounds.** A Voice never leaves its three bands. *(Range of ρ ⊆ the three intervals, because σ < 1.)*
3. **Law of Ascent.** More length, mana or colour never lowers the matching formant. *(Monotonicity of each coordinate.)*
4. **Law of Shared Voices.** Different Walks can sound alike. *(ρ is non-injective: it is a signature, not an encoding. Use a Sigil if you need to tell them apart.)*
5. **Law of Unclosed Threads.** The graph records what was *asserted*, not what follows. Precedence is not closed under transitivity; ask with a Walk when you want the consequence.

## What this magic is **not**

- Not a lie detector for scholars. It checks *internal consistency of what you entered*.
- Not a validated sonification. Whether anyone can hear a precedence chain is an open experiment (see the Future Work).
- Not a spacecraft, propulsion, or telemetry system. Earlier drafts of this repo said otherwise; those claims were removed because nothing was built or tested.
- Not a replacement for W3C PROV. It is a small vocabulary that is meant to map *into* PROV.

---

## Casting from the shell

```bash
python -m pip install networkx
python examples/ritual_of_three.py
```

`numpy` and `scipy` are only needed if you add a renderer that turns a Voice into a WAV file (sketched in the paper, not shipped here).

## Where the Grimoire is going

The honest map lives in [`docs/FUTURE_WORK.md`](docs/FUTURE_WORK.md): Lean proofs, a PROV translation, a listening study, a real corpus, and the known flaws of v0.1 that v0.2 already repaired.

## Citation

> Seals, L. J., Jr. *The Epistolary Transfer Graph: A Typed Directed Multigraph for Modeling Precedence and Attribution Among Claims, with an Exploratory Spectral Mapping.* Version 0.2.0, 2026.

See `CITATION.cff`. Add your institution and ORCID before release.

*⟁ A circle of precedence that closes is a sentence that cannot be true. Write the record carefully.*
