from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class CopilotApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def copilot_get_users(
        self,
        aiUser_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get users from copilot

        Args:
            aiUser_id (string): aiUser-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            copilot.aiUser, important
        """
        if aiUser_id is None:
            raise ValueError("Missing required parameter 'aiUser-id'.")
        url = f"{self.main_app_client.base_url}/copilot/users/{aiUser_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def copilot_update_users(
        self,
        aiUser_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        interactionHistory: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property users in copilot

        Args:
            aiUser_id (string): aiUser-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            interactionHistory (string): The history of interactions between AI agents and users.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            copilot.aiUser
        """
        if aiUser_id is None:
            raise ValueError("Missing required parameter 'aiUser-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "interactionHistory": interactionHistory,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/copilot/users/{aiUser_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def copilot_delete_users(self, aiUser_id: str) -> Any:
        """

        Delete navigation property users for copilot

        Args:
            aiUser_id (string): aiUser-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            copilot.aiUser
        """
        if aiUser_id is None:
            raise ValueError("Missing required parameter 'aiUser-id'.")
        url = f"{self.main_app_client.base_url}/copilot/users/{aiUser_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_interaction_history(
        self,
        aiUser_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get interactionHistory from copilot

        Args:
            aiUser_id (string): aiUser-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            copilot.aiUser
        """
        if aiUser_id is None:
            raise ValueError("Missing required parameter 'aiUser-id'.")
        url = f"{self.main_app_client.base_url}/copilot/users/{aiUser_id}/interactionHistory"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_interaction_history(
        self, aiUser_id: str, atodata_type: str, id: Optional[str] = None
    ) -> Any:
        """

        Update the navigation property interactionHistory in copilot

        Args:
            aiUser_id (string): aiUser-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            copilot.aiUser
        """
        if aiUser_id is None:
            raise ValueError("Missing required parameter 'aiUser-id'.")
        request_body_data = None
        request_body_data = {"id": id, "@odata.type": atodata_type}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/copilot/users/{aiUser_id}/interactionHistory"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_interaction_history(self, aiUser_id: str) -> Any:
        """

        Delete navigation property interactionHistory for copilot

        Args:
            aiUser_id (string): aiUser-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            copilot.aiUser
        """
        if aiUser_id is None:
            raise ValueError("Missing required parameter 'aiUser-id'.")
        url = f"{self.main_app_client.base_url}/copilot/users/{aiUser_id}/interactionHistory"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_enterprise_user_interactions(
        self,
        aiUser_id: str,
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

        Invoke function getAllEnterpriseInteractions

        Args:
            aiUser_id (string): aiUser-id
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
            copilot.aiUser
        """
        if aiUser_id is None:
            raise ValueError("Missing required parameter 'aiUser-id'.")
        url = f"{self.main_app_client.base_url}/copilot/users/{aiUser_id}/interactionHistory/getAllEnterpriseInteractions()"
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

    def copilot_users_get_count_ed(
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
            copilot.aiUser
        """
        url = f"{self.main_app_client.base_url}/copilot/users/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.copilot_get_users,
            self.copilot_update_users,
            self.copilot_delete_users,
            self.get_interaction_history,
            self.update_interaction_history,
            self.delete_interaction_history,
            self.list_enterprise_user_interactions,
            self.copilot_users_get_count_ed,
        ]
