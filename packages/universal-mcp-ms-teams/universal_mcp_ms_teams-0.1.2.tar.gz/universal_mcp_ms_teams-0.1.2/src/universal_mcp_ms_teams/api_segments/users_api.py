from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class UsersApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def list_user_chats(
        self,
        user_id: str,
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

        List chats

        Args:
            user_id (string): user-id
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
            users.chat, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats"
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

    def create_user_chat_link(
        self,
        user_id: str,
        id: Optional[str] = None,
        chatType: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        isHiddenForAllMembers: Optional[bool] = None,
        lastUpdatedDateTime: Optional[str] = None,
        onlineMeetingInfo: Optional[dict[str, dict[str, Any]]] = None,
        tenantId: Optional[str] = None,
        topic: Optional[str] = None,
        viewpoint: Optional[dict[str, dict[str, Any]]] = None,
        webUrl: Optional[str] = None,
        installedApps: Optional[List[Any]] = None,
        lastMessagePreview: Optional[Any] = None,
        members: Optional[List[Any]] = None,
        messages: Optional[List[Any]] = None,
        permissionGrants: Optional[List[Any]] = None,
        pinnedMessages: Optional[List[Any]] = None,
        tabs: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to chats for users

        Args:
            user_id (string): user-id
            id (string): The unique identifier for an entity. Read-only.
            chatType (string): chatType
            createdDateTime (string): Date and time at which the chat was created. Read-only.
            isHiddenForAllMembers (boolean): Indicates whether the chat is hidden for all its members. Read-only.
            lastUpdatedDateTime (string): Date and time at which the chat was renamed or the list of members was last changed. Read-only.
            onlineMeetingInfo (object): onlineMeetingInfo
            tenantId (string): The identifier of the tenant in which the chat was created. Read-only.
            topic (string): (Optional) Subject or topic for the chat. Only available for group chats.
            viewpoint (object): viewpoint
            webUrl (string): The URL for the chat in Microsoft Teams. The URL should be treated as an opaque blob, and not parsed. Read-only.
            installedApps (array): A collection of all the apps in the chat. Nullable.
            lastMessagePreview (string): lastMessagePreview
            members (array): A collection of all the members in the chat. Nullable.
            messages (array): A collection of all the messages in the chat. Nullable.
            permissionGrants (array): A collection of permissions granted to apps for the chat.
            pinnedMessages (array): A collection of all the pinned messages in the chat. Nullable.
            tabs (array): A collection of all the tabs in the chat. Nullable.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "chatType": chatType,
            "createdDateTime": createdDateTime,
            "isHiddenForAllMembers": isHiddenForAllMembers,
            "lastUpdatedDateTime": lastUpdatedDateTime,
            "onlineMeetingInfo": onlineMeetingInfo,
            "tenantId": tenantId,
            "topic": topic,
            "viewpoint": viewpoint,
            "webUrl": webUrl,
            "installedApps": installedApps,
            "lastMessagePreview": lastMessagePreview,
            "members": members,
            "messages": messages,
            "permissionGrants": permissionGrants,
            "pinnedMessages": pinnedMessages,
            "tabs": tabs,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_chat_details(
        self,
        user_id: str,
        chat_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get chat

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_chat(
        self,
        user_id: str,
        chat_id: str,
        id: Optional[str] = None,
        chatType: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        isHiddenForAllMembers: Optional[bool] = None,
        lastUpdatedDateTime: Optional[str] = None,
        onlineMeetingInfo: Optional[dict[str, dict[str, Any]]] = None,
        tenantId: Optional[str] = None,
        topic: Optional[str] = None,
        viewpoint: Optional[dict[str, dict[str, Any]]] = None,
        webUrl: Optional[str] = None,
        installedApps: Optional[List[Any]] = None,
        lastMessagePreview: Optional[Any] = None,
        members: Optional[List[Any]] = None,
        messages: Optional[List[Any]] = None,
        permissionGrants: Optional[List[Any]] = None,
        pinnedMessages: Optional[List[Any]] = None,
        tabs: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property chats in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            id (string): The unique identifier for an entity. Read-only.
            chatType (string): chatType
            createdDateTime (string): Date and time at which the chat was created. Read-only.
            isHiddenForAllMembers (boolean): Indicates whether the chat is hidden for all its members. Read-only.
            lastUpdatedDateTime (string): Date and time at which the chat was renamed or the list of members was last changed. Read-only.
            onlineMeetingInfo (object): onlineMeetingInfo
            tenantId (string): The identifier of the tenant in which the chat was created. Read-only.
            topic (string): (Optional) Subject or topic for the chat. Only available for group chats.
            viewpoint (object): viewpoint
            webUrl (string): The URL for the chat in Microsoft Teams. The URL should be treated as an opaque blob, and not parsed. Read-only.
            installedApps (array): A collection of all the apps in the chat. Nullable.
            lastMessagePreview (string): lastMessagePreview
            members (array): A collection of all the members in the chat. Nullable.
            messages (array): A collection of all the messages in the chat. Nullable.
            permissionGrants (array): A collection of permissions granted to apps for the chat.
            pinnedMessages (array): A collection of all the pinned messages in the chat. Nullable.
            tabs (array): A collection of all the tabs in the chat. Nullable.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "chatType": chatType,
            "createdDateTime": createdDateTime,
            "isHiddenForAllMembers": isHiddenForAllMembers,
            "lastUpdatedDateTime": lastUpdatedDateTime,
            "onlineMeetingInfo": onlineMeetingInfo,
            "tenantId": tenantId,
            "topic": topic,
            "viewpoint": viewpoint,
            "webUrl": webUrl,
            "installedApps": installedApps,
            "lastMessagePreview": lastMessagePreview,
            "members": members,
            "messages": messages,
            "permissionGrants": permissionGrants,
            "pinnedMessages": pinnedMessages,
            "tabs": tabs,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_chat(self, user_id: str, chat_id: str) -> Any:
        """

        Delete navigation property chats for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_installed_apps(
        self,
        user_id: str,
        chat_id: str,
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

        Get installedApps from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps"
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

    def create_installed_app(
        self,
        user_id: str,
        chat_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to installedApps for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (object): consentedPermissionSet
            teamsApp (string): teamsApp
            teamsAppDefinition (string): teamsAppDefinition

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_installed_apps_by_user_chat(
        self,
        user_id: str,
        chat_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get installedApps from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_chat_installed_app(
        self,
        user_id: str,
        chat_id: str,
        teamsAppInstallation_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property installedApps in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_chat_app(
        self, user_id: str, chat_id: str, teamsAppInstallation_id: str
    ) -> Any:
        """

        Delete navigation property installedApps for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def upgrade_chat_app(
        self,
        user_id: str,
        chat_id: str,
        teamsAppInstallation_id: str,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action upgrade

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            consentedPermissionSet (object): consentedPermissionSet

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        request_body_data = None
        request_body_data = {"consentedPermissionSet": consentedPermissionSet}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}/microsoft.graph.upgrade"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_teams_app(
        self,
        user_id: str,
        chat_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def fetch_chat_teams_app_definition(
        self,
        user_id: str,
        chat_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsAppDefinition from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}/teamsAppDefinition"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_installed_apps(
        self,
        user_id: str,
        chat_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/installedApps/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_chat_last_message_preview(
        self,
        user_id: str,
        chat_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get lastMessagePreview from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/lastMessagePreview"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_last_message_preview(
        self,
        user_id: str,
        chat_id: str,
        id: Optional[str] = None,
        body: Optional[dict[str, dict[str, Any]]] = None,
        createdDateTime: Optional[str] = None,
        eventDetail: Optional[dict[str, dict[str, Any]]] = None,
        from_: Optional[Any] = None,
        isDeleted: Optional[bool] = None,
        messageType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property lastMessagePreview in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            id (string): The unique identifier for an entity. Read-only.
            body (object): body
            createdDateTime (string): Date time object representing the time at which message was created.
            eventDetail (object): eventDetail
            from_ (string): from
            isDeleted (boolean): If set to true, the original message has been deleted.
            messageType (string): messageType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "body": body,
            "createdDateTime": createdDateTime,
            "eventDetail": eventDetail,
            "from": from_,
            "isDeleted": isDeleted,
            "messageType": messageType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/lastMessagePreview"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_last_message_preview(self, user_id: str, chat_id: str) -> Any:
        """

        Delete navigation property lastMessagePreview for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/lastMessagePreview"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_user_chat_members(
        self,
        user_id: str,
        chat_id: str,
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

        Get members from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/members"
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

    def create_chat_member(
        self,
        user_id: str,
        chat_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name of the user.
            roles (array): The roles for that user. This property contains more qualifiers only when relevant - for example, if the member has owner privileges, the roles property contains owner as one of the values. Similarly, if the member is an in-tenant guest, the roles property contains guest as one of the values. A basic member shouldn't have any values specified in the roles property. An Out-of-tenant external member is assigned the owner role.
            visibleHistoryStartDateTime (string): The timestamp denoting how far back a conversation's history is shared with the conversation member. This property is settable only for members of a chat.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_chat_members(
        self,
        user_id: str,
        chat_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_chat_members(
        self,
        user_id: str,
        chat_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_chat_member(
        self, user_id: str, chat_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property members for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_member_count(
        self,
        user_id: str,
        chat_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_microsoft_graph_member_to_chat(
        self, user_id: str, chat_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_chat_member_post(
        self, user_id: str, chat_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_messages_by_user_chat(
        self,
        user_id: str,
        chat_id: str,
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

        Get messages from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = (
            f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages"
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

    def create_user_chat_message(
        self,
        user_id: str,
        chat_id: str,
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

        Create new navigation property to messages for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = (
            f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_chat_messages(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get messages from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_chat_message(
        self,
        user_id: str,
        chat_id: str,
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

        Update the navigation property messages in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_chat_message_by_id(
        self, user_id: str, chat_id: str, chatMessage_id: str
    ) -> Any:
        """

        Delete navigation property messages for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_user_chat_message_hosted_conten(
        self,
        user_id: str,
        chat_id: str,
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

        Get hostedContents from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents"
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

    def create_user_chat_message_hosted_con(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            id (string): The unique identifier for an entity. Read-only.
            contentBytes (string): Write only. Bytes for the hosted content (such as images).
            contentType (string): Write only. Content type. such as image/png, image/jpg.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_messages_chat_hosted_content_by(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_chat_message_hosted_cont(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_chat_message_hosted_content(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_message_hosted_content_val(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_chat_message_hosted_con(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_user_chat_message_hosted_con(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_chat_message_hosted_contents(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_on_chat_message_by_user(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_user_chat_message(
        self, user_id: str, chat_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_chat_message_soft_delete(
        self, user_id: str, chat_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_chat_message_reaction(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_replies_from_user_chat_message(
        self,
        user_id: str,
        chat_id: str,
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

        Get replies from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies"
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

    def create_reply_link(
        self,
        user_id: str,
        chat_id: str,
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

        Create new navigation property to replies for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_replies_from_chat_message(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get replies from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_message_reply_by_id(
        self,
        user_id: str,
        chat_id: str,
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

        Update the navigation property replies in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_chat_reply(
        self, user_id: str, chat_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Delete navigation property replies for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_message_reply_hosted_contents(
        self,
        user_id: str,
        chat_id: str,
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

        Get hostedContents from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
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

    def create_user_chat_message_reply_host(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_chat_message_reply_hosted_c(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_chat_message_reply_hoste(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_reply_hosted_content(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_content(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_chat_message_reply_host(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_user_chat_reply_hosted_conte(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_chat_message_replies(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_chat_message_reaction_reply(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_chat_message_reply_by_id(
        self, user_id: str, chat_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_chat_message_reply_soft_delete(
        self, user_id: str, chat_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_chat_message_reply_reaction_u(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_chat_message_replies_count(
        self,
        user_id: str,
        chat_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_user_chat_message_reply_delta(
        self,
        user_id: str,
        chat_id: str,
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
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/{chatMessage_id}/replies/microsoft.graph.delta()"
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

    def get_chat_message_count(
        self,
        user_id: str,
        chat_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_chats_delta_messages(
        self,
        user_id: str,
        chat_id: str,
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
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/messages/microsoft.graph.delta()"
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

    def hide_user_chat(
        self, user_id: str, chat_id: str, user: Optional[Any] = None
    ) -> Any:
        """

        Invoke action hideForUser

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            user (string): user

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"user": user}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/microsoft.graph.hideForUser"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def mark_chat_read_for_user(
        self, user_id: str, chat_id: str, user: Optional[Any] = None
    ) -> Any:
        """

        Invoke action markChatReadForUser

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            user (string): user

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"user": user}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/microsoft.graph.markChatReadForUser"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def mark_chat_unread_for_user(
        self,
        user_id: str,
        chat_id: str,
        user: Optional[Any] = None,
        lastMessageReadDateTime: Optional[str] = None,
    ) -> Any:
        """

        Invoke action markChatUnreadForUser

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            user (string): user
            lastMessageReadDateTime (string): lastMessageReadDateTime

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {
            "user": user,
            "lastMessageReadDateTime": lastMessageReadDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/microsoft.graph.markChatUnreadForUser"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def send_activity_notification_to_chat(
        self,
        user_id: str,
        chat_id: str,
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
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/microsoft.graph.sendActivityNotification"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unhide_chat_for_user(
        self, user_id: str, chat_id: str, user: Optional[Any] = None
    ) -> Any:
        """

        Invoke action unhideForUser

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            user (string): user

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"user": user}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/microsoft.graph.unhideForUser"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def fetch_user_chat_permissions(
        self,
        user_id: str,
        chat_id: str,
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

        Get permissionGrants from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/permissionGrants"
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

    def grant_chat_permission(
        self,
        user_id: str,
        chat_id: str,
        id: Optional[str] = None,
        deletedDateTime: Optional[str] = None,
        clientAppId: Optional[str] = None,
        clientId: Optional[str] = None,
        permission: Optional[str] = None,
        permissionType: Optional[str] = None,
        resourceAppId: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to permissionGrants for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/permissionGrants"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_chat_permission_grant_by_id(
        self,
        user_id: str,
        chat_id: str,
        resourceSpecificPermissionGrant_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get permissionGrants from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_chat_permission_grant(
        self,
        user_id: str,
        chat_id: str,
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

        Update the navigation property permissionGrants in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_permission_grant(
        self, user_id: str, chat_id: str, resourceSpecificPermissionGrant_id: str
    ) -> Any:
        """

        Delete navigation property permissionGrants for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_user_chat_permissions(
        self,
        user_id: str,
        chat_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/permissionGrants/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_pinned_messages(
        self,
        user_id: str,
        chat_id: str,
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

        Get pinnedMessages from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/pinnedMessages"
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

    def create_pinned_message(
        self,
        user_id: str,
        chat_id: str,
        id: Optional[str] = None,
        message: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to pinnedMessages for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            id (string): The unique identifier for an entity. Read-only.
            message (string): message

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"id": id, "message": message}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/pinnedMessages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_pinned_messages_for_user_chat(
        self,
        user_id: str,
        chat_id: str,
        pinnedChatMessageInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get pinnedMessages from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            pinnedChatMessageInfo_id (string): pinnedChatMessageInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if pinnedChatMessageInfo_id is None:
            raise ValueError("Missing required parameter 'pinnedChatMessageInfo-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/pinnedMessages/{pinnedChatMessageInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_pinned_messages(
        self,
        user_id: str,
        chat_id: str,
        pinnedChatMessageInfo_id: str,
        id: Optional[str] = None,
        message: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property pinnedMessages in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            pinnedChatMessageInfo_id (string): pinnedChatMessageInfo-id
            id (string): The unique identifier for an entity. Read-only.
            message (string): message

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if pinnedChatMessageInfo_id is None:
            raise ValueError("Missing required parameter 'pinnedChatMessageInfo-id'.")
        request_body_data = None
        request_body_data = {"id": id, "message": message}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/pinnedMessages/{pinnedChatMessageInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_chat_pinned_message(
        self, user_id: str, chat_id: str, pinnedChatMessageInfo_id: str
    ) -> Any:
        """

        Delete navigation property pinnedMessages for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            pinnedChatMessageInfo_id (string): pinnedChatMessageInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if pinnedChatMessageInfo_id is None:
            raise ValueError("Missing required parameter 'pinnedChatMessageInfo-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/pinnedMessages/{pinnedChatMessageInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_pinned_chat_message_details(
        self,
        user_id: str,
        chat_id: str,
        pinnedChatMessageInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get message from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            pinnedChatMessageInfo_id (string): pinnedChatMessageInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if pinnedChatMessageInfo_id is None:
            raise ValueError("Missing required parameter 'pinnedChatMessageInfo-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/pinnedMessages/{pinnedChatMessageInfo_id}/message"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_pinned_message_count(
        self,
        user_id: str,
        chat_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/pinnedMessages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_user_chat_tabs(
        self,
        user_id: str,
        chat_id: str,
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

        Get tabs from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/tabs"
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

    def create_user_chat_tab(
        self,
        user_id: str,
        chat_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to tabs for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_tabs_for_user(
        self,
        user_id: str,
        chat_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tabs from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_tabs(
        self,
        user_id: str,
        chat_id: str,
        teamsTab_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property tabs in users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_tab(self, user_id: str, chat_id: str, teamsTab_id: str) -> Any:
        """

        Delete navigation property tabs for users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_teams_app_info(
        self,
        user_id: str,
        chat_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from users

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_tab_count(
        self,
        user_id: str,
        chat_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/{chat_id}/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_chat_count_by_user(
        self, user_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_user_chat_messages(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/microsoft.graph.getAllMessages()"
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

    def get_retained_messages_by_user(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.chat
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/chats/microsoft.graph.getAllRetainedMessages()"
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

    def list_user_joined_teams(
        self,
        user_id: str,
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

        Get joinedTeams from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams"
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

    def create_user_joined_team_relation(
        self,
        user_id: str,
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

        Create new navigation property to joinedTeams for users

        Args:
            user_id (string): user-id
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
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_joined_teams_by_user(
        self,
        user_id: str,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get joinedTeams from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_team_association(
        self,
        user_id: str,
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

        Update the navigation property joinedTeams in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team(self, user_id: str, team_id: str) -> Any:
        """

        Delete navigation property joinedTeams for users

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_user_joined_teams_channels(
        self,
        user_id: str,
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

        Get allChannels from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/allChannels"
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

    def get_channels_by_user_team(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allChannels from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/allChannels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channels_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/allChannels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_channels_by_user_team_id(
        self,
        user_id: str,
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

        Get channels from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels"
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

    def create_user_channel_link(
        self,
        user_id: str,
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

        Create new navigation property to channels for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_channels_from_user_team(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get channels from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_channel(
        self,
        user_id: str,
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

        Update the navigation property channels in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_channel(self, user_id: str, team_id: str, channel_id: str) -> Any:
        """

        Delete navigation property channels for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_channel_members(
        self,
        user_id: str,
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

        Get allMembers from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/allMembers"
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

    def create_user_team_channel_members(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to allMembers for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/allMembers"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_conversation_members(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allMembers from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_conversation_member(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property allMembers in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_channel_conversat(
        self, user_id: str, team_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property allMembers for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_channel_members_count(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/allMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_microsoft_graph_member(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        values: Optional[List[Any]] = None,
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/allMembers/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_channel_all_members(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        values: Optional[List[Any]] = None,
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/allMembers/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_files_folder_details(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get filesFolder from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/filesFolder"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_files_content(
        self, user_id: str, team_id: str, channel_id: str, format: Optional[str] = None
    ) -> Any:
        """

        Get content for the navigation property filesFolder from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            format (string): Format of the content

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/filesFolder/content"
        query_params = {k: v for k, v in [("$format", format)] if v is not None}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_file_content(
        self, user_id: str, team_id: str, channel_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property filesFolder in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/filesFolder/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_files_folder_content(
        self, user_id: str, team_id: str, channel_id: str
    ) -> Any:
        """

        Delete content for the navigation property filesFolder in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/filesFolder/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_channel_team_member(
        self,
        user_id: str,
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

        Get members from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/members"
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

    def add_member_to_channel(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_joined_team_channel_member(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_conversation_member(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_joined_team_channel_mem(
        self, user_id: str, team_id: str, channel_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property members for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_members_count(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_user_team_channel_member_by_grap(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        values: Optional[List[Any]] = None,
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_channel_member_by_graph_id(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        values: Optional[List[Any]] = None,
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_user_team_channel_messages(
        self,
        user_id: str,
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

        Get messages from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages"
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

    def create_message_in_channel(
        self,
        user_id: str,
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

        Create new navigation property to messages for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_channel_message(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get messages from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_chat_message(
        self,
        user_id: str,
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

        Update the navigation property messages in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_team_message(
        self, user_id: str, team_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Delete navigation property messages for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_user_chat_message_hosted_conte(
        self,
        user_id: str,
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

        Get hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents"
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

    def create_user_team_channel_message_ho(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_team_channel_message_hoste(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_team_channel_message_hos(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_channel_message_ho(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_user_channel_message_hosted_con(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_channel_message_ho(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_user_team_channel_msg_hosted(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_message_hosted_contents_co(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_chat_message_reaction(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_channel_message_post(
        self, user_id: str, team_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def restore_chat_message_from_soft_dele(
        self, user_id: str, team_id: str, channel_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_chat_reaction(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_channel_message_replies_by_ids(
        self,
        user_id: str,
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

        Get replies from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies"
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

    def add_message_reply(
        self,
        user_id: str,
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

        Create new navigation property to replies for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_reply_message(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get replies from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_reply_to_message(
        self,
        user_id: str,
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

        Update the navigation property replies in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_chat_message_reply(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
    ) -> Any:
        """

        Delete navigation property replies for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_user_team_channel_message_repl(
        self,
        user_id: str,
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

        Get hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
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

    def create_reply_content(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_team_channel_reply_hosted_c(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_hosted_content_message(
        self,
        user_id: str,
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

        Update the navigation property hostedContents in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_channel_message_re(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_user_team_channel_message_reply(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_reply_hosted_content_value(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_user_team_channel_msg_reply_h(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_message_reply_hosted_conte(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_for_message_reply(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_channel_message_reply_b(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_soft_delete_replies(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_from_message_reply(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_replies_count(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_channel_message_delta_replies(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/{chatMessage_id}/replies/microsoft.graph.delta()"
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

    def count_user_team_channel_messages(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_user_team_channel_message_delta(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/messages/microsoft.graph.delta()"
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

    def archive_channel(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None,
    ) -> Any:
        """

        Invoke action archive

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/microsoft.graph.archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_migration_channel(
        self, user_id: str, team_id: str, channel_id: str
    ) -> Any:
        """

        Invoke action completeMigration

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def check_user_channel_access(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        userId: Optional[str] = None,
        tenantId: Optional[str] = None,
        userPrincipalName: Optional[str] = None,
    ) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/microsoft.graph.doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
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

    def provision_channel_email(
        self, user_id: str, team_id: str, channel_id: str
    ) -> dict[str, Any]:
        """

        Invoke action provisionEmail

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/microsoft.graph.provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_email_from_channel(
        self, user_id: str, team_id: str, channel_id: str
    ) -> Any:
        """

        Invoke action removeEmail

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/microsoft.graph.removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def post_unarchive_channel_for_user_tea(
        self, user_id: str, team_id: str, channel_id: str
    ) -> Any:
        """

        Invoke action unarchive

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/microsoft.graph.unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_teams(
        self,
        user_id: str,
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

        Get sharedWithTeams from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams"
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

    def add_team_to_shared_channel(
        self,
        user_id: str,
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

        Create new navigation property to sharedWithTeams for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_teams_details(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get sharedWithTeams from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_shared_channel_team_info(
        self,
        user_id: str,
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

        Update the navigation property sharedWithTeams in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_shared_with_team_info(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
    ) -> Any:
        """

        Delete navigation property sharedWithTeams for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_shared_channel_allowed_members(
        self,
        user_id: str,
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

        Get allowedMembers from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers"
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

    def get_allowed_members_in_channel(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allowedMembers from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_with_channel_allowed_mem(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_team_channels(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams/{sharedWithChannelTeamInfo_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_team_channels_count(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/sharedWithTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_user_team_channel_tabs(
        self,
        user_id: str,
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

        Get tabs from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/tabs"
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

    def add_tab_to_user_channel(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to tabs for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_tab_details(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tabs from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_tab(
        self,
        user_id: str,
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

        Update the navigation property tabs in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_tab(
        self, user_id: str, team_id: str, channel_id: str, teamsTab_id: str
    ) -> Any:
        """

        Delete navigation property tabs for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_teams_tab_details(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_tabs_count(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/{channel_id}/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_channel_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_user_team_all_channel_messages(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/microsoft.graph.getAllMessages()"
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

    def get_all_retained_team_messages(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/channels/microsoft.graph.getAllRetainedMessages()"
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

    def get_user_group_details(
        self,
        user_id: str,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get group from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/group"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_service_provisioning_errors(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/group/serviceProvisioningErrors"
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

    def get_team_service_errors_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/group/serviceProvisioningErrors/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_incoming_channels(
        self,
        user_id: str,
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

        Get incomingChannels from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/incomingChannels"
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

    def get_team_channel(
        self,
        user_id: str,
        team_id: str,
        channel_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get incomingChannels from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            channel_id (string): channel-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if channel_id is None:
            raise ValueError("Missing required parameter 'channel-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/incomingChannels/{channel_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_incoming_channels(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/incomingChannels/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_installed_apps_for_team(
        self,
        user_id: str,
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

        Get installedApps from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps"
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

    def install_app_for_team(
        self,
        user_id: str,
        team_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to installedApps for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_team_installed_app_by_id(
        self,
        user_id: str,
        team_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get installedApps from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_teams_app_installation(
        self,
        user_id: str,
        team_id: str,
        teamsAppInstallation_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property installedApps in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_app_installation(
        self, user_id: str, team_id: str, teamsAppInstallation_id: str
    ) -> Any:
        """

        Delete navigation property installedApps for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def upgrade_app_installation(
        self,
        user_id: str,
        team_id: str,
        teamsAppInstallation_id: str,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action upgrade

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            consentedPermissionSet (object): consentedPermissionSet

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        request_body_data = None
        request_body_data = {"consentedPermissionSet": consentedPermissionSet}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps/{teamsAppInstallation_id}/microsoft.graph.upgrade"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_app_details(
        self,
        user_id: str,
        team_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps/{teamsAppInstallation_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_app_installation_details(
        self,
        user_id: str,
        team_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsAppDefinition from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps/{teamsAppInstallation_id}/teamsAppDefinition"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_user_installed_apps(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/installedApps/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_member_list_for_user_team(
        self,
        user_id: str,
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

        Get members from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/members"
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

    def create_user_team_member(
        self,
        user_id: str,
        team_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_members_data(
        self,
        user_id: str,
        team_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_team_member(
        self,
        user_id: str,
        team_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_conversation_member_from_us(
        self, user_id: str, team_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property members for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_team_members(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_team_member_to_joined_team(
        self, user_id: str, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            user_id (string): user-id
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_member_from_user(
        self, user_id: str, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            user_id (string): user-id
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def archive_team_membership(
        self,
        user_id: str,
        team_id: str,
        shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None,
    ) -> Any:
        """

        Invoke action archive

        Args:
            user_id (string): user-id
            team_id (string): team-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/microsoft.graph.archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def clone_team_by_graph(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/microsoft.graph.clone"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_migration_team(self, user_id: str, team_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def send_activity_to_team(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/microsoft.graph.sendActivityNotification"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_team_membership(self, user_id: str, team_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/microsoft.graph.unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_team_operations(
        self,
        user_id: str,
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

        Get operations from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/operations"
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

    def add_team_operation(
        self,
        user_id: str,
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

        Create new navigation property to operations for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/operations"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_operations(
        self,
        user_id: str,
        team_id: str,
        teamsAsyncOperation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get operations from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsAsyncOperation_id (string): teamsAsyncOperation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAsyncOperation_id is None:
            raise ValueError("Missing required parameter 'teamsAsyncOperation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/operations/{teamsAsyncOperation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_async_operation(
        self,
        user_id: str,
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

        Update the navigation property operations in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/operations/{teamsAsyncOperation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_async_team_operation(
        self, user_id: str, team_id: str, teamsAsyncOperation_id: str
    ) -> Any:
        """

        Delete navigation property operations for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsAsyncOperation_id (string): teamsAsyncOperation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsAsyncOperation_id is None:
            raise ValueError("Missing required parameter 'teamsAsyncOperation-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/operations/{teamsAsyncOperation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_operations_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/operations/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_permission_grants(
        self,
        user_id: str,
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

        Get permissionGrants from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/permissionGrants"
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

    def grant_user_permission(
        self,
        user_id: str,
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

        Create new navigation property to permissionGrants for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/permissionGrants"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_permission_grants(
        self,
        user_id: str,
        team_id: str,
        resourceSpecificPermissionGrant_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get permissionGrants from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_permission_grant(
        self,
        user_id: str,
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

        Update the navigation property permissionGrants in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_permission_grant(
        self, user_id: str, team_id: str, resourceSpecificPermissionGrant_id: str
    ) -> Any:
        """

        Delete navigation property permissionGrants for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_permission_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/permissionGrants/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_photo_from_user(
        self,
        user_id: str,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get photo from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/photo"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_team_photo(
        self,
        user_id: str,
        team_id: str,
        id: Optional[str] = None,
        height: Optional[float] = None,
        width: Optional[float] = None,
    ) -> Any:
        """

        Update the navigation property photo in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            id (string): The unique identifier for an entity. Read-only.
            height (number): The height of the photo. Read-only.
            width (number): The width of the photo. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"id": id, "height": height, "width": width}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/photo"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def get_team_photo(self, user_id: str, team_id: str) -> Any:
        """

        Get media content for the navigation property photo from users

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/photo/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_photo(
        self, user_id: str, team_id: str, body_content: bytes
    ) -> Any:
        """

        Update media content for the navigation property photo in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/photo/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_team_photo(self, user_id: str, team_id: str) -> Any:
        """

        Delete media content for the navigation property photo in users

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/photo/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel(
        self,
        user_id: str,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get primaryChannel from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_primary_channel(
        self,
        user_id: str,
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

        Update the navigation property primaryChannel in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_primary_channel_from_team(self, user_id: str, team_id: str) -> Any:
        """

        Delete navigation property primaryChannel for users

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_team_members(
        self,
        user_id: str,
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

        Get allMembers from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/allMembers"
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

    def add_team_members(
        self,
        user_id: str,
        team_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to allMembers for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/allMembers"
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
        user_id: str,
        team_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allMembers from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_joined_team_primary_chan(
        self,
        user_id: str,
        team_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property allMembers in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def remove_user_team_primary_channel_me(
        self, user_id: str, team_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property allMembers for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/allMembers/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_user_team_channel_members(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/allMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_team_member(
        self, user_id: str, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            user_id (string): user-id
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/allMembers/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_member_from_channel(
        self, user_id: str, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            user_id (string): user-id
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/allMembers/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_team_channel_files_folder(
        self,
        user_id: str,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get filesFolder from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/filesFolder"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_files_content(
        self, user_id: str, team_id: str, format: Optional[str] = None
    ) -> Any:
        """

        Get content for the navigation property filesFolder from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            format (string): Format of the content

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/filesFolder/content"
        query_params = {k: v for k, v in [("$format", format)] if v is not None}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_file_content(
        self, user_id: str, team_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property filesFolder in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/filesFolder/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_content_folder(self, user_id: str, team_id: str) -> Any:
        """

        Delete content for the navigation property filesFolder in users

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/filesFolder/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_team_channel_members(
        self,
        user_id: str,
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

        Get members from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/members"
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

    def add_member_to_primary_channel(
        self,
        user_id: str,
        team_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_channel_members(
        self,
        user_id: str,
        team_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_members(
        self,
        user_id: str,
        team_id: str,
        conversationMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_joined_team_primary_cha(
        self, user_id: str, team_id: str, conversationMember_id: str
    ) -> Any:
        """

        Delete navigation property members for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_members_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_member_to_primary_channel_team(
        self, user_id: str, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            user_id (string): user-id
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/members/microsoft.graph.add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_member(
        self, user_id: str, team_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            user_id (string): user-id
            team_id (string): team-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/members/microsoft.graph.remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_team_channel_messages(
        self,
        user_id: str,
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

        Get messages from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages"
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

    def create_message_in_primary_channel(
        self,
        user_id: str,
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

        Create new navigation property to messages for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_message(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get messages from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_message_by_id(
        self,
        user_id: str,
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

        Update the navigation property messages in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_message_in_primary_channel(
        self, user_id: str, team_id: str, chatMessage_id: str
    ) -> Any:
        """

        Delete navigation property messages for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_user_team_primary_channel_messa(
        self,
        user_id: str,
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

        Get hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents"
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

    def create_user_team_message_hosted_con(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_joined_team_primary_channe(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_message_hosted_content(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_primary_channel_ms(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_user_team_primary_channel_msg_ho(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_primary_channel_ms(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_user_team_channel_content(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_primary_channel_msg_hosted_coun(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_reaction_on_primary_channel_mes(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_message(
        self, user_id: str, team_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def user_joined_team_primary_channel_me(
        self, user_id: str, team_id: str, chatMessage_id: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_reaction_for_message(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_user_joined_team_primary_chann(
        self,
        user_id: str,
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

        Get replies from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies"
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

    def create_reply(
        self,
        user_id: str,
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

        Create new navigation property to replies for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_channel_message_reply_by_ids(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get replies from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_channel_reply_by_id(
        self,
        user_id: str,
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

        Update the navigation property replies in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_joined_team_channel_mes(
        self, user_id: str, team_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Delete navigation property replies for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_replies_hosted_contents(
        self,
        user_id: str,
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

        Get hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
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

    def add_hosted_content_reply(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_team_reply_hosted_content_b(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_channel_reply_hosted_content(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_joined_team_channel_rep(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_content_value(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_channel_reply_host(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_user_team_channel_reply_host(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_primary_channel_message_repl(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def plaintext(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_team_chat_reply_by_id(
        self, user_id: str, team_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_soft_delete_message_reply(
        self, user_id: str, team_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_channel_message_reply_reacti(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/{chatMessage_id1}/microsoft.graph.unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def count_user_team_message_replies(
        self,
        user_id: str,
        team_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_replies_delta(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/{chatMessage_id}/replies/microsoft.graph.delta()"
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

    def get_user_team_channel_message_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_delta_messages(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/messages/microsoft.graph.delta()"
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

    def archive_user_team_primary_channel(
        self,
        user_id: str,
        team_id: str,
        shouldSetSpoSiteReadOnlyForMembers: Optional[bool] = None,
    ) -> Any:
        """

        Invoke action archive

        Args:
            user_id (string): user-id
            team_id (string): team-id
            shouldSetSpoSiteReadOnlyForMembers (boolean): shouldSetSpoSiteReadOnlyForMembers

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        request_body_data = {
            "shouldSetSpoSiteReadOnlyForMembers": shouldSetSpoSiteReadOnlyForMembers
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/microsoft.graph.archive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def complete_migration_team_channel(self, user_id: str, team_id: str) -> Any:
        """

        Invoke action completeMigration

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/microsoft.graph.completeMigration"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_access(
        self,
        user_id: str,
        team_id: str,
        userId: Optional[str] = None,
        tenantId: Optional[str] = None,
        userPrincipalName: Optional[str] = None,
    ) -> dict[str, Any]:
        """

        Invoke function doesUserHaveAccess

        Args:
            user_id (string): user-id
            team_id (string): team-id
            userId (string): Usage: userId='@userId'
            tenantId (string): Usage: tenantId='@tenantId'
            userPrincipalName (string): Usage: userPrincipalName='@userPrincipalName'

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/microsoft.graph.doesUserHaveAccess(userId='@userId',tenantId='@tenantId',userPrincipalName='@userPrincipalName')"
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

    def provision_email_for_team(self, user_id: str, team_id: str) -> dict[str, Any]:
        """

        Invoke action provisionEmail

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/microsoft.graph.provisionEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def remove_team_email(self, user_id: str, team_id: str) -> Any:
        """

        Invoke action removeEmail

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/microsoft.graph.removeEmail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unarchive_primary_channel_action(self, user_id: str, team_id: str) -> Any:
        """

        Invoke action unarchive

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/microsoft.graph.unarchive"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_shared_teams(
        self,
        user_id: str,
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

        Get sharedWithTeams from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams"
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

    def share_team_channel(
        self,
        user_id: str,
        team_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
        isHostTeam: Optional[bool] = None,
        allowedMembers: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to sharedWithTeams for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shared_teams_channels(
        self,
        user_id: str,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get sharedWithTeams from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_team_channel_shared_info(
        self,
        user_id: str,
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

        Update the navigation property sharedWithTeams in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_shared_team_info(
        self, user_id: str, team_id: str, sharedWithChannelTeamInfo_id: str
    ) -> Any:
        """

        Delete navigation property sharedWithTeams for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_shared_with_channel_members(
        self,
        user_id: str,
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

        Get allowedMembers from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers"
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

    def get_shared_with_team_members(
        self,
        user_id: str,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get allowedMembers from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_shared_with_team_members(
        self,
        user_id: str,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/allowedMembers/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_shared_channel_team_info_by_id(
        self,
        user_id: str,
        team_id: str,
        sharedWithChannelTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            sharedWithChannelTeamInfo_id (string): sharedWithChannelTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if sharedWithChannelTeamInfo_id is None:
            raise ValueError(
                "Missing required parameter 'sharedWithChannelTeamInfo-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams/{sharedWithChannelTeamInfo_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_shared_with_teams_in_primary_c(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/sharedWithTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_tabs_from_user(
        self,
        user_id: str,
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

        Get tabs from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/tabs"
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

    def create_primary_tab(
        self,
        user_id: str,
        team_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to tabs for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_teams_tab(
        self,
        user_id: str,
        team_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tabs from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_tab(
        self,
        user_id: str,
        team_id: str,
        teamsTab_id: str,
        id: Optional[str] = None,
        configuration: Optional[dict[str, dict[str, Any]]] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property tabs in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_tab_by_id(self, user_id: str, team_id: str, teamsTab_id: str) -> Any:
        """

        Delete navigation property tabs for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_tab_app(
        self,
        user_id: str,
        team_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_user_team_tabs(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/primaryChannel/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_user_joined_team_schedule(
        self,
        user_id: str,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get schedule from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_schedule(
        self,
        user_id: str,
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

        Update the navigation property schedule in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def delete_user_schedule(self, user_id: str, team_id: str) -> Any:
        """

        Delete navigation property schedule for users

        Args:
            user_id (string): user-id
            team_id (string): team-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_day_notes_for_user_team(
        self,
        user_id: str,
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

        Get dayNotes from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/dayNotes"
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

    def add_day_notes_to_team_schedule(
        self,
        user_id: str,
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

        Create new navigation property to dayNotes for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/dayNotes"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_day_note_schedule(
        self,
        user_id: str,
        team_id: str,
        dayNote_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get dayNotes from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            dayNote_id (string): dayNote-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if dayNote_id is None:
            raise ValueError("Missing required parameter 'dayNote-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/dayNotes/{dayNote_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_day_note_schedule(
        self,
        user_id: str,
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

        Update the navigation property dayNotes in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/dayNotes/{dayNote_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_day_note_by_user_team_id(
        self, user_id: str, team_id: str, dayNote_id: str
    ) -> Any:
        """

        Delete navigation property dayNotes for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            dayNote_id (string): dayNote-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if dayNote_id is None:
            raise ValueError("Missing required parameter 'dayNote-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/dayNotes/{dayNote_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_user_team_day_notes(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/dayNotes/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def share_joined_team_schedule(
        self,
        user_id: str,
        team_id: str,
        notifyTeam: Optional[bool] = None,
        startDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
    ) -> Any:
        """

        Invoke action share

        Args:
            user_id (string): user-id
            team_id (string): team-id
            notifyTeam (boolean): notifyTeam
            startDateTime (string): startDateTime
            endDateTime (string): endDateTime

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/microsoft.graph.share"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_offer_shift_requests(
        self,
        user_id: str,
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

        Get offerShiftRequests from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/offerShiftRequests"
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

    def offer_shift_request_in_team(
        self,
        user_id: str,
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

        Create new navigation property to offerShiftRequests for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/offerShiftRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shift_requests(
        self,
        user_id: str,
        team_id: str,
        offerShiftRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get offerShiftRequests from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            offerShiftRequest_id (string): offerShiftRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if offerShiftRequest_id is None:
            raise ValueError("Missing required parameter 'offerShiftRequest-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_shift_request(
        self,
        user_id: str,
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

        Update the navigation property offerShiftRequests in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_joined_team_schedule_of(
        self, user_id: str, team_id: str, offerShiftRequest_id: str
    ) -> Any:
        """

        Delete navigation property offerShiftRequests for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            offerShiftRequest_id (string): offerShiftRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if offerShiftRequest_id is None:
            raise ValueError("Missing required parameter 'offerShiftRequest-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/offerShiftRequests/{offerShiftRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_user_shift_requests(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/offerShiftRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_open_shift_requests(
        self,
        user_id: str,
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

        Get openShiftChangeRequests from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShiftChangeRequests"
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

    def create_open_shift_request(
        self,
        user_id: str,
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

        Create new navigation property to openShiftChangeRequests for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShiftChangeRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_team_open_shift_change_requ(
        self,
        user_id: str,
        team_id: str,
        openShiftChangeRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get openShiftChangeRequests from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            openShiftChangeRequest_id (string): openShiftChangeRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShiftChangeRequest_id is None:
            raise ValueError("Missing required parameter 'openShiftChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_open_shift_change_request(
        self,
        user_id: str,
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

        Update the navigation property openShiftChangeRequests in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_open_shift_request(
        self, user_id: str, team_id: str, openShiftChangeRequest_id: str
    ) -> Any:
        """

        Delete navigation property openShiftChangeRequests for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            openShiftChangeRequest_id (string): openShiftChangeRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShiftChangeRequest_id is None:
            raise ValueError("Missing required parameter 'openShiftChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShiftChangeRequests/{openShiftChangeRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_open_shift_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShiftChangeRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_user_open_shifts(
        self,
        user_id: str,
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

        Get openShifts from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShifts"
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

    def claim_open_shifts(
        self,
        user_id: str,
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

        Create new navigation property to openShifts for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShifts"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_open_shift_by_id(
        self,
        user_id: str,
        team_id: str,
        openShift_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get openShifts from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            openShift_id (string): openShift-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShift_id is None:
            raise ValueError("Missing required parameter 'openShift-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShifts/{openShift_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_open_shift_for_user_team(
        self,
        user_id: str,
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

        Update the navigation property openShifts in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShifts/{openShift_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_open_shift(
        self, user_id: str, team_id: str, openShift_id: str
    ) -> Any:
        """

        Delete navigation property openShifts for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            openShift_id (string): openShift-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if openShift_id is None:
            raise ValueError("Missing required parameter 'openShift-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShifts/{openShift_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_user_team_open_shifts_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/openShifts/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_user_team_scheduling_groups(
        self,
        user_id: str,
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

        Get schedulingGroups from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/schedulingGroups"
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

    def create_user_team_scheduling_group(
        self,
        user_id: str,
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

        Create new navigation property to schedulingGroups for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/schedulingGroups"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_scheduling_group_schedule(
        self,
        user_id: str,
        team_id: str,
        schedulingGroup_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get schedulingGroups from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            schedulingGroup_id (string): schedulingGroup-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if schedulingGroup_id is None:
            raise ValueError("Missing required parameter 'schedulingGroup-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_team_scheduling_group_na(
        self,
        user_id: str,
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

        Update the navigation property schedulingGroups in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_joined_team_scheduling(
        self, user_id: str, team_id: str, schedulingGroup_id: str
    ) -> Any:
        """

        Delete navigation property schedulingGroups for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            schedulingGroup_id (string): schedulingGroup-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if schedulingGroup_id is None:
            raise ValueError("Missing required parameter 'schedulingGroup-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/schedulingGroups/{schedulingGroup_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_scheduling_group_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/schedulingGroups/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_user_team_shifts(
        self,
        user_id: str,
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

        Get shifts from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/shifts"
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

    def create_shift_for_team(
        self,
        user_id: str,
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

        Create new navigation property to shifts for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/shifts"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_shift_details(
        self,
        user_id: str,
        team_id: str,
        shift_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get shifts from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            shift_id (string): shift-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if shift_id is None:
            raise ValueError("Missing required parameter 'shift-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/shifts/{shift_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_shift_details(
        self,
        user_id: str,
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

        Update the navigation property shifts in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/shifts/{shift_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_shift_for_user(self, user_id: str, team_id: str, shift_id: str) -> Any:
        """

        Delete navigation property shifts for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            shift_id (string): shift-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if shift_id is None:
            raise ValueError("Missing required parameter 'shift-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/shifts/{shift_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_shift_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/shifts/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_user_swap_shift_requests(
        self,
        user_id: str,
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

        Get swapShiftsChangeRequests from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/swapShiftsChangeRequests"
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

    def swap_shifts_request(
        self,
        user_id: str,
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

        Create new navigation property to swapShiftsChangeRequests for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/swapShiftsChangeRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_swap_shifts_change_request(
        self,
        user_id: str,
        team_id: str,
        swapShiftsChangeRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get swapShiftsChangeRequests from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            swapShiftsChangeRequest_id (string): swapShiftsChangeRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if swapShiftsChangeRequest_id is None:
            raise ValueError("Missing required parameter 'swapShiftsChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_swap_shifts_request(
        self,
        user_id: str,
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

        Update the navigation property swapShiftsChangeRequests in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_swap_shift_change_request(
        self, user_id: str, team_id: str, swapShiftsChangeRequest_id: str
    ) -> Any:
        """

        Delete navigation property swapShiftsChangeRequests for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            swapShiftsChangeRequest_id (string): swapShiftsChangeRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if swapShiftsChangeRequest_id is None:
            raise ValueError("Missing required parameter 'swapShiftsChangeRequest-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/swapShiftsChangeRequests/{swapShiftsChangeRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_swap_shift_requests_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/swapShiftsChangeRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_schedule_time_cards(
        self,
        user_id: str,
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

        Get timeCards from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards"
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

    def create_time_card_for_team(
        self,
        user_id: str,
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

        Create new navigation property to timeCards for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_time_card_details(
        self,
        user_id: str,
        team_id: str,
        timeCard_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeCards from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/{timeCard_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_time_card(
        self,
        user_id: str,
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

        Update the navigation property timeCards in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/{timeCard_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_time_card_by_id(
        self, user_id: str, team_id: str, timeCard_id: str
    ) -> Any:
        """

        Delete navigation property timeCards for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeCard_id (string): timeCard-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/{timeCard_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def clock_out_team_time_card(
        self,
        user_id: str,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action clockOut

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/{timeCard_id}/microsoft.graph.clockOut"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def confirm_time_card_schedule(
        self, user_id: str, team_id: str, timeCard_id: str
    ) -> Any:
        """

        Invoke action confirm

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeCard_id (string): timeCard-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeCard_id is None:
            raise ValueError("Missing required parameter 'timeCard-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/{timeCard_id}/microsoft.graph.confirm"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def end_break_time_card_by_user_team_id(
        self,
        user_id: str,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action endBreak

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/{timeCard_id}/microsoft.graph.endBreak"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def start_break_for_user_time_card(
        self,
        user_id: str,
        team_id: str,
        timeCard_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action startBreak

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeCard_id (string): timeCard-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/{timeCard_id}/microsoft.graph.startBreak"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def count_user_team_time_cards(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def clock_in_team_user(
        self,
        user_id: str,
        team_id: str,
        isAtApprovedLocation: Optional[bool] = None,
        notes: Optional[dict[str, dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action clockIn

        Args:
            user_id (string): user-id
            team_id (string): team-id
            isAtApprovedLocation (boolean): isAtApprovedLocation
            notes (object): notes

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeCards/microsoft.graph.clockIn"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_time_off_reasons(
        self,
        user_id: str,
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

        Get timeOffReasons from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffReasons"
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

    def create_time_off_reason(
        self,
        user_id: str,
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

        Create new navigation property to timeOffReasons for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffReasons"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_user_time_off_reasons(
        self,
        user_id: str,
        team_id: str,
        timeOffReason_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeOffReasons from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeOffReason_id (string): timeOffReason-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffReason_id is None:
            raise ValueError("Missing required parameter 'timeOffReason-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_time_off_reason(
        self,
        user_id: str,
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

        Update the navigation property timeOffReasons in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_time_off_reason_for_user(
        self, user_id: str, team_id: str, timeOffReason_id: str
    ) -> Any:
        """

        Delete navigation property timeOffReasons for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeOffReason_id (string): timeOffReason-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffReason_id is None:
            raise ValueError("Missing required parameter 'timeOffReason-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffReasons/{timeOffReason_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_user_team_time_off_reasons(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffReasons/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_time_off_requests_for_team(
        self,
        user_id: str,
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

        Get timeOffRequests from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffRequests"
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

    def user_joined_team_schedule_create_ti(
        self,
        user_id: str,
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

        Create new navigation property to timeOffRequests for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffRequests"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_time_off_request(
        self,
        user_id: str,
        team_id: str,
        timeOffRequest_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timeOffRequests from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeOffRequest_id (string): timeOffRequest-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffRequest_id is None:
            raise ValueError("Missing required parameter 'timeOffRequest-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_time_off_request(
        self,
        user_id: str,
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

        Update the navigation property timeOffRequests in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_time_off_request(
        self, user_id: str, team_id: str, timeOffRequest_id: str
    ) -> Any:
        """

        Delete navigation property timeOffRequests for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeOffRequest_id (string): timeOffRequest-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOffRequest_id is None:
            raise ValueError("Missing required parameter 'timeOffRequest-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffRequests/{timeOffRequest_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_time_off_request_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timeOffRequests/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_times_off_schedule(
        self,
        user_id: str,
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

        Get timesOff from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timesOff"
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

    def post_user_team_schedule_off(
        self,
        user_id: str,
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

        Create new navigation property to timesOff for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timesOff"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_team_user_time_off(
        self,
        user_id: str,
        team_id: str,
        timeOff_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get timesOff from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeOff_id (string): timeOff-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOff_id is None:
            raise ValueError("Missing required parameter 'timeOff-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timesOff/{timeOff_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_time_off(
        self,
        user_id: str,
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

        Update the navigation property timesOff in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timesOff/{timeOff_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_time_off_by_id(
        self, user_id: str, team_id: str, timeOff_id: str
    ) -> Any:
        """

        Delete navigation property timesOff for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            timeOff_id (string): timeOff-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if timeOff_id is None:
            raise ValueError("Missing required parameter 'timeOff-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timesOff/{timeOff_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_times_off_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/schedule/timesOff/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_team_tags_for_user(
        self,
        user_id: str,
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

        Get tags from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags"
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

    def create_user_team_tag(
        self,
        user_id: str,
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

        Create new navigation property to tags for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_tags_from_user(
        self,
        user_id: str,
        team_id: str,
        teamworkTag_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tags from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_team_tag_by_id(
        self,
        user_id: str,
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

        Update the navigation property tags in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_team_tag(
        self, user_id: str, team_id: str, teamworkTag_id: str
    ) -> Any:
        """

        Delete navigation property tags for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_team_members_by_tag_id(
        self,
        user_id: str,
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

        Get members from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}/members"
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

    def add_teamwork_tag_member(
        self,
        user_id: str,
        team_id: str,
        teamworkTag_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to members for users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_teamwork_tag_members(
        self,
        user_id: str,
        team_id: str,
        teamworkTag_id: str,
        teamworkTagMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get members from users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        if teamworkTagMember_id is None:
            raise ValueError("Missing required parameter 'teamworkTagMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_teamwork_tag_member(
        self,
        user_id: str,
        team_id: str,
        teamworkTag_id: str,
        teamworkTagMember_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in users

        Args:
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_tag_member(
        self, user_id: str, team_id: str, teamworkTag_id: str, teamworkTagMember_id: str
    ) -> Any:
        """

        Delete navigation property members for users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            teamworkTagMember_id (string): teamworkTagMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        if teamworkTagMember_id is None:
            raise ValueError("Missing required parameter 'teamworkTagMember-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}/members/{teamworkTagMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_teamwork_tag_members(
        self,
        user_id: str,
        team_id: str,
        teamworkTag_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            teamworkTag_id (string): teamworkTag-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        if teamworkTag_id is None:
            raise ValueError("Missing required parameter 'teamworkTag-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/{teamworkTag_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_tag_count(
        self,
        user_id: str,
        team_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            team_id (string): team-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/tags/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_user_template(
        self,
        user_id: str,
        team_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get template from users

        Args:
            user_id (string): user-id
            team_id (string): team-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if team_id is None:
            raise ValueError("Missing required parameter 'team-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/{team_id}/template"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_joined_teams_count(
        self, user_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_joined_team_messages(
        self,
        user_id: str,
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
            user_id (string): user-id
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
            users.team
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/joinedTeams/microsoft.graph.getAllMessages()"
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

    def get_user_teamwork_data(
        self,
        user_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get userTeamwork

        Args:
            user_id (string): user-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_user_teamwork(
        self,
        user_id: str,
        id: Optional[str] = None,
        locale: Optional[str] = None,
        region: Optional[str] = None,
        associatedTeams: Optional[List[Any]] = None,
        installedApps: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property teamwork in users

        Args:
            user_id (string): user-id
            id (string): The unique identifier for an entity. Read-only.
            locale (string): Represents the location that a user selected in Microsoft Teams and doesn't follow the Office's locale setting. A user's locale is represented by their preferred language and country or region. For example, en-us. The language component follows two-letter codes as defined in ISO 639-1, and the country component follows two-letter codes as defined in ISO 3166-1 alpha-2.
            region (string): Represents the region of the organization or the user. For users with multigeo licenses, the property contains the user's region (if available). For users without multigeo licenses, the property contains the organization's region.The region value can be any region supported by the Teams payload. The possible values are: Americas, Europe and MiddleEast, Asia Pacific, UAE, Australia, Brazil, Canada, Switzerland, Germany, France, India, Japan, South Korea, Norway, Singapore, United Kingdom, South Africa, Sweden, Qatar, Poland, Italy, Israel, Spain, Mexico, USGov Community Cloud, USGov Community Cloud High, USGov Department of Defense, and China.
            associatedTeams (array): The list of associatedTeamInfo objects that a user is associated with.
            installedApps (array): The apps installed in the personal scope of this user.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "locale": locale,
            "region": region,
            "associatedTeams": associatedTeams,
            "installedApps": installedApps,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_user_teamwork(self, user_id: str) -> Any:
        """

        Delete navigation property teamwork for users

        Args:
            user_id (string): user-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_associated_teams(
        self,
        user_id: str,
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

        Get associatedTeams from users

        Args:
            user_id (string): user-id
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
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = (
            f"{self.main_app_client.base_url}/users/{user_id}/teamwork/associatedTeams"
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

    def associate_team_to_user(
        self,
        user_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to associatedTeams for users

        Args:
            user_id (string): user-id
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The name of the team.
            tenantId (string): The ID of the Microsoft Entra tenant.
            team (string): team

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "displayName": displayName,
            "tenantId": tenantId,
            "team": team,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = (
            f"{self.main_app_client.base_url}/users/{user_id}/teamwork/associatedTeams"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_associated_teams_by_user(
        self,
        user_id: str,
        associatedTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get associatedTeams from users

        Args:
            user_id (string): user-id
            associatedTeamInfo_id (string): associatedTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if associatedTeamInfo_id is None:
            raise ValueError("Missing required parameter 'associatedTeamInfo-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/associatedTeams/{associatedTeamInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_associated_team_info(
        self,
        user_id: str,
        associatedTeamInfo_id: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property associatedTeams in users

        Args:
            user_id (string): user-id
            associatedTeamInfo_id (string): associatedTeamInfo-id
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The name of the team.
            tenantId (string): The ID of the Microsoft Entra tenant.
            team (string): team

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if associatedTeamInfo_id is None:
            raise ValueError("Missing required parameter 'associatedTeamInfo-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "displayName": displayName,
            "tenantId": tenantId,
            "team": team,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/associatedTeams/{associatedTeamInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_associated_team(self, user_id: str, associatedTeamInfo_id: str) -> Any:
        """

        Delete navigation property associatedTeams for users

        Args:
            user_id (string): user-id
            associatedTeamInfo_id (string): associatedTeamInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if associatedTeamInfo_id is None:
            raise ValueError("Missing required parameter 'associatedTeamInfo-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/associatedTeams/{associatedTeamInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_associated_team(
        self,
        user_id: str,
        associatedTeamInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get team from users

        Args:
            user_id (string): user-id
            associatedTeamInfo_id (string): associatedTeamInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if associatedTeamInfo_id is None:
            raise ValueError("Missing required parameter 'associatedTeamInfo-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/associatedTeams/{associatedTeamInfo_id}/team"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_associated_teams_count(
        self, user_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/associatedTeams/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_user_installed_apps(
        self,
        user_id: str,
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

        List apps installed for user

        Args:
            user_id (string): user-id
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
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps"
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

    def install_app_for_user(
        self,
        user_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
        chat: Optional[Any] = None,
    ) -> Any:
        """

        Install app for user

        Args:
            user_id (string): user-id
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (object): consentedPermissionSet
            teamsApp (string): teamsApp
            teamsAppDefinition (string): teamsAppDefinition
            chat (string): chat

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "consentedPermissionSet": consentedPermissionSet,
            "teamsApp": teamsApp,
            "teamsAppDefinition": teamsAppDefinition,
            "chat": chat,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_user_installed_app(
        self,
        user_id: str,
        userScopeTeamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get installed app for user

        Args:
            user_id (string): user-id
            userScopeTeamsAppInstallation_id (string): userScopeTeamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if userScopeTeamsAppInstallation_id is None:
            raise ValueError(
                "Missing required parameter 'userScopeTeamsAppInstallation-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps/{userScopeTeamsAppInstallation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_user_teamwork_app(
        self,
        user_id: str,
        userScopeTeamsAppInstallation_id: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[dict[str, dict[str, Any]]] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
        chat: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property installedApps in users

        Args:
            user_id (string): user-id
            userScopeTeamsAppInstallation_id (string): userScopeTeamsAppInstallation-id
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (object): consentedPermissionSet
            teamsApp (string): teamsApp
            teamsAppDefinition (string): teamsAppDefinition
            chat (string): chat

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if userScopeTeamsAppInstallation_id is None:
            raise ValueError(
                "Missing required parameter 'userScopeTeamsAppInstallation-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "consentedPermissionSet": consentedPermissionSet,
            "teamsApp": teamsApp,
            "teamsAppDefinition": teamsAppDefinition,
            "chat": chat,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps/{userScopeTeamsAppInstallation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_installed_app(
        self, user_id: str, userScopeTeamsAppInstallation_id: str
    ) -> Any:
        """

        Uninstall app for user

        Args:
            user_id (string): user-id
            userScopeTeamsAppInstallation_id (string): userScopeTeamsAppInstallation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if userScopeTeamsAppInstallation_id is None:
            raise ValueError(
                "Missing required parameter 'userScopeTeamsAppInstallation-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps/{userScopeTeamsAppInstallation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_app_installation(
        self,
        user_id: str,
        userScopeTeamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get chat between user and teamsApp

        Args:
            user_id (string): user-id
            userScopeTeamsAppInstallation_id (string): userScopeTeamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if userScopeTeamsAppInstallation_id is None:
            raise ValueError(
                "Missing required parameter 'userScopeTeamsAppInstallation-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps/{userScopeTeamsAppInstallation_id}/chat"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_installed_teams_app(
        self,
        user_id: str,
        userScopeTeamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from users

        Args:
            user_id (string): user-id
            userScopeTeamsAppInstallation_id (string): userScopeTeamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if userScopeTeamsAppInstallation_id is None:
            raise ValueError(
                "Missing required parameter 'userScopeTeamsAppInstallation-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps/{userScopeTeamsAppInstallation_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_installed_app_details(
        self,
        user_id: str,
        userScopeTeamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsAppDefinition from users

        Args:
            user_id (string): user-id
            userScopeTeamsAppInstallation_id (string): userScopeTeamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if userScopeTeamsAppInstallation_id is None:
            raise ValueError(
                "Missing required parameter 'userScopeTeamsAppInstallation-id'."
            )
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps/{userScopeTeamsAppInstallation_id}/teamsAppDefinition"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_installed_apps_count(
        self, user_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            user_id (string): user-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/installedApps/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def send_user_team_activity(
        self,
        user_id: str,
        topic: Optional[dict[str, dict[str, Any]]] = None,
        activityType: Optional[str] = None,
        chainId: Optional[float] = None,
        previewText: Optional[dict[str, dict[str, Any]]] = None,
        teamsAppId: Optional[str] = None,
        templateParameters: Optional[List[dict[str, dict[str, Any]]]] = None,
    ) -> Any:
        """

        Invoke action sendActivityNotification

        Args:
            user_id (string): user-id
            topic (object): topic
            activityType (string): activityType
            chainId (number): chainId
            previewText (object): previewText
            teamsAppId (string): teamsAppId
            templateParameters (array): templateParameters

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.userTeamwork
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        request_body_data = None
        request_body_data = {
            "topic": topic,
            "activityType": activityType,
            "chainId": chainId,
            "previewText": previewText,
            "teamsAppId": teamsAppId,
            "templateParameters": templateParameters,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/microsoft.graph.sendActivityNotification"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.list_user_chats,
            self.create_user_chat_link,
            self.get_chat_details,
            self.update_user_chat,
            self.delete_user_chat,
            self.get_installed_apps,
            self.create_installed_app,
            self.get_installed_apps_by_user_chat,
            self.update_user_chat_installed_app,
            self.delete_user_chat_app,
            self.upgrade_chat_app,
            self.get_teams_app,
            self.fetch_chat_teams_app_definition,
            self.count_installed_apps,
            self.get_chat_last_message_preview,
            self.update_last_message_preview,
            self.delete_last_message_preview,
            self.list_user_chat_members,
            self.create_chat_member,
            self.get_chat_members,
            self.update_chat_members,
            self.delete_chat_member,
            self.get_chat_member_count,
            self.add_microsoft_graph_member_to_chat,
            self.remove_chat_member_post,
            self.get_messages_by_user_chat,
            self.create_user_chat_message,
            self.get_chat_messages,
            self.update_user_chat_message,
            self.delete_user_chat_message_by_id,
            self.get_user_chat_message_hosted_conten,
            self.create_user_chat_message_hosted_con,
            self.get_messages_chat_hosted_content_by,
            self.patch_user_chat_message_hosted_cont,
            self.delete_chat_message_hosted_content,
            self.get_chat_message_hosted_content_val,
            self.update_user_chat_message_hosted_con,
            self.delete_user_chat_message_hosted_con,
            self.count_chat_message_hosted_contents,
            self.set_reaction_on_chat_message_by_user,
            self.soft_delete_user_chat_message,
            self.undo_chat_message_soft_delete,
            self.unset_chat_message_reaction,
            self.get_replies_from_user_chat_message,
            self.create_reply_link,
            self.get_replies_from_chat_message,
            self.update_user_message_reply_by_id,
            self.delete_user_chat_reply,
            self.list_message_reply_hosted_contents,
            self.create_user_chat_message_reply_host,
            self.get_user_chat_message_reply_hosted_c,
            self.patch_user_chat_message_reply_hoste,
            self.delete_reply_hosted_content,
            self.get_hosted_content,
            self.update_user_chat_message_reply_host,
            self.delete_user_chat_reply_hosted_conte,
            self.count_chat_message_replies,
            self.set_chat_message_reaction_reply,
            self.soft_delete_chat_message_reply_by_id,
            self.undo_chat_message_reply_soft_delete,
            self.unset_chat_message_reply_reaction_u,
            self.get_chat_message_replies_count,
            self.get_user_chat_message_reply_delta,
            self.get_chat_message_count,
            self.get_chats_delta_messages,
            self.hide_user_chat,
            self.mark_chat_read_for_user,
            self.mark_chat_unread_for_user,
            self.send_activity_notification_to_chat,
            self.unhide_chat_for_user,
            self.fetch_user_chat_permissions,
            self.grant_chat_permission,
            self.get_user_chat_permission_grant_by_id,
            self.update_chat_permission_grant,
            self.delete_permission_grant,
            self.count_user_chat_permissions,
            self.get_pinned_messages,
            self.create_pinned_message,
            self.get_pinned_messages_for_user_chat,
            self.update_pinned_messages,
            self.delete_user_chat_pinned_message,
            self.get_pinned_chat_message_details,
            self.get_pinned_message_count,
            self.list_user_chat_tabs,
            self.create_user_chat_tab,
            self.get_tabs_for_user,
            self.update_user_tabs,
            self.delete_user_tab,
            self.get_teams_app_info,
            self.get_tab_count,
            self.get_chat_count_by_user,
            self.get_user_chat_messages,
            self.get_retained_messages_by_user,
            self.list_user_joined_teams,
            self.create_user_joined_team_relation,
            self.get_joined_teams_by_user,
            self.patch_user_team_association,
            self.delete_user_team,
            self.get_user_joined_teams_channels,
            self.get_channels_by_user_team,
            self.get_team_channels_count,
            self.get_channels_by_user_team_id,
            self.create_user_channel_link,
            self.get_channels_from_user_team,
            self.update_user_channel,
            self.delete_user_channel,
            self.get_channel_members,
            self.create_user_team_channel_members,
            self.get_conversation_members,
            self.patch_conversation_member,
            self.delete_user_team_channel_conversat,
            self.get_channel_members_count,
            self.add_microsoft_graph_member,
            self.remove_channel_all_members,
            self.get_files_folder_details,
            self.get_team_channel_files_content,
            self.update_file_content,
            self.delete_files_folder_content,
            self.list_channel_team_member,
            self.add_member_to_channel,
            self.get_user_joined_team_channel_member,
            self.update_conversation_member,
            self.delete_user_joined_team_channel_mem,
            self.get_team_channel_members_count,
            self.add_user_team_channel_member_by_grap,
            self.remove_channel_member_by_graph_id,
            self.list_user_team_channel_messages,
            self.create_message_in_channel,
            self.get_team_channel_message,
            self.update_chat_message,
            self.delete_team_message,
            self.list_user_chat_message_hosted_conte,
            self.create_user_team_channel_message_ho,
            self.get_user_team_channel_message_hoste,
            self.patch_user_team_channel_message_hos,
            self.delete_user_team_channel_message_ho,
            self.get_user_channel_message_hosted_con,
            self.update_user_team_channel_message_ho,
            self.delete_user_team_channel_msg_hosted,
            self.get_chat_message_hosted_contents_co,
            self.set_chat_message_reaction,
            self.soft_delete_channel_message_post,
            self.restore_chat_message_from_soft_dele,
            self.unset_chat_reaction,
            self.get_channel_message_replies_by_ids,
            self.add_message_reply,
            self.get_reply_message,
            self.update_reply_to_message,
            self.delete_chat_message_reply,
            self.list_user_team_channel_message_repl,
            self.create_reply_content,
            self.get_user_team_channel_reply_hosted_c,
            self.update_hosted_content_message,
            self.delete_user_team_channel_message_re,
            self.get_user_team_channel_message_reply,
            self.update_reply_hosted_content_value,
            self.delete_user_team_channel_msg_reply_h,
            self.get_chat_message_reply_hosted_conte,
            self.set_reaction_for_message_reply,
            self.soft_delete_channel_message_reply_b,
            self.undo_soft_delete_replies,
            self.unset_reaction_from_message_reply,
            self.get_replies_count,
            self.get_channel_message_delta_replies,
            self.count_user_team_channel_messages,
            self.get_user_team_channel_message_delta,
            self.archive_channel,
            self.complete_migration_channel,
            self.check_user_channel_access,
            self.provision_channel_email,
            self.remove_email_from_channel,
            self.post_unarchive_channel_for_user_tea,
            self.get_shared_teams,
            self.add_team_to_shared_channel,
            self.get_shared_teams_details,
            self.patch_shared_channel_team_info,
            self.delete_shared_with_team_info,
            self.get_shared_channel_allowed_members,
            self.get_allowed_members_in_channel,
            self.get_shared_with_channel_allowed_mem,
            self.get_shared_team_channels,
            self.get_shared_team_channels_count,
            self.get_user_team_channel_tabs,
            self.add_tab_to_user_channel,
            self.get_team_tab_details,
            self.update_tab,
            self.delete_tab,
            self.get_teams_tab_details,
            self.get_team_channel_tabs_count,
            self.get_team_channel_count,
            self.get_user_team_all_channel_messages,
            self.get_all_retained_team_messages,
            self.get_user_group_details,
            self.get_service_provisioning_errors,
            self.get_team_service_errors_count,
            self.get_team_incoming_channels,
            self.get_team_channel,
            self.count_incoming_channels,
            self.get_installed_apps_for_team,
            self.install_app_for_team,
            self.get_user_team_installed_app_by_id,
            self.update_teams_app_installation,
            self.delete_app_installation,
            self.upgrade_app_installation,
            self.get_team_app_details,
            self.get_app_installation_details,
            self.count_user_installed_apps,
            self.get_member_list_for_user_team,
            self.create_user_team_member,
            self.get_team_members_data,
            self.patch_user_team_member,
            self.delete_conversation_member_from_us,
            self.count_team_members,
            self.add_team_member_to_joined_team,
            self.remove_team_member_from_user,
            self.archive_team_membership,
            self.clone_team_by_graph,
            self.complete_migration_team,
            self.send_activity_to_team,
            self.unarchive_team_membership,
            self.get_user_team_operations,
            self.add_team_operation,
            self.get_team_operations,
            self.patch_async_operation,
            self.delete_async_team_operation,
            self.get_team_operations_count,
            self.get_team_permission_grants,
            self.grant_user_permission,
            self.get_permission_grants,
            self.update_user_team_permission_grant,
            self.delete_user_team_permission_grant,
            self.get_team_permission_count,
            self.get_team_photo_from_user,
            self.patch_user_team_photo,
            self.get_team_photo,
            self.update_user_team_photo,
            self.delete_team_photo,
            self.get_primary_channel,
            self.update_primary_channel,
            self.delete_primary_channel_from_team,
            self.list_team_members,
            self.add_team_members,
            self.get_team_members,
            self.patch_user_joined_team_primary_chan,
            self.remove_user_team_primary_channel_me,
            self.count_user_team_channel_members,
            self.add_team_member,
            self.remove_team_member_from_channel,
            self.get_user_team_channel_files_folder,
            self.get_team_files_content,
            self.update_user_team_file_content,
            self.delete_content_folder,
            self.list_team_channel_members,
            self.add_member_to_primary_channel,
            self.get_team_channel_members,
            self.update_user_team_members,
            self.delete_user_joined_team_primary_cha,
            self.get_team_members_count,
            self.add_member_to_primary_channel_team,
            self.remove_team_member,
            self.get_user_team_channel_messages,
            self.create_message_in_primary_channel,
            self.get_team_message,
            self.update_message_by_id,
            self.delete_message_in_primary_channel,
            self.get_user_team_primary_channel_messa,
            self.create_user_team_message_hosted_con,
            self.get_user_joined_team_primary_channe,
            self.patch_message_hosted_content,
            self.delete_user_team_primary_channel_ms,
            self.get_user_team_primary_channel_msg_ho,
            self.update_user_team_primary_channel_ms,
            self.delete_user_team_channel_content,
            self.get_primary_channel_msg_hosted_coun,
            self.set_reaction_on_primary_channel_mes,
            self.soft_delete_message,
            self.user_joined_team_primary_channel_me,
            self.unset_reaction_for_message,
            self.list_user_joined_team_primary_chann,
            self.create_reply,
            self.get_channel_message_reply_by_ids,
            self.update_channel_reply_by_id,
            self.delete_user_joined_team_channel_mes,
            self.get_chat_replies_hosted_contents,
            self.add_hosted_content_reply,
            self.get_user_team_reply_hosted_content_b,
            self.patch_channel_reply_hosted_content,
            self.delete_user_joined_team_channel_rep,
            self.get_hosted_content_value,
            self.update_user_team_channel_reply_host,
            self.delete_user_team_channel_reply_host,
            self.count_primary_channel_message_repl,
            self.plaintext,
            self.soft_delete_team_chat_reply_by_id,
            self.undo_soft_delete_message_reply,
            self.unset_channel_message_reply_reacti,
            self.count_user_team_message_replies,
            self.get_replies_delta,
            self.get_user_team_channel_message_count,
            self.get_delta_messages,
            self.archive_user_team_primary_channel,
            self.complete_migration_team_channel,
            self.get_team_access,
            self.provision_email_for_team,
            self.remove_team_email,
            self.unarchive_primary_channel_action,
            self.list_shared_teams,
            self.share_team_channel,
            self.get_shared_teams_channels,
            self.update_team_channel_shared_info,
            self.delete_shared_team_info,
            self.get_shared_with_channel_members,
            self.get_shared_with_team_members,
            self.count_shared_with_team_members,
            self.get_shared_channel_team_info_by_id,
            self.count_shared_with_teams_in_primary_c,
            self.get_tabs_from_user,
            self.create_primary_tab,
            self.get_teams_tab,
            self.update_user_team_tab,
            self.delete_tab_by_id,
            self.get_team_tab_app,
            self.count_user_team_tabs,
            self.get_user_joined_team_schedule,
            self.update_user_team_schedule,
            self.delete_user_schedule,
            self.get_day_notes_for_user_team,
            self.add_day_notes_to_team_schedule,
            self.get_day_note_schedule,
            self.update_day_note_schedule,
            self.delete_day_note_by_user_team_id,
            self.count_user_team_day_notes,
            self.share_joined_team_schedule,
            self.get_offer_shift_requests,
            self.offer_shift_request_in_team,
            self.get_shift_requests,
            self.update_shift_request,
            self.delete_user_joined_team_schedule_of,
            self.count_user_shift_requests,
            self.get_open_shift_requests,
            self.create_open_shift_request,
            self.get_user_team_open_shift_change_requ,
            self.patch_open_shift_change_request,
            self.delete_open_shift_request,
            self.get_open_shift_count,
            self.list_user_open_shifts,
            self.claim_open_shifts,
            self.get_user_open_shift_by_id,
            self.update_open_shift_for_user_team,
            self.delete_user_team_open_shift,
            self.get_user_team_open_shifts_count,
            self.list_user_team_scheduling_groups,
            self.create_user_team_scheduling_group,
            self.get_scheduling_group_schedule,
            self.patch_user_team_scheduling_group_na,
            self.delete_user_joined_team_scheduling,
            self.get_scheduling_group_count,
            self.list_user_team_shifts,
            self.create_shift_for_team,
            self.get_shift_details,
            self.update_user_shift_details,
            self.delete_shift_for_user,
            self.get_shift_count,
            self.get_team_user_swap_shift_requests,
            self.swap_shifts_request,
            self.get_swap_shifts_change_request,
            self.update_swap_shifts_request,
            self.delete_swap_shift_change_request,
            self.get_swap_shift_requests_count,
            self.get_team_schedule_time_cards,
            self.create_time_card_for_team,
            self.get_time_card_details,
            self.update_user_team_time_card,
            self.delete_user_team_time_card_by_id,
            self.clock_out_team_time_card,
            self.confirm_time_card_schedule,
            self.end_break_time_card_by_user_team_id,
            self.start_break_for_user_time_card,
            self.count_user_team_time_cards,
            self.clock_in_team_user,
            self.list_time_off_reasons,
            self.create_time_off_reason,
            self.get_team_user_time_off_reasons,
            self.update_user_team_time_off_reason,
            self.delete_time_off_reason_for_user,
            self.count_user_team_time_off_reasons,
            self.get_time_off_requests_for_team,
            self.user_joined_team_schedule_create_ti,
            self.get_team_time_off_request,
            self.update_user_team_time_off_request,
            self.delete_time_off_request,
            self.get_time_off_request_count,
            self.get_times_off_schedule,
            self.post_user_team_schedule_off,
            self.get_team_user_time_off,
            self.update_user_time_off,
            self.delete_user_team_time_off_by_id,
            self.get_team_times_off_count,
            self.get_team_tags_for_user,
            self.create_user_team_tag,
            self.get_tags_from_user,
            self.update_user_team_tag_by_id,
            self.delete_user_team_tag,
            self.get_team_members_by_tag_id,
            self.add_teamwork_tag_member,
            self.get_teamwork_tag_members,
            self.update_teamwork_tag_member,
            self.delete_tag_member,
            self.count_teamwork_tag_members,
            self.get_tag_count,
            self.get_user_template,
            self.get_joined_teams_count,
            self.get_joined_team_messages,
            self.get_user_teamwork_data,
            self.update_user_teamwork,
            self.delete_user_teamwork,
            self.get_associated_teams,
            self.associate_team_to_user,
            self.get_associated_teams_by_user,
            self.update_associated_team_info,
            self.delete_associated_team,
            self.get_associated_team,
            self.get_associated_teams_count,
            self.get_user_installed_apps,
            self.install_app_for_user,
            self.get_user_installed_app,
            self.patch_user_teamwork_app,
            self.delete_installed_app,
            self.get_chat_app_installation,
            self.get_installed_teams_app,
            self.get_installed_app_details,
            self.get_installed_apps_count,
            self.send_user_team_activity,
        ]
