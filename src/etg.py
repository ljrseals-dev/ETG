"""
Epistolary Transfer Graph (ETG), v0.2.0
=======================================
A typed, weighted, directed multigraph for precedence / attribution claims,
with an exploratory spectral mapping (rho) from paths and cycles to formants.

This is a conceptual proposal with a reference implementation. The spectral
mapping has not been empirically validated.

v0.2.0 changes (see docs/FUTURE_WORK.md, "Known issues fixed"):
  * rho now implements the monotone feature map of the paper (length, weight,
    type diversity). The earlier SHA-256 mapping is kept as `sigil()`, an
    identifier, not a meaningful spectrum.
  * Parallel edges of the same type are no longer collapsed.
  * Cycle handling no longer crashes (networkx edges() call fixed).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple
import hashlib
import json

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None

TRANSFER_TYPES = ("precedence", "influence", "embedding", "citation", "modulation")
_ALIASES = {"algebraic_embedding": "embedding", "harmonic_modulation": "modulation"}

F1_RANGE = (250.0, 850.0)
F2_RANGE = (600.0, 2400.0)
F3_RANGE = (2400.0, 3200.0)


@dataclass
class Vertex:
    id: str
    kind: str = "letter"  # letter | claim | motif | packet
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    target: str
    transfer_type: str
    strength: float = 1.0
    label: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.transfer_type = _ALIASES.get(self.transfer_type, self.transfer_type)
        if self.transfer_type not in TRANSFER_TYPES:
            raise ValueError(f"unknown transfer type {self.transfer_type!r}; expected one of {TRANSFER_TYPES}")
        if self.strength < 0:
            raise ValueError("strength (lambda) must be non-negative")


def _sigma(x: float) -> float:
    """Soft ceiling: maps [0, inf) into [0, 1)."""
    return x / (1.0 + x)


def _lerp(lo_hi: Tuple[float, float], x: float) -> float:
    lo, hi = lo_hi
    return lo + (hi - lo) * x


class EpistolaryTransferGraph:
    def __init__(self, name: str = "ETG"):
        self.name = name
        self.vertices: Dict[str, Vertex] = {}
        self.edges: List[Edge] = []

    # -- construction -------------------------------------------------
    def add_vertex(self, v: Vertex) -> None:
        if v.id in self.vertices:
            raise ValueError(f"Vertex {v.id} already exists")
        self.vertices[v.id] = v

    def add_edge(self, e: Edge) -> None:
        if e.source not in self.vertices or e.target not in self.vertices:
            raise ValueError("Both endpoints must already be vertices")
        self.edges.append(e)

    # -- networkx view (rebuilt on demand; always consistent) ---------
    def as_networkx(self):
        if nx is None:
            raise RuntimeError("networkx is required for graph algorithms")
        G = nx.MultiDiGraph()
        for vid, v in self.vertices.items():
            G.add_node(vid, kind=v.kind, **v.metadata)
        for i, e in enumerate(self.edges):
            # unique integer key per edge: parallel same-type edges survive
            G.add_edge(e.source, e.target, key=i, transfer_type=e.transfer_type,
                       strength=e.strength, label=e.label)
        return G

    # -- queries ------------------------------------------------------
    def cycles(self, transfer_type: Optional[str] = None) -> List[List[str]]:
        """Simple cycles, optionally using only edges of one type."""
        G = self.as_networkx()
        if transfer_type is not None:
            transfer_type = _ALIASES.get(transfer_type, transfer_type)
            H = nx.DiGraph()
            H.add_nodes_from(G.nodes)
            H.add_edges_from((u, v) for u, v, d in G.edges(data=True)
                             if d["transfer_type"] == transfer_type)
            return [list(c) for c in nx.simple_cycles(H)]
        return [list(c) for c in nx.simple_cycles(nx.DiGraph(G))]

    def precedence_conflicts(self) -> List[List[str]]:
        """Cycles made only of precedence edges: 'A before B before A' cannot
        all be true. This is the ETG's most practical consistency check."""
        return self.cycles("precedence")

    def simple_paths(self, source: str, target: str, max_len: Optional[int] = None):
        G = nx.DiGraph(self.as_networkx())
        return [list(p) for p in nx.all_simple_paths(G, source, target, cutoff=max_len)]

    # -- rho: the Voice ----------------------------------------------
    def _w_max(self) -> float:
        # NOTE: maximum single-edge weight (the paper text says "maximum total
        # weight"; see docs/FUTURE_WORK.md, Known issues).
        return max((e.strength for e in self.edges), default=1.0) or 1.0

    def rho(self, path: List[str], l_max: float = 10.0, policy: str = "first") -> Dict[str, float]:
        """Map a path (or a closed cycle, first vertex repeated at the end) to
        a formant triple. policy picks one edge when several join a pair:
        'first' (insertion order) | 'max' (heaviest)."""
        if len(path) < 2:
            raise ValueError("path must contain at least one edge")
        chosen: List[Edge] = []
        for u, v in zip(path[:-1], path[1:]):
            options = [e for e in self.edges if e.source == u and e.target == v]
            if not options:
                raise ValueError(f"no edge from {u} to {v}")
            chosen.append(max(options, key=lambda e: e.strength) if policy == "max" else options[0])
        f_l = len(chosen)
        f_w = sum(e.strength for e in chosen)
        f_t = len({e.transfer_type for e in chosen})
        return {
            "f1": round(_lerp(F1_RANGE, _sigma(f_l / l_max)), 2),
            "f2": round(_lerp(F2_RANGE, _sigma(f_w / self._w_max())), 2),
            "f3": round(_lerp(F3_RANGE, _sigma(f_t / 5.0)), 2),
            "length": f_l, "weight": round(f_w, 4), "types": f_t,
        }

    def rho_cycle(self, cycle: List[str], **kw) -> Dict[str, float]:
        return self.rho(list(cycle) + [cycle[0]], **kw)

    nasal_resonance = rho_cycle  # backwards-compatible name from v0.1

    # -- sigil: an identifier, NOT a spectrum -------------------------
    @staticmethod
    def sigil(path: Iterable[str]) -> str:
        """Stable short fingerprint of an ordered vertex sequence. Useful as a
        name for a structure; carries no structural meaning in its digits."""
        return hashlib.sha256("-".join(path).encode()).hexdigest()[:12]

    # -- serialisation ------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "vertices": [{"id": v.id, "kind": v.kind, "metadata": v.metadata} for v in self.vertices.values()],
            "edges": [{"source": e.source, "target": e.target, "transfer_type": e.transfer_type,
                       "strength": e.strength, "label": e.label, "metadata": e.metadata} for e in self.edges],
        }

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "EpistolaryTransferGraph":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        g = cls(name=data.get("name", "ETG"))
        for v in data["vertices"]:
            g.add_vertex(Vertex(v["id"], v.get("kind", "letter"), v.get("metadata", {})))
        for e in data["edges"]:
            g.add_edge(Edge(e["source"], e["target"], e["transfer_type"], e.get("strength", 1.0),
                            e.get("label", ""), e.get("metadata", {})))
        return g

    def __repr__(self) -> str:
        return f"<ETG '{self.name}' |V|={len(self.vertices)} |E|={len(self.edges)}>"
