from graphframes import GraphFrame
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

# Vertex aliases of the motif, so a path can have at most len(NODE_NAMES) - 1 = 7 segments.
NODE_NAMES = "abcdefgh"


def motif(segments: int) -> str:
    """Chain motif with `segments` edges: 2 -> "(a)-[e1]->(b); (b)-[e2]->(c)"."""
    nodes = NODE_NAMES[: segments + 1]
    return "; ".join(f"({u})-[e{i}]->({v})" for i, (u, v) in enumerate(zip(nodes, nodes[1:]), start=1))


def simple_paths(g: GraphFrame, segments: int, start: str, end: str) -> DataFrame:
    """Routes of exactly `segments` flights that visit no airport twice.

    `start` and `end` are SQL conditions on the first and last airport, with `{v}` standing for
    the airport's alias, e.g. "{v}.country = 'Germany'". Vertices need `code` and edges
    `distance_km`. Returns segments, route ("TXL → AMS → EDI") and total distance_km.
    """
    nodes = NODE_NAMES[: segments + 1]
    distinct = [f"{u}.id != {v}.id" for i, u in enumerate(nodes) for v in nodes[i + 1:]]
    condition = " AND ".join([start.format(v=nodes[0]), end.format(v=nodes[-1]), *distinct])
    distance: Column = sum((F.col(f"e{i}.distance_km") for i in range(1, segments + 1)), F.lit(0.0))
    return g.find(motif(segments)).filter(condition).select(
        F.lit(segments).alias("segments"),
        F.concat_ws(" → ", *(F.col(f"{v}.code") for v in nodes)).alias("route"),
        distance.alias("distance_km"),
    )
