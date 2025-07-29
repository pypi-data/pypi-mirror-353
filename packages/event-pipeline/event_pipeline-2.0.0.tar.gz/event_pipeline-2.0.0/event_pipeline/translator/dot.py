import typing
from event_pipeline.task import PipelineTask, PipeType

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def process_parallel_nodes(
    parallel_nodes: typing.Deque[PipelineTask], nodes_list: typing.List[str]
) -> typing.Tuple[typing.Optional[str], typing.Optional[str]]:
    """Process a group of parallel execution nodes and return node ID"""
    if not parallel_nodes:
        return None, None

    node_id = parallel_nodes[0].id
    node_label = "{" + "|".join([n.event for n in parallel_nodes]) + "}"
    node_text = f'\t"{node_id}" [label="{node_label}", shape=record, style="filled,rounded", fillcolor=lightblue]\n'

    if node_text not in nodes_list:
        nodes_list.append(node_text)

    return node_id, node_label


def generate_dot_from_task_state(task_state: PipelineTask) -> str:
    root = task_state.get_root()
    nodes = []
    edges = []

    f = StringIO()

    f.write("digraph G {\n")
    f.write('\tnode [fontname="Helvetica", fontsize=11]\n')
    f.write('\tedge [fontname="Helvetica", fontsize=10]\n')

    iterator = task_state.bf_traversal(root)

    while True:
        try:
            node: PipelineTask = next(iterator)
        except StopIteration:
            break

        """
        If a node is the last node in the parallel execution queue, we should ignore it,
        as it has already been processed. Instead, we should focus on its children.
        """
        parent = node.parent_node
        if (
            parent
            and parent.on_success_pipe == PipeType.PARALLELISM
            and node.on_success_pipe != PipeType.PARALLELISM
        ):
            continue

        text = node.get_dot_node_data()
        if text and text not in nodes:
            nodes.append(text)

        if node.is_parallel_execution_node:
            parallel_nodes = node.get_parallel_nodes()
            node_id, _ = process_parallel_nodes(parallel_nodes, nodes)
            if node_id is None:
                continue

            last_node = parallel_nodes[-1]

            for n in last_node.get_children():
                edge = (
                    f'\t"{node_id}" -> "{n.id}" [taillabel="{n._descriptor}"]'
                    if n._descriptor is not None
                    else f'\t"{node_id}" -> "{n.id}"'
                )

                if edge not in edges:
                    edges.append(edge)

            # reset the iterator to point to the last item in the queue
            iterator = task_state.bf_traversal(last_node)
        else:
            for child in node.get_children():
                edge = f'\t"{node.id}" -> '
                if child.is_parallel_execution_node:
                    parallel_nodes = child.get_parallel_nodes()
                    if not parallel_nodes:
                        continue
                    node_id, _ = process_parallel_nodes(parallel_nodes, nodes)
                    if not node_id:
                        continue

                    first_node = parallel_nodes[0]
                    edge += (
                        f'"{node_id}" [taillabel="{first_node._descriptor}"]'
                        if first_node._descriptor is not None
                        else f'"{node_id}"'
                    )
                elif child._descriptor is not None:
                    edge += f'"{child.id}" [taillabel="{child._descriptor}"]'
                else:
                    edge += f'"{child.id}"'

                if edge not in edges:
                    edges.append(edge)

    for n in nodes:
        f.write(n)

    for edge in edges:
        f.write(f"{edge}\n")

    f.write("}")
    return f.getvalue()
