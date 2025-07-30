from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class GroupsApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def get_group_team(
        self,
        group_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from groups

        Args:
            group_id (string): group-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team, important
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_team_from_group(
        self,
        group_id: str,
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

        Create team from group

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def delete_group_team(self, group_id: str) -> Any:
        """

        Delete navigation property team for groups

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def fetch_groups_team_all_channels(
        self,
        group_id: str,
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

        Get allChannels from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/allChannels"
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

    def get_group_team_all_channels(
        self,
        group_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allChannels from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/allChannels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_channels_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = (
            f"{self.main_app_client.base_url}/groups/{group_id}/team/allChannels/$count"
        )
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_channels(
        self,
        group_id: str,
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

        Get channels from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels"
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

    def create_group_channel(
        self,
        group_id: str,
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

        Create new navigation property to channels for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_channels(
        self,
        group_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get channels from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_channels(
        self,
        group_id: str,
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

        Update the navigation property channels in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_channel(self, group_id: str, channel_id: str) -> Any:
        """

        Delete navigation property channels for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_channel_members(
        self,
        group_id: str,
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

        Get allMembers from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/allMembers"
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

    def create_group_team_channel_all_membe(
        self,
        group_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to allMembers for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/allMembers"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_channel_member_details(
        self,
        group_id: str,
        channel_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allMembers from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_team_channel_member(
        self,
        group_id: str,
        channel_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property allMembers in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_channel_member(
        self, group_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property allMembers for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_channel_members(
        self,
        group_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/allMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_group_channel_all_members(
        self, group_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/allMembers/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_channel_members(
        self, group_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/allMembers/microsoft.graph.remove"
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
        group_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get filesFolder from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/filesFolder"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_files_content(
        self, group_id: str, channel_id: str, format: Optional[str] = None
    ) -> Any:
        """

        Get content for the navigation property filesFolder from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            format (string): Format of the content

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/filesFolder/content"
        query_params = {k: v for k, v in [("$format", format)] if v is not None}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_files_folder_content(
        self, group_id: str, channel_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property filesFolder in groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/filesFolder/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_file_content(self, group_id: str, channel_id: str) -> Any:
        """

        Delete content for the navigation property filesFolder in groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/filesFolder/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_channel_members(
        self,
        group_id: str,
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

        Get members from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/members"
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

    def create_group_team_channel_member(
        self,
        group_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_channel_members(
        self,
        group_id: str,
        channel_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_channel_member(
        self,
        group_id: str,
        channel_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_member_from_channel(
        self, group_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property members for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_channel_member_count(
        self,
        group_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_team_channel_member(
        self, group_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_channel_member(
        self, group_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_messages(
        self,
        group_id: str,
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

        Get messages from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages"
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

    def create_group_channel_message(
        self,
        group_id: str,
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

        Create new navigation property to messages for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_channel_messages(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get messages from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_message(
        self,
        group_id: str,
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

        Update the navigation property messages in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_message_in_channel(
        self, group_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Delete navigation property messages for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_group_team_channel_message_hos(
        self,
        group_id: str,
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

        Get hostedContents from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents"
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
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_channel_message_hosted_con(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_hosted_content(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_team_channel_message_h(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_channel_message_hosted_co(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_team_channel_msg_hoste(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_hosted_content(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_content_count(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_on_group_team_channel_m(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_channel_message(
        self, group_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def restore_group_channel_message(
        self, group_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_on_message(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_chat_message_replies(
        self,
        group_id: str,
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

        Get replies from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies"
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

    def create_reply_in_message(
        self,
        group_id: str,
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

        Create new navigation property to replies for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_reply_messages(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get replies from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_reply_message(
        self,
        group_id: str,
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

        Update the navigation property replies in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_channel_message_reply_by_id(
        self, group_id: str, channel_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Delete navigation property replies for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_channel_msg_replies_h(
        self,
        group_id: str,
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

        Get hostedContents from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
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

    def add_reply_content(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_hosted_content_by_reply_id(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_hosted_content_reply(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_hosted_content_by_message_id(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_channel_msg_hosted_co(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_team_channel_reply_hos(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_group_team_channel_message_r(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_hosted_contents_replies(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_to_message_reply(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_channel_message_reply(
        self, group_id: str, channel_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_message_reply_soft_delete(
        self, group_id: str, channel_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_on_reply(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_reply_count(
        self,
        group_id: str,
        channel_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_microsoft_graph_delta_replies(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/{chatMessage_id}/replies/microsoft.graph.delta()"
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

    def get_group_channel_message_count(
        self,
        group_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_channel_messages_delta(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/messages/microsoft.graph.delta()"
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
        group_id: str,
        channel_id: str,
        shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None,
    ) -> Any:
        """

        Invoke action archive

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/microsoft.graph.archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_group_channel_migration(self, group_id: str, channel_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            group_id (string): group-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def check_user_access(
        self,
        group_id: str,
        channel_id: str,
        userId: Optional[str] = None,
        tenantId: Optional[str] = None,
        userPrincipalName: Optional[str] = None,
    ) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            userId (string): Usage: userId='@userId'
            tenantId (string): Usage: tenantId='@tenantId'
            userPrincipalName (string): Usage: userPrincipalName='@userPrincipalName'

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/microsoft.graph.doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
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

    def provision_email_to_channel(
        self, group_id: str, channel_id: str
    ) -> dict[str, Any]:
        """

        Invoke action provisionEmail

        Args:
            group_id (string): group-id
            channel_id (string): channel-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/microsoft.graph.provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_channel_email(self, group_id: str, channel_id: str) -> Any:
        """

        Invoke action removeEmail

        Args:
            group_id (string): group-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/microsoft.graph.removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_channel(self, group_id: str, channel_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            group_id (string): group-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/microsoft.graph.unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_channel_shared_teams(
        self,
        group_id: str,
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

        Get sharedWithTeams from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams"
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

    def add_team_to_channel(
        self,
        group_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to sharedWithTeams for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_with_team_info(
        self,
        group_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get sharedWithTeams from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_channel_sharing(
        self,
        group_id: str,
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

        Update the navigation property sharedWithTeams in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_shared_team_channel(
        self, group_id: str, channel_id: str, sharedWithChannelTeamInfo_id: str
    ) -> Any:
        """

        Delete navigation property sharedWithTeams for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_shared_channel_members(
        self,
        group_id: str,
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

        Get allowedMembers from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers"
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

    def get_channel_allowed_member_by_ids(
        self,
        group_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allowedMembers from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_allowed_members_by_channel_te(
        self,
        group_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_team_info(
        self,
        group_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_with_teams_count_in_chann(
        self,
        group_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/sharedWithTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_tabs(
        self,
        group_id: str,
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

        Get tabs from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/tabs"
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

    def create_group_tab(
        self,
        group_id: str,
        channel_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to tabs for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_tabs(
        self,
        group_id: str,
        channel_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tabs from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_tab(
        self,
        group_id: str,
        channel_id: str,
        teamsTab_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property tabs in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_tab(self, group_id: str, channel_id: str, teamsTab_id: str) -> Any:
        """

        Delete navigation property tabs for groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_teams_app_tab(
        self,
        group_id: str,
        channel_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_channel_tabs_count(
        self,
        group_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/{channel_id}/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_channel_total(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_channel_messages_all(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/microsoft.graph.getAllMessages()"
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

    def get_retained_messages(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/channels/microsoft.graph.getAllRetainedMessages()"
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

    def get_group_team_data(
        self,
        group_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get group from groups

        Args:
            group_id (string): group-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/group"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_service_errors(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/group/serviceProvisioningErrors"
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
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/group/serviceProvisioningErrors/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_incoming_channels(
        self,
        group_id: str,
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

        Get incomingChannels from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/incomingChannels"
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

    def get_incoming_channels_by_group(
        self,
        group_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get incomingChannels from groups

        Args:
            group_id (string): group-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/incomingChannels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_incoming_channels_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/incomingChannels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_group_team_apps(
        self,
        group_id: str,
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

        Get installedApps from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps"
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

    def add_group_installed_app(
        self,
        group_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to installedApps for groups

        Args:
            group_id (string): group-id
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (object): consentedPermissionSet
            teamsApp (string): teamsApp
            teamsAppDefinition (string): teamsAppDefinition

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_installed_apps(
        self,
        group_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get installedApps from groups

        Args:
            group_id (string): group-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps/{teamsAppInstallation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_installed_apps(
        self,
        group_id: str,
        teamsAppInstallation_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property installedApps in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_installed_app_for_group_team(
        self, group_id: str, teamsAppInstallation_id: str
    ) -> Any:
        """

        Delete navigation property installedApps for groups

        Args:
            group_id (string): group-id
            teamsAppInstallation_id (string): teamsAppInstallation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def upgrade_teams_app(
        self,
        group_id: str,
        teamsAppInstallation_id: str,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action upgrade

        Args:
            group_id (string): group-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            consentedPermissionSet (object): consentedPermissionSet

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        request_body_data = None
        request_body_data = {"consentedPermissionSet": consentedPermissionSet}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps/{teamsAppInstallation_id}/microsoft.graph.upgrade"
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
        group_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from groups

        Args:
            group_id (string): group-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps/{teamsAppInstallation_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_teams_app_definition(
        self,
        group_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsAppDefinition from groups

        Args:
            group_id (string): group-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps/{teamsAppInstallation_id}/teamsAppDefinition"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_group_team_apps(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/installedApps/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_members(
        self,
        group_id: str,
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

        Get members from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/members"
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

    def create_group_member(
        self,
        group_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for groups

        Args:
            group_id (string): group-id
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_team_members(
        self,
        group_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from groups

        Args:
            group_id (string): group-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_team_member(
        self,
        group_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_member(self, group_id: str, conversationMember_id: str) -> Any:
        """

        Delete navigation property members for groups

        Args:
            group_id (string): group-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_member_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_group_team_member_action(
        self, group_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            group_id (string): group-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_member_action(
        self, group_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            group_id (string): group-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def archive_group_team(
        self, group_id: str, shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None
    ) -> Any:
        """

        Invoke action archive

        Args:
            group_id (string): group-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/microsoft.graph.archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def clone_team_group(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/microsoft.graph.clone"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_group_team_migration(self, group_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def send_activity_notification_to_grou(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/microsoft.graph.sendActivityNotification"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_group_team(self, group_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/microsoft.graph.unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_operations(
        self,
        group_id: str,
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

        Get operations from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/operations"
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

    def create_group_team_operation(
        self,
        group_id: str,
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

        Create new navigation property to operations for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/operations"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_team_operations(
        self,
        group_id: str,
        teamsAsyncOperation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get operations from groups

        Args:
            group_id (string): group-id
            teamsAsyncOperation_id (string): teamsAsyncOperation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsAsyncOperation_id is None:
            raise ValueError("Missing required parameter 'teamsAsyncOperation-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/operations/{teamsAsyncOperation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_operations(
        self,
        group_id: str,
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

        Update the navigation property operations in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/operations/{teamsAsyncOperation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_operation(self, group_id: str, teamsAsyncOperation_id: str) -> Any:
        """

        Delete navigation property operations for groups

        Args:
            group_id (string): group-id
            teamsAsyncOperation_id (string): teamsAsyncOperation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsAsyncOperation_id is None:
            raise ValueError("Missing required parameter 'teamsAsyncOperation-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/operations/{teamsAsyncOperation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = (
            f"{self.main_app_client.base_url}/groups/{group_id}/team/operations/$count"
        )
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_group_team_permission_grants(
        self,
        group_id: str,
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

        Get permissionGrants from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/permissionGrants"
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

    def create_permission_grant(
        self,
        group_id: str,
        id: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        clientAppId: Optional[str] = None,
        clientId: Optional[str] = None,
        permission: Optional[str] = None,
        permissionType: Optional[str] = None,
        resourceAppId: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to permissionGrants for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/permissionGrants"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_permission_grants(
        self,
        group_id: str,
        resourceSpecificPermissionGrant_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get permissionGrants from groups

        Args:
            group_id (string): group-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_permission_grant(
        self,
        group_id: str,
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

        Update the navigation property permissionGrants in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_permission_grant(
        self, group_id: str, resourceSpecificPermissionGrant_id: str
    ) -> Any:
        """

        Delete navigation property permissionGrants for groups

        Args:
            group_id (string): group-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_permission_grants_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/permissionGrants/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_picture(
        self,
        group_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get photo from groups

        Args:
            group_id (string): group-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/photo"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_group_team_photo(
        self,
        group_id: str,
        id: Optional[str] = None,
        height: Optional[float] = None,
        width: Optional[float] = None,
    ) -> Any:
        """

        Update the navigation property photo in groups

        Args:
            group_id (string): group-id
            id (string): The unique identifier for an entity. Read-only.
            height (number): The height of the photo. Read-only.
            width (number): The width of the photo. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {"id": id, "height": height, "width": width}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/photo"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def get_group_team_photo(self, group_id: str) -> Any:
        """

        Get media content for the navigation property photo from groups

        Args:
            group_id (string): group-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/photo/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def put_group_team_photo_content(self, group_id: str, body_content: bytes) -> Any:
        """

        Update media content for the navigation property photo in groups

        Args:
            group_id (string): group-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/photo/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_group_team_photo(self, group_id: str) -> Any:
        """

        Delete media content for the navigation property photo in groups

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/photo/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_primary(
        self,
        group_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get primaryChannel from groups

        Args:
            group_id (string): group-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_primary_channel(
        self,
        group_id: str,
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

        Update the navigation property primaryChannel in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_primary_channel(self, group_id: str) -> Any:
        """

        Delete navigation property primaryChannel for groups

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def fetch_team_primary_channel_members(
        self,
        group_id: str,
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

        Get allMembers from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/allMembers"
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

    def create_primary_channel_all_members(
        self,
        group_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to allMembers for groups

        Args:
            group_id (string): group-id
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/allMembers"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_primary_channel_member(
        self,
        group_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allMembers from groups

        Args:
            group_id (string): group-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_member(
        self,
        group_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property allMembers in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_primary_channel_member(
        self, group_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property allMembers for groups

        Args:
            group_id (string): group-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_member_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/allMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_group_team_members(
        self, group_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            group_id (string): group-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/allMembers/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_primary_channel_members(
        self, group_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            group_id (string): group-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/allMembers/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_primary_channel_folder(
        self,
        group_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get filesFolder from groups

        Args:
            group_id (string): group-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/filesFolder"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_files_content(
        self, group_id: str, format: Optional[str] = None
    ) -> Any:
        """

        Get content for the navigation property filesFolder from groups

        Args:
            group_id (string): group-id
            format (string): Format of the content

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/filesFolder/content"
        query_params = {k: v for k, v in [("$format", format)] if v is not None}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel_content(self, group_id: str, body_content: bytes) -> Any:
        """

        Update content for the navigation property filesFolder in groups

        Args:
            group_id (string): group-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/filesFolder/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_group_files_folder_content(self, group_id: str) -> Any:
        """

        Delete content for the navigation property filesFolder in groups

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/filesFolder/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_primary_channel_members(
        self,
        group_id: str,
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

        Get members from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/members"
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

    def create_primary_channel_member_for_g(
        self,
        group_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for groups

        Args:
            group_id (string): group-id
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_primary_channel_members(
        self,
        group_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from groups

        Args:
            group_id (string): group-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel_member(
        self,
        group_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_member_from_primary_channel(
        self, group_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property members for groups

        Args:
            group_id (string): group-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_primary_channel_members(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_primary_channel_member(
        self, group_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            group_id (string): group-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_group_team_member(
        self, group_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            group_id (string): group-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_primary_channel_messages(
        self,
        group_id: str,
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

        Get messages from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages"
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

    def post_primary_channel_message(
        self,
        group_id: str,
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

        Create new navigation property to messages for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_primary_channel_message(
        self,
        group_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get messages from groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel_message(
        self,
        group_id: str,
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

        Update the navigation property messages in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_primary_channel_message(self, group_id: str, chatMessage_id: str) -> Any:
        """

        Delete navigation property messages for groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_content_by_message_id(
        self,
        group_id: str,
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

        Get hostedContents from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents"
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

    def add_hosted_content_to_group_message(
        self,
        group_id: str,
        chatMessage_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_team_primary_channel_mess(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_group_team_primary_channel_me(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_message_hosted_content(
        self, group_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        Delete navigation property hostedContents for groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_primary_channel_msg_h(
        self, group_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_team_primary_msg_hoste(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_group_team_primary_channel_m(
        self, group_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_hosted_content(
        self,
        group_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_to_chat_message(
        self, group_id: str, chatMessage_id: str, reactionType: Optional[str] = None
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_group_channel_message(
        self, group_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_soft_delete_chat_message(self, group_id: str, chatMessage_id: str) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_for_primary_channel(
        self, group_id: str, chatMessage_id: str, reactionType: Optional[str] = None
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/microsoft.graph.unsetReaction"
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
        group_id: str,
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

        Get replies from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies"
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

    def create_reply_to_message(
        self,
        group_id: str,
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

        Create new navigation property to replies for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_group_team_primary_channel_mes(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get replies from groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel_reply(
        self,
        group_id: str,
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

        Update the navigation property replies in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_reply_message(
        self, group_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Delete navigation property replies for groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_reply_contents(
        self,
        group_id: str,
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

        Get hostedContents from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
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

    def create_reply_hosted_content(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_hosted_content_reply(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_group_team_msg_reply_hosted_co(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_team_primary_channel_r(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_channel_msg_reply_hos(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_team_primary_channel_m(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_group_team_primary_ch_reply_h(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in groups

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_primary_channel_repl(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reply_reaction(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_group_message_reply(
        self, group_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_soft_delete_chat_message_reply(
        self, group_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_to_reply(
        self,
        group_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def count_primary_channel_replies(
        self,
        group_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_replies_delta(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/{chatMessage_id}/replies/microsoft.graph.delta()"
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

    def count_primary_channel_messages(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_messages_delta(
        self,
        group_id: str,
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
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/messages/microsoft.graph.delta()"
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
        self, group_id: str, shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None
    ) -> Any:
        """

        Invoke action archive

        Args:
            group_id (string): group-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/microsoft.graph.archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_group_migration(self, group_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def check_user_access_to_group(
        self,
        group_id: str,
        userId: Optional[str] = None,
        tenantId: Optional[str] = None,
        userPrincipalName: Optional[str] = None,
    ) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            group_id (string): group-id
            userId (string): Usage: userId='@userId'
            tenantId (string): Usage: tenantId='@tenantId'
            userPrincipalName (string): Usage: userPrincipalName='@userPrincipalName'

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/microsoft.graph.doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
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

    def provision_primary_email(self, group_id: str) -> dict[str, Any]:
        """

        Invoke action provisionEmail

        Args:
            group_id (string): group-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/microsoft.graph.provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_primary_channel_email(self, group_id: str) -> Any:
        """

        Invoke action removeEmail

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/microsoft.graph.removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_primary_channel(self, group_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/microsoft.graph.unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_with_teams(
        self,
        group_id: str,
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

        Get sharedWithTeams from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams"
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

    def share_primary_channel_teams(
        self,
        group_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to sharedWithTeams for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_channel_teams(
        self,
        group_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get sharedWithTeams from groups

        Args:
            group_id (string): group-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_shared_team_channel_info(
        self,
        group_id: str,
        sharedWithChannelTeamInfo_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property sharedWithTeams in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def remove_group_team_primary_channel_s(
        self, group_id: str, sharedWithChannelTeamInfo_id: str
    ) -> Any:
        """

        Delete navigation property sharedWithTeams for groups

        Args:
            group_id (string): group-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_allowed_members_in_shared_chan(
        self,
        group_id: str,
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

        Get allowedMembers from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers"
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

    def get_channel_team_allowed_member(
        self,
        group_id: str,
        sharedWithChannelTeamInfo_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allowedMembers from groups

        Args:
            group_id (string): group-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_allowed_members(
        self,
        group_id: str,
        sharedWithChannelTeamInfo_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_channel_team_info(
        self,
        group_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from groups

        Args:
            group_id (string): group-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_teams_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/sharedWithTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_group_team_primary_channel_tab(
        self,
        group_id: str,
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

        Get tabs from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/tabs"
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

    def create_primary_channel_tab(
        self,
        group_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to tabs for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_primary_channel_tab(
        self,
        group_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tabs from groups

        Args:
            group_id (string): group-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel_tab(
        self,
        group_id: str,
        teamsTab_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property tabs in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_primary_channel_tab(self, group_id: str, teamsTab_id: str) -> Any:
        """

        Delete navigation property tabs for groups

        Args:
            group_id (string): group-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_tabs_app(
        self,
        group_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from groups

        Args:
            group_id (string): group-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_primary_channel_tabs(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/primaryChannel/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_schedule(
        self,
        group_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get schedule from groups

        Args:
            group_id (string): group-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_schedule(
        self,
        group_id: str,
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

        Update the navigation property schedule in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def delete_group_schedule(self, group_id: str) -> Any:
        """

        Delete navigation property schedule for groups

        Args:
            group_id (string): group-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_day_notes(
        self,
        group_id: str,
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

        Get dayNotes from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = (
            f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/dayNotes"
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

    def add_day_notes_to_group_team_schedule(
        self,
        group_id: str,
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

        Create new navigation property to dayNotes for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = (
            f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/dayNotes"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_team_day_notes(
        self,
        group_id: str,
        dayNote_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get dayNotes from groups

        Args:
            group_id (string): group-id
            dayNote_id (string): dayNote-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if dayNote_id is None:
            raise ValueError("Missing required parameter 'dayNote-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/dayNotes/{dayNote_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_day_note(
        self,
        group_id: str,
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

        Update the navigation property dayNotes in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/dayNotes/{dayNote_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_day_note_by_id(self, group_id: str, dayNote_id: str) -> Any:
        """

        Delete navigation property dayNotes for groups

        Args:
            group_id (string): group-id
            dayNote_id (string): dayNote-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if dayNote_id is None:
            raise ValueError("Missing required parameter 'dayNote-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/dayNotes/{dayNote_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_day_note_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/dayNotes/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def share_team_schedule(
        self,
        group_id: str,
        notifyTeam: Optional[bool] = None,
        startDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
    ) -> Any:
        """

        Invoke action share

        Args:
            group_id (string): group-id
            notifyTeam (boolean): notifyTeam
            startDateTime (string): startDateTime
            endDateTime (string): endDateTime

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {
            "notifyTeam": notifyTeam,
            "startDateTime": startDateTime,
            "endDateTime": endDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/microsoft.graph.share"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_group_shift_requests(
        self,
        group_id: str,
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

        Get offerShiftRequests from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/offerShiftRequests"
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

    def offer_shift_requests_to_group(
        self,
        group_id: str,
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

        Create new navigation property to offerShiftRequests for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/offerShiftRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_offer_shift_request_details(
        self,
        group_id: str,
        offerShiftRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get offerShiftRequests from groups

        Args:
            group_id (string): group-id
            offerShiftRequest_id (string): offerShiftRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if offerShiftRequest_id is None:
            raise ValueError("Missing required parameter 'offerShiftRequest-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_offer_shift_request(
        self,
        group_id: str,
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

        Update the navigation property offerShiftRequests in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_team_schedule_offer_sh(
        self, group_id: str, offerShiftRequest_id: str
    ) -> Any:
        """

        Delete navigation property offerShiftRequests for groups

        Args:
            group_id (string): group-id
            offerShiftRequest_id (string): offerShiftRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if offerShiftRequest_id is None:
            raise ValueError("Missing required parameter 'offerShiftRequest-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_group_shift_requests(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/offerShiftRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_group_team_open_shift_change_re(
        self,
        group_id: str,
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

        Get openShiftChangeRequests from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShiftChangeRequests"
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
        group_id: str,
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

        Create new navigation property to openShiftChangeRequests for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShiftChangeRequests"
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
        group_id: str,
        openShiftChangeRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get openShiftChangeRequests from groups

        Args:
            group_id (string): group-id
            openShiftChangeRequest_id (string): openShiftChangeRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if openShiftChangeRequest_id is None:
            raise ValueError("Missing required parameter 'openShiftChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_group_team_open_shift_change_r(
        self,
        group_id: str,
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

        Update the navigation property openShiftChangeRequests in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_open_shift_change_request(
        self, group_id: str, openShiftChangeRequest_id: str
    ) -> Any:
        """

        Delete navigation property openShiftChangeRequests for groups

        Args:
            group_id (string): group-id
            openShiftChangeRequest_id (string): openShiftChangeRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if openShiftChangeRequest_id is None:
            raise ValueError("Missing required parameter 'openShiftChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_open_shift_requests(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShiftChangeRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_open_shifts(
        self,
        group_id: str,
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

        Get openShifts from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShifts"
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

    def open_shifts_in_group(
        self,
        group_id: str,
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

        Create new navigation property to openShifts for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShifts"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_open_shift_details(
        self,
        group_id: str,
        openShift_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get openShifts from groups

        Args:
            group_id (string): group-id
            openShift_id (string): openShift-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if openShift_id is None:
            raise ValueError("Missing required parameter 'openShift-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShifts/{openShift_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_open_shift(
        self,
        group_id: str,
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

        Update the navigation property openShifts in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShifts/{openShift_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_open_shift_by_id(self, group_id: str, openShift_id: str) -> Any:
        """

        Delete navigation property openShifts for groups

        Args:
            group_id (string): group-id
            openShift_id (string): openShift-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if openShift_id is None:
            raise ValueError("Missing required parameter 'openShift-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShifts/{openShift_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_open_shifts_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/openShifts/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_scheduling_groups(
        self,
        group_id: str,
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

        Get schedulingGroups from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/schedulingGroups"
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
        group_id: str,
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

        Create new navigation property to schedulingGroups for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/schedulingGroups"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_scheduling_group_details(
        self,
        group_id: str,
        schedulingGroup_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get schedulingGroups from groups

        Args:
            group_id (string): group-id
            schedulingGroup_id (string): schedulingGroup-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if schedulingGroup_id is None:
            raise ValueError("Missing required parameter 'schedulingGroup-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_group_team_schedule_scheduli(
        self,
        group_id: str,
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

        Update the navigation property schedulingGroups in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_team_scheduling_group(
        self, group_id: str, schedulingGroup_id: str
    ) -> Any:
        """

        Delete navigation property schedulingGroups for groups

        Args:
            group_id (string): group-id
            schedulingGroup_id (string): schedulingGroup-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if schedulingGroup_id is None:
            raise ValueError("Missing required parameter 'schedulingGroup-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_scheduling_groups_for_team(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/schedulingGroups/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_team_shifts(
        self,
        group_id: str,
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

        Get shifts from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/shifts"
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

    def schedule_group_shifts(
        self,
        group_id: str,
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

        Create new navigation property to shifts for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/shifts"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_shifts(
        self,
        group_id: str,
        shift_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get shifts from groups

        Args:
            group_id (string): group-id
            shift_id (string): shift-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if shift_id is None:
            raise ValueError("Missing required parameter 'shift-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/shifts/{shift_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_shift_details(
        self,
        group_id: str,
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

        Update the navigation property shifts in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/shifts/{shift_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_team_shift_by_id(self, group_id: str, shift_id: str) -> Any:
        """

        Delete navigation property shifts for groups

        Args:
            group_id (string): group-id
            shift_id (string): shift-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if shift_id is None:
            raise ValueError("Missing required parameter 'shift-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/shifts/{shift_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_shifts_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/shifts/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_swap_shift_change_requests(
        self,
        group_id: str,
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

        Get swapShiftsChangeRequests from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/swapShiftsChangeRequests"
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
        group_id: str,
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

        Create new navigation property to swapShiftsChangeRequests for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/swapShiftsChangeRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_swap_shifts_change_request_by_id(
        self,
        group_id: str,
        swapShiftsChangeRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get swapShiftsChangeRequests from groups

        Args:
            group_id (string): group-id
            swapShiftsChangeRequest_id (string): swapShiftsChangeRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if swapShiftsChangeRequest_id is None:
            raise ValueError("Missing required parameter 'swapShiftsChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_swap_shifts_change_request(
        self,
        group_id: str,
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

        Update the navigation property swapShiftsChangeRequests in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_swap_shift_request(
        self, group_id: str, swapShiftsChangeRequest_id: str
    ) -> Any:
        """

        Delete navigation property swapShiftsChangeRequests for groups

        Args:
            group_id (string): group-id
            swapShiftsChangeRequest_id (string): swapShiftsChangeRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if swapShiftsChangeRequest_id is None:
            raise ValueError("Missing required parameter 'swapShiftsChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_swap_shifts_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/swapShiftsChangeRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_time_cards(
        self,
        group_id: str,
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

        Get timeCards from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = (
            f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards"
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

    def create_time_card_for_group(
        self,
        group_id: str,
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

        Create new navigation property to timeCards for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = (
            f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_time_card_schedule(
        self,
        group_id: str,
        timeCard_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeCards from groups

        Args:
            group_id (string): group-id
            timeCard_id (string): timeCard-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/{timeCard_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_time_card(
        self,
        group_id: str,
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

        Update the navigation property timeCards in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/{timeCard_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_time_card(self, group_id: str, timeCard_id: str) -> Any:
        """

        Delete navigation property timeCards for groups

        Args:
            group_id (string): group-id
            timeCard_id (string): timeCard-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/{timeCard_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def clock_out_time_card(
        self,
        group_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action clockOut

        Args:
            group_id (string): group-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/{timeCard_id}/microsoft.graph.clockOut"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def confirm_time_card(self, group_id: str, timeCard_id: str) -> Any:
        """

        Invoke action confirm

        Args:
            group_id (string): group-id
            timeCard_id (string): timeCard-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/{timeCard_id}/microsoft.graph.confirm"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def end_break_time_card(
        self,
        group_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action endBreak

        Args:
            group_id (string): group-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/{timeCard_id}/microsoft.graph.endBreak"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def start_group_team_time_card_break(
        self,
        group_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action startBreak

        Args:
            group_id (string): group-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/{timeCard_id}/microsoft.graph.startBreak"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_schedule_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def clock_in_team_schedule(
        self,
        group_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action clockIn

        Args:
            group_id (string): group-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        request_body_data = None
        request_body_data = {
            "isAtApprovedLocation": isAtApprovedLocation,
            "notes": notes,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeCards/microsoft.graph.clockIn"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_time_off_reasons_for_group(
        self,
        group_id: str,
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

        Get timeOffReasons from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffReasons"
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
        group_id: str,
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

        Create new navigation property to timeOffReasons for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffReasons"
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
        group_id: str,
        timeOffReason_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeOffReasons from groups

        Args:
            group_id (string): group-id
            timeOffReason_id (string): timeOffReason-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeOffReason_id is None:
            raise ValueError("Missing required parameter 'timeOffReason-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_time_off_reason(
        self,
        group_id: str,
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

        Update the navigation property timeOffReasons in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_time_off_reason(self, group_id: str, timeOffReason_id: str) -> Any:
        """

        Delete navigation property timeOffReasons for groups

        Args:
            group_id (string): group-id
            timeOffReason_id (string): timeOffReason-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeOffReason_id is None:
            raise ValueError("Missing required parameter 'timeOffReason-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_time_off_reasons_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffReasons/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_group_time_off_requests(
        self,
        group_id: str,
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

        Get timeOffRequests from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffRequests"
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

    def create_group_team_schedule_time_off(
        self,
        group_id: str,
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

        Create new navigation property to timeOffRequests for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_time_off_request_by_id(
        self,
        group_id: str,
        timeOffRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeOffRequests from groups

        Args:
            group_id (string): group-id
            timeOffRequest_id (string): timeOffRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeOffRequest_id is None:
            raise ValueError("Missing required parameter 'timeOffRequest-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_time_off_request(
        self,
        group_id: str,
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

        Update the navigation property timeOffRequests in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_time_off_request_by_id(
        self, group_id: str, timeOffRequest_id: str
    ) -> Any:
        """

        Delete navigation property timeOffRequests for groups

        Args:
            group_id (string): group-id
            timeOffRequest_id (string): timeOffRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeOffRequest_id is None:
            raise ValueError("Missing required parameter 'timeOffRequest-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_time_off_requests_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timeOffRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_times_off(
        self,
        group_id: str,
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

        Get timesOff from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = (
            f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timesOff"
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

    def create_times_off(
        self,
        group_id: str,
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

        Create new navigation property to timesOff for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = (
            f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timesOff"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_time_off_details(
        self,
        group_id: str,
        timeOff_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timesOff from groups

        Args:
            group_id (string): group-id
            timeOff_id (string): timeOff-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeOff_id is None:
            raise ValueError("Missing required parameter 'timeOff-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timesOff/{timeOff_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_time_off_by_id(
        self,
        group_id: str,
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

        Update the navigation property timesOff in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timesOff/{timeOff_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_time_off_from_group(self, group_id: str, timeOff_id: str) -> Any:
        """

        Delete navigation property timesOff for groups

        Args:
            group_id (string): group-id
            timeOff_id (string): timeOff-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if timeOff_id is None:
            raise ValueError("Missing required parameter 'timeOff-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timesOff/{timeOff_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_group_times_off_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/schedule/timesOff/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_tags(
        self,
        group_id: str,
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

        Get tags from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags"
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

    def add_group_team_tag(
        self,
        group_id: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        memberCount: Optional[float] = None,
        tagType: Optional[str] = None,
        teamId: Optional[str] = None,
        members: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to tags for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_team_tag_list(
        self,
        group_id: str,
        teamworkTag_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tags from groups

        Args:
            group_id (string): group-id
            teamworkTag_id (string): teamworkTag-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_group_team_tag_by_id(
        self,
        group_id: str,
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

        Update the navigation property tags in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_team_tags(self, group_id: str, teamworkTag_id: str) -> Any:
        """

        Delete navigation property tags for groups

        Args:
            group_id (string): group-id
            teamworkTag_id (string): teamworkTag-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_members_by_group(
        self,
        group_id: str,
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

        Get members from groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}/members"
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

    def create_group_team_tag_member(
        self,
        group_id: str,
        teamworkTag_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_group_team_tag_members(
        self,
        group_id: str,
        teamworkTag_id: str,
        teamworkTagMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from groups

        Args:
            group_id (string): group-id
            teamworkTag_id (string): teamworkTag-id
            teamworkTagMember_id (string): teamworkTagMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        if teamworkTagMember_id is None:
            raise ValueError("Missing required parameter 'teamworkTagMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_group_team_tag_member(
        self,
        group_id: str,
        teamworkTag_id: str,
        teamworkTagMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in groups

        Args:
            group_id (string): group-id
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
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
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
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_group_tag_member(
        self, group_id: str, teamworkTag_id: str, teamworkTagMember_id: str
    ) -> Any:
        """

        Delete navigation property members for groups

        Args:
            group_id (string): group-id
            teamworkTag_id (string): teamworkTag-id
            teamworkTagMember_id (string): teamworkTagMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        if teamworkTagMember_id is None:
            raise ValueError("Missing required parameter 'teamworkTagMember-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_tag_member_count(
        self,
        group_id: str,
        teamworkTag_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            teamworkTag_id (string): teamworkTag-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/{teamworkTag_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_tag_count(
        self, group_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            group_id (string): group-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/tags/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_group_template(
        self,
        group_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get template from groups

        Args:
            group_id (string): group-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            groups.team
        """
        if group_id is None:
            raise ValueError("Missing required parameter 'group-id'.")
        url = f"{self.main_app_client.base_url}/groups/{group_id}/team/template"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.get_group_team,
            self.create_team_from_group,
            self.delete_group_team,
            self.fetch_groups_team_all_channels,
            self.get_group_team_all_channels,
            self.get_group_team_channels_count,
            self.get_group_team_channels,
            self.create_group_channel,
            self.get_group_channels,
            self.update_group_channels,
            self.delete_group_channel,
            self.list_channel_members,
            self.create_group_team_channel_all_membe,
            self.get_channel_member_details,
            self.update_group_team_channel_member,
            self.delete_group_channel_member,
            self.count_channel_members,
            self.add_group_channel_all_members,
            self.remove_channel_members,
            self.get_files_folder,
            self.get_files_content,
            self.update_files_folder_content,
            self.delete_file_content,
            self.get_group_team_channel_members,
            self.create_group_team_channel_member,
            self.get_group_channel_members,
            self.update_channel_member,
            self.delete_member_from_channel,
            self.get_channel_member_count,
            self.add_team_channel_member,
            self.remove_channel_member,
            self.get_group_messages,
            self.create_group_channel_message,
            self.get_group_channel_messages,
            self.update_message,
            self.delete_message_in_channel,
            self.list_group_team_channel_message_hos,
            self.add_hosted_content,
            self.get_team_channel_message_hosted_con,
            self.patch_hosted_content,
            self.delete_group_team_channel_message_h,
            self.get_group_channel_message_hosted_co,
            self.update_group_team_channel_msg_hoste,
            self.delete_hosted_content,
            self.get_hosted_content_count,
            self.set_reaction_on_group_team_channel_m,
            self.soft_delete_channel_message,
            self.restore_group_channel_message,
            self.unset_reaction_on_message,
            self.get_chat_message_replies,
            self.create_reply_in_message,
            self.get_reply_messages,
            self.update_reply_message,
            self.delete_channel_message_reply_by_id,
            self.get_group_team_channel_msg_replies_h,
            self.add_reply_content,
            self.get_hosted_content_by_reply_id,
            self.update_hosted_content_reply,
            self.delete_hosted_content_by_message_id,
            self.get_group_team_channel_msg_hosted_co,
            self.update_group_team_channel_reply_hos,
            self.delete_group_team_channel_message_r,
            self.count_hosted_contents_replies,
            self.set_reaction_to_message_reply,
            self.soft_delete_channel_message_reply,
            self.undo_message_reply_soft_delete,
            self.unset_reaction_on_reply,
            self.get_reply_count,
            self.get_microsoft_graph_delta_replies,
            self.get_group_channel_message_count,
            self.get_channel_messages_delta,
            self.archive_team_channel,
            self.complete_group_channel_migration,
            self.check_user_access,
            self.provision_email_to_channel,
            self.remove_channel_email,
            self.unarchive_channel,
            self.get_channel_shared_teams,
            self.add_team_to_channel,
            self.get_shared_with_team_info,
            self.update_team_channel_sharing,
            self.delete_shared_team_channel,
            self.get_shared_channel_members,
            self.get_channel_allowed_member_by_ids,
            self.count_allowed_members_by_channel_te,
            self.get_shared_team_info,
            self.get_shared_with_teams_count_in_chann,
            self.get_group_team_tabs,
            self.create_group_tab,
            self.get_group_tabs,
            self.update_group_tab,
            self.delete_group_tab,
            self.get_teams_app_tab,
            self.get_channel_tabs_count,
            self.get_group_channel_total,
            self.get_group_team_channel_messages_all,
            self.get_retained_messages,
            self.get_group_team_data,
            self.get_group_service_errors,
            self.count_service_provisioning_errors,
            self.get_group_incoming_channels,
            self.get_incoming_channels_by_group,
            self.get_incoming_channels_count,
            self.list_group_team_apps,
            self.add_group_installed_app,
            self.get_group_installed_apps,
            self.patch_installed_apps,
            self.delete_installed_app_for_group_team,
            self.upgrade_teams_app,
            self.get_teams_app_details,
            self.get_teams_app_definition,
            self.count_group_team_apps,
            self.get_group_members,
            self.create_group_member,
            self.get_group_team_members,
            self.update_group_team_member,
            self.delete_group_member,
            self.get_group_team_member_count,
            self.add_group_team_member_action,
            self.remove_team_member_action,
            self.archive_group_team,
            self.clone_team_group,
            self.complete_group_team_migration,
            self.send_activity_notification_to_grou,
            self.unarchive_group_team,
            self.get_group_operations,
            self.create_group_team_operation,
            self.get_group_team_operations,
            self.update_group_operations,
            self.delete_group_operation,
            self.get_group_team_count,
            self.list_group_team_permission_grants,
            self.create_permission_grant,
            self.get_group_permission_grants,
            self.update_permission_grant,
            self.delete_group_permission_grant,
            self.get_group_permission_grants_count,
            self.get_group_team_picture,
            self.patch_group_team_photo,
            self.get_group_team_photo,
            self.put_group_team_photo_content,
            self.delete_group_team_photo,
            self.get_group_primary,
            self.patch_primary_channel,
            self.delete_primary_channel,
            self.fetch_team_primary_channel_members,
            self.create_primary_channel_all_members,
            self.get_group_primary_channel_member,
            self.update_team_member,
            self.delete_primary_channel_member,
            self.get_primary_channel_member_count,
            self.add_group_team_members,
            self.remove_primary_channel_members,
            self.get_group_primary_channel_folder,
            self.get_primary_channel_files_content,
            self.update_primary_channel_content,
            self.delete_group_files_folder_content,
            self.list_primary_channel_members,
            self.create_primary_channel_member_for_g,
            self.get_primary_channel_members,
            self.update_primary_channel_member,
            self.delete_member_from_primary_channel,
            self.count_primary_channel_members,
            self.add_primary_channel_member,
            self.remove_group_team_member,
            self.get_primary_channel_messages,
            self.post_primary_channel_message,
            self.get_primary_channel_message,
            self.update_primary_channel_message,
            self.delete_primary_channel_message,
            self.get_hosted_content_by_message_id,
            self.add_hosted_content_to_group_message,
            self.get_group_team_primary_channel_mess,
            self.patch_group_team_primary_channel_me,
            self.delete_message_hosted_content,
            self.get_group_team_primary_channel_msg_h,
            self.update_group_team_primary_msg_hoste,
            self.delete_group_team_primary_channel_m,
            self.count_hosted_content,
            self.set_reaction_to_chat_message,
            self.soft_delete_group_channel_message,
            self.undo_soft_delete_chat_message,
            self.unset_reaction_for_primary_channel,
            self.get_primary_channel_replies,
            self.create_reply_to_message,
            self.list_group_team_primary_channel_mes,
            self.update_primary_channel_reply,
            self.delete_reply_message,
            self.get_reply_contents,
            self.create_reply_hosted_content,
            self.get_hosted_content_reply,
            self.patch_group_team_msg_reply_hosted_co,
            self.delete_group_team_primary_channel_r,
            self.get_group_team_channel_msg_reply_hos,
            self.update_group_team_primary_channel_m,
            self.delete_group_team_primary_ch_reply_h,
            self.get_group_team_primary_channel_repl,
            self.set_reply_reaction,
            self.soft_delete_group_message_reply,
            self.undo_soft_delete_chat_message_reply,
            self.unset_reaction_to_reply,
            self.count_primary_channel_replies,
            self.get_primary_channel_replies_delta,
            self.count_primary_channel_messages,
            self.get_primary_channel_messages_delta,
            self.archive_primary_channel,
            self.complete_group_migration,
            self.check_user_access_to_group,
            self.provision_primary_email,
            self.remove_primary_channel_email,
            self.unarchive_primary_channel,
            self.get_shared_with_teams,
            self.share_primary_channel_teams,
            self.get_shared_channel_teams,
            self.update_shared_team_channel_info,
            self.remove_group_team_primary_channel_s,
            self.list_allowed_members_in_shared_chan,
            self.get_channel_team_allowed_member,
            self.count_allowed_members,
            self.get_shared_channel_team_info,
            self.get_shared_teams_count,
            self.list_group_team_primary_channel_tab,
            self.create_primary_channel_tab,
            self.get_primary_channel_tab,
            self.update_primary_channel_tab,
            self.delete_primary_channel_tab,
            self.get_primary_channel_tabs_app,
            self.count_primary_channel_tabs,
            self.get_group_schedule,
            self.update_group_schedule,
            self.delete_group_schedule,
            self.get_group_day_notes,
            self.add_day_notes_to_group_team_schedule,
            self.get_group_team_day_notes,
            self.update_day_note,
            self.delete_day_note_by_id,
            self.get_group_day_note_count,
            self.share_team_schedule,
            self.list_group_shift_requests,
            self.offer_shift_requests_to_group,
            self.get_offer_shift_request_details,
            self.update_offer_shift_request,
            self.delete_group_team_schedule_offer_sh,
            self.count_group_shift_requests,
            self.list_group_team_open_shift_change_re,
            self.create_open_shift_change_request,
            self.get_open_shift_change_request,
            self.patch_group_team_open_shift_change_r,
            self.delete_open_shift_change_request,
            self.count_open_shift_requests,
            self.get_open_shifts,
            self.open_shifts_in_group,
            self.get_open_shift_details,
            self.update_open_shift,
            self.delete_open_shift_by_id,
            self.get_open_shifts_count,
            self.get_group_scheduling_groups,
            self.create_scheduling_group,
            self.get_scheduling_group_details,
            self.patch_group_team_schedule_scheduli,
            self.delete_group_team_scheduling_group,
            self.count_scheduling_groups_for_team,
            self.get_group_team_shifts,
            self.schedule_group_shifts,
            self.get_group_shifts,
            self.update_shift_details,
            self.delete_group_team_shift_by_id,
            self.get_shifts_count,
            self.get_swap_shift_change_requests,
            self.swap_shift_requests,
            self.get_swap_shifts_change_request_by_id,
            self.update_swap_shifts_change_request,
            self.delete_swap_shift_request,
            self.get_group_swap_shifts_count,
            self.get_group_time_cards,
            self.create_time_card_for_group,
            self.get_group_time_card_schedule,
            self.update_time_card,
            self.delete_time_card,
            self.clock_out_time_card,
            self.confirm_time_card,
            self.end_break_time_card,
            self.start_group_team_time_card_break,
            self.get_team_schedule_count,
            self.clock_in_team_schedule,
            self.list_time_off_reasons_for_group,
            self.create_time_off_reasons,
            self.get_team_time_off_reasons,
            self.update_time_off_reason,
            self.delete_time_off_reason,
            self.get_team_time_off_reasons_count,
            self.list_group_time_off_requests,
            self.create_group_team_schedule_time_off,
            self.get_time_off_request_by_id,
            self.update_time_off_request,
            self.delete_time_off_request_by_id,
            self.get_team_time_off_requests_count,
            self.get_team_times_off,
            self.create_times_off,
            self.get_group_time_off_details,
            self.update_time_off_by_id,
            self.delete_time_off_from_group,
            self.get_group_times_off_count,
            self.get_group_tags,
            self.add_group_team_tag,
            self.get_group_team_tag_list,
            self.patch_group_team_tag_by_id,
            self.delete_group_team_tags,
            self.get_team_members_by_group,
            self.create_group_team_tag_member,
            self.get_group_team_tag_members,
            self.update_group_team_tag_member,
            self.delete_group_tag_member,
            self.get_team_tag_member_count,
            self.get_group_tag_count,
            self.get_group_template,
        ]
