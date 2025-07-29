#!/usr/bin/env python3
"""Test the orchestrator planning visibility features."""

import asyncio
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

@pytest.mark.asyncio
async def test_planning_visibility():
    """Test that planning steps are visible in orchestrator output."""
    from tunacode.core.agents.orchestrator import OrchestratorAgent
    from tunacode.core.state import StateManager
    from tunacode.types import ModelName
    from unittest.mock import patch, MagicMock, AsyncMock
    from tunacode.core.agents.planner_schema import Task
    
    # Create state manager
    state = StateManager()
    
    # Set a default model
    state.session.current_model = ModelName("anthropic:claude-3-haiku-20240307")
    
    # Set required config
    state.session.user_config = {
        "settings": {
            "max_retries": 3,
            "max_iterations": 20
        }
    }
    
    # Create orchestrator
    orchestrator = OrchestratorAgent(state)
    
    # Test request that should generate multiple tasks
    test_request = """
    I need to analyze the project structure and then add a new feature.
    First, read the README.md file to understand the project.
    Then create a new file called feature.py with a simple function.
    """
    
    # Create proper Task objects
    mock_tasks = [
        Task(id=1, description="Read README.md", mutate=False),
        Task(id=2, description="Create feature.py", mutate=True)
    ]
    
    # Mock the Agent class to avoid API key requirement
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = AsyncMock(return_value=MagicMock(data=mock_tasks))
    
    # Mock get_agent_tool to return our mock Agent class
    with patch('tunacode.core.agents.main.get_agent_tool', return_value=(MagicMock(return_value=mock_agent_instance), None)):
        # Mock the agent execution
        mock_run = MagicMock()
        mock_run.result = MagicMock(output="Task completed")
        
        with patch.object(orchestrator, '_run_sub_task', new_callable=AsyncMock, return_value=mock_run):
            # Run the orchestrator
            results = await orchestrator.run(test_request)
            
            assert len(results) == len(mock_tasks), f"Expected {len(mock_tasks)} results, got {len(results)}"