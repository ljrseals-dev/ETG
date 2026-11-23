# Future Work

The ETG is a conceptual proposal with a reference implementation. This document separates what is planned, in order of how testable it is, from what is only speculation. Each item names the result that would count as success, so it can also fail.

## A. Known issues fixed in v0.2.0 (and still to be reflected in the paper)

| # | Issue found in v0.1 / manuscript | Status |
|---|---|---|
| 1 | Repo ρ was a SHA-256 hash of the vertex list. That is non-monotone and non-structural, which contradicts the paper's properties (monotone, bounded, non-injective) and the claim that it is "robust under low SNR". | Replaced by the paper's feature map; hash kept as `sigil()` and labelled an identifier. |
| 2 | `nasal_resonance()` crashed whenever the graph had a cycle (`G.edges(u, v, data=True)`). The shipped example has no cycle, so it silently returned all zeros. | Fixed; new example contains a real cycle. |
| 3 | Edge key was the transfer type, so two edges of the same type between the same pair collapsed into one. That breaks the multigraph definition. | Unique key per edge. |
| 4 | Manuscript `paths_of_length` calls `nx.all_simple_paths(..., source=None, target=None)`, which raises `NodeNotFound`. | Replaced by `simple_paths(source, target)`; manuscript code block needs the same change. |
| 5 | Manuscript text says `W_max` is the maximum *total* weight in the graph; code uses the maximum *single-edge* weight. | Documented in code; the paper should pick one. |
| 6 | Manuscript §5.5 uses a cycle `L1→L2→L3→L1` that §5.3's graph does not contain. | Example repaired in repo; paper to match. |
| 7 | With `σ(x)=x/(1+x)` and features normalised to ≤ 1, a coordinate only reaches the lower half of its band (σ(1) = 0.5). The paper states the full ranges. | Open: either state the reachable range or change the normalisation. |
| 8 | README and DEFINITION.md claimed novelty, "newsworthiness" and propulsion applications. | Removed. |

## B. Near term (weeks): things a reviewer can check

### B1. Test suite and the precedence-conflict check
Property tests (e.g. Hypothesis): ρ is bounded, monotone in each feature, deterministic under a fixed edge-selection policy; `precedence_conflicts()` returns exactly the cycles of the precedence-only subgraph.
**Success:** all properties hold on randomly generated graphs; any counterexample is a bug report.

### B2. Date-consistency validator
Many vertices carry dates. A precedence edge `u→v` should imply `date(u) ≤ date(v)`. Report violations separately from structural cycles.
**Success:** on a hand-built correspondence set, the validator flags the known seeded errors and nothing else.

### B3. Per-type weight calibration
Weights are comparable only within a type. Define an optional per-type normalisation (rank or z-score within type) so cross-type path weights stop being meaningless sums.
**Success:** a stated rule, plus a test showing rankings are invariant to rescaling any single type's weights.

## C. Medium term (months): formal and interoperable

### C1. Lean 4 formalisation
Define the 5-tuple, then prove: (i) ρ is total on finite paths; (ii) outputs lie in the stated bands; (iii) each coordinate is monotone in its feature; (iv) for concatenated paths `P ++ Q`, `f_L` and `f_W` add and `f_T` is bounded by `f_T(P) + f_T(Q)`, giving a bound on `ρ(P ++ Q)`; (v) a precedence-only cycle exists iff the precedence subgraph is not a DAG. Start from existing finite-graph libraries and extend with typed multiedges.
**Success:** `lake build` passes with no `sorry`.

### C2. Translation to W3C PROV
Specify a mapping and its losses.

| ETG type | Candidate PROV / related term | Loss |
|---|---|---|
| influence | `prov:wasInfluencedBy` | weight has no PROV slot (keep as annotation) |
| citation | `prov:wasDerivedFrom` or a citation vocabulary such as CiTO | derivation is stronger than citation; choose per use |
| precedence | no direct term; temporal ordering over activities/entities | needs timestamps |
| embedding, modulation | domain-specific extension | outside core PROV |

**Success:** round-trip a test graph ETG → PROV-N/RDF → ETG and list exactly which attributes survive.

### C3. Extensible type set
Five types are fixed. Decide whether to allow user-defined types with a declared PROV parent, and what that does to ρ's `f_T / 5` normalisation.

## D. Empirical (a year): does the Voice mean anything?

### D1. Listening study
Question: can people tell structures apart by ρ? Design: forced-choice discrimination ("same or different path structure?") and a classification task (chain vs cycle vs fan-in) using rendered ρ output. Compare against a control that maps the same features to pitch only, so formant structure is tested rather than assumed. Report accuracy, sensitivity (d′), and just-noticeable differences for each coordinate. Pre-register the analysis, and include a screen-reader-using group to test the accessibility claim.
**Success:** discrimination reliably above chance and at least matching the pitch-only control. **Failure is informative:** it would say the formant framing adds nothing, and ρ should be dropped or redesigned.

### D2. Real-corpus evaluation
Load a public correspondence or citation dataset into the ETG (letters as vertices, citation and reply links as typed edges). Measure how many precedence conflicts it finds, hand-verify a sample for precision, and compare with the same queries on a single-type citation graph.
**Success:** a stated precision figure with the verification protocol, and at least one query type the single-type graph cannot express.

## E. Speculative (explicitly untested)

These are hypotheses. None should be described as a capability until a result exists.

- **Compact signalling.** A quantised formant triple is a small code. With `q` levels per formant it carries `3·log₂ q` bits, and ρ is non-injective, so it is a lossy summary rather than a message format. Before any hardware talk, a channel model is required: noise, bandwidth, and a comparison against ordinary error-correcting codes. A hash-based sigil would be the better identifier here; ρ's meaningful structure and a collision-resistant ID are different tools.
- **Telemetry provenance.** Use an ETG to record how a state packet was derived through relays, and ρ as an audible health cue. Needs a real telemetry log and an operator study.
- **Propulsion monitoring.** The ETG records relations; it neither models nor controls a physical system. The phrase "nasal-aeronautic propulsion" from earlier drafts has no definition or evidence and is retired.
- **Music.** Modulation edges over motif graphs, with ρ as an analytic aid. Evaluate with musicologists before calling it a method.

## F. Repository and release
- Rename `basic-maths` → `epistolary-transfer-graph`; archive via GitHub→Zenodo release `v0.2.0`.
- Add `CITATION.cff` with confirmed affiliation (ORCID optional).
- State the licence split clearly: code MIT, concept CC0 (Zenodo takes one licence per record; put the CC0 note in the description).
- Keep one canonical definition. The repo, the manuscript and the Zenodo text should say the same thing about ρ.
