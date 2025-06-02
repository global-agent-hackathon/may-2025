"""
Main CLI implementation for ZeroMesh
"""

import asyncio
import click
import json
import os
from datetime import datetime, timedelta
from typing import Optional

from ..config import ZeroMeshConfig, load_config
from ..services.registry import ServiceRegistry
from ..services.core import CoreService
from ..dashboard.app import create_app
import uvicorn

@click.group()
def cli():
    """ZeroMesh - Zero-Trust Security Layer for Agent Communication"""
    pass

@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to config file')
def start(config):
    """Start the ZeroMesh service"""
    if config:
        # Load custom config file if provided
        with open(config) as f:
            config_data = json.load(f)
            os.environ.update(config_data)
    
    # Load configuration
    config = load_config()
    
    # Create service registry
    registry = ServiceRegistry(config)
    
    # Register core service
    registry.register_service_type("core", CoreService)
    
    async def run():
        # Initialize and start core service
        await registry.initialize_service("core")
        await registry.start_all()
        
        click.echo("ZeroMesh service started. Press Ctrl+C to stop.")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await registry.stop_all()
            click.echo("\nZeroMesh service stopped.")

    asyncio.run(run())

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind the dashboard to')
@click.option('--port', default=8080, help='Port to run the dashboard on')
@click.option('--dev/--prod', default=False, help='Run in development mode')
def dashboard(host: str, port: int, dev: bool):
    """Start the ZeroMesh web dashboard"""
    if dev:
        click.echo("Starting dashboard in development mode...")
        click.echo("Please run 'npm start' in zeromesh/dashboard/static directory for the frontend")
    
    click.echo(f"Starting dashboard on http://{host}:{port}")
    app = create_app()
    uvicorn.run(app, host=host, port=port)

@cli.group()
def policy():
    """Manage security policies"""
    pass

@policy.command('block')
@click.argument('agent_id')
@click.option('--reason', required=True, help='Reason for blocking')
def block_agent(agent_id: str, reason: str):
    """Block an agent from sending messages"""
    config = load_config()
    registry = ServiceRegistry(config)
    registry.register_service_type("core", CoreService)
    
    async def run():
        core = await registry.initialize_service("core")
        await core.handle_message("system", {
            "type": "block_agent",
            "agent_id": agent_id,
            "reason": reason
        })
        click.echo(f"Agent {agent_id} has been blocked")
        await registry.stop_all()

    asyncio.run(run())

@cli.group()
def trust():
    """Manage trust relationships"""
    pass

@trust.command('score')
@click.argument('agent_id')
def get_trust_score(agent_id: str):
    """Get trust score for an agent"""
    config = load_config()
    registry = ServiceRegistry(config)
    registry.register_service_type("core", CoreService)
    
    async def run():
        core = await registry.initialize_service("core")
        result = await core.handle_message("system", {
            "type": "get_trust_score",
            "agent_id": agent_id
        })
        click.echo(f"Trust score for {agent_id}: {result['score']:.2f}")
        await registry.stop_all()

    asyncio.run(run())

@cli.group()
def audit():
    """Query audit logs"""
    pass

@audit.command('query')
@click.option('--type', 'event_type', help='Event type filter')
@click.option('--agent', help='Agent ID filter')
@click.option('--start', help='Start time (ISO format)')
@click.option('--end', help='End time (ISO format)')
def query_logs(event_type: Optional[str], agent: Optional[str], 
               start: Optional[str], end: Optional[str]):
    """Query audit logs with filters"""
    config = load_config()
    registry = ServiceRegistry(config)
    registry.register_service_type("core", CoreService)
    
    async def run():
        core = await registry.initialize_service("core")
        result = await core.handle_message("system", {
            "type": "query_audit_logs",
            "filters": {
                "event_type": event_type,
                "agent_id": agent,
                "start_time": start,
                "end_time": end
            }
        })
        
        for event in result['events']:
            click.echo(json.dumps(event, indent=2))
            
        await registry.stop_all()

    asyncio.run(run()) 