from typing import Any, Optional, List
from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from universal_mcp_ms_teams.api_segments.appcatalogs_api import AppcatalogsApi
from universal_mcp_ms_teams.api_segments.teams_api import TeamsApi
from universal_mcp_ms_teams.api_segments.teamstemplates_api import TeamstemplatesApi
from universal_mcp_ms_teams.api_segments.chats_api import ChatsApi
from universal_mcp_ms_teams.api_segments.me_api import MeApi
from universal_mcp_ms_teams.api_segments.communications_api import CommunicationsApi
from universal_mcp_ms_teams.api_segments.employeeexperience_api import EmployeeexperienceApi
from universal_mcp_ms_teams.api_segments.copilot_api import CopilotApi
from universal_mcp_ms_teams.api_segments.teamwork_api import TeamworkApi
from universal_mcp_ms_teams.api_segments.users_api import UsersApi

class MsTeamsApp(APIApplication):

    def __init__(self, integration: Integration=None, **kwargs) -> None:
        super().__init__(name='ms-teams', integration=integration, **kwargs)
        self.base_url = 'https://graph.microsoft.com/v1.0'
        self.appcatalogs = AppcatalogsApi(self)
        self.teams = TeamsApi(self)
        self.teamstemplates = TeamstemplatesApi(self)
        self.chats = ChatsApi(self)
        self.me = MeApi(self)
        self.communications = CommunicationsApi(self)
        self.employeeexperience = EmployeeexperienceApi(self)
        self.copilot = CopilotApi(self)
        self.teamwork = TeamworkApi(self)
        self.users = UsersApi(self)

    def list_tools(self):
        all_tools = []
        all_tools.extend(self.appcatalogs.list_tools())
        all_tools.extend(self.teams.list_tools())
        all_tools.extend(self.teamstemplates.list_tools())
        all_tools.extend(self.chats.list_tools())
        all_tools.extend(self.me.list_tools())
        all_tools.extend(self.communications.list_tools())
        all_tools.extend(self.employeeexperience.list_tools())
        all_tools.extend(self.copilot.list_tools())
        all_tools.extend(self.teamwork.list_tools())
        all_tools.extend(self.users.list_tools())
        return all_tools