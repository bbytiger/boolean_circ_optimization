from synth import (
    SynthesisCircuit,
    AndAssociative,
    XorDistributive,
    run_minimization_heuristic,
    priority_c,
)
import circuitgraph as cg

c = cg.from_file("ctrl_opt.v")
print(set(c.type(c.nodes())))
sc = SynthesisCircuit(c)

sc.do_and_xor_transform()
print("depth_max", sc.depth_max())
print(set(sc.c.type(c.nodes())))
print("# of ANDs", sc.count_AND())

outc = run_minimization_heuristic(
    sc,
    [XorDistributive, AndAssociative],
    priority_c,
)
print("new depth_max", outc.depth_max())
cg.to_file(outc.c, "ctrl_rewrite.v", behavioral=True)
