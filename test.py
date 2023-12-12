from synth import (
    SynthesisCircuit,
    AndAssociative,
    XorDistributive,
    run_minimization_heuristic,
    priority_c,
)
import circuitgraph as cg

c = cg.from_file("router_opt.v")
print(set(c.type(c.nodes())))
sc = SynthesisCircuit(c)
print("depth_max", sc.depth_max())
print(set(sc.c.type(c.nodes())))
print("# of ANDs", sc.count_AND())
print("size of circuit", len(sc.c.nodes()))

sc.do_and_xor_transform()
print("depth_max", sc.depth_max())
print(set(sc.c.type(c.nodes())))
print("# of ANDs", sc.count_AND())
print("size of circuit", len(sc.c.nodes()))

outc = run_minimization_heuristic(
    sc,
    [XorDistributive, AndAssociative],
    priority_c,
)
print("depth_max", sc.depth_max())
print(set(sc.c.type(c.nodes())))
print("# of ANDs", sc.count_AND())
print("size of circuit", len(sc.c.nodes()))
cg.to_file(outc.c, "router_rewrite.v", behavioral=True)
