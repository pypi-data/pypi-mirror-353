#!/usr/bin/env python3
"""Claude Session Repair Tool - Fix broken tool_use/tool_result pairs in Claude conversations."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Any, Dict
from dataclasses import dataclass, field

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

app = typer.Typer(help="Repair broken Claude conversation sessions")
console = Console()


@dataclass
class Message:
    """Represents a message in the conversation."""
    uuid: str
    type: str  # "user", "assistant"
    timestamp: str
    content: Any  # Can be dict or other
    raw_data: Dict[str, Any]  # Store original JSON
    parent_uuid: Optional[str] = None
    tool_use_ids: List[str] = field(default_factory=list)
    tool_result_ids: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of session validation."""
    is_valid: bool
    error_at_index: Optional[int] = None
    error_message: Optional[str] = None
    orphaned_tool_uses: List[Tuple[int, str]] = field(default_factory=list)


def find_broken_sessions_with_rg() -> List[Tuple[Path, datetime, str]]:
    """Use rg to rapidly find all broken sessions across all Claude projects.
    
    Returns list of (session_path, modification_time, error_type) tuples.
    """
    claude_dir = Path.home() / ".claude" / "projects"
    if not claude_dir.exists():
        return []
    
    broken_sessions = set()  # Use set to avoid duplicates
    
    # Search patterns for broken sessions
    patterns = [
        ('"isApiErrorMessage":true', 'API Error'),
        ('"Request was aborted"', 'Request Aborted'),
        ('[Request interrupted', 'Request Interrupted')
    ]
    
    for pattern, error_type in patterns:
        try:
            # Use rg to find files containing the pattern
            result = subprocess.run(
                ['rg', '-l', '--json', pattern, str(claude_dir)],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Parse rg JSON output
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get('type') == 'match':
                                path = Path(data['data']['path']['text'])
                                if path.suffix == '.jsonl' and not path.name.endswith('.backup.jsonl'):
                                    mod_time = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                                    broken_sessions.add((path, mod_time, error_type))
                        except (json.JSONDecodeError, KeyError):
                            continue
        except (subprocess.CalledProcessError, FileNotFoundError):
            # rg not installed, fallback to manual search
            console.print("[yellow]Warning: ripgrep (rg) not found. Using slower fallback search.[/yellow]")
            return find_broken_sessions_fallback()
    
    # Convert set to sorted list (most recent first)
    return sorted(list(broken_sessions), key=lambda x: x[1], reverse=True)


def find_broken_sessions_fallback() -> List[Tuple[Path, datetime, str]]:
    """Fallback method to find broken sessions without rg."""
    claude_dir = Path.home() / ".claude" / "projects"
    broken_sessions = []
    
    for project_dir in claude_dir.iterdir():
        if project_dir.is_dir():
            for jsonl_file in project_dir.glob("*.jsonl"):
                if not jsonl_file.name.endswith('.backup.jsonl'):
                    # Check file content for error patterns
                    try:
                        with open(jsonl_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            error_type = None
                            if '"isApiErrorMessage":true' in content:
                                error_type = 'API Error'
                            elif '"Request was aborted"' in content:
                                error_type = 'Request Aborted'
                            elif '[Request interrupted' in content:
                                error_type = 'Request Interrupted'
                            
                            if error_type:
                                mod_time = datetime.fromtimestamp(jsonl_file.stat().st_mtime, tz=timezone.utc)
                                broken_sessions.append((jsonl_file, mod_time, error_type))
                    except Exception:
                        continue
    
    return sorted(broken_sessions, key=lambda x: x[1], reverse=True)


def find_claude_projects() -> List[Tuple[Path, datetime]]:
    """Find all Claude projects in ~/.claude/projects/."""
    claude_dir = Path.home() / ".claude" / "projects"
    
    if not claude_dir.exists():
        return []
    
    projects = []
    for project_dir in claude_dir.iterdir():
        if project_dir.is_dir():
            latest_mod = get_latest_modification(project_dir)
            if latest_mod:
                projects.append((project_dir, latest_mod))
    
    return sorted(projects, key=lambda x: x[1], reverse=True)


def get_latest_modification(directory: Path) -> Optional[datetime]:
    """Get most recent modification time from any file in directory."""
    latest = None
    
    try:
        for file in directory.rglob("*.jsonl"):
            if file.is_file():
                mod_time = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
                if latest is None or mod_time > latest:
                    latest = mod_time
    except Exception:
        pass
    
    return latest


def display_project_selection(projects: List[Tuple[Path, datetime]]) -> Path:
    """Display projects and let user select."""
    table = Table(title="Select a Claude Project")
    table.add_column("Index", style="cyan", width=6)
    table.add_column("Project Name", style="green", width=40)
    table.add_column("Last Modified", style="yellow")
    
    # Show top 3
    for idx, (path, mod_time) in enumerate(projects[:3]):
        project_name = path.name.replace("-", " ").title()
        formatted_time = mod_time.strftime("%Y-%m-%d %H:%M:%S")
        table.add_row(str(idx + 1), project_name, formatted_time)
    
    console.print(table)
    
    while True:
        choice = Prompt.ask("Select project", choices=["1", "2", "3"], default="1")
        idx = int(choice) - 1
        if 0 <= idx < min(3, len(projects)):
            return projects[idx][0]


def find_sessions(project_path: Path) -> List[Tuple[Path, datetime, str]]:
    """Find all .jsonl session files in project."""
    sessions = []
    
    for jsonl_file in project_path.glob("*.jsonl"):
        if not jsonl_file.name.endswith('.backup.jsonl'):
            mod_time = datetime.fromtimestamp(jsonl_file.stat().st_mtime, tz=timezone.utc)
            session_id = jsonl_file.stem
            sessions.append((jsonl_file, mod_time, session_id))
    
    return sorted(sessions, key=lambda x: x[1], reverse=True)


def display_session_selection(sessions: List[Tuple[Path, datetime, str]]) -> Path:
    """Display sessions and let user select."""
    table = Table(title="Select a Session to Repair")
    table.add_column("Index", style="cyan", width=6)
    table.add_column("Session ID", style="green", width=30)
    table.add_column("Last Modified", style="yellow")
    table.add_column("Size", style="blue")
    
    # Show top 3
    for idx, (path, mod_time, session_id) in enumerate(sessions[:3]):
        formatted_time = mod_time.strftime("%Y-%m-%d %H:%M:%S")
        size_kb = path.stat().st_size / 1024
        size_str = f"{size_kb:.1f} KB"
        # Truncate session ID for display
        display_id = session_id[:8] + "..." if len(session_id) > 11 else session_id
        table.add_row(str(idx + 1), display_id, formatted_time, size_str)
    
    console.print(table)
    
    while True:
        choice = Prompt.ask("Select session", choices=["1", "2", "3"], default="1")
        idx = int(choice) - 1
        if 0 <= idx < min(3, len(sessions)):
            return sessions[idx][0]


def parse_message(data: Dict[str, Any], line_num: int) -> Optional[Message]:
    """Parse a JSON line into a Message object."""
    try:
        # Extract common fields
        uuid = data.get('uuid', '')
        msg_type = data.get('type', '')
        timestamp = data.get('timestamp', '')
        
        # Get message content from nested structure
        message_data = data.get('message', {})
        content = message_data.get('content', data.get('content', ''))
        
        parent_uuid = data.get('parentUuid', data.get('parentMessageUuid'))
        
        msg = Message(
            uuid=uuid,
            type=msg_type,
            timestamp=timestamp,
            content=content,
            parent_uuid=parent_uuid,
            raw_data=data
        )
        
        # Extract tool use/result IDs
        if msg_type == "assistant" and isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'tool_use':
                    tool_id = item.get('id', '')
                    if tool_id:
                        msg.tool_use_ids.append(tool_id)
        
        elif msg_type == "user" and isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'tool_result':
                    tool_id = item.get('tool_use_id', '')
                    if tool_id:
                        msg.tool_result_ids.append(tool_id)
        
        return msg
    except Exception as e:
        console.print(f"[red]Error parsing line {line_num}: {e}[/red]")
        return None


def detect_multiple_sessions(session_path: Path) -> List[str]:
    """Detect if a file contains multiple sessions and return their IDs."""
    session_ids = []
    seen_ids = set()
    
    with open(session_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    session_id = data.get('sessionId', '')
                    if session_id and session_id not in seen_ids:
                        session_ids.append(session_id)
                        seen_ids.add(session_id)
                except json.JSONDecodeError:
                    continue
    
    return session_ids


def split_sessions_to_temp(session_path: Path) -> List[Tuple[Path, str, datetime]]:
    """Split a multi-session file into temporary files.
    
    Returns list of (temp_path, session_id, first_timestamp) tuples.
    """
    sessions = {}  # session_id -> (temp_file, first_timestamp)
    
    with open(session_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    session_id = data.get('sessionId', 'unknown')
                    
                    if session_id not in sessions:
                        # Create temp file for this session
                        temp_file = tempfile.NamedTemporaryFile(
                            mode='w',
                            suffix=f'_{session_id[:8]}.jsonl',
                            delete=False,
                            encoding='utf-8'
                        )
                        # Extract timestamp from first message
                        timestamp_str = data.get('timestamp', '')
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except:
                            timestamp = datetime.now(timezone.utc)
                        sessions[session_id] = (temp_file, timestamp)
                    
                    # Write line to appropriate temp file
                    sessions[session_id][0].write(line)
                except json.JSONDecodeError:
                    continue
    
    # Close all temp files and prepare results
    results = []
    for session_id, (temp_file, timestamp) in sessions.items():
        temp_file.close()
        results.append((Path(temp_file.name), session_id, timestamp))
    
    # Sort by timestamp (most recent first)
    return sorted(results, key=lambda x: x[2], reverse=True)


def load_session(session_path: Path) -> List[Message]:
    """Load JSONL file and parse into Message objects."""
    messages = []
    session_ids_seen = set()
    expected_session_id = None
    
    with open(session_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            if not line.strip():
                continue
            try:
                data = json.loads(line.strip())
                
                # Check for session consistency
                session_id = data.get('sessionId', '')
                if session_id:
                    if expected_session_id is None:
                        expected_session_id = session_id
                    elif session_id != expected_session_id:
                        console.print(f"[yellow]Warning: Multiple sessions detected in file![/yellow]")
                        console.print(f"[yellow]Expected: {expected_session_id}[/yellow]")
                        console.print(f"[yellow]Found: {session_id} at line {line_num + 1}[/yellow]")
                        # Stop loading at session boundary
                        break
                    session_ids_seen.add(session_id)
                
                msg = parse_message(data, line_num)
                if msg:
                    messages.append(msg)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error parsing JSON at line {line_num}: {e}[/red]")
    
    if len(session_ids_seen) > 1:
        console.print(f"[red]File contains {len(session_ids_seen)} different sessions![/red]")
        console.print("[red]Only processing the first session.[/red]")
    
    return messages


def validate_session(messages: List[Message]) -> ValidationResult:
    """Check for tool_use blocks without corresponding tool_result and orphaned tool_results."""
    pending_tool_uses = {}  # tool_use_id -> message_index
    api_error_tool_uses = {}  # tool_use_id -> message_index
    all_tool_uses = set()  # Track all tool_use IDs we've seen
    orphaned_tool_results = []  # tool_results without matching tool_use
    
    # First pass: check for API errors mentioning tool_use problems
    for idx, msg in enumerate(messages):
        if (msg.type == "assistant" and 
            hasattr(msg, 'raw_data') and 
            msg.raw_data.get('isApiErrorMessage', False)):
            content = str(msg.content)
            if "tool_use" in content and "without" in content:
                # Extract tool_use_id from error text
                import re
                match = re.search(r'toolu_\w+', content)
                if match:
                    tool_id = match.group()
                    # Find the message index mentioned in error
                    msg_idx_match = re.search(r'messages\.(\d+):', content)
                    if msg_idx_match:
                        error_msg_idx = int(msg_idx_match.group(1))
                        api_error_tool_uses[tool_id] = error_msg_idx
    
    # Second pass: standard validation
    for idx, msg in enumerate(messages):
        if msg.type == "assistant":
            # Add any tool uses to pending
            for tool_id in msg.tool_use_ids:
                pending_tool_uses[tool_id] = idx
                all_tool_uses.add(tool_id)
                
        elif msg.type == "user":
            # Check for orphaned tool results
            for tool_id in msg.tool_result_ids:
                if tool_id in pending_tool_uses:
                    del pending_tool_uses[tool_id]
                elif tool_id not in all_tool_uses:
                    # This is an orphaned tool_result
                    orphaned_tool_results.append((idx, tool_id))
    
    # Combine problems from all checks
    all_problems = list(pending_tool_uses.items())
    all_problems.extend(api_error_tool_uses.items())
    all_problems.extend(orphaned_tool_results)
    
    # Remove duplicates
    seen = set()
    unique_problems = []
    for item in all_problems:
        if len(item) == 2:
            idx, tool_id = item
            if tool_id not in seen:
                seen.add(tool_id)
                unique_problems.append((idx, tool_id))
    
    if unique_problems:
        return ValidationResult(
            is_valid=False,
            orphaned_tool_uses=unique_problems
        )
    
    return ValidationResult(is_valid=True)


def repair_session(messages: List[Message], validation: ValidationResult) -> List[Message]:
    """Remove problematic messages to restore valid conversation flow."""
    indices_to_remove = set()
    problematic_tool_use_ids = set()
    
    # First pass: find and mark ALL API error messages for removal
    for idx, msg in enumerate(messages):
        if (msg.type == "assistant" and 
            hasattr(msg, 'raw_data') and 
            msg.raw_data.get('isApiErrorMessage', False)):
            # Always remove API error messages
            indices_to_remove.add(idx)
            
            # Extract tool_use_id from error message if it mentions one
            content = str(msg.content)
            if "tool_use" in content and "without" in content:
                # Extract tool_use_id from error text
                import re
                match = re.search(r'toolu_\w+', content)
                if match:
                    problematic_tool_use_ids.add(match.group())
    
    # Second pass: remove messages with problematic tool_use_ids
    for idx, msg in enumerate(messages):
        # Remove tool_use messages with problematic IDs
        if msg.type == "assistant" and msg.tool_use_ids:
            if any(tid in problematic_tool_use_ids for tid in msg.tool_use_ids):
                indices_to_remove.add(idx)
        
        # Remove tool_result messages for problematic IDs
        if msg.type == "user" and msg.tool_result_ids:
            if any(tid in problematic_tool_use_ids for tid in msg.tool_result_ids):
                indices_to_remove.add(idx)
        
        # Remove interrupt messages
        if (msg.type == "user" and isinstance(msg.content, list) and
            any("[Request interrupted" in str(item.get('text', '')) 
                for item in msg.content if isinstance(item, dict))):
            indices_to_remove.add(idx)
        
        # Remove "Request was aborted" error messages
        if (msg.type == "assistant" and isinstance(msg.content, list) and
            any("Request was aborted" in str(item.get('text', '')) 
                for item in msg.content if isinstance(item, dict))):
            indices_to_remove.add(idx)
    
    # Also handle orphaned tool uses from validation
    for tool_use_idx, tool_use_id in validation.orphaned_tool_uses:
        indices_to_remove.add(tool_use_idx)
        # Also check if this might be an orphaned tool_result
        # (when validation detects it at a user message index)
        if tool_use_idx < len(messages) and messages[tool_use_idx].type == "user":
            # This is actually an orphaned tool_result, remove it
            indices_to_remove.add(tool_use_idx)
        else:
            # Remove the tool_result for this orphaned tool_use if it exists
            for idx in range(tool_use_idx + 1, min(tool_use_idx + 5, len(messages))):
                msg = messages[idx]
                if msg.type == "user" and tool_use_id in msg.tool_result_ids:
                    indices_to_remove.add(idx)
    
    # Create new message list excluding problematic messages
    return [msg for idx, msg in enumerate(messages) if idx not in indices_to_remove]


def create_backup(session_path: Path) -> Path:
    """Create backup of session file."""
    backup_path = session_path.with_suffix('.backup.jsonl')
    shutil.copy2(session_path, backup_path)
    console.print(f"[green]✓ Backup created: {backup_path.name}[/green]")
    return backup_path


def save_repaired_session(session_path: Path, messages: List[Message]):
    """Write repaired messages back to JSONL file preserving original formatting."""
    # Create a set of UUIDs to keep for fast lookup
    uuids_to_keep = {msg.uuid for msg in messages}
    
    # Read original file and write only the lines we want to keep
    temp_path = session_path.with_suffix('.tmp')
    
    with open(session_path, 'r', encoding='utf-8') as infile:
        with open(temp_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                if line.strip():  # Skip empty lines
                    try:
                        # Parse just enough to get the UUID
                        data = json.loads(line)
                        uuid = data.get('uuid', '')
                        
                        # If this UUID should be kept, write the original line
                        if uuid in uuids_to_keep:
                            outfile.write(line)
                    except json.JSONDecodeError:
                        # If we can't parse, skip the line
                        pass
    
    # Replace original with temp file
    temp_path.replace(session_path)


@app.command()
def find_broken():
    """Find all broken Claude sessions across all projects using rapid search."""
    console.print("[bold]Searching for broken sessions across all Claude projects...[/bold]")
    
    broken_sessions = find_broken_sessions_with_rg()
    
    if not broken_sessions:
        console.print("[green]✓ No broken sessions found![/green]")
        return
    
    # Display results in a table
    table = Table(title=f"Found {len(broken_sessions)} Broken Sessions")
    table.add_column("Project", style="cyan", width=30)
    table.add_column("Session ID", style="yellow", width=20)
    table.add_column("Error Type", style="red", width=20)
    table.add_column("Last Modified", style="green")
    table.add_column("Size", style="blue")
    
    for idx, (path, mod_time, error_type) in enumerate(broken_sessions[:20]):  # Show top 20
        # Extract project name from path
        project_name = path.parent.name.replace('-', ' ').title()[:30]
        session_id = path.stem[:20]
        formatted_time = mod_time.strftime("%Y-%m-%d %H:%M")
        size_kb = path.stat().st_size / 1024
        size_str = f"{size_kb:.1f} KB"
        
        table.add_row(project_name, session_id, error_type, formatted_time, size_str)
    
    console.print(table)
    
    if len(broken_sessions) > 20:
        console.print(f"\n[yellow]... and {len(broken_sessions) - 20} more broken sessions[/yellow]")
    
    console.print("\n[bold]To repair a specific session:[/bold]")
    console.print("[cyan]claude-repair repair --session-path /path/to/session.jsonl[/cyan]")
    console.print("\n[bold]To repair the most recent broken session:[/bold]")
    console.print("[cyan]claude-repair repair[/cyan]")


@app.command()
def repair(
    project_index: Optional[int] = typer.Option(None, "--project", "-p", help="Project index (1-3)"),
    session_index: Optional[int] = typer.Option(None, "--session", "-s", help="Session index (1-3)"),
    auto_confirm: bool = typer.Option(False, "--yes", "-y", help="Auto-confirm repair"),
    session_path: Optional[Path] = typer.Option(None, "--session-path", "-f", help="Direct path to session JSONL file"),
    use_rg: bool = typer.Option(True, "--use-rg/--no-rg", help="Use ripgrep for fast search")
):
    """Repair a Claude conversation session with broken tool_use/tool_result pairs.
    
    If no session path is provided, searches for broken sessions using rg.
    Automatically handles multi-session files by splitting them.
    """
    # If no session_path provided, find broken sessions
    if not session_path and use_rg:
        console.print("[bold]Searching for broken sessions...[/bold]")
        broken_sessions = find_broken_sessions_with_rg()
        
        if not broken_sessions:
            console.print("[green]✓ No broken sessions found![/green]")
            raise typer.Exit(0)
        
        # Display found sessions
        table = Table(title="Select a Broken Session to Repair")
        table.add_column("Index", style="cyan", width=6)
        table.add_column("Project", style="green", width=25)
        table.add_column("Error Type", style="red", width=15)
        table.add_column("Last Modified", style="yellow")
        table.add_column("Size", style="blue")
        
        # Show top 5 broken sessions
        for idx, (path, mod_time, error_type) in enumerate(broken_sessions[:5]):
            project_name = path.parent.name.replace('-', ' ').title()[:25]
            formatted_time = mod_time.strftime("%Y-%m-%d %H:%M")
            size_kb = path.stat().st_size / 1024
            size_str = f"{size_kb:.1f} KB"
            table.add_row(str(idx + 1), project_name, error_type, formatted_time, size_str)
        
        console.print(table)
        
        choice = Prompt.ask("Select session to repair", choices=[str(i) for i in range(1, min(6, len(broken_sessions) + 1))], default="1")
        session_path = broken_sessions[int(choice) - 1][0]
        console.print(f"\n[bold]Selected: {session_path.name}[/bold]")
    
    # If session_path is provided, use it directly
    elif session_path:
        if not session_path.exists():
            console.print(f"[red]Error: Session file '{session_path}' not found[/red]")
            raise typer.Exit(1)
        if not session_path.suffix == '.jsonl':
            console.print(f"[red]Error: Session file must be a .jsonl file[/red]")
            raise typer.Exit(1)
        selected_session = session_path
        console.print(f"[bold]Using session file: {session_path.name}[/bold]")
    else:
        # Step 1: Project Selection
        console.print("[bold]Finding Claude projects...[/bold]")
        projects = find_claude_projects()
        
        if not projects:
            console.print("[red]No Claude projects found in ~/.claude/projects/[/red]")
            raise typer.Exit(1)
        
        if project_index and 0 < project_index <= len(projects):
            selected_project = projects[project_index - 1][0]
        else:
            selected_project = display_project_selection(projects)
        
        # Step 2: Session Selection
        console.print(f"\n[bold]Finding sessions in {selected_project.name}...[/bold]")
        sessions = find_sessions(selected_project)
        
        if not sessions:
            console.print("[red]No sessions found in project[/red]")
            raise typer.Exit(1)
        
        if session_index and 0 < session_index <= len(sessions):
            selected_session = sessions[session_index - 1][0]
        else:
            selected_session = display_session_selection(sessions)
    
    # Check if file contains multiple sessions
    console.print(f"\n[bold]Checking for multiple sessions in {selected_session.name}...[/bold]")
    session_ids = detect_multiple_sessions(selected_session)
    
    if len(session_ids) > 1:
        console.print(f"[yellow]Warning: File contains {len(session_ids)} sessions![/yellow]")
        console.print("[bold]Splitting sessions for individual repair...[/bold]")
        
        # Split sessions into temporary files
        split_sessions = split_sessions_to_temp(selected_session)
        
        # Display split sessions with validation status
        table = Table(title="Split Sessions")
        table.add_column("Index", style="cyan", width=6)
        table.add_column("Session ID", style="green", width=30)
        table.add_column("Date", style="yellow")
        table.add_column("Status", style="red")
        table.add_column("Resume Command", style="blue")
        
        corrupted_sessions = []
        
        for idx, (temp_path, session_id, timestamp) in enumerate(split_sessions):
            # Validate each split session
            try:
                temp_messages = load_session(temp_path)
                temp_validation = validate_session(temp_messages)
                status = "✓ Valid" if temp_validation.is_valid else "✗ Corrupted"
                if not temp_validation.is_valid:
                    corrupted_sessions.append((idx, temp_path, session_id, timestamp))
            except:
                status = "✗ Error"
                corrupted_sessions.append((idx, temp_path, session_id, timestamp))
            
            date_str = timestamp.strftime("%Y-%m-%d")
            resume_cmd = f"claude --resume {session_id[:8]}..."
            table.add_row(str(idx + 1), session_id[:8] + "...", date_str, status, resume_cmd)
        
        console.print(table)
        
        # Clean up temp files if user doesn't want to proceed
        if not corrupted_sessions:
            console.print("\n[green]✓ All split sessions are valid![/green]")
            for temp_path, _, _ in split_sessions:
                temp_path.unlink()
            raise typer.Exit(0)
        
        console.print(f"\n[yellow]Found {len(corrupted_sessions)} corrupted sessions[/yellow]")
        
        if not auto_confirm:
            if not Confirm.ask("Repair all corrupted sessions?"):
                # Clean up temp files
                for temp_path, _, _ in split_sessions:
                    temp_path.unlink()
                raise typer.Exit(0)
        
        # Repair each corrupted session
        for idx, temp_path, session_id, timestamp in corrupted_sessions:
            console.print(f"\n[bold]Repairing session {session_id[:8]}...[/bold]")
            
            # Load and repair
            messages = load_session(temp_path)
            validation = validate_session(messages)
            repaired_messages = repair_session(messages, validation)
            
            # Save repaired session to original location
            output_path = selected_session.parent / f"{session_id}.jsonl"
            with open(output_path, 'w', encoding='utf-8') as f:
                for msg in repaired_messages:
                    f.write(json.dumps(msg.raw_data) + '\n')
            
            console.print(f"[green]✓ Repaired and saved to {output_path.name}[/green]")
            console.print(f"[cyan]Resume with: claude --resume {session_id}[/cyan]")
        
        # Clean up all temp files
        for temp_path, _, _ in split_sessions:
            temp_path.unlink()
        
        console.print("\n[green]✓ All corrupted sessions have been repaired![/green]")
        raise typer.Exit(0)
    
    # Single session - proceed with normal repair
    console.print(f"\n[bold]Loading session {selected_session.name}...[/bold]")
    messages = load_session(selected_session)
    console.print(f"Loaded {len(messages)} messages")
    
    validation = validate_session(messages)
    
    if validation.is_valid:
        console.print("[green]✓ Session is valid, no repair needed![/green]")
        raise typer.Exit(0)
    
    # Step 4: Show Problems
    console.print(f"\n[yellow]Found {len(validation.orphaned_tool_uses)} orphaned tool_use blocks[/yellow]")
    for idx, tool_id in validation.orphaned_tool_uses[:5]:  # Show first 5
        console.print(f"  - Message {idx}: {tool_id}")
    if len(validation.orphaned_tool_uses) > 5:
        console.print(f"  ... and {len(validation.orphaned_tool_uses) - 5} more")
    
    # Step 5: Confirm Repair
    if not auto_confirm:
        if not Confirm.ask("Proceed with repair?"):
            raise typer.Exit(0)
    
    # Step 6: Backup
    backup_path = create_backup(selected_session)
    
    # Step 7: Repair
    console.print("\n[bold]Repairing session...[/bold]")
    repaired_messages = repair_session(messages, validation)
    removed_count = len(messages) - len(repaired_messages)
    console.print(f"Removed {removed_count} problematic messages")
    
    # Step 8: Save
    save_repaired_session(selected_session, repaired_messages)
    console.print("[green]✓ Session repaired and saved[/green]")
    
    # Step 9: Test and Confirm
    console.print("\n[bold]Please test the repaired session in Claude[/bold]")
    console.print("Options:")
    console.print("  [cyan]r[/cyan] - Restore from backup")
    console.print("  [cyan]c[/cyan] - Continue (delete backup)")
    
    while True:
        choice = Prompt.ask("Your choice", choices=["r", "c"])
        
        if choice == 'r':
            shutil.copy2(backup_path, selected_session)
            backup_path.unlink()
            console.print("[yellow]✓ Restored from backup[/yellow]")
            break
            
        elif choice == 'c':
            backup_path.unlink()
            console.print("[green]✓ Backup deleted, repair complete![/green]")
            
            # Extract project path from session path
            if session_path:
                # Extract project directory from session path
                # Path format: ~/.claude/projects/-Users-christophermann-path-to-project/session.jsonl
                project_dir_name = session_path.parent.name
                # Convert back to actual path: -Users-christophermann-path -> /Users/christophermann/path
                actual_path = project_dir_name.replace('-', '/').lstrip('/')
                console.print("\n[bold]To continue this session:[/bold]")
                console.print(f"[cyan]cd /{actual_path}[/cyan]")
                console.print("[cyan]claude -c[/cyan]")
            else:
                # For interactive selection, we already have the project path
                # Convert project name to actual path
                project_dir_name = selected_project.name
                actual_path = project_dir_name.replace('-', '/').lstrip('/')
                console.print("\n[bold]To continue this session:[/bold]")
                console.print(f"[cyan]cd /{actual_path}[/cyan]")
                console.print("[cyan]claude -c[/cyan]")
            break


@app.command()
def validate(
    project_index: Optional[int] = typer.Option(None, "--project", "-p", help="Project index (1-3)"),
    session_index: Optional[int] = typer.Option(None, "--session", "-s", help="Session index (1-3)"),
    session_path: Optional[Path] = typer.Option(None, "--session-path", "-f", help="Direct path to session JSONL file")
):
    """Validate a Claude session without repairing it."""
    # If session_path is provided, use it directly
    if session_path:
        if not session_path.exists():
            console.print(f"[red]Error: Session file '{session_path}' not found[/red]")
            raise typer.Exit(1)
        if not session_path.suffix == '.jsonl':
            console.print(f"[red]Error: Session file must be a .jsonl file[/red]")
            raise typer.Exit(1)
        selected_session = session_path
        console.print(f"[bold]Using session file: {session_path.name}[/bold]")
    else:
        # Step 1: Project Selection
        console.print("[bold]Finding Claude projects...[/bold]")
        projects = find_claude_projects()
        
        if not projects:
            console.print("[red]No Claude projects found in ~/.claude/projects/[/red]")
            raise typer.Exit(1)
        
        if project_index and 0 < project_index <= len(projects):
            selected_project = projects[project_index - 1][0]
        else:
            selected_project = display_project_selection(projects)
        
        # Step 2: Session Selection
        console.print(f"\n[bold]Finding sessions in {selected_project.name}...[/bold]")
        sessions = find_sessions(selected_project)
        
        if not sessions:
            console.print("[red]No sessions found in project[/red]")
            raise typer.Exit(1)
        
        if session_index and 0 < session_index <= len(sessions):
            selected_session = sessions[session_index - 1][0]
        else:
            selected_session = display_session_selection(sessions)
    
    # Step 3: Load and Validate
    console.print(f"\n[bold]Loading session {selected_session.name}...[/bold]")
    messages = load_session(selected_session)
    console.print(f"Loaded {len(messages)} messages")
    
    validation = validate_session(messages)
    
    if validation.is_valid:
        console.print("[green]✓ Session is valid![/green]")
    else:
        console.print(f"\n[yellow]Found {len(validation.orphaned_tool_uses)} orphaned tool_use blocks[/yellow]")
        for idx, tool_id in validation.orphaned_tool_uses:
            console.print(f"  - Message {idx}: {tool_id}")


@app.command()
def split(
    session_path: Path = typer.Argument(..., help="Path to session JSONL file"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for split sessions")
):
    """Split a file containing multiple sessions into separate files."""
    if not session_path.exists():
        console.print(f"[red]Error: Session file '{session_path}' not found[/red]")
        raise typer.Exit(1)
    
    if not output_dir:
        output_dir = session_path.parent
    
    output_dir.mkdir(exist_ok=True)
    
    sessions = {}  # session_id -> list of lines
    line_count = 0
    
    with open(session_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_count += 1
            if line.strip():
                try:
                    data = json.loads(line)
                    session_id = data.get('sessionId', 'unknown')
                    
                    if session_id not in sessions:
                        sessions[session_id] = []
                    sessions[session_id].append(line)
                except json.JSONDecodeError:
                    console.print(f"[yellow]Warning: Skipping invalid JSON at line {line_count}[/yellow]")
    
    console.print(f"\n[bold]Found {len(sessions)} sessions in file:[/bold]")
    
    for session_id, lines in sessions.items():
        output_file = output_dir / f"{session_id}.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line)
        console.print(f"[green]✓ Wrote {len(lines)} messages to {output_file.name}[/green]")
    
    if len(sessions) > 1:
        console.print("\n[yellow]Note: Original file contains multiple sessions.[/yellow]")
        console.print("[yellow]Each session has been saved to a separate file.[/yellow]")
        console.print("[yellow]You may want to repair each session individually.[/yellow]")


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()