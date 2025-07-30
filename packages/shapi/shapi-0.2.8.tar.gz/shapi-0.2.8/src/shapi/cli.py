"""
Command line interface for shapi.
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional

from .generator import ServiceGenerator
from .core import ShapiService
import uvicorn


@click.group()
@click.version_option(version="0.2.0")
def main():
    """shapi - Transform shell scripts into production-ready APIs."""
    pass


@main.command()
@click.argument("script_path", type=click.Path(exists=True))
@click.option("--name", "-n", help="Service name (defaults to script filename)")
@click.option("--output", "-o", default="./generated", help="Output directory")
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
def generate(script_path: str, name: Optional[str], output: str, config: Optional[str]):
    """Generate API service for a shell script."""

    script_path_obj = Path(script_path)
    service_name = name or script_path_obj.stem

    # Load configuration if provided
    service_config = {}
    if config:
        import yaml

        with open(config, "r") as f:
            service_config = yaml.safe_load(f)

    generator = ServiceGenerator(output)
    service_dir = generator.generate_service(script_path, service_name, service_config)

    click.echo(f"✅ Service generated successfully in: {service_dir}")
    click.echo(f"📁 Generated files:")
    click.echo(f"   - main.py")
    click.echo(f"   - Dockerfile")
    click.echo(f"   - Makefile")
    click.echo(f"   - test_service.py")
    click.echo(f"   - requirements.txt")
    click.echo(f"   - docker-compose.yml")
    click.echo(f"   - ansible/test.yml")
    click.echo(f"\n🚀 To run the service:")
    click.echo(f"   cd {service_dir}")
    click.echo(f"   python main.py")


@main.command()
@click.argument("script_path", type=click.Path(exists=True))
@click.option("--name", "-n", help="Service name")
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
@click.option("--port", "-p", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--force", "-f", is_flag=True, help="Force stop any service running on the same port")
async def serve(script_path: str, name: Optional[str], host: str, port: int, reload: bool, force: bool):
    """Serve a shell script as an API directly."""
    import asyncio
    
    try:
        script_path_obj = Path(script_path)
        service_name = name or script_path_obj.stem

        # Create service instance with host and port
        service = ShapiService(script_path, service_name, host=host, port=port)

        # Check if port is available
        is_used, pid = service.is_port_in_use(port, host)
        
        if is_used:
            if not force:
                click.echo(f"❌ Port {port} is already in use by process {pid}")
                click.echo(f"   Use --force to stop the existing service")
                return 1
            
            click.echo(f"⚠️  Stopping existing service on port {port}...")
            if service.stop_process_on_port(port, host):
                click.echo(f"✅ Successfully stopped process on port {port}")
                # Small delay to ensure port is released
                await asyncio.sleep(1)
            else:
                click.echo(f"❌ Failed to stop process on port {port}")
                return 1

        click.echo(f"🚀 Starting shapi service for: {service_name}")
        click.echo(f"📍 Script: {script_path}")
        click.echo(f"🌐 Server: http://{host}:{port}")
        click.echo(f"📖 Docs: http://{host}:{port}/docs")
        click.echo(f"❤️  Health: http://{host}:{port}/health")
        click.echo("🛑 Press Ctrl+C to stop the service")

        # Run the service
        config = uvicorn.Config(
            service.app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        except asyncio.CancelledError:
            click.echo("\n👋 Shutting down gracefully...")
            await server.shutdown()
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        return 1


@main.command()
@click.argument("service_dir", type=click.Path(exists=True))
def test(service_dir: str):
    """Run tests for generated service."""

    service_path = Path(service_dir)
    test_file = service_path / "test_service.py"

    if not test_file.exists():
        click.echo("❌ Test file not found. Generate service first.")
        sys.exit(1)

    import subprocess

    click.echo("🧪 Running service tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v"], cwd=service_path
    )

    if result.returncode == 0:
        click.echo("✅ All tests passed!")
    else:
        click.echo("❌ Some tests failed.")
        sys.exit(1)


@main.command()
@click.argument("service_dir", type=click.Path(exists=True))
def build(service_dir: str):
    """Build Docker image for generated service."""

    service_path = Path(service_dir)
    dockerfile = service_path / "Dockerfile"

    if not dockerfile.exists():
        click.echo("❌ Dockerfile not found. Generate service first.")
        sys.exit(1)

    import subprocess

    service_name = service_path.name
    image_name = f"shapi-{service_name}:latest"

    click.echo(f"🐳 Building Docker image: {image_name}")

    result = subprocess.run(
        ["docker", "build", "-t", image_name, "."], cwd=service_path
    )

    if result.returncode == 0:
        click.echo(f"✅ Docker image built successfully: {image_name}")
    else:
        click.echo("❌ Docker build failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
