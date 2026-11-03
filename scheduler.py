
from dataclasses import dataclass
from collections import deque


@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0


def fcfs(processes):
    ordered = sorted(processes, key=lambda p: p.arrival)
    current_time = 0
    results = []

    for p in ordered:
        start = max(current_time, p.arrival)
        finish = start + p.burst

        results.append({
            "pid": p.pid,
            "start": start,
            "finish": finish,
            "waiting": finish - p.arrival - p.burst,
            "turnaround": finish - p.arrival,
        })
        current_time = finish

    return results


def sjf(processes):
    remaining = processes.copy()
    current_time = 0
    results = []

    while remaining:
        available = [p for p in remaining if p.arrival <= current_time]

        if not available:
            current_time = min(p.arrival for p in remaining)
            continue

        p = min(available, key=lambda x: (x.burst, x.arrival, x.pid))
        start = current_time
        finish = start + p.burst

        results.append({
            "pid": p.pid,
            "start": start,
            "finish": finish,
            "waiting": finish - p.arrival - p.burst,
            "turnaround": finish - p.arrival,
        })

        current_time = finish
        remaining.remove(p)

    return results


def round_robin(processes, quantum=2):
    if quantum <= 0:
        raise ValueError("Quantum must be positive")

    ordered = sorted(processes, key=lambda p: p.arrival)
    remaining = {p.pid: p.burst for p in ordered}
    completion = {}
    timeline = []
    queue = deque()

    current_time = 0
    index = 0

    while len(completion) < len(ordered):
        if not queue:
            if index < len(ordered):
                current_time = max(current_time, ordered[index].arrival)
                while index < len(ordered) and ordered[index].arrival <= current_time:
                    queue.append(ordered[index])
                    index += 1

        p = queue.popleft()
        start = current_time
        duration = min(quantum, remaining[p.pid])
        current_time += duration
        remaining[p.pid] -= duration

        timeline.append((p.pid, start, current_time))

        while index < len(ordered) and ordered[index].arrival <= current_time:
            queue.append(ordered[index])
            index += 1

        if remaining[p.pid] > 0:
            queue.append(p)
        else:
            completion[p.pid] = current_time

    results = []

    for p in ordered:
        finish = completion[p.pid]
        results.append({
            "pid": p.pid,
            "start": next(s for pid, s, e in timeline if pid == p.pid),
            "finish": finish,
            "waiting": finish - p.arrival - p.burst,
            "turnaround": finish - p.arrival,
        })

    return results, timeline


def priority_scheduling(processes):
    remaining = processes.copy()
    current_time = 0
    results = []

    while remaining:
        available = [p for p in remaining if p.arrival <= current_time]

        if not available:
            current_time = min(p.arrival for p in remaining)
            continue

        p = min(available, key=lambda x: (x.priority, x.arrival, x.pid))
        start = current_time
        finish = start + p.burst

        results.append({
            "pid": p.pid,
            "start": start,
            "finish": finish,
            "waiting": finish - p.arrival - p.burst,
            "turnaround": finish - p.arrival,
        })

        current_time = finish
        remaining.remove(p)

    return results


def print_results(results, timeline=None):
    print("PID | Start | Finish | Waiting | Turnaround")
    print("-" * 47)

    for p in results:
        print(
            f"{p['pid']:3} | "
            f"{p['start']:5} | "
            f"{p['finish']:6} | "
            f"{p['waiting']:7} | "
            f"{p['turnaround']:10}"
        )

    avg_waiting = sum(p["waiting"] for p in results) / len(results)
    avg_turnaround = sum(p["turnaround"] for p in results) / len(results)

    print(f"\nAverage waiting: {avg_waiting:.2f}")
    print(f"Average turnaround: {avg_turnaround:.2f}")

    if timeline is None:
        timeline = [(p["pid"], p["start"], p["finish"]) for p in results]

    print("\nGantt chart:")
    print(" ".join(f"{pid}[{start}-{finish}]" for pid, start, finish in timeline))



def load_processes(filename):
    processes = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            pid, arrival, burst, priority = line.split()

            processes.append(
                Process(
                    pid,
                    int(arrival),
                    int(burst),
                    int(priority)
                )
            )

    return processes


if __name__ == "__main__":
    import sys

    filename = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "original_files/project1/jobs.txt"
    )

    processes = load_processes(filename)

    print(f"\nDataset: {filename}")
    print(f"Processes: {len(processes)}")

    print("\n========== FCFS ==========")
    print_results(fcfs(processes))

    print("\n========== SJF ==========")
    print_results(sjf(processes))

    print("\n========== ROUND ROBIN (q=2) ==========")
    rr_results, rr_timeline = round_robin(processes, quantum=2)
    print_results(rr_results, rr_timeline)

    print("\n========== PRIORITY ==========")
    print_results(priority_scheduling(processes))
