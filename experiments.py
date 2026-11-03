
from scheduler import load_processes, round_robin, priority_scheduling


def priority_aging(processes, interval=5):
    remaining = processes.copy()
    current_time = 0
    results = []

    while remaining:
        available = [p for p in remaining if p.arrival <= current_time]

        if not available:
            current_time = min(p.arrival for p in remaining)
            continue

        p = min(
            available,
            key=lambda x: (
                max(0, x.priority - (current_time - x.arrival) // interval),
                x.arrival,
                x.pid
            )
        )

        start = current_time
        finish = start + p.burst

        results.append({
            "pid": p.pid,
            "start": start,
            "finish": finish,
            "waiting": finish - p.arrival - p.burst,
            "turnaround": finish - p.arrival
        })

        current_time = finish
        remaining.remove(p)

    return results


def statistics(results):
    waiting = [p["waiting"] for p in results]
    turnaround = [p["turnaround"] for p in results]

    return (
        sum(waiting) / len(waiting),
        max(waiting),
        sum(turnaround) / len(turnaround)
    )


def show(name, results):
    avg, maximum, turnaround = statistics(results)

    print(
        f"{name:18} "
        f"Avg wait={avg:7.2f} "
        f"Max wait={maximum:4} "
        f"Avg turnaround={turnaround:7.2f}"
    )


print("========== ROUND ROBIN QUANTUM ==========")

for filename in ["jobs.txt", "mixed.txt", "set1.txt"]:
    processes = load_processes(f"original_files/project1/{filename}")

    print(f"\nDataset: {filename}")

    for quantum in [1, 2, 4, 8, 16]:
        results, timeline = round_robin(processes, quantum)
        show(f"RR q={quantum}", results)
        print(f"Context switches: {len(timeline) - 1}")


print("\n========== PRIORITY AGING ==========")

processes = load_processes("original_files/project1/starve.txt")

normal = priority_scheduling(processes)
show("Priority", normal)

for interval in [3, 5, 10]:
    aged = priority_aging(processes, interval)
    show(f"Aging interval={interval}", aged)

    p1 = next(p for p in aged if p["pid"] == "P1")
    print(f"P1 waiting: {p1['waiting']}")
