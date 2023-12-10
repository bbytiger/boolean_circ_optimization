from abc import ABC, abstractmethod
import circuitgraph as cg


class SynthesisCircuit(cg.Circuit):
    def __init__(self, circ: cg.Circuit):
        self.c = circ

    def pred(self, nd):
        if self.c.graph.has_node(nd):
            return list(self.c.graph.predecessors(nd))
        raise KeyError(f"Node {nd} not found.")

    def succ(self, nd):
        if self.c.graph.has_node(nd):
            return list(self.c.graph.successors(nd))
        raise KeyError(f"Node {nd} not found.")

    def isAnd(self, nd):
        return self.c.type(nd) == "and"

    def isXor(self, nd):
        return self.c.type(nd) == "xor"

    def setType(self, nd, t):
        self.c.graph.nodes[nd]["type"] = t

    def depth_l(self, v):
        predessors = self.pred(v)
        if len(predessors) == 0:
            return 0
        return max([self.depth_l(u) for u in predessors]) + self.isAnd(v)

    def depth_r(self, v):
        successors = self.succ(v)
        if len(successors) == 0:
            return 0
        return max([self.depth_r(u) + self.isAnd(u) for u in successors])

    def depth_max(self):
        nodes = self.c.nodes()
        maxl = max([self.depth_l(v) for v in nodes])
        maxr = max([self.depth_r(v) for v in nodes])
        assert maxl == maxr
        return maxl

    def count_AND(self):
        return len(list(filter(lambda v: self.isAnd(v), self.c.nodes())))

    def critical_nodes(self):
        """
        Generate a list of critical nodes in the given circuit
        (i.e. nodes satisfying l(v) + r(v) = max_depth(C))

        Args:
            c (cg.Circuit): The input circuit.

        Returns:
            List[cg.Node]: A list of critical nodes in the circuit.
        """
        maxd = self.depth_max()
        return list(
            filter(
                lambda v: self.depth_l(v) + self.depth_r(v) == maxd,
                self.c.nodes(),
            )
        )

    def count_AND_in_path(self, path):
        count = 0
        for v in path:
            if self.isAnd(v):
                count += 1
        return count

    # TODO: go back and re-optimize this critical path search
    def critical_paths(self):
        critical_node_set = set(self.critical_nodes())
        and_critical_nodes = list(
            filter(
                lambda v: self.isAnd(v),
                critical_node_set,
            )
        )

        def special_dfs(path, paths):
            datum = path[-1]
            if len(path) != 1 and datum in and_critical_nodes:
                assert self.count_AND_in_path(path) == 2
                paths += [path]
            else:
                assert datum in critical_node_set
                for val in self.succ(datum):
                    if val in critical_node_set:
                        new_path = path + [val]
                        paths = special_dfs(new_path, paths)
            return paths

        paths = []
        for and_node in and_critical_nodes:
            node_paths = special_dfs([and_node], [])
            paths += node_paths
        return paths

    def or_rewrite(self, nd):
        """a OR b = (a XOR b) XOR (a AND b)"""
        if self.c.type(nd) == "or":
            # extract predecessors and successors
            predecessors = self.pred(nd)
            successors = self.succ(nd)
            assert len(predecessors) == 2

            # build new circ topo
            node_xor_l_uid = self.c.uid("rewrite")
            self.c.add(node_xor_l_uid, "xor", fanin=predecessors)
            node_and_uid = self.c.uid("rewrite")
            self.c.add(node_and_uid, "and", fanin=predecessors)
            is_output = self.c.is_output(nd)
            self.c.remove(nd)
            self.c.add(
                nd,
                "xor",
                fanin=[node_xor_l_uid, node_and_uid],
                fanout=successors,
                output=is_output,
            )

    def not_rewrite(self, nd):
        """NOT a = 1 XOR a"""
        if self.c.type(nd) == "not":
            # extract predecessors and successors
            predecessors = self.pred(nd)
            successors = self.succ(nd)
            assert len(predecessors) == 1

            # build the new circ topo
            node_a = predecessors[0]
            node_l = self.c.uid("rewrite")
            self.c.add(node_l, "1")
            is_output = self.c.is_output(nd)
            self.c.remove(nd)
            self.c.add(
                nd,
                "xor",
                fanin=[node_l, node_a],
                fanout=successors,
                output=is_output,
            )

    def do_and_xor_transform(self):
        for nd in list(self.c.nodes()):
            self.or_rewrite(nd)
            self.not_rewrite(nd)

    def print_node_info(self, nd):
        if nd not in self.c.nodes():
            print(f"{nd} not found")
            return
        print(f"{nd} node_type", self.c.type(nd))
        print(f"{nd} succ", self.succ(nd))
        print(f"{nd} pred", self.pred(nd))

    def copy(self):
        return SynthesisCircuit(circ=self.c.copy())


class RewriteRule(ABC):
    @abstractmethod
    def is_rewrite_target(sc: SynthesisCircuit, p: list[str]):
        pass

    @abstractmethod
    def do_rewrite(sc: SynthesisCircuit, p: list[str]):
        pass

    @abstractmethod
    def filter_condition(sc: SynthesisCircuit, p: list[str]):
        pass


class AndAssociative(RewriteRule):
    def is_rewrite_target(sc: SynthesisCircuit, p: list[str]):
        return len(p) == 2 and sc.isAnd(p[0]) and sc.isAnd(p[1])

    def do_rewrite(sc: SynthesisCircuit, p: list[str]):
        assert AndAssociative.is_rewrite_target(sc, p)
        firstANDpred = sc.pred(p[0])
        secondANDpred = sc.pred(p[1])
        assert len(firstANDpred) == 2
        assert len(secondANDpred) == 2 and p[0] in secondANDpred

        new_and_node = sc.c.uid("rewrite")
        xnode = firstANDpred[0]
        ynode = firstANDpred[1]
        znode = list(filter(lambda x: x not in p, secondANDpred))[0]

        # make new connections
        sc.c.disconnect(znode, p[1])
        sc.c.disconnect(p[0], p[1])
        sc.c.add(new_and_node, "and", fanin=[ynode, znode])
        sc.c.connect(xnode, p[1])
        sc.c.connect(new_and_node, p[1])

    def filter_condition(sc: SynthesisCircuit, p: list[str]):
        firstANDpred = sc.pred(p[0])
        secondANDpred = sc.pred(p[1])
        assert len(firstANDpred) == 2
        assert len(secondANDpred) == 2 and p[0] in secondANDpred

        xnode = firstANDpred[0]
        ynode = firstANDpred[1]
        znode = list(filter(lambda x: x not in p, secondANDpred))[0]

        xdepth = sc.depth_l(xnode)
        ydepth = sc.depth_l(ynode)
        zdepth = sc.depth_l(znode)

        print("xdepth", xdepth, "ydepth", ydepth, "zdepth", zdepth)

        return ydepth < xdepth and zdepth < xdepth


class XorDistributive(RewriteRule):
    def is_rewrite_target(sc: SynthesisCircuit, p: list[str]):
        return (
            len(p) > 2
            and sc.count_AND_in_path(p) == 2
            and sc.isAnd(p[0])
            and sc.isAnd(p[-1])
        )

    def do_rewrite(sc: SynthesisCircuit, p: list[str]):
        assert XorDistributive.is_rewrite_target(sc, p)
        XORpred = sc.pred(p[-2])
        ANDpred = sc.pred(p[-1])
        assert len(XORpred) == 2 and len(ANDpred) == 2

        xnode = XORpred[0]
        ynode = XORpred[1]
        assert p[-2] in ANDpred
        znode = list(filter(lambda x: x != p[-2], ANDpred))[0]

        new_and_node_1 = sc.c.uid("rewrite")
        sc.c.add(new_and_node_1, "and", fanin=[xnode, znode])

        new_and_node_2 = sc.c.uid("rewrite")
        sc.c.add(new_and_node_2, "and", fanin=[ynode, znode])

        # rearrange circuit connections
        sc.c.disconnect(p[-2], p[-1])
        sc.c.disconnect(znode, p[-1])
        assert len(sc.pred(p[-1])) == 0

        sc.setType(p[-1], "xor")
        sc.c.connect(new_and_node_1, p[-1])
        sc.c.connect(new_and_node_2, p[-1])

    def filter_condition(sc: SynthesisCircuit, p: list[str]):
        l1v = sc.depth_l(p[-2])
        will_reduce_depth = True
        for v in [p[-2], p[-1]]:
            will_reduce_depth &= min([sc.depth_l(u) for u in sc.pred(v)]) < l1v - 1
        return will_reduce_depth


def priority_c(sc: SynthesisCircuit, p: list[str]):
    crit_nd_set = set(sc.critical_nodes())
    total = set()
    for nd in p:
        for n in sc.pred(nd):
            if n in crit_nd_set:
                total.add(n)
    return len(total)


def run_minimization_heuristic(
    sc: SynthesisCircuit,
    rw_list: list[RewriteRule],
    priority_func,
    max_iter=100,
):
    iter = 0
    cout = sc.copy()
    while iter < max_iter:
        iter += 1
        continue_cnt = 0
        for rw in rw_list:
            coutp = cout.copy()
            critical_paths = coutp.critical_paths()
            filtered_cpath = list(
                filter(
                    lambda p: (
                        rw.is_rewrite_target(coutp, p) and rw.filter_condition(coutp, p)
                    ),
                    critical_paths,
                )
            )
            if len(filtered_cpath) == 0:
                print("no paths left to rewrite for rule ", rw)
                continue_cnt += 1
                continue

            filtered_cpath.sort(
                reverse=True,
                key=lambda p: priority_func(coutp, p),
            )
            rewrite_target_path = filtered_cpath[0]
            rw.do_rewrite(coutp, rewrite_target_path)

            # rewrite to tracker if output depth is lower
            if cout.depth_max() > coutp.depth_max():
                cout = coutp

        if continue_cnt == len(rw_list):
            print("no paths left to rewrite for all rules")
            break

    return cout


if __name__ == "__main__":
    c = cg.from_file("switch_behav.v")
    sc = SynthesisCircuit(c)

    edges = c.edges()
    print(len(edges))

    first_edge = list(edges)[0]
    print(first_edge)

    nodes = c.nodes()
    print(type(nodes))
    print(len(nodes))

    print(first_edge[0] in nodes)
    print(first_edge[1] in nodes)

    andGates = c.filter_type("and")
    print(andGates)

    and0 = list(andGates)[0]
    print(and0)
    print(sc.isAnd(and0))

    print(c.filter_type("xor"))
    print(set(c.type(nodes)))

    inputGates = c.filter_type("input")
    # print(inputGates)

    # bufGates = c.filter_type("buf")
    # print(bufGates, "bufGates")
    # g1 = list(bufGates)[0]
    # print("predecessors buf g1", sc.pred(g1))
    # print("successors bug g1", sc.succ(g1))

    input0 = list(inputGates)[0]
    print(input0)
    print("predecessors", sc.pred(input0))
    print("successors", sc.succ(input0))

    # going to have to use dp to avoid the recursion limit here
    print(sc.depth_max())
    print(sc.critical_nodes())

    print("----- Before rewrite operations -----")

    sc.print_node_info("\\alu_op_ext[0]")
    sc.print_node_info("\\alu_op_ext[1]")

    print("----- After rewrite operations -----")

    sc.do_and_xor_transform()

    sc.print_node_info("\\alu_op_ext[0]")
    sc.print_node_info("\\alu_op_ext[1]")

    print(set(c.type(c.nodes())))

    cg.to_file(sc.c, "switch_rewrite.v", behavioral=True)

    # test code for visualizing the circuit
    # cg.utils.visualize(c, "test.png", suppress_output=True)
