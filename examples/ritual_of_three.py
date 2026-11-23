#!/usr/bin/env python3
"""The Ritual of Three: build a small ETG, find a contradiction, hear a Voice.

Run from anywhere:  python examples/ritual_of_three.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from etg import Edge, EpistolaryTransferGraph, Vertex  # noqa: E402


def main():
    g = EpistolaryTransferGraph("ritual-of-three")
    for vid in ("L1", "L2", "L3"):
        g.add_vertex(Vertex(vid, "letter"))
    g.add_vertex(Vertex("C1", "claim"))

    g.add_edge(Edge("L1", "L2", "precedence", 0.9))
    g.add_edge(Edge("L2", "L3", "precedence", 0.8))
    g.add_edge(Edge("L3", "L1", "precedence", 0.7))   # <- contradicts the other two
    g.add_edge(Edge("L2", "C1", "influence", 0.6))
    g.add_edge(Edge("L1", "C1", "embedding", 0.7))

    print(g)
    print("precedence conflicts:", g.precedence_conflicts())

    circle = g.precedence_conflicts()[0]
    print("voice of the circle :", g.rho_cycle(circle))
    print("sigil of the circle :", g.sigil(circle))
    print("voice of L1->L2->C1 :", g.rho(["L1", "L2", "C1"]))


if __name__ == "__main__":
    main()
