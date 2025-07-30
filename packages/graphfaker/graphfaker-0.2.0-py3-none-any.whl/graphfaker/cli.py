# graphfaker/cli.py
"""
Command-line interface for GraphFaker.
"""
from venv import logger
import typer
from graphfaker.core import GraphFaker
from graphfaker.fetchers.osm import OSMGraphFetcher
from graphfaker.fetchers.flights import FlightGraphFetcher

app = typer.Typer()


@app.command()
def gen(
    source: str = typer.Option("faker", help="Generation source faker library)"),
    # for faker source
    total_nodes: int = typer.Option(100, help="Total nodes for random mode"),
    total_edges: int = typer.Option(1000, help="Total edges for random mode"),
    # for osm source
    place: str = typer.Option(
        None, help="OSM place name (e.g., 'Soho Square, London, UK')"
    ),
    address: str = typer.Option(
        None, help="OSM address (e.g., '1600 Amphitheatre Parkway, Mountain View, CA')"
    ),
    bbox: str = typer.Option(None, help="OSM bounding box as 'north,south,east,west'"),
    network_type: str = typer.Option(
        "drive", help="OSM network type: drive | walk | bike | all"
    ),
    simplify: str = typer.Option(True, help="Simplify OSM graph topology"),
    retain_all: bool = typer.Option(False, help="Retain all components in OSM graph"),
    dist: int = typer.Option(
        1000, help="Search radius (meters) when fetching around address"
    ),
    # for flight source
    country: str = typer.Option(
        "United States", help="Filter airports by country for flight data"
    ),
    year: int = typer.Option(2024, help="Year (YYYY) for single-month flight fetch"),
    month: int = typer.Option(1, help="Month (1-12) for single-month flight fetch"),
    date_range: tuple = typer.Option(None, help="Year and Month range for flight data"),
):
    """Generate a graph using GraphFaker."""
    gf = GraphFaker()
    if source == "faker":
        G = gf.generate_graph(total_nodes=total_nodes, total_edges=total_edges)

    elif source == "osm":
        # parse bbox string if provided
        bbox_tuple = None
        if bbox:
            north, south, east, west = map(float, bbox.split(","))
            bbox_tuple = (north, south, east, west)
        G = OSMGraphFetcher.fetch_network(
            place=place,
            address=address,
            bbox=bbox_tuple,
            network_type=network_type,
            simplify=simplify,
            retain_all=retain_all,
            dist=dist,
        )
    elif source == "flights":

        airlines_df = FlightGraphFetcher.fetch_airlines()

        airports_df = FlightGraphFetcher.fetch_airports(country=country)

        # 2) Fetch on-time performance data
        flights_df = FlightGraphFetcher.fetch_flights(
            year=year, month=month, date_range=date_range
        )
        logger.info(
            f"Fetched {len(airlines_df)} airlines, "
            f"{len(airports_df)} airports, "
            f"{len(flights_df)} flights."
        )

        # 3) Build the NetworkX graph
        G = FlightGraphFetcher.build_graph(airlines_df, airports_df, flights_df)

    else:
        typer.echo(f"Source '{source}' not supported.")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
