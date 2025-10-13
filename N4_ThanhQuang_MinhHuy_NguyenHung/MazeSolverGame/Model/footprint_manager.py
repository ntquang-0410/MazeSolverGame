"""
Footprint Manager
Quản lý logic xác định ảnh footprint phù hợp cho từng ô trong path solving
"""

class FootprintManager:
    """
    Quản lý việc xác định ảnh footprint phù hợp dựa trên hướng di chuyển
    """

    def __init__(self):
        # Mapping các hướng di chuyển
        self.DIRECTIONS = {
            'UP': (0, -1),
            'DOWN': (0, 1),
            'LEFT': (-1, 0),
            'RIGHT': (1, 0)
        }

        # Mapping ảnh footprint theo hướng di chuyển
        self.FOOTPRINT_MAPPING = {
            # Di chuyển thẳng
            'bottom_to_top': 'bottom_to_top.png',      # Di chuyển từ dưới lên trên
            'top_to_bottom': 'top_to_bottom.png',      # Di chuyển từ trên xuống dưới
            'left_to_right': 'left_to_right.png',      # Di chuyển từ trái sang phải
            'right_to_left': 'right_to_left.png',      # Di chuyển từ phải sang trái

            # Giao lộ và rẽ
            'cross_footprints': 'cross_footprints.png',    # Ngã tư (4 hướng giao nhau)
            'fork_footprints': 'folk_in_the_footprints.png',  # Ngã ba (3 hướng giao nhau)
            'turn_back': 'turn_back.png'               # Quay đầu/rẽ gấp
        }

    def determine_footprint_type(self, path, current_index):
        """
        Xác định loại footprint phù hợp cho một vị trí trong path

        Args:
            path: List các vị trí trong path solving [(x, y), ...]
            current_index: Index hiện tại trong path

        Returns:
            str: Tên key của footprint image phù hợp
        """
        if not path or current_index < 0 or current_index >= len(path):
            return 'cross_footprints'  # Default fallback

        current_pos = path[current_index]

        # Lấy vị trí trước và sau (nếu có)
        prev_pos = path[current_index - 1] if current_index > 0 else None
        next_pos = path[current_index + 1] if current_index < len(path) - 1 else None

        # Nếu là điểm đầu hoặc cuối
        if prev_pos is None and next_pos is not None:
            return self._get_direction_footprint(current_pos, next_pos)
        elif next_pos is None and prev_pos is not None:
            return self._get_direction_footprint(prev_pos, current_pos)
        elif prev_pos is None and next_pos is None:
            return 'cross_footprints'  # Single point

        # Xác định hướng đi vào và ra
        incoming_direction = self._get_direction(prev_pos, current_pos)
        outgoing_direction = self._get_direction(current_pos, next_pos)

        # Kiểm tra các trường hợp đặc biệt
        return self._analyze_path_pattern(incoming_direction, outgoing_direction)

    def _get_direction(self, from_pos, to_pos):
        """Xác định hướng di chuyển giữa 2 điểm"""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]

        if dx > 0:
            return 'RIGHT'
        elif dx < 0:
            return 'LEFT'
        elif dy > 0:
            return 'DOWN'
        elif dy < 0:
            return 'UP'
        else:
            return 'SAME'

    def _get_direction_footprint(self, from_pos, to_pos):
        """Lấy footprint cho di chuyển thẳng giữa 2 điểm"""
        direction = self._get_direction(from_pos, to_pos)

        direction_mapping = {
            'UP': 'bottom_to_top',      # Di chuyển lên → dấu chân từ dưới lên trên
            'DOWN': 'top_to_bottom',    # Di chuyển xuống → dấu chân từ trên xuống dưới
            'LEFT': 'right_to_left',    # Di chuyển trái → dấu chân từ phải sang trái
            'RIGHT': 'left_to_right'    # Di chuyển phải → dấu chân từ trái sang phải
        }

        return direction_mapping.get(direction, 'cross_footprints')

    def _analyze_path_pattern(self, incoming, outgoing):
        """
        Phân tích pattern của path để xác định footprint

        Args:
            incoming: Hướng đi vào
            outgoing: Hướng đi ra

        Returns:
            str: Footprint type phù hợp
        """
        # Nếu đi thẳng (cùng hướng)
        if incoming == outgoing:
            direction_mapping = {
                'UP': 'bottom_to_top',      # Đi thẳng lên → dấu chân từ dưới lên trên
                'DOWN': 'top_to_bottom',    # Đi thẳng xuống → dấu chân từ trên xuống dưới
                'LEFT': 'right_to_left',    # Đi thẳng trái → dấu chân từ phải sang trái
                'RIGHT': 'left_to_right'    # Đi thẳng phải → dấu chân từ trái sang phải
            }
            return direction_mapping.get(incoming, 'cross_footprints')

        # Nếu quay đầu (hướng ngược lại)
        opposite_pairs = [
            ('UP', 'DOWN'), ('DOWN', 'UP'),
            ('LEFT', 'RIGHT'), ('RIGHT', 'LEFT')
        ]

        if (incoming, outgoing) in opposite_pairs:
            return 'turn_back'

        # Nếu rẽ góc (2 hướng vuông góc) - sử dụng fork_footprints
        perpendicular_pairs = [
            ('UP', 'LEFT'), ('UP', 'RIGHT'),
            ('DOWN', 'LEFT'), ('DOWN', 'RIGHT'),
            ('LEFT', 'UP'), ('LEFT', 'DOWN'),
            ('RIGHT', 'UP'), ('RIGHT', 'DOWN')
        ]

        if (incoming, outgoing) in perpendicular_pairs:
            return 'fork_footprints'

        # Default fallback
        return 'cross_footprints'

    def analyze_full_path(self, path):
        """
        Phân tích toàn bộ path và trả về mapping footprint cho từng vị trí

        Args:
            path: List các vị trí trong path solving

        Returns:
            dict: {(x, y): footprint_type}
        """
        footprint_map = {}

        for i in range(len(path)):
            pos = path[i]
            footprint_type = self.determine_footprint_type(path, i)
            footprint_map[pos] = footprint_type

        return footprint_map

    def get_footprint_for_algorithm_step(self, path, visited_positions, current_algorithm=""):
        """
        Xác định footprint cho từng bước của thuật toán giải mê cung

        Args:
            path: Final solution path
            visited_positions: Các vị trí đã được thuật toán thăm
            current_algorithm: Tên thuật toán đang sử dụng

        Returns:
            dict: {(x, y): footprint_type}
        """
        result = {}

        # Phân tích final path với footprint chính xác
        if path:
            path_footprints = self.analyze_full_path(path)
            result.update(path_footprints)

        # Các vị trí đã thăm nhưng không thuộc final path - sử dụng cross_footprints
        for pos in visited_positions:
            if pos not in result:
                # Sử dụng cross_footprints cho các vị trí đã thăm nhưng không thuộc solution
                result[pos] = 'cross_footprints'

        return result

    def get_visited_footprint(self, algorithm_type=""):
        """
        Xác định footprint cho các ô đã được thuật toán thăm nhưng không thuộc solution

        Args:
            algorithm_type: Loại thuật toán để có thể customize footprint khác nhau

        Returns:
            str: Footprint type cho visited cells
        """
        # Có thể customize theo thuật toán khác nhau
        if algorithm_type in ["BFS", "Bidirectional"]:
            return 'cross_footprints'  # Ngã tư cho BFS vì nó explore theo patterns rộng
        elif algorithm_type in ["DFS"]:
            return 'fork_footprints'   # Ngã ba cho DFS vì nó explore theo depth
        elif algorithm_type in ["A*", "UCS"]:
            return 'cross_footprints'  # Ngã tư cho các thuật toán heuristic
        else:
            return 'cross_footprints'  # Default
