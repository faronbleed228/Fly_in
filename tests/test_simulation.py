import contextlib
import io
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fly_in import Connection, Parsing, Pathfinder, Simulation  # noqa: E402


class SimulationTests(unittest.TestCase):
    def test_all_maps(self):
        if len(sys.argv) > 1 and sys.argv[1] == "--map":
            return
        for path in sorted((ROOT / "maps").rglob("*.txt")):
            with self.subTest(map=str(path.relative_to(ROOT))):
                subprocess.run(
                    [sys.executable, __file__, "--map", str(path)],
                    cwd=ROOT, check=True, timeout=30, capture_output=True)

    def test_cli_error(self):
        result = subprocess.run(
            [sys.executable, "main.py", "/nonexistent-map.txt", "--headless"],
            cwd=ROOT, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 1)

    def test_headless_does_not_import_pygame(self):
        result = subprocess.run(
            [sys.executable, "-c",
             "import runpy,sys; sys.modules['pygame']=None; "
             "sys.argv=['main.py','maps/easy/01_linear_path.txt','--headless']; "
             "runpy.run_path('main.py',run_name='__main__')"],
            cwd=ROOT, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


def check_map(path):
    parser = Parsing(str(path))
    parser.dispatcher()
    graph = parser._graph
    drones = graph._drones_lst.copy()
    Pathfinder(graph, list(graph._zone_dict.values()),
               graph._connections_links, len(drones)).main_circle()
    sim = Simulation(graph)
    with contextlib.redirect_stdout(io.StringIO()):
        sim.run()
    assert not graph._drones_lst
    for before, after in zip(sim.gamestate_list, sim.gamestate_list[1:]):
        for drone in drones:
            old, new = before.state_dict[drone], after.state_dict[drone]
            if old is new:
                continue
            if isinstance(old, Connection):
                assert new in (old.zone_a, old.zone_b)
            elif isinstance(new, Connection):
                assert old in (new.zone_a, new.zone_b)
            else:
                assert new in old.get_neighbours()
                assert new.get_movement_cost() != 2
    for state in sim.gamestate_list:
        assert set(state.state_dict) == set(drones)
        for pos in set(state.state_dict.values()):
            count = list(state.state_dict.values()).count(pos)
            if isinstance(pos, Connection):
                assert count <= pos._max_link_capacity
            elif pos._hub_type not in ("start_hub", "end_hub"):
                assert count <= pos._max_capacity
                assert not pos._zone_blocked
    assert all(pos._hub_type == "end_hub"
               for pos in sim.gamestate_list[-1].state_dict.values())
    sim.validate_state()
    # Deliberate corruption must be rejected by the runtime invariant check.
    graph._connections_links[0]._cur_link_capacity += 1
    try:
        sim.validate_state()
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid capacity counter was accepted")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--map":
        sys.path.insert(0, str(ROOT))
        check_map(sys.argv[2])
    else:
        unittest.main()
