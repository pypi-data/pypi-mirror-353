"""Console script for pyuavlink."""
import os
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import pyuavlink

app = typer.Typer()
console = Console()

@app.command()
def run(
    ns3_path: str = typer.Argument(..., help="Path to NS-3 installation"),
    target_name: str = typer.Argument(..., help="Name of the simulation target"),
    show_output: bool = typer.Option(False, help="Show simulation output"),
    vector_mode: bool = typer.Option(False, help="Enable vector mode"),
    vector_size: Optional[int] = typer.Option(None, help="Vector size when vector mode is enabled"),
    shared_memory_size: int = typer.Option(4096, help="Size of shared memory segment")
):
    """Run a UAV simulation."""
    try:
        # Validate NS-3 path
        if not os.path.exists(ns3_path):
            console.print(f"[red]Error: NS-3 path '{ns3_path}' does not exist.[/red]")
            raise typer.Exit(1)

        # Create simulation instance
        simulation = pyuavlink.UAVLinkSimulation(
            simulation_target_name=target_name,
            ns3_path=ns3_path,
            uavlink_module=None,  # This needs to be properly initialized
            use_vector=vector_mode,
            vector_size=vector_size,
            shared_memory_size=shared_memory_size
        )

        # Start simulation
        simulation.start_simulation(show_output=show_output)
        
        # Show simulation info
        table = Table(title="Simulation Information")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Target", target_name)
        table.add_row("NS-3 Path", ns3_path)
        table.add_row("Vector Mode", str(vector_mode))
        if vector_mode:
            table.add_row("Vector Size", str(vector_size))
        table.add_row("Shared Memory Size", str(shared_memory_size))
        
        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def version():
    """Show version information."""
    from pyuavlink import __version__
    console.print(f"pyUAVLink version: {__version__}")

if __name__ == "__main__":
    app()
