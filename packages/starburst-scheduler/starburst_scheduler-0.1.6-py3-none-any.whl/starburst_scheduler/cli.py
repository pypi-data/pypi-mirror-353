
import click
from .connector import StarburstConnector
from .scheduler import QueryScheduler

@click.group()
def cli():
    """Starburst Scheduler CLI for running and scheduling queries."""
    pass

@cli.command()
@click.option("--host", required=True, help="Starburst cluster host")
@click.option("--port", required=True, type=int, help="Starburst cluster port")
@click.option("--user", required=True, help="Starburst username")
@click.option("--password", prompt=True, hide_input=True, help="Starburst password")
@click.option("--catalog", default="sample", help="Catalog name")
@click.option("--schema", default="default", help="Schema name")
@click.option("--query", required=True, help="SQL query to execute")
def run_query(host, port, user, password, catalog, schema, query):
    connector = StarburstConnector(host, port, user, password, catalog, schema)
    if connector.connect():
        result = connector.execute_query(query)
        if result:
            click.echo(f"Query result: {result}")

@cli.command()
@click.option("--host", required=True, help="Starburst cluster host")
@click.option("--port", required=True, type=int, help="Starburst cluster port")
@click.option("--user", required=True, help="Starburst username")
@click.option("--password", prompt=True, hide_input=True, help="Starburst password")
@click.option("--catalog", default="sample", help="Catalog name")
@click.option("--schema", default="default", help="Schema name")
@click.option("--query", required=True, help="SQL query to schedule")
@click.option("--frequency", required=True, type=int, help="Frequency of execution")
@click.option("--time-unit", default="seconds", type=click.Choice(["seconds", "minutes", "hours", "days"]), help="Time unit for frequency")
def schedule_query(host, port, user, password, catalog, schema, query, frequency, time_unit):
    connector = StarburstConnector(host, port, user, password, catalog, schema)
    if connector.connect():
        scheduler = QueryScheduler(connector)
        scheduler.schedule_query(query, frequency, time_unit)
        scheduler.run()

if __name__ == "__main__":
    cli()
