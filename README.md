# CPS 3250 Hybrid Scheduler

An Operating Systems course project that compares task-scheduling policies on peak, batch, and mixed workloads. The hybrid policy uses Earliest Deadline First for real-time tasks, Round Robin for short interactive tasks, and Shortest Job First for batch tasks.

The simulator compares the hybrid policy with Round Robin, Shortest Job First, Highest Response Ratio Next, and Earliest Deadline First. It records wait time and turnaround time for each task. Sample results are in [src/results](src/results). The project also includes a FastAPI service and Prometheus metrics.

## Run a simulation

Use Python 3.12 or later.

```sh
python -m pip install -e .
python -m hybrid_scheduler.experiments.runner --strategy hybrid --workload mixed.json --output mixed-hybrid.csv --dry
```
