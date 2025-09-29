class Node_Cell:
    def __init__(self, node_id, cell_id):
        self.node_id = node_id
        self.cell_id = cell_id

    def __repr__(self):
        return f"Node_Cell(node_id={self.node_id}, cell_id={self.cell_id})"
