/*
 * This example showcases multiple cases of redundant `depends_on` declarations
 * in various parts of a dependency chain. It is also a good opportunity to use
 * the tool's graph export to visualize the dependencies.
 */

// Case A

resource "node" "a" {
    references = [node.b]
    depends_on = [node.c]
}

resource "node" "b" {
    references = [node.c]
}

resource "node" "c" {}

// Case B

resource "node" "d" {
    references = [node.e]
    depends_on = [node.f]
}

resource "node" "e" {
    depends_on = [node.f]
}

resource "node" "f" {}

// Case C

resource "node" "g" {
    depends_on = [node.h, node.i]
}

resource "node" "h" {
    references = [node.i]
}

resource "node" "i" {}

// Case D

resource "node" "j" {
    references = [node.k]
    depends_on = [node.m]
}

resource "node" "k" {
    depends_on = [node.l]
}

resource "node" "l" {
    references = [node.m]
}

resource "node" "m" {}

// Case e


resource "node" "n" {
    depends_on = [node.o, node.p]
}

resource "node" "o" {
    depends_on = [node.p]
}
resource "node" "p" {}
