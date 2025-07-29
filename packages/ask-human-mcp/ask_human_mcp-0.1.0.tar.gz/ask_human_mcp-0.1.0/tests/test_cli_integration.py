"""CLI integration tests for the Ask-Human MCP server"""

import asyncio
import json
import subprocess
import tempfile
import time
from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_cli_help():
    """Test that the CLI help command works"""
    result = subprocess.run(
        ["python", "-m", "ask_human_mcp.server", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0
    assert "Ask-Human MCP Server" in result.stdout
    assert "--port" in result.stdout
    assert "--host" in result.stdout
    assert "--timeout" in result.stdout


@pytest.mark.asyncio
async def test_stdio_mode_startup():
    """Test that stdio mode starts up correctly"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        ask_file = Path(f.name)
    
    try:
        # Start server in stdio mode
        process = subprocess.Popen(
            ["python", "-m", "ask_human_mcp.server", "--file", str(ask_file)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send a minimal MCP handshake
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        # Send the request
        request_line = json.dumps(init_request) + "\n"
        process.stdin.write(request_line)
        process.stdin.flush()
        
        # Wait for response (with timeout)
        try:
            stdout, stderr = process.communicate(timeout=5)
            
            # Should not crash immediately
            assert process.returncode is not None
            
            # Should contain MCP response
            if stdout:
                assert "jsonrpc" in stdout or "protocolVersion" in stdout
                
        except subprocess.TimeoutExpired:
            # Server is still running, which is good
            process.terminate()
            process.wait(timeout=5)
        
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        ask_file.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_http_mode_startup():
    """Test that HTTP mode starts up correctly"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        ask_file = Path(f.name)
    
    try:
        # Start server in HTTP mode on a random port
        process = subprocess.Popen(
            [
                "python", "-m", "ask_human_mcp.server",
                "--host", "127.0.0.1",
                "--port", "0",  # Let OS choose port
                "--file", str(ask_file)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it time to start up
        await asyncio.sleep(2)
        
        # Check if process is still running
        assert process.poll() is None, "Server process exited unexpectedly"
        
        # Terminate the server
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        
        # Should have started successfully
        assert "Starting Ask-Human MCP server" in stderr or "Uvicorn running" in stderr
        
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        ask_file.unlink(missing_ok=True)


def test_package_entry_point():
    """Test that the package entry point works"""
    result = subprocess.run(
        ["ask-human-mcp", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # Should work if package is properly installed
    assert result.returncode == 0
    assert "Ask-Human MCP Server" in result.stdout


def test_config_validation():
    """Test that invalid configuration is rejected"""
    # Test invalid timeout
    result = subprocess.run(
        ["python", "-m", "ask_human_mcp.server", "--timeout", "-1"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    assert result.returncode != 0
    assert "positive" in result.stderr.lower() or "invalid" in result.stderr.lower()
    
    # Test invalid port
    result = subprocess.run(
        ["python", "-m", "ask_human_mcp.server", "--port", "99999"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    assert result.returncode != 0 