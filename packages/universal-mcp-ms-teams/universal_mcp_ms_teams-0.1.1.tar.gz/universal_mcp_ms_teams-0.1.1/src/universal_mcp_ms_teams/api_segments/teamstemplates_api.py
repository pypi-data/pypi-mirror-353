from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class TeamstemplatesApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def list_team_templates(
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

        Get entities from teamsTemplates

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
            teamsTemplates.teamsTemplate, important
        """
        url = f"{self.main_app_client.base_url}/teamsTemplates"
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

    def create_team_template(self, atodata_type: str, id: Optional[str] = None) -> Any:
        """

        Add new entity to teamsTemplates

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.

        Returns:
            Any: Created entity

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamsTemplates.teamsTemplate
        """
        request_body_data = None
        request_body_data = {"id": id, "@odata.type": atodata_type}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamsTemplates"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_teams_template_by_id(
        self,
        teamsTemplate_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get entity from teamsTemplates by key

        Args:
            teamsTemplate_id (string): teamsTemplate-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved entity

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamsTemplates.teamsTemplate
        """
        if teamsTemplate_id is None:
            raise ValueError("Missing required parameter 'teamsTemplate-id'.")
        url = f"{self.main_app_client.base_url}/teamsTemplates/{teamsTemplate_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_teams_template(
        self, teamsTemplate_id: str, atodata_type: str, id: Optional[str] = None
    ) -> Any:
        """

        Update entity in teamsTemplates

        Args:
            teamsTemplate_id (string): teamsTemplate-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamsTemplates.teamsTemplate
        """
        if teamsTemplate_id is None:
            raise ValueError("Missing required parameter 'teamsTemplate-id'.")
        request_body_data = None
        request_body_data = {"id": id, "@odata.type": atodata_type}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/teamsTemplates/{teamsTemplate_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_team_template_by_id(self, teamsTemplate_id: str) -> Any:
        """

        Delete entity from teamsTemplates

        Args:
            teamsTemplate_id (string): teamsTemplate-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            teamsTemplates.teamsTemplate
        """
        if teamsTemplate_id is None:
            raise ValueError("Missing required parameter 'teamsTemplate-id'.")
        url = f"{self.main_app_client.base_url}/teamsTemplates/{teamsTemplate_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def teams_templates_get_count_ba(
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
            teamsTemplates.teamsTemplate
        """
        url = f"{self.main_app_client.base_url}/teamsTemplates/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.list_team_templates,
            self.create_team_template,
            self.get_teams_template_by_id,
            self.update_teams_template,
            self.delete_team_template_by_id,
            self.teams_templates_get_count_ba,
        ]
