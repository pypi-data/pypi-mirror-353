from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class UsersApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def list_installed_apps_by_user(
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
        atodata_type: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[Any] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
        chat: Optional[Any] = None,
    ) -> Any:
        """

        Install app for user

        Args:
            user_id (string): user-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (string): The set of resource-specific permissions consented to while installing or upgrading the teamsApp.
            teamsApp (string): The app that is installed.
            teamsAppDefinition (string): The details of this version of the app.
            chat (string): The chat between the user and Teams app.

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
            "@odata.type": atodata_type,
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

    def get_user_teamwork_app_installation(
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
        atodata_type: str,
        id: Optional[str] = None,
        consentedPermissionSet: Optional[Any] = None,
        teamsApp: Optional[Any] = None,
        teamsAppDefinition: Optional[Any] = None,
        chat: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property installedApps in users

        Args:
            user_id (string): user-id
            userScopeTeamsAppInstallation_id (string): userScopeTeamsAppInstallation-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            consentedPermissionSet (string): The set of resource-specific permissions consented to while installing or upgrading the teamsApp.
            teamsApp (string): The app that is installed.
            teamsAppDefinition (string): The details of this version of the app.
            chat (string): The chat between the user and Teams app.

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
            "@odata.type": atodata_type,
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

    def users_get_teamwork(
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

    def users_update_teamwork(
        self,
        user_id: str,
        atodata_type: str,
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
            atodata_type (string): @odata.type
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
            "@odata.type": atodata_type,
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

    def users_delete_teamwork(self, user_id: str) -> Any:
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
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        tenantId: Optional[str] = None,
        team: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to associatedTeams for users

        Args:
            user_id (string): user-id
            atodata_type (string): @odata.type
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
            "@odata.type": atodata_type,
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
        atodata_type: str,
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
            atodata_type (string): @odata.type
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
            "@odata.type": atodata_type,
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

    def send_user_activity_notification(
        self,
        user_id: str,
        topic: Optional[Any] = None,
        activityType: Optional[str] = None,
        chainId: Optional[float] = None,
        previewText: Optional[Any] = None,
        teamsAppId: Optional[str] = None,
        templateParameters: Optional[List[dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action sendActivityNotification

        Args:
            user_id (string): user-id
            topic (string): topic
            activityType (string): activityType
            chainId (number): chainId
            previewText (string): previewText
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
        url = f"{self.main_app_client.base_url}/users/{user_id}/teamwork/sendActivityNotification"
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
            self.list_installed_apps_by_user,
            self.install_app_for_user,
            self.get_user_teamwork_app_installation,
            self.patch_user_teamwork_app,
            self.delete_installed_app,
            self.users_get_teamwork,
            self.users_update_teamwork,
            self.users_delete_teamwork,
            self.get_associated_teams,
            self.associate_team_to_user,
            self.get_associated_teams_by_user,
            self.update_associated_team_info,
            self.delete_associated_team,
            self.get_associated_team,
            self.get_associated_teams_count,
            self.get_chat_app_installation,
            self.get_installed_teams_app,
            self.get_installed_app_details,
            self.get_installed_apps_count,
            self.send_user_activity_notification,
        ]
