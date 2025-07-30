from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class TeamworkApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

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
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        apiVersion: Optional[float] = None,
        displayName: Optional[str] = None,
        eligibilityFilteringEnabledEntities: Optional[Any] = None,
        encryption: Optional[Any] = None,
        isActive: Optional[bool] = None,
        supportedEntities: Optional[Any] = None,
        url: Optional[str] = None,
    ) -> Any:
        """

        Create workforceIntegration

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            apiVersion (number): API version for the callback URL. Start with 1.
            displayName (string): Name of the workforce integration.
            eligibilityFilteringEnabledEntities (string): Support to view eligibility-filtered results. Possible values are: none, swapRequest, offerShiftRequest, unknownFutureValue, timeOffReason. Use the Prefer: include-unknown-enum-members request header to get the following value in this evolvable enum: timeOffReason.
            encryption (string): The workforce integration encryption resource.
            isActive (boolean): Indicates whether this workforce integration is currently active and available.
            supportedEntities (string): The Shifts entities supported for synchronous change notifications. Shifts call back to the provided URL when client changes occur to the entities specified in this property. By default, no entities are supported for change notifications. Possible values are: none, shift, swapRequest, userShiftPreferences, openShift, openShiftRequest, offerShiftRequest, unknownFutureValue, timeCard, timeOffReason, timeOff, timeOffRequest. Use the Prefer: include-unknown-enum-members request header to get the following values in this evolvable enum: timeCard , timeOffReason , timeOff , timeOffRequest.
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
            "@odata.type": atodata_type,
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
        atodata_type: str,
        id: Optional[str] = None,
        createdBy: Optional[Any] = None,
        createdDateTime: Optional[str] = None,
        lastModifiedBy: Optional[Any] = None,
        lastModifiedDateTime: Optional[str] = None,
        apiVersion: Optional[float] = None,
        displayName: Optional[str] = None,
        eligibilityFilteringEnabledEntities: Optional[Any] = None,
        encryption: Optional[Any] = None,
        isActive: Optional[bool] = None,
        supportedEntities: Optional[Any] = None,
        url: Optional[str] = None,
    ) -> Any:
        """

        Update workforceIntegration

        Args:
            workforceIntegration_id (string): workforceIntegration-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdBy (string): Identity of the creator of the entity.
            createdDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            lastModifiedBy (string): Identity of the person who last modified the entity.
            lastModifiedDateTime (string): The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            apiVersion (number): API version for the callback URL. Start with 1.
            displayName (string): Name of the workforce integration.
            eligibilityFilteringEnabledEntities (string): Support to view eligibility-filtered results. Possible values are: none, swapRequest, offerShiftRequest, unknownFutureValue, timeOffReason. Use the Prefer: include-unknown-enum-members request header to get the following value in this evolvable enum: timeOffReason.
            encryption (string): The workforce integration encryption resource.
            isActive (boolean): Indicates whether this workforce integration is currently active and available.
            supportedEntities (string): The Shifts entities supported for synchronous change notifications. Shifts call back to the provided URL when client changes occur to the entities specified in this property. By default, no entities are supported for change notifications. Possible values are: none, shift, swapRequest, userShiftPreferences, openShift, openShiftRequest, offerShiftRequest, unknownFutureValue, timeCard, timeOffReason, timeOff, timeOffRequest. Use the Prefer: include-unknown-enum-members request header to get the following values in this evolvable enum: timeCard , timeOffReason , timeOff , timeOffRequest.
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
            "@odata.type": atodata_type,
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
            self.list_workforce_integrations,
            self.create_workforce_integration,
            self.get_workforce_integration,
            self.update_workforce_integration,
            self.delete_workforce_integration_by_id,
            self.get_workforce_integration_count,
        ]
