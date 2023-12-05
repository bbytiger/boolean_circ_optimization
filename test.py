from synth import (
    SynthesisCircuit,
    AndAssociative,
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

# cg.to_file(sc.c, "i2c_opt_and_xor.v", behavioral=True)

P = sc.critical_paths()
print(P)

# F1 = list(
#     filter(
#         lambda p: (AndAssociative.is_rewrite_target(sc, p)),
#         P,
#     )
# )
# print(F1)

# F2 = list(
#     filter(
#         lambda p: (AndAssociative.filter_condition(sc, p)),
#         F1,
#     )
# )
# print(F2)

run_minimization_heuristic(sc, AndAssociative, priority_c)
print("new depth_max", sc.depth_max())
cg.to_file(sc.c, "ctrl_and_associative_rewrite.v", behavioral=True)
