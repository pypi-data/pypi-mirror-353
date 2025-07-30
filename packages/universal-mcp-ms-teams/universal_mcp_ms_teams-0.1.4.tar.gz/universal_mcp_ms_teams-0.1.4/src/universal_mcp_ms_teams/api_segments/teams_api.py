from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class TeamsApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def list_teams(
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
            teams.team, important
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

    def create_team(
        self,
        id: Optional[str] = None,
        classification: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        firstChannelName: Optional[str] = None,
        funSettings: Optional[dict[str, dict[str, Any]]] = None,
        guestSettings: Optional[dict[str, dict[str, Any]]] = None,
        internalId: Optional[str] = None,
        isArchived: Optional[bool] = None,
        memberSettings: Optional[dict[str, dict[str, Any]]] = None,
        messagingSettings: Optional[dict[str, dict[str, Any]]] = None,
        specialization: Optional[str] = None,
        summary: Optional[dict[str, dict[str, Any]]] = None,
        tenantId: Optional[str] = None,
        visibility: Optional[str] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            classification (string): An optional label. Typically describes the data or business sensitivity of the team. Must match one of a preconfigured set in the tenant's directory.
            createdDateTime (string): Timestamp at which the team was created.
            description (string): An optional description for the team. Maximum length: 1,024 characters.
            displayName (string): The name of the team.
            firstChannelName (string): The name of the first channel in the team. This is an optional property, only used during team creation and isn't returned in methods to get and list teams.
            funSettings (object): funSettings
            guestSettings (object): guestSettings
            internalId (string): A unique ID for the team that was used in a few places such as the audit log/Office 365 Management Activity API.
            isArchived (boolean): Whether this team is in read-only mode.
            memberSettings (object): memberSettings
            messagingSettings (object): messagingSettings
            specialization (string): specialization
            summary (object): summary
            tenantId (string): The ID of the Microsoft Entra tenant.
            visibility (string): visibility
            webUrl (string): A hyperlink that goes to the team in the Microsoft Teams client. You get this URL when you right-click a team in the Microsoft Teams client and select Get link to team. This URL should be treated as an opaque blob, and not parsed.
            allChannels (array): List of channels either hosted in or shared with the team (incoming channels).
            channels (array): The collection of channels and messages associated with the team.
            group (string): group
            incomingChannels (array): List of channels shared with the team.
            installedApps (array): The apps installed in this team.
            members (array): Members and owners of the team.
            operations (array): The async operations that ran or are running on this team.
            permissionGrants (array): A collection of permissions granted to apps to access the team.
            photo (string): photo
            primaryChannel (string): primaryChannel
            schedule (string): schedule
            tags (array): The tags associated with the team.
            template (string): template

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

    def get_team_info(
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
            teams.team
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team(
        self,
        team_id: str,
        id: Optional[str] = None,
        classification: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        firstChannelName: Optional[str] = None,
        funSettings: Optional[dict[str, dict[str, Any]]] = None,
        guestSettings: Optional[dict[str, dict[str, Any]]] = None,
        internalId: Optional[str] = None,
        isArchived: Optional[bool] = None,
        memberSettings: Optional[dict[str, dict[str, Any]]] = None,
        messagingSettings: Optional[dict[str, dict[str, Any]]] = None,
        specialization: Optional[str] = None,
        summary: Optional[dict[str, dict[str, Any]]] = None,
        tenantId: Optional[str] = None,
        visibility: Optional[str] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            classification (string): An optional label. Typically describes the data or business sensitivity of the team. Must match one of a preconfigured set in the tenant's directory.
            createdDateTime (string): Timestamp at which the team was created.
            description (string): An optional description for the team. Maximum length: 1,024 characters.
            displayName (string): The name of the team.
            firstChannelName (string): The name of the first channel in the team. This is an optional property, only used during team creation and isn't returned in methods to get and list teams.
            funSettings (object): funSettings
            guestSettings (object): guestSettings
            internalId (string): A unique ID for the team that was used in a few places such as the audit log/Office 365 Management Activity API.
            isArchived (boolean): Whether this team is in read-only mode.
            memberSettings (object): memberSettings
            messagingSettings (object): messagingSettings
            specialization (string): specialization
            summary (object): summary
            tenantId (string): The ID of the Microsoft Entra tenant.
            visibility (string): visibility
            webUrl (string): A hyperlink that goes to the team in the Microsoft Teams client. You get this URL when you right-click a team in the Microsoft Teams client and select Get link to team. This URL should be treated as an opaque blob, and not parsed.
            allChannels (array): List of channels either hosted in or shared with the team (incoming channels).
            channels (array): The collection of channels and messages associated with the team.
            group (string): group
            incomingChannels (array): List of channels shared with the team.
            installedApps (array): The apps installed in this team.
            members (array): Members and owners of the team.
            operations (array): The async operations that ran or are running on this team.
            permissionGrants (array): A collection of permissions granted to apps to access the team.
            photo (string): photo
            primaryChannel (string): primaryChannel
            schedule (string): schedule
            tags (array): The tags associated with the team.
            template (string): template

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

    def delete_team_entity(self, team_id: str) -> Any:
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

    def list_all_team_channels(
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

    def get_team_channels(
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

    def get_team_all_channels_count(
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

    def list_channels_for_team(
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

    def create_team_channel(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        email: Optional[str] = None,
        isArchived: Optional[bool] = None,
        isFavoriteByDefault: Optional[bool] = None,
        membershipType: Optional[str] = None,
        summary: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdDateTime (string): Read only. Timestamp at which the channel was created.
            description (string): Optional textual description for the channel.
            displayName (string): Channel name as it will appear to the user in Microsoft Teams. The maximum length is 50 characters.
            email (string): The email address for sending messages to the channel. Read-only.
            isArchived (boolean): Indicates whether the channel is archived. Read-only.
            isFavoriteByDefault (boolean): Indicates whether the channel should be marked as recommended for all members of the team to show in their channel list. Note: All recommended channels automatically show in the channels list for education and frontline worker users. The property can only be set programmatically via the Create team method. The default value is false.
            membershipType (string): membershipType
            summary (object): summary
            tenantId (string): The ID of the Microsoft Entra tenant.
            webUrl (string): A hyperlink that will go to the channel in Microsoft Teams. This is the URL that you get when you right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an opaque blob, and not parsed. Read-only.
            allMembers (array): A collection of membership records associated with the channel, including both direct and indirect members of shared channels.
            filesFolder (string): filesFolder
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

    def get_team_channel_info(
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

    def update_channel(
        self,
        team_id: str,
        channel_id: str,
        id: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        email: Optional[str] = None,
        isArchived: Optional[bool] = None,
        isFavoriteByDefault: Optional[bool] = None,
        membershipType: Optional[str] = None,
        summary: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdDateTime (string): Read only. Timestamp at which the channel was created.
            description (string): Optional textual description for the channel.
            displayName (string): Channel name as it will appear to the user in Microsoft Teams. The maximum length is 50 characters.
            email (string): The email address for sending messages to the channel. Read-only.
            isArchived (boolean): Indicates whether the channel is archived. Read-only.
            isFavoriteByDefault (boolean): Indicates whether the channel should be marked as recommended for all members of the team to show in their channel list. Note: All recommended channels automatically show in the channels list for education and frontline worker users. The property can only be set programmatically via the Create team method. The default value is false.
            membershipType (string): membershipType
            summary (object): summary
            tenantId (string): The ID of the Microsoft Entra tenant.
            webUrl (string): A hyperlink that will go to the channel in Microsoft Teams. This is the URL that you get when you right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an opaque blob, and not parsed. Read-only.
            allMembers (array): A collection of membership records associated with the channel, including both direct and indirect members of shared channels.
            filesFolder (string): filesFolder
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

    def delete_channel(self, team_id: str, channel_id: str) -> Any:
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

    def list_all_team_channel_members(
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

    def create_team_channel_members(
        self,
        team_id: str,
        channel_id: str,
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

    def get_team_channel_members_details(
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

    def update_conversation_member_in_team(
        self,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
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

    def delete_team_channel_member(
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

    def add_channel_members(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_channel_all_members(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/allMembers/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_channel_files_folder(
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

    def update_team_channel_file_content(
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

    def delete_team_channel_file_content(self, team_id: str, channel_id: str) -> Any:
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

    def list_channel_members_by_team_and_cha(
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

    def add_member_to_channel_teamwise(
        self,
        team_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Add member to channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
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

    def get_channel_member(
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

    def update_channel_member_by_id(
        self,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update member in channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
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

    def delete_conversation_member(
        self, team_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete conversationMember

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

    def get_member_count(
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

    def add_team_channel_member_action(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_member_action(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_channel_messages_by_id(
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

    def send_chat_message(
        self,
        team_id: str,
        channel_id: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, dict[str, Any]]]] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        channelIdentity: Optional[dict[str, dict[str, Any]]] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageHistory: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[dict[str, dict[str, Any]]] = None,
        reactions: Optional[List[dict[str, dict[str, Any]]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Send chatMessage in a channel or a chat

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (object): channelIdentity
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (object): eventDetail
            from_ (string): from
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (object): policyViolation
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

    def get_chat_message(
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

    def update_chat_message_by_team_channel(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, dict[str, Any]]]] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        channelIdentity: Optional[dict[str, dict[str, Any]]] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageHistory: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[dict[str, dict[str, Any]]] = None,
        reactions: Optional[List[dict[str, dict[str, Any]]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (object): channelIdentity
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (object): eventDetail
            from_ (string): from
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (object): policyViolation
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

    def delete_team_channel_message(
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

    def create_message_hosted_content(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
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

    def get_chat_message_hosted_content_by_i(
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

    def delete_channel_message_hosted_cont(
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

    def count_message_hosted_contents_by_me(
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

    def set_reaction_on_channel_message(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_chat_message(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def restore_team_channel_message(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_from_message(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_replies(
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
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, dict[str, Any]]]] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        channelIdentity: Optional[dict[str, dict[str, Any]]] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageHistory: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[dict[str, dict[str, Any]]] = None,
        reactions: Optional[List[dict[str, dict[str, Any]]]] = None,
        replyToId: Optional[str] = None,
        subject: Optional[str] = None,
        summary: Optional[str] = None,
        webUrl: Optional[str] = None,
        hostedContents: Optional[List[Any]] = None,
        replies: Optional[List[Any]] = None,
    ) -> Any:
        """

        Reply to a message in a channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (object): channelIdentity
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (object): eventDetail
            from_ (string): from
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (object): policyViolation
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

    def get_chat_message_reply(
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

    def update_message_reply(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, dict[str, Any]]]] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        channelIdentity: Optional[dict[str, dict[str, Any]]] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageHistory: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[dict[str, dict[str, Any]]] = None,
        reactions: Optional[List[dict[str, dict[str, Any]]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (object): channelIdentity
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (object): eventDetail
            from_ (string): from
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (object): policyViolation
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

    def delete_team_channel_message_reply_b(
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

    def list_reply_hosted_contents_by_messa(
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

    def create_hosted_content_link(
        self,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
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

    def delete_hosted_content_by_message_re(
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

    def add_reaction_to_reply(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_channel_message_reply_p(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_soft_delete_team_message_reply(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_message_reaction_reply(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.unsetReaction"
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

    def get_delta_replies_for_message(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/microsoft.graph.delta()"
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

    def get_team_channel_message_count(
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

    def delta_team_channel_messages(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/messages/microsoft.graph.delta()"
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

    def archive_channel_action(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/microsoft.graph.archive"
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def check_channel_user_access(
        self,
        team_id: str,
        channel_id: str,
        userId: Optional[str] = None,
        tenantId: Optional[str] = None,
        userPrincipalName: Optional[str] = None,
    ) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            userId (string): Usage: userId='@userId'
            tenantId (string): Usage: tenantId='@tenantId'
            userPrincipalName (string): Usage: userPrincipalName='@userPrincipalName'

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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/microsoft.graph.doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
        query_params = {
            k: v
            for k, v in [
                ("userId", userId),
                ("tenantId", tenantId),
                ("userPrincipalName", userPrincipalName),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def teams_channels_provision_email_pos(
        self, team_id: str, channel_id: str
    ) -> dict[str, Any]:
        """

        Invoke action provisionEmail

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
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/microsoft.graph.provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_channel_email_from_team(self, team_id: str, channel_id: str) -> Any:
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/microsoft.graph.removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_team_channel(self, team_id: str, channel_id: str) -> Any:
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/{channel_id}/microsoft.graph.unarchive"
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

    def delete_shared_team_channel_link(
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

    def list_channel_allowed_members_by_tea(
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

    def get_channel_allowed_member_by_id(
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

    def get_shared_team_members_count(
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

    def get_shared_team_channel_info(
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

    def count_shared_with_teams_in_channel(
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

    def get_channel_tabs(
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

    def add_channel_tab(
        self,
        team_id: str,
        channel_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Add tab to channel

        Args:
            team_id (string): team-id
            channel_id (string): channel-id
            id (string): The unique identifier for an entity. Read-only.
            configuration (object): configuration
            displayName (string): Name of the tab.
            webUrl (string): Deep link URL of the tab instance. Read only.
            teamsApp (string): teamsApp

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

    def get_team_tab_info(
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

    def update_tab_info(
        self,
        team_id: str,
        channel_id: str,
        teamsTab_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            configuration (object): configuration
            displayName (string): Name of the tab.
            webUrl (string): Deep link URL of the tab instance. Read only.
            teamsApp (string): teamsApp

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

    def delete_channel_tab_by_id(
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

    def get_teams_app_data(
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

    def count_team_channel_tabs(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/microsoft.graph.getAllMessages()"
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/channels/microsoft.graph.getAllRetainedMessages()"
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

    def get_team_group(
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

    def get_team_provisioning_errors_count(
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

    def get_incoming_team_channels(
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

    def get_incoming_channel_by_team_id(
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

    def get_team_incoming_channels_count(
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

    def get_team_apps(
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

    def add_team_app(
        self,
        team_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Add app to team

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (object): consentedPermissionSet
            teamsApp (string): teamsApp
            teamsAppDefinition (string): teamsAppDefinition

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

    def get_installed_team_app(
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

    def update_teams_installed_app_navigat(
        self,
        team_id: str,
        teamsAppInstallation_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property installedApps in teams

        Args:
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (object): consentedPermissionSet
            teamsApp (string): teamsApp
            teamsAppDefinition (string): teamsAppDefinition

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

    def remove_team_installed_app(
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

    def upgrade_team_app(
        self,
        team_id: str,
        teamsAppInstallation_id: str,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action upgrade

        Args:
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            consentedPermissionSet (object): consentedPermissionSet

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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/installedApps/{teamsAppInstallation_id}/microsoft.graph.upgrade"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_teams_app_detail(
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

    def get_app_definition(
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

    def get_installed_app_count(
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

    def get_team_members_list(
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

    def add_member_to_team(
        self,
        team_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Add member to team

        Args:
            team_id (string): team-id
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

    def get_team_member_details(
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

    def update_team_member_conversation_me(
        self,
        team_id: str,
        conversationMember_id: str,
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

    def remove_team_member_by_id(self, team_id: str, conversationMember_id: str) -> Any:
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

    def get_team_member_count(
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

    def add_team_members_by_graph_action(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_member_by_graph_action(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def team_archive_action(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/microsoft.graph.archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def clone_team_action(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/microsoft.graph.clone"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_team_migration_action(self, team_id: str) -> Any:
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_send_activity_notif(
        self,
        team_id: str,
        topic: Optional[dict[str, dict[str, Any]]] = None,
        activityType: Optional[str] = None,
        chainId: Optional[float] = None,
        previewText: Optional[dict[str, dict[str, Any]]] = None,
        teamsAppId: Optional[str] = None,
        templateParameters: Optional[List[dict[str, dict[str, Any]]]] = None,
        recipient: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action sendActivityNotification

        Args:
            team_id (string): team-id
            topic (object): topic
            activityType (string): activityType
            chainId (number): chainId
            previewText (object): previewText
            teamsAppId (string): teamsAppId
            templateParameters (array): templateParameters
            recipient (object): recipient

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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/microsoft.graph.sendActivityNotification"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_team_operation(self, team_id: str) -> Any:
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
        url = (
            f"{self.main_app_client.base_url}/teams/{team_id}/microsoft.graph.unarchive"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_operations_by_id(
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

    def create_team_operation(
        self,
        team_id: str,
        id: Optional[str] = None,
        attemptsCount: Optional[float] = None,
        createdDateTime: Optional[str] = None,
        error: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            attemptsCount (number): Number of times the operation was attempted before being marked successful or failed.
            createdDateTime (string): Time when the operation was created.
            error (object): error
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

    def get_teams_async_operation_by_id(
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

    def update_team_operation(
        self,
        team_id: str,
        teamsAsyncOperation_id: str,
        id: Optional[str] = None,
        attemptsCount: Optional[float] = None,
        createdDateTime: Optional[str] = None,
        error: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            attemptsCount (number): Number of times the operation was attempted before being marked successful or failed.
            createdDateTime (string): Time when the operation was created.
            error (object): error
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

    def delete_teams_async_operation_for_te(
        self, team_id: str, teamsAsyncOperation_id: str
    ) -> Any:
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

    def get_team_operation_count(
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

    def list_team_permission_grants(
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

    def create_team_permission_grant(
        self,
        team_id: str,
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

    def get_permission_grant_by_team_resour(
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

    def update_team_permission_grants(
        self,
        team_id: str,
        resourceSpecificPermissionGrant_id: str,
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

    def delete_team_permission_grant(
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

    def count_permission_grants(
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

    def get_team_profile_photo(
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

    def update_team_photo(
        self,
        team_id: str,
        id: Optional[str] = None,
        height: Optional[float] = None,
        width: Optional[float] = None,
    ) -> Any:
        """

        Update profilePhoto

        Args:
            team_id (string): team-id
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
        request_body_data = {"id": id, "height": height, "width": width}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/photo"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def get_profile_photo(self, team_id: str) -> Any:
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

    def update_team_photo_content(self, team_id: str, body_content: bytes) -> Any:
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

    def delete_team_photo_content(self, team_id: str) -> Any:
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

    def get_primary_team_channel(
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

    def update_team_primary_channel(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        email: Optional[str] = None,
        isArchived: Optional[bool] = None,
        isFavoriteByDefault: Optional[bool] = None,
        membershipType: Optional[str] = None,
        summary: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdDateTime (string): Read only. Timestamp at which the channel was created.
            description (string): Optional textual description for the channel.
            displayName (string): Channel name as it will appear to the user in Microsoft Teams. The maximum length is 50 characters.
            email (string): The email address for sending messages to the channel. Read-only.
            isArchived (boolean): Indicates whether the channel is archived. Read-only.
            isFavoriteByDefault (boolean): Indicates whether the channel should be marked as recommended for all members of the team to show in their channel list. Note: All recommended channels automatically show in the channels list for education and frontline worker users. The property can only be set programmatically via the Create team method. The default value is false.
            membershipType (string): membershipType
            summary (object): summary
            tenantId (string): The ID of the Microsoft Entra tenant.
            webUrl (string): A hyperlink that will go to the channel in Microsoft Teams. This is the URL that you get when you right-click a channel in Microsoft Teams and select Get link to channel. This URL should be treated as an opaque blob, and not parsed. Read-only.
            allMembers (array): A collection of membership records associated with the channel, including both direct and indirect members of shared channels.
            filesFolder (string): filesFolder
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

    def delete_team_primary_channel(self, team_id: str) -> Any:
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
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to allMembers for teams

        Args:
            team_id (string): team-id
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

    def add_primary_channel_all_members_act(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_members(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/allMembers/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_files_folder(
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

    def get_team_primary_members(
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

    def add_team_channel_members(
        self,
        team_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for teams

        Args:
            team_id (string): team-id
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

    def get_team_primary_channel_member_by_i(
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

    def update_conversation_member_by_id(
        self,
        team_id: str,
        conversationMember_id: str,
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

    def get_team_primary_channel_member_cou(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_primary_channel_member(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/members/microsoft.graph.remove"
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
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, dict[str, Any]]]] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        channelIdentity: Optional[dict[str, dict[str, Any]]] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageHistory: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[dict[str, dict[str, Any]]] = None,
        reactions: Optional[List[dict[str, dict[str, Any]]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (object): channelIdentity
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (object): eventDetail
            from_ (string): from
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (object): policyViolation
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

    def get_team_primary_messages(
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

    def patch_team_message_by_id(
        self,
        team_id: str,
        chatMessage_id: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, dict[str, Any]]]] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        channelIdentity: Optional[dict[str, dict[str, Any]]] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageHistory: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[dict[str, dict[str, Any]]] = None,
        reactions: Optional[List[dict[str, dict[str, Any]]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (object): channelIdentity
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (object): eventDetail
            from_ (string): from
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (object): policyViolation
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
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for teams

        Args:
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
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

    def set_reaction_to_primary_channel_mes(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_team_channel_message(
        self, team_id: str, chatMessage_id: str
    ) -> Any:
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def teams_undo_soft_delete_message(self, team_id: str, chatMessage_id: str) -> Any:
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_by_message_id(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/microsoft.graph.unsetReaction"
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
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, dict[str, Any]]]] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        channelIdentity: Optional[dict[str, dict[str, Any]]] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageHistory: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[dict[str, dict[str, Any]]] = None,
        reactions: Optional[List[dict[str, dict[str, Any]]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (object): channelIdentity
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (object): eventDetail
            from_ (string): from
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (object): policyViolation
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

    def get_team_primary_channel_message_re(
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

    def update_reply(
        self,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        id: Optional[str] = None,
        attachments: Optional[List[dict[str, dict[str, Any]]]] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        channelIdentity: Optional[dict[str, dict[str, Any]]] = None,
        chatId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        etag: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        importance: Optional[str] = None,
        lastEditedDateTime: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        locale: Optional[str] = None,
        mentions: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageHistory: Optional[List[dict[str, dict[str, Any]]]] = None,
        messageType: Optional[str] = None,
        policyViolation: Optional[dict[str, dict[str, Any]]] = None,
        reactions: Optional[List[dict[str, dict[str, Any]]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            attachments (array): References to attached objects like files, tabs, meetings etc.
            body (object): body
            channelIdentity (object): channelIdentity
            chatId (string): If the message was sent in a chat, represents the identity of the chat.
            createdDateTime (string): Timestamp of when the chat message was created.
            deletedDateTime (string): Read only. Timestamp at which the chat message was deleted, or null if not deleted.
            etag (string): Read-only. Version number of the chat message.
            eventDetail (object): eventDetail
            from_ (string): from
            importance (string): importance
            lastEditedDateTime (string): Read only. Timestamp when edits to the chat message were made. Triggers an 'Edited' flag in the Teams UI. If no edits are made the value is null.
            lastModifiedDateTime (string): Read only. Timestamp when the chat message is created (initial setting) or modified, including when a reaction is added or removed.
            locale (string): Locale of the chat message set by the client. Always set to en-us.
            mentions (array): List of entities mentioned in the chat message. Supported entities are: user, bot, team, channel, chat, and tag.
            messageHistory (array): List of activity history of a message item, including modification time and actions, such as reactionAdded, reactionRemoved, or reaction changes, on the message.
            messageType (string): messageType
            policyViolation (object): policyViolation
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

    def list_team_reply_hosted_contents_by_i(
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

    def set_reaction_to_reply(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_reply_message(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_reply_soft_delete(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reply_reaction(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.unsetReaction"
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

    def get_delta_replies(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/microsoft.graph.delta()"
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

    def list_primary_channel_messages(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/messages/microsoft.graph.delta()"
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

    def archive_team_primary_channel(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/microsoft.graph.archive"
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def check_user_access_in_channel(
        self,
        team_id: str,
        userId: Optional[str] = None,
        tenantId: Optional[str] = None,
        userPrincipalName: Optional[str] = None,
    ) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            team_id (string): team-id
            userId (string): Usage: userId='@userId'
            tenantId (string): Usage: tenantId='@tenantId'
            userPrincipalName (string): Usage: userPrincipalName='@userPrincipalName'

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teams.channel
        """
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/microsoft.graph.doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
        query_params = {
            k: v
            for k, v in [
                ("userId", userId),
                ("tenantId", tenantId),
                ("userPrincipalName", userPrincipalName),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def provision_team_email(self, team_id: str) -> dict[str, Any]:
        """

        Invoke action provisionEmail

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
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/microsoft.graph.provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_primary_team_email(self, team_id: str) -> Any:
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/microsoft.graph.removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_team_primary_channel(self, team_id: str) -> Any:
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/primaryChannel/microsoft.graph.unarchive"
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

    def remove_shared_with_team(
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

    def count_shared_team_members(
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

    def get_shared_channel_team_info_team(
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

    def get_primary_channel_shared_with_tea(
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

    def get_team_tabs(
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
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to tabs for teams

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            configuration (object): configuration
            displayName (string): Name of the tab.
            webUrl (string): Deep link URL of the tab instance. Read only.
            teamsApp (string): teamsApp

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

    def get_team_primary_tabs(
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
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property tabs in teams

        Args:
            team_id (string): team-id
            teamsTab_id (string): teamsTab-id
            id (string): The unique identifier for an entity. Read-only.
            configuration (object): configuration
            displayName (string): Name of the tab.
            webUrl (string): Deep link URL of the tab instance. Read only.
            teamsApp (string): teamsApp

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

    def delete_team_tab(self, team_id: str, teamsTab_id: str) -> Any:
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

    def get_team_schedule(
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

    def update_team_schedule(
        self,
        team_id: str,
        id: Optional[str] = None,
        enabled: Optional[bool] = None,
        isActivitiesIncludedWhenCopyingShiftsEnabled: Optional[bool] = None,
        offerShiftRequestsEnabled: Optional[bool] = None,
        openShiftsEnabled: Optional[bool] = None,
        provisionStatus: Optional[str] = None,
        provisionStatusCode: Optional[str] = None,
        startDayOfWeek: Optional[str] = None,
        swapShiftsRequestsEnabled: Optional[bool] = None,
        timeClockEnabled: Optional[bool] = None,
        timeClockSettings: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            enabled (boolean): Indicates whether the schedule is enabled for the team. Required.
            isActivitiesIncludedWhenCopyingShiftsEnabled (boolean): Indicates whether copied shifts include activities from the original shift.
            offerShiftRequestsEnabled (boolean): Indicates whether offer shift requests are enabled for the schedule.
            openShiftsEnabled (boolean): Indicates whether open shifts are enabled for the schedule.
            provisionStatus (string): provisionStatus
            provisionStatusCode (string): Additional information about why schedule provisioning failed.
            startDayOfWeek (string): startDayOfWeek
            swapShiftsRequestsEnabled (boolean): Indicates whether swap shifts requests are enabled for the schedule.
            timeClockEnabled (boolean): Indicates whether time clock is enabled for the schedule.
            timeClockSettings (object): timeClockSettings
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

    def delete_team_schedule(self, team_id: str) -> Any:
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

    def get_team_day_notes(
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

    def create_team_schedule_day_note(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        dayNoteDate: Optional[str] = None,
        draftDayNote: Optional[dict[str, dict[str, Any]]] = None,
        sharedDayNote: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Create new navigation property to dayNotes for teams

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            dayNoteDate (string): The date of the day note.
            draftDayNote (object): draftDayNote
            sharedDayNote (object): sharedDayNote

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

    def get_team_schedule_day_note(
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

    def update_team_day_note(
        self,
        team_id: str,
        dayNote_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        dayNoteDate: Optional[str] = None,
        draftDayNote: Optional[dict[str, dict[str, Any]]] = None,
        sharedDayNote: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Update the navigation property dayNotes in teams

        Args:
            team_id (string): team-id
            dayNote_id (string): dayNote-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            dayNoteDate (string): The date of the day note.
            draftDayNote (object): draftDayNote
            sharedDayNote (object): sharedDayNote

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

    def delete_team_day_note(self, team_id: str, dayNote_id: str) -> Any:
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

    def get_team_schedule_day_notes_count(
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

    def share_team_schedule_action(
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/microsoft.graph.share"
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
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[str] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[str] = None,
        recipientActionDateTime: Optional[str] = None,
        recipientActionMessage: Optional[str] = None,
        recipientUserId: Optional[str] = None,
        senderShiftId: Optional[str] = None,
    ) -> Any:
        """

        Create offerShiftRequest

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): assignedTo
            managerActionDateTime (string): managerActionDateTime
            managerActionMessage (string): managerActionMessage
            managerUserId (string): managerUserId
            senderDateTime (string): senderDateTime
            senderMessage (string): senderMessage
            senderUserId (string): senderUserId
            state (string): state
            recipientActionDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            recipientActionMessage (string): Custom message sent by recipient of the offer shift request.
            recipientUserId (string): User ID of the recipient of the offer shift request.
            senderShiftId (string): User ID of the sender of the offer shift request.

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
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[str] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[str] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): assignedTo
            managerActionDateTime (string): managerActionDateTime
            managerActionMessage (string): managerActionMessage
            managerUserId (string): managerUserId
            senderDateTime (string): senderDateTime
            senderMessage (string): senderMessage
            senderUserId (string): senderUserId
            state (string): state
            recipientActionDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            recipientActionMessage (string): Custom message sent by recipient of the offer shift request.
            recipientUserId (string): User ID of the recipient of the offer shift request.
            senderShiftId (string): User ID of the sender of the offer shift request.

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

    def get_team_open_shift_requests(
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

    def create_open_shift_change_requests(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[str] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[str] = None,
        openShiftId: Optional[str] = None,
    ) -> Any:
        """

        Create openShiftChangeRequest

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): assignedTo
            managerActionDateTime (string): managerActionDateTime
            managerActionMessage (string): managerActionMessage
            managerUserId (string): managerUserId
            senderDateTime (string): senderDateTime
            senderMessage (string): senderMessage
            senderUserId (string): senderUserId
            state (string): state
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

    def get_open_shift_change_request_by_id(
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

    def patch_open_shift_change_request_by_i(
        self,
        team_id: str,
        openShiftChangeRequest_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[str] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[str] = None,
        openShiftId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property openShiftChangeRequests in teams

        Args:
            team_id (string): team-id
            openShiftChangeRequest_id (string): openShiftChangeRequest-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): assignedTo
            managerActionDateTime (string): managerActionDateTime
            managerActionMessage (string): managerActionMessage
            managerUserId (string): managerUserId
            senderDateTime (string): senderDateTime
            senderMessage (string): senderMessage
            senderUserId (string): senderUserId
            state (string): state
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

    def remove_open_shift_change_request(
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

    def list_team_open_shifts(
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

    def create_open_shift_for_team_schedule(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftOpenShift (string): draftOpenShift
            isStagedForDeletion (boolean): The openShift is marked for deletion, a process that is finalized when the schedule is shared.
            schedulingGroupId (string): The ID of the schedulingGroup that contains the openShift.
            sharedOpenShift (string): sharedOpenShift

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

    def get_open_shift_by_team_id(
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

    def update_open_shift_details(
        self,
        team_id: str,
        openShift_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftOpenShift (string): draftOpenShift
            isStagedForDeletion (boolean): The openShift is marked for deletion, a process that is finalized when the schedule is shared.
            schedulingGroupId (string): The ID of the schedulingGroup that contains the openShift.
            sharedOpenShift (string): sharedOpenShift

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

    def delete_open_shift(self, team_id: str, openShift_id: str) -> Any:
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

    def create_scheduling_group_for_team(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
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

    def replace_scheduling_group_in_team_sc(
        self,
        team_id: str,
        schedulingGroup_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
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

    def delete_scheduling_group_by_id(
        self, team_id: str, schedulingGroup_id: str
    ) -> Any:
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

    def get_team_shifts(
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

    def create_team_schedule_shift(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftShift (string): draftShift
            isStagedForDeletion (boolean): The shift is marked for deletion, a process that is finalized when the schedule is shared.
            schedulingGroupId (string): ID of the scheduling group the shift is part of. Required.
            sharedShift (string): sharedShift
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

    def get_team_shift(
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

    def replace_shift(
        self,
        team_id: str,
        shift_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftShift (string): draftShift
            isStagedForDeletion (boolean): The shift is marked for deletion, a process that is finalized when the schedule is shared.
            schedulingGroupId (string): ID of the scheduling group the shift is part of. Required.
            sharedShift (string): sharedShift
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

    def delete_shift_by_team_id(self, team_id: str, shift_id: str) -> Any:
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

    def get_team_shift_count(
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

    def list_swap_shift_change_requests(
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

    def swap_shifts_change_request(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[str] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[str] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): assignedTo
            managerActionDateTime (string): managerActionDateTime
            managerActionMessage (string): managerActionMessage
            managerUserId (string): managerUserId
            senderDateTime (string): senderDateTime
            senderMessage (string): senderMessage
            senderUserId (string): senderUserId
            state (string): state
            recipientActionDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            recipientActionMessage (string): Custom message sent by recipient of the offer shift request.
            recipientUserId (string): User ID of the recipient of the offer shift request.
            senderShiftId (string): User ID of the sender of the offer shift request.
            recipientShiftId (string): ShiftId for the recipient user with whom the request is to swap.

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
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[str] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[str] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): assignedTo
            managerActionDateTime (string): managerActionDateTime
            managerActionMessage (string): managerActionMessage
            managerUserId (string): managerUserId
            senderDateTime (string): senderDateTime
            senderMessage (string): senderMessage
            senderUserId (string): senderUserId
            state (string): state
            recipientActionDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            recipientActionMessage (string): Custom message sent by recipient of the offer shift request.
            recipientUserId (string): User ID of the recipient of the offer shift request.
            senderShiftId (string): User ID of the sender of the offer shift request.
            recipientShiftId (string): ShiftId for the recipient user with whom the request is to swap.

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

    def list_team_time_cards(
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

    def create_team_schedule_time_card(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        breaks: Optional[List[dict[str, dict[str, Any]]]] = None,
        clockInEvent: Optional[dict[str, dict[str, Any]]] = None,
        clockOutEvent: Optional[dict[str, dict[str, Any]]] = None,
        confirmedBy: Optional[str] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
        originalEntry: Optional[dict[str, dict[str, Any]]] = None,
        state: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Create timeCard

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            breaks (array): The list of breaks associated with the timeCard.
            clockInEvent (object): clockInEvent
            clockOutEvent (object): clockOutEvent
            confirmedBy (string): confirmedBy
            notes (object): notes
            originalEntry (object): originalEntry
            state (string): state
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

    def get_team_time_cards(
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

    def update_team_schedule_time_card_by_id(
        self,
        team_id: str,
        timeCard_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        breaks: Optional[List[dict[str, dict[str, Any]]]] = None,
        clockInEvent: Optional[dict[str, dict[str, Any]]] = None,
        clockOutEvent: Optional[dict[str, dict[str, Any]]] = None,
        confirmedBy: Optional[str] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
        originalEntry: Optional[dict[str, dict[str, Any]]] = None,
        state: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property timeCards in teams

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            breaks (array): The list of breaks associated with the timeCard.
            clockInEvent (object): clockInEvent
            clockOutEvent (object): clockOutEvent
            confirmedBy (string): confirmedBy
            notes (object): notes
            originalEntry (object): originalEntry
            state (string): state
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

    def delete_time_card_by_id(self, team_id: str, timeCard_id: str) -> Any:
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

    def clock_out_time_card_for_team_by_id(
        self,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action clockOut

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}/microsoft.graph.clockOut"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def confirm_team_time_card(self, team_id: str, timeCard_id: str) -> Any:
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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}/microsoft.graph.confirm"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def end_time_card_break(
        self,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action endBreak

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}/microsoft.graph.endBreak"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def start_break_time_card(
        self,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action startBreak

        Args:
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

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
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/{timeCard_id}/microsoft.graph.startBreak"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_time_cards_count(
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

    def clock_in_time_card(
        self,
        team_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action clockIn

        Args:
            team_id (string): team-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

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
            "notes": notes,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teams/{team_id}/schedule/timeCards/microsoft.graph.clockIn"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_team_time_off_reasons(
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

    def add_team_schedule_reason(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        code: Optional[str] = None,
        displayName: Optional[str] = None,
        iconType: Optional[str] = None,
        isActive: Optional[bool] = None,
    ) -> Any:
        """

        Create timeOffReason

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            code (string): The code of the timeOffReason to represent an external identifier. This field must be unique within the team in Microsoft Teams and uses an alphanumeric format, with a maximum of 100 characters.
            displayName (string): The name of the timeOffReason. Required.
            iconType (string): iconType
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

    def get_time_off_reason(
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
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        code: Optional[str] = None,
        displayName: Optional[str] = None,
        iconType: Optional[str] = None,
        isActive: Optional[bool] = None,
    ) -> Any:
        """

        Replace timeOffReason

        Args:
            team_id (string): team-id
            timeOffReason_id (string): timeOffReason-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            code (string): The code of the timeOffReason to represent an external identifier. This field must be unique within the team in Microsoft Teams and uses an alphanumeric format, with a maximum of 100 characters.
            displayName (string): The name of the timeOffReason. Required.
            iconType (string): iconType
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

    def get_team_schedule_reasons_count(
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

    def create_team_time_off_request(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[str] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[str] = None,
        endDateTime: Optional[str] = None,
        startDateTime: Optional[str] = None,
        timeOffReasonId: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to timeOffRequests for teams

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): assignedTo
            managerActionDateTime (string): managerActionDateTime
            managerActionMessage (string): managerActionMessage
            managerUserId (string): managerUserId
            senderDateTime (string): senderDateTime
            senderMessage (string): senderMessage
            senderUserId (string): senderUserId
            state (string): state
            endDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            startDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
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

    def update_time_off_request_by_id(
        self,
        team_id: str,
        timeOffRequest_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        assignedTo: Optional[str] = None,
        managerActionDateTime: Optional[str] = None,
        managerActionMessage: Optional[str] = None,
        managerUserId: Optional[str] = None,
        senderDateTime: Optional[str] = None,
        senderMessage: Optional[str] = None,
        senderUserId: Optional[str] = None,
        state: Optional[str] = None,
        endDateTime: Optional[str] = None,
        startDateTime: Optional[str] = None,
        timeOffReasonId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property timeOffRequests in teams

        Args:
            team_id (string): team-id
            timeOffRequest_id (string): timeOffRequest-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            assignedTo (string): assignedTo
            managerActionDateTime (string): managerActionDateTime
            managerActionMessage (string): managerActionMessage
            managerUserId (string): managerUserId
            senderDateTime (string): senderDateTime
            senderMessage (string): senderMessage
            senderUserId (string): senderUserId
            state (string): state
            endDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            startDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
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

    def get_team_schedule_times_off(
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

    def create_time_off(
        self,
        team_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftTimeOff (string): draftTimeOff
            isStagedForDeletion (boolean): The timeOff is marked for deletion, a process that is finalized when the schedule is shared.
            sharedTimeOff (string): sharedTimeOff
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

    def get_team_time_off_details(
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

    def patch_time_off_entry(
        self,
        team_id: str,
        timeOff_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
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
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            draftTimeOff (string): draftTimeOff
            isStagedForDeletion (boolean): The timeOff is marked for deletion, a process that is finalized when the schedule is shared.
            sharedTimeOff (string): sharedTimeOff
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

    def delete_time_off_entry(self, team_id: str, timeOff_id: str) -> Any:
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

    def list_teamwork_tags_by_team_id(
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

    def create_team_tag(
        self,
        team_id: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        memberCount: Optional[float] = None,
        tagType: Optional[str] = None,
        teamId: Optional[str] = None,
        members: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create teamworkTag

        Args:
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            description (string): The description of the tag as it appears to the user in Microsoft Teams. A teamworkTag can't have more than 200 teamworkTagMembers.
            displayName (string): The name of the tag as it appears to the user in Microsoft Teams.
            memberCount (number): The number of users assigned to the tag.
            tagType (string): tagType
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

    def get_teamwork_tag(
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

    def update_teamwork_tag(
        self,
        team_id: str,
        teamworkTag_id: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        memberCount: Optional[float] = None,
        tagType: Optional[str] = None,
        teamId: Optional[str] = None,
        members: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update teamworkTag

        Args:
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            id (string): The unique identifier for an entity. Read-only.
            description (string): The description of the tag as it appears to the user in Microsoft Teams. A teamworkTag can't have more than 200 teamworkTagMembers.
            displayName (string): The name of the tag as it appears to the user in Microsoft Teams.
            memberCount (number): The number of users assigned to the tag.
            tagType (string): tagType
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

    def delete_teamwork_tag(self, team_id: str, teamworkTag_id: str) -> Any:
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

    def list_teamwork_tag_members(
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

    def create_teamwork_tag_member(
        self,
        team_id: str,
        teamworkTag_id: str,
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

    def get_teamwork_tag_member(
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

    def update_team_tag_member(
        self,
        team_id: str,
        teamworkTag_id: str,
        teamworkTagMember_id: str,
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

    def delete_teamwork_tag_member(
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

    def get_team_tag_members_count(
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

    def count_team_tags(
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

    def get_team_template(
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

    def get_team_count(
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

    def get_all_team_messages(
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
            teams.team.Functions
        """
        url = f"{self.main_app_client.base_url}/teams/microsoft.graph.getAllMessages()"
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
            self.list_teams,
            self.create_team,
            self.get_team_info,
            self.update_team,
            self.delete_team_entity,
            self.list_all_team_channels,
            self.get_team_channels,
            self.get_team_all_channels_count,
            self.list_channels_for_team,
            self.create_team_channel,
            self.get_team_channel_info,
            self.update_channel,
            self.delete_channel,
            self.list_all_team_channel_members,
            self.create_team_channel_members,
            self.get_team_channel_members_details,
            self.update_conversation_member_in_team,
            self.delete_team_channel_member,
            self.count_team_channel_members,
            self.add_channel_members,
            self.remove_team_channel_all_members,
            self.get_team_channel_files_folder,
            self.get_files_folder_content,
            self.update_team_channel_file_content,
            self.delete_team_channel_file_content,
            self.list_channel_members_by_team_and_cha,
            self.add_member_to_channel_teamwise,
            self.get_channel_member,
            self.update_channel_member_by_id,
            self.delete_conversation_member,
            self.get_member_count,
            self.add_team_channel_member_action,
            self.remove_member_action,
            self.list_channel_messages_by_id,
            self.send_chat_message,
            self.get_chat_message,
            self.update_chat_message_by_team_channel,
            self.delete_team_channel_message,
            self.list_channel_msg_hosted_content,
            self.create_message_hosted_content,
            self.get_chat_message_hosted_content_by_i,
            self.update_hosted_content_details,
            self.del_ch_msg_hosted_content,
            self.get_channel_msg_hosted_content_val,
            self.update_team_hosted_content_val,
            self.delete_channel_message_hosted_cont,
            self.count_message_hosted_contents_by_me,
            self.set_reaction_on_channel_message,
            self.soft_delete_chat_message,
            self.restore_team_channel_message,
            self.unset_reaction_from_message,
            self.get_replies,
            self.create_channel_message_reply,
            self.get_chat_message_reply,
            self.update_message_reply,
            self.delete_team_channel_message_reply_b,
            self.list_reply_hosted_contents_by_messa,
            self.create_hosted_content_link,
            self.get_channel_reply_hosted_content,
            self.patch_ch_reply_hosted_content,
            self.del_ch_msg_reply_hosted_content,
            self.get_ch_msg_reply_hosted_content_val,
            self.update_msg_reply_hosted_content,
            self.delete_hosted_content_by_message_re,
            self.count_ch_msg_reply_host_contents,
            self.add_reaction_to_reply,
            self.soft_delete_channel_message_reply_p,
            self.undo_soft_delete_team_message_reply,
            self.unset_message_reaction_reply,
            self.count_replies,
            self.get_delta_replies_for_message,
            self.get_team_channel_message_count,
            self.delta_team_channel_messages,
            self.archive_channel_action,
            self.complete_team_channel_migration,
            self.check_channel_user_access,
            self.teams_channels_provision_email_pos,
            self.remove_channel_email_from_team,
            self.unarchive_team_channel,
            self.list_channel_shared_teams,
            self.share_channel_with_team,
            self.get_shared_teams_channels_info,
            self.update_shared_with_team_info,
            self.delete_shared_team_channel_link,
            self.list_channel_allowed_members_by_tea,
            self.get_channel_allowed_member_by_id,
            self.get_shared_team_members_count,
            self.get_shared_team_channel_info,
            self.count_shared_with_teams_in_channel,
            self.get_channel_tabs,
            self.add_channel_tab,
            self.get_team_tab_info,
            self.update_tab_info,
            self.delete_channel_tab_by_id,
            self.get_teams_app_data,
            self.count_team_channel_tabs,
            self.count_team_channels,
            self.get_team_channel_messages,
            self.get_retained_messages_by_team_id,
            self.get_team_group,
            self.list_service_provisioning_errors,
            self.get_team_provisioning_errors_count,
            self.get_incoming_team_channels,
            self.get_incoming_channel_by_team_id,
            self.get_team_incoming_channels_count,
            self.get_team_apps,
            self.add_team_app,
            self.get_installed_team_app,
            self.update_teams_installed_app_navigat,
            self.remove_team_installed_app,
            self.upgrade_team_app,
            self.get_teams_app_detail,
            self.get_app_definition,
            self.get_installed_app_count,
            self.get_team_members_list,
            self.add_member_to_team,
            self.get_team_member_details,
            self.update_team_member_conversation_me,
            self.remove_team_member_by_id,
            self.get_team_member_count,
            self.add_team_members_by_graph_action,
            self.remove_team_member_by_graph_action,
            self.team_archive_action,
            self.clone_team_action,
            self.complete_team_migration_action,
            self.teams_send_activity_notif,
            self.unarchive_team_operation,
            self.get_team_operations_by_id,
            self.create_team_operation,
            self.get_teams_async_operation_by_id,
            self.update_team_operation,
            self.delete_teams_async_operation_for_te,
            self.get_team_operation_count,
            self.list_team_permission_grants,
            self.create_team_permission_grant,
            self.get_permission_grant_by_team_resour,
            self.update_team_permission_grants,
            self.delete_team_permission_grant,
            self.count_permission_grants,
            self.get_team_profile_photo,
            self.update_team_photo,
            self.get_profile_photo,
            self.update_team_photo_content,
            self.delete_team_photo_content,
            self.get_primary_team_channel,
            self.update_team_primary_channel,
            self.delete_team_primary_channel,
            self.list_team_primary_channel_members,
            self.add_team_primary_channel_members,
            self.get_team_primary_channel_members,
            self.update_primary_channel_members,
            self.remove_conversation_member,
            self.count_team_primary_channel_members,
            self.add_primary_channel_all_members_act,
            self.remove_team_members,
            self.get_team_files_folder,
            self.get_team_primary_channel_content,
            self.upload_team_folder_content,
            self.delete_team_files_folder_content,
            self.get_team_primary_members,
            self.add_team_channel_members,
            self.get_team_primary_channel_member_by_i,
            self.update_conversation_member_by_id,
            self.delete_team_primary_channel_member,
            self.get_team_primary_channel_member_cou,
            self.add_team_primary_channel_member,
            self.remove_team_primary_channel_member,
            self.list_team_primary_channel_messages,
            self.create_team_message,
            self.get_team_primary_messages,
            self.patch_team_message_by_id,
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
            self.set_reaction_to_primary_channel_mes,
            self.soft_delete_team_channel_message,
            self.teams_undo_soft_delete_message,
            self.unset_reaction_by_message_id,
            self.list_replies_by_message_id,
            self.create_reply_to_chat_message,
            self.get_team_primary_channel_message_re,
            self.update_reply,
            self.delete_reply,
            self.list_team_reply_hosted_contents_by_i,
            self.create_team_reply_hosted_content,
            self.get_pri_ch_reply_hosted_content,
            self.patch_pri_ch_reply_hosted_content,
            self.del_pri_ch_reply_hosted_content,
            self.get_pri_ch_reply_host_content_val,
            self.put_pri_ch_reply_hosted_content_val,
            self.del_pri_ch_reply_host_cont_val,
            self.count_hosted_content_replies,
            self.set_reaction_to_reply,
            self.soft_delete_reply_message,
            self.undo_reply_soft_delete,
            self.unset_reply_reaction,
            self.get_primary_channel_replies_count,
            self.get_delta_replies,
            self.get_primary_channel_message_count,
            self.list_primary_channel_messages,
            self.archive_team_primary_channel,
            self.complete_team_migration,
            self.check_user_access_in_channel,
            self.provision_team_email,
            self.remove_primary_team_email,
            self.unarchive_team_primary_channel,
            self.list_primary_channel_shared_teams,
            self.share_primary_channel_with_teams,
            self.get_shared_channel_info_by_id,
            self.update_shared_channel_team_info,
            self.remove_shared_with_team,
            self.get_shared_members,
            self.get_team_channel_shared_member_by_id,
            self.count_shared_team_members,
            self.get_shared_channel_team_info_team,
            self.get_primary_channel_shared_with_tea,
            self.get_team_tabs,
            self.create_team_tab,
            self.get_team_primary_tabs,
            self.update_team_tab,
            self.delete_team_tab,
            self.get_teams_app_by_tab_id,
            self.get_team_primary_channel_tabs_count,
            self.get_team_schedule,
            self.update_team_schedule,
            self.delete_team_schedule,
            self.get_team_day_notes,
            self.create_team_schedule_day_note,
            self.get_team_schedule_day_note,
            self.update_team_day_note,
            self.delete_team_day_note,
            self.get_team_schedule_day_notes_count,
            self.share_team_schedule_action,
            self.get_team_shift_requests,
            self.offer_shift_requests,
            self.get_team_schedule_offer_shifts,
            self.patch_offer_shift_request,
            self.delete_shift_offer_request,
            self.count_shift_offer_requests,
            self.get_team_open_shift_requests,
            self.create_open_shift_change_requests,
            self.get_open_shift_change_request_by_id,
            self.patch_open_shift_change_request_by_i,
            self.remove_open_shift_change_request,
            self.count_open_shift_change_requests,
            self.list_team_open_shifts,
            self.create_open_shift_for_team_schedule,
            self.get_open_shift_by_team_id,
            self.update_open_shift_details,
            self.delete_open_shift,
            self.count_open_shifts,
            self.get_scheduling_groups,
            self.create_scheduling_group_for_team,
            self.get_team_schedule_scheduling_group,
            self.replace_scheduling_group_in_team_sc,
            self.delete_scheduling_group_by_id,
            self.count_scheduling_groups,
            self.get_team_shifts,
            self.create_team_schedule_shift,
            self.get_team_shift,
            self.replace_shift,
            self.delete_shift_by_team_id,
            self.get_team_shift_count,
            self.list_swap_shift_change_requests,
            self.swap_shifts_change_request,
            self.swap_shift_request_read,
            self.update_swap_shift_request,
            self.delete_swap_shifts_change_request,
            self.count_swap_shift_requests,
            self.list_team_time_cards,
            self.create_team_schedule_time_card,
            self.get_team_time_cards,
            self.update_team_schedule_time_card_by_id,
            self.delete_time_card_by_id,
            self.clock_out_time_card_for_team_by_id,
            self.confirm_team_time_card,
            self.end_time_card_break,
            self.start_break_time_card,
            self.get_team_time_cards_count,
            self.clock_in_time_card,
            self.list_team_time_off_reasons,
            self.add_team_schedule_reason,
            self.get_time_off_reason,
            self.update_time_off_reason_by_id,
            self.delete_time_off_reason_by_id,
            self.get_team_schedule_reasons_count,
            self.list_time_off_requests,
            self.create_team_time_off_request,
            self.get_team_time_off_request_details,
            self.update_time_off_request_by_id,
            self.delete_team_time_off_request,
            self.get_team_time_off_count,
            self.get_team_schedule_times_off,
            self.create_time_off,
            self.get_team_time_off_details,
            self.patch_time_off_entry,
            self.delete_time_off_entry,
            self.get_team_schedule_times_off_count,
            self.list_teamwork_tags_by_team_id,
            self.create_team_tag,
            self.get_teamwork_tag,
            self.update_teamwork_tag,
            self.delete_teamwork_tag,
            self.list_teamwork_tag_members,
            self.create_teamwork_tag_member,
            self.get_teamwork_tag_member,
            self.update_team_tag_member,
            self.delete_teamwork_tag_member,
            self.get_team_tag_members_count,
            self.count_team_tags,
            self.get_team_template,
            self.get_team_count,
            self.get_all_team_messages,
        ]
