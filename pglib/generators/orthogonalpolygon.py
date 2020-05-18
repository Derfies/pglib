import itertools as it

from base import Base
from pglib.graph import const


class OrthogonalPolygon(Base):

    def __init__(self, num_points):
        super(OrthogonalPolygon, self).__init__()

        self.num_points = num_points

    def _permute_face_angles(self):
        poss_angles = [list(const.Angle)] * self.num_points
        all_angle_perms = set(it.product(*poss_angles))
        return filter(lambda x: sum(x) == 360, all_angle_perms)

    def foo(self):

        foobar = {}
        for axis in (Direction.xs(), Direction.ys()):
            lengths = {d: sum(layout.get_direction_lengths(d)) for d in axis}
            min_dir = min(lengths, key=lengths.get)
            min_length, max_length = lengths[min_dir], lengths[Direction.opposite(min_dir)]
            num_unknowns = layout.get_direction_lengths(min_dir, None).count(None)
            max_perm_length = max_length - sum(layout.get_direction_lengths(min_dir, 0)) - (num_unknowns - 1)
            edge_perms = [
                range(1, max_perm_length + 1) if layout.lengths[idx] is None else [layout.lengths[idx]]
                for idx in layout.get_direction_indices(min_dir)
            ]
            all_length_perms = it.product(*edge_perms)
            length_perms = filter(lambda x: sum(x) == max_length, it.product(*edge_perms))
            foobar[min_dir] = length_perms

        print ' ' * (indent + 2), 'perms:', foobar

        for perm in [dict(zip(foobar, v)) for v in it.product(*foobar.values())]:
            poly = copy.deepcopy(layout)
            for dir_, lengths in perm.items():
                for i, idx in enumerate(poly.get_direction_indices(dir_)):
                    poly.lengths[idx] = lengths[i]

            layouts.append(poly)


        return layouts

    def run(self, region):
        angle_perms = self._permute_face_angles()






if __name__ == '__main__':
    perms = OrthogonalPolygon(5)._permute_face_angles()
    print len(perms)
    for perm in perms:
        print perm