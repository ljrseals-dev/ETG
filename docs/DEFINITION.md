# Formal definition of the Epistolary Transfer Graph (v0.2.0)

An ETG is a 5-tuple `G = (V, E, τ, λ, ρ)`.

- `V`: finite set of vertices (letters, claims, motifs, packets; the kind is metadata).
- `E`: finite multiset of directed edges `(u, v)`.
- `τ : E → T`, `T = {precedence, influence, embedding, citation, modulation}`.
- `λ : E → ℝ≥0`. Comparable only within one type.
- `ρ`: partial function from distinguished finite paths and cycles to `(F₁, F₂, F₃)`.

## ρ

For a path of `k` edges with chosen realisations `e₁…e_k`:

- `f_L = k`, `f_W = Σ λ(eᵢ)`, `f_T = |{τ(eᵢ)}|`
- `σ(x) = x / (1 + x)`
- `F₁ = 250 + 600·σ(f_L / 10)`, `F₂ = 600 + 1800·σ(f_W / W_max)`, `F₃ = 2400 + 800·σ(f_T / 5)`

`W_max` in the reference implementation is the largest single-edge weight. When several edges join a pair, one is chosen by a stated policy (`first` or `max`).

Properties: total on finite existing paths; bounded; each coordinate monotone in its feature; non-injective. Perceptual validity is **not** established.

## Sigil

`sigil(path)` is a SHA-256 prefix of the ordered vertex ids. It is an identifier. It has no spectral or structural meaning.

## Relation to prior work

Citation graphs, W3C PROV and sonification research cover parts of this ground. The ETG is a small domain vocabulary, not a replacement for any of them. No novelty claim is made beyond the specific combination.
