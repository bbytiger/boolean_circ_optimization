from synth import SynthesisCircuit
import circuitgraph as cg

c = cg.from_file("ctrl.v")
sc = SynthesisCircuit(c)
sc.do_and_xor_transform()
P = sc.critical_paths()
print(P)
