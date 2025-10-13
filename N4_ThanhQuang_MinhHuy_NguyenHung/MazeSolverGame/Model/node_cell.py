class Node_Cell:
    def __init__(self, x, y, status, visited, g_cost, h_cost):
        self.x = x
        self.y = y
        self.status = status
        self.visited = visited
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.footprint_type = None  # Loại footprint cho rendering

    def get_position(self):
        return (self.x, self.y)

    def get_status(self):
        return self.status

    def is_visited(self):
        return self.visited

    def get_g_cost(self):
        return self.g_cost

    def get_h_cost(self):
        return self.h_cost

    def get_f_cost(self):
        return self.f_cost

    def set_footprint_type(self, footprint_type):
        """Đặt loại footprint cho cell này"""
        self.footprint_type = footprint_type

    def get_footprint_type(self):
        """Lấy loại footprint của cell này"""
        return self.footprint_type
