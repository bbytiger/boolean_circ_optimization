from synth import SynthesisCircuit, AndAssociative
import circuitgraph as cg

c = cg.from_file("ctrl_opt.v")
sc = SynthesisCircuit(c)
sc.do_and_xor_transform()

cg.to_file(sc.c, "ctrl_and_xor_rewrite.v", behavioral=True)

P = sc.critical_paths()
print(P)
F1 = list(
    filter(
        lambda p: (AndAssociative.is_rewrite_target(sc, p)),
        P,
    )
)
print(F1)


AndAssociative.do_rewrite(sc, F1[0])
cg.to_file(sc.c, "ctrl_and_associative_rewrite.v", behavioral=True)


""" F2 = list(
    filter(
        lambda p: (AndAssociative.filter_condition(sc, p)),
        F1,
    )
)
print(F2)
 """
