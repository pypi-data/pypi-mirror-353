
# Starburst Scheduler

A Python pip package to run and schedule SQL queries on Starburst Galaxy or Enterprise clusters.

## Installation

```bash
pip install starburst_scheduler
```

## Usage

### Run a Single Query

```bash
starburst-scheduler run-query --host <host> --port <port> --user <user> --password <password> --catalog sample --schema burstbank --query "SELECT * FROM system.runtime.nodes"
```

### Schedule a Query

```bash
starburst-scheduler schedule-query --host <host> --port <port> --user <user> --password <password> --catalog sample --schema burstbank --query "SELECT * FROM system.runtime.nodes" --frequency 60 --time-unit seconds
```

## License

MIT License
