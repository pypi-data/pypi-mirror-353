"""Integration tests for the Ask-Human MCP server"""

import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from ask_human_mcp.server import AskHumanConfig, AskHumanServer, safe_write_text


@pytest.fixture
def integration_config():
    """Create configuration for integration testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        ask_file = Path(f.name)
    
    config = AskHumanConfig(
        ask_file=ask_file,
        timeout=5,  # Short timeout for testing
        max_question_length=1000,
        max_context_length=2000,
        max_pending_questions=10,
        max_file_size=1000000,
        rotation_size=500000,
    )
    
    yield config
    
    # Cleanup
    ask_file.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_full_question_answer_workflow(integration_config):
    """Test the complete workflow: ask question -> human answers -> AI gets response"""
    server = AskHumanServer(integration_config)
    
    try:
        # Start the server
        server.start_watching()
        
        # Step 1: AI asks a question
        question_task = asyncio.create_task(
            server._handle_question("What's the database password?", "Setting up auth")
        )
        
        # Give it a moment to write the question
        await asyncio.sleep(0.1)
        
        # Step 2: Verify question was written to file
        content = safe_read_text(integration_config.ask_file)
        assert "What's the database password?" in content
        assert "Setting up auth" in content
        assert "PENDING" in content
        
        # Extract question ID from the content
        import re
        q_id_match = re.search(r"### (Q[a-zA-Z0-9]+)", content)
        assert q_id_match, "Question ID not found in file"
        q_id = q_id_match.group(1)
        
        # Step 3: Human provides answer (simulate editing the file)
        updated_content = content.replace("**Answer:** PENDING", "**Answer:** password123")
        safe_write_text(integration_config.ask_file, updated_content)
        
        # Step 4: AI should receive the answer
        answer = await question_task
        assert answer == "password123"
        
        # Step 5: Verify question is marked as answered
        assert q_id in server.answered_questions
        assert q_id not in server.pending_questions
        
    finally:
        server.stop_watching()


@pytest.mark.asyncio
async def test_concurrent_questions(integration_config):
    """Test handling multiple questions simultaneously"""
    server = AskHumanServer(integration_config)
    
    try:
        server.start_watching()
        
        # Ask multiple questions concurrently
        tasks = [
            asyncio.create_task(server._handle_question(f"Question {i}?", f"Context {i}"))
            for i in range(3)
        ]
        
        # Wait for questions to be written
        await asyncio.sleep(0.2)
        
        # Read file and answer all questions
        content = safe_read_text(integration_config.ask_file)
        
        # Find all question IDs and answer them
        q_ids = re.findall(r"### (Q[a-zA-Z0-9]+)", content)
        assert len(q_ids) == 3
        
        # Answer each question
        for i, q_id in enumerate(q_ids):
            content = content.replace(
                f"### {q_id}\n**Timestamp:**",
                f"### {q_id}\n**Timestamp:**"
            ).replace(
                "**Answer:** PENDING",
                f"**Answer:** Answer {i}",
                1  # Replace only the first occurrence
            )
        
        safe_write_text(integration_config.ask_file, content)
        
        # Wait for all answers
        answers = await asyncio.gather(*tasks)
        
        # Verify answers
        expected_answers = [f"Answer {i}" for i in range(3)]
        assert sorted(answers) == sorted(expected_answers)
        
    finally:
        server.stop_watching()


@pytest.mark.asyncio
async def test_question_timeout(integration_config):
    """Test that questions timeout appropriately"""
    server = AskHumanServer(integration_config)
    
    try:
        server.start_watching()
        
        # Ask a question but don't answer it
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                server._handle_question("Unanswered question?", "Will timeout"),
                timeout=6  # Slightly longer than server timeout
            )
        
    finally:
        server.stop_watching()


@pytest.mark.asyncio
async def test_mcp_tool_integration(integration_config):
    """Test that MCP tools work correctly"""
    server = AskHumanServer(integration_config)
    
    try:
        server.start_watching()
        
        # Test ask_human tool
        question_task = asyncio.create_task(
            server.mcp.call_tool("ask_human", {
                "question": "What's the API endpoint?",
                "context": "Building client"
            })
        )
        
        await asyncio.sleep(0.1)
        
        # Answer the question
        content = safe_read_text(integration_config.ask_file)
        updated_content = content.replace("**Answer:** PENDING", "**Answer:** /api/v1/users")
        safe_write_text(integration_config.ask_file, updated_content)
        
        result = await question_task
        assert result == "/api/v1/users"
        
        # Test list_pending_questions tool
        # First, ask a question without answering
        asyncio.create_task(
            server._handle_question("Pending question?", "Will remain pending")
        )
        await asyncio.sleep(0.1)
        
        pending_result = await server.mcp.call_tool("list_pending_questions", {})
        assert "Pending question?" in pending_result
        
        # Test get_qa_stats tool
        stats_result = await server.mcp.call_tool("get_qa_stats", {})
        assert "Total questions asked:" in stats_result
        assert "Currently pending:" in stats_result
        
    finally:
        server.stop_watching()


@pytest.mark.asyncio
async def test_file_watching_accuracy(integration_config):
    """Test that file watching detects changes accurately"""
    server = AskHumanServer(integration_config)
    
    try:
        server.start_watching()
        
        # Create initial content
        initial_content = """
### Q12345678
**Timestamp:** 2025-01-15 14:30:22
**Question:** Test question?
**Context:** Test context
**Answer:** PENDING
"""
        safe_write_text(integration_config.ask_file, initial_content)
        
        # Register a callback for the question
        future = await server.watcher.register_callback("Q12345678")
        
        # Modify the file (simulate human answering)
        updated_content = initial_content.replace("**Answer:** PENDING", "**Answer:** Test answer")
        safe_write_text(integration_config.ask_file, updated_content)
        
        # The callback should be notified
        await asyncio.wait_for(future, timeout=2)
        
        # Verify the answer can be read
        answer = server._read_answer("Q12345678")
        assert answer == "Test answer"
        
    finally:
        server.stop_watching()


def safe_read_text(file_path: Path, encoding: str = "utf-8") -> str:
    """Helper function to safely read text files"""
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except Exception:
        return "" 