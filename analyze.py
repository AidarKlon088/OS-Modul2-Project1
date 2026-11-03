
from scheduler import load_processes, fcfs, sjf, round_robin, priority_scheduling


datasets = [
    "jobs.txt",
    "mixed.txt",
    "set1.txt",
    "starve.txt"
]

for dataset in datasets:
    path = f"original_files/project1/{dataset}"
    processes = load_processes(path)

    algorithms = {
        "FCFS": fcfs(processes),
        "SJF": sjf(processes),
        "RR": round_robin(processes, 2)[0],
        "Priority": priority_scheduling(processes)
    }

    print(f"\n========== {dataset} ==========")

    for name, results in algorithms.items():
        waiting = [p["waiting"] for p in results]
        turnaround = [p["turnaround"] for p in results]

        print(
            f"{name:10} | "
            f"Avg wait: {sum(waiting)/len(waiting):7.2f} | "
            f"Max wait: {max(waiting):3} | "
            f"Avg turnaround: {sum(turnaround)/len(turnaround):7.2f}"
        )

    if dataset == "starve.txt":
        print("\nP1 waiting time:")

        for name, results in algorithms.items():
            p1 = next(p for p in results if p["pid"] == "P1")
            print(f"{name:10}: {p1['waiting']}")
