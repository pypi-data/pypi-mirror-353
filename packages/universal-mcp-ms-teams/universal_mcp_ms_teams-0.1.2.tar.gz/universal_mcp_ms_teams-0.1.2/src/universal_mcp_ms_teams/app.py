from typing import Any, Optional, List
from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from universal_mcp_ms_teams.api_segments.appcatalogs_api import AppcatalogsApi
from universal_mcp_ms_teams.api_segments.chats_api import ChatsApi
from universal_mcp_ms_teams.api_segments.groups_api import GroupsApi
from universal_mcp_ms_teams.api_segments.teams_api import TeamsApi
from universal_mcp_ms_teams.api_segments.teamwork_api import TeamworkApi
from universal_mcp_ms_teams.api_segments.users_api import UsersApi

class MsTeamsApp(APIApplication):

    def __init__(self, integration: Integration=None, **kwargs) -> None:
        super().__init__(name='ms-teams', integration=integration, **kwargs)
        self.base_url = 'https://graph.microsoft.com/v1.0'
        self.appcatalogs = AppcatalogsApi(self)
        self.chats = ChatsApi(self)
        self.groups = GroupsApi(self)
        self.teams = TeamsApi(self)
        self.teamwork = TeamworkApi(self)
        self.users = UsersApi(self)

    def list_tools(self):
        all_tools = []
        all_tools.extend(self.appcatalogs.list_tools())
        all_tools.extend(self.chats.list_tools())
        all_tools.extend(self.groups.list_tools())
        all_tools.extend(self.teams.list_tools())
        all_tools.extend(self.teamwork.list_tools())
        all_tools.extend(self.users.list_tools())
        return all_tools