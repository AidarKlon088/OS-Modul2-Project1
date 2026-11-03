
import unittest

from scheduler import (
    Process,
    fcfs,
    sjf,
    round_robin,
    priority_scheduling,
    load_processes
)

from advanced import simulate_preemptive, mlfq


class SchedulerTests(unittest.TestCase):

    def setUp(self):
        self.processes = [
            Process("P1", 0, 5, 3),
            Process("P2", 1, 3, 1),
            Process("P3", 2, 2, 2)
        ]

    def test_fcfs(self):
        results = fcfs(self.processes)
        self.assertEqual(
            [p["pid"] for p in results],
            ["P1", "P2", "P3"]
        )
        self.assertEqual(
            [p["waiting"] for p in results],
            [0, 4, 6]
        )

    def test_sjf(self):
        results = sjf(self.processes)
        self.assertEqual(
            [p["pid"] for p in results],
            ["P1", "P3", "P2"]
        )
        self.assertEqual(
            [p["waiting"] for p in results],
            [0, 3, 6]
        )

    def test_round_robin(self):
        results, timeline = round_robin(self.processes, 2)
        self.assertEqual(
            [p[0] for p in timeline],
            ["P1", "P2", "P3", "P1", "P2", "P1"]
        )
        self.assertEqual(
            sum(p["waiting"] for p in results),
            12
        )

    def test_priority(self):
        results = priority_scheduling(self.processes)
        self.assertEqual(
            [p["pid"] for p in results],
            ["P1", "P2", "P3"]
        )

    def test_srtf(self):
        results, timeline = simulate_preemptive(
            self.processes, "SRTF"
        )
        self.assertEqual(len(results), 3)
        self.assertEqual(
            sorted(p["finish"] for p in results)[-1],
            10
        )

    def test_mlfq(self):
        results, timeline = mlfq(self.processes)
        self.assertEqual(len(results), 3)
        self.assertEqual(
            sum(p["turnaround"] - p["waiting"] for p in results),
            10
        )

    def test_input_file(self):
        processes = load_processes(
            "original_files/project1/jobs.txt"
        )
        self.assertEqual(len(processes), 6)
        self.assertEqual(processes[0].pid, "P1")


if __name__ == "__main__":
    unittest.main()
