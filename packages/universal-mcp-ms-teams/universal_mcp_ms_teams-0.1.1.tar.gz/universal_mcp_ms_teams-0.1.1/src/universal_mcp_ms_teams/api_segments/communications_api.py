from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class CommunicationsApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def list_communications(
        self, select: Optional[List[str]] = None, expand: Optional[List[str]] = None
    ) -> dict[str, Any]:
        """

        Get communications

        Args:
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved entity

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.cloudCommunications
        """
        url = f"{self.main_app_client.base_url}/communications"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_communication(
        self,
        atodata_type: str,
        callRecords: Optional[List[Any]] = None,
        calls: Optional[List[Any]] = None,
        onlineMeetings: Optional[List[Any]] = None,
        presences: Optional[List[Any]] = None,
    ) -> dict[str, Any]:
        """

        Update communications

        Args:
            atodata_type (string): @odata.type
            callRecords (array): callRecords
            calls (array): calls
            onlineMeetings (array): onlineMeetings
            presences (array): presences

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.cloudCommunications
        """
        request_body_data = None
        request_body_data = {
            "callRecords": callRecords,
            "calls": calls,
            "onlineMeetings": onlineMeetings,
            "presences": presences,
            "@odata.type": atodata_type,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def communications_list_call_records(
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

        List callRecords

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
            communications.callRecord
        """
        url = f"{self.main_app_client.base_url}/communications/callRecords"
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

    def create_call_record(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        endDateTime: Optional[str] = None,
        joinWebUrl: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        modalities: Optional[List[str]] = None,
        organizer: Optional[Any] = None,
        participants: Optional[List[dict[str, Any]]] = None,
        startDateTime: Optional[str] = None,
        type: Optional[str] = None,
        version: Optional[float] = None,
        organizer_v2: Optional[Any] = None,
        participants_v2: Optional[List[Any]] = None,
        sessions: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to callRecords for communications

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            endDateTime (string): UTC time when the last user left the call. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            joinWebUrl (string): Meeting URL associated to the call. May not be available for a peerToPeer call record type.
            lastModifiedDateTime (string): UTC time when the call record was created. The DatetimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            modalities (array): List of all the modalities used in the call. Possible values are: unknown, audio, video, videoBasedScreenSharing, data, screenSharing, unknownFutureValue.
            organizer (string): The organizing party's identity. The organizer property is deprecated and will stop returning data on June 30, 2026. Going forward, use the organizer_v2 relationship.
            participants (array): List of distinct identities involved in the call. Limited to 130 entries. The participants property is deprecated and will stop returning data on June 30, 2026. Going forward, use the participants_v2 relationship.
            startDateTime (string): UTC time when the first user joined the call. The DatetimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            type (string): type
            version (number): Monotonically increasing version of the call record. Higher version call records with the same id includes additional data compared to the lower version.
            organizer_v2 (string): Identity of the organizer of the call. This relationship is expanded by default in callRecord methods.
            participants_v2 (array): List of distinct participants in the call.
            sessions (array): List of sessions involved in the call. Peer-to-peer calls typically only have one session, whereas group calls typically have at least one session per participant. Read-only. Nullable.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "endDateTime": endDateTime,
            "joinWebUrl": joinWebUrl,
            "lastModifiedDateTime": lastModifiedDateTime,
            "modalities": modalities,
            "organizer": organizer,
            "participants": participants,
            "startDateTime": startDateTime,
            "type": type,
            "version": version,
            "organizer_v2": organizer_v2,
            "participants_v2": participants_v2,
            "sessions": sessions,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def communications_get_call_records(
        self,
        callRecord_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get callRecord

        Args:
            callRecord_id (string): callRecord-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_record(
        self,
        callRecord_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        endDateTime: Optional[str] = None,
        joinWebUrl: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        modalities: Optional[List[str]] = None,
        organizer: Optional[Any] = None,
        participants: Optional[List[dict[str, Any]]] = None,
        startDateTime: Optional[str] = None,
        type: Optional[str] = None,
        version: Optional[float] = None,
        organizer_v2: Optional[Any] = None,
        participants_v2: Optional[List[Any]] = None,
        sessions: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property callRecords in communications

        Args:
            callRecord_id (string): callRecord-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            endDateTime (string): UTC time when the last user left the call. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            joinWebUrl (string): Meeting URL associated to the call. May not be available for a peerToPeer call record type.
            lastModifiedDateTime (string): UTC time when the call record was created. The DatetimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            modalities (array): List of all the modalities used in the call. Possible values are: unknown, audio, video, videoBasedScreenSharing, data, screenSharing, unknownFutureValue.
            organizer (string): The organizing party's identity. The organizer property is deprecated and will stop returning data on June 30, 2026. Going forward, use the organizer_v2 relationship.
            participants (array): List of distinct identities involved in the call. Limited to 130 entries. The participants property is deprecated and will stop returning data on June 30, 2026. Going forward, use the participants_v2 relationship.
            startDateTime (string): UTC time when the first user joined the call. The DatetimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            type (string): type
            version (number): Monotonically increasing version of the call record. Higher version call records with the same id includes additional data compared to the lower version.
            organizer_v2 (string): Identity of the organizer of the call. This relationship is expanded by default in callRecord methods.
            participants_v2 (array): List of distinct participants in the call.
            sessions (array): List of sessions involved in the call. Peer-to-peer calls typically only have one session, whereas group calls typically have at least one session per participant. Read-only. Nullable.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "endDateTime": endDateTime,
            "joinWebUrl": joinWebUrl,
            "lastModifiedDateTime": lastModifiedDateTime,
            "modalities": modalities,
            "organizer": organizer,
            "participants": participants,
            "startDateTime": startDateTime,
            "type": type,
            "version": version,
            "organizer_v2": organizer_v2,
            "participants_v2": participants_v2,
            "sessions": sessions,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_call_record_by_id(self, callRecord_id: str) -> Any:
        """

        Delete navigation property callRecords for communications

        Args:
            callRecord_id (string): callRecord-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_call_record_organizer_v(
        self,
        callRecord_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get organizer_v2 from communications

        Args:
            callRecord_id (string): callRecord-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/organizer_v2"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_record_organizer_v(
        self,
        callRecord_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        administrativeUnitInfos: Optional[List[dict[str, Any]]] = None,
        identity: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property organizer_v2 in communications

        Args:
            callRecord_id (string): callRecord-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            administrativeUnitInfos (array): List of administrativeUnitInfo objects for the call participant.
            identity (string): The identity of the call participant.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "administrativeUnitInfos": administrativeUnitInfos,
            "identity": identity,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/organizer_v2"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_call_record_organizer(self, callRecord_id: str) -> Any:
        """

        Delete navigation property organizer_v2 for communications

        Args:
            callRecord_id (string): callRecord-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/organizer_v2"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_call_record_participants_v(
        self,
        callRecord_id: str,
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

        List participants_v2

        Args:
            callRecord_id (string): callRecord-id
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
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/participants_v2"
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

    def add_call_record_participants_v(
        self,
        callRecord_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        administrativeUnitInfos: Optional[List[dict[str, Any]]] = None,
        identity: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to participants_v2 for communications

        Args:
            callRecord_id (string): callRecord-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            administrativeUnitInfos (array): List of administrativeUnitInfo objects for the call participant.
            identity (string): The identity of the call participant.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "administrativeUnitInfos": administrativeUnitInfos,
            "identity": identity,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/participants_v2"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_participant_by_id_v(
        self,
        callRecord_id: str,
        participant_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get participants_v2 from communications

        Args:
            callRecord_id (string): callRecord-id
            participant_id (string): participant-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/participants_v2/{participant_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_participant_v(
        self,
        callRecord_id: str,
        participant_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        administrativeUnitInfos: Optional[List[dict[str, Any]]] = None,
        identity: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property participants_v2 in communications

        Args:
            callRecord_id (string): callRecord-id
            participant_id (string): participant-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            administrativeUnitInfos (array): List of administrativeUnitInfo objects for the call participant.
            identity (string): The identity of the call participant.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "administrativeUnitInfos": administrativeUnitInfos,
            "identity": identity,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/participants_v2/{participant_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_participant_by_id(self, callRecord_id: str, participant_id: str) -> Any:
        """

        Delete navigation property participants_v2 for communications

        Args:
            callRecord_id (string): callRecord-id
            participant_id (string): participant-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/participants_v2/{participant_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_call_record_participants_count(
        self,
        callRecord_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            callRecord_id (string): callRecord-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/participants_v2/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_call_record_sessions(
        self,
        callRecord_id: str,
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

        List sessions

        Args:
            callRecord_id (string): callRecord-id
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
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions"
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

    def create_call_record_session(
        self,
        callRecord_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callee: Optional[Any] = None,
        caller: Optional[Any] = None,
        endDateTime: Optional[str] = None,
        failureInfo: Optional[Any] = None,
        isTest: Optional[bool] = None,
        modalities: Optional[List[str]] = None,
        startDateTime: Optional[str] = None,
        segments: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to sessions for communications

        Args:
            callRecord_id (string): callRecord-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callee (string): Endpoint that answered the session.
            caller (string): Endpoint that initiated the session.
            endDateTime (string): UTC time when the last user left the session. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            failureInfo (string): Failure information associated with the session if the session failed.
            isTest (boolean): Specifies whether the session is a test.
            modalities (array): List of modalities present in the session. Possible values are: unknown, audio, video, videoBasedScreenSharing, data, screenSharing, unknownFutureValue.
            startDateTime (string): UTC time when the first user joined the session. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            segments (array): The list of segments involved in the session. Read-only. Nullable.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callee": callee,
            "caller": caller,
            "endDateTime": endDateTime,
            "failureInfo": failureInfo,
            "isTest": isTest,
            "modalities": modalities,
            "startDateTime": startDateTime,
            "segments": segments,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_call_session_by_id(
        self,
        callRecord_id: str,
        session_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get sessions from communications

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_session(
        self,
        callRecord_id: str,
        session_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callee: Optional[Any] = None,
        caller: Optional[Any] = None,
        endDateTime: Optional[str] = None,
        failureInfo: Optional[Any] = None,
        isTest: Optional[bool] = None,
        modalities: Optional[List[str]] = None,
        startDateTime: Optional[str] = None,
        segments: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property sessions in communications

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callee (string): Endpoint that answered the session.
            caller (string): Endpoint that initiated the session.
            endDateTime (string): UTC time when the last user left the session. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            failureInfo (string): Failure information associated with the session if the session failed.
            isTest (boolean): Specifies whether the session is a test.
            modalities (array): List of modalities present in the session. Possible values are: unknown, audio, video, videoBasedScreenSharing, data, screenSharing, unknownFutureValue.
            startDateTime (string): UTC time when the first user joined the session. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            segments (array): The list of segments involved in the session. Read-only. Nullable.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callee": callee,
            "caller": caller,
            "endDateTime": endDateTime,
            "failureInfo": failureInfo,
            "isTest": isTest,
            "modalities": modalities,
            "startDateTime": startDateTime,
            "segments": segments,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_call_session(self, callRecord_id: str, session_id: str) -> Any:
        """

        Delete navigation property sessions for communications

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_call_segments(
        self,
        callRecord_id: str,
        session_id: str,
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

        Get segments from communications

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id
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
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}/segments"
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

    def create_segment(
        self,
        callRecord_id: str,
        session_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callee: Optional[Any] = None,
        caller: Optional[Any] = None,
        endDateTime: Optional[str] = None,
        failureInfo: Optional[Any] = None,
        media: Optional[List[dict[str, Any]]] = None,
        startDateTime: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to segments for communications

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callee (string): Endpoint that answered this segment.
            caller (string): Endpoint that initiated this segment.
            endDateTime (string): UTC time when the segment ended. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            failureInfo (string): Failure information associated with the segment if it failed.
            media (array): Media associated with this segment.
            startDateTime (string): UTC time when the segment started. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callee": callee,
            "caller": caller,
            "endDateTime": endDateTime,
            "failureInfo": failureInfo,
            "media": media,
            "startDateTime": startDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}/segments"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_call_segment(
        self,
        callRecord_id: str,
        session_id: str,
        segment_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get segments from communications

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id
            segment_id (string): segment-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}/segments/{segment_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_record_segment(
        self,
        callRecord_id: str,
        session_id: str,
        segment_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callee: Optional[Any] = None,
        caller: Optional[Any] = None,
        endDateTime: Optional[str] = None,
        failureInfo: Optional[Any] = None,
        media: Optional[List[dict[str, Any]]] = None,
        startDateTime: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property segments in communications

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id
            segment_id (string): segment-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callee (string): Endpoint that answered this segment.
            caller (string): Endpoint that initiated this segment.
            endDateTime (string): UTC time when the segment ended. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
            failureInfo (string): Failure information associated with the segment if it failed.
            media (array): Media associated with this segment.
            startDateTime (string): UTC time when the segment started. The DateTimeOffset type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callee": callee,
            "caller": caller,
            "endDateTime": endDateTime,
            "failureInfo": failureInfo,
            "media": media,
            "startDateTime": startDateTime,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}/segments/{segment_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_segment_by_id(
        self, callRecord_id: str, session_id: str, segment_id: str
    ) -> Any:
        """

        Delete navigation property segments for communications

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id
            segment_id (string): segment-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        if segment_id is None:
            raise ValueError("Missing required parameter 'segment-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}/segments/{segment_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_call_segments(
        self,
        callRecord_id: str,
        session_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            callRecord_id (string): callRecord-id
            session_id (string): session-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        if session_id is None:
            raise ValueError("Missing required parameter 'session-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/{session_id}/segments/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_call_record_sessions(
        self,
        callRecord_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            callRecord_id (string): callRecord-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if callRecord_id is None:
            raise ValueError("Missing required parameter 'callRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/{callRecord_id}/sessions/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_call_records_count(
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
            communications.callRecord
        """
        url = f"{self.main_app_client.base_url}/communications/callRecords/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_direct_routing_calls(
        self,
        fromDateTime: str,
        toDateTime: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
    ) -> dict[str, Any]:
        """

        Invoke function getDirectRoutingCalls

        Args:
            fromDateTime (string): fromDateTime
            toDateTime (string): toDateTime
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if fromDateTime is None:
            raise ValueError("Missing required parameter 'fromDateTime'.")
        if toDateTime is None:
            raise ValueError("Missing required parameter 'toDateTime'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/microsoft.graph.callRecords.getDirectRoutingCalls(fromDateTime={fromDateTime},toDateTime={toDateTime})"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_pstn_calls(
        self,
        fromDateTime: str,
        toDateTime: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
    ) -> dict[str, Any]:
        """

        Invoke function getPstnCalls

        Args:
            fromDateTime (string): fromDateTime
            toDateTime (string): toDateTime
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.callRecord
        """
        if fromDateTime is None:
            raise ValueError("Missing required parameter 'fromDateTime'.")
        if toDateTime is None:
            raise ValueError("Missing required parameter 'toDateTime'.")
        url = f"{self.main_app_client.base_url}/communications/callRecords/microsoft.graph.callRecords.getPstnCalls(fromDateTime={fromDateTime},toDateTime={toDateTime})"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def communications_list_calls(
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

        Get call

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
            communications.call
        """
        url = f"{self.main_app_client.base_url}/communications/calls"
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

    def communications_create_calls(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        callbackUri: Optional[str] = None,
        callChainId: Optional[str] = None,
        callOptions: Optional[Any] = None,
        callRoutes: Optional[List[dict[str, Any]]] = None,
        chatInfo: Optional[Any] = None,
        direction: Optional[Any] = None,
        incomingContext: Optional[Any] = None,
        mediaConfig: Optional[Any] = None,
        mediaState: Optional[Any] = None,
        meetingInfo: Optional[Any] = None,
        myParticipantId: Optional[str] = None,
        requestedModalities: Optional[List[Any]] = None,
        resultInfo: Optional[Any] = None,
        source: Optional[Any] = None,
        state: Optional[Any] = None,
        subject: Optional[str] = None,
        targets: Optional[List[dict[str, Any]]] = None,
        tenantId: Optional[str] = None,
        toneInfo: Optional[Any] = None,
        transcription: Optional[Any] = None,
        audioRoutingGroups: Optional[List[Any]] = None,
        contentSharingSessions: Optional[List[Any]] = None,
        operations: Optional[List[Any]] = None,
        participants: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create call

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callbackUri (string): The callback URL on which callbacks are delivered. Must be an HTTPS URL.
            callChainId (string): A unique identifier for all the participant calls in a conference or a unique identifier for two participant calls in a P2P call.  This identifier must be copied over from Microsoft.Graph.Call.CallChainId.
            callOptions (string): Contains the optional features for the call.
            callRoutes (array): The routing information on how the call was retargeted. Read-only.
            chatInfo (string): The chat information. Required information for joining a meeting.
            direction (string): The direction of the call. The possible values are incoming or outgoing. Read-only.
            incomingContext (string): Call context associated with an incoming call.
            mediaConfig (string): The media configuration. Required.
            mediaState (string): Read-only. The call media state.
            meetingInfo (string): The meeting information. Required information for meeting scenarios.
            myParticipantId (string): myParticipantId
            requestedModalities (array): The list of requested modalities. Possible values are: unknown, audio, video, videoBasedScreenSharing, data.
            resultInfo (string): The result information. For example, the result can hold termination reason. Read-only.
            source (string): The originator of the call.
            state (string): The call state. Possible values are: incoming, establishing, ringing, established, hold, transferring, transferAccepted, redirecting, terminating, terminated. Read-only.
            subject (string): The subject of the conversation.
            targets (array): The targets of the call. Required information for creating peer to peer call.
            tenantId (string): tenantId
            toneInfo (string): toneInfo
            transcription (string): The transcription information for the call. Read-only.
            audioRoutingGroups (array): audioRoutingGroups
            contentSharingSessions (array): contentSharingSessions
            operations (array): operations
            participants (array): participants

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callbackUri": callbackUri,
            "callChainId": callChainId,
            "callOptions": callOptions,
            "callRoutes": callRoutes,
            "chatInfo": chatInfo,
            "direction": direction,
            "incomingContext": incomingContext,
            "mediaConfig": mediaConfig,
            "mediaState": mediaState,
            "meetingInfo": meetingInfo,
            "myParticipantId": myParticipantId,
            "requestedModalities": requestedModalities,
            "resultInfo": resultInfo,
            "source": source,
            "state": state,
            "subject": subject,
            "targets": targets,
            "tenantId": tenantId,
            "toneInfo": toneInfo,
            "transcription": transcription,
            "audioRoutingGroups": audioRoutingGroups,
            "contentSharingSessions": contentSharingSessions,
            "operations": operations,
            "participants": participants,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def communications_get_calls(
        self,
        call_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get call

        Args:
            call_id (string): call-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def communications_update_calls(
        self,
        call_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callbackUri: Optional[str] = None,
        callChainId: Optional[str] = None,
        callOptions: Optional[Any] = None,
        callRoutes: Optional[List[dict[str, Any]]] = None,
        chatInfo: Optional[Any] = None,
        direction: Optional[Any] = None,
        incomingContext: Optional[Any] = None,
        mediaConfig: Optional[Any] = None,
        mediaState: Optional[Any] = None,
        meetingInfo: Optional[Any] = None,
        myParticipantId: Optional[str] = None,
        requestedModalities: Optional[List[Any]] = None,
        resultInfo: Optional[Any] = None,
        source: Optional[Any] = None,
        state: Optional[Any] = None,
        subject: Optional[str] = None,
        targets: Optional[List[dict[str, Any]]] = None,
        tenantId: Optional[str] = None,
        toneInfo: Optional[Any] = None,
        transcription: Optional[Any] = None,
        audioRoutingGroups: Optional[List[Any]] = None,
        contentSharingSessions: Optional[List[Any]] = None,
        operations: Optional[List[Any]] = None,
        participants: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property calls in communications

        Args:
            call_id (string): call-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callbackUri (string): The callback URL on which callbacks are delivered. Must be an HTTPS URL.
            callChainId (string): A unique identifier for all the participant calls in a conference or a unique identifier for two participant calls in a P2P call.  This identifier must be copied over from Microsoft.Graph.Call.CallChainId.
            callOptions (string): Contains the optional features for the call.
            callRoutes (array): The routing information on how the call was retargeted. Read-only.
            chatInfo (string): The chat information. Required information for joining a meeting.
            direction (string): The direction of the call. The possible values are incoming or outgoing. Read-only.
            incomingContext (string): Call context associated with an incoming call.
            mediaConfig (string): The media configuration. Required.
            mediaState (string): Read-only. The call media state.
            meetingInfo (string): The meeting information. Required information for meeting scenarios.
            myParticipantId (string): myParticipantId
            requestedModalities (array): The list of requested modalities. Possible values are: unknown, audio, video, videoBasedScreenSharing, data.
            resultInfo (string): The result information. For example, the result can hold termination reason. Read-only.
            source (string): The originator of the call.
            state (string): The call state. Possible values are: incoming, establishing, ringing, established, hold, transferring, transferAccepted, redirecting, terminating, terminated. Read-only.
            subject (string): The subject of the conversation.
            targets (array): The targets of the call. Required information for creating peer to peer call.
            tenantId (string): tenantId
            toneInfo (string): toneInfo
            transcription (string): The transcription information for the call. Read-only.
            audioRoutingGroups (array): audioRoutingGroups
            contentSharingSessions (array): contentSharingSessions
            operations (array): operations
            participants (array): participants

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callbackUri": callbackUri,
            "callChainId": callChainId,
            "callOptions": callOptions,
            "callRoutes": callRoutes,
            "chatInfo": chatInfo,
            "direction": direction,
            "incomingContext": incomingContext,
            "mediaConfig": mediaConfig,
            "mediaState": mediaState,
            "meetingInfo": meetingInfo,
            "myParticipantId": myParticipantId,
            "requestedModalities": requestedModalities,
            "resultInfo": resultInfo,
            "source": source,
            "state": state,
            "subject": subject,
            "targets": targets,
            "tenantId": tenantId,
            "toneInfo": toneInfo,
            "transcription": transcription,
            "audioRoutingGroups": audioRoutingGroups,
            "contentSharingSessions": contentSharingSessions,
            "operations": operations,
            "participants": participants,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def communications_delete_calls(self, call_id: str) -> Any:
        """

        Delete call

        Args:
            call_id (string): call-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_audio_routing_groups(
        self,
        call_id: str,
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

        List audioRoutingGroups

        Args:
            call_id (string): call-id
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
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/audioRoutingGroups"
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

    def add_audio_routing_group(
        self,
        call_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        receivers: Optional[List[str]] = None,
        routingMode: Optional[str] = None,
        sources: Optional[List[str]] = None,
    ) -> Any:
        """

        Create audioRoutingGroup

        Args:
            call_id (string): call-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            receivers (array): List of receiving participant ids.
            routingMode (string): routingMode
            sources (array): List of source participant ids.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "receivers": receivers,
            "routingMode": routingMode,
            "sources": sources,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/audioRoutingGroups"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_audio_routing_group_details(
        self,
        call_id: str,
        audioRoutingGroup_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get audioRoutingGroup

        Args:
            call_id (string): call-id
            audioRoutingGroup_id (string): audioRoutingGroup-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if audioRoutingGroup_id is None:
            raise ValueError("Missing required parameter 'audioRoutingGroup-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/audioRoutingGroups/{audioRoutingGroup_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_audio_routing_group(
        self,
        call_id: str,
        audioRoutingGroup_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        receivers: Optional[List[str]] = None,
        routingMode: Optional[str] = None,
        sources: Optional[List[str]] = None,
    ) -> Any:
        """

        Update audioRoutingGroup

        Args:
            call_id (string): call-id
            audioRoutingGroup_id (string): audioRoutingGroup-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            receivers (array): List of receiving participant ids.
            routingMode (string): routingMode
            sources (array): List of source participant ids.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if audioRoutingGroup_id is None:
            raise ValueError("Missing required parameter 'audioRoutingGroup-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "receivers": receivers,
            "routingMode": routingMode,
            "sources": sources,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/audioRoutingGroups/{audioRoutingGroup_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_audio_routing_group(
        self, call_id: str, audioRoutingGroup_id: str
    ) -> Any:
        """

        Delete audioRoutingGroup

        Args:
            call_id (string): call-id
            audioRoutingGroup_id (string): audioRoutingGroup-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if audioRoutingGroup_id is None:
            raise ValueError("Missing required parameter 'audioRoutingGroup-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/audioRoutingGroups/{audioRoutingGroup_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_audio_routing_groups_count(
        self, call_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            call_id (string): call-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/audioRoutingGroups/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_content_sharing_sessions(
        self,
        call_id: str,
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

        List contentSharingSessions

        Args:
            call_id (string): call-id
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
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/contentSharingSessions"
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

    def create_content_sharing_session(
        self, call_id: str, atodata_type: str, id: Optional[str] = None
    ) -> Any:
        """

        Create new navigation property to contentSharingSessions for communications

        Args:
            call_id (string): call-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"id": id, "@odata.type": atodata_type}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/contentSharingSessions"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_call_content_sharing_session(
        self,
        call_id: str,
        contentSharingSession_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get contentSharingSession

        Args:
            call_id (string): call-id
            contentSharingSession_id (string): contentSharingSession-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if contentSharingSession_id is None:
            raise ValueError("Missing required parameter 'contentSharingSession-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/contentSharingSessions/{contentSharingSession_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_content_sharing_session(
        self,
        call_id: str,
        contentSharingSession_id: str,
        atodata_type: str,
        id: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property contentSharingSessions in communications

        Args:
            call_id (string): call-id
            contentSharingSession_id (string): contentSharingSession-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if contentSharingSession_id is None:
            raise ValueError("Missing required parameter 'contentSharingSession-id'.")
        request_body_data = None
        request_body_data = {"id": id, "@odata.type": atodata_type}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/contentSharingSessions/{contentSharingSession_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_content_sharing_session(
        self, call_id: str, contentSharingSession_id: str
    ) -> Any:
        """

        Delete navigation property contentSharingSessions for communications

        Args:
            call_id (string): call-id
            contentSharingSession_id (string): contentSharingSession-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if contentSharingSession_id is None:
            raise ValueError("Missing required parameter 'contentSharingSession-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/contentSharingSessions/{contentSharingSession_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_call_content_sessions(
        self, call_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            call_id (string): call-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/contentSharingSessions/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def add_large_gallery_view(
        self, call_id: str, clientContext: Optional[str] = None
    ) -> Any:
        """

        Invoke action addLargeGalleryView

        Args:
            call_id (string): call-id
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/addLargeGalleryView"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def answer_call_by_id(
        self,
        call_id: str,
        callbackUri: Optional[str] = None,
        mediaConfig: Optional[dict[str, Any]] = None,
        acceptedModalities: Optional[List[Any]] = None,
        participantCapacity: Optional[float] = None,
        callOptions: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action answer

        Args:
            call_id (string): call-id
            callbackUri (string): callbackUri
            mediaConfig (object): mediaConfig
            acceptedModalities (array): acceptedModalities
            participantCapacity (number): participantCapacity
            callOptions (string): callOptions

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "callbackUri": callbackUri,
            "mediaConfig": mediaConfig,
            "acceptedModalities": acceptedModalities,
            "participantCapacity": participantCapacity,
            "callOptions": callOptions,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/answer"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def cancel_media_processing_by_call_id(
        self, call_id: str, clientContext: Optional[str] = None
    ) -> Any:
        """

        Invoke action cancelMediaProcessing

        Args:
            call_id (string): call-id
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/cancelMediaProcessing"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def change_screen_sharing_role(
        self, call_id: str, role: Optional[str] = None
    ) -> Any:
        """

        Invoke action changeScreenSharingRole

        Args:
            call_id (string): call-id
            role (string): role

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"role": role}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/changeScreenSharingRole"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def keep_call_alive(self, call_id: str) -> Any:
        """

        Invoke action keepAlive

        Args:
            call_id (string): call-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        url = (
            f"{self.main_app_client.base_url}/communications/calls/{call_id}/keepAlive"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def communications_calls_call_mute(
        self, call_id: str, clientContext: Optional[str] = None
    ) -> Any:
        """

        Invoke action mute

        Args:
            call_id (string): call-id
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/mute"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def play_call_prompt(
        self,
        call_id: str,
        prompts: Optional[List[dict[str, Any]]] = None,
        clientContext: Optional[str] = None,
    ) -> Any:
        """

        Invoke action playPrompt

        Args:
            call_id (string): call-id
            prompts (array): prompts
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"prompts": prompts, "clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = (
            f"{self.main_app_client.base_url}/communications/calls/{call_id}/playPrompt"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def record_call_response(
        self,
        call_id: str,
        prompts: Optional[List[dict[str, Any]]] = None,
        bargeInAllowed: Optional[bool] = None,
        initialSilenceTimeoutInSeconds: Optional[float] = None,
        maxSilenceTimeoutInSeconds: Optional[float] = None,
        maxRecordDurationInSeconds: Optional[float] = None,
        playBeep: Optional[bool] = None,
        stopTones: Optional[List[str]] = None,
        clientContext: Optional[str] = None,
    ) -> Any:
        """

        Invoke action recordResponse

        Args:
            call_id (string): call-id
            prompts (array): prompts
            bargeInAllowed (boolean): bargeInAllowed
            initialSilenceTimeoutInSeconds (number): initialSilenceTimeoutInSeconds
            maxSilenceTimeoutInSeconds (number): maxSilenceTimeoutInSeconds
            maxRecordDurationInSeconds (number): maxRecordDurationInSeconds
            playBeep (boolean): playBeep
            stopTones (array): stopTones
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "prompts": prompts,
            "bargeInAllowed": bargeInAllowed,
            "initialSilenceTimeoutInSeconds": initialSilenceTimeoutInSeconds,
            "maxSilenceTimeoutInSeconds": maxSilenceTimeoutInSeconds,
            "maxRecordDurationInSeconds": maxRecordDurationInSeconds,
            "playBeep": playBeep,
            "stopTones": stopTones,
            "clientContext": clientContext,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/recordResponse"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def redirect_call_by_id(
        self,
        call_id: str,
        targets: Optional[List[dict[str, Any]]] = None,
        timeout: Optional[float] = None,
        callbackUri: Optional[str] = None,
    ) -> Any:
        """

        Invoke action redirect

        Args:
            call_id (string): call-id
            targets (array): targets
            timeout (number): timeout
            callbackUri (string): callbackUri

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "targets": targets,
            "timeout": timeout,
            "callbackUri": callbackUri,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/redirect"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def reject_call_by_id(
        self,
        call_id: str,
        reason: Optional[Any] = None,
        callbackUri: Optional[str] = None,
    ) -> Any:
        """

        Invoke action reject

        Args:
            call_id (string): call-id
            reason (string): reason
            callbackUri (string): callbackUri

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"reason": reason, "callbackUri": callbackUri}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/reject"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def send_dtmf_tones_to_call(
        self,
        call_id: str,
        tones: Optional[List[str]] = None,
        delayBetweenTonesMs: Optional[float] = None,
        clientContext: Optional[str] = None,
    ) -> Any:
        """

        Invoke action sendDtmfTones

        Args:
            call_id (string): call-id
            tones (array): tones
            delayBetweenTonesMs (number): delayBetweenTonesMs
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "tones": tones,
            "delayBetweenTonesMs": delayBetweenTonesMs,
            "clientContext": clientContext,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/sendDtmfTones"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def subscribe_to_call_tone(
        self, call_id: str, clientContext: Optional[str] = None
    ) -> Any:
        """

        Invoke action subscribeToTone

        Args:
            call_id (string): call-id
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/subscribeToTone"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def transfer_call_by_id(
        self,
        call_id: str,
        transferTarget: Optional[dict[str, Any]] = None,
        transferee: Optional[Any] = None,
    ) -> Any:
        """

        Invoke action transfer

        Args:
            call_id (string): call-id
            transferTarget (object): transferTarget
            transferee (string): transferee

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"transferTarget": transferTarget, "transferee": transferee}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/transfer"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def unmute_call(self, call_id: str, clientContext: Optional[str] = None) -> Any:
        """

        Invoke action unmute

        Args:
            call_id (string): call-id
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/unmute"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def update_call_recording_status(
        self,
        call_id: str,
        status: Optional[str] = None,
        clientContext: Optional[str] = None,
    ) -> Any:
        """

        Invoke action updateRecordingStatus

        Args:
            call_id (string): call-id
            status (string): status
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {"status": status, "clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/updateRecordingStatus"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_call_operations(
        self,
        call_id: str,
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

        Get addLargeGalleryViewOperation

        Args:
            call_id (string): call-id
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
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = (
            f"{self.main_app_client.base_url}/communications/calls/{call_id}/operations"
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

    def create_call_operation(
        self,
        call_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        clientContext: Optional[str] = None,
        resultInfo: Optional[Any] = None,
        status: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to operations for communications

        Args:
            call_id (string): call-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            clientContext (string): Unique Client Context string. Max limit is 256 chars.
            resultInfo (string): The result information. Read-only.
            status (string): status

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "clientContext": clientContext,
            "resultInfo": resultInfo,
            "status": status,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = (
            f"{self.main_app_client.base_url}/communications/calls/{call_id}/operations"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_comms_operation_details(
        self,
        call_id: str,
        commsOperation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get addLargeGalleryViewOperation

        Args:
            call_id (string): call-id
            commsOperation_id (string): commsOperation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if commsOperation_id is None:
            raise ValueError("Missing required parameter 'commsOperation-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/operations/{commsOperation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_call_operation(
        self,
        call_id: str,
        commsOperation_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        clientContext: Optional[str] = None,
        resultInfo: Optional[Any] = None,
        status: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property operations in communications

        Args:
            call_id (string): call-id
            commsOperation_id (string): commsOperation-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            clientContext (string): Unique Client Context string. Max limit is 256 chars.
            resultInfo (string): The result information. Read-only.
            status (string): status

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if commsOperation_id is None:
            raise ValueError("Missing required parameter 'commsOperation-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "clientContext": clientContext,
            "resultInfo": resultInfo,
            "status": status,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/operations/{commsOperation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_comms_operation(self, call_id: str, commsOperation_id: str) -> Any:
        """

        Delete navigation property operations for communications

        Args:
            call_id (string): call-id
            commsOperation_id (string): commsOperation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if commsOperation_id is None:
            raise ValueError("Missing required parameter 'commsOperation-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/operations/{commsOperation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_call_operations(
        self, call_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            call_id (string): call-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/operations/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_call_participants(
        self,
        call_id: str,
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

        List participants

        Args:
            call_id (string): call-id
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
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants"
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

    def add_call_participant(
        self,
        call_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        info: Optional[dict[str, Any]] = None,
        isInLobby: Optional[bool] = None,
        isMuted: Optional[bool] = None,
        mediaStreams: Optional[List[dict[str, Any]]] = None,
        metadata: Optional[str] = None,
        recordingInfo: Optional[Any] = None,
        removedState: Optional[Any] = None,
        restrictedExperience: Optional[Any] = None,
        rosterSequenceNumber: Optional[float] = None,
    ) -> Any:
        """

        Create new navigation property to participants for communications

        Args:
            call_id (string): call-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            info (object): info
            isInLobby (boolean): true if the participant is in lobby.
            isMuted (boolean): true if the participant is muted (client or server muted).
            mediaStreams (array): The list of media streams.
            metadata (string): A blob of data provided by the participant in the roster.
            recordingInfo (string): Information about whether the participant has recording capability.
            removedState (string): Indicates the reason why the participant was removed from the roster.
            restrictedExperience (string): Indicates the reason or reasons media content from this participant is restricted.
            rosterSequenceNumber (number): Indicates the roster sequence number in which the participant was last updated.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "info": info,
            "isInLobby": isInLobby,
            "isMuted": isMuted,
            "mediaStreams": mediaStreams,
            "metadata": metadata,
            "recordingInfo": recordingInfo,
            "removedState": removedState,
            "restrictedExperience": restrictedExperience,
            "rosterSequenceNumber": rosterSequenceNumber,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_call_participant(
        self,
        call_id: str,
        participant_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get participant

        Args:
            call_id (string): call-id
            participant_id (string): participant-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants/{participant_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_participant(
        self,
        call_id: str,
        participant_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        info: Optional[dict[str, Any]] = None,
        isInLobby: Optional[bool] = None,
        isMuted: Optional[bool] = None,
        mediaStreams: Optional[List[dict[str, Any]]] = None,
        metadata: Optional[str] = None,
        recordingInfo: Optional[Any] = None,
        removedState: Optional[Any] = None,
        restrictedExperience: Optional[Any] = None,
        rosterSequenceNumber: Optional[float] = None,
    ) -> Any:
        """

        Update the navigation property participants in communications

        Args:
            call_id (string): call-id
            participant_id (string): participant-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            info (object): info
            isInLobby (boolean): true if the participant is in lobby.
            isMuted (boolean): true if the participant is muted (client or server muted).
            mediaStreams (array): The list of media streams.
            metadata (string): A blob of data provided by the participant in the roster.
            recordingInfo (string): Information about whether the participant has recording capability.
            removedState (string): Indicates the reason why the participant was removed from the roster.
            restrictedExperience (string): Indicates the reason or reasons media content from this participant is restricted.
            rosterSequenceNumber (number): Indicates the roster sequence number in which the participant was last updated.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "info": info,
            "isInLobby": isInLobby,
            "isMuted": isMuted,
            "mediaStreams": mediaStreams,
            "metadata": metadata,
            "recordingInfo": recordingInfo,
            "removedState": removedState,
            "restrictedExperience": restrictedExperience,
            "rosterSequenceNumber": rosterSequenceNumber,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants/{participant_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_participant_from_call(self, call_id: str, participant_id: str) -> Any:
        """

        Delete participant

        Args:
            call_id (string): call-id
            participant_id (string): participant-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants/{participant_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def mute_participant(
        self, call_id: str, participant_id: str, clientContext: Optional[str] = None
    ) -> Any:
        """

        Invoke action mute

        Args:
            call_id (string): call-id
            participant_id (string): participant-id
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        request_body_data = None
        request_body_data = {"clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants/{participant_id}/mute"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def start_hold_music_for_participant(
        self,
        call_id: str,
        participant_id: str,
        customPrompt: Optional[Any] = None,
        clientContext: Optional[str] = None,
    ) -> Any:
        """

        Invoke action startHoldMusic

        Args:
            call_id (string): call-id
            participant_id (string): participant-id
            customPrompt (string): customPrompt
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        request_body_data = None
        request_body_data = {
            "customPrompt": customPrompt,
            "clientContext": clientContext,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants/{participant_id}/startHoldMusic"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def stop_hold_music_for_participant(
        self, call_id: str, participant_id: str, clientContext: Optional[str] = None
    ) -> Any:
        """

        Invoke action stopHoldMusic

        Args:
            call_id (string): call-id
            participant_id (string): participant-id
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        if participant_id is None:
            raise ValueError("Missing required parameter 'participant-id'.")
        request_body_data = None
        request_body_data = {"clientContext": clientContext}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants/{participant_id}/stopHoldMusic"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_call_participants_count(
        self, call_id: str, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Any:
        """

        Get the number of the resource

        Args:
            call_id (string): call-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def invite_call_participant(
        self,
        call_id: str,
        participants: Optional[List[dict[str, Any]]] = None,
        clientContext: Optional[str] = None,
    ) -> Any:
        """

        Invoke action invite

        Args:
            call_id (string): call-id
            participants (array): participants
            clientContext (string): clientContext

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        if call_id is None:
            raise ValueError("Missing required parameter 'call-id'.")
        request_body_data = None
        request_body_data = {
            "participants": participants,
            "clientContext": clientContext,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/{call_id}/participants/invite"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_calls_count(
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
            communications.call
        """
        url = f"{self.main_app_client.base_url}/communications/calls/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def log_teleconference_device_quality(
        self, quality: Optional[dict[str, Any]] = None
    ) -> Any:
        """

        Invoke action logTeleconferenceDeviceQuality

        Args:
            quality (object): quality

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.call
        """
        request_body_data = None
        request_body_data = {"quality": quality}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/calls/logTeleconferenceDeviceQuality"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_presences_by_user(self, ids: Optional[List[str]] = None) -> dict[str, Any]:
        """

        Invoke action getPresencesByUserId

        Args:
            ids (array): ids

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.cloudCommunications.Actions
        """
        request_body_data = None
        request_body_data = {"ids": ids}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/getPresencesByUserId"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_online_meetings(
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

        Get onlineMeeting

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
            communications.onlineMeeting
        """
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings"
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

    def create_online_meeting(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        allowAttendeeToEnableCamera: Optional[bool] = None,
        allowAttendeeToEnableMic: Optional[bool] = None,
        allowBreakoutRooms: Optional[bool] = None,
        allowedLobbyAdmitters: Optional[Any] = None,
        allowedPresenters: Optional[Any] = None,
        allowLiveShare: Optional[Any] = None,
        allowMeetingChat: Optional[Any] = None,
        allowParticipantsToChangeName: Optional[bool] = None,
        allowPowerPointSharing: Optional[bool] = None,
        allowRecording: Optional[bool] = None,
        allowTeamworkReactions: Optional[bool] = None,
        allowTranscription: Optional[bool] = None,
        allowWhiteboard: Optional[bool] = None,
        audioConferencing: Optional[Any] = None,
        chatInfo: Optional[Any] = None,
        chatRestrictions: Optional[Any] = None,
        isEntryExitAnnounced: Optional[bool] = None,
        joinInformation: Optional[Any] = None,
        joinMeetingIdSettings: Optional[Any] = None,
        joinWebUrl: Optional[str] = None,
        lobbyBypassSettings: Optional[Any] = None,
        recordAutomatically: Optional[bool] = None,
        shareMeetingChatHistoryDefault: Optional[Any] = None,
        subject: Optional[str] = None,
        videoTeleconferenceId: Optional[str] = None,
        watermarkProtection: Optional[Any] = None,
        attendanceReports: Optional[List[Any]] = None,
        attendeeReport: Optional[str] = None,
        broadcastSettings: Optional[Any] = None,
        creationDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
        externalId: Optional[str] = None,
        isBroadcast: Optional[bool] = None,
        meetingTemplateId: Optional[str] = None,
        participants: Optional[Any] = None,
        startDateTime: Optional[str] = None,
        recordings: Optional[List[Any]] = None,
        transcripts: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to onlineMeetings for communications

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            allowAttendeeToEnableCamera (boolean): Indicates whether attendees can turn on their camera.
            allowAttendeeToEnableMic (boolean): Indicates whether attendees can turn on their microphone.
            allowBreakoutRooms (boolean): Indicates whether breakout rooms are enabled for the meeting.
            allowedLobbyAdmitters (string): Specifies the users who can admit from the lobby. Possible values are: organizerAndCoOrganizersAndPresenters, organizerAndCoOrganizers, unknownFutureValue.
            allowedPresenters (string): Specifies who can be a presenter in a meeting.
            allowLiveShare (string): Indicates whether live share is enabled for the meeting. Possible values are: enabled, disabled, unknownFutureValue.
            allowMeetingChat (string): Specifies the mode of the meeting chat.
            allowParticipantsToChangeName (boolean): Specifies if participants are allowed to rename themselves in an instance of the meeting.
            allowPowerPointSharing (boolean): Indicates whether PowerPoint live is enabled for the meeting.
            allowRecording (boolean): Indicates whether recording is enabled for the meeting.
            allowTeamworkReactions (boolean): Indicates if Teams reactions are enabled for the meeting.
            allowTranscription (boolean): Indicates whether transcription is enabled for the meeting.
            allowWhiteboard (boolean): Indicates whether whiteboard is enabled for the meeting.
            audioConferencing (string): The phone access (dial-in) information for an online meeting. Read-only.
            chatInfo (string): The chat information associated with this online meeting.
            chatRestrictions (string): Specifies the configuration settings for meeting chat restrictions.
            isEntryExitAnnounced (boolean): Indicates whether to announce when callers join or leave.
            joinInformation (string): The join information in the language and locale variant specified in 'Accept-Language' request HTTP header. Read-only.
            joinMeetingIdSettings (string): Specifies the joinMeetingId, the meeting passcode, and the requirement for the passcode. Once an onlineMeeting is created, the joinMeetingIdSettings can't be modified. To make any changes to this property, you must cancel this meeting and create a new one.
            joinWebUrl (string): The join URL of the online meeting. Read-only.
            lobbyBypassSettings (string): Specifies which participants can bypass the meeting lobby.
            recordAutomatically (boolean): Indicates whether to record the meeting automatically.
            shareMeetingChatHistoryDefault (string): Specifies whether meeting chat history is shared with participants.  Possible values are: all, none, unknownFutureValue.
            subject (string): The subject of the online meeting.
            videoTeleconferenceId (string): The video teleconferencing ID. Read-only.
            watermarkProtection (string): Specifies whether the client application should apply a watermark to a content type.
            attendanceReports (array): The attendance reports of an online meeting. Read-only.
            attendeeReport (string): The content stream of the attendee report of a Microsoft Teams live event. Read-only.
            broadcastSettings (string): Settings related to a live event.
            creationDateTime (string): The meeting creation time in UTC. Read-only.
            endDateTime (string): The meeting end time in UTC. Required when you create an online meeting.
            externalId (string): externalId
            isBroadcast (boolean): Indicates whether this meeting is a Teams live event.
            meetingTemplateId (string): The ID of the meeting template.
            participants (string): The participants associated with the online meeting, including the organizer and the attendees.
            startDateTime (string): The meeting start time in UTC.
            recordings (array): The recordings of an online meeting. Read-only.
            transcripts (array): The transcripts of an online meeting. Read-only.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "allowAttendeeToEnableCamera": allowAttendeeToEnableCamera,
            "allowAttendeeToEnableMic": allowAttendeeToEnableMic,
            "allowBreakoutRooms": allowBreakoutRooms,
            "allowedLobbyAdmitters": allowedLobbyAdmitters,
            "allowedPresenters": allowedPresenters,
            "allowLiveShare": allowLiveShare,
            "allowMeetingChat": allowMeetingChat,
            "allowParticipantsToChangeName": allowParticipantsToChangeName,
            "allowPowerPointSharing": allowPowerPointSharing,
            "allowRecording": allowRecording,
            "allowTeamworkReactions": allowTeamworkReactions,
            "allowTranscription": allowTranscription,
            "allowWhiteboard": allowWhiteboard,
            "audioConferencing": audioConferencing,
            "chatInfo": chatInfo,
            "chatRestrictions": chatRestrictions,
            "isEntryExitAnnounced": isEntryExitAnnounced,
            "joinInformation": joinInformation,
            "joinMeetingIdSettings": joinMeetingIdSettings,
            "joinWebUrl": joinWebUrl,
            "lobbyBypassSettings": lobbyBypassSettings,
            "recordAutomatically": recordAutomatically,
            "shareMeetingChatHistoryDefault": shareMeetingChatHistoryDefault,
            "subject": subject,
            "videoTeleconferenceId": videoTeleconferenceId,
            "watermarkProtection": watermarkProtection,
            "attendanceReports": attendanceReports,
            "attendeeReport": attendeeReport,
            "broadcastSettings": broadcastSettings,
            "creationDateTime": creationDateTime,
            "endDateTime": endDateTime,
            "externalId": externalId,
            "isBroadcast": isBroadcast,
            "meetingTemplateId": meetingTemplateId,
            "participants": participants,
            "startDateTime": startDateTime,
            "recordings": recordings,
            "transcripts": transcripts,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_online_meeting_details(
        self,
        onlineMeeting_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get onlineMeetings from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_online_meeting(
        self,
        onlineMeeting_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        allowAttendeeToEnableCamera: Optional[bool] = None,
        allowAttendeeToEnableMic: Optional[bool] = None,
        allowBreakoutRooms: Optional[bool] = None,
        allowedLobbyAdmitters: Optional[Any] = None,
        allowedPresenters: Optional[Any] = None,
        allowLiveShare: Optional[Any] = None,
        allowMeetingChat: Optional[Any] = None,
        allowParticipantsToChangeName: Optional[bool] = None,
        allowPowerPointSharing: Optional[bool] = None,
        allowRecording: Optional[bool] = None,
        allowTeamworkReactions: Optional[bool] = None,
        allowTranscription: Optional[bool] = None,
        allowWhiteboard: Optional[bool] = None,
        audioConferencing: Optional[Any] = None,
        chatInfo: Optional[Any] = None,
        chatRestrictions: Optional[Any] = None,
        isEntryExitAnnounced: Optional[bool] = None,
        joinInformation: Optional[Any] = None,
        joinMeetingIdSettings: Optional[Any] = None,
        joinWebUrl: Optional[str] = None,
        lobbyBypassSettings: Optional[Any] = None,
        recordAutomatically: Optional[bool] = None,
        shareMeetingChatHistoryDefault: Optional[Any] = None,
        subject: Optional[str] = None,
        videoTeleconferenceId: Optional[str] = None,
        watermarkProtection: Optional[Any] = None,
        attendanceReports: Optional[List[Any]] = None,
        attendeeReport: Optional[str] = None,
        broadcastSettings: Optional[Any] = None,
        creationDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
        externalId: Optional[str] = None,
        isBroadcast: Optional[bool] = None,
        meetingTemplateId: Optional[str] = None,
        participants: Optional[Any] = None,
        startDateTime: Optional[str] = None,
        recordings: Optional[List[Any]] = None,
        transcripts: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property onlineMeetings in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            allowAttendeeToEnableCamera (boolean): Indicates whether attendees can turn on their camera.
            allowAttendeeToEnableMic (boolean): Indicates whether attendees can turn on their microphone.
            allowBreakoutRooms (boolean): Indicates whether breakout rooms are enabled for the meeting.
            allowedLobbyAdmitters (string): Specifies the users who can admit from the lobby. Possible values are: organizerAndCoOrganizersAndPresenters, organizerAndCoOrganizers, unknownFutureValue.
            allowedPresenters (string): Specifies who can be a presenter in a meeting.
            allowLiveShare (string): Indicates whether live share is enabled for the meeting. Possible values are: enabled, disabled, unknownFutureValue.
            allowMeetingChat (string): Specifies the mode of the meeting chat.
            allowParticipantsToChangeName (boolean): Specifies if participants are allowed to rename themselves in an instance of the meeting.
            allowPowerPointSharing (boolean): Indicates whether PowerPoint live is enabled for the meeting.
            allowRecording (boolean): Indicates whether recording is enabled for the meeting.
            allowTeamworkReactions (boolean): Indicates if Teams reactions are enabled for the meeting.
            allowTranscription (boolean): Indicates whether transcription is enabled for the meeting.
            allowWhiteboard (boolean): Indicates whether whiteboard is enabled for the meeting.
            audioConferencing (string): The phone access (dial-in) information for an online meeting. Read-only.
            chatInfo (string): The chat information associated with this online meeting.
            chatRestrictions (string): Specifies the configuration settings for meeting chat restrictions.
            isEntryExitAnnounced (boolean): Indicates whether to announce when callers join or leave.
            joinInformation (string): The join information in the language and locale variant specified in 'Accept-Language' request HTTP header. Read-only.
            joinMeetingIdSettings (string): Specifies the joinMeetingId, the meeting passcode, and the requirement for the passcode. Once an onlineMeeting is created, the joinMeetingIdSettings can't be modified. To make any changes to this property, you must cancel this meeting and create a new one.
            joinWebUrl (string): The join URL of the online meeting. Read-only.
            lobbyBypassSettings (string): Specifies which participants can bypass the meeting lobby.
            recordAutomatically (boolean): Indicates whether to record the meeting automatically.
            shareMeetingChatHistoryDefault (string): Specifies whether meeting chat history is shared with participants.  Possible values are: all, none, unknownFutureValue.
            subject (string): The subject of the online meeting.
            videoTeleconferenceId (string): The video teleconferencing ID. Read-only.
            watermarkProtection (string): Specifies whether the client application should apply a watermark to a content type.
            attendanceReports (array): The attendance reports of an online meeting. Read-only.
            attendeeReport (string): The content stream of the attendee report of a Microsoft Teams live event. Read-only.
            broadcastSettings (string): Settings related to a live event.
            creationDateTime (string): The meeting creation time in UTC. Read-only.
            endDateTime (string): The meeting end time in UTC. Required when you create an online meeting.
            externalId (string): externalId
            isBroadcast (boolean): Indicates whether this meeting is a Teams live event.
            meetingTemplateId (string): The ID of the meeting template.
            participants (string): The participants associated with the online meeting, including the organizer and the attendees.
            startDateTime (string): The meeting start time in UTC.
            recordings (array): The recordings of an online meeting. Read-only.
            transcripts (array): The transcripts of an online meeting. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "allowAttendeeToEnableCamera": allowAttendeeToEnableCamera,
            "allowAttendeeToEnableMic": allowAttendeeToEnableMic,
            "allowBreakoutRooms": allowBreakoutRooms,
            "allowedLobbyAdmitters": allowedLobbyAdmitters,
            "allowedPresenters": allowedPresenters,
            "allowLiveShare": allowLiveShare,
            "allowMeetingChat": allowMeetingChat,
            "allowParticipantsToChangeName": allowParticipantsToChangeName,
            "allowPowerPointSharing": allowPowerPointSharing,
            "allowRecording": allowRecording,
            "allowTeamworkReactions": allowTeamworkReactions,
            "allowTranscription": allowTranscription,
            "allowWhiteboard": allowWhiteboard,
            "audioConferencing": audioConferencing,
            "chatInfo": chatInfo,
            "chatRestrictions": chatRestrictions,
            "isEntryExitAnnounced": isEntryExitAnnounced,
            "joinInformation": joinInformation,
            "joinMeetingIdSettings": joinMeetingIdSettings,
            "joinWebUrl": joinWebUrl,
            "lobbyBypassSettings": lobbyBypassSettings,
            "recordAutomatically": recordAutomatically,
            "shareMeetingChatHistoryDefault": shareMeetingChatHistoryDefault,
            "subject": subject,
            "videoTeleconferenceId": videoTeleconferenceId,
            "watermarkProtection": watermarkProtection,
            "attendanceReports": attendanceReports,
            "attendeeReport": attendeeReport,
            "broadcastSettings": broadcastSettings,
            "creationDateTime": creationDateTime,
            "endDateTime": endDateTime,
            "externalId": externalId,
            "isBroadcast": isBroadcast,
            "meetingTemplateId": meetingTemplateId,
            "participants": participants,
            "startDateTime": startDateTime,
            "recordings": recordings,
            "transcripts": transcripts,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_online_meeting_by_id(self, onlineMeeting_id: str) -> Any:
        """

        Delete navigation property onlineMeetings for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_attendance_report(
        self,
        onlineMeeting_id: str,
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

        Get attendanceReports from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
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
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports"
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

    def create_meeting_attendance_report(
        self,
        onlineMeeting_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        externalEventInformation: Optional[List[dict[str, Any]]] = None,
        meetingEndDateTime: Optional[str] = None,
        meetingStartDateTime: Optional[str] = None,
        totalParticipantCount: Optional[float] = None,
        attendanceRecords: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create new navigation property to attendanceReports for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            externalEventInformation (array): The external information of a virtual event. Returned only for event organizers or coorganizers. Read-only.
            meetingEndDateTime (string): UTC time when the meeting ended. Read-only.
            meetingStartDateTime (string): UTC time when the meeting started. Read-only.
            totalParticipantCount (number): Total number of participants. Read-only.
            attendanceRecords (array): List of attendance records of an attendance report. Read-only.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "externalEventInformation": externalEventInformation,
            "meetingEndDateTime": meetingEndDateTime,
            "meetingStartDateTime": meetingStartDateTime,
            "totalParticipantCount": totalParticipantCount,
            "attendanceRecords": attendanceRecords,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_attendance_report_details(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get attendanceReports from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_attendance_report(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        externalEventInformation: Optional[List[dict[str, Any]]] = None,
        meetingEndDateTime: Optional[str] = None,
        meetingStartDateTime: Optional[str] = None,
        totalParticipantCount: Optional[float] = None,
        attendanceRecords: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update the navigation property attendanceReports in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            externalEventInformation (array): The external information of a virtual event. Returned only for event organizers or coorganizers. Read-only.
            meetingEndDateTime (string): UTC time when the meeting ended. Read-only.
            meetingStartDateTime (string): UTC time when the meeting started. Read-only.
            totalParticipantCount (number): Total number of participants. Read-only.
            attendanceRecords (array): List of attendance records of an attendance report. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "externalEventInformation": externalEventInformation,
            "meetingEndDateTime": meetingEndDateTime,
            "meetingStartDateTime": meetingStartDateTime,
            "totalParticipantCount": totalParticipantCount,
            "attendanceRecords": attendanceRecords,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_meeting_attendance_report(
        self, onlineMeeting_id: str, meetingAttendanceReport_id: str
    ) -> Any:
        """

        Delete navigation property attendanceReports for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_comm_meeting_att_records(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
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

        Get attendanceRecords from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
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
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords"
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

    def add_attendance_record(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attendanceIntervals: Optional[List[dict[str, Any]]] = None,
        emailAddress: Optional[str] = None,
        externalRegistrationInformation: Optional[Any] = None,
        identity: Optional[Any] = None,
        registrationId: Optional[str] = None,
        role: Optional[str] = None,
        totalAttendanceInSeconds: Optional[float] = None,
    ) -> Any:
        """

        Create new navigation property to attendanceRecords for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attendanceIntervals (array): List of time periods between joining and leaving a meeting.
            emailAddress (string): Email address of the user associated with this attendance record.
            externalRegistrationInformation (string): The external information for a virtualEventRegistration.
            identity (string): The identity of the user associated with this attendance record. The specific type is one of the following derived types of identity, depending on the user type: communicationsUserIdentity, azureCommunicationServicesUserIdentity.
            registrationId (string): Unique identifier of a virtualEventRegistration that is available to all participants registered for the virtualEventWebinar.
            role (string): Role of the attendee. Possible values are: None, Attendee, Presenter, and Organizer.
            totalAttendanceInSeconds (number): Total duration of the attendances in seconds.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attendanceIntervals": attendanceIntervals,
            "emailAddress": emailAddress,
            "externalRegistrationInformation": externalRegistrationInformation,
            "identity": identity,
            "registrationId": registrationId,
            "role": role,
            "totalAttendanceInSeconds": totalAttendanceInSeconds,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_attendance_record_details(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        attendanceRecord_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get attendanceRecords from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
            attendanceRecord_id (string): attendanceRecord-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        if attendanceRecord_id is None:
            raise ValueError("Missing required parameter 'attendanceRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords/{attendanceRecord_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_attendance_record_by_id(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        attendanceRecord_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        attendanceIntervals: Optional[List[dict[str, Any]]] = None,
        emailAddress: Optional[str] = None,
        externalRegistrationInformation: Optional[Any] = None,
        identity: Optional[Any] = None,
        registrationId: Optional[str] = None,
        role: Optional[str] = None,
        totalAttendanceInSeconds: Optional[float] = None,
    ) -> Any:
        """

        Update the navigation property attendanceRecords in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
            attendanceRecord_id (string): attendanceRecord-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            attendanceIntervals (array): List of time periods between joining and leaving a meeting.
            emailAddress (string): Email address of the user associated with this attendance record.
            externalRegistrationInformation (string): The external information for a virtualEventRegistration.
            identity (string): The identity of the user associated with this attendance record. The specific type is one of the following derived types of identity, depending on the user type: communicationsUserIdentity, azureCommunicationServicesUserIdentity.
            registrationId (string): Unique identifier of a virtualEventRegistration that is available to all participants registered for the virtualEventWebinar.
            role (string): Role of the attendee. Possible values are: None, Attendee, Presenter, and Organizer.
            totalAttendanceInSeconds (number): Total duration of the attendances in seconds.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        if attendanceRecord_id is None:
            raise ValueError("Missing required parameter 'attendanceRecord-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "attendanceIntervals": attendanceIntervals,
            "emailAddress": emailAddress,
            "externalRegistrationInformation": externalRegistrationInformation,
            "identity": identity,
            "registrationId": registrationId,
            "role": role,
            "totalAttendanceInSeconds": totalAttendanceInSeconds,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords/{attendanceRecord_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def deletecomm_attendance_record(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        attendanceRecord_id: str,
    ) -> Any:
        """

        Delete navigation property attendanceRecords for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
            attendanceRecord_id (string): attendanceRecord-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        if attendanceRecord_id is None:
            raise ValueError("Missing required parameter 'attendanceRecord-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords/{attendanceRecord_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_attendance_records_count(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_meeting_attendance_count(
        self,
        onlineMeeting_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendanceReports/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_attendee_report_by_meeting_id(self, onlineMeeting_id: str) -> Any:
        """

        Get attendeeReport for the navigation property onlineMeetings from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendeeReport"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def upload_attendee_report_stream(
        self, onlineMeeting_id: str, body_content: bytes
    ) -> Any:
        """

        Update attendeeReport for the navigation property onlineMeetings in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendeeReport"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_comm_online_mtg_att_report(self, onlineMeeting_id: str) -> Any:
        """

        Delete attendeeReport for the navigation property onlineMeetings in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/attendeeReport"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_virtual_join_url(self, onlineMeeting_id: str) -> dict[str, Any]:
        """

        Invoke function getVirtualAppointmentJoinWebUrl

        Args:
            onlineMeeting_id (string): onlineMeeting-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/getVirtualAppointmentJoinWebUrl()"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def send_virtual_meeting_reminder_sms(
        self,
        onlineMeeting_id: str,
        remindBeforeTimeInMinutesType: Optional[Any] = None,
        attendees: Optional[List[dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action sendVirtualAppointmentReminderSms

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            remindBeforeTimeInMinutesType (string): remindBeforeTimeInMinutesType
            attendees (array): attendees

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = {
            "remindBeforeTimeInMinutesType": remindBeforeTimeInMinutesType,
            "attendees": attendees,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/sendVirtualAppointmentReminderSms"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def send_online_meeting_sms(
        self,
        onlineMeeting_id: str,
        messageType: Optional[Any] = None,
        attendees: Optional[List[dict[str, Any]]] = None,
    ) -> Any:
        """

        Invoke action sendVirtualAppointmentSms

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            messageType (string): messageType
            attendees (array): attendees

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = {"messageType": messageType, "attendees": attendees}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/sendVirtualAppointmentSms"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_meeting_recordings(
        self,
        onlineMeeting_id: str,
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

        Get recordings from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
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
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings"
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

    def start_recording(
        self,
        onlineMeeting_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callId: Optional[str] = None,
        content: Optional[str] = None,
        contentCorrelationId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
        meetingId: Optional[str] = None,
        meetingOrganizer: Optional[Any] = None,
        recordingContentUrl: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to recordings for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callId (string): The unique identifier for the call that is related to this recording. Read-only.
            content (string): The content of the recording. Read-only.
            contentCorrelationId (string): The unique identifier that links the transcript with its corresponding recording. Read-only.
            createdDateTime (string): Date and time at which the recording was created. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
            endDateTime (string): Date and time at which the recording ends. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
            meetingId (string): The unique identifier of the onlineMeeting related to this recording. Read-only.
            meetingOrganizer (string): The identity information of the organizer of the onlineMeeting related to this recording. Read-only.
            recordingContentUrl (string): The URL that can be used to access the content of the recording. Read-only.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callId": callId,
            "content": content,
            "contentCorrelationId": contentCorrelationId,
            "createdDateTime": createdDateTime,
            "endDateTime": endDateTime,
            "meetingId": meetingId,
            "meetingOrganizer": meetingOrganizer,
            "recordingContentUrl": recordingContentUrl,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_recording(
        self,
        onlineMeeting_id: str,
        callRecording_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get recordings from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_meeting_recording(
        self,
        onlineMeeting_id: str,
        callRecording_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callId: Optional[str] = None,
        content: Optional[str] = None,
        contentCorrelationId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
        meetingId: Optional[str] = None,
        meetingOrganizer: Optional[Any] = None,
        recordingContentUrl: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property recordings in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callId (string): The unique identifier for the call that is related to this recording. Read-only.
            content (string): The content of the recording. Read-only.
            contentCorrelationId (string): The unique identifier that links the transcript with its corresponding recording. Read-only.
            createdDateTime (string): Date and time at which the recording was created. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
            endDateTime (string): Date and time at which the recording ends. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
            meetingId (string): The unique identifier of the onlineMeeting related to this recording. Read-only.
            meetingOrganizer (string): The identity information of the organizer of the onlineMeeting related to this recording. Read-only.
            recordingContentUrl (string): The URL that can be used to access the content of the recording. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callId": callId,
            "content": content,
            "contentCorrelationId": contentCorrelationId,
            "createdDateTime": createdDateTime,
            "endDateTime": endDateTime,
            "meetingId": meetingId,
            "meetingOrganizer": meetingOrganizer,
            "recordingContentUrl": recordingContentUrl,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_call_recording_by_id(
        self, onlineMeeting_id: str, callRecording_id: str
    ) -> Any:
        """

        Delete navigation property recordings for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_meeting_recording_content(
        self, onlineMeeting_id: str, callRecording_id: str
    ) -> Any:
        """

        Get content for the navigation property recordings from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}/content"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def upload_recording_content(
        self, onlineMeeting_id: str, callRecording_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property recordings in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_call_recording_content_by_id(
        self, onlineMeeting_id: str, callRecording_id: str
    ) -> Any:
        """

        Delete content for the navigation property recordings in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_recordings(
        self,
        onlineMeeting_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_comm_meeting_recordings_delta(
        self,
        onlineMeeting_id: str,
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
            onlineMeeting_id (string): onlineMeeting-id
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
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/recordings/delta()"
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

    def get_online_meeting_transcript(
        self,
        onlineMeeting_id: str,
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

        Get transcripts from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
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
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts"
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

    def create_transcript_comm(
        self,
        onlineMeeting_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callId: Optional[str] = None,
        content: Optional[str] = None,
        contentCorrelationId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
        meetingId: Optional[str] = None,
        meetingOrganizer: Optional[Any] = None,
        metadataContent: Optional[str] = None,
        transcriptContentUrl: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to transcripts for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callId (string): The unique identifier for the call that is related to this transcript. Read-only.
            content (string): The content of the transcript. Read-only.
            contentCorrelationId (string): The unique identifier that links the transcript with its corresponding recording. Read-only.
            createdDateTime (string): Date and time at which the transcript was created. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
            endDateTime (string): Date and time at which the transcription ends. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
            meetingId (string): The unique identifier of the online meeting related to this transcript. Read-only.
            meetingOrganizer (string): The identity information of the organizer of the onlineMeeting related to this transcript. Read-only.
            metadataContent (string): The time-aligned metadata of the utterances in the transcript. Read-only.
            transcriptContentUrl (string): The URL that can be used to access the content of the transcript. Read-only.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callId": callId,
            "content": content,
            "contentCorrelationId": contentCorrelationId,
            "createdDateTime": createdDateTime,
            "endDateTime": endDateTime,
            "meetingId": meetingId,
            "meetingOrganizer": meetingOrganizer,
            "metadataContent": metadataContent,
            "transcriptContentUrl": transcriptContentUrl,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_transcript_data(
        self,
        onlineMeeting_id: str,
        callTranscript_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get transcripts from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_transcript(
        self,
        onlineMeeting_id: str,
        callTranscript_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        callId: Optional[str] = None,
        content: Optional[str] = None,
        contentCorrelationId: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        endDateTime: Optional[str] = None,
        meetingId: Optional[str] = None,
        meetingOrganizer: Optional[Any] = None,
        metadataContent: Optional[str] = None,
        transcriptContentUrl: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property transcripts in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            callId (string): The unique identifier for the call that is related to this transcript. Read-only.
            content (string): The content of the transcript. Read-only.
            contentCorrelationId (string): The unique identifier that links the transcript with its corresponding recording. Read-only.
            createdDateTime (string): Date and time at which the transcript was created. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
            endDateTime (string): Date and time at which the transcription ends. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Read-only.
            meetingId (string): The unique identifier of the online meeting related to this transcript. Read-only.
            meetingOrganizer (string): The identity information of the organizer of the onlineMeeting related to this transcript. Read-only.
            metadataContent (string): The time-aligned metadata of the utterances in the transcript. Read-only.
            transcriptContentUrl (string): The URL that can be used to access the content of the transcript. Read-only.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "callId": callId,
            "content": content,
            "contentCorrelationId": contentCorrelationId,
            "createdDateTime": createdDateTime,
            "endDateTime": endDateTime,
            "meetingId": meetingId,
            "meetingOrganizer": meetingOrganizer,
            "metadataContent": metadataContent,
            "transcriptContentUrl": transcriptContentUrl,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_transcript(self, onlineMeeting_id: str, callTranscript_id: str) -> Any:
        """

        Delete navigation property transcripts for communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_transcript_content_by_id(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Get content for the navigation property transcripts from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/content"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_transcript_content(
        self, onlineMeeting_id: str, callTranscript_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property transcripts in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_transcript_content_by_id(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Delete content for the navigation property transcripts in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_metadata_content(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Get metadataContent for the navigation property transcripts from communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/metadataContent"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_comm_transcript_metadata(
        self, onlineMeeting_id: str, callTranscript_id: str, body_content: bytes
    ) -> Any:
        """

        Update metadataContent for the navigation property transcripts in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/metadataContent"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_metadata_content(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Delete metadataContent for the navigation property transcripts in communications

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/metadataContent"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_online_meeting_transcript(
        self,
        onlineMeeting_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_meeting_transcripts_delta(
        self,
        onlineMeeting_id: str,
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
            onlineMeeting_id (string): onlineMeeting-id
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
            communications.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/{onlineMeeting_id}/transcripts/delta()"
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

    def get_online_meetings_count(
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
            communications.onlineMeeting
        """
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def create_or_get_online_meeting(
        self,
        chatInfo: Optional[Any] = None,
        endDateTime: Optional[str] = None,
        externalId: Optional[str] = None,
        participants: Optional[Any] = None,
        startDateTime: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> Any:
        """

        Invoke action createOrGet

        Args:
            chatInfo (string): chatInfo
            endDateTime (string): endDateTime
            externalId (string): externalId
            participants (string): participants
            startDateTime (string): startDateTime
            subject (string): subject

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.onlineMeeting
        """
        request_body_data = None
        request_body_data = {
            "chatInfo": chatInfo,
            "endDateTime": endDateTime,
            "externalId": externalId,
            "participants": participants,
            "startDateTime": startDateTime,
            "subject": subject,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = (
            f"{self.main_app_client.base_url}/communications/onlineMeetings/createOrGet"
        )
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_recordings_by_organizer(
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

        Invoke function getAllRecordings

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
            communications.onlineMeeting
        """
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/getAllRecordings(meetingOrganizerUserId='@meetingOrganizerUserId',startDateTime=@startDateTime,endDateTime=@endDateTime)"
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

    def get_all_meeting_transcripts(
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

        Invoke function getAllTranscripts

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
            communications.onlineMeeting
        """
        url = f"{self.main_app_client.base_url}/communications/onlineMeetings/getAllTranscripts(meetingOrganizerUserId='@meetingOrganizerUserId',startDateTime=@startDateTime,endDateTime=@endDateTime)"
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

    def communications_list_presences(
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

        Get presence

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
            communications.presence
        """
        url = f"{self.main_app_client.base_url}/communications/presences"
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

    def communications_create_presences(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        activity: Optional[str] = None,
        availability: Optional[str] = None,
        statusMessage: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to presences for communications

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            activity (string): The supplemental information to a user's availability. Possible values are Available, Away, BeRightBack, Busy, DoNotDisturb, InACall, InAConferenceCall, Inactive, InAMeeting, Offline, OffWork, OutOfOffice, PresenceUnknown, Presenting, UrgentInterruptionsOnly.
            availability (string): The base presence information for a user. Possible values are Available, AvailableIdle,  Away, BeRightBack, Busy, BusyIdle, DoNotDisturb, Offline, PresenceUnknown
            statusMessage (string): The presence status message of a user.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "activity": activity,
            "availability": availability,
            "statusMessage": statusMessage,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/presences"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def communications_get_presences(
        self,
        presence_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get presence

        Args:
            presence_id (string): presence-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        if presence_id is None:
            raise ValueError("Missing required parameter 'presence-id'.")
        url = f"{self.main_app_client.base_url}/communications/presences/{presence_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def communications_update_presences(
        self,
        presence_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        activity: Optional[str] = None,
        availability: Optional[str] = None,
        statusMessage: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property presences in communications

        Args:
            presence_id (string): presence-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            activity (string): The supplemental information to a user's availability. Possible values are Available, Away, BeRightBack, Busy, DoNotDisturb, InACall, InAConferenceCall, Inactive, InAMeeting, Offline, OffWork, OutOfOffice, PresenceUnknown, Presenting, UrgentInterruptionsOnly.
            availability (string): The base presence information for a user. Possible values are Available, AvailableIdle,  Away, BeRightBack, Busy, BusyIdle, DoNotDisturb, Offline, PresenceUnknown
            statusMessage (string): The presence status message of a user.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        if presence_id is None:
            raise ValueError("Missing required parameter 'presence-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "activity": activity,
            "availability": availability,
            "statusMessage": statusMessage,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/presences/{presence_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def communications_delete_presences(self, presence_id: str) -> Any:
        """

        Delete navigation property presences for communications

        Args:
            presence_id (string): presence-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        if presence_id is None:
            raise ValueError("Missing required parameter 'presence-id'.")
        url = f"{self.main_app_client.base_url}/communications/presences/{presence_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def clear_presence_by_id(
        self, presence_id: str, sessionId: Optional[str] = None
    ) -> Any:
        """

        Invoke action clearPresence

        Args:
            presence_id (string): presence-id
            sessionId (string): sessionId

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        if presence_id is None:
            raise ValueError("Missing required parameter 'presence-id'.")
        request_body_data = None
        request_body_data = {"sessionId": sessionId}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/presences/{presence_id}/clearPresence"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def clear_user_presence(self, presence_id: str) -> Any:
        """

        Invoke action clearUserPreferredPresence

        Args:
            presence_id (string): presence-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        if presence_id is None:
            raise ValueError("Missing required parameter 'presence-id'.")
        request_body_data = None
        url = f"{self.main_app_client.base_url}/communications/presences/{presence_id}/clearUserPreferredPresence"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def set_presence_by_id(
        self,
        presence_id: str,
        sessionId: Optional[str] = None,
        availability: Optional[str] = None,
        activity: Optional[str] = None,
        expirationDuration: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setPresence

        Args:
            presence_id (string): presence-id
            sessionId (string): sessionId
            availability (string): availability
            activity (string): activity
            expirationDuration (string): expirationDuration

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        if presence_id is None:
            raise ValueError("Missing required parameter 'presence-id'.")
        request_body_data = None
        request_body_data = {
            "sessionId": sessionId,
            "availability": availability,
            "activity": activity,
            "expirationDuration": expirationDuration,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/presences/{presence_id}/setPresence"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def set_presence_status_message(
        self, presence_id: str, statusMessage: Optional[Any] = None
    ) -> Any:
        """

        Invoke action setStatusMessage

        Args:
            presence_id (string): presence-id
            statusMessage (string): statusMessage

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        if presence_id is None:
            raise ValueError("Missing required parameter 'presence-id'.")
        request_body_data = None
        request_body_data = {"statusMessage": statusMessage}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/presences/{presence_id}/setStatusMessage"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def set_preferred_presence(
        self,
        presence_id: str,
        availability: Optional[str] = None,
        activity: Optional[str] = None,
        expirationDuration: Optional[str] = None,
    ) -> Any:
        """

        Invoke action setUserPreferredPresence

        Args:
            presence_id (string): presence-id
            availability (string): availability
            activity (string): activity
            expirationDuration (string): expirationDuration

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            communications.presence
        """
        if presence_id is None:
            raise ValueError("Missing required parameter 'presence-id'.")
        request_body_data = None
        request_body_data = {
            "availability": availability,
            "activity": activity,
            "expirationDuration": expirationDuration,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/communications/presences/{presence_id}/setUserPreferredPresence"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def count_communications_presences(
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
            communications.presence
        """
        url = f"{self.main_app_client.base_url}/communications/presences/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.list_communications,
            self.patch_communication,
            self.communications_list_call_records,
            self.create_call_record,
            self.communications_get_call_records,
            self.update_call_record,
            self.delete_call_record_by_id,
            self.get_call_record_organizer_v,
            self.update_call_record_organizer_v,
            self.delete_call_record_organizer,
            self.get_call_record_participants_v,
            self.add_call_record_participants_v,
            self.get_participant_by_id_v,
            self.update_call_participant_v,
            self.delete_participant_by_id,
            self.get_call_record_participants_count,
            self.get_call_record_sessions,
            self.create_call_record_session,
            self.get_call_session_by_id,
            self.update_call_session,
            self.delete_call_session,
            self.get_call_segments,
            self.create_segment,
            self.get_call_segment,
            self.update_call_record_segment,
            self.delete_segment_by_id,
            self.count_call_segments,
            self.count_call_record_sessions,
            self.get_call_records_count,
            self.get_direct_routing_calls,
            self.get_pstn_calls,
            self.communications_list_calls,
            self.communications_create_calls,
            self.communications_get_calls,
            self.communications_update_calls,
            self.communications_delete_calls,
            self.get_audio_routing_groups,
            self.add_audio_routing_group,
            self.get_audio_routing_group_details,
            self.update_call_audio_routing_group,
            self.delete_audio_routing_group,
            self.get_audio_routing_groups_count,
            self.get_content_sharing_sessions,
            self.create_content_sharing_session,
            self.get_call_content_sharing_session,
            self.update_content_sharing_session,
            self.delete_content_sharing_session,
            self.count_call_content_sessions,
            self.add_large_gallery_view,
            self.answer_call_by_id,
            self.cancel_media_processing_by_call_id,
            self.change_screen_sharing_role,
            self.keep_call_alive,
            self.communications_calls_call_mute,
            self.play_call_prompt,
            self.record_call_response,
            self.redirect_call_by_id,
            self.reject_call_by_id,
            self.send_dtmf_tones_to_call,
            self.subscribe_to_call_tone,
            self.transfer_call_by_id,
            self.unmute_call,
            self.update_call_recording_status,
            self.get_call_operations,
            self.create_call_operation,
            self.get_comms_operation_details,
            self.patch_call_operation,
            self.delete_comms_operation,
            self.count_call_operations,
            self.get_call_participants,
            self.add_call_participant,
            self.get_call_participant,
            self.update_call_participant,
            self.delete_participant_from_call,
            self.mute_participant,
            self.start_hold_music_for_participant,
            self.stop_hold_music_for_participant,
            self.get_call_participants_count,
            self.invite_call_participant,
            self.get_calls_count,
            self.log_teleconference_device_quality,
            self.get_presences_by_user,
            self.list_online_meetings,
            self.create_online_meeting,
            self.get_online_meeting_details,
            self.update_online_meeting,
            self.delete_online_meeting_by_id,
            self.get_attendance_report,
            self.create_meeting_attendance_report,
            self.get_attendance_report_details,
            self.update_attendance_report,
            self.delete_meeting_attendance_report,
            self.list_comm_meeting_att_records,
            self.add_attendance_record,
            self.get_attendance_record_details,
            self.update_attendance_record_by_id,
            self.deletecomm_attendance_record,
            self.get_attendance_records_count,
            self.get_meeting_attendance_count,
            self.get_attendee_report_by_meeting_id,
            self.upload_attendee_report_stream,
            self.delete_comm_online_mtg_att_report,
            self.get_virtual_join_url,
            self.send_virtual_meeting_reminder_sms,
            self.send_online_meeting_sms,
            self.list_meeting_recordings,
            self.start_recording,
            self.get_recording,
            self.update_meeting_recording,
            self.delete_call_recording_by_id,
            self.get_meeting_recording_content,
            self.upload_recording_content,
            self.delete_call_recording_content_by_id,
            self.count_recordings,
            self.get_comm_meeting_recordings_delta,
            self.get_online_meeting_transcript,
            self.create_transcript_comm,
            self.get_transcript_data,
            self.patch_transcript,
            self.delete_transcript,
            self.get_transcript_content_by_id,
            self.update_call_transcript_content,
            self.delete_transcript_content_by_id,
            self.get_metadata_content,
            self.update_comm_transcript_metadata,
            self.delete_metadata_content,
            self.count_online_meeting_transcript,
            self.get_meeting_transcripts_delta,
            self.get_online_meetings_count,
            self.create_or_get_online_meeting,
            self.get_recordings_by_organizer,
            self.get_all_meeting_transcripts,
            self.communications_list_presences,
            self.communications_create_presences,
            self.communications_get_presences,
            self.communications_update_presences,
            self.communications_delete_presences,
            self.clear_presence_by_id,
            self.clear_user_presence,
            self.set_presence_by_id,
            self.set_presence_status_message,
            self.set_preferred_presence,
            self.count_communications_presences,
        ]
