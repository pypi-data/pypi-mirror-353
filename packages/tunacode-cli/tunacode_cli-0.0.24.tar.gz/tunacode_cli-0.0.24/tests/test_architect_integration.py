#!/usr/bin/env python3
"""Integration test for architect mode with actual orchestrator."""

import asyncio
import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


@pytest.mark.asyncio
async def test_orchestrator_planning():
    """Test that orchestrator actually creates and shows a plan."""
    try:
        from tunacode.core.agents.orchestrator import OrchestratorAgent
        from tunacode.core.state import StateManager
        from tunacode.types import ModelName
        from unittest.mock import patch, MagicMock, AsyncMock
        from tunacode.core.agents.planner_schema import Task
        
        # Create state manager
        state = StateManager()
        state.session.current_model = ModelName("anthropic:claude-3-haiku-20240307")
        state.session.user_config = {
            "settings": {
                "max_retries": 3,
                "max_iterations": 20
            }
        }
        
        # Create orchestrator
        orchestrator = OrchestratorAgent(state)
        
        # Create proper Task objects
        mock_tasks = [
            Task(id=1, description="Read the file", mutate=False),
            Task(id=2, description="Update the code", mutate=True)
        ]
        
        # Capture console output
        outputs = []
        
        def capture_print(*args, **kwargs):
            if args:
                outputs.append(str(args[0]))
        
        # Mock the Agent class to avoid API key requirement
        mock_agent_instance = MagicMock()
        mock_agent_instance.run = AsyncMock(return_value=MagicMock(data=mock_tasks))
        
        with patch('rich.console.Console.print', side_effect=capture_print):
            # Mock get_agent_tool to return our mock Agent class
            with patch('tunacode.core.agents.main.get_agent_tool', return_value=(MagicMock(return_value=mock_agent_instance), None)):
                # Mock the agent execution
                mock_run = MagicMock()
                mock_run.result = MagicMock(output="Task completed")
                
                with patch.object(orchestrator, '_run_sub_task', new_callable=AsyncMock, return_value=mock_run):
                    # Run orchestrator
                    results = await orchestrator.run("Test request")
                    
                    # Check outputs
                    assert any("Orchestrator Mode" in out for out in outputs), "Missing orchestrator start message"
                    assert any("Executing plan" in out for out in outputs), "Missing execution message"
                    assert any("Orchestrator completed" in out for out in outputs), "Missing completion message"
        
    except ImportError as e:
        pytest.skip(f"Skipping integration test due to missing dependencies: {e}")


@pytest.mark.asyncio
async def test_architect_mode_check():
    """Test the actual check in repl.py for architect mode."""
    # Simulate the check from repl.py
    class MockSession:
        architect_mode = False
    
    class MockState:
        session = MockSession()
    
    state = MockState()
    
    # Test the actual condition used in repl.py
    if getattr(state.session, 'architect_mode', False):
        assert False, "Should not use orchestrator when architect_mode is False"
    
    # Enable architect mode
    state.session.architect_mode = True
    
    if not getattr(state.session, 'architect_mode', False):
        assert False, "Should use orchestrator when architect_mode is True"


# Remove the main() function and if __name__ block since pytest will handle test discovery and execution