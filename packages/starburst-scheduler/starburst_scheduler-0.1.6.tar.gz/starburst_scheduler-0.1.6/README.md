
# Starburst Scheduler

A Python pip package to run and schedule SQL queries on **Starburst Galaxy** or **Starburst Enterprise** clusters.

It provides a **simple command-line interface (CLI)** to run queries once or on a schedule, and is designed for:
- Automating reports
- Monitoring Starburst cluster health
- Sending query results to collaboration tools (coming soon)

The package is lightweight, easy to use, and works well inside CI/CD pipelines, on servers, or in developer environments.

## Key Features

 Run SQL queries directly from the CLI  
 Schedule queries at regular intervals (seconds, minutes, hours, days)  
 Compatible with Starburst Galaxy and Starburst Enterprise  
 Easy to install no complex setup required  
 Designed to integrate with Slack, Mattermost, and other tools (feature coming soon!)  
 Works with Python 3.9+  
 Supports secure password input  
 Designed for extensibility (you can add custom output actions easily)

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

## Planned Enhancements

 Slack & Mattermost integration:  
-> When a query runs, results can be automatically posted to your team chat.  
-> Example: Monitor active queries, cluster status, send alerts.

 CSV/JSON output:  
-> Option to save query results to CSV / JSON for use in data pipelines.

 Advanced scheduling:  
-> Support cron expressions, weekly/monthly jobs.

 Email notifications:  
-> Option to send query results by email.

 Error alerting:  
-> Notify on failed query runs.

## License

MIT License

## GitHub Repository

[https://github.com/karranikhilreddy99/starburst_scheduler](https://github.com/karranikhilreddy99/starburst_scheduler)

## Summary

Starburst Scheduler makes it simple to:
- Run queries manually  
- Automate reporting  
- Monitor Starburst cluster health  
- Send alerts (Slack, Mattermost coming soon!)
