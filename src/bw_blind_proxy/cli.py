import os
import json
import typer
from rich.console import Console
from rich.table import Table
from rich.json import JSON

from .logger import LOG_DIR
from .wal import WALManager
from .models import TransactionStatus

app = typer.Typer(help="BW-Blind-Proxy Management & Audit CLI")
console = Console()

@app.command("logs", help="View the latest transaction logs in a beautifully formatted table.")
def view_logs(n: int = typer.Option(5, help="Number of latest logs to view")):
    if not os.path.exists(LOG_DIR):
        console.print("[yellow]No logs directory found. No transactions have been processed yet.[/yellow]")
        return
        
    files = [f for f in os.listdir(LOG_DIR) if f.endswith(".json")]
    if not files:
        console.print("[yellow]No logs found.[/yellow]")
        return
        
    # Sort by descending order (newest first)
    files.sort(reverse=True)
    
    table = Table(title=f"Last {n} Transactions (Anti-Gravity Vault Audit)", show_lines=True)
    table.add_column("Timestamp", style="cyan", no_wrap=True)
    table.add_column("Transaction ID", style="magenta")
    table.add_column("Status", style="bold")
    table.add_column("Rationale", style="white")
    
    count = 0
    for filename in files:
        if count >= n:
            break
            
        filepath = os.path.join(LOG_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                log_data = json.load(f)
                
            tx_id = log_data.get("transaction_id", "")
            ts = log_data.get("timestamp", "")
            status = log_data.get("status", "")
            rat_str = log_data.get("rationale", "")
                
            stat_color = "green"
            if status == TransactionStatus.CRASH_RECOVERED_ON_BOOT:
                stat_color = "yellow"
            elif status in [TransactionStatus.ROLLBACK_TRIGGERED, TransactionStatus.ROLLBACK_SUCCESS, TransactionStatus.ROLLBACK_FAILED, TransactionStatus.ABORTED]:
                stat_color = "red"
                
            status_f = f"[{stat_color}]{status}[/{stat_color}]"
            
            table.add_row(ts, tx_id, status_f, rat_str)
            count += 1
        except Exception as e:
            console.print(f"[red]Error reading log {filename}: {str(e)}[/red]")
            
    console.print(table)

@app.command("log", help="View the full details of a specific transaction log. Default: shows the most recent log.")
def view_log(
    tx_id: str = typer.Argument(None, help="The Transaction ID (or a unique prefix of it)"),
    n: int = typer.Option(None, "--last", "-n", help="Fetch the N-th most recent log (1 = newest)")
):
    if not os.path.exists(LOG_DIR):
        console.print("[yellow]No logs directory found.[/yellow]")
        return
        
    all_files = [f for f in os.listdir(LOG_DIR) if f.endswith(".json")]
    if not all_files:
        console.print("[red]No logs found.[/red]")
        return
        
    all_files.sort(reverse=True) # newest first
        
    if n is not None:
        if n < 1 or n > len(all_files):
            console.print(f"[red]Invalid index '{n}'. Only {len(all_files)} logs available.[/red]")
            return
        target_file = all_files[n - 1]
    elif tx_id is not None:
        matches = [f for f in all_files if tx_id in f]
        if not matches:
            console.print(f"[red]No log found matching Transaction ID: {tx_id}[/red]")
            return
        if len(matches) > 1:
            console.print(f"[yellow]Multiple logs match '{tx_id}'. Please be more specific.[/yellow]")
            for m in matches:
                console.print(f"  - {m}")
            return
        target_file = matches[0]
    else:
        # Default to newest if neither id nor n is provided
        target_file = all_files[0]
        
    filepath = os.path.join(LOG_DIR, target_file)
    try:
        with open(filepath, 'r') as f:
            raw_content = f.read()
            
        console.print(f"[cyan bold]Log File: {target_file}[/cyan bold]")
        console.print(JSON(raw_content))
    except Exception as e:
        console.print(f"[red]Error reading log {target_file}: {str(e)}[/red]")

@app.command("wal", help="Inspect the Write-Ahead Log for any stranded transactions.")
def view_wal():
    if WALManager.has_pending_transaction():
        data = WALManager.read_wal()
        console.print(f"[red bold]CRITICAL: Uncommitted transaction found in WAL![/red bold]")
        console.print(f"Transaction ID: {data.get('transaction_id')}")
        console.print(f"Pending Rollback Commands stack size: {len(data.get('rollback_commands', []))}")
        console.print("\n[cyan]Full WAL state:[/cyan]")
        console.print(JSON(json.dumps(data)))
        console.print("\nThe proxy will automatically resolve this upon the next MCP execution.")
    else:
        console.print("[green]WAL is clean. No stranded transactions. Vault is perfectly synced.[/green]")

@app.command("purge", help="Delete old transaction logs, keeping only the N most recent ones.")
def purge_logs(keep: int = typer.Option(10, help="Number of latest logs to keep")):
    if not os.path.exists(LOG_DIR):
        console.print("[yellow]No logs directory found. Nothing to purge.[/yellow]")
        return
        
    files = [f for f in os.listdir(LOG_DIR) if f.endswith(".json")]
    if not files:
        console.print("[yellow]No logs found. Nothing to purge.[/yellow]")
        return
        
    if len(files) <= keep:
        console.print(f"[green]Only {len(files)} logs exist, which is <= the keep limit of {keep}. No action taken.[/green]")
        return
        
    # Sort by descending order (newest first)
    files.sort(reverse=True)
    
    # Files to delete are everything after the 'keep' limit
    files_to_delete = files[keep:]
    
    deleted_count = 0
    for filename in files_to_delete:
        filepath = os.path.join(LOG_DIR, filename)
        try:
            os.remove(filepath)
            deleted_count += 1
        except Exception as e:
            console.print(f"[red]Error deleting log {filename}: {str(e)}[/red]")
            
    console.print(f"[green]Successfully purged {deleted_count} old log files. Kept the most recent {keep}.[/green]")

if __name__ == "__main__":
    app()
