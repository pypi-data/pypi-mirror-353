from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class TeamsApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def teams_list_installed_apps(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List apps in team

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_create_installed_apps(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[Any] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Add app to team

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (string): The set of resource-specific permissions consented to while installing or upgrading the teamsApp.
            teamsApp (string): The app that is installed.
            teamsAppDefinition (string): The details of this version of the app.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "consentedPermissionSet": consentedPermissionSet,
            "teamsApp": teamsApp,
            "teamsAppDefinition": teamsAppDefinition,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_get_installed_apps(
        self,
        team_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get installed app in team

        Args:
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_installed_apps(
        self,
        team_id: str,
        teamsAppInstallation_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[Any] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property installedApps in teams

        Args:
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (string): The set of resource-specific permissions consented to while installing or upgrading the teamsApp.
            teamsApp (string): The app that is installed.
            teamsAppDefinition (string): The details of this version of the app.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "consentedPermissionSet": consentedPermissionSet,
            "teamsApp": teamsApp,
            "teamsAppDefinition": teamsAppDefinition,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_delete_installed_apps(
        self, team_id: str, teamsAppInstallation_id: str
    ) -> Any:
        """

        Remove app from team

        Args:
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def upgrade_teams_app_installation(
        self,
        team_id: str,
        teamsAppInstallation_id: str,
        consentedPermissionSet: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action upgrade

        Args:
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            consentedPermissionSet (string): consentedPermissionSet

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        request_body_data = None
        request_body_data = {"consentedPermissionSet": consentedPermissionSet}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps/{teamsAppInstallation_id}/upgrade"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_teams_app_details(
        self,
        team_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from teams

        Args:
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps/{teamsAppInstallation_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_teams_app_definition(
        self,
        team_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsAppDefinition from teams

        Args:
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps/{teamsAppInstallation_id}/teamsAppDefinition"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_installed_apps(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAppInstallation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_team_list_team(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List teams

        Args:
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team
        """
        url = f"{self.main_app_client.base_url}/teams"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_team_create_team(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        classification: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        firstChannelName: Optional[str] = None,
        funSettings: Optional[Any] = None,
        guestSettings: Optional[Any] = None,
        internalId: Optional[str] = None,
        isArchived: Optional[bool] = None,
        memberSettings: Optional[Any] = None,
        messagingSettings: Optional[Any] = None,
        specialization: Optional[Any] = None,
        summary: Optional[Any] = None,
        tenantId: Optional[str] = None,
        visibility: Optional[Any] = None,
        webUrl: Optional[str] = None,
        allChannels: Optional[List[Any]] = None,
        channels: Optional[List[Any]] = None,
        group: Optional[Any] = None,
        incomingChannels: Optional[List[Any]] = None,
        installedApps: Optional[List[Any]] = None,
        members: Optional[List[Any]] = None,
        operations: Optional[List[Any]] = None,
        permissionGrants: Optional[List[Any]] = None,
        photo: Optional[Any] = None,
        primaryChannel: Optional[Any] = None,
        schedule: Optional[Any] = None,
        tags: Optional[List[Any]] = None,
        template: Optional[Any] = None,
    ) -> Any:
        """

        Create team

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            classification (string): An optional label. Typically describes the data or business sensitivity of the team. Must match one of a preconfigured set in the tenant's directory.
            createdDateTime (string): Timestamp at which the team was created.
            description (string): An optional description for the team. Maximum length: 1,024 characters.
            displayName (string): The name of the team.
            firstChannelName (string): The name of the first channel in the team. This is an optional property, only used during team creation and isn't returned in methods to get and list teams.
            funSettings (string): Settings to configure use of Giphy, memes, and stickers in the team.
            guestSettings (string): Settings to configure whether guests can create, update, or delete channels in the team.
            internalId (string): A unique ID for the team that was used in a few places such as the audit log/Office 365 Management Activity API.
            isArchived (boolean): Whether this team is in read-only mode.
            memberSettings (string): Settings to configure whether members can perform certain actions, for example, create channels and add bots, in the team.
            messagingSettings (string): Settings to configure messaging and mentions in the team.
            specialization (string): Optional. Indicates whether the team is intended for a particular use case. Each team specialization has access to unique behaviors and experiences targeted to its use case.
            summary (string): Contains summary information about the team, including number of owners, members, and guests.
            tenantId (string): The ID of the Microsoft Entra tenant.
            visibility (string): The visibility of the group and team. Defaults to Public.
            webUrl (string): A hyperlink that goes to the team in the Microsoft Teams client. You get this URL when you right-click a team in the Microsoft Teams client and select Get link to team. This URL should be treated as an opaque blob, and not parsed.
            allChannels (array): List of channels either hosted in or shared with the team (incoming channels).
            channels (array): The collection of channels and messages associated with the team.
            group (string): group
            incomingChannels (array): List of channels shared with the team.
            installedApps (array): The apps installed in this team.
            members (array): Members and owners of the team.
            operations (array): The async operations that ran or are running on this team.
            permissionGrants (array): A collection of permissions granted to apps to access the team.
            photo (string): The profile photo for the team.
            primaryChannel (string): The general channel for the team.
            schedule (string): The schedule of shifts for this team.
            tags (array): The tags associated with the team.
            template (string): The template this team was created from. See available templates.

        Returns:
            Any: Created entity

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "classification": classification,
            "createdDateTime": createdDateTime,
            "description": description,
            "displayName": displayName,
            "firstChannelName": firstChannelName,
            "funSettings": funSettings,
            "guestSettings": guestSettings,
            "internalId": internalId,
            "isArchived": isArchived,
            "memberSettings": memberSettings,
            "messagingSettings": messagingSettings,
            "specialization": specialization,
            "summary": summary,
            "tenantId": tenantId,
            "visibility": visibility,
            "webUrl": webUrl,
            "allChannels": allChannels,
            "channels": channels,
            "group": group,
            "incomingChannels": incomingChannels,
            "installedApps": installedApps,
            "members": members,
            "operations": operations,
            "permissionGrants": permissionGrants,
            "photo": photo,
            "primaryChannel": primaryChannel,
            "schedule": schedule,
            "tags": tags,
            "template": template,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_team_get_team(
        self,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team

        Args:
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved entity

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team, important
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_team_update_team(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        classification: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        firstChannelName: Optional[str] = None,
        funSettings: Optional[Any] = None,
        guestSettings: Optional[Any] = None,
        internalId: Optional[str] = None,
        isArchived: Optional[bool] = None,
        memberSettings: Optional[Any] = None,
        messagingSettings: Optional[Any] = None,
        specialization: Optional[Any] = None,
        summary: Optional[Any] = None,
        tenantId: Optional[str] = None,
        visibility: Optional[Any] = None,
        webUrl: Optional[str] = None,
        allChannels: Optional[List[Any]] = None,
        channels: Optional[List[Any]] = None,
        group: Optional[Any] = None,
        incomingChannels: Optional[List[Any]] = None,
        installedApps: Optional[List[Any]] = None,
        members: Optional[List[Any]] = None,
        operations: Optional[List[Any]] = None,
        permissionGrants: Optional[List[Any]] = None,
        photo: Optional[Any] = None,
        primaryChannel: Optional[Any] = None,
        schedule: Optional[Any] = None,
        tags: Optional[List[Any]] = None,
        template: Optional[Any] = None,
    ) -> Any:
        """

        Update team

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            classification (string): An optional label. Typically describes the data or business sensitivity of the team. Must match one of a preconfigured set in the tenant's directory.
            createdDateTime (string): Timestamp at which the team was created.
            description (string): An optional description for the team. Maximum length: 1,024 characters.
            displayName (string): The name of the team.
            firstChannelName (string): The name of the first channel in the team. This is an optional property, only used during team creation and isn't returned in methods to get and list teams.
            funSettings (string): Settings to configure use of Giphy, memes, and stickers in the team.
            guestSettings (string): Settings to configure whether guests can create, update, or delete channels in the team.
            internalId (string): A unique ID for the team that was used in a few places such as the audit log/Office 365 Management Activity API.
            isArchived (boolean): Whether this team is in read-only mode.
            memberSettings (string): Settings to configure whether members can perform certain actions, for example, create channels and add bots, in the team.
            messagingSettings (string): Settings to configure messaging and mentions in the team.
            specialization (string): Optional. Indicates whether the team is intended for a particular use case. Each team specialization has access to unique behaviors and experiences targeted to its use case.
            summary (string): Contains summary information about the team, including number of owners, members, and guests.
            tenantId (string): The ID of the Microsoft Entra tenant.
            visibility (string): The visibility of the group and team. Defaults to Public.
            webUrl (string): A hyperlink that goes to the team in the Microsoft Teams client. You get this URL when you right-click a team in the Microsoft Teams client and select Get link to team. This URL should be treated as an opaque blob, and not parsed.
            allChannels (array): List of channels either hosted in or shared with the team (incoming channels).
            channels (array): The collection of channels and messages associated with the team.
            group (string): group
            incomingChannels (array): List of channels shared with the team.
            installedApps (array): The apps installed in this team.
            members (array): Members and owners of the team.
            operations (array): The async operations that ran or are running on this team.
            permissionGrants (array): A collection of permissions granted to apps to access the team.
            photo (string): The profile photo for the team.
            primaryChannel (string): The general channel for the team.
            schedule (string): The schedule of shifts for this team.
            tags (array): The tags associated with the team.
            template (string): The template this team was created from. See available templates.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "classification": classification,
            "createdDateTime": createdDateTime,
            "description": description,
            "displayName": displayName,
            "firstChannelName": firstChannelName,
            "funSettings": funSettings,
            "guestSettings": guestSettings,
            "internalId": internalId,
            "isArchived": isArchived,
            "memberSettings": memberSettings,
            "messagingSettings": messagingSettings,
            "specialization": specialization,
            "summary": summary,
            "tenantId": tenantId,
            "visibility": visibility,
            "webUrl": webUrl,
            "allChannels": allChannels,
            "channels": channels,
            "group": group,
            "incomingChannels": incomingChannels,
            "installedApps": installedApps,
            "members": members,
            "operations": operations,
            "permissionGrants": permissionGrants,
            "photo": photo,
            "primaryChannel": primaryChannel,
            "schedule": schedule,
            "tags": tags,
            "template": template,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_team_delete_team(self, team_id: str) -> Any:
        """

        Delete entity from teams

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_list_all_channels(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List allChannels

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/allChannels"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_get_all_channels(
        self,
        team_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allChannels from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/allChannels/{channel_id}"
        )
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_team_channels(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/allChannels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_list_channels(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List channels

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_create_channels(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        email: Optional[str] = None,
        isArchived: Optional[bool] = None,
        isFavoriteByDefault: Optional[bool] = None,
        membershipType: Optional[Any] = None,
        summary: Optional[Any] = None,
        tenantId: Optional[str] = None,
        webUrl: Optional[str] = None,
        allMembers: Optional[List[Any]] = None,
        filesFolder: Optional[Any] = None,
        members: Optional[List[Any]] = None,
        messages: Optional[List[Any]] = None,
        sharedWithTeams: Optional[List[Any]] = None,
        tabs: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create channel

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdDateTime (string): Read only. Timestamp at which the channel was created.
            description (string): Optional textual description for the channel.
            displayName (string): Channel name as it will appear to the user in Microsoft Teams. The maximum length is 50 characters.
            email (string): The email address for sending messages to the channel. Read-only.
            isArchived (boolean): Indicates whether the channel is archived. Read-only.
            isFavoriteByDefault (boolean): Indicates whether the channel should be marked as recommended for all members of the team to show in their channel list. Note: All recommended channels automatically show in the channels list for education and frontline worker users. The property can only be set programmatically via the Create team method. The default value is false.
            membershipType (string): The type of the channel. Can be set during creation and can't be changed. The possible values are: standard, private, unknownFutureValue, shared. The default value is standard. Use the Prefer: include-unknown-enum-members request header to get the following value in this evolvable enum: shared.
            summary (string): Contains summary information about the channel, including number of owners, members, guests, and an indicator for members from other tenants. The summary property will only be returned if it is specified in the $select clause of the Get channel method.
            tenantId (string): The ID of the Microsoft Entra tenant.
            webUrl (string): A hyperlink that will go to the channel in Microsoft Teams. This is the URL that you get when you right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an opaque blob, and not parsed. Read-only.
            allMembers (array): A collection of membership records associated with the channel, including both direct and indirect members of shared channels.
            filesFolder (string): Metadata for the location where the channel's files are stored.
            members (array): A collection of membership records associated with the channel.
            messages (array): A collection of all the messages in the channel. A navigation property. Nullable.
            sharedWithTeams (array): A collection of teams with which a channel is shared.
            tabs (array): A collection of all the tabs in the channel. A navigation property.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdDateTime": createdDateTime,
            "description": description,
            "displayName": displayName,
            "email": email,
            "isArchived": isArchived,
            "isFavoriteByDefault": isFavoriteByDefault,
            "membershipType": membershipType,
            "summary": summary,
            "tenantId": tenantId,
            "webUrl": webUrl,
            "allMembers": allMembers,
            "filesFolder": filesFolder,
            "members": members,
            "messages": messages,
            "sharedWithTeams": sharedWithTeams,
            "tabs": tabs,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_get_channels(
        self,
        team_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_channels(
        self,
        team_id: str,
        channel_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        email: Optional[str] = None,
        isArchived: Optional[bool] = None,
        isFavoriteByDefault: Optional[bool] = None,
        membershipType: Optional[Any] = None,
        summary: Optional[Any] = None,
        tenantId: Optional[str] = None,
        webUrl: Optional[str] = None,
        allMembers: Optional[List[Any]] = None,
        filesFolder: Optional[Any] = None,
        members: Optional[List[Any]] = None,
        messages: Optional[List[Any]] = None,
        sharedWithTeams: Optional[List[Any]] = None,
        tabs: Optional[List[Any]] = None,
    ) -> Any:
        """

        Patch channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdDateTime (string): Read only. Timestamp at which the channel was created.
            description (string): Optional textual description for the channel.
            displayName (string): Channel name as it will appear to the user in Microsoft Teams. The maximum length is 50 characters.
            email (string): The email address for sending messages to the channel. Read-only.
            isArchived (boolean): Indicates whether the channel is archived. Read-only.
            isFavoriteByDefault (boolean): Indicates whether the channel should be marked as recommended for all members of the team to show in their channel list. Note: All recommended channels automatically show in the channels list for education and frontline worker users. The property can only be set programmatically via the Create team method. The default value is false.
            membershipType (string): The type of the channel. Can be set during creation and can't be changed. The possible values are: standard, private, unknownFutureValue, shared. The default value is standard. Use the Prefer: include-unknown-enum-members request header to get the following value in this evolvable enum: shared.
            summary (string): Contains summary information about the channel, including number of owners, members, guests, and an indicator for members from other tenants. The summary property will only be returned if it is specified in the $select clause of the Get channel method.
            tenantId (string): The ID of the Microsoft Entra tenant.
            webUrl (string): A hyperlink that will go to the channel in Microsoft Teams. This is the URL that you get when you right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an opaque blob, and not parsed. Read-only.
            allMembers (array): A collection of membership records associated with the channel, including both direct and indirect members of shared channels.
            filesFolder (string): Metadata for the location where the channel's files are stored.
            members (array): A collection of membership records associated with the channel.
            messages (array): A collection of all the messages in the channel. A navigation property. Nullable.
            sharedWithTeams (array): A collection of teams with which a channel is shared.
            tabs (array): A collection of all the tabs in the channel. A navigation property.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdDateTime": createdDateTime,
            "description": description,
            "displayName": displayName,
            "email": email,
            "isArchived": isArchived,
            "isFavoriteByDefault": isFavoriteByDefault,
            "membershipType": membershipType,
            "summary": summary,
            "tenantId": tenantId,
            "webUrl": webUrl,
            "allMembers": allMembers,
            "filesFolder": filesFolder,
            "members": members,
            "messages": messages,
            "sharedWithTeams": sharedWithTeams,
            "tabs": tabs,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_delete_channels(self, team_id: str, channel_id: str) -> Any:
        """

        Delete channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_list_all_members(
        self,
        team_id: str,
        channel_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List allMembers

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_members(
        self,
        team_id: str,
        channel_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to allMembers for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_channels_get_all_members(
        self,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allMembers from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_member_details(
        self,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property allMembers in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_conversation_member(
        self, team_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property allMembers for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_team_channel_members(
        self,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_channel_member(
        self, team_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers/add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_channel_member(
        self, team_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers/remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_channels_get_files_folder(
        self,
        team_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get filesFolder

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/filesFolder"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_files_folder_content(
        self, team_id: str, channel_id: str, format: Optional[str] = None
    ) -> Any:
        """

        Get content for the navigation property filesFolder from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            format (string): Format of the content

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/filesFolder/content"
        query_params = {k: v for k, v in [("$format", format)] if v is not None}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_files_folder_content(
        self, team_id: str, channel_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property filesFolder in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/filesFolder/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_files_folder_content(self, team_id: str, channel_id: str) -> Any:
        """

        Delete content for the navigation property filesFolder in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/filesFolder/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_list_members(
        self,
        team_id: str,
        channel_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List members of a channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_create_members(
        self,
        team_id: str,
        channel_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Add conversationMember

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_channels_get_members(
        self,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get member of channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_update_members(
        self,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update conversationMember

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_channels_delete_members(
        self, team_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Remove member from channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_members_count(
        self,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_channel_members_bulk(
        self, team_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members/add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_member_from_channel(
        self, team_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members/remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_channels_list_messages(
        self,
        team_id: str,
        channel_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List channel messages

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_create_messages(
        self,
        team_id: str,
        channel_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, Any]]] = None,
        body: Optional[dict[str, Any]] = None,
        channelIdentity: Optional[Any] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, Any]]] = None,
        messageHistory: Optional[List[dict[str, Any]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[Any] = None,
        reactions: Optional[List[dict[str, Any]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Send chatMessage in channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (string): If the message was sent in a channel, represents identity of the channel.
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (string): Read-only. If present, represents details of an event that happened in a chat, a channel, or a team, for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
            from_ (string): Details of the sender of the chat message. Can only be set during migration.
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (string): Defines the properties of a policy violation set by a data loss prevention (DLP) application.
            reactions (array): Reactions for this chat message (for example, Like).
            replyToId (string): Read-only. ID of the parent chat message or root chat message of the thread. (Only applies to chat messages in channels, not chats.)
            subject (string): The subject of the chat message, in plaintext.
            summary (string): Summary text of the chat message that could be used for push notifications and summary views or fall back views. Only applies to channel chat messages, not chat messages in a chat.
            webUrl (string): Read-only. Link to the message in Microsoft Teams.
            hostedContents (array): Content in a message hosted by Microsoft Teams - for example, images or code snippets.
            replies (array): Replies for a specified message. Supports $expand for channel messages.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attachments": attachments,
            "body": body,
            "channelIdentity": channelIdentity,
            "chatId": chatId,
            "createdDateTime": createdDateTime,
            "deletedDateTime": deletedDateTime,
            "etag": etag,
            "eventDetail": eventDetail,
            "from": from_,
            "importance": importance,
            "lastEditedDateTime": lastEditedDateTime,
            "lastModifiedDateTime": lastModifiedDateTime,
            "locale": locale,
            "mentions": mentions,
            "messageHistory": messageHistory,
            "messageType": messageType,
            "policyViolation": policyViolation,
            "reactions": reactions,
            "replyToId": replyToId,
            "subject": subject,
            "summary": summary,
            "webUrl": webUrl,
            "hostedContents": hostedContents,
            "replies": replies,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_channels_get_messages(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get chatMessage in a channel or chat

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_update_messages(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, Any]]] = None,
        body: Optional[dict[str, Any]] = None,
        channelIdentity: Optional[Any] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, Any]]] = None,
        messageHistory: Optional[List[dict[str, Any]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[Any] = None,
        reactions: Optional[List[dict[str, Any]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update chatMessage

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (string): If the message was sent in a channel, represents identity of the channel.
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (string): Read-only. If present, represents details of an event that happened in a chat, a channel, or a team, for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
            from_ (string): Details of the sender of the chat message. Can only be set during migration.
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (string): Defines the properties of a policy violation set by a data loss prevention (DLP) application.
            reactions (array): Reactions for this chat message (for example, Like).
            replyToId (string): Read-only. ID of the parent chat message or root chat message of the thread. (Only applies to chat messages in channels, not chats.)
            subject (string): The subject of the chat message, in plaintext.
            summary (string): Summary text of the chat message that could be used for push notifications and summary views or fall back views. Only applies to channel chat messages, not chat messages in a chat.
            webUrl (string): Read-only. Link to the message in Microsoft Teams.
            hostedContents (array): Content in a message hosted by Microsoft Teams - for example, images or code snippets.
            replies (array): Replies for a specified message. Supports $expand for channel messages.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attachments": attachments,
            "body": body,
            "channelIdentity": channelIdentity,
            "chatId": chatId,
            "createdDateTime": createdDateTime,
            "deletedDateTime": deletedDateTime,
            "etag": etag,
            "eventDetail": eventDetail,
            "from": from_,
            "importance": importance,
            "lastEditedDateTime": lastEditedDateTime,
            "lastModifiedDateTime": lastModifiedDateTime,
            "locale": locale,
            "mentions": mentions,
            "messageHistory": messageHistory,
            "messageType": messageType,
            "policyViolation": policyViolation,
            "reactions": reactions,
            "replyToId": replyToId,
            "subject": subject,
            "summary": summary,
            "webUrl": webUrl,
            "hostedContents": hostedContents,
            "replies": replies,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_channels_delete_messages(
        self, team_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Delete navigation property messages for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_channel_msg_hosted_content(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List hostedContents

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_hosted_content(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_hosted_content_details(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_hosted_content_details(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def del_ch_msg_hosted_content(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_channel_msg_hosted_content_val(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        List hostedContents

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_hosted_content_val(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_hosted_content_by_message_id(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_content_count(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_to_message(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_message(
        self, team_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_soft_delete_message(
        self, team_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_to_message(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_channel_message_replies(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List replies

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_channel_message_reply(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, Any]]] = None,
        body: Optional[dict[str, Any]] = None,
        channelIdentity: Optional[Any] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, Any]]] = None,
        messageHistory: Optional[List[dict[str, Any]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[Any] = None,
        reactions: Optional[List[dict[str, Any]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Send replies to a message in a channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (string): If the message was sent in a channel, represents identity of the channel.
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (string): Read-only. If present, represents details of an event that happened in a chat, a channel, or a team, for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
            from_ (string): Details of the sender of the chat message. Can only be set during migration.
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (string): Defines the properties of a policy violation set by a data loss prevention (DLP) application.
            reactions (array): Reactions for this chat message (for example, Like).
            replyToId (string): Read-only. ID of the parent chat message or root chat message of the thread. (Only applies to chat messages in channels, not chats.)
            subject (string): The subject of the chat message, in plaintext.
            summary (string): Summary text of the chat message that could be used for push notifications and summary views or fall back views. Only applies to channel chat messages, not chat messages in a chat.
            webUrl (string): Read-only. Link to the message in Microsoft Teams.
            hostedContents (array): Content in a message hosted by Microsoft Teams - for example, images or code snippets.
            replies (array): Replies for a specified message. Supports $expand for channel messages.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attachments": attachments,
            "body": body,
            "channelIdentity": channelIdentity,
            "chatId": chatId,
            "createdDateTime": createdDateTime,
            "deletedDateTime": deletedDateTime,
            "etag": etag,
            "eventDetail": eventDetail,
            "from": from_,
            "importance": importance,
            "lastEditedDateTime": lastEditedDateTime,
            "lastModifiedDateTime": lastModifiedDateTime,
            "locale": locale,
            "mentions": mentions,
            "messageHistory": messageHistory,
            "messageType": messageType,
            "policyViolation": policyViolation,
            "reactions": reactions,
            "replyToId": replyToId,
            "subject": subject,
            "summary": summary,
            "webUrl": webUrl,
            "hostedContents": hostedContents,
            "replies": replies,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_replies_by_message_id(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get chatMessage in a channel or chat

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_reply_message(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        atodata_type: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, Any]]] = None,
        body: Optional[dict[str, Any]] = None,
        channelIdentity: Optional[Any] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, Any]]] = None,
        messageHistory: Optional[List[dict[str, Any]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[Any] = None,
        reactions: Optional[List[dict[str, Any]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property replies in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (string): If the message was sent in a channel, represents identity of the channel.
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (string): Read-only. If present, represents details of an event that happened in a chat, a channel, or a team, for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
            from_ (string): Details of the sender of the chat message. Can only be set during migration.
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (string): Defines the properties of a policy violation set by a data loss prevention (DLP) application.
            reactions (array): Reactions for this chat message (for example, Like).
            replyToId (string): Read-only. ID of the parent chat message or root chat message of the thread. (Only applies to chat messages in channels, not chats.)
            subject (string): The subject of the chat message, in plaintext.
            summary (string): Summary text of the chat message that could be used for push notifications and summary views or fall back views. Only applies to channel chat messages, not chat messages in a chat.
            webUrl (string): Read-only. Link to the message in Microsoft Teams.
            hostedContents (array): Content in a message hosted by Microsoft Teams - for example, images or code snippets.
            replies (array): Replies for a specified message. Supports $expand for channel messages.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attachments": attachments,
            "body": body,
            "channelIdentity": channelIdentity,
            "chatId": chatId,
            "createdDateTime": createdDateTime,
            "deletedDateTime": deletedDateTime,
            "etag": etag,
            "eventDetail": eventDetail,
            "from": from_,
            "importance": importance,
            "lastEditedDateTime": lastEditedDateTime,
            "lastModifiedDateTime": lastModifiedDateTime,
            "locale": locale,
            "mentions": mentions,
            "messageHistory": messageHistory,
            "messageType": messageType,
            "policyViolation": policyViolation,
            "reactions": reactions,
            "replyToId": replyToId,
            "subject": subject,
            "summary": summary,
            "webUrl": webUrl,
            "hostedContents": hostedContents,
            "replies": replies,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_message_reply(
        self, team_id: str, channel_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Delete navigation property replies for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_content_replies(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List hostedContents

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_hosted_content_reply(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_channel_reply_hosted_content(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_ch_reply_hosted_content(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def del_ch_msg_reply_hosted_content(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_ch_msg_reply_hosted_content_val(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        List hostedContents

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_msg_reply_hosted_content(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_hosted_content_value(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_ch_msg_reply_host_contents(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_to_reply(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_reply(
        self, team_id: str, channel_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_soft_delete_reply(
        self, team_id: str, channel_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def count_replies(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_chat_message_replies_delta(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        select: Optional[List[str]] = None,
        orderby: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Invoke function delta

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            select (array): Select properties to be returned
            orderby (array): Order items by property values
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/delta()"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$select", select),
                ("$orderby", orderby),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_channel_messages(
        self,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_messages_delta(
        self,
        team_id: str,
        channel_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        select: Optional[List[str]] = None,
        orderby: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Invoke function delta

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            select (array): Select properties to be returned
            orderby (array): Order items by property values
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/delta()"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$select", select),
                ("$orderby", orderby),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def archive_team_channel(
        self,
        team_id: str,
        channel_id: str,
        shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None,
    ) -> Any:
        """

        Invoke action archive

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_team_channel_migration(self, team_id: str, channel_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def check_user_channel_access(
        self, team_id: str, channel_id: str
    ) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def provision_team_email(self, team_id: str, channel_id: str) -> Any:
        """

        Invoke action provisionEmail

        Args:
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_channel_email(self, team_id: str, channel_id: str) -> Any:
        """

        Invoke action removeEmail

        Args:
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_channel(self, team_id: str, channel_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_channel_shared_teams(
        self,
        team_id: str,
        channel_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List sharedWithChannelTeamInfo

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def share_channel_with_team(
        self,
        team_id: str,
        channel_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to sharedWithTeams for teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The name of the team.
            tenantId (string): The ID of the Microsoft Entra tenant.
            team (string): team
            isHostTeam (boolean): Indicates whether the team is the host of the channel.
            allowedMembers (array): A collection of team members who have access to the shared channel.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "tenantId": tenantId,
            "team": team,
            "isHostTeam": isHostTeam,
            "allowedMembers": allowedMembers,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_teams_channels_info(
        self,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get sharedWithChannelTeamInfo

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_shared_with_team_info(
        self,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property sharedWithTeams in teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The name of the team.
            tenantId (string): The ID of the Microsoft Entra tenant.
            team (string): team
            isHostTeam (boolean): Indicates whether the team is the host of the channel.
            allowedMembers (array): A collection of team members who have access to the shared channel.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "tenantId": tenantId,
            "team": team,
            "isHostTeam": isHostTeam,
            "allowedMembers": allowedMembers,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_shared_team_channel(
        self, team_id: str, channel_id: str, sharedWithChannelTeamInfo_id: str
    ) -> Any:
        """

        Delete sharedWithChannelTeamInfo

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_shared_channel_members(
        self,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List allowedMembers

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_team_members(
        self,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allowedMembers from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_allowed_members(
        self,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_channel_team_info(
        self,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_teams_count(
        self,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/sharedWithTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_list_tabs(
        self,
        team_id: str,
        channel_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List tabs in channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/tabs"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_create_tabs(
        self,
        team_id: str,
        channel_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        configuration: Optional[Any] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Add tab to channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            configuration (string): Container for custom settings applied to a tab. The tab is considered configured only once this property is set.
            displayName (string): Name of the tab.
            webUrl (string): Deep link URL of the tab instance. Read only.
            teamsApp (string): The application that is linked to the tab. This can't be changed after tab creation.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "configuration": configuration,
            "displayName": displayName,
            "webUrl": webUrl,
            "teamsApp": teamsApp,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_channels_get_tabs(
        self,
        team_id: str,
        channel_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tab

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_update_tabs(
        self,
        team_id: str,
        channel_id: str,
        teamsTab_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        configuration: Optional[Any] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update tab

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            configuration (string): Container for custom settings applied to a tab. The tab is considered configured only once this property is set.
            displayName (string): Name of the tab.
            webUrl (string): Deep link URL of the tab instance. Read only.
            teamsApp (string): The application that is linked to the tab. This can't be changed after tab creation.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "configuration": configuration,
            "displayName": displayName,
            "webUrl": webUrl,
            "teamsApp": teamsApp,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_channels_delete_tabs(
        self, team_id: str, channel_id: str, teamsTab_id: str
    ) -> Any:
        """

        Delete tab from channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_teams_app_tab(
        self,
        team_id: str,
        channel_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_tabs_count(
        self,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_get_count_a(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_messages(
        self,
        team_id: str,
        model: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        select: Optional[List[str]] = None,
        orderby: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Invoke function getAllMessages

        Args:
            team_id (string): team-id
            model (string): The payment model for the API
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            select (array): Select properties to be returned
            orderby (array): Order items by property values
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/channels/getAllMessages()"
        )
        query_params = {
            k: v
            for k, v in [
                ("model", model),
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$select", select),
                ("$orderby", orderby),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_retained_messages_by_team_id(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        select: Optional[List[str]] = None,
        orderby: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Invoke function getAllRetainedMessages

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            select (array): Select properties to be returned
            orderby (array): Order items by property values
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/getAllRetainedMessages()"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$select", select),
                ("$orderby", orderby),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_get_group(
        self,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get group from teams

        Args:
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.group
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/group"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_service_provisioning_errors(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get serviceProvisioningErrors property value

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.group
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/group/serviceProvisioningErrors"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_service_provisioning_errors(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.group
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/group/serviceProvisioningErrors/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_list_incoming_channels(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List incomingChannels

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/incomingChannels"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_get_incoming_channels(
        self,
        team_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get incomingChannels from teams

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/incomingChannels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_team_incoming_channels(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/incomingChannels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_list_members(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List members of team

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.conversationMember
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_create_members(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Add member to team

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.conversationMember
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_get_members(
        self,
        team_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get member of team

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.conversationMember
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_members(
        self,
        team_id: str,
        conversationMember_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update member in team

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.conversationMember
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_delete_members(self, team_id: str, conversationMember_id: str) -> Any:
        """

        Remove member from team

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.conversationMember
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_members_get_count_b(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.conversationMember
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_team_members_add(
        self, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.conversationMember
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members/add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_team_members_remove(
        self, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.conversationMember
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members/remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_team_archive(
        self, team_id: str, shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None
    ) -> Any:
        """

        Invoke action archive

        Args:
            team_id (string): team-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team.Actions
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_team_clone(
        self,
        team_id: str,
        displayName: Optional[str] = None,
        description: Optional[str] = None,
        mailNickname: Optional[str] = None,
        classification: Optional[str] = None,
        visibility: Optional[str] = None,
        partsToClone: Optional[str] = None,
    ) -> Any:
        """

        Invoke action clone

        Args:
            team_id (string): team-id
            displayName (string): displayName
            description (string): description
            mailNickname (string): mailNickname
            classification (string): classification
            visibility (string): visibility
            partsToClone (string): partsToClone

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team.Actions
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "displayName": displayName,
            "description": description,
            "mailNickname": mailNickname,
            "classification": classification,
            "visibility": visibility,
            "partsToClone": partsToClone,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/clone"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_team_complete_migration(self, team_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team.Actions
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def send_team_notification(
        self,
        team_id: str,
        topic: Optional[Any] = None,
        activityType: Optional[str] = None,
        chainId: Optional[float] = None,
        previewText: Optional[Any] = None,
        teamsAppId: Optional[str] = None,
        templateParameters: Optional[List[dict[str, Any]]] = None,
        recipient: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action sendActivityNotification

        Args:
            team_id (string): team-id
            topic (string): topic
            activityType (string): activityType
            chainId (number): chainId
            previewText (string): previewText
            teamsAppId (string): teamsAppId
            templateParameters (array): templateParameters
            recipient (string): recipient

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team.Actions
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "topic": topic,
            "activityType": activityType,
            "chainId": chainId,
            "previewText": previewText,
            "teamsAppId": teamsAppId,
            "templateParameters": templateParameters,
            "recipient": recipient,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/sendActivityNotification"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_team_unarchive(self, team_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team.Actions
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_list_operations(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get operations from teams

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAsyncOperation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/operations"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_create_operations(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attemptsCount: Optional[float] = None,
        createdDateTime: Optional[str] = None,
        error: Optional[Any] = None,
        lastActionDateTime: Optional[str] = None,
        operationType: Optional[str] = None,
        status: Optional[str] = None,
        targetResourceId: Optional[str] = None,
        targetResourceLocation: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to operations for teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attemptsCount (number): Number of times the operation was attempted before being marked successful or failed.
            createdDateTime (string): Time when the operation was created.
            error (string): Any error that causes the async operation to fail.
            lastActionDateTime (string): Time when the async operation was last updated.
            operationType (string): operationType
            status (string): status
            targetResourceId (string): The ID of the object that's created or modified as result of this async operation, typically a team.
            targetResourceLocation (string): The location of the object that's created or modified as result of this async operation. This URL should be treated as an opaque value and not parsed into its component paths.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAsyncOperation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attemptsCount": attemptsCount,
            "createdDateTime": createdDateTime,
            "error": error,
            "lastActionDateTime": lastActionDateTime,
            "operationType": operationType,
            "status": status,
            "targetResourceId": targetResourceId,
            "targetResourceLocation": targetResourceLocation,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/operations"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_get_operations(
        self,
        team_id: str,
        teamsAsyncOperation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get operations from teams

        Args:
            team_id (string): team-id
            teamsAsyncOperation_id (string): teamsAsyncOperation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAsyncOperation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAsyncOperation_id is None:
            raise ValueError("Missing required parameter 'teamsAsyncOperation-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/operations/{teamsAsyncOperation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_operations(
        self,
        team_id: str,
        teamsAsyncOperation_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attemptsCount: Optional[float] = None,
        createdDateTime: Optional[str] = None,
        error: Optional[Any] = None,
        lastActionDateTime: Optional[str] = None,
        operationType: Optional[str] = None,
        status: Optional[str] = None,
        targetResourceId: Optional[str] = None,
        targetResourceLocation: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property operations in teams

        Args:
            team_id (string): team-id
            teamsAsyncOperation_id (string): teamsAsyncOperation-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attemptsCount (number): Number of times the operation was attempted before being marked successful or failed.
            createdDateTime (string): Time when the operation was created.
            error (string): Any error that causes the async operation to fail.
            lastActionDateTime (string): Time when the async operation was last updated.
            operationType (string): operationType
            status (string): status
            targetResourceId (string): The ID of the object that's created or modified as result of this async operation, typically a team.
            targetResourceLocation (string): The location of the object that's created or modified as result of this async operation. This URL should be treated as an opaque value and not parsed into its component paths.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAsyncOperation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAsyncOperation_id is None:
            raise ValueError("Missing required parameter 'teamsAsyncOperation-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attemptsCount": attemptsCount,
            "createdDateTime": createdDateTime,
            "error": error,
            "lastActionDateTime": lastActionDateTime,
            "operationType": operationType,
            "status": status,
            "targetResourceId": targetResourceId,
            "targetResourceLocation": targetResourceLocation,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/operations/{teamsAsyncOperation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_delete_operations(self, team_id: str, teamsAsyncOperation_id: str) -> Any:
        """

        Delete navigation property operations for teams

        Args:
            team_id (string): team-id
            teamsAsyncOperation_id (string): teamsAsyncOperation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAsyncOperation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAsyncOperation_id is None:
            raise ValueError("Missing required parameter 'teamsAsyncOperation-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/operations/{teamsAsyncOperation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_operations_get_count_af(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsAsyncOperation
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/operations/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_list_permission_grants(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List permissionGrants of a team

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.resourceSpecificPermissionGrant
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/permissionGrants"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_create_permission_grants(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        clientAppId: Optional[str] = None,
        clientId: Optional[str] = None,
        permission: Optional[str] = None,
        permissionType: Optional[str] = None,
        resourceAppId: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to permissionGrants for teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            deletedDateTime (string): Date and time when this object was deleted. Always null when the object hasn't been deleted.
            clientAppId (string): ID of the service principal of the Microsoft Entra app that has been granted access. Read-only.
            clientId (string): ID of the Microsoft Entra app that has been granted access. Read-only.
            permission (string): The name of the resource-specific permission. Read-only.
            permissionType (string): The type of permission. Possible values are: Application, Delegated. Read-only.
            resourceAppId (string): ID of the Microsoft Entra app that is hosting the resource. Read-only.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.resourceSpecificPermissionGrant
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "deletedDateTime": deletedDateTime,
            "clientAppId": clientAppId,
            "clientId": clientId,
            "permission": permission,
            "permissionType": permissionType,
            "resourceAppId": resourceAppId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/permissionGrants"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_get_permission_grants(
        self,
        team_id: str,
        resourceSpecificPermissionGrant_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get permissionGrants from teams

        Args:
            team_id (string): team-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.resourceSpecificPermissionGrant
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_permission_grants(
        self,
        team_id: str,
        resourceSpecificPermissionGrant_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        clientAppId: Optional[str] = None,
        clientId: Optional[str] = None,
        permission: Optional[str] = None,
        permissionType: Optional[str] = None,
        resourceAppId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property permissionGrants in teams

        Args:
            team_id (string): team-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            deletedDateTime (string): Date and time when this object was deleted. Always null when the object hasn't been deleted.
            clientAppId (string): ID of the service principal of the Microsoft Entra app that has been granted access. Read-only.
            clientId (string): ID of the Microsoft Entra app that has been granted access. Read-only.
            permission (string): The name of the resource-specific permission. Read-only.
            permissionType (string): The type of permission. Possible values are: Application, Delegated. Read-only.
            resourceAppId (string): ID of the Microsoft Entra app that is hosting the resource. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.resourceSpecificPermissionGrant
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "deletedDateTime": deletedDateTime,
            "clientAppId": clientAppId,
            "clientId": clientId,
            "permission": permission,
            "permissionType": permissionType,
            "resourceAppId": resourceAppId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_delete_permission_grants(
        self, team_id: str, resourceSpecificPermissionGrant_id: str
    ) -> Any:
        """

        Delete navigation property permissionGrants for teams

        Args:
            team_id (string): team-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.resourceSpecificPermissionGrant
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_team_permission_grants(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.resourceSpecificPermissionGrant
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/permissionGrants/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_get_photo(
        self,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get profilePhoto

        Args:
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.profilePhoto
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/photo"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_photo(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        height: Optional[float] = None,
        width: Optional[float] = None,
    ) -> Any:
        """

        Update profilePhoto

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            height (number): The height of the photo. Read-only.
            width (number): The width of the photo. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.profilePhoto
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "height": height,
            "width": width,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/photo"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_get_photo_content(self, team_id: str) -> Any:
        """

        Get profilePhoto

        Args:
            team_id (string): team-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.profilePhoto
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/photo/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_photo_content(self, team_id: str, body_content: bytes) -> Any:
        """

        Update profilePhoto

        Args:
            team_id (string): team-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.profilePhoto
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/teams/{team_id}/photo/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def teams_delete_photo_content(self, team_id: str) -> Any:
        """

        Delete media content for the navigation property photo in teams

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.profilePhoto
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/photo/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_get_primary_channel(
        self,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get primaryChannel

        Args:
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_primary_channel(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        email: Optional[str] = None,
        isArchived: Optional[bool] = None,
        isFavoriteByDefault: Optional[bool] = None,
        membershipType: Optional[Any] = None,
        summary: Optional[Any] = None,
        tenantId: Optional[str] = None,
        webUrl: Optional[str] = None,
        allMembers: Optional[List[Any]] = None,
        filesFolder: Optional[Any] = None,
        members: Optional[List[Any]] = None,
        messages: Optional[List[Any]] = None,
        sharedWithTeams: Optional[List[Any]] = None,
        tabs: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property primaryChannel in teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdDateTime (string): Read only. Timestamp at which the channel was created.
            description (string): Optional textual description for the channel.
            displayName (string): Channel name as it will appear to the user in Microsoft Teams. The maximum length is 50 characters.
            email (string): The email address for sending messages to the channel. Read-only.
            isArchived (boolean): Indicates whether the channel is archived. Read-only.
            isFavoriteByDefault (boolean): Indicates whether the channel should be marked as recommended for all members of the team to show in their channel list. Note: All recommended channels automatically show in the channels list for education and frontline worker users. The property can only be set programmatically via the Create team method. The default value is false.
            membershipType (string): The type of the channel. Can be set during creation and can't be changed. The possible values are: standard, private, unknownFutureValue, shared. The default value is standard. Use the Prefer: include-unknown-enum-members request header to get the following value in this evolvable enum: shared.
            summary (string): Contains summary information about the channel, including number of owners, members, guests, and an indicator for members from other tenants. The summary property will only be returned if it is specified in the $select clause of the Get channel method.
            tenantId (string): The ID of the Microsoft Entra tenant.
            webUrl (string): A hyperlink that will go to the channel in Microsoft Teams. This is the URL that you get when you right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an opaque blob, and not parsed. Read-only.
            allMembers (array): A collection of membership records associated with the channel, including both direct and indirect members of shared channels.
            filesFolder (string): Metadata for the location where the channel's files are stored.
            members (array): A collection of membership records associated with the channel.
            messages (array): A collection of all the messages in the channel. A navigation property. Nullable.
            sharedWithTeams (array): A collection of teams with which a channel is shared.
            tabs (array): A collection of all the tabs in the channel. A navigation property.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdDateTime": createdDateTime,
            "description": description,
            "displayName": displayName,
            "email": email,
            "isArchived": isArchived,
            "isFavoriteByDefault": isFavoriteByDefault,
            "membershipType": membershipType,
            "summary": summary,
            "tenantId": tenantId,
            "webUrl": webUrl,
            "allMembers": allMembers,
            "filesFolder": filesFolder,
            "members": members,
            "messages": messages,
            "sharedWithTeams": sharedWithTeams,
            "tabs": tabs,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_delete_primary_channel(self, team_id: str) -> Any:
        """

        Delete navigation property primaryChannel for teams

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_team_primary_channel_members(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get allMembers from teams

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers"
        )
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_team_primary_channel_members(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to allMembers for teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_primary_channel_members(
        self,
        team_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allMembers from teams

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel_members(
        self,
        team_id: str,
        conversationMember_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property allMembers in teams

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def remove_conversation_member(
        self, team_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property allMembers for teams

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_team_primary_channel_members(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_team_members_bulk(
        self, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers/add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_primary_channel_member(
        self, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers/remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_files_folder(
        self,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get filesFolder from teams

        Args:
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/filesFolder"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_primary_channel_content(
        self, team_id: str, format: Optional[str] = None
    ) -> Any:
        """

        Get content for the navigation property filesFolder from teams

        Args:
            team_id (string): team-id
            format (string): Format of the content

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/filesFolder/content"
        query_params = {k: v for k, v in [("$format", format)] if v is not None}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def upload_team_folder_content(self, team_id: str, body_content: bytes) -> Any:
        """

        Update content for the navigation property filesFolder in teams

        Args:
            team_id (string): team-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/filesFolder/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_team_files_folder_content(self, team_id: str) -> Any:
        """

        Delete content for the navigation property filesFolder in teams

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/filesFolder/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_primary_channel_members(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get members from teams

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_primary_channel_member(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_members(
        self,
        team_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from teams

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_member(
        self,
        team_id: str,
        conversationMember_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in teams

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "roles": roles,
            "visibleHistoryStartDateTime": visibleHistoryStartDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_team_primary_channel_member(
        self, team_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property members for teams

        Args:
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_member_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_team_primary_channel_member(
        self, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members/add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_member(
        self, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members/remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_team_primary_channel_messages(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get messages from teams

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_team_message(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, Any]]] = None,
        body: Optional[dict[str, Any]] = None,
        channelIdentity: Optional[Any] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, Any]]] = None,
        messageHistory: Optional[List[dict[str, Any]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[Any] = None,
        reactions: Optional[List[dict[str, Any]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to messages for teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (string): If the message was sent in a channel, represents identity of the channel.
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (string): Read-only. If present, represents details of an event that happened in a chat, a channel, or a team, for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
            from_ (string): Details of the sender of the chat message. Can only be set during migration.
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (string): Defines the properties of a policy violation set by a data loss prevention (DLP) application.
            reactions (array): Reactions for this chat message (for example, Like).
            replyToId (string): Read-only. ID of the parent chat message or root chat message of the thread. (Only applies to chat messages in channels, not chats.)
            subject (string): The subject of the chat message, in plaintext.
            summary (string): Summary text of the chat message that could be used for push notifications and summary views or fall back views. Only applies to channel chat messages, not chat messages in a chat.
            webUrl (string): Read-only. Link to the message in Microsoft Teams.
            hostedContents (array): Content in a message hosted by Microsoft Teams - for example, images or code snippets.
            replies (array): Replies for a specified message. Supports $expand for channel messages.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attachments": attachments,
            "body": body,
            "channelIdentity": channelIdentity,
            "chatId": chatId,
            "createdDateTime": createdDateTime,
            "deletedDateTime": deletedDateTime,
            "etag": etag,
            "eventDetail": eventDetail,
            "from": from_,
            "importance": importance,
            "lastEditedDateTime": lastEditedDateTime,
            "lastModifiedDateTime": lastModifiedDateTime,
            "locale": locale,
            "mentions": mentions,
            "messageHistory": messageHistory,
            "messageType": messageType,
            "policyViolation": policyViolation,
            "reactions": reactions,
            "replyToId": replyToId,
            "subject": subject,
            "summary": summary,
            "webUrl": webUrl,
            "hostedContents": hostedContents,
            "replies": replies,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_primary_channel_messages(
        self,
        team_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get messages from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel_message(
        self,
        team_id: str,
        chatMessage_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, Any]]] = None,
        body: Optional[dict[str, Any]] = None,
        channelIdentity: Optional[Any] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, Any]]] = None,
        messageHistory: Optional[List[dict[str, Any]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[Any] = None,
        reactions: Optional[List[dict[str, Any]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property messages in teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (string): If the message was sent in a channel, represents identity of the channel.
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (string): Read-only. If present, represents details of an event that happened in a chat, a channel, or a team, for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
            from_ (string): Details of the sender of the chat message. Can only be set during migration.
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (string): Defines the properties of a policy violation set by a data loss prevention (DLP) application.
            reactions (array): Reactions for this chat message (for example, Like).
            replyToId (string): Read-only. ID of the parent chat message or root chat message of the thread. (Only applies to chat messages in channels, not chats.)
            subject (string): The subject of the chat message, in plaintext.
            summary (string): Summary text of the chat message that could be used for push notifications and summary views or fall back views. Only applies to channel chat messages, not chat messages in a chat.
            webUrl (string): Read-only. Link to the message in Microsoft Teams.
            hostedContents (array): Content in a message hosted by Microsoft Teams - for example, images or code snippets.
            replies (array): Replies for a specified message. Supports $expand for channel messages.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attachments": attachments,
            "body": body,
            "channelIdentity": channelIdentity,
            "chatId": chatId,
            "createdDateTime": createdDateTime,
            "deletedDateTime": deletedDateTime,
            "etag": etag,
            "eventDetail": eventDetail,
            "from": from_,
            "importance": importance,
            "lastEditedDateTime": lastEditedDateTime,
            "lastModifiedDateTime": lastModifiedDateTime,
            "locale": locale,
            "mentions": mentions,
            "messageHistory": messageHistory,
            "messageType": messageType,
            "policyViolation": policyViolation,
            "reactions": reactions,
            "replyToId": replyToId,
            "subject": subject,
            "summary": summary,
            "webUrl": webUrl,
            "hostedContents": hostedContents,
            "replies": replies,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_message_by_id(self, team_id: str, chatMessage_id: str) -> Any:
        """

        Delete navigation property messages for teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_msg_hosted(
        self,
        team_id: str,
        chatMessage_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get hostedContents from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def upload_hosted_content(
        self,
        team_id: str,
        chatMessage_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def read_hosted_content(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_pri_ch_hosted_content(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def del_pri_ch_msg_hosted_content(
        self, team_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        Delete navigation property hostedContents for teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_message_content_by_id(
        self, team_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def put_pri_ch_hosted_content_val(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def del_pri_ch_msg_host_content_val(
        self, team_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_contents_count(
        self,
        team_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_to_chat_message(
        self, team_id: str, chatMessage_id: str, reactionType: Optional[str] = None
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_chat_message(self, team_id: str, chatMessage_id: str) -> Any:
        """

        Invoke action softDelete

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def restore_primary_channel_message(self, team_id: str, chatMessage_id: str) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_message(
        self, team_id: str, chatMessage_id: str, reactionType: Optional[str] = None
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_replies_by_message_id(
        self,
        team_id: str,
        chatMessage_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get replies from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_reply_to_chat_message(
        self,
        team_id: str,
        chatMessage_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, Any]]] = None,
        body: Optional[dict[str, Any]] = None,
        channelIdentity: Optional[Any] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, Any]]] = None,
        messageHistory: Optional[List[dict[str, Any]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[Any] = None,
        reactions: Optional[List[dict[str, Any]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to replies for teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (string): If the message was sent in a channel, represents identity of the channel.
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (string): Read-only. If present, represents details of an event that happened in a chat, a channel, or a team, for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
            from_ (string): Details of the sender of the chat message. Can only be set during migration.
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (string): Defines the properties of a policy violation set by a data loss prevention (DLP) application.
            reactions (array): Reactions for this chat message (for example, Like).
            replyToId (string): Read-only. ID of the parent chat message or root chat message of the thread. (Only applies to chat messages in channels, not chats.)
            subject (string): The subject of the chat message, in plaintext.
            summary (string): Summary text of the chat message that could be used for push notifications and summary views or fall back views. Only applies to channel chat messages, not chat messages in a chat.
            webUrl (string): Read-only. Link to the message in Microsoft Teams.
            hostedContents (array): Content in a message hosted by Microsoft Teams - for example, images or code snippets.
            replies (array): Replies for a specified message. Supports $expand for channel messages.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attachments": attachments,
            "body": body,
            "channelIdentity": channelIdentity,
            "chatId": chatId,
            "createdDateTime": createdDateTime,
            "deletedDateTime": deletedDateTime,
            "etag": etag,
            "eventDetail": eventDetail,
            "from": from_,
            "importance": importance,
            "lastEditedDateTime": lastEditedDateTime,
            "lastModifiedDateTime": lastModifiedDateTime,
            "locale": locale,
            "mentions": mentions,
            "messageHistory": messageHistory,
            "messageType": messageType,
            "policyViolation": policyViolation,
            "reactions": reactions,
            "replyToId": replyToId,
            "subject": subject,
            "summary": summary,
            "webUrl": webUrl,
            "hostedContents": hostedContents,
            "replies": replies,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_primary_channel_replies(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get replies from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel_reply(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        atodata_type: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, Any]]] = None,
        body: Optional[dict[str, Any]] = None,
        channelIdentity: Optional[Any] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, Any]]] = None,
        messageHistory: Optional[List[dict[str, Any]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[Any] = None,
        reactions: Optional[List[dict[str, Any]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property replies in teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (string): If the message was sent in a channel, represents identity of the channel.
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (string): Read-only. If present, represents details of an event that happened in a chat, a channel, or a team, for example, adding new members. For event messages, the messageType property will be set to systemEventMessage.
            from_ (string): Details of the sender of the chat message. Can only be set during migration.
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (string): Defines the properties of a policy violation set by a data loss prevention (DLP) application.
            reactions (array): Reactions for this chat message (for example, Like).
            replyToId (string): Read-only. ID of the parent chat message or root chat message of the thread. (Only applies to chat messages in channels, not chats.)
            subject (string): The subject of the chat message, in plaintext.
            summary (string): Summary text of the chat message that could be used for push notifications and summary views or fall back views. Only applies to channel chat messages, not chat messages in a chat.
            webUrl (string): Read-only. Link to the message in Microsoft Teams.
            hostedContents (array): Content in a message hosted by Microsoft Teams - for example, images or code snippets.
            replies (array): Replies for a specified message. Supports $expand for channel messages.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attachments": attachments,
            "body": body,
            "channelIdentity": channelIdentity,
            "chatId": chatId,
            "createdDateTime": createdDateTime,
            "deletedDateTime": deletedDateTime,
            "etag": etag,
            "eventDetail": eventDetail,
            "from": from_,
            "importance": importance,
            "lastEditedDateTime": lastEditedDateTime,
            "lastModifiedDateTime": lastModifiedDateTime,
            "locale": locale,
            "mentions": mentions,
            "messageHistory": messageHistory,
            "messageType": messageType,
            "policyViolation": policyViolation,
            "reactions": reactions,
            "replyToId": replyToId,
            "subject": subject,
            "summary": summary,
            "webUrl": webUrl,
            "hostedContents": hostedContents,
            "replies": replies,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_reply(
        self, team_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Delete navigation property replies for teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_reply_contents(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get hostedContents from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_team_reply_hosted_content(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_pri_ch_reply_hosted_content(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_pri_ch_reply_hosted_content(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def del_pri_ch_reply_hosted_content(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_pri_ch_reply_host_content_val(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def put_pri_ch_reply_hosted_content_val(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def del_pri_ch_reply_host_cont_val(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_hosted_content_replies(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_to_reply_message(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def delete_reply_message(
        self, team_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_team_message_reply_delete(
        self, team_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_team_message_reply_reaction(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_primary_channel_replies_count(
        self,
        team_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_reply_delta(
        self,
        team_id: str,
        chatMessage_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        select: Optional[List[str]] = None,
        orderby: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Invoke function delta

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            select (array): Select properties to be returned
            orderby (array): Order items by property values
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/delta()"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$select", select),
                ("$orderby", orderby),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_message_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_messages_delta(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        select: Optional[List[str]] = None,
        orderby: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Invoke function delta

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            select (array): Select properties to be returned
            orderby (array): Order items by property values
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/delta()"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$select", select),
                ("$orderby", orderby),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def archive_primary_channel(
        self, team_id: str, shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None
    ) -> Any:
        """

        Invoke action archive

        Args:
            team_id (string): team-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_team_migration(self, team_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def has_primary_channel_access(self, team_id: str) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            team_id (string): team-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def provision_team_channel_email(self, team_id: str) -> Any:
        """

        Invoke action provisionEmail

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_primary_channel_email(self, team_id: str) -> Any:
        """

        Invoke action removeEmail

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_primary_channel(self, team_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/unarchive"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_primary_channel_shared_teams(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get sharedWithTeams from teams

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def share_primary_channel_with_teams(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to sharedWithTeams for teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The name of the team.
            tenantId (string): The ID of the Microsoft Entra tenant.
            team (string): team
            isHostTeam (boolean): Indicates whether the team is the host of the channel.
            allowedMembers (array): A collection of team members who have access to the shared channel.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "tenantId": tenantId,
            "team": team,
            "isHostTeam": isHostTeam,
            "allowedMembers": allowedMembers,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_channel_info_by_id(
        self,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get sharedWithTeams from teams

        Args:
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_shared_channel_team_info(
        self,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property sharedWithTeams in teams

        Args:
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The name of the team.
            tenantId (string): The ID of the Microsoft Entra tenant.
            team (string): team
            isHostTeam (boolean): Indicates whether the team is the host of the channel.
            allowedMembers (array): A collection of team members who have access to the shared channel.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "tenantId": tenantId,
            "team": team,
            "isHostTeam": isHostTeam,
            "allowedMembers": allowedMembers,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_shared_channel_team_info(
        self, team_id: str, sharedWithChannelTeamInfo_id: str
    ) -> Any:
        """

        Delete navigation property sharedWithTeams for teams

        Args:
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_shared_members(
        self,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get allowedMembers from teams

        Args:
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_shared_member_by_id(
        self,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allowedMembers from teams

        Args:
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_team_members_count(
        self,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_with_team_info(
        self,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from teams

        Args:
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_team_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/sharedWithTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_primary_channel_list_tabs(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get tabs from teams

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/tabs"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_team_tab(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        configuration: Optional[Any] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to tabs for teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            configuration (string): Container for custom settings applied to a tab. The tab is considered configured only once this property is set.
            displayName (string): Name of the tab.
            webUrl (string): Deep link URL of the tab instance. Read only.
            teamsApp (string): The application that is linked to the tab. This can't be changed after tab creation.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "configuration": configuration,
            "displayName": displayName,
            "webUrl": webUrl,
            "teamsApp": teamsApp,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_primary_channel_get_tabs(
        self,
        team_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tabs from teams

        Args:
            team_id (string): team-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_tab(
        self,
        team_id: str,
        teamsTab_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        configuration: Optional[Any] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property tabs in teams

        Args:
            team_id (string): team-id
            teamsTab_id (string): teamsTab-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            configuration (string): Container for custom settings applied to a tab. The tab is considered configured only once this property is set.
            displayName (string): Name of the tab.
            webUrl (string): Deep link URL of the tab instance. Read only.
            teamsApp (string): The application that is linked to the tab. This can't be changed after tab creation.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "configuration": configuration,
            "displayName": displayName,
            "webUrl": webUrl,
            "teamsApp": teamsApp,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_primary_channel_tab(self, team_id: str, teamsTab_id: str) -> Any:
        """

        Delete navigation property tabs for teams

        Args:
            team_id (string): team-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_teams_app_by_tab_id(
        self,
        team_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from teams

        Args:
            team_id (string): team-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_primary_channel_tabs_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_get_schedule(
        self,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get schedule

        Args:
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_set_schedule(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        enabled: Optional[bool] = None,
        isActivitiesIncludedWhenCopyingShiftsEnabled: Optional[bool] = None,
        offerShiftRequestsEnabled: Optional[bool] = None,
        openShiftsEnabled: Optional[bool] = None,
        provisionStatus: Optional[Any] = None,
        provisionStatusCode: Optional[str] = None,
        startDayOfWeek: Optional[Any] = None,
        swapShiftsRequestsEnabled: Optional[bool] = None,
        timeClockEnabled: Optional[bool] = None,
        timeClockSettings: Optional[Any] = None,
        timeOffRequestsEnabled: Optional[bool] = None,
        timeZone: Optional[str] = None,
        workforceIntegrationIds: Optional[List[str]] = None,
        dayNotes: Optional[List[Any]] = None,
        offerShiftRequests: Optional[List[Any]] = None,
        openShiftChangeRequests: Optional[List[Any]] = None,
        openShifts: Optional[List[Any]] = None,
        schedulingGroups: Optional[List[Any]] = None,
        shifts: Optional[List[Any]] = None,
        swapShiftsChangeRequests: Optional[List[Any]] = None,
        timeCards: Optional[List[Any]] = None,
        timeOffReasons: Optional[List[Any]] = None,
        timeOffRequests: Optional[List[Any]] = None,
        timesOff: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create or replace schedule

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            enabled (boolean): Indicates whether the schedule is enabled for the team. Required.
            isActivitiesIncludedWhenCopyingShiftsEnabled (boolean): Indicates whether copied shifts include activities from the original shift.
            offerShiftRequestsEnabled (boolean): Indicates whether offer shift requests are enabled for the schedule.
            openShiftsEnabled (boolean): Indicates whether open shifts are enabled for the schedule.
            provisionStatus (string): The status of the schedule provisioning. The possible values are notStarted, running, completed, failed.
            provisionStatusCode (string): Additional information about why schedule provisioning failed.
            startDayOfWeek (string): Indicates the start day of the week. The possible values are: sunday, monday, tuesday, wednesday, thursday, friday, saturday.
            swapShiftsRequestsEnabled (boolean): Indicates whether swap shifts requests are enabled for the schedule.
            timeClockEnabled (boolean): Indicates whether time clock is enabled for the schedule.
            timeClockSettings (string): The time clock location settings for this schedule.
            timeOffRequestsEnabled (boolean): Indicates whether time off requests are enabled for the schedule.
            timeZone (string): Indicates the time zone of the schedule team using tz database format. Required.
            workforceIntegrationIds (array): The IDs for the workforce integrations associated with this schedule.
            dayNotes (array): The day notes in the schedule.
            offerShiftRequests (array): The offer requests for shifts in the schedule.
            openShiftChangeRequests (array): The open shift requests in the schedule.
            openShifts (array): The set of open shifts in a scheduling group in the schedule.
            schedulingGroups (array): The logical grouping of users in the schedule (usually by role).
            shifts (array): The shifts in the schedule.
            swapShiftsChangeRequests (array): The swap requests for shifts in the schedule.
            timeCards (array): The time cards in the schedule.
            timeOffReasons (array): The set of reasons for a time off in the schedule.
            timeOffRequests (array): The time off requests in the schedule.
            timesOff (array): The instances of times off in the schedule.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "enabled": enabled,
            "isActivitiesIncludedWhenCopyingShiftsEnabled": isActivitiesIncludedWhenCopyingShiftsEnabled,
            "offerShiftRequestsEnabled": offerShiftRequestsEnabled,
            "openShiftsEnabled": openShiftsEnabled,
            "provisionStatus": provisionStatus,
            "provisionStatusCode": provisionStatusCode,
            "startDayOfWeek": startDayOfWeek,
            "swapShiftsRequestsEnabled": swapShiftsRequestsEnabled,
            "timeClockEnabled": timeClockEnabled,
            "timeClockSettings": timeClockSettings,
            "timeOffRequestsEnabled": timeOffRequestsEnabled,
            "timeZone": timeZone,
            "workforceIntegrationIds": workforceIntegrationIds,
            "dayNotes": dayNotes,
            "offerShiftRequests": offerShiftRequests,
            "openShiftChangeRequests": openShiftChangeRequests,
            "openShifts": openShifts,
            "schedulingGroups": schedulingGroups,
            "shifts": shifts,
            "swapShiftsChangeRequests": swapShiftsChangeRequests,
            "timeCards": timeCards,
            "timeOffReasons": timeOffReasons,
            "timeOffRequests": timeOffRequests,
            "timesOff": timesOff,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_delete_schedule(self, team_id: str) -> Any:
        """

        Delete navigation property schedule for teams

        Args:
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_list_day_notes(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get dayNotes from teams

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/dayNotes"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_create_day_notes(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        dayNoteDate: Optional[str] = None,
        draftDayNote: Optional[Any] = None,
        sharedDayNote: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to dayNotes for teams

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            dayNoteDate (string): The date of the day note.
            draftDayNote (string): The draft version of this day note that is viewable by managers. Only contentType text is supported.
            sharedDayNote (string): The shared version of this day note that is viewable by both employees and managers. Only contentType text is supported.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "dayNoteDate": dayNoteDate,
            "draftDayNote": draftDayNote,
            "sharedDayNote": sharedDayNote,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/dayNotes"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_schedule_get_day_notes(
        self,
        team_id: str,
        dayNote_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get dayNotes from teams

        Args:
            team_id (string): team-id
            dayNote_id (string): dayNote-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if dayNote_id is None:
            raise ValueError("Missing required parameter 'dayNote-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/dayNotes/{dayNote_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_update_day_notes(
        self,
        team_id: str,
        dayNote_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        dayNoteDate: Optional[str] = None,
        draftDayNote: Optional[Any] = None,
        sharedDayNote: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property dayNotes in teams

        Args:
            team_id (string): team-id
            dayNote_id (string): dayNote-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            dayNoteDate (string): The date of the day note.
            draftDayNote (string): The draft version of this day note that is viewable by managers. Only contentType text is supported.
            sharedDayNote (string): The shared version of this day note that is viewable by both employees and managers. Only contentType text is supported.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if dayNote_id is None:
            raise ValueError("Missing required parameter 'dayNote-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "dayNoteDate": dayNoteDate,
            "draftDayNote": draftDayNote,
            "sharedDayNote": sharedDayNote,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/dayNotes/{dayNote_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_schedule_delete_day_notes(self, team_id: str, dayNote_id: str) -> Any:
        """

        Delete navigation property dayNotes for teams

        Args:
            team_id (string): team-id
            dayNote_id (string): dayNote-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if dayNote_id is None:
            raise ValueError("Missing required parameter 'dayNote-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/dayNotes/{dayNote_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_day_notes_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/schedule/dayNotes/$count"
        )
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_team_schedule_share(
        self,
        team_id: str,
        notifyTeam: Optional[bool] = None,
        startDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
    ) -> Any:
        """

        Invoke action share

        Args:
            team_id (string): team-id
            notifyTeam (boolean): notifyTeam
            startDateTime (string): startDateTime
            endDateTime (string): endDateTime

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "notifyTeam": notifyTeam,
            "startDateTime": startDateTime,
            "endDateTime": endDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/share"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_shift_requests(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List offerShiftRequest

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/offerShiftRequests"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def offer_shift_requests(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[Any] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[Any] = None,
        recipientActionDateTime: Optional[str] = None,
        recipientActionMessage: Optional[str] = None,
        recipientUserId: Optional[str] = None,
        senderShiftId: Optional[str] = None,
    ) -> Any:
        """

        Create offerShiftRequest

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): Indicates who the request is assigned to. Possible values are: sender, recipient, manager, system, unknownFutureValue.
            managerActionDateTime (string): The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            managerActionMessage (string): The message sent by the manager regarding the scheduleChangeRequest. Optional.
            managerUserId (string): The user ID of the manager who approved or declined the scheduleChangeRequest.
            senderDateTime (string): The date and time when the sender sent the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            senderMessage (string): The message sent by the sender of the scheduleChangeRequest. Optional.
            senderUserId (string): The user ID of the sender of the scheduleChangeRequest.
            state (string): The state of the scheduleChangeRequest. Possible values are: pending, approved, declined, unknownFutureValue.
            recipientActionDateTime (string): The date and time when the recipient approved or declined the request.
            recipientActionMessage (string): The message sent by the recipient regarding the request.
            recipientUserId (string): The recipient's user ID.
            senderShiftId (string): The sender's shift ID.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "assignedTo": assignedTo,
            "managerActionDateTime": managerActionDateTime,
            "managerActionMessage": managerActionMessage,
            "managerUserId": managerUserId,
            "senderDateTime": senderDateTime,
            "senderMessage": senderMessage,
            "senderUserId": senderUserId,
            "state": state,
            "recipientActionDateTime": recipientActionDateTime,
            "recipientActionMessage": recipientActionMessage,
            "recipientUserId": recipientUserId,
            "senderShiftId": senderShiftId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/offerShiftRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_schedule_offer_shifts(
        self,
        team_id: str,
        offerShiftRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get offerShiftRequest

        Args:
            team_id (string): team-id
            offerShiftRequest_id (string): offerShiftRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if offerShiftRequest_id is None:
            raise ValueError("Missing required parameter 'offerShiftRequest-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_offer_shift_request(
        self,
        team_id: str,
        offerShiftRequest_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[Any] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[Any] = None,
        recipientActionDateTime: Optional[str] = None,
        recipientActionMessage: Optional[str] = None,
        recipientUserId: Optional[str] = None,
        senderShiftId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property offerShiftRequests in teams

        Args:
            team_id (string): team-id
            offerShiftRequest_id (string): offerShiftRequest-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): Indicates who the request is assigned to. Possible values are: sender, recipient, manager, system, unknownFutureValue.
            managerActionDateTime (string): The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            managerActionMessage (string): The message sent by the manager regarding the scheduleChangeRequest. Optional.
            managerUserId (string): The user ID of the manager who approved or declined the scheduleChangeRequest.
            senderDateTime (string): The date and time when the sender sent the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            senderMessage (string): The message sent by the sender of the scheduleChangeRequest. Optional.
            senderUserId (string): The user ID of the sender of the scheduleChangeRequest.
            state (string): The state of the scheduleChangeRequest. Possible values are: pending, approved, declined, unknownFutureValue.
            recipientActionDateTime (string): The date and time when the recipient approved or declined the request.
            recipientActionMessage (string): The message sent by the recipient regarding the request.
            recipientUserId (string): The recipient's user ID.
            senderShiftId (string): The sender's shift ID.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if offerShiftRequest_id is None:
            raise ValueError("Missing required parameter 'offerShiftRequest-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "assignedTo": assignedTo,
            "managerActionDateTime": managerActionDateTime,
            "managerActionMessage": managerActionMessage,
            "managerUserId": managerUserId,
            "senderDateTime": senderDateTime,
            "senderMessage": senderMessage,
            "senderUserId": senderUserId,
            "state": state,
            "recipientActionDateTime": recipientActionDateTime,
            "recipientActionMessage": recipientActionMessage,
            "recipientUserId": recipientUserId,
            "senderShiftId": senderShiftId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_shift_offer_request(
        self, team_id: str, offerShiftRequest_id: str
    ) -> Any:
        """

        Delete navigation property offerShiftRequests for teams

        Args:
            team_id (string): team-id
            offerShiftRequest_id (string): offerShiftRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if offerShiftRequest_id is None:
            raise ValueError("Missing required parameter 'offerShiftRequest-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_shift_offer_requests(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/offerShiftRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_open_shift_change_requests(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List openShiftChangeRequests

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShiftChangeRequests"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_open_shift_change_request(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[Any] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[Any] = None,
        openShiftId: Optional[str] = None,
    ) -> Any:
        """

        Create openShiftChangeRequest

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): Indicates who the request is assigned to. Possible values are: sender, recipient, manager, system, unknownFutureValue.
            managerActionDateTime (string): The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            managerActionMessage (string): The message sent by the manager regarding the scheduleChangeRequest. Optional.
            managerUserId (string): The user ID of the manager who approved or declined the scheduleChangeRequest.
            senderDateTime (string): The date and time when the sender sent the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            senderMessage (string): The message sent by the sender of the scheduleChangeRequest. Optional.
            senderUserId (string): The user ID of the sender of the scheduleChangeRequest.
            state (string): The state of the scheduleChangeRequest. Possible values are: pending, approved, declined, unknownFutureValue.
            openShiftId (string): ID for the open shift.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "assignedTo": assignedTo,
            "managerActionDateTime": managerActionDateTime,
            "managerActionMessage": managerActionMessage,
            "managerUserId": managerUserId,
            "senderDateTime": senderDateTime,
            "senderMessage": senderMessage,
            "senderUserId": senderUserId,
            "state": state,
            "openShiftId": openShiftId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShiftChangeRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_open_shift_change_request(
        self,
        team_id: str,
        openShiftChangeRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get openShiftChangeRequest

        Args:
            team_id (string): team-id
            openShiftChangeRequest_id (string): openShiftChangeRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShiftChangeRequest_id is None:
            raise ValueError("Missing required parameter 'openShiftChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_open_shift_change_request(
        self,
        team_id: str,
        openShiftChangeRequest_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[Any] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[Any] = None,
        openShiftId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property openShiftChangeRequests in teams

        Args:
            team_id (string): team-id
            openShiftChangeRequest_id (string): openShiftChangeRequest-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): Indicates who the request is assigned to. Possible values are: sender, recipient, manager, system, unknownFutureValue.
            managerActionDateTime (string): The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            managerActionMessage (string): The message sent by the manager regarding the scheduleChangeRequest. Optional.
            managerUserId (string): The user ID of the manager who approved or declined the scheduleChangeRequest.
            senderDateTime (string): The date and time when the sender sent the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            senderMessage (string): The message sent by the sender of the scheduleChangeRequest. Optional.
            senderUserId (string): The user ID of the sender of the scheduleChangeRequest.
            state (string): The state of the scheduleChangeRequest. Possible values are: pending, approved, declined, unknownFutureValue.
            openShiftId (string): ID for the open shift.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShiftChangeRequest_id is None:
            raise ValueError("Missing required parameter 'openShiftChangeRequest-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "assignedTo": assignedTo,
            "managerActionDateTime": managerActionDateTime,
            "managerActionMessage": managerActionMessage,
            "managerUserId": managerUserId,
            "senderDateTime": senderDateTime,
            "senderMessage": senderMessage,
            "senderUserId": senderUserId,
            "state": state,
            "openShiftId": openShiftId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_open_shift_change_request(
        self, team_id: str, openShiftChangeRequest_id: str
    ) -> Any:
        """

        Delete navigation property openShiftChangeRequests for teams

        Args:
            team_id (string): team-id
            openShiftChangeRequest_id (string): openShiftChangeRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShiftChangeRequest_id is None:
            raise ValueError("Missing required parameter 'openShiftChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_open_shift_change_requests(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShiftChangeRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_list_open_shifts(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List openShifts

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShifts"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_open_shifts(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        draftOpenShift: Optional[Any] = None,
        isStagedForDeletion: Optional[bool] = None,
        schedulingGroupId: Optional[str] = None,
        sharedOpenShift: Optional[Any] = None,
    ) -> Any:
        """

        Create openShift

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftOpenShift (string): Draft changes in the openShift are only visible to managers until they're shared.
            isStagedForDeletion (boolean): The openShift is marked for deletion, a process that is finalized when the schedule is shared.
            schedulingGroupId (string): The ID of the schedulingGroup that contains the openShift.
            sharedOpenShift (string): The shared version of this openShift that is viewable by both employees and managers.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "draftOpenShift": draftOpenShift,
            "isStagedForDeletion": isStagedForDeletion,
            "schedulingGroupId": schedulingGroupId,
            "sharedOpenShift": sharedOpenShift,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShifts"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_schedule_get_open_shifts(
        self,
        team_id: str,
        openShift_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get openShift

        Args:
            team_id (string): team-id
            openShift_id (string): openShift-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShift_id is None:
            raise ValueError("Missing required parameter 'openShift-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShifts/{openShift_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_open_shift(
        self,
        team_id: str,
        openShift_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        draftOpenShift: Optional[Any] = None,
        isStagedForDeletion: Optional[bool] = None,
        schedulingGroupId: Optional[str] = None,
        sharedOpenShift: Optional[Any] = None,
    ) -> Any:
        """

        Update openShift

        Args:
            team_id (string): team-id
            openShift_id (string): openShift-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftOpenShift (string): Draft changes in the openShift are only visible to managers until they're shared.
            isStagedForDeletion (boolean): The openShift is marked for deletion, a process that is finalized when the schedule is shared.
            schedulingGroupId (string): The ID of the schedulingGroup that contains the openShift.
            sharedOpenShift (string): The shared version of this openShift that is viewable by both employees and managers.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShift_id is None:
            raise ValueError("Missing required parameter 'openShift-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "draftOpenShift": draftOpenShift,
            "isStagedForDeletion": isStagedForDeletion,
            "schedulingGroupId": schedulingGroupId,
            "sharedOpenShift": sharedOpenShift,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShifts/{openShift_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_open_shift_by_id(self, team_id: str, openShift_id: str) -> Any:
        """

        Delete openShift

        Args:
            team_id (string): team-id
            openShift_id (string): openShift-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShift_id is None:
            raise ValueError("Missing required parameter 'openShift-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShifts/{openShift_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_open_shifts(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/openShifts/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_scheduling_groups(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List scheduleGroups

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/schedule/schedulingGroups"
        )
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_scheduling_group(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        code: Optional[str] = None,
        displayName: Optional[str] = None,
        isActive: Optional[bool] = None,
        userIds: Optional[List[str]] = None,
    ) -> Any:
        """

        Create schedulingGroup

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            code (string): The code for the schedulingGroup to represent an external identifier. This field must be unique within the team in Microsoft Teams and uses an alphanumeric format, with a maximum of 100 characters.
            displayName (string): The display name for the schedulingGroup. Required.
            isActive (boolean): Indicates whether the schedulingGroup can be used when creating new entities or updating existing ones. Required.
            userIds (array): The list of user IDs that are a member of the schedulingGroup. Required.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "code": code,
            "displayName": displayName,
            "isActive": isActive,
            "userIds": userIds,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/schedule/schedulingGroups"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_schedule_scheduling_group(
        self,
        team_id: str,
        schedulingGroup_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get schedulingGroup

        Args:
            team_id (string): team-id
            schedulingGroup_id (string): schedulingGroup-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if schedulingGroup_id is None:
            raise ValueError("Missing required parameter 'schedulingGroup-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_scheduling_group(
        self,
        team_id: str,
        schedulingGroup_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        code: Optional[str] = None,
        displayName: Optional[str] = None,
        isActive: Optional[bool] = None,
        userIds: Optional[List[str]] = None,
    ) -> Any:
        """

        Replace schedulingGroup

        Args:
            team_id (string): team-id
            schedulingGroup_id (string): schedulingGroup-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            code (string): The code for the schedulingGroup to represent an external identifier. This field must be unique within the team in Microsoft Teams and uses an alphanumeric format, with a maximum of 100 characters.
            displayName (string): The display name for the schedulingGroup. Required.
            isActive (boolean): Indicates whether the schedulingGroup can be used when creating new entities or updating existing ones. Required.
            userIds (array): The list of user IDs that are a member of the schedulingGroup. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if schedulingGroup_id is None:
            raise ValueError("Missing required parameter 'schedulingGroup-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "code": code,
            "displayName": displayName,
            "isActive": isActive,
            "userIds": userIds,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_scheduling_group(self, team_id: str, schedulingGroup_id: str) -> Any:
        """

        Delete schedulingGroup

        Args:
            team_id (string): team-id
            schedulingGroup_id (string): schedulingGroup-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if schedulingGroup_id is None:
            raise ValueError("Missing required parameter 'schedulingGroup-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_scheduling_groups(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/schedulingGroups/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_list_shifts(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List shifts

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/shifts"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_create_shifts(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        draftShift: Optional[Any] = None,
        isStagedForDeletion: Optional[bool] = None,
        schedulingGroupId: Optional[str] = None,
        sharedShift: Optional[Any] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Create shift

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftShift (string): Draft changes in the shift. Draft changes are only visible to managers. The changes are visible to employees when they're shared, which copies the changes from the draftShift to the sharedShift property.
            isStagedForDeletion (boolean): The shift is marked for deletion, a process that is finalized when the schedule is shared.
            schedulingGroupId (string): ID of the scheduling group the shift is part of. Required.
            sharedShift (string): The shared version of this shift that is viewable by both employees and managers. Updates to the sharedShift property send notifications to users in the Teams client.
            userId (string): ID of the user assigned to the shift. Required.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "draftShift": draftShift,
            "isStagedForDeletion": isStagedForDeletion,
            "schedulingGroupId": schedulingGroupId,
            "sharedShift": sharedShift,
            "userId": userId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/shifts"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_schedule_get_shifts(
        self,
        team_id: str,
        shift_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get shift

        Args:
            team_id (string): team-id
            shift_id (string): shift-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if shift_id is None:
            raise ValueError("Missing required parameter 'shift-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/shifts/{shift_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_update_shifts(
        self,
        team_id: str,
        shift_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        draftShift: Optional[Any] = None,
        isStagedForDeletion: Optional[bool] = None,
        schedulingGroupId: Optional[str] = None,
        sharedShift: Optional[Any] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Replace shift

        Args:
            team_id (string): team-id
            shift_id (string): shift-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftShift (string): Draft changes in the shift. Draft changes are only visible to managers. The changes are visible to employees when they're shared, which copies the changes from the draftShift to the sharedShift property.
            isStagedForDeletion (boolean): The shift is marked for deletion, a process that is finalized when the schedule is shared.
            schedulingGroupId (string): ID of the scheduling group the shift is part of. Required.
            sharedShift (string): The shared version of this shift that is viewable by both employees and managers. Updates to the sharedShift property send notifications to users in the Teams client.
            userId (string): ID of the user assigned to the shift. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if shift_id is None:
            raise ValueError("Missing required parameter 'shift-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "draftShift": draftShift,
            "isStagedForDeletion": isStagedForDeletion,
            "schedulingGroupId": schedulingGroupId,
            "sharedShift": sharedShift,
            "userId": userId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/shifts/{shift_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_schedule_delete_shifts(self, team_id: str, shift_id: str) -> Any:
        """

        Delete shift

        Args:
            team_id (string): team-id
            shift_id (string): shift-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if shift_id is None:
            raise ValueError("Missing required parameter 'shift-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/shifts/{shift_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_schedule_shifts_count_by_team_id(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/shifts/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_swap_shift_change_requests(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List swapShiftsChangeRequest

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/swapShiftsChangeRequests"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def swap_shift_requests(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[Any] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[Any] = None,
        recipientActionDateTime: Optional[str] = None,
        recipientActionMessage: Optional[str] = None,
        recipientUserId: Optional[str] = None,
        senderShiftId: Optional[str] = None,
        recipientShiftId: Optional[str] = None,
    ) -> Any:
        """

        Create swapShiftsChangeRequest

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): Indicates who the request is assigned to. Possible values are: sender, recipient, manager, system, unknownFutureValue.
            managerActionDateTime (string): The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            managerActionMessage (string): The message sent by the manager regarding the scheduleChangeRequest. Optional.
            managerUserId (string): The user ID of the manager who approved or declined the scheduleChangeRequest.
            senderDateTime (string): The date and time when the sender sent the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            senderMessage (string): The message sent by the sender of the scheduleChangeRequest. Optional.
            senderUserId (string): The user ID of the sender of the scheduleChangeRequest.
            state (string): The state of the scheduleChangeRequest. Possible values are: pending, approved, declined, unknownFutureValue.
            recipientActionDateTime (string): The date and time when the recipient approved or declined the request.
            recipientActionMessage (string): The message sent by the recipient regarding the request.
            recipientUserId (string): The recipient's user ID.
            senderShiftId (string): The sender's shift ID.
            recipientShiftId (string): The recipient's Shift ID

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "assignedTo": assignedTo,
            "managerActionDateTime": managerActionDateTime,
            "managerActionMessage": managerActionMessage,
            "managerUserId": managerUserId,
            "senderDateTime": senderDateTime,
            "senderMessage": senderMessage,
            "senderUserId": senderUserId,
            "state": state,
            "recipientActionDateTime": recipientActionDateTime,
            "recipientActionMessage": recipientActionMessage,
            "recipientUserId": recipientUserId,
            "senderShiftId": senderShiftId,
            "recipientShiftId": recipientShiftId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/swapShiftsChangeRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def swap_shift_request_read(
        self,
        team_id: str,
        swapShiftsChangeRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get swapShiftsChangeRequest

        Args:
            team_id (string): team-id
            swapShiftsChangeRequest_id (string): swapShiftsChangeRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if swapShiftsChangeRequest_id is None:
            raise ValueError("Missing required parameter 'swapShiftsChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_swap_shift_request(
        self,
        team_id: str,
        swapShiftsChangeRequest_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[Any] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[Any] = None,
        recipientActionDateTime: Optional[str] = None,
        recipientActionMessage: Optional[str] = None,
        recipientUserId: Optional[str] = None,
        senderShiftId: Optional[str] = None,
        recipientShiftId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property swapShiftsChangeRequests in teams

        Args:
            team_id (string): team-id
            swapShiftsChangeRequest_id (string): swapShiftsChangeRequest-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): Indicates who the request is assigned to. Possible values are: sender, recipient, manager, system, unknownFutureValue.
            managerActionDateTime (string): The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            managerActionMessage (string): The message sent by the manager regarding the scheduleChangeRequest. Optional.
            managerUserId (string): The user ID of the manager who approved or declined the scheduleChangeRequest.
            senderDateTime (string): The date and time when the sender sent the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            senderMessage (string): The message sent by the sender of the scheduleChangeRequest. Optional.
            senderUserId (string): The user ID of the sender of the scheduleChangeRequest.
            state (string): The state of the scheduleChangeRequest. Possible values are: pending, approved, declined, unknownFutureValue.
            recipientActionDateTime (string): The date and time when the recipient approved or declined the request.
            recipientActionMessage (string): The message sent by the recipient regarding the request.
            recipientUserId (string): The recipient's user ID.
            senderShiftId (string): The sender's shift ID.
            recipientShiftId (string): The recipient's Shift ID

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if swapShiftsChangeRequest_id is None:
            raise ValueError("Missing required parameter 'swapShiftsChangeRequest-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "assignedTo": assignedTo,
            "managerActionDateTime": managerActionDateTime,
            "managerActionMessage": managerActionMessage,
            "managerUserId": managerUserId,
            "senderDateTime": senderDateTime,
            "senderMessage": senderMessage,
            "senderUserId": senderUserId,
            "state": state,
            "recipientActionDateTime": recipientActionDateTime,
            "recipientActionMessage": recipientActionMessage,
            "recipientUserId": recipientUserId,
            "senderShiftId": senderShiftId,
            "recipientShiftId": recipientShiftId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_swap_shifts_change_request(
        self, team_id: str, swapShiftsChangeRequest_id: str
    ) -> Any:
        """

        Delete navigation property swapShiftsChangeRequests for teams

        Args:
            team_id (string): team-id
            swapShiftsChangeRequest_id (string): swapShiftsChangeRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if swapShiftsChangeRequest_id is None:
            raise ValueError("Missing required parameter 'swapShiftsChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_swap_shift_requests(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/swapShiftsChangeRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_list_time_cards(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List timeCard

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_create_time_cards(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        breaks: Optional[List[dict[str, Any]]] = None,
        clockInEvent: Optional[Any] = None,
        clockOutEvent: Optional[Any] = None,
        confirmedBy: Optional[Any] = None,
        notes: Optional[Any] = None,
        originalEntry: Optional[Any] = None,
        state: Optional[Any] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Create timeCard

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            breaks (array): The list of breaks associated with the timeCard.
            clockInEvent (string): The clock-in event of the timeCard.
            clockOutEvent (string): The clock-out event of the timeCard.
            confirmedBy (string): Indicates whether this timeCard entry is confirmed. Possible values are: none, user, manager, unknownFutureValue.
            notes (string): Notes about the timeCard.
            originalEntry (string): The original timeCardEntry of the timeCard before it was edited.
            state (string): The current state of the timeCard during its life cycle. The possible values are: clockedIn, onBreak, clockedOut, unknownFutureValue.
            userId (string): User ID to which the timeCard belongs.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "breaks": breaks,
            "clockInEvent": clockInEvent,
            "clockOutEvent": clockOutEvent,
            "confirmedBy": confirmedBy,
            "notes": notes,
            "originalEntry": originalEntry,
            "state": state,
            "userId": userId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_schedule_get_time_cards(
        self,
        team_id: str,
        timeCard_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeCards from teams

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_update_time_cards(
        self,
        team_id: str,
        timeCard_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        breaks: Optional[List[dict[str, Any]]] = None,
        clockInEvent: Optional[Any] = None,
        clockOutEvent: Optional[Any] = None,
        confirmedBy: Optional[Any] = None,
        notes: Optional[Any] = None,
        originalEntry: Optional[Any] = None,
        state: Optional[Any] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property timeCards in teams

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            breaks (array): The list of breaks associated with the timeCard.
            clockInEvent (string): The clock-in event of the timeCard.
            clockOutEvent (string): The clock-out event of the timeCard.
            confirmedBy (string): Indicates whether this timeCard entry is confirmed. Possible values are: none, user, manager, unknownFutureValue.
            notes (string): Notes about the timeCard.
            originalEntry (string): The original timeCardEntry of the timeCard before it was edited.
            state (string): The current state of the timeCard during its life cycle. The possible values are: clockedIn, onBreak, clockedOut, unknownFutureValue.
            userId (string): User ID to which the timeCard belongs.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "breaks": breaks,
            "clockInEvent": clockInEvent,
            "clockOutEvent": clockOutEvent,
            "confirmedBy": confirmedBy,
            "notes": notes,
            "originalEntry": originalEntry,
            "state": state,
            "userId": userId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_schedule_delete_time_cards(self, team_id: str, timeCard_id: str) -> Any:
        """

        Delete timeCard

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def clock_out_time_card(
        self,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action clockOut

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (string): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        request_body_data = None
        request_body_data = {
            "isAtApprovedLocation": isAtApprovedLocation,
            "notes": notes,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}/clockOut"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def confirm_time_card(self, team_id: str, timeCard_id: str) -> Any:
        """

        Invoke action confirm

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}/confirm"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def end_team_break(
        self,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action endBreak

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (string): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        request_body_data = None
        request_body_data = {
            "isAtApprovedLocation": isAtApprovedLocation,
            "notes": notes,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}/endBreak"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def start_time_card_break(
        self,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action startBreak

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (string): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        request_body_data = None
        request_body_data = {
            "isAtApprovedLocation": isAtApprovedLocation,
            "notes": notes,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}/startBreak"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_schedule_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/$count"
        )
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def clock_in_team_schedule(
        self,
        team_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        onBehalfOfUserId: Optional[str] = None,
        notes: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action clockIn

        Args:
            team_id (string): team-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            onBehalfOfUserId (string): onBehalfOfUserId
            notes (string): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "isAtApprovedLocation": isAtApprovedLocation,
            "onBehalfOfUserId": onBehalfOfUserId,
            "notes": notes,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/clockIn"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_time_off_reasons(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List timeOffReasons

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffReasons"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_time_off_reasons(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        code: Optional[str] = None,
        displayName: Optional[str] = None,
        iconType: Optional[Any] = None,
        isActive: Optional[bool] = None,
    ) -> Any:
        """

        Create timeOffReason

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            code (string): The code of the timeOffReason to represent an external identifier. This field must be unique within the team in Microsoft Teams and uses an alphanumeric format, with a maximum of 100 characters.
            displayName (string): The name of the timeOffReason. Required.
            iconType (string): Supported icon types are: none, car, calendar, running, plane, firstAid, doctor, notWorking, clock, juryDuty, globe, cup, phone, weather, umbrella, piggyBank, dog, cake, trafficCone, pin, sunny. Required.
            isActive (boolean): Indicates whether the timeOffReason can be used when creating new entities or updating existing ones. Required.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "code": code,
            "displayName": displayName,
            "iconType": iconType,
            "isActive": isActive,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffReasons"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_time_off_reason_by_id(
        self,
        team_id: str,
        timeOffReason_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeOffReason

        Args:
            team_id (string): team-id
            timeOffReason_id (string): timeOffReason-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffReason_id is None:
            raise ValueError("Missing required parameter 'timeOffReason-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_time_off_reason_by_id(
        self,
        team_id: str,
        timeOffReason_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        code: Optional[str] = None,
        displayName: Optional[str] = None,
        iconType: Optional[Any] = None,
        isActive: Optional[bool] = None,
    ) -> Any:
        """

        Replace timeOffReason

        Args:
            team_id (string): team-id
            timeOffReason_id (string): timeOffReason-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            code (string): The code of the timeOffReason to represent an external identifier. This field must be unique within the team in Microsoft Teams and uses an alphanumeric format, with a maximum of 100 characters.
            displayName (string): The name of the timeOffReason. Required.
            iconType (string): Supported icon types are: none, car, calendar, running, plane, firstAid, doctor, notWorking, clock, juryDuty, globe, cup, phone, weather, umbrella, piggyBank, dog, cake, trafficCone, pin, sunny. Required.
            isActive (boolean): Indicates whether the timeOffReason can be used when creating new entities or updating existing ones. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffReason_id is None:
            raise ValueError("Missing required parameter 'timeOffReason-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "code": code,
            "displayName": displayName,
            "iconType": iconType,
            "isActive": isActive,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_time_off_reason_by_id(self, team_id: str, timeOffReason_id: str) -> Any:
        """

        Delete timeOffReason

        Args:
            team_id (string): team-id
            timeOffReason_id (string): timeOffReason-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffReason_id is None:
            raise ValueError("Missing required parameter 'timeOffReason-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_time_off_reasons_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffReasons/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_time_off_requests(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List timeOffRequest

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffRequests"
        )
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_time_off_request(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[Any] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[Any] = None,
        endDateTime: Optional[str] = None,
        startDateTime: Optional[str] = None,
        timeOffReasonId: Optional[str] = None,
    ) -> Any:
        """

        Create timeOffRequest

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): Indicates who the request is assigned to. Possible values are: sender, recipient, manager, system, unknownFutureValue.
            managerActionDateTime (string): The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            managerActionMessage (string): The message sent by the manager regarding the scheduleChangeRequest. Optional.
            managerUserId (string): The user ID of the manager who approved or declined the scheduleChangeRequest.
            senderDateTime (string): The date and time when the sender sent the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            senderMessage (string): The message sent by the sender of the scheduleChangeRequest. Optional.
            senderUserId (string): The user ID of the sender of the scheduleChangeRequest.
            state (string): The state of the scheduleChangeRequest. Possible values are: pending, approved, declined, unknownFutureValue.
            endDateTime (string): The date and time the time off ends in ISO 8601 format and in UTC time.
            startDateTime (string): The date and time the time off starts in ISO 8601 format and in UTC time.
            timeOffReasonId (string): The reason for the time off.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "assignedTo": assignedTo,
            "managerActionDateTime": managerActionDateTime,
            "managerActionMessage": managerActionMessage,
            "managerUserId": managerUserId,
            "senderDateTime": senderDateTime,
            "senderMessage": senderMessage,
            "senderUserId": senderUserId,
            "state": state,
            "endDateTime": endDateTime,
            "startDateTime": startDateTime,
            "timeOffReasonId": timeOffReasonId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffRequests"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_time_off_request_details(
        self,
        team_id: str,
        timeOffRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeOffRequest

        Args:
            team_id (string): team-id
            timeOffRequest_id (string): timeOffRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffRequest_id is None:
            raise ValueError("Missing required parameter 'timeOffRequest-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_time_off_request(
        self,
        team_id: str,
        timeOffRequest_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[Any] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[Any] = None,
        endDateTime: Optional[str] = None,
        startDateTime: Optional[str] = None,
        timeOffReasonId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property timeOffRequests in teams

        Args:
            team_id (string): team-id
            timeOffRequest_id (string): timeOffRequest-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): Indicates who the request is assigned to. Possible values are: sender, recipient, manager, system, unknownFutureValue.
            managerActionDateTime (string): The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            managerActionMessage (string): The message sent by the manager regarding the scheduleChangeRequest. Optional.
            managerUserId (string): The user ID of the manager who approved or declined the scheduleChangeRequest.
            senderDateTime (string): The date and time when the sender sent the scheduleChangeRequest. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            senderMessage (string): The message sent by the sender of the scheduleChangeRequest. Optional.
            senderUserId (string): The user ID of the sender of the scheduleChangeRequest.
            state (string): The state of the scheduleChangeRequest. Possible values are: pending, approved, declined, unknownFutureValue.
            endDateTime (string): The date and time the time off ends in ISO 8601 format and in UTC time.
            startDateTime (string): The date and time the time off starts in ISO 8601 format and in UTC time.
            timeOffReasonId (string): The reason for the time off.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffRequest_id is None:
            raise ValueError("Missing required parameter 'timeOffRequest-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "assignedTo": assignedTo,
            "managerActionDateTime": managerActionDateTime,
            "managerActionMessage": managerActionMessage,
            "managerUserId": managerUserId,
            "senderDateTime": senderDateTime,
            "senderMessage": senderMessage,
            "senderUserId": senderUserId,
            "state": state,
            "endDateTime": endDateTime,
            "startDateTime": startDateTime,
            "timeOffReasonId": timeOffReasonId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_team_time_off_request(self, team_id: str, timeOffRequest_id: str) -> Any:
        """

        Delete timeOffRequest

        Args:
            team_id (string): team-id
            timeOffRequest_id (string): timeOffRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffRequest_id is None:
            raise ValueError("Missing required parameter 'timeOffRequest-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_time_off_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeOffRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_list_times_off(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List timesOff

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timesOff"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_create_times_off(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        draftTimeOff: Optional[Any] = None,
        isStagedForDeletion: Optional[bool] = None,
        sharedTimeOff: Optional[Any] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Create timeOff

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftTimeOff (string): The draft version of this timeOff item that is viewable by managers. It must be shared before it's visible to team members. Required.
            isStagedForDeletion (boolean): The timeOff is marked for deletion, a process that is finalized when the schedule is shared.
            sharedTimeOff (string): The shared version of this timeOff that is viewable by both employees and managers. Updates to the sharedTimeOff property send notifications to users in the Teams client. Required.
            userId (string): ID of the user assigned to the timeOff. Required.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "draftTimeOff": draftTimeOff,
            "isStagedForDeletion": isStagedForDeletion,
            "sharedTimeOff": sharedTimeOff,
            "userId": userId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timesOff"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_schedule_get_times_off(
        self,
        team_id: str,
        timeOff_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeOff

        Args:
            team_id (string): team-id
            timeOff_id (string): timeOff-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOff_id is None:
            raise ValueError("Missing required parameter 'timeOff-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timesOff/{timeOff_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_schedule_update_times_off(
        self,
        team_id: str,
        timeOff_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        draftTimeOff: Optional[Any] = None,
        isStagedForDeletion: Optional[bool] = None,
        sharedTimeOff: Optional[Any] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Replace timeOff

        Args:
            team_id (string): team-id
            timeOff_id (string): timeOff-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftTimeOff (string): The draft version of this timeOff item that is viewable by managers. It must be shared before it's visible to team members. Required.
            isStagedForDeletion (boolean): The timeOff is marked for deletion, a process that is finalized when the schedule is shared.
            sharedTimeOff (string): The shared version of this timeOff that is viewable by both employees and managers. Updates to the sharedTimeOff property send notifications to users in the Teams client. Required.
            userId (string): ID of the user assigned to the timeOff. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOff_id is None:
            raise ValueError("Missing required parameter 'timeOff-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "draftTimeOff": draftTimeOff,
            "isStagedForDeletion": isStagedForDeletion,
            "sharedTimeOff": sharedTimeOff,
            "userId": userId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timesOff/{timeOff_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_schedule_delete_times_off(self, team_id: str, timeOff_id: str) -> Any:
        """

        Delete timeOff

        Args:
            team_id (string): team-id
            timeOff_id (string): timeOff-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOff_id is None:
            raise ValueError("Missing required parameter 'timeOff-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timesOff/{timeOff_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_schedule_times_off_count(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.schedule
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timesOff/$count"
        )
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_list_tags(
        self,
        team_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List teamworkTags

        Args:
            team_id (string): team-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_create_tags(
        self,
        team_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        memberCount: Optional[float] = None,
        tagType: Optional[Any] = None,
        teamId: Optional[str] = None,
        members: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create teamworkTag

        Args:
            team_id (string): team-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            description (string): The description of the tag as it appears to the user in Microsoft Teams. A teamworkTag can't have more than 200 teamworkTagMembers.
            displayName (string): The name of the tag as it appears to the user in Microsoft Teams.
            memberCount (number): The number of users assigned to the tag.
            tagType (string): The type of the tag. Default is standard.
            teamId (string): ID of the team in which the tag is defined.
            members (array): Users assigned to the tag.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "description": description,
            "displayName": displayName,
            "memberCount": memberCount,
            "tagType": tagType,
            "teamId": teamId,
            "members": members,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_get_tags(
        self,
        team_id: str,
        teamworkTag_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamworkTag

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_update_tags(
        self,
        team_id: str,
        teamworkTag_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        memberCount: Optional[float] = None,
        tagType: Optional[Any] = None,
        teamId: Optional[str] = None,
        members: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update teamworkTag

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            description (string): The description of the tag as it appears to the user in Microsoft Teams. A teamworkTag can't have more than 200 teamworkTagMembers.
            displayName (string): The name of the tag as it appears to the user in Microsoft Teams.
            memberCount (number): The number of users assigned to the tag.
            tagType (string): The type of the tag. Default is standard.
            teamId (string): ID of the team in which the tag is defined.
            members (array): Users assigned to the tag.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "description": description,
            "displayName": displayName,
            "memberCount": memberCount,
            "tagType": tagType,
            "teamId": teamId,
            "members": members,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_delete_tags(self, team_id: str, teamworkTag_id: str) -> Any:
        """

        Delete teamworkTag

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_tags_list_members(
        self,
        team_id: str,
        teamworkTag_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        List members in a teamworkTag

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}/members"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_tags_create_members(
        self,
        team_id: str,
        teamworkTag_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Create teamworkTagMember

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The member's display name.
            tenantId (string): The ID of the tenant that the tag member is a part of.
            userId (string): The user ID of the member.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "tenantId": tenantId,
            "userId": userId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_tags_get_members(
        self,
        team_id: str,
        teamworkTag_id: str,
        teamworkTagMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamworkTagMember

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            teamworkTagMember_id (string): teamworkTagMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        if teamworkTagMember_id is None:
            raise ValueError("Missing required parameter 'teamworkTagMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_tags_update_members(
        self,
        team_id: str,
        teamworkTag_id: str,
        teamworkTagMember_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in teams

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            teamworkTagMember_id (string): teamworkTagMember-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The member's display name.
            tenantId (string): The ID of the tenant that the tag member is a part of.
            userId (string): The user ID of the member.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        if teamworkTagMember_id is None:
            raise ValueError("Missing required parameter 'teamworkTagMember-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "tenantId": tenantId,
            "userId": userId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def teams_tags_delete_members(
        self, team_id: str, teamworkTag_id: str, teamworkTagMember_id: str
    ) -> Any:
        """

        Delete teamworkTagMember

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            teamworkTagMember_id (string): teamworkTagMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        if teamworkTagMember_id is None:
            raise ValueError("Missing required parameter 'teamworkTagMember-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_tag_member_count(
        self,
        team_id: str,
        teamworkTag_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/{teamworkTag_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_tags_get_count_db(
        self, team_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamworkTag
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/tags/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_get_template(
        self,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get template from teams

        Args:
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.teamsTemplate
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/template"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_get_count_ff(
        self, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team
        """
        url = f"{self.main_app_client.base_url}/teams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_get_all_messages(
        self,
        model: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        select: Optional[List[str]] = None,
        orderby: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Invoke function getAllMessages

        Args:
            model (string): The payment model for the API
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            select (array): Select properties to be returned
            orderby (array): Order items by property values
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.team.Functions, important
        """
        url = f"{self.main_app_client.base_url}/teams/getAllMessages()"
        query_params = {
            k: v
            for k, v in [
                ("model", model),
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$select", select),
                ("$orderby", orderby),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.teams_list_installed_apps,
            self.teams_create_installed_apps,
            self.teams_get_installed_apps,
            self.teams_update_installed_apps,
            self.teams_delete_installed_apps,
            self.upgrade_teams_app_installation,
            self.get_teams_app_details,
            self.get_teams_app_definition,
            self.count_installed_apps,
            self.teams_team_list_team,
            self.teams_team_create_team,
            self.teams_team_get_team,
            self.teams_team_update_team,
            self.teams_team_delete_team,
            self.teams_list_all_channels,
            self.teams_get_all_channels,
            self.count_team_channels,
            self.teams_list_channels,
            self.teams_create_channels,
            self.teams_get_channels,
            self.teams_update_channels,
            self.teams_delete_channels,
            self.teams_channels_list_all_members,
            self.get_team_channel_members,
            self.teams_channels_get_all_members,
            self.update_member_details,
            self.delete_conversation_member,
            self.count_team_channel_members,
            self.add_channel_member,
            self.remove_team_channel_member,
            self.teams_channels_get_files_folder,
            self.get_files_folder_content,
            self.update_files_folder_content,
            self.delete_files_folder_content,
            self.teams_channels_list_members,
            self.teams_channels_create_members,
            self.teams_channels_get_members,
            self.teams_channels_update_members,
            self.teams_channels_delete_members,
            self.get_team_channel_members_count,
            self.add_channel_members_bulk,
            self.remove_member_from_channel,
            self.teams_channels_list_messages,
            self.teams_channels_create_messages,
            self.teams_channels_get_messages,
            self.teams_channels_update_messages,
            self.teams_channels_delete_messages,
            self.list_channel_msg_hosted_content,
            self.add_hosted_content,
            self.get_hosted_content_details,
            self.update_hosted_content_details,
            self.del_ch_msg_hosted_content,
            self.get_channel_msg_hosted_content_val,
            self.update_team_hosted_content_val,
            self.delete_hosted_content_by_message_id,
            self.get_hosted_content_count,
            self.set_reaction_to_message,
            self.soft_delete_message,
            self.undo_soft_delete_message,
            self.unset_reaction_to_message,
            self.list_channel_message_replies,
            self.create_channel_message_reply,
            self.get_replies_by_message_id,
            self.update_reply_message,
            self.delete_message_reply,
            self.get_hosted_content_replies,
            self.create_hosted_content_reply,
            self.get_channel_reply_hosted_content,
            self.patch_ch_reply_hosted_content,
            self.del_ch_msg_reply_hosted_content,
            self.get_ch_msg_reply_hosted_content_val,
            self.update_msg_reply_hosted_content,
            self.delete_hosted_content_value,
            self.count_ch_msg_reply_host_contents,
            self.set_reaction_to_reply,
            self.soft_delete_reply,
            self.undo_soft_delete_reply,
            self.unset_reaction,
            self.count_replies,
            self.get_chat_message_replies_delta,
            self.count_channel_messages,
            self.get_team_channel_messages_delta,
            self.archive_team_channel,
            self.complete_team_channel_migration,
            self.check_user_channel_access,
            self.provision_team_email,
            self.remove_team_channel_email,
            self.unarchive_channel,
            self.list_channel_shared_teams,
            self.share_channel_with_team,
            self.get_shared_teams_channels_info,
            self.update_shared_with_team_info,
            self.delete_shared_team_channel,
            self.get_shared_channel_members,
            self.get_shared_team_members,
            self.count_allowed_members,
            self.get_shared_channel_team_info,
            self.get_shared_teams_count,
            self.teams_channels_list_tabs,
            self.teams_channels_create_tabs,
            self.teams_channels_get_tabs,
            self.teams_channels_update_tabs,
            self.teams_channels_delete_tabs,
            self.get_teams_app_tab,
            self.get_team_channel_tabs_count,
            self.teams_channels_get_count_a,
            self.get_team_channel_messages,
            self.get_retained_messages_by_team_id,
            self.teams_get_group,
            self.list_service_provisioning_errors,
            self.count_service_provisioning_errors,
            self.teams_list_incoming_channels,
            self.teams_get_incoming_channels,
            self.count_team_incoming_channels,
            self.teams_list_members,
            self.teams_create_members,
            self.teams_get_members,
            self.teams_update_members,
            self.teams_delete_members,
            self.teams_members_get_count_b,
            self.teams_team_members_add,
            self.teams_team_members_remove,
            self.teams_team_archive,
            self.teams_team_clone,
            self.teams_team_complete_migration,
            self.send_team_notification,
            self.teams_team_unarchive,
            self.teams_list_operations,
            self.teams_create_operations,
            self.teams_get_operations,
            self.teams_update_operations,
            self.teams_delete_operations,
            self.teams_operations_get_count_af,
            self.teams_list_permission_grants,
            self.teams_create_permission_grants,
            self.teams_get_permission_grants,
            self.teams_update_permission_grants,
            self.teams_delete_permission_grants,
            self.count_team_permission_grants,
            self.teams_get_photo,
            self.teams_update_photo,
            self.teams_get_photo_content,
            self.teams_update_photo_content,
            self.teams_delete_photo_content,
            self.teams_get_primary_channel,
            self.teams_update_primary_channel,
            self.teams_delete_primary_channel,
            self.list_team_primary_channel_members,
            self.add_team_primary_channel_members,
            self.get_team_primary_channel_members,
            self.update_primary_channel_members,
            self.remove_conversation_member,
            self.count_team_primary_channel_members,
            self.add_team_members_bulk,
            self.remove_primary_channel_member,
            self.get_files_folder,
            self.get_team_primary_channel_content,
            self.upload_team_folder_content,
            self.delete_team_files_folder_content,
            self.list_primary_channel_members,
            self.add_primary_channel_member,
            self.get_team_members,
            self.update_team_member,
            self.delete_team_primary_channel_member,
            self.get_primary_channel_member_count,
            self.add_team_primary_channel_member,
            self.remove_team_member,
            self.list_team_primary_channel_messages,
            self.create_team_message,
            self.get_team_primary_channel_messages,
            self.update_primary_channel_message,
            self.delete_message_by_id,
            self.get_team_channel_msg_hosted,
            self.upload_hosted_content,
            self.read_hosted_content,
            self.patch_pri_ch_hosted_content,
            self.del_pri_ch_msg_hosted_content,
            self.get_hosted_message_content_by_id,
            self.put_pri_ch_hosted_content_val,
            self.del_pri_ch_msg_host_content_val,
            self.get_hosted_contents_count,
            self.set_reaction_to_chat_message,
            self.soft_delete_chat_message,
            self.restore_primary_channel_message,
            self.unset_reaction_message,
            self.list_replies_by_message_id,
            self.create_reply_to_chat_message,
            self.get_primary_channel_replies,
            self.update_primary_channel_reply,
            self.delete_reply,
            self.get_reply_contents,
            self.create_team_reply_hosted_content,
            self.get_pri_ch_reply_hosted_content,
            self.patch_pri_ch_reply_hosted_content,
            self.del_pri_ch_reply_hosted_content,
            self.get_pri_ch_reply_host_content_val,
            self.put_pri_ch_reply_hosted_content_val,
            self.del_pri_ch_reply_host_cont_val,
            self.count_hosted_content_replies,
            self.set_reaction_to_reply_message,
            self.delete_reply_message,
            self.undo_team_message_reply_delete,
            self.unset_team_message_reply_reaction,
            self.get_primary_channel_replies_count,
            self.get_reply_delta,
            self.get_primary_channel_message_count,
            self.get_primary_channel_messages_delta,
            self.archive_primary_channel,
            self.complete_team_migration,
            self.has_primary_channel_access,
            self.provision_team_channel_email,
            self.remove_team_primary_channel_email,
            self.unarchive_primary_channel,
            self.list_primary_channel_shared_teams,
            self.share_primary_channel_with_teams,
            self.get_shared_channel_info_by_id,
            self.update_shared_channel_team_info,
            self.delete_shared_channel_team_info,
            self.get_shared_members,
            self.get_team_channel_shared_member_by_id,
            self.get_shared_team_members_count,
            self.get_shared_with_team_info,
            self.get_shared_team_count,
            self.teams_primary_channel_list_tabs,
            self.create_team_tab,
            self.teams_primary_channel_get_tabs,
            self.update_team_tab,
            self.delete_primary_channel_tab,
            self.get_teams_app_by_tab_id,
            self.get_team_primary_channel_tabs_count,
            self.teams_get_schedule,
            self.teams_set_schedule,
            self.teams_delete_schedule,
            self.teams_schedule_list_day_notes,
            self.teams_schedule_create_day_notes,
            self.teams_schedule_get_day_notes,
            self.teams_schedule_update_day_notes,
            self.teams_schedule_delete_day_notes,
            self.get_day_notes_count,
            self.teams_team_schedule_share,
            self.get_team_shift_requests,
            self.offer_shift_requests,
            self.get_team_schedule_offer_shifts,
            self.patch_offer_shift_request,
            self.delete_shift_offer_request,
            self.count_shift_offer_requests,
            self.get_open_shift_change_requests,
            self.create_open_shift_change_request,
            self.get_open_shift_change_request,
            self.update_open_shift_change_request,
            self.delete_open_shift_change_request,
            self.count_open_shift_change_requests,
            self.teams_schedule_list_open_shifts,
            self.create_open_shifts,
            self.teams_schedule_get_open_shifts,
            self.update_open_shift,
            self.delete_open_shift_by_id,
            self.count_open_shifts,
            self.get_scheduling_groups,
            self.create_scheduling_group,
            self.get_team_schedule_scheduling_group,
            self.update_scheduling_group,
            self.delete_scheduling_group,
            self.count_scheduling_groups,
            self.teams_schedule_list_shifts,
            self.teams_schedule_create_shifts,
            self.teams_schedule_get_shifts,
            self.teams_schedule_update_shifts,
            self.teams_schedule_delete_shifts,
            self.get_schedule_shifts_count_by_team_id,
            self.get_swap_shift_change_requests,
            self.swap_shift_requests,
            self.swap_shift_request_read,
            self.update_swap_shift_request,
            self.delete_swap_shifts_change_request,
            self.count_swap_shift_requests,
            self.teams_schedule_list_time_cards,
            self.teams_schedule_create_time_cards,
            self.teams_schedule_get_time_cards,
            self.teams_schedule_update_time_cards,
            self.teams_schedule_delete_time_cards,
            self.clock_out_time_card,
            self.confirm_time_card,
            self.end_team_break,
            self.start_time_card_break,
            self.get_team_schedule_count,
            self.clock_in_team_schedule,
            self.get_team_time_off_reasons,
            self.create_time_off_reasons,
            self.get_time_off_reason_by_id,
            self.update_time_off_reason_by_id,
            self.delete_time_off_reason_by_id,
            self.get_team_time_off_reasons_count,
            self.list_time_off_requests,
            self.create_time_off_request,
            self.get_team_time_off_request_details,
            self.update_time_off_request,
            self.delete_team_time_off_request,
            self.get_team_time_off_count,
            self.teams_schedule_list_times_off,
            self.teams_schedule_create_times_off,
            self.teams_schedule_get_times_off,
            self.teams_schedule_update_times_off,
            self.teams_schedule_delete_times_off,
            self.get_team_schedule_times_off_count,
            self.teams_list_tags,
            self.teams_create_tags,
            self.teams_get_tags,
            self.teams_update_tags,
            self.teams_delete_tags,
            self.teams_tags_list_members,
            self.teams_tags_create_members,
            self.teams_tags_get_members,
            self.teams_tags_update_members,
            self.teams_tags_delete_members,
            self.get_team_tag_member_count,
            self.teams_tags_get_count_db,
            self.teams_get_template,
            self.teams_get_count_ff,
            self.teams_get_all_messages,
        ]
