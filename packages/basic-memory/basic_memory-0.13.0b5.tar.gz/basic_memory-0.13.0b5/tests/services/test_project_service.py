"""Tests for ProjectService."""

import os

import pytest

from basic_memory.schemas import (
    ProjectInfoResponse,
    ProjectStatistics,
    ActivityMetrics,
    SystemStatus,
)
from basic_memory.services.project_service import ProjectService
from basic_memory.config import ConfigManager


def test_projects_property(project_service: ProjectService):
    """Test the projects property."""
    # Get the projects
    projects = project_service.projects

    # Assert that it returns a dictionary
    assert isinstance(projects, dict)
    # The test config should have at least one project
    assert len(projects) > 0


def test_default_project_property(project_service: ProjectService):
    """Test the default_project property."""
    # Get the default project
    default_project = project_service.default_project

    # Assert it's a string and has a value
    assert isinstance(default_project, str)
    assert default_project


def test_current_project_property(project_service: ProjectService):
    """Test the current_project property."""
    # Save original environment
    original_env = os.environ.get("BASIC_MEMORY_PROJECT")

    try:
        # Test with environment variable not set
        if "BASIC_MEMORY_PROJECT" in os.environ:
            del os.environ["BASIC_MEMORY_PROJECT"]

        # Should return default_project when env var not set
        assert project_service.current_project == project_service.default_project

        # Now set the environment variable
        os.environ["BASIC_MEMORY_PROJECT"] = "test-project"

        # Should return env var value
        assert project_service.current_project == "test-project"
    finally:
        # Restore original environment
        if original_env is not None:
            os.environ["BASIC_MEMORY_PROJECT"] = original_env
        elif "BASIC_MEMORY_PROJECT" in os.environ:
            del os.environ["BASIC_MEMORY_PROJECT"]

    """Test the methods of ProjectService."""


@pytest.mark.asyncio
async def test_project_operations_sync_methods(
    app_config, project_service: ProjectService, config_manager: ConfigManager, tmp_path
):
    """Test adding, switching, and removing a project using ConfigManager directly.

    This test uses the ConfigManager directly instead of the async methods.
    """
    # Generate a unique project name for testing
    test_project_name = f"test-project-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-project")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    try:
        # Test adding a project (using ConfigManager directly)
        config_manager.add_project(test_project_name, test_project_path)

        # Verify it was added
        assert test_project_name in project_service.projects
        assert project_service.projects[test_project_name] == test_project_path

        # Test setting as default
        original_default = project_service.default_project
        config_manager.set_default_project(test_project_name)
        assert project_service.default_project == test_project_name

        # Restore original default
        if original_default:
            config_manager.set_default_project(original_default)

        # Test removing the project
        config_manager.remove_project(test_project_name)
        assert test_project_name not in project_service.projects

    except Exception as e:
        # Clean up in case of error
        if test_project_name in project_service.projects:
            try:
                config_manager.remove_project(test_project_name)
            except Exception:
                pass
        raise e


@pytest.mark.asyncio
async def test_get_system_status(project_service: ProjectService):
    """Test getting system status."""
    # Get the system status
    status = project_service.get_system_status()

    # Assert it returns a valid SystemStatus object
    assert isinstance(status, SystemStatus)
    assert status.version
    assert status.database_path
    assert status.database_size


@pytest.mark.asyncio
async def test_get_statistics(project_service: ProjectService, test_graph, test_project):
    """Test getting statistics."""
    # Get statistics
    statistics = await project_service.get_statistics(test_project.id)

    # Assert it returns a valid ProjectStatistics object
    assert isinstance(statistics, ProjectStatistics)
    assert statistics.total_entities > 0
    assert "test" in statistics.entity_types


@pytest.mark.asyncio
async def test_get_activity_metrics(project_service: ProjectService, test_graph, test_project):
    """Test getting activity metrics."""
    # Get activity metrics
    metrics = await project_service.get_activity_metrics(test_project.id)

    # Assert it returns a valid ActivityMetrics object
    assert isinstance(metrics, ActivityMetrics)
    assert len(metrics.recently_created) > 0
    assert len(metrics.recently_updated) > 0


@pytest.mark.asyncio
async def test_get_project_info(project_service: ProjectService, test_graph, test_project):
    """Test getting full project info."""
    # Get project info
    info = await project_service.get_project_info(test_project.name)

    # Assert it returns a valid ProjectInfoResponse object
    assert isinstance(info, ProjectInfoResponse)
    assert info.project_name
    assert info.project_path
    assert info.default_project
    assert isinstance(info.available_projects, dict)
    assert isinstance(info.statistics, ProjectStatistics)
    assert isinstance(info.activity, ActivityMetrics)
    assert isinstance(info.system, SystemStatus)


@pytest.mark.asyncio
async def test_add_project_async(project_service: ProjectService, tmp_path):
    """Test adding a project with the updated async method."""
    test_project_name = f"test-async-project-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-async-project")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    try:
        # Test adding a project
        await project_service.add_project(test_project_name, test_project_path)

        # Verify it was added to config
        assert test_project_name in project_service.projects
        assert project_service.projects[test_project_name] == test_project_path

        # Verify it was added to the database
        project = await project_service.repository.get_by_name(test_project_name)
        assert project is not None
        assert project.name == test_project_name
        assert project.path == test_project_path

    finally:
        # Clean up
        if test_project_name in project_service.projects:
            await project_service.remove_project(test_project_name)

        # Ensure it was removed from both config and DB
        assert test_project_name not in project_service.projects
        project = await project_service.repository.get_by_name(test_project_name)
        assert project is None


@pytest.mark.asyncio
async def test_set_default_project_async(project_service: ProjectService, tmp_path):
    """Test setting a project as default with the updated async method."""
    # First add a test project
    test_project_name = f"test-default-project-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-default-project")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    original_default = project_service.default_project

    try:
        # Add the test project
        await project_service.add_project(test_project_name, test_project_path)

        # Set as default
        await project_service.set_default_project(test_project_name)

        # Verify it's set as default in config
        assert project_service.default_project == test_project_name

        # Verify it's set as default in database
        project = await project_service.repository.get_by_name(test_project_name)
        assert project is not None
        assert project.is_default is True

        # Make sure old default is no longer default
        old_default_project = await project_service.repository.get_by_name(original_default)
        if old_default_project:
            assert old_default_project.is_default is not True

    finally:
        # Restore original default
        if original_default:
            await project_service.set_default_project(original_default)

        # Clean up test project
        if test_project_name in project_service.projects:
            await project_service.remove_project(test_project_name)


@pytest.mark.asyncio
async def test_get_project_method(project_service: ProjectService, tmp_path):
    """Test the get_project method directly."""
    test_project_name = f"test-get-project-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-get-project")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    try:
        # Test getting a non-existent project
        result = await project_service.get_project("non-existent-project")
        assert result is None

        # Add a project
        await project_service.add_project(test_project_name, test_project_path)

        # Test getting an existing project
        result = await project_service.get_project(test_project_name)
        assert result is not None
        assert result.name == test_project_name
        assert result.path == test_project_path

    finally:
        # Clean up
        if test_project_name in project_service.projects:
            await project_service.remove_project(test_project_name)


@pytest.mark.asyncio
async def test_set_default_project_config_db_mismatch(
    project_service: ProjectService, config_manager: ConfigManager, tmp_path
):
    """Test set_default_project when project exists in config but not in database."""
    test_project_name = f"test-mismatch-project-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-mismatch-project")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    original_default = project_service.default_project

    try:
        # Add project to config only (not to database)
        config_manager.add_project(test_project_name, test_project_path)

        # Verify it's in config but not in database
        assert test_project_name in project_service.projects
        db_project = await project_service.repository.get_by_name(test_project_name)
        assert db_project is None

        # Try to set as default - this should trigger the error log on line 142
        await project_service.set_default_project(test_project_name)

        # Should still update config despite database mismatch
        assert project_service.default_project == test_project_name

    finally:
        # Restore original default
        if original_default:
            config_manager.set_default_project(original_default)

        # Clean up
        if test_project_name in project_service.projects:
            config_manager.remove_project(test_project_name)


@pytest.mark.asyncio
async def test_add_project_with_set_default_true(project_service: ProjectService, tmp_path):
    """Test adding a project with set_default=True enforces single default."""
    test_project_name = f"test-default-true-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-default-true")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    original_default = project_service.default_project

    try:
        # Get original default project from database
        original_default_project = await project_service.repository.get_by_name(original_default)

        # Add project with set_default=True
        await project_service.add_project(test_project_name, test_project_path, set_default=True)

        # Verify new project is set as default in both config and database
        assert project_service.default_project == test_project_name

        new_project = await project_service.repository.get_by_name(test_project_name)
        assert new_project is not None
        assert new_project.is_default is True

        # Verify original default is no longer default in database
        if original_default_project:
            refreshed_original = await project_service.repository.get_by_name(original_default)
            assert refreshed_original.is_default is not True

        # Verify only one project has is_default=True
        all_projects = await project_service.repository.find_all()
        default_projects = [p for p in all_projects if p.is_default is True]
        assert len(default_projects) == 1
        assert default_projects[0].name == test_project_name

    finally:
        # Restore original default
        if original_default:
            await project_service.set_default_project(original_default)

        # Clean up test project
        if test_project_name in project_service.projects:
            await project_service.remove_project(test_project_name)


@pytest.mark.asyncio
async def test_add_project_with_set_default_false(project_service: ProjectService, tmp_path):
    """Test adding a project with set_default=False doesn't change defaults."""
    test_project_name = f"test-default-false-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-default-false")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    original_default = project_service.default_project

    try:
        # Add project with set_default=False (explicit)
        await project_service.add_project(test_project_name, test_project_path, set_default=False)

        # Verify default project hasn't changed
        assert project_service.default_project == original_default

        # Verify new project is NOT set as default
        new_project = await project_service.repository.get_by_name(test_project_name)
        assert new_project is not None
        assert new_project.is_default is not True

        # Verify original default is still default
        original_default_project = await project_service.repository.get_by_name(original_default)
        if original_default_project:
            assert original_default_project.is_default is True

    finally:
        # Clean up test project
        if test_project_name in project_service.projects:
            await project_service.remove_project(test_project_name)


@pytest.mark.asyncio
async def test_add_project_default_parameter_omitted(project_service: ProjectService, tmp_path):
    """Test adding a project without set_default parameter defaults to False behavior."""
    test_project_name = f"test-default-omitted-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-default-omitted")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    original_default = project_service.default_project

    try:
        # Add project without set_default parameter (should default to False)
        await project_service.add_project(test_project_name, test_project_path)

        # Verify default project hasn't changed
        assert project_service.default_project == original_default

        # Verify new project is NOT set as default
        new_project = await project_service.repository.get_by_name(test_project_name)
        assert new_project is not None
        assert new_project.is_default is not True

    finally:
        # Clean up test project
        if test_project_name in project_service.projects:
            await project_service.remove_project(test_project_name)


@pytest.mark.asyncio
async def test_ensure_single_default_project_enforcement_logic(project_service: ProjectService):
    """Test that _ensure_single_default_project logic works correctly."""
    # Test that the method exists and is callable
    assert hasattr(project_service, "_ensure_single_default_project")
    assert callable(getattr(project_service, "_ensure_single_default_project"))

    # Call the enforcement method - should work without error
    await project_service._ensure_single_default_project()

    # Verify there is exactly one default project after enforcement
    all_projects = await project_service.repository.find_all()
    default_projects = [p for p in all_projects if p.is_default is True]
    assert len(default_projects) == 1  # Should have exactly one default


@pytest.mark.asyncio
async def test_synchronize_projects_calls_ensure_single_default(
    project_service: ProjectService, tmp_path
):
    """Test that synchronize_projects calls _ensure_single_default_project."""
    test_project_name = f"test-sync-default-{os.urandom(4).hex()}"
    test_project_path = str(tmp_path / "test-sync-default")

    # Make sure the test directory exists
    os.makedirs(test_project_path, exist_ok=True)

    try:
        # Add project to config only (simulating unsynchronized state)
        from basic_memory.config import config_manager

        config_manager.add_project(test_project_name, test_project_path)

        # Verify it's in config but not in database
        assert test_project_name in project_service.projects
        db_project = await project_service.repository.get_by_name(test_project_name)
        assert db_project is None

        # Call synchronize_projects (this should call _ensure_single_default_project)
        await project_service.synchronize_projects()

        # Verify project is now in database
        db_project = await project_service.repository.get_by_name(test_project_name)
        assert db_project is not None

        # Verify default project enforcement was applied
        all_projects = await project_service.repository.find_all()
        default_projects = [p for p in all_projects if p.is_default is True]
        assert len(default_projects) <= 1  # Should be exactly 1 or 0

    finally:
        # Clean up test project
        if test_project_name in project_service.projects:
            await project_service.remove_project(test_project_name)
