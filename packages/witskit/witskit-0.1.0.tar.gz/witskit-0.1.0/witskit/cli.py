"""
Command-line interface for witskit.

A CLI tool for decoding, processing, and analyzing WITS drilling data.
"""

import typer
from typing import Any, Dict, List, Literal, Optional, Union
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import json
from datetime import datetime

from .models.symbols import WITSSymbol, WITSUnits
from .models.wits_frame import DecodedFrame
from .decoder.wits_decoder import (
    WITSDecoder,
    decode_frame,
    decode_file,
    split_multiple_frames,
)
from .models.symbols import WITS_SYMBOLS
from .models.unit_converter import UnitConverter, ConversionError
from .transport.tcp_reader import TCPReader
from .transport.requesting_tcp_reader import RequestingTCPReader
from .transport.serial_reader import SerialReader
from .transport.file_reader import FileReader
from witskit import __version__

# Optional SQL storage imports
try:
    from .storage.sql_writer import SQLWriter, DatabaseConfig

    SQL_AVAILABLE = True
except ImportError:
    SQL_AVAILABLE = False

app = typer.Typer(
    name="witskit",
    help="🛠️ Modern Python SDK for WITS drilling data processing",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"WitsKit Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    WitsKit - Python SDK for WITS data processing
    """
    pass


@app.command("decode")
def decode_command(
    data: str = typer.Argument(..., help="WITS frame data or path to file"),
    metric: bool = typer.Option(
        False, "--metric/--fps", help="Use metric units or FPS units (default)"
    ),
    strict: bool = typer.Option(
        False, "--strict", help="Enable strict mode (fail on unknown symbols)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file for JSON results"
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, or raw"
    ),
    convert_to_metric: bool = typer.Option(
        False,
        "--convert-to-metric",
        help="Convert all values to metric units after decoding",
    ),
    convert_to_fps: bool = typer.Option(
        False, "--convert-to-fps", help="Convert all values to FPS units after decoding"
    ),
):
    """
    Decode a WITS frame from string or file.

    Examples:
    \b
        # Decode a WITS frame directly
        witskit decode "&&\\n01083650.40\\n011323.38\\n!!"

        # Decode from file
        witskit decode data.wits --output results.json

        # Use metric units instead of FPS (default)
        witskit decode data.wits --metric

        # Decode with FPS units then convert all to metric
        witskit decode data.wits --fps --convert-to-metric
    """

    # Validate conversion options
    if convert_to_metric and convert_to_fps:
        rprint("[red]❌ Error: Cannot convert to both metric and FPS units")
        raise typer.Exit(1)

    # Check if data is a file path
    if Path(data).exists():
        with open(data, "r") as f:
            frame_data: str = f.read()
        source = str(data)
    else:
        # Treat as direct WITS data
        frame_data = data.replace("\\n", "\n")  # Allow escaped newlines
        source = "cli_input"

    try:
        # Check if file contains multiple frames
        frames: List[str] = split_multiple_frames(frame_data)

        if len(frames) > 1:
            # Multiple frames - use decode_file
            results = decode_file(
                frame_data, use_metric_units=metric, strict_mode=strict, source=source
            )
            # Combine all data points for display
            all_data_points = []
            all_errors = []
            for result in results:
                all_data_points.extend(result.data_points)
                all_errors.extend(result.errors)

            # Create a combined result object for display
            class CombinedResult:
                def __init__(
                    self, data_points: list, errors: list, source: str
                ) -> None:
                    self.data_points = data_points
                    self.errors = errors
                    self.source = source
                    self.timestamp: datetime = datetime.now()

                def to_dict(self) -> dict[str, Any]:
                    return {
                        "timestamp": self.timestamp.isoformat(),
                        "source": self.source,
                        "frames": len(results),
                        "data": {
                            dp.symbol_code: {
                                "name": dp.symbol_name,
                                "description": dp.symbol_description,
                                "value": dp.parsed_value,
                                "raw_value": dp.raw_value,
                                "unit": dp.unit,
                            }
                            for dp in self.data_points
                        },
                        "errors": self.errors,
                    }

            result = CombinedResult(all_data_points, all_errors, source)
        else:
            # Single frame - use existing logic
            result = decode_frame(
                frame_data, use_metric_units=metric, strict_mode=strict, source=source
            )

        # Apply unit conversions if requested
        if convert_to_metric or convert_to_fps:
            conversion_errors = []
            converted_count = 0

            for dp in result.data_points:
                try:
                    # Get the symbol definition to determine target unit
                    symbol: WITSSymbol | None = WITS_SYMBOLS.get(dp.symbol_code)
                    if symbol:
                        current_unit = (
                            getattr(WITSUnits, dp.unit, None)
                            if dp.unit != "UNITLESS"
                            else WITSUnits.UNITLESS
                        )
                        target_unit: WITSUnits = (
                            symbol.metric_units
                            if convert_to_metric
                            else symbol.fps_units
                        )

                        if current_unit and target_unit and current_unit != target_unit:
                            if UnitConverter.is_convertible(current_unit, target_unit):
                                # Ensure the parsed value is a float
                                if isinstance(dp.parsed_value, (int, float)):
                                    converted_value: float = (
                                        UnitConverter.convert_value(
                                            float(dp.parsed_value),
                                            current_unit,
                                            target_unit,
                                        )
                                    )
                                    dp.parsed_value = converted_value
                                    dp.unit = target_unit.value
                                    converted_count += 1
                except Exception as e:
                    conversion_errors.append(
                        f"Failed to convert {dp.symbol_code}: {str(e)}"
                    )

            if converted_count > 0:
                units_type: Literal["metric"] | Literal["FPS"] = (
                    "metric" if convert_to_metric else "FPS"
                )
                rprint(
                    f"✅ [green]Converted {converted_count} values to {units_type} units"
                )

            if conversion_errors:
                rprint(f"⚠️ [yellow]Conversion warnings:")
                for error in conversion_errors[:5]:  # Show first 5 errors
                    rprint(f"[yellow]  • {error}")
                if len(conversion_errors) > 5:
                    rprint(f"[yellow]  ... and {len(conversion_errors) - 5} more")

        # Output results
        if format == "json" or output:
            output_data = result.to_dict()
            if output:
                with open(output, "w") as f:
                    json.dump(output_data, f, indent=2)
                rprint(f"✅ Results saved to {output}")
            else:
                rprint(json.dumps(output_data, indent=2))

        elif format == "raw":
            for dp in result.data_points:
                rprint(f"{dp.symbol_code}: {dp.parsed_value} {dp.unit}")

        else:  # table format
            if result.data_points:
                table = Table(title="🛠️ Decoded WITS Data")
                table.add_column("Symbol", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Value", style="yellow")
                table.add_column("Unit", style="blue")
                table.add_column("Description", style="dim")

                for dp in result.data_points:
                    table.add_row(
                        dp.symbol_code,
                        dp.symbol_name,
                        str(dp.parsed_value),
                        dp.unit,
                        (
                            dp.symbol_description[:50] + "..."
                            if len(dp.symbol_description) > 50
                            else dp.symbol_description
                        ),
                    )

                console.print(table)

                # Show metadata
                rprint(f"\n[dim]Source: {result.source}")
                rprint(f"Timestamp: {result.timestamp}")
                rprint(f"Data points: {len(result.data_points)}")
                if result.errors:
                    rprint(f"[red]Errors: {len(result.errors)}")
            else:
                rprint("[yellow]⚠️ No data points decoded")

        # Show errors if any
        if result.errors:
            rprint(f"\n[red]❌ Errors encountered:")
            for error in result.errors:
                rprint(f"[red]  • {error}")

    except Exception as e:
        rprint(f"[red]❌ Error: {str(e)}")
        raise typer.Exit(1)


@app.command("convert")
def convert_command(
    value: float = typer.Argument(..., help="Value to convert"),
    from_unit: str = typer.Argument(..., help="Source unit (e.g., PSI, KPA, MHR, FHR)"),
    to_unit: str = typer.Argument(..., help="Target unit (e.g., PSI, KPA, MHR, FHR)"),
    precision: int = typer.Option(
        3, "--precision", "-p", help="Decimal places in result"
    ),
    show_formula: bool = typer.Option(
        False, "--formula", "-f", help="Show conversion formula and factor"
    ),
    list_units: bool = typer.Option(
        False, "--list-units", "-l", help="List all available units"
    ),
):
    """
    Convert values between drilling industry units.

    Supports all WITS drilling industry units including rates, pressures,
    flow rates, densities, temperatures, and more.

    Examples:
    \b
        # Convert drilling rate
        witskit convert 30 MHR FHR

        # Convert pressure with high precision
        witskit convert 2500 PSI KPA --precision 2

        # Convert flow rate and show formula
        witskit convert 800 GPM LPM --formula

        # Convert temperature
        witskit convert 150 DEGF DEGC

        # List all available units
        witskit convert 0 _ _ --list-units
    """

    if list_units:
        _show_available_units()
        return

    try:
        # Parse units
        try:
            from_wits_unit = getattr(WITSUnits, from_unit.upper())
        except AttributeError:
            rprint(f"[red]❌ Unknown source unit: {from_unit}")
            rprint("[dim]Use --list-units to see available units")
            raise typer.Exit(1)

        try:
            to_wits_unit = getattr(WITSUnits, to_unit.upper())
        except AttributeError:
            rprint(f"[red]❌ Unknown target unit: {to_unit}")
            rprint("[dim]Use --list-units to see available units")
            raise typer.Exit(1)

        # Check if conversion is supported
        if not UnitConverter.is_convertible(from_wits_unit, to_wits_unit):
            rprint(f"[red]❌ Conversion from {from_unit} to {to_unit} is not supported")
            rprint(
                "[dim]These units are not in the same category (pressure, rate, etc.)"
            )
            raise typer.Exit(1)

        # Perform conversion
        result: float = UnitConverter.convert_value(value, from_wits_unit, to_wits_unit)

        # Format result
        formatted_result: float = round(result, precision)

        # Display result
        table = Table(title="🔄 Unit Conversion Result")
        table.add_column("From", style="cyan")
        table.add_column("To", style="green")
        table.add_column("Result", style="yellow")

        table.add_row(
            f"{value} {from_unit}",
            f"{formatted_result} {to_unit}",
            f"{formatted_result:.{precision}f} {to_unit}",
        )

        console.print(table)

        # Show formula if requested
        if show_formula:
            factor: float | None = UnitConverter.get_conversion_factor(
                from_wits_unit, to_wits_unit
            )
            if factor:
                if factor == 1.0:
                    rprint(f"\n[dim]Formula: {from_unit} = {to_unit} (same unit)")
                else:
                    if (
                        from_wits_unit == WITSUnits.DEGC
                        and to_wits_unit == WITSUnits.DEGF
                    ):
                        rprint(f"\n[dim]Formula: °F = (°C × 9/5) + 32")
                    elif (
                        from_wits_unit == WITSUnits.DEGF
                        and to_wits_unit == WITSUnits.DEGC
                    ):
                        rprint(f"\n[dim]Formula: °C = (°F - 32) × 5/9")
                    else:
                        rprint(f"\n[dim]Formula: {to_unit} = {from_unit} × {factor}")
                        rprint(
                            f"[dim]Calculation: {value} × {factor} = {formatted_result}"
                        )

        # Show category info
        category: str = UnitConverter.get_unit_category(from_wits_unit)
        rprint(f"\n[dim]Category: {category}")

    except ConversionError as e:
        rprint(f"[red]❌ Conversion error: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]❌ Error: {str(e)}")
        raise typer.Exit(1)


def _show_available_units() -> None:
    """Display all available units organized by category."""
    rprint("🔧 [bold cyan]Available WITS Units\n")

    # Group units by category
    unit_categories: Dict[str, List[WITSUnits]] = {
        "Drilling Rates": [WITSUnits.MHR, WITSUnits.FHR],
        "Pressures": [WITSUnits.KPA, WITSUnits.PSI, WITSUnits.BAR],
        "Flow Rates": [WITSUnits.LPM, WITSUnits.GPM, WITSUnits.M3PM, WITSUnits.BPM],
        "Lengths": [
            WITSUnits.METERS,
            WITSUnits.FEET,
            WITSUnits.MILLIMETERS,
            WITSUnits.INCHES,
        ],
        "Densities": [WITSUnits.KGM3, WITSUnits.PPG],
        "Temperatures": [WITSUnits.DEGC, WITSUnits.DEGF],
        "Weights/Forces": [WITSUnits.KDN, WITSUnits.KLB, WITSUnits.KGM, WITSUnits.LBF],
        "Torques": [WITSUnits.KNM, WITSUnits.KFLB],
        "Volumes": [WITSUnits.M3, WITSUnits.BBL],
        "Speeds": [WITSUnits.MS, WITSUnits.FPM, WITSUnits.KPH, WITSUnits.MPH],
        "Angular": [WITSUnits.DGHM, WITSUnits.DGHF],
        "Electrical": [WITSUnits.OHMM, WITSUnits.MMHO],
        "Other": [WITSUnits.UNITLESS],
    }

    for category, units in unit_categories.items():
        table = Table(title=f"📊 {category}")
        table.add_column("Unit Code", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("System", style="yellow")

        for unit in units:
            if category == "Drilling Rates":
                if unit == WITSUnits.MHR:
                    desc, system = "Meters per Hour", "Metric"
                else:
                    desc, system = "Feet per Hour", "FPS"
            elif category == "Pressures":
                if unit == WITSUnits.KPA:
                    desc, system = "Kilopascals", "Metric"
                elif unit == WITSUnits.PSI:
                    desc, system = "Pounds per Square Inch", "FPS"
                else:
                    desc, system = "Bar", "Metric"
            elif category == "Temperatures":
                if unit == WITSUnits.DEGC:
                    desc, system = "Degrees Celsius", "Metric"
                else:
                    desc, system = "Degrees Fahrenheit", "FPS"
            else:
                desc = unit.value
                system = "Both" if unit == WITSUnits.UNITLESS else "Mixed"

            table.add_row(unit.name, desc, system)

        console.print(table)
        rprint()  # Add spacing between tables

    rprint("[dim]💡 Example: witskit convert 30 MHR FHR")
    rprint("[dim]💡 Example: witskit convert 2500 PSI KPA --precision 2")


@app.command("symbols")
def symbols_command(
    search: Optional[str] = typer.Option(
        None, "--search", "-s", help="Search symbols by name or description"
    ),
    record_type: Optional[int] = typer.Option(
        None, "--record", "-r", help="Filter by record type"
    ),
    list_records: bool = typer.Option(
        False, "--list-records", "-l", help="List all available record types"
    ),
) -> None:
    """
    List available WITS symbols with their definitions.

    This command provides access to the complete WITS specification with 724 symbols
    across 20+ record types including drilling, logging, and completion data.
    """
    from .models.symbols import (
        get_record_types,
        get_symbols_by_record_type,
        search_symbols,
        get_record_description,
    )

    if list_records:
        # Show all record types
        table = Table(title="📋 WITS Record Types")
        table.add_column("Record", style="cyan", width=8)
        table.add_column("Description", style="white", width=40)
        table.add_column("Symbols", style="green", width=8)
        table.add_column("Category", style="yellow", width=15)

        # Categorize records for better organization
        categories: Dict[str, list[int]] = {
            "Drilling": [1, 2, 3, 4],
            "Tripping": [5, 6],
            "Surveying": [7],
            "MWD/LWD": [8, 9],
            "Evaluation": [10, 12, 13, 14, 15, 16],
            "Operations": [11, 17, 18],
            "Configuration": [19, 20, 21],
            "Reporting": [22, 23],
            "Marine": [24, 25],
        }

        category_map = {}
        for cat, records in categories.items():
            for record in records:
                category_map[record] = cat

        for rt in sorted(get_record_types()):
            symbols_count: int = len(get_symbols_by_record_type(rt))
            category = category_map.get(rt, "Other")
            table.add_row(
                str(rt), get_record_description(rt), str(symbols_count), category
            )

        console.print(table)

        total_symbols: int = len(WITS_SYMBOLS)
        total_records: int = len(get_record_types())
        rprint(
            f"\n📈 [bold green]Total: {total_records} record types, {total_symbols} symbols"
        )
        rprint(f"[dim]Use --record <number> to see symbols for a specific record type")
        return

    # Filter symbols
    if search:
        # First search across all symbols
        symbols_to_show: Dict[str, WITSSymbol] = search_symbols(search)

        # If record_type is specified, filter further by record type
        if record_type:
            symbols_to_show = {
                code: symbol
                for code, symbol in symbols_to_show.items()
                if symbol.record_type == record_type
            }
            title: str = f"Record {record_type} Symbols matching '{search}'"
        else:
            title = f"All Symbols matching '{search}'"
    elif record_type:
        symbols_to_show = get_symbols_by_record_type(record_type)
        title = f"Record {record_type}: {get_record_description(record_type)}"
    else:
        symbols_to_show = WITS_SYMBOLS
        title = "All WITS Symbols"

    if not symbols_to_show:
        rprint("[yellow]⚠️ No symbols found matching criteria")
        if search:
            rprint("[dim]Try a different search term or use broader keywords")
        rprint("[dim]Use --list-records to see available record types")
        return

    # Create table
    table = Table(title=f"📊 {title} ({len(symbols_to_show)} found)")
    table.add_column("Code", style="cyan", width=6)
    table.add_column("Rec", style="dim cyan", width=4)
    table.add_column("Name", style="green", width=12)
    table.add_column("Type", style="blue", width=4)
    table.add_column("Metric", style="yellow", width=10)
    table.add_column("FPS", style="yellow", width=10)
    table.add_column("Description", style="dim", width=45)

    for code, symbol in sorted(symbols_to_show.items()):
        description: str = symbol.description
        if len(description) > 40:
            description = description[:37] + "..."

        table.add_row(
            code,
            str(symbol.record_type),
            symbol.name,
            symbol.data_type.value,
            symbol.metric_units.value,
            symbol.fps_units.value,
            description,
        )

    console.print(table)

    # Show helpful hints
    if len(symbols_to_show) > 50:
        rprint(
            f"\n[dim]💡 Large result set. Use --search to filter or --record to focus on specific record types"
        )

    if record_type:
        rprint(
            f"\n[dim]📖 Record {record_type} contains {len(symbols_to_show)} symbols for {get_record_description(record_type)}"
        )
    else:
        rprint(
            f"\n[dim]📖 Showing {len(symbols_to_show)} of {len(WITS_SYMBOLS)} total symbols across {len(get_record_types())} record types"
        )


@app.command("validate")
def validate_command(
    data: str = typer.Argument(..., help="WITS frame data or path to file")
):
    """
    Validate WITS frame format without decoding.

    Examples:
    \b
        # Validate a WITS frame
        witskit validate "&&\\n01083650.40\\n!!"

        # Validate from file
        witskit validate data.wits
    """

    # Check if data is a file path
    if Path(data).exists():
        with open(data, "r") as f:
            frame_data: str = f.read()
    else:
        frame_data = data.replace("\\n", "\n")

    try:
        from .decoder.wits_decoder import validate_wits_frame

        is_valid = validate_wits_frame(frame_data)
        if is_valid:
            rprint("✅ [green]Valid WITS frame format")
        else:
            rprint("❌ [red]Invalid WITS frame format")
            raise typer.Exit(1)

    except Exception as e:
        rprint(f"❌ [red]Validation error: {str(e)}")
        raise typer.Exit(1)


@app.command("stream")
def stream_command(
    source: str = typer.Argument(
        ...,
        help="Data source: tcp://host:port, serial:///dev/ttyUSB0, or file://path/to/file.wits",
    ),
    metric: bool = typer.Option(
        False, "--metric/--fps", help="Use metric units or FPS units (default)"
    ),
    strict: bool = typer.Option(
        False, "--strict", help="Enable strict mode (fail on unknown symbols)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file for JSON results"
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, or raw"
    ),
    baudrate: int = typer.Option(
        9600, "--baudrate", "-b", help="Baud rate for serial connections"
    ),
    max_frames: Optional[int] = typer.Option(
        None, "--max-frames", "-n", help="Maximum number of frames to process"
    ),
    request_mode: bool = typer.Option(
        False,
        "--request",
        help="Use request mode for TCP (send initial request to trigger streaming)",
    ),
    # SQL storage options
    sql_db: Optional[str] = typer.Option(
        None,
        "--sql-db",
        help="Store data in SQL database (sqlite:///path.db, postgresql://...)",
    ),
    sql_batch_size: int = typer.Option(
        100, "--sql-batch-size", help="Batch size for SQL inserts"
    ),
    sql_echo: bool = typer.Option(
        False, "--sql-echo", help="Echo SQL statements (for debugging)"
    ),
) -> None:
    """
    Stream and decode WITS data from various sources.

    Examples:
    \b
        # Stream from TCP server
        witskit stream tcp://192.168.1.100:12345

        # Stream from TCP server with request mode (for request/response servers)
        witskit stream tcp://localhost:8686 --request

        # Stream from serial port
        witskit stream serial:///dev/ttyUSB0 --baudrate 19200

        # Stream from file (for testing)
        witskit stream file://sample.wits

        # Store in SQLite database
        witskit stream tcp://localhost:8686 --request --sql-db sqlite:///drilling_data.db

        # Store in PostgreSQL with batch processing
        witskit stream tcp://localhost:12345 --sql-db postgresql://user:pass@localhost/wits --sql-batch-size 50

        # Limit to 10 frames and save as JSON
        witskit stream tcp://localhost:8686 --request --max-frames 10 --output results.json
    """

    # Initialize SQL writer if requested
    sql_writer = None
    if sql_db:
        if not SQL_AVAILABLE:
            rprint(
                "❌ [red]SQL storage not available. Install with: pip install witskit[sql][/red]"
            )
            raise typer.Exit(1)

        try:
            # Parse database URL and create config
            if sql_db.startswith("sqlite:///"):
                path = sql_db[10:]  # Remove sqlite:///
                config = DatabaseConfig.sqlite(path, echo=sql_echo)
            elif sql_db.startswith("postgresql://"):
                config = DatabaseConfig(
                    database_type="postgresql",
                    database_url=sql_db.replace(
                        "postgresql://", "postgresql+asyncpg://"
                    ),
                    echo_sql=sql_echo,
                )
            elif sql_db.startswith("mysql://"):
                config = DatabaseConfig(
                    database_type="mysql",
                    database_url=sql_db.replace("mysql://", "mysql+aiomysql://"),
                    echo_sql=sql_echo,
                )
            else:
                rprint(f"❌ [red]Unsupported database URL: {sql_db}[/red]")
                raise typer.Exit(1)

            sql_writer = SQLWriter(config)
            import asyncio

            asyncio.run(sql_writer.initialize())
            rprint(
                f"🗄️ [green]Connected to SQL database: {config.database_type}[/green]"
            )

        except Exception as e:
            rprint(f"❌ [red]Failed to connect to database: {e}[/red]")
            raise typer.Exit(1)

    # Parse the source URL
    reader: Union[TCPReader, RequestingTCPReader, SerialReader, FileReader, None] = None
    try:
        if source.startswith("tcp://"):
            # Parse tcp://host:port
            url_part: str = source[6:]  # Remove 'tcp://'
            if ":" not in url_part:
                raise ValueError("TCP source must include port: tcp://host:port")
            host, port_str = url_part.rsplit(":", 1)
            port = int(port_str)

            if request_mode:
                reader = RequestingTCPReader(host, port)
                rprint(
                    f"🌐 [cyan]Connecting to TCP {host}:{port} (request mode)...[/cyan]"
                )
            else:
                reader = TCPReader(host, port)
                rprint(f"🌐 [cyan]Connecting to TCP {host}:{port}...[/cyan]")

        elif source.startswith("serial://"):
            # Parse serial:///dev/ttyUSB0
            serial_port = source[9:]  # Remove 'serial://'
            reader = SerialReader(serial_port, baudrate)
            rprint(
                f"🔌 [cyan]Opening serial port {serial_port} at {baudrate} baud...[/cyan]"
            )
        elif source.startswith("file://"):
            # Parse file://path/to/file.wits
            file_path: str = source[7:]  # Remove 'file://'
            if not Path(file_path).exists():
                raise ValueError(f"File not found: {file_path}")
            reader = FileReader(file_path)
            rprint(f"📁 [cyan]Reading from file {file_path}...[/cyan]")

        else:
            raise ValueError("Source must start with tcp://, serial://, or file://")

        # Show startup information
        rprint(f"\n🚀 [bold green]Starting WITS Stream Processing[/bold green]")
        rprint(f"📡 Source: {source}")
        if request_mode:
            rprint("📤 [cyan]Request mode enabled - sending initial request[/cyan]")
        if sql_writer:
            rprint(f"💾 [cyan]Database storage enabled[/cyan]")
        if max_frames:
            rprint(f"🔢 [cyan]Processing up to {max_frames} frames[/cyan]")
        rprint("   [dim]Press Ctrl+C to stop streaming...[/dim]\n")

        # Stream and process frames
        frame_count = 0
        all_results = []
        sql_batch = [] if sql_writer else None

        try:
            if reader is None:
                raise ValueError("Failed to initialize data source reader.")
            for frame in reader.stream():
                if max_frames and frame_count >= max_frames:
                    break

                try:
                    result: DecodedFrame = decode_frame(
                        frame,
                        use_metric_units=metric,
                        strict_mode=strict,
                        source=source,
                    )

                    frame_count += 1
                    all_results.append(result)

                    # Add to SQL batch if SQL storage is enabled
                    if sql_writer and sql_batch is not None:
                        sql_batch.append(result)

                        # Process batch when it reaches the batch size
                        if len(sql_batch) >= sql_batch_size:
                            try:
                                import asyncio

                                asyncio.run(sql_writer.store_frames(sql_batch))
                                rprint(
                                    f"💾 [dim]Stored batch of {len(sql_batch)} frames to database[/dim]"
                                )
                                sql_batch.clear()
                            except Exception as e:
                                rprint(f"⚠️ [yellow]SQL storage error: {e}[/yellow]")

                    # Display based on format
                    if format == "json":
                        rprint(json.dumps(result.to_dict(), indent=2))
                    elif format == "raw":
                        rprint(f"\n🔄 Frame {frame_count}:")
                        for dp in result.data_points:
                            rprint(f"  {dp.symbol_code}: {dp.parsed_value} {dp.unit}")
                    else:  # table format
                        # Show frame header with statistics
                        success_rate = (
                            (frame_count / frame_count) * 100 if frame_count > 0 else 0
                        )
                        rprint(
                            f"\n📦 [bold cyan]Frame {frame_count}[/bold cyan] - [dim]{result.timestamp.strftime('%H:%M:%S')}[/dim] "
                            f"[green]({len(result.data_points)} points)[/green]"
                        )

                        if sql_writer:
                            rprint(f"   💾 [dim]Storing to database...[/dim]")

                        if result.data_points:
                            # Create a beautiful table like in demo
                            table = Table(
                                title=f"🛠️ WITS Data Frame {frame_count}",
                                title_style="bold blue",
                            )
                            table.add_column("Symbol", style="cyan", width=8)
                            table.add_column("Name", style="green", width=12)
                            table.add_column("Value", style="yellow bold", width=12)
                            table.add_column("Unit", style="blue", width=8)
                            table.add_column("Description", style="dim", width=20)

                            # Show only top 8 most important parameters for readability
                            important_symbols = [
                                "0105",
                                "0106",
                                "0108",
                                "0113",
                                "0120",
                                "0121",
                                "0114",
                                "0116",
                            ]

                            # First show important symbols
                            shown_count = 0
                            for symbol_code in important_symbols:
                                if shown_count >= 8:
                                    break
                                for dp in result.data_points:
                                    if dp.symbol_code == symbol_code:
                                        table.add_row(
                                            dp.symbol_code,
                                            dp.symbol_name,
                                            str(dp.parsed_value),
                                            dp.unit,
                                            (
                                                dp.symbol_description[:20] + "..."
                                                if len(dp.symbol_description) > 20
                                                else dp.symbol_description
                                            ),
                                        )
                                        shown_count += 1
                                        break

                            # Then show remaining symbols up to limit
                            for dp in result.data_points:
                                if shown_count >= 8:
                                    break
                                if dp.symbol_code not in important_symbols:
                                    table.add_row(
                                        dp.symbol_code,
                                        dp.symbol_name,
                                        str(dp.parsed_value),
                                        dp.unit,
                                        (
                                            dp.symbol_description[:20] + "..."
                                            if len(dp.symbol_description) > 20
                                            else dp.symbol_description
                                        ),
                                    )
                                    shown_count += 1

                            console.print(table)

                            # Show summary if there are more points
                            if len(result.data_points) > shown_count:
                                rprint(
                                    f"   [dim]... and {len(result.data_points) - shown_count} more data points[/dim]"
                                )

                        else:
                            rprint("   [yellow]⚠️  No data points decoded[/yellow]")

                        if result.errors:
                            rprint(
                                f"   [yellow]⚠️  {len(result.errors)} warnings: {', '.join(result.errors[:2])}[/yellow]"
                            )
                            if len(result.errors) > 2:
                                rprint(
                                    f"   [dim]... and {len(result.errors) - 2} more[/dim]"
                                )

                        # Show running statistics every 5 frames or if it's the first few
                        if frame_count <= 3 or frame_count % 5 == 0:
                            avg_points = (
                                sum(len(r.data_points) for r in all_results)
                                / len(all_results)
                                if all_results
                                else 0
                            )
                            rprint(
                                f"   [dim]📊 Stats: {frame_count} frames, avg {avg_points:.1f} points/frame[/dim]"
                            )

                except Exception as e:
                    rprint(f"❌ [red]Frame {frame_count + 1} decode error: {e}[/red]")
                    continue

        except KeyboardInterrupt:
            rprint(f"\n⏹️ [yellow]Stopped by user after {frame_count} frames[/yellow]")

        finally:
            # Store any remaining SQL batch
            if sql_writer and sql_batch and len(sql_batch) > 0:
                try:
                    import asyncio

                    asyncio.run(sql_writer.store_frames(sql_batch))
                    rprint(
                        f"💾 [green]Stored final batch of {len(sql_batch)} frames to database[/green]"
                    )
                except Exception as e:
                    rprint(f"⚠️ [yellow]Final SQL batch error: {e}[/yellow]")

            # Close SQL connection
            if sql_writer:
                try:
                    import asyncio

                    asyncio.run(sql_writer.close())
                except Exception as e:
                    rprint(f"⚠️ [yellow]SQL close error: {e}[/yellow]")

            if reader is not None:
                reader.close()

        # Save output if requested
        if output and all_results:
            output_data = {
                "source": source,
                "frames_processed": frame_count,
                "timestamp": datetime.now().isoformat(),
                "frames": [result.to_dict() for result in all_results],
            }
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2)
            rprint(f"\n💾 [green]Saved {frame_count} frames to {output}[/green]")

        # Show final statistics
        if frame_count > 0:
            total_points = sum(len(r.data_points) for r in all_results)
            avg_points = total_points / frame_count if frame_count > 0 else 0
            unique_symbols = set()
            for r in all_results:
                for dp in r.data_points:
                    unique_symbols.add(dp.symbol_code)

            rprint(f"\n📊 [bold green]Stream Processing Complete[/bold green]")
            rprint(f"   Frames processed: {frame_count}")
            rprint(f"   Total data points: {total_points}")
            rprint(f"   Average points/frame: {avg_points:.1f}")
            rprint(f"   Unique symbols: {len(unique_symbols)}")
            if sql_writer:
                rprint(f"   💾 [green]Data stored to database[/green]")
        else:
            rprint(f"\n❌ [yellow]No frames processed[/yellow]")

    except Exception as e:
        rprint(f"❌ [red]Error: {e}[/red]")
        if reader:
            reader.close()
        raise typer.Exit(1)


@app.command("sql-query")
def sql_query_command(
    database: str = typer.Argument(
        ..., help="Database URL (sqlite:///path.db, postgresql://...)"
    ),
    symbols: Optional[str] = typer.Option(
        None,
        "--symbols",
        "-s",
        help="Comma-separated symbol codes to query (e.g., 0108,0113)",
    ),
    start_time: Optional[str] = typer.Option(
        None, "--start", help="Start time (ISO format: 2024-01-01T10:00:00)"
    ),
    end_time: Optional[str] = typer.Option(
        None, "--end", help="End time (ISO format: 2024-01-01T12:00:00)"
    ),
    source: Optional[str] = typer.Option(
        None, "--source", help="Filter by data source"
    ),
    limit: Optional[int] = typer.Option(
        1000, "--limit", "-l", help="Maximum number of records to return"
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, csv"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    list_symbols: bool = typer.Option(
        False, "--list-symbols", help="List available symbols in database"
    ),
    time_range: bool = typer.Option(
        False, "--time-range", help="Show time range of data in database"
    ),
) -> None:
    """
    Query stored WITS data from SQL database.

    Examples:
    \b
        # List available symbols
        witskit sql-query sqlite:///drilling_data.db --list-symbols

        # Query specific symbols
        witskit sql-query sqlite:///drilling_data.db --symbols "0108,0113" --limit 100

        # Time-based query
        witskit sql-query sqlite:///drilling_data.db --start "2024-01-01T10:00:00" --end "2024-01-01T12:00:00"

        # Export to CSV
        witskit sql-query sqlite:///drilling_data.db --symbols "0108" --format csv --output depth_data.csv
    """
    if not SQL_AVAILABLE:
        rprint(
            "❌ [red]SQL functionality not available. Install with: pip install witskit[sql][/red]"
        )
        raise typer.Exit(1)

    try:
        # Parse database URL and create config
        if database.startswith("sqlite:///"):
            path = database[10:]
            config = DatabaseConfig.sqlite(path)
        elif database.startswith("postgresql://"):
            config = DatabaseConfig(
                database_type="postgresql",
                database_url=database.replace("postgresql://", "postgresql+asyncpg://"),
            )
        elif database.startswith("mysql://"):
            config = DatabaseConfig(
                database_type="mysql",
                database_url=database.replace("mysql://", "mysql+aiomysql://"),
            )
        else:
            rprint(f"❌ [red]Unsupported database URL: {database}[/red]")
            raise typer.Exit(1)

        sql_writer = SQLWriter(config)

        async def run_query():
            await sql_writer.initialize()

            try:
                if list_symbols:
                    symbols_list = await sql_writer.get_available_symbols(source)
                    if symbols_list:
                        rprint(
                            f"📊 [cyan]Available symbols ({len(symbols_list)}):[/cyan]"
                        )
                        for symbol_code in sorted(symbols_list):
                            # Get symbol info from WITS_SYMBOLS
                            symbol_info = WITS_SYMBOLS.get(symbol_code)
                            if symbol_info:
                                rprint(f"  {symbol_code}: {symbol_info.name}")
                            else:
                                rprint(f"  {symbol_code}: Unknown symbol")
                    else:
                        rprint("📊 [yellow]No symbols found in database[/yellow]")
                    return

                if time_range:
                    min_time, max_time = await sql_writer.get_time_range(source)
                    if min_time and max_time:
                        rprint(f"⏰ [cyan]Data time range:[/cyan]")
                        rprint(f"  Start: {min_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        rprint(f"  End:   {max_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        duration = max_time - min_time
                        rprint(f"  Duration: {duration}")
                    else:
                        rprint("⏰ [yellow]No data found in database[/yellow]")
                    return

                # Parse time filters
                start_dt = None
                end_dt = None
                if start_time:
                    try:
                        start_dt = datetime.fromisoformat(start_time)
                    except ValueError:
                        rprint(f"❌ [red]Invalid start time format: {start_time}[/red]")
                        return

                if end_time:
                    try:
                        end_dt = datetime.fromisoformat(end_time)
                    except ValueError:
                        rprint(f"❌ [red]Invalid end time format: {end_time}[/red]")
                        return

                # Parse symbol codes
                symbol_codes = []
                if symbols:
                    symbol_codes = [s.strip() for s in symbols.split(",")]

                if not symbol_codes:
                    rprint("❌ [red]Please specify symbol codes with --symbols[/red]")
                    return

                # Query data points
                data_points = []
                async for dp in sql_writer.query_data_points(
                    symbol_codes=symbol_codes,
                    start_time=start_dt,
                    end_time=end_dt,
                    source=source,
                    limit=limit,
                ):
                    data_points.append(dp)

                if not data_points:
                    rprint("📊 [yellow]No data found matching criteria[/yellow]")
                    return

                # Display results
                if format == "json":
                    results = [
                        {
                            "timestamp": dp.timestamp.isoformat(),
                            "symbol_code": dp.symbol_code,
                            "symbol_name": dp.symbol_name,
                            "value": dp.parsed_value,
                            "unit": dp.unit,
                            "source": dp.source,
                        }
                        for dp in data_points
                    ]

                    if output:
                        with open(output, "w") as f:
                            json.dump(results, f, indent=2)
                        rprint(
                            f"💾 [green]Saved {len(results)} records to {output}[/green]"
                        )
                    else:
                        rprint(json.dumps(results, indent=2))

                elif format == "csv":
                    import csv

                    if output:
                        with open(output, "w", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(
                                [
                                    "timestamp",
                                    "symbol_code",
                                    "symbol_name",
                                    "value",
                                    "unit",
                                    "source",
                                ]
                            )
                            for dp in data_points:
                                writer.writerow(
                                    [
                                        dp.timestamp.isoformat(),
                                        dp.symbol_code,
                                        dp.symbol_name,
                                        dp.parsed_value,
                                        dp.unit,
                                        dp.source,
                                    ]
                                )
                        rprint(
                            f"💾 [green]Saved {len(data_points)} records to {output}[/green]"
                        )
                    else:
                        rprint("timestamp,symbol_code,symbol_name,value,unit,source")
                        for dp in data_points:
                            rprint(
                                f"{dp.timestamp.isoformat()},{dp.symbol_code},{dp.symbol_name},{dp.parsed_value},{dp.unit},{dp.source}"
                            )

                else:  # table format
                    table = Table(
                        title=f"📊 WITS Data Query Results ({len(data_points)} records)"
                    )
                    table.add_column("Time", style="cyan")
                    table.add_column("Symbol", style="yellow")
                    table.add_column("Name", style="green")
                    table.add_column("Value", style="white")
                    table.add_column("Unit", style="blue")

                    for dp in data_points:
                        table.add_row(
                            dp.timestamp.strftime("%H:%M:%S"),
                            dp.symbol_code,
                            dp.symbol_name,
                            str(dp.parsed_value),
                            dp.unit,
                        )

                    console.print(table)

                    if output:
                        rprint(
                            f"💾 [yellow]Note: Use --format json or csv to save table data to file[/yellow]"
                        )

            finally:
                await sql_writer.close()

        import asyncio

        asyncio.run(run_query())

    except Exception as e:
        rprint(f"❌ [red]Query error: {e}[/red]")
        raise typer.Exit(1)


@app.command("demo")
def demo_command() -> None:
    """
    Run a demonstration with sample WITS data.
    """
    rprint("🛠️ [bold cyan]WITS Kit Demo")
    rprint("Decoding sample drilling data...\n")

    # Sample WITS frame with common drilling parameters
    sample_frame = """&&
01083650.40
011323.38
011412.5
012112.5
!!"""

    rprint("[dim]Sample WITS frame:")
    for line in sample_frame.split("\n"):
        if line.strip():
            rprint(f"[dim]  {line}")
    rprint()

    # Decode it
    result = decode_frame(sample_frame, source="demo")

    if result.data_points:
        table = Table(title="📊 Decoded Sample Data")
        table.add_column("Symbol", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Value", style="yellow")
        table.add_column("Unit", style="blue")
        table.add_column("Description", style="dim")

        for dp in result.data_points:
            table.add_row(
                dp.symbol_code,
                dp.symbol_name,
                str(dp.raw_value),
                dp.unit,
                dp.symbol_description,
            )

        console.print(table)

        rprint(f"\n✅ [green]Successfully decoded {len(result.data_points)} parameters")

        if result.errors:
            rprint(f"⚠️ [yellow]{len(result.errors)} warnings/errors:")
            for error in result.errors:
                rprint(f"[yellow]  • {error}")

        rprint("\n🎯 [bold]Try these commands:[/bold]")
        rprint("• [cyan]witskit decode 'sample.wits'[/cyan] - Decode from file")
        rprint("• [cyan]witskit stream file://sample.wits[/cyan] - Stream from file")
        rprint("• [cyan]witskit stream tcp://localhost:12345[/cyan] - Stream from TCP")
        rprint("• [cyan]witskit symbols --search depth[/cyan] - Search symbols")
        rprint("• [cyan]witskit convert 3650.40 M F[/cyan] - Convert meters to feet")
    else:
        rprint("❌ [red]No data could be decoded")


if __name__ == "__main__":
    app()
