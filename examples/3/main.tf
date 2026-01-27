/*
 * This example showcases multiple cases of redundant `depends_on` declarations
 * in various parts of a dependency chain. It is also a good opportunity to use
 * the tool's graph export to visualize the dependencies.
 */

provider "graph" {}

// Case A

resource "graph_node" "a" {
    references = [graph_node.b]
    depends_on = [graph_node.c]
}

resource "graph_node" "b" {
    references = [graph_node.c]
}

resource "graph_node" "c" {}

// Case B

resource "graph_node" "d" {
    references = [graph_node.e]
    depends_on = [graph_node.f]
}

resource "graph_node" "e" {
    depends_on = [graph_node.f]
}

resource "graph_node" "f" {}

// Case C

resource "graph_node" "g" {
    depends_on = [graph_node.h, graph_node.i]
}

resource "graph_node" "h" {
    references = [graph_node.i]
}

resource "graph_node" "i" {}

// Case D

resource "graph_node" "j" {
    references = [graph_node.k]
    depends_on = [graph_node.m]
}

resource "graph_node" "k" {
    depends_on = [graph_node.l]
}

resource "graph_node" "l" {
    references = [graph_node.m]
}

resource "graph_node" "m" {}

// Case e


resource "graph_node" "n" {
    depends_on = [graph_node.o, graph_node.p]
}

resource "graph_node" "o" {
    depends_on = [graph_node.p]
}
resource "graph_node" "p" {}
