from abc import ABC

import pytest
import yaml

from dify_user_client import DifyClient
from dify_user_client.apps import (AdvancedChatApp, AgentApp, App, ChatApp, CompletionApp, WorkflowApp)
from dify_user_client.models import (
    AppType, AgentConversation, PaginatedAgentLogs, PaginatedWorkflowLogs,
    WorkflowLogEntry, WorkflowNodeExecution, WorkflowNodeExecutions
)


def test_app_models(client: DifyClient):
    apps = client.apps
    assert isinstance(apps, list)

    for app in apps:
        assert isinstance(app, App)


class BaseTestApp(ABC):
    mode = None
    app_class = None

    def test_create_delete_app(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        assert isinstance(app, self.app_class)
        app = client.get_app(app_id=app.id)
        assert isinstance(app, self.app_class)
        app.delete()

        with pytest.raises(ValueError, match=".*not found.*"):
            client.get_app(app_id=app.id)

    def test_export_yaml(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        try:
            yaml_content = app.export_yaml()
            parsed_yaml = yaml.safe_load(yaml_content)
            assert isinstance(parsed_yaml, dict)

        finally:
            app.delete()

    def test_create_from_yaml(self, client: DifyClient):
        agent_app = client.create_app(
            name=f"test-{self.mode}-app", mode=self.mode)
        try:

            yaml_content = agent_app.export_yaml()
            new_agent_app = client.create_app_from_yaml(yaml_content)
            assert isinstance(new_agent_app, self.app_class)
            new_agent_app = client.get_app(new_agent_app.id)
            assert isinstance(new_agent_app, self.app_class)
            new_agent_app.delete()

        finally:
            agent_app.delete()


class TestAgentApp(BaseTestApp):
    mode = AppType.AGENT_CHAT
    app_class = AgentApp

    def test_import_yaml(self, client: DifyClient):
        agent_app = client.create_app(
            name=f"test-{self.mode}-app",
            mode=self.mode)
        try:
            agent_app.import_yaml(agent_app.export_yaml())
            assert isinstance(agent_app, self.app_class)

        finally:
            agent_app.delete()

    def test_get_logs(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        try:
            logs = app.get_logs(page=1, limit=10)
            assert isinstance(logs, PaginatedAgentLogs)
            assert isinstance(logs.page, int)
            assert isinstance(logs.limit, int)
            assert isinstance(logs.total, int)
            assert isinstance(logs.has_more, bool)
            assert isinstance(logs.data, list)
            
            if logs.data:
                assert isinstance(logs.data[0], AgentConversation)
        finally:
            app.delete()

    def test_iter_logs(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        try:
            logs_count = 0
            for log in app.iter_logs(limit=10):
                assert isinstance(log, AgentConversation)
                logs_count += 1
                if logs_count >= 15:  # Test at least a few pages
                    break
        finally:
            app.delete()


class TestChatApp(BaseTestApp):
    mode = AppType.CHAT
    app_class = ChatApp

    def test_get_logs(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        try:
            logs = app.get_logs(page=1, limit=10)
            assert isinstance(logs, PaginatedAgentLogs)
            assert isinstance(logs.page, int)
            assert isinstance(logs.limit, int)
            assert isinstance(logs.total, int)
            assert isinstance(logs.has_more, bool)
            assert isinstance(logs.data, list)
            
            if logs.data:
                assert isinstance(logs.data[0], AgentConversation)
        finally:
            app.delete()

    def test_iter_logs(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        try:
            logs_count = 0
            for log in app.iter_logs(limit=10):
                assert isinstance(log, AgentConversation)
                logs_count += 1
                if logs_count >= 15:  # Test at least a few pages
                    break
        finally:
            app.delete()


class TestCompletionApp(BaseTestApp):
    mode = AppType.COMPLETION
    app_class = CompletionApp


class TestWorkflowApp(BaseTestApp):
    mode = AppType.WORKFLOW
    app_class = WorkflowApp

    def test_import_yaml(self, client: DifyClient):
        workflow_app = client.create_app(
            name=f"test-{self.mode}-app",
            mode=self.mode)
        try:
            workflow_app.import_yaml(workflow_app.export_yaml())
            assert isinstance(workflow_app, self.app_class)
        finally:
            workflow_app.delete()

    def test_get_logs(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        try:
            logs = app.get_logs(page=1, limit=10)
            assert isinstance(logs, PaginatedWorkflowLogs)
            assert isinstance(logs.page, int)
            assert isinstance(logs.limit, int)
            assert isinstance(logs.total, int)
            assert isinstance(logs.has_more, bool)
            assert isinstance(logs.data, list)
            
            if logs.data:
                assert isinstance(logs.data[0], WorkflowLogEntry)
        finally:
            app.delete()

    def test_iter_logs(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        try:
            logs_count = 0
            for log in app.iter_logs(limit=10):
                assert isinstance(log, WorkflowLogEntry)
                logs_count += 1
                if logs_count >= 15:  # Test at least a few pages
                    break
        finally:
            app.delete()

    def test_get_node_executions(self, client: DifyClient):
        app = client.create_app(name=f"test-{self.mode}-app", mode=self.mode)
        try:
            # First, we need to get a workflow run ID from logs
            logs = app.get_logs(page=1, limit=1)
            if logs.data:
                workflow_run_id = logs.data[0].workflow_run.id
                executions = app.get_node_executions(workflow_run_id)
                assert isinstance(executions, WorkflowNodeExecutions)
                assert isinstance(executions.data, list)
                
                if executions.data:
                    execution = executions.data[0]
                    assert isinstance(execution, WorkflowNodeExecution)
                    assert isinstance(execution.index, int)
                    assert isinstance(execution.node_type, str)
                    assert isinstance(execution.title, str)
                    assert isinstance(execution.status, str)
                    assert isinstance(execution.elapsed_time, float)
                    assert isinstance(execution.created_at, int)
                    assert isinstance(execution.finished_at, int)
        finally:
            app.delete()


class TestAdvancedChatApp(BaseTestApp):
    mode = AppType.ADVANCED_CHAT
    app_class = AdvancedChatApp
