
from collections import deque
from scheduler import load_processes, round_robin


def simulate_preemptive(processes, mode):
    remaining = {p.pid: p.burst for p in processes}
    first_start = {}
    completion = {}
    timeline = []
    time = 0

    while len(completion) < len(processes):
        ready = [
            p for p in processes
            if p.arrival <= time and remaining[p.pid] > 0
        ]

        if not ready:
            time += 1
            continue

        if mode == "SRTF":
            p = min(
                ready,
                key=lambda x: (remaining[x.pid], x.arrival, x.pid)
            )
        else:
            p = min(
                ready,
                key=lambda x: (x.priority, x.arrival, x.pid)
            )

        first_start.setdefault(p.pid, time)

        if timeline and timeline[-1][0] == p.pid:
            timeline[-1] = (p.pid, timeline[-1][1], time + 1)
        else:
            timeline.append((p.pid, time, time + 1))

        remaining[p.pid] -= 1
        time += 1

        if remaining[p.pid] == 0:
            completion[p.pid] = time

    return make_results(processes, first_start, completion), timeline


def make_results(processes, first_start, completion):
    results = []

    for p in processes:
        finish = completion[p.pid]
        results.append({
            "pid": p.pid,
            "start": first_start[p.pid],
            "finish": finish,
            "waiting": finish - p.arrival - p.burst,
            "turnaround": finish - p.arrival
        })

    return results


def mlfq(processes, quantums=(2, 4, 8), boost_period=20):
    ordered = sorted(processes, key=lambda p: (p.arrival, p.pid))
    queues = [deque(), deque(), deque()]
    remaining = {p.pid: p.burst for p in ordered}
    first_start = {}
    completion = {}
    timeline = []

    time = 0
    index = 0
    running = None
    level = 0
    used = 0

    while len(completion) < len(ordered):
        if time > 0 and time % boost_period == 0:
            pending = []

            if running is not None:
                pending.append(running)

            for queue in queues:
                pending.extend(queue)
                queue.clear()

            queues[0].extend(pending)
            running = None
            used = 0

        while index < len(ordered) and ordered[index].arrival <= time:
            queues[0].append(ordered[index].pid)
            index += 1

        if running is not None:
            if any(queues[k] for k in range(level)):
                queues[level].appendleft(running)
                running = None

        if running is None:
            for k in range(3):
                if queues[k]:
                    running = queues[k].popleft()
                    level = k
                    used = 0
                    break

        if running is None:
            time += 1
            continue

        first_start.setdefault(running, time)

        if timeline and timeline[-1][0] == running:
            timeline[-1] = (running, timeline[-1][1], time + 1)
        else:
            timeline.append((running, time, time + 1))

        remaining[running] -= 1
        used += 1
        time += 1

        if remaining[running] == 0:
            completion[running] = time
            running = None
            used = 0
        elif used >= quantums[level]:
            next_level = min(level + 1, 2)
            queues[next_level].append(running)
            running = None
            used = 0

    return make_results(ordered, first_start, completion), timeline


def show(name, results, timeline):
    waiting = [p["waiting"] for p in results]
    turnaround = [p["turnaround"] for p in results]

    print(
        f"{name:20} "
        f"Avg wait={sum(waiting)/len(waiting):7.2f} "
        f"Max wait={max(waiting):4} "
        f"Avg turnaround={sum(turnaround)/len(turnaround):7.2f} "
        f"Segments={len(timeline):4}"
    )


if __name__ == "__main__":
    jobs = load_processes("original_files/project1/jobs.txt")
    mixed = load_processes("original_files/project1/mixed.txt")
    starve = load_processes("original_files/project1/starve.txt")

    print("========== JOBS ==========")
    for mode in ["SRTF", "Priority"]:
        results, timeline = simulate_preemptive(jobs, mode)
        show(mode, results, timeline)

    print("\n========== RR QUANTUM 1-10 ==========")
    for quantum in range(1, 11):
        results, timeline = round_robin(mixed, quantum)
        show(f"RR q={quantum}", results, timeline)

    print("\n========== MIXED: MLFQ COMPARISON ==========")
    for mode in ["SRTF", "Priority"]:
        results, timeline = simulate_preemptive(mixed, mode)
        show(mode, results, timeline)

    results, timeline = round_robin(mixed, 2)
    show("RR q=2", results, timeline)

    results, timeline = mlfq(mixed)
    show("MLFQ", results, timeline)

    print("\n========== STARVATION ==========")
    for mode in ["SRTF", "Priority"]:
        results, timeline = simulate_preemptive(starve, mode)
        show(mode, results, timeline)
        p1 = next(p for p in results if p["pid"] == "P1")
        print(f"P1 waiting: {p1['waiting']}")

    results, timeline = mlfq(starve)
    show("MLFQ", results, timeline)
    p1 = next(p for p in results if p["pid"] == "P1")
    print(f"P1 waiting: {p1['waiting']}")
