from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class TeamworkApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def get_teamwork_info(
        self, select: Optional[List[str]] = None, expand: Optional[List[str]] = None
    ) -> Any:
        """

        Get teamwork

        Args:
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved entity

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.teamwork, important
        """
        url = f"{self.main_app_client.base_url}/teamwork"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_teamwork(
        self,
        id: Optional[str] = None,
        isTeamsEnabled: Optional[bool] = None,
        region: Optional[str] = None,
        deletedChats: Optional[List[Any]] = None,
        deletedTeams: Optional[List[Any]] = None,
        teamsAppSettings: Optional[Any] = None,
        workforceIntegrations: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update teamwork

        Args:
            id (string): The unique identifier for an entity. Read-only.
            isTeamsEnabled (boolean): Indicates whether Microsoft Teams is enabled for the organization.
            region (string): Represents the region of the organization or the tenant. The region value can be any region supported by the Teams payload. The possible values are: Americas, Europe and MiddleEast, Asia Pacific, UAE, Australia, Brazil, Canada, Switzerland, Germany, France, India, Japan, South Korea, Norway, Singapore, United Kingdom, South Africa, Sweden, Qatar, Poland, Italy, Israel, Spain, Mexico, USGov Community Cloud, USGov Community Cloud High, USGov Department of Defense, and China.
            deletedChats (array): A collection of deleted chats.
            deletedTeams (array): The deleted team.
            teamsAppSettings (string): teamsAppSettings
            workforceIntegrations (array): workforceIntegrations

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.teamwork
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "isTeamsEnabled": isTeamsEnabled,
            "region": region,
            "deletedChats": deletedChats,
            "deletedTeams": deletedTeams,
            "teamsAppSettings": teamsAppSettings,
            "workforceIntegrations": workforceIntegrations,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def list_deleted_chats(
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

        Get deletedChat

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
            teamwork.deletedChat
        """
        url = f"{self.main_app_client.base_url}/teamwork/deletedChats"
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

    def link_deleted_chats_to_teamwork(self, id: Optional[str] = None) -> Any:
        """

        Create new navigation property to deletedChats for teamwork

        Args:
            id (string): The unique identifier for an entity. Read-only.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedChat
        """
        request_body_data = None
        request_body_data = {"id": id}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedChats"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_chat(
        self,
        deletedChat_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get deletedChat

        Args:
            deletedChat_id (string): deletedChat-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedChat
        """
        if deletedChat_id is None:
            raise ValueError("Missing required parameter 'deletedChat-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedChats/{deletedChat_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_teamwork_deleted_chat(
        self, deletedChat_id: str, id: Optional[str] = None
    ) -> Any:
        """

        Update the navigation property deletedChats in teamwork

        Args:
            deletedChat_id (string): deletedChat-id
            id (string): The unique identifier for an entity. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedChat
        """
        if deletedChat_id is None:
            raise ValueError("Missing required parameter 'deletedChat-id'.")
        request_body_data = None
        request_body_data = {"id": id}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedChats/{deletedChat_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_teamwork_deleted_chat(self, deletedChat_id: str) -> Any:
        """

        Delete navigation property deletedChats for teamwork

        Args:
            deletedChat_id (string): deletedChat-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedChat
        """
        if deletedChat_id is None:
            raise ValueError("Missing required parameter 'deletedChat-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedChats/{deletedChat_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def undo_delete_chat(self, deletedChat_id: str) -> Any:
        """

        Invoke action undoDelete

        Args:
            deletedChat_id (string): deletedChat-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedChat
        """
        if deletedChat_id is None:
            raise ValueError("Missing required parameter 'deletedChat-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedChats/{deletedChat_id}/microsoft.graph.undoDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_chats_count(
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
            teamwork.deletedChat
        """
        url = f"{self.main_app_client.base_url}/teamwork/deletedChats/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_deleted_teams(
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

        List deletedTeams

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
            teamwork.deletedTeam
        """
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams"
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

    def create_teamwork_deleted_teams_link(
        self, id: Optional[str] = None, channels: Optional[List[Any]] = None
    ) -> Any:
        """

        Create new navigation property to deletedTeams for teamwork

        Args:
            id (string): The unique identifier for an entity. Read-only.
            channels (array): The channels that are either shared with this deleted team or created in this deleted team.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        request_body_data = None
        request_body_data = {"id": id, "channels": channels}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_teamwork_deleted_teams(
        self,
        deletedTeam_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get deletedTeams from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_teamwork_deleted_team(
        self,
        deletedTeam_id: str,
        id: Optional[str] = None,
        channels: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property deletedTeams in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            id (string): The unique identifier for an entity. Read-only.
            channels (array): The channels that are either shared with this deleted team or created in this deleted team.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        request_body_data = None
        request_body_data = {"id": id, "channels": channels}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_teamwork_deleted_team(self, deletedTeam_id: str) -> Any:
        """

        Delete navigation property deletedTeams for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channels(
        self,
        deletedTeam_id: str,
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

        Get channels from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels"
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

    def create_deleted_team_channels(
        self,
        deletedTeam_id: str,
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

        Create new navigation property to channels for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_team_channel(
        self,
        deletedTeam_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get channels from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_deleted_team_channel(
        self,
        deletedTeam_id: str,
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

        Update the navigation property channels in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_team_channel_by_id(self, deletedTeam_id: str, channel_id: str) -> Any:
        """

        Delete navigation property channels for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_deleted_team_channel_members(
        self,
        deletedTeam_id: str,
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

        Get allMembers from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/allMembers"
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

    def add_team_members_to_channel(
        self,
        deletedTeam_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to allMembers for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/allMembers"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_member_details(
        self,
        deletedTeam_id: str,
        channel_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allMembers from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_channel_member(
        self,
        deletedTeam_id: str,
        channel_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property allMembers in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_team_member(
        self, deletedTeam_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property allMembers for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channel_all_member(
        self,
        deletedTeam_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/allMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_microsoft_graph_members(
        self, deletedTeam_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/allMembers/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_channel_members_by_team_id(
        self, deletedTeam_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/allMembers/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_team_channel_files(
        self,
        deletedTeam_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get filesFolder from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/filesFolder"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channel_files_cont(
        self, deletedTeam_id: str, channel_id: str, format: Optional[str] = None
    ) -> Any:
        """

        Get content for the navigation property filesFolder from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            format (string): Format of the content

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/filesFolder/content"
        query_params = {k: v for k, v in [("$format", format)] if v is not None}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_deleted_team_channel_file(
        self, deletedTeam_id: str, channel_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property filesFolder in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/filesFolder/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_channel_file_content(self, deletedTeam_id: str, channel_id: str) -> Any:
        """

        Delete content for the navigation property filesFolder in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/filesFolder/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channel_members(
        self,
        deletedTeam_id: str,
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

        Get members from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/members"
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

    def create_teamwork_channel_members(
        self,
        deletedTeam_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_channel_member(
        self,
        deletedTeam_id: str,
        channel_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_member_in_channel(
        self,
        deletedTeam_id: str,
        channel_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_team_members(
        self, deletedTeam_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property members for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channel_members_co(
        self,
        deletedTeam_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_channel_member(
        self, deletedTeam_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_channel_member(
        self, deletedTeam_id: str, channel_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_team_channel_messages(
        self,
        deletedTeam_id: str,
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

        Get messages from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages"
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

    def send_team_message(
        self,
        deletedTeam_id: str,
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

        Create new navigation property to messages for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_team_channel_message(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get messages from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_channel_message(
        self,
        deletedTeam_id: str,
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

        Update the navigation property messages in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_chat_message(
        self, deletedTeam_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Delete navigation property messages for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_content_by_message(
        self,
        deletedTeam_id: str,
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

        Get hostedContents from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents"
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

    def create_deleted_team_channel_msg_hos(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_team_channel_message_ho(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_chat_message_hosted_content(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_deleted_team_channel_messag(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channel_message_me(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def put_deleted_team_channel_msg_hosted(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_hosted_content_value_by_ids(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_deleted_team_channel_message(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_on_deleted_team_messag(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_team_chat(
        self, deletedTeam_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def restore_deleted_message(
        self, deletedTeam_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.undoSoftDelete"
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
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_team_channel_replies(
        self,
        deletedTeam_id: str,
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

        Get replies from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies"
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

    def add_channel_message_reply(
        self,
        deletedTeam_id: str,
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

        Create new navigation property to replies for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_channel_message_reply(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get replies from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_message_reply(
        self,
        deletedTeam_id: str,
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

        Update the navigation property replies in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_team_message_reply(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
    ) -> Any:
        """

        Delete navigation property replies for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channel_reply_host(
        self,
        deletedTeam_id: str,
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

        Get hostedContents from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
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

    def add_reply_to_deleted_team_message(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_team_channel_message_re(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_deleted_team_channel_message(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_deleted_team_channel_msg_rep(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_content(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_deleted_team_channel_msg_hos(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_teamwork_content(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_hosted_replies(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_on_message_reply(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_team_message_reply(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def restore_message_reply(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_in_reply(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def count_team_message_replies(
        self,
        deletedTeam_id: str,
        channel_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_delta_message_replies(
        self,
        deletedTeam_id: str,
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
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/microsoft.graph.delta()"
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

    def count_deleted_channel_messages(
        self,
        deletedTeam_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_messages_delta(
        self,
        deletedTeam_id: str,
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
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/messages/microsoft.graph.delta()"
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

    def archive_deleted_team_channel(
        self,
        deletedTeam_id: str,
        channel_id: str,
        shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None,
    ) -> Any:
        """

        Invoke action archive

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/microsoft.graph.archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_channel_migration(self, deletedTeam_id: str, channel_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def has_user_access_to_channel(
        self,
        deletedTeam_id: str,
        channel_id: str,
        userId: Optional[str] = None,
        tenantId: Optional[str] = None,
        userPrincipalName: Optional[str] = None,
    ) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            userId (string): Usage: userId='@userId'
            tenantId (string): Usage: tenantId='@tenantId'
            userPrincipalName (string): Usage: userPrincipalName='@userPrincipalName'

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/microsoft.graph.doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
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

    def provision_email_channel(
        self, deletedTeam_id: str, channel_id: str
    ) -> dict[str, Any]:
        """

        Invoke action provisionEmail

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/microsoft.graph.provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_email_channel(self, deletedTeam_id: str, channel_id: str) -> Any:
        """

        Invoke action removeEmail

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/microsoft.graph.removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_team_channel_post(self, deletedTeam_id: str, channel_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/microsoft.graph.unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_teams_for_channel(
        self,
        deletedTeam_id: str,
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

        Get sharedWithTeams from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams"
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

    def share_channels_with_teams(
        self,
        deletedTeam_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to sharedWithTeams for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_teams_info(
        self,
        deletedTeam_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get sharedWithTeams from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_shared_with_teams(
        self,
        deletedTeam_id: str,
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

        Update the navigation property sharedWithTeams in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_shared_with_team_channel(
        self, deletedTeam_id: str, channel_id: str, sharedWithChannelTeamInfo_id: str
    ) -> Any:
        """

        Delete navigation property sharedWithTeams for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_shared_team_allowed_members(
        self,
        deletedTeam_id: str,
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

        Get allowedMembers from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers"
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

    def get_allowed_members_by_team_channel(
        self,
        deletedTeam_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allowedMembers from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channel_shared_tea(
        self,
        deletedTeam_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_team_details(
        self,
        deletedTeam_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_shared_teams_in_channel(
        self,
        deletedTeam_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/sharedWithTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channel_tabs(
        self,
        deletedTeam_id: str,
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

        Get tabs from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/tabs"
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

    def add_tab_to_channel(
        self,
        deletedTeam_id: str,
        channel_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to tabs for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_deleted_team_tab_info(
        self,
        deletedTeam_id: str,
        channel_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tabs from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_teams_tab(
        self,
        deletedTeam_id: str,
        channel_id: str,
        teamsTab_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property tabs in teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
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
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_teams_tab(
        self, deletedTeam_id: str, channel_id: str, teamsTab_id: str
    ) -> Any:
        """

        Delete navigation property tabs for teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_teams_app_tab_details(
        self,
        deletedTeam_id: str,
        channel_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from teamwork

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_deleted_team_tabs(
        self,
        deletedTeam_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/{channel_id}/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_deleted_team_channels_count(
        self,
        deletedTeam_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            deletedTeam_id (string): deletedTeam-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_messages(
        self,
        deletedTeam_id: str,
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
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/microsoft.graph.getAllMessages()"
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

    def get_all_retained_channel_messages(
        self,
        deletedTeam_id: str,
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
            deletedTeam_id (string): deletedTeam-id
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
            teamwork.deletedTeam
        """
        if deletedTeam_id is None:
            raise ValueError("Missing required parameter 'deletedTeam-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/{deletedTeam_id}/channels/microsoft.graph.getAllRetainedMessages()"
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

    def get_team_deleted_count(
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
            teamwork.deletedTeam
        """
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_all_deleted_team_messages(
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
            teamwork.deletedTeam
        """
        url = f"{self.main_app_client.base_url}/teamwork/deletedTeams/microsoft.graph.getAllMessages()"
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

    def send_activity_notification_to_reci(
        self,
        topic: Optional[dict[str, dict[str, Any]]] = None,
        activityType: Optional[str] = None,
        chainId: Optional[float] = None,
        previewText: Optional[dict[str, dict[str, Any]]] = None,
        teamsAppId: Optional[str] = None,
        templateParameters: Optional[List[dict[str, dict[str, Any]]]] = None,
        recipients: Optional[List[dict[str, dict[str, Any]]]] = None,
    ) -> Any:
        """

        Invoke action sendActivityNotificationToRecipients

        Args:
            topic (object): topic
            activityType (string): activityType
            chainId (number): chainId
            previewText (object): previewText
            teamsAppId (string): teamsAppId
            templateParameters (array): templateParameters
            recipients (array): recipients

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.teamwork.Actions
        """
        request_body_data = None
        request_body_data = {
            "topic": topic,
            "activityType": activityType,
            "chainId": chainId,
            "previewText": previewText,
            "teamsAppId": teamsAppId,
            "templateParameters": templateParameters,
            "recipients": recipients,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/microsoft.graph.sendActivityNotificationToRecipients"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_app_settings(
        self, select: Optional[List[str]] = None, expand: Optional[List[str]] = None
    ) -> Any:
        """

        Get teamsAppSettings

        Args:
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.teamsAppSettings
        """
        url = f"{self.main_app_client.base_url}/teamwork/teamsAppSettings"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_teams_app_settings(
        self,
        id: Optional[str] = None,
        allowUserRequestsForAppAccess: Optional[bool] = None,
        isUserPersonalScopeResourceSpecificConsentEnabled: Optional[bool] = None,
    ) -> Any:
        """

        Update teamsAppSettings

        Args:
            id (string): The unique identifier for an entity. Read-only.
            allowUserRequestsForAppAccess (boolean): Indicates whether users are allowed to request access to the unavailable Teams apps.
            isUserPersonalScopeResourceSpecificConsentEnabled (boolean): Indicates whether resource-specific consent for personal scope in Teams apps is enabled for the tenant. True indicates that Teams apps that are allowed in the tenant and require resource-specific permissions can be installed in the personal scope. False blocks the installation of any Teams app that requires resource-specific permissions in the personal scope.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.teamsAppSettings
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "allowUserRequestsForAppAccess": allowUserRequestsForAppAccess,
            "isUserPersonalScopeResourceSpecificConsentEnabled": isUserPersonalScopeResourceSpecificConsentEnabled,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/teamsAppSettings"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_teams_app_setting(self) -> Any:
        """

        Delete navigation property teamsAppSettings for teamwork

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.teamsAppSettings
        """
        url = f"{self.main_app_client.base_url}/teamwork/teamsAppSettings"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_workforce_integrations(
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

        List workforceIntegrations

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
            teamwork.workforceIntegration
        """
        url = f"{self.main_app_client.base_url}/teamwork/workforceIntegrations"
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

    def create_workforce_integration(
        self,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        apiVersion: Optional[float] = None,
        displayName: Optional[str] = None,
        eligibilityFilteringEnabledEntities: Optional[str] = None,
        encryption: Optional[dict[str, dict[str, Any]]] = None,
        isActive: Optional[bool] = None,
        supportedEntities: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Any:
        """

        Create workforceIntegration

        Args:
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            apiVersion (number): API version for the callback URL. Start with 1.
            displayName (string): Name of the workforce integration.
            eligibilityFilteringEnabledEntities (string): eligibilityFilteringEnabledEntities
            encryption (object): encryption
            isActive (boolean): Indicates whether this workforce integration is currently active and available.
            supportedEntities (string): supportedEntities
            url (string): Workforce Integration URL for callbacks from the Shifts service.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.workforceIntegration
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "apiVersion": apiVersion,
            "displayName": displayName,
            "eligibilityFilteringEnabledEntities": eligibilityFilteringEnabledEntities,
            "encryption": encryption,
            "isActive": isActive,
            "supportedEntities": supportedEntities,
            "url": url,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/workforceIntegrations"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_workforce_integration(
        self,
        workforceIntegration_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get workforceIntegration

        Args:
            workforceIntegration_id (string): workforceIntegration-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.workforceIntegration
        """
        if workforceIntegration_id is None:
            raise ValueError("Missing required parameter 'workforceIntegration-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/workforceIntegrations/{workforceIntegration_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_workforce_integration(
        self,
        workforceIntegration_id: str,
        id: Optional[str] = None,
        createdBy: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[dict[str, dict[str, Any]]] = None,
        lastModifiedDateTime: Optional[str] = None,
        apiVersion: Optional[float] = None,
        displayName: Optional[str] = None,
        eligibilityFilteringEnabledEntities: Optional[str] = None,
        encryption: Optional[dict[str, dict[str, Any]]] = None,
        isActive: Optional[bool] = None,
        supportedEntities: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Any:
        """

        Update workforceIntegration

        Args:
            workforceIntegration_id (string): workforceIntegration-id
            id (string): The unique identifier for an entity. Read-only.
            createdBy (object): createdBy
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (object): lastModifiedBy
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            apiVersion (number): API version for the callback URL. Start with 1.
            displayName (string): Name of the workforce integration.
            eligibilityFilteringEnabledEntities (string): eligibilityFilteringEnabledEntities
            encryption (object): encryption
            isActive (boolean): Indicates whether this workforce integration is currently active and available.
            supportedEntities (string): supportedEntities
            url (string): Workforce Integration URL for callbacks from the Shifts service.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.workforceIntegration
        """
        if workforceIntegration_id is None:
            raise ValueError("Missing required parameter 'workforceIntegration-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "createdBy": createdBy,
            "createdDateTime": createdDateTime,
            "lastModifiedBy": lastModifiedBy,
            "lastModifiedDateTime": lastModifiedDateTime,
            "apiVersion": apiVersion,
            "displayName": displayName,
            "eligibilityFilteringEnabledEntities": eligibilityFilteringEnabledEntities,
            "encryption": encryption,
            "isActive": isActive,
            "supportedEntities": supportedEntities,
            "url": url,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamwork/workforceIntegrations/{workforceIntegration_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_workforce_integration_by_id(self, workforceIntegration_id: str) -> Any:
        """

        Delete workforceIntegration

        Args:
            workforceIntegration_id (string): workforceIntegration-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamwork.workforceIntegration
        """
        if workforceIntegration_id is None:
            raise ValueError("Missing required parameter 'workforceIntegration-id'.")
        url = f"{self.main_app_client.base_url}/teamwork/workforceIntegrations/{workforceIntegration_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_workforce_integration_count(
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
            teamwork.workforceIntegration
        """
        url = f"{self.main_app_client.base_url}/teamwork/workforceIntegrations/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.get_teamwork_info,
            self.patch_teamwork,
            self.list_deleted_chats,
            self.link_deleted_chats_to_teamwork,
            self.get_deleted_chat,
            self.update_teamwork_deleted_chat,
            self.delete_teamwork_deleted_chat,
            self.undo_delete_chat,
            self.get_deleted_chats_count,
            self.list_deleted_teams,
            self.create_teamwork_deleted_teams_link,
            self.get_teamwork_deleted_teams,
            self.patch_teamwork_deleted_team,
            self.delete_teamwork_deleted_team,
            self.get_deleted_team_channels,
            self.create_deleted_team_channels,
            self.get_deleted_team_channel,
            self.update_deleted_team_channel,
            self.delete_team_channel_by_id,
            self.list_deleted_team_channel_members,
            self.add_team_members_to_channel,
            self.get_member_details,
            self.update_team_channel_member,
            self.delete_team_member,
            self.get_deleted_team_channel_all_member,
            self.add_microsoft_graph_members,
            self.remove_channel_members_by_team_id,
            self.list_team_channel_files,
            self.get_deleted_team_channel_files_cont,
            self.update_deleted_team_channel_file,
            self.delete_channel_file_content,
            self.get_deleted_team_channel_members,
            self.create_teamwork_channel_members,
            self.get_team_channel_member,
            self.update_member_in_channel,
            self.delete_team_members,
            self.get_deleted_team_channel_members_co,
            self.add_channel_member,
            self.remove_team_channel_member,
            self.get_deleted_team_channel_messages,
            self.send_team_message,
            self.get_deleted_team_channel_message,
            self.update_team_channel_message,
            self.delete_chat_message,
            self.get_hosted_content_by_message,
            self.create_deleted_team_channel_msg_hos,
            self.get_deleted_team_channel_message_ho,
            self.update_chat_message_hosted_content,
            self.delete_deleted_team_channel_messag,
            self.get_deleted_team_channel_message_me,
            self.put_deleted_team_channel_msg_hosted,
            self.delete_hosted_content_value_by_ids,
            self.count_deleted_team_channel_message,
            self.set_reaction_on_deleted_team_messag,
            self.soft_delete_team_chat,
            self.restore_deleted_message,
            self.unset_reaction,
            self.get_deleted_team_channel_replies,
            self.add_channel_message_reply,
            self.get_channel_message_reply,
            self.update_team_message_reply,
            self.delete_team_message_reply,
            self.get_deleted_team_channel_reply_host,
            self.add_reply_to_deleted_team_message,
            self.get_deleted_team_channel_message_re,
            self.patch_deleted_team_channel_message,
            self.delete_deleted_team_channel_msg_rep,
            self.get_team_content,
            self.update_deleted_team_channel_msg_hos,
            self.delete_teamwork_content,
            self.count_hosted_replies,
            self.set_reaction_on_message_reply,
            self.soft_delete_team_message_reply,
            self.restore_message_reply,
            self.unset_reaction_in_reply,
            self.count_team_message_replies,
            self.get_delta_message_replies,
            self.count_deleted_channel_messages,
            self.get_team_channel_messages_delta,
            self.archive_deleted_team_channel,
            self.complete_channel_migration,
            self.has_user_access_to_channel,
            self.provision_email_channel,
            self.remove_email_channel,
            self.unarchive_team_channel_post,
            self.get_shared_teams_for_channel,
            self.share_channels_with_teams,
            self.get_shared_teams_info,
            self.update_shared_with_teams,
            self.delete_shared_with_team_channel,
            self.get_shared_team_allowed_members,
            self.get_allowed_members_by_team_channel,
            self.get_deleted_team_channel_shared_tea,
            self.get_shared_team_details,
            self.count_shared_teams_in_channel,
            self.get_deleted_team_channel_tabs,
            self.add_tab_to_channel,
            self.get_deleted_team_tab_info,
            self.update_teams_tab,
            self.delete_teams_tab,
            self.get_teams_app_tab_details,
            self.count_deleted_team_tabs,
            self.get_deleted_team_channels_count,
            self.get_team_messages,
            self.get_all_retained_channel_messages,
            self.get_team_deleted_count,
            self.get_all_deleted_team_messages,
            self.send_activity_notification_to_reci,
            self.get_team_app_settings,
            self.update_teams_app_settings,
            self.delete_teams_app_setting,
            self.list_workforce_integrations,
            self.create_workforce_integration,
            self.get_workforce_integration,
            self.update_workforce_integration,
            self.delete_workforce_integration_by_id,
            self.get_workforce_integration_count,
        ]
