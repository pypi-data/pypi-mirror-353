from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class ChatsApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def chats_chat_list_chat(
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

        List chats

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
            chats.chat, important
        """
        url = f"{self.main_app_client.base_url}/chats"
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

    def chats_chat_create_chat(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        chatType: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        isHiddenForAllMembers: Optional[bool] = None,
        lastUpdatedDateTime: Optional[str] = None,
        onlineMeetingInfo: Optional[Any] = None,
        tenantId: Optional[str] = None,
        topic: Optional[str] = None,
        viewpoint: Optional[Any] = None,
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

        Create chat

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            chatType (string): chatType
            createdDateTime (string): Date and time at which the chat was created. Read-only.
            isHiddenForAllMembers (boolean): Indicates whether the chat is hidden for all its members. Read-only.
            lastUpdatedDateTime (string): Date and time at which the chat was renamed or the list of members was last changed. Read-only.
            onlineMeetingInfo (string): Represents details about an online meeting. If the chat isn't associated with an online meeting, the property is empty. Read-only.
            tenantId (string): The identifier of the tenant in which the chat was created. Read-only.
            topic (string): (Optional) Subject or topic for the chat. Only available for group chats.
            viewpoint (string): Represents caller-specific information about the chat, such as the last message read date and time. This property is populated only when the request is made in a delegated context.
            webUrl (string): The URL for the chat in Microsoft Teams. The URL should be treated as an opaque blob, and not parsed. Read-only.
            installedApps (array): A collection of all the apps in the chat. Nullable.
            lastMessagePreview (string): Preview of the last message sent in the chat. Null if no messages were sent in the chat. Currently, only the list chats operation supports this property.
            members (array): A collection of all the members in the chat. Nullable.
            messages (array): A collection of all the messages in the chat. Nullable.
            permissionGrants (array): A collection of permissions granted to apps for the chat.
            pinnedMessages (array): A collection of all the pinned messages in the chat. Nullable.
            tabs (array): A collection of all the tabs in the chat. Nullable.

        Returns:
            Any: Created entity

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chat
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
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
        url = f"{self.main_app_client.base_url}/chats"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_chat_get_chat(
        self,
        chat_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get chat

        Args:
            chat_id (string): chat-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved entity

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chat
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_chat_update_chat(
        self,
        chat_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        chatType: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        isHiddenForAllMembers: Optional[bool] = None,
        lastUpdatedDateTime: Optional[str] = None,
        onlineMeetingInfo: Optional[Any] = None,
        tenantId: Optional[str] = None,
        topic: Optional[str] = None,
        viewpoint: Optional[Any] = None,
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

        Update chat

        Args:
            chat_id (string): chat-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            chatType (string): chatType
            createdDateTime (string): Date and time at which the chat was created. Read-only.
            isHiddenForAllMembers (boolean): Indicates whether the chat is hidden for all its members. Read-only.
            lastUpdatedDateTime (string): Date and time at which the chat was renamed or the list of members was last changed. Read-only.
            onlineMeetingInfo (string): Represents details about an online meeting. If the chat isn't associated with an online meeting, the property is empty. Read-only.
            tenantId (string): The identifier of the tenant in which the chat was created. Read-only.
            topic (string): (Optional) Subject or topic for the chat. Only available for group chats.
            viewpoint (string): Represents caller-specific information about the chat, such as the last message read date and time. This property is populated only when the request is made in a delegated context.
            webUrl (string): The URL for the chat in Microsoft Teams. The URL should be treated as an opaque blob, and not parsed. Read-only.
            installedApps (array): A collection of all the apps in the chat. Nullable.
            lastMessagePreview (string): Preview of the last message sent in the chat. Null if no messages were sent in the chat. Currently, only the list chats operation supports this property.
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
            chats.chat
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_chat_delete_chat(self, chat_id: str) -> Any:
        """

        Delete chat

        Args:
            chat_id (string): chat-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chat
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def chats_list_installed_apps(
        self,
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

        List apps in chat

        Args:
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
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps"
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

    def chats_create_installed_apps(
        self,
        chat_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[Any] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Add app to chat

        Args:
            chat_id (string): chat-id
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
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_get_installed_apps(
        self,
        chat_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get installed app in chat

        Args:
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_update_installed_apps(
        self,
        chat_id: str,
        teamsAppInstallation_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[Any] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property installedApps in chats

        Args:
            chat_id (string): chat-id
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
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_delete_installed_apps(
        self, chat_id: str, teamsAppInstallation_id: str
    ) -> Any:
        """

        Uninstall app in a chat

        Args:
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def upgrade_installed_app(
        self,
        chat_id: str,
        teamsAppInstallation_id: str,
        consentedPermissionSet: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action upgrade

        Args:
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            consentedPermissionSet (string): consentedPermissionSet

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        request_body_data = None
        request_body_data = {"consentedPermissionSet": consentedPermissionSet}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}/upgrade"
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
        chat_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from chats

        Args:
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_installed_app_definition(
        self,
        chat_id: str,
        teamsAppInstallation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsAppDefinition from chats

        Args:
            chat_id (string): chat-id
            teamsAppInstallation_id (string): teamsAppInstallation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsAppInstallation_id is None:
            raise ValueError("Missing required parameter 'teamsAppInstallation-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps/{teamsAppInstallation_id}/teamsAppDefinition"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_chat_apps_count(
        self, chat_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsAppInstallation
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/installedApps/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_get_last_message_preview(
        self,
        chat_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get lastMessagePreview from chats

        Args:
            chat_id (string): chat-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/lastMessagePreview"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_update_last_message_preview(
        self,
        chat_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        body: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        eventDetail: Optional[Any] = None,
        from_: Optional[Any] = None,
        isDeleted: Optional[bool] = None,
        messageType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property lastMessagePreview in chats

        Args:
            chat_id (string): chat-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            body (string): Body of the chatMessage. This will still contain markers for @mentions and attachments even though the object doesn't return @mentions and attachments.
            createdDateTime (string): Date time object representing the time at which message was created.
            eventDetail (string): Read-only.  If present, represents details of an event that happened in a chat, a channel, or a team, for example, members were added, and so on. For event messages, the messageType property is set to systemEventMessage.
            from_ (string): Information about the sender of the message.
            isDeleted (boolean): If set to true, the original message has been deleted.
            messageType (string): messageType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/lastMessagePreview"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_delete_last_message_preview(self, chat_id: str) -> Any:
        """

        Delete navigation property lastMessagePreview for chats

        Args:
            chat_id (string): chat-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/lastMessagePreview"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def chats_list_members(
        self,
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

        List conversationMembers

        Args:
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
            chats.conversationMember
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/members"
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

    def chats_create_members(
        self,
        chat_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Add member to a chat

        Args:
            chat_id (string): chat-id
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
            chats.conversationMember
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/members"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_get_members(
        self,
        chat_id: str,
        conversationMember_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get conversationMember in a chat

        Args:
            chat_id (string): chat-id
            conversationMember_id (string): conversationMember-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.conversationMember
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/members/{conversationMember_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_update_members(
        self,
        chat_id: str,
        conversationMember_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        roles: Optional[List[str]] = None,
        visibleHistoryStartDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property members in chats

        Args:
            chat_id (string): chat-id
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
            chats.conversationMember
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_delete_members(self, chat_id: str, conversationMember_id: str) -> Any:
        """

        Remove member from chat

        Args:
            chat_id (string): chat-id
            conversationMember_id (string): conversationMember-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.conversationMember
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if conversationMember_id is None:
            raise ValueError("Missing required parameter 'conversationMember-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/members/{conversationMember_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def chats_members_get_count(
        self, chat_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.conversationMember
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/members/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_chat_members_add(
        self, chat_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action add

        Args:
            chat_id (string): chat-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.conversationMember
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/members/add"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_chat_members_remove(
        self, chat_id: str, values: Optional[List[Any]] = None
    ) -> dict[str, Any]:
        """

        Invoke action remove

        Args:
            chat_id (string): chat-id
            values (array): values

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.conversationMember
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"values": values}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/members/remove"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_list_messages(
        self,
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

        List messages in a chat

        Args:
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages"
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

    def chats_create_messages(
        self,
        chat_id: str,
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

        Send message in a chat

        Args:
            chat_id (string): chat-id
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_get_messages(
        self,
        chat_id: str,
        chatMessage_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get chatMessage in a channel or chat

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = (
            f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}"
        )
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_update_messages(
        self,
        chat_id: str,
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

        Update the navigation property messages in chats

        Args:
            chat_id (string): chat-id
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = (
            f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}"
        )
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_delete_messages(self, chat_id: str, chatMessage_id: str) -> Any:
        """

        Delete navigation property messages for chats

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = (
            f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}"
        )
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_content_by_message_id(
        self,
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

        List hostedContents

        Args:
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents"
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

    def create_hosted_content(
        self,
        chat_id: str,
        chatMessage_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for chats

        Args:
            chat_id (string): chat-id
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_chat_msg_hosted_content(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get chatMessageHostedContent

        Args:
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_chat_message_content(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in chats

        Args:
            chat_id (string): chat-id
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
            chats.chatMessage
        """
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
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def del_chat_msg_hosted_content(
        self, chat_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        Delete navigation property hostedContents for chats

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_msg_hosted_content_val(
        self, chat_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        List hostedContents

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_chat_hosted_content_val(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in chats

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def del_chat_msg_host_content_val(
        self, chat_id: str, chatMessage_id: str, chatMessageHostedContent_id: str
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in chats

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessageHostedContent_id is None:
            raise ValueError(
                "Missing required parameter 'chatMessageHostedContent-id'."
            )
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_chat_msg_hosted_contents(
        self,
        chat_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_chat_message_reaction(
        self, chat_id: str, chatMessage_id: str, reactionType: Optional[str] = None
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def delete_message_softly(self, chat_id: str, chatMessage_id: str) -> Any:
        """

        Invoke action softDelete

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def restore_soft_deleted_message(self, chat_id: str, chatMessage_id: str) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/undoSoftDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unset_message_reaction(
        self, chat_id: str, chatMessage_id: str, reactionType: Optional[str] = None
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        request_body_data = None
        request_body_data = {"reactionType": reactionType}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_messages_list_replies(
        self,
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

        Get replies from chats

        Args:
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies"
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

    def chats_messages_create_replies(
        self,
        chat_id: str,
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

        Create new navigation property to replies for chats

        Args:
            chat_id (string): chat-id
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_messages_get_replies(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get replies from chats

        Args:
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_messages_update_replies(
        self,
        chat_id: str,
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

        Update the navigation property replies in chats

        Args:
            chat_id (string): chat-id
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_messages_delete_replies(
        self, chat_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Delete navigation property replies for chats

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_hosted_contents(
        self,
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

        Get hostedContents from chats

        Args:
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
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

    def add_chat_message_hosted_content(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to hostedContents for chats

        Args:
            chat_id (string): chat-id
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_chat_message_hosted_content(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get hostedContents from chats

        Args:
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
            chats.chatMessage
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_chat_reply_hosted_content(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        contentBytes: Optional[str] = None,
        contentType: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property hostedContents in chats

        Args:
            chat_id (string): chat-id
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
            chats.chatMessage
        """
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
            "@odata.type": atodata_type,
            "contentBytes": contentBytes,
            "contentType": contentType,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def del_chat_reply_hosted_content(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete navigation property hostedContents for chats

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_hosted_content_value(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Get media content for the navigation property hostedContents from chats

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_chat_rply_hosted_content_val(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
        body_content: bytes,
    ) -> Any:
        """

        Update media content for the navigation property hostedContents in chats

        Args:
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
            chats.chatMessage
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def del_chat_reply_host_content_val(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        chatMessageHostedContent_id: str,
    ) -> Any:
        """

        Delete media content for the navigation property hostedContents in chats

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            chatMessageHostedContent_id (string): chatMessageHostedContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/{chatMessageHostedContent_id}/$value"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_chat_message_replies_content(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/hostedContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def set_chat_message_reply_reaction(
        self,
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setReaction

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/setReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def soft_delete_message_reply(
        self, chat_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action softDelete

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/softDelete"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def undo_soft_delete_chat_message_reply(
        self, chat_id: str, chatMessage_id: str, chatMessage_id1: str
    ) -> Any:
        """

        Invoke action undoSoftDelete

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        if chatMessage_id1 is None:
            raise ValueError("Missing required parameter 'chatMessage-id1'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/undoSoftDelete"
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
        chat_id: str,
        chatMessage_id: str,
        chatMessage_id1: str,
        reactionType: Optional[str] = None,
    ) -> Any:
        """

        Invoke action unsetReaction

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            chatMessage_id1 (string): chatMessage-id1
            reactionType (string): reactionType

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/{chatMessage_id1}/unsetReaction"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_chat_replies_count(
        self,
        chat_id: str,
        chatMessage_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            chat_id (string): chat-id
            chatMessage_id (string): chatMessage-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_chat_replies_delta(
        self,
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if chatMessage_id is None:
            raise ValueError("Missing required parameter 'chatMessage-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/{chatMessage_id}/replies/delta()"
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

    def chats_messages_get_count_dde(
        self, chat_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_chat_messages_delta(
        self,
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
            chats.chatMessage
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/messages/delta()"
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

    def chats_chat_hide_for_user(self, chat_id: str, user: Optional[Any] = None) -> Any:
        """

        Invoke action hideForUser

        Args:
            chat_id (string): chat-id
            user (string): user

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chat.Actions
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"user": user}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/hideForUser"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_chat_mark_chat_read_for_user(
        self, chat_id: str, user: Optional[Any] = None
    ) -> Any:
        """

        Invoke action markChatReadForUser

        Args:
            chat_id (string): chat-id
            user (string): user

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chat.Actions
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"user": user}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/markChatReadForUser"
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
        chat_id: str,
        user: Optional[Any] = None,
        lastMessageReadDateTime: Optional[str] = None,
    ) -> Any:
        """

        Invoke action markChatUnreadForUser

        Args:
            chat_id (string): chat-id
            user (string): user
            lastMessageReadDateTime (string): lastMessageReadDateTime

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chat.Actions
        """
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/markChatUnreadForUser"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def send_chat_notification(
        self,
        chat_id: str,
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
            chat_id (string): chat-id
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
            chats.chat.Actions
        """
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
        url = (
            f"{self.main_app_client.base_url}/chats/{chat_id}/sendActivityNotification"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_chat_unhide_for_user(
        self, chat_id: str, user: Optional[Any] = None
    ) -> Any:
        """

        Invoke action unhideForUser

        Args:
            chat_id (string): chat-id
            user (string): user

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.chat.Actions
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"user": user}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/unhideForUser"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_list_permission_grants(
        self,
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

        List permissionGrants of a chat

        Args:
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
            chats.resourceSpecificPermissionGrant
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/permissionGrants"
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

    def chats_create_permission_grants(
        self,
        chat_id: str,
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

        Create new navigation property to permissionGrants for chats

        Args:
            chat_id (string): chat-id
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
            chats.resourceSpecificPermissionGrant
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/permissionGrants"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_get_permission_grants(
        self,
        chat_id: str,
        resourceSpecificPermissionGrant_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get permissionGrants from chats

        Args:
            chat_id (string): chat-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.resourceSpecificPermissionGrant
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_update_permission_grants(
        self,
        chat_id: str,
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

        Update the navigation property permissionGrants in chats

        Args:
            chat_id (string): chat-id
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
            chats.resourceSpecificPermissionGrant
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_delete_permission_grants(
        self, chat_id: str, resourceSpecificPermissionGrant_id: str
    ) -> Any:
        """

        Delete navigation property permissionGrants for chats

        Args:
            chat_id (string): chat-id
            resourceSpecificPermissionGrant_id (string): resourceSpecificPermissionGrant-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.resourceSpecificPermissionGrant
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if resourceSpecificPermissionGrant_id is None:
            raise ValueError(
                "Missing required parameter 'resourceSpecificPermissionGrant-id'."
            )
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/permissionGrants/{resourceSpecificPermissionGrant_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_chat_permission_count(
        self, chat_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.resourceSpecificPermissionGrant
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/permissionGrants/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_list_pinned_messages(
        self,
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

        List pinnedChatMessages in a chat

        Args:
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
            chats.pinnedChatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/pinnedMessages"
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

    def chats_create_pinned_messages(
        self,
        chat_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        message: Optional[Any] = None,
    ) -> Any:
        """

        Pin a message in a chat

        Args:
            chat_id (string): chat-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            message (string): Represents details about the chat message that is pinned.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.pinnedChatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        request_body_data = None
        request_body_data = {"id": id, "@odata.type": atodata_type, "message": message}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/pinnedMessages"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_get_pinned_messages(
        self,
        chat_id: str,
        pinnedChatMessageInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get pinnedMessages from chats

        Args:
            chat_id (string): chat-id
            pinnedChatMessageInfo_id (string): pinnedChatMessageInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.pinnedChatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if pinnedChatMessageInfo_id is None:
            raise ValueError("Missing required parameter 'pinnedChatMessageInfo-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/pinnedMessages/{pinnedChatMessageInfo_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_update_pinned_messages(
        self,
        chat_id: str,
        pinnedChatMessageInfo_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        message: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property pinnedMessages in chats

        Args:
            chat_id (string): chat-id
            pinnedChatMessageInfo_id (string): pinnedChatMessageInfo-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            message (string): Represents details about the chat message that is pinned.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.pinnedChatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if pinnedChatMessageInfo_id is None:
            raise ValueError("Missing required parameter 'pinnedChatMessageInfo-id'.")
        request_body_data = None
        request_body_data = {"id": id, "@odata.type": atodata_type, "message": message}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/pinnedMessages/{pinnedChatMessageInfo_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_delete_pinned_messages(
        self, chat_id: str, pinnedChatMessageInfo_id: str
    ) -> Any:
        """

        Unpin a message from a chat

        Args:
            chat_id (string): chat-id
            pinnedChatMessageInfo_id (string): pinnedChatMessageInfo-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.pinnedChatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if pinnedChatMessageInfo_id is None:
            raise ValueError("Missing required parameter 'pinnedChatMessageInfo-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/pinnedMessages/{pinnedChatMessageInfo_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_pinned_chat_message_detail(
        self,
        chat_id: str,
        pinnedChatMessageInfo_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get message from chats

        Args:
            chat_id (string): chat-id
            pinnedChatMessageInfo_id (string): pinnedChatMessageInfo-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.pinnedChatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if pinnedChatMessageInfo_id is None:
            raise ValueError("Missing required parameter 'pinnedChatMessageInfo-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/pinnedMessages/{pinnedChatMessageInfo_id}/message"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_chat_pinned_messages_count(
        self, chat_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.pinnedChatMessageInfo
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/pinnedMessages/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_list_tabs(
        self,
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

        List tabs in chat

        Args:
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
            chats.teamsTab
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/tabs"
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

    def chats_create_tabs(
        self,
        chat_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        configuration: Optional[Any] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Add tab to chat

        Args:
            chat_id (string): chat-id
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
            chats.teamsTab
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/tabs"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def chats_get_tabs(
        self,
        chat_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get tab in chat

        Args:
            chat_id (string): chat-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsTab
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/tabs/{teamsTab_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_update_tabs(
        self,
        chat_id: str,
        teamsTab_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        configuration: Optional[Any] = None,
        displayName: Optional[str] = None,
        webUrl: Optional[str] = None,
        teamsApp: Optional[Any] = None,
    ) -> Any:
        """

        Update tab in chat

        Args:
            chat_id (string): chat-id
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
            chats.teamsTab
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
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
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def chats_delete_tabs(self, chat_id: str, teamsTab_id: str) -> Any:
        """

        Delete tab from chat

        Args:
            chat_id (string): chat-id
            teamsTab_id (string): teamsTab-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsTab
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/tabs/{teamsTab_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def chats_tabs_get_teams_app(
        self,
        chat_id: str,
        teamsTab_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get teamsApp from chats

        Args:
            chat_id (string): chat-id
            teamsTab_id (string): teamsTab-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsTab
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        if teamsTab_id is None:
            raise ValueError("Missing required parameter 'teamsTab-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/tabs/{teamsTab_id}/teamsApp"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_tabs_get_count_b(
        self, chat_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            chat_id (string): chat-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            chats.teamsTab
        """
        if chat_id is None:
            raise ValueError("Missing required parameter 'chat-id'.")
        url = f"{self.main_app_client.base_url}/chats/{chat_id}/tabs/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_get_count_c(
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
            chats.chat
        """
        url = f"{self.main_app_client.base_url}/chats/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def chats_get_all_messages(
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
            chats.chat.Functions
        """
        url = f"{self.main_app_client.base_url}/chats/getAllMessages()"
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

    def chats_get_all_retained_messages(
        self,
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
            chats.chat.Functions
        """
        url = f"{self.main_app_client.base_url}/chats/getAllRetainedMessages()"
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

    def list_tools(self):
        return [
            self.chats_chat_list_chat,
            self.chats_chat_create_chat,
            self.chats_chat_get_chat,
            self.chats_chat_update_chat,
            self.chats_chat_delete_chat,
            self.chats_list_installed_apps,
            self.chats_create_installed_apps,
            self.chats_get_installed_apps,
            self.chats_update_installed_apps,
            self.chats_delete_installed_apps,
            self.upgrade_installed_app,
            self.get_teams_app,
            self.get_installed_app_definition,
            self.get_chat_apps_count,
            self.chats_get_last_message_preview,
            self.chats_update_last_message_preview,
            self.chats_delete_last_message_preview,
            self.chats_list_members,
            self.chats_create_members,
            self.chats_get_members,
            self.chats_update_members,
            self.chats_delete_members,
            self.chats_members_get_count,
            self.chats_chat_members_add,
            self.chats_chat_members_remove,
            self.chats_list_messages,
            self.chats_create_messages,
            self.chats_get_messages,
            self.chats_update_messages,
            self.chats_delete_messages,
            self.get_hosted_content_by_message_id,
            self.create_hosted_content,
            self.get_chat_msg_hosted_content,
            self.update_chat_message_content,
            self.del_chat_msg_hosted_content,
            self.get_chat_msg_hosted_content_val,
            self.update_chat_hosted_content_val,
            self.del_chat_msg_host_content_val,
            self.count_chat_msg_hosted_contents,
            self.set_chat_message_reaction,
            self.delete_message_softly,
            self.restore_soft_deleted_message,
            self.unset_message_reaction,
            self.chats_messages_list_replies,
            self.chats_messages_create_replies,
            self.chats_messages_get_replies,
            self.chats_messages_update_replies,
            self.chats_messages_delete_replies,
            self.get_hosted_contents,
            self.add_chat_message_hosted_content,
            self.get_chat_message_hosted_content,
            self.patch_chat_reply_hosted_content,
            self.del_chat_reply_hosted_content,
            self.get_chat_hosted_content_value,
            self.update_chat_rply_hosted_content_val,
            self.del_chat_reply_host_content_val,
            self.count_chat_message_replies_content,
            self.set_chat_message_reply_reaction,
            self.soft_delete_message_reply,
            self.undo_soft_delete_chat_message_reply,
            self.unset_chat_message_reaction,
            self.get_chat_replies_count,
            self.get_chat_replies_delta,
            self.chats_messages_get_count_dde,
            self.chats_chat_messages_delta,
            self.chats_chat_hide_for_user,
            self.chats_chat_mark_chat_read_for_user,
            self.mark_chat_unread_for_user,
            self.send_chat_notification,
            self.chats_chat_unhide_for_user,
            self.chats_list_permission_grants,
            self.chats_create_permission_grants,
            self.chats_get_permission_grants,
            self.chats_update_permission_grants,
            self.chats_delete_permission_grants,
            self.get_chat_permission_count,
            self.chats_list_pinned_messages,
            self.chats_create_pinned_messages,
            self.chats_get_pinned_messages,
            self.chats_update_pinned_messages,
            self.chats_delete_pinned_messages,
            self.get_pinned_chat_message_detail,
            self.get_chat_pinned_messages_count,
            self.chats_list_tabs,
            self.chats_create_tabs,
            self.chats_get_tabs,
            self.chats_update_tabs,
            self.chats_delete_tabs,
            self.chats_tabs_get_teams_app,
            self.chats_tabs_get_count_b,
            self.chats_get_count_c,
            self.chats_get_all_messages,
            self.chats_get_all_retained_messages,
        ]
