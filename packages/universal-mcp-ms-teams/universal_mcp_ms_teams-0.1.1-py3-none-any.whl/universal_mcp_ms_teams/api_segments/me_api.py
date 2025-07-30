from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class MeApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def me_list_online_meetings(
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
            me.onlineMeeting, important
        """
        url = f"{self.main_app_client.base_url}/me/onlineMeetings"
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

    def me_create_online_meetings(
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

        Create onlineMeeting

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def me_get_online_meetings(
        self,
        onlineMeeting_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get onlineMeeting

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def me_update_online_meetings(
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

        Update onlineMeeting

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def me_delete_online_meetings(self, onlineMeeting_id: str) -> Any:
        """

        Delete onlineMeeting

        Args:
            onlineMeeting_id (string): onlineMeeting-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_meeting_attendance_reports(
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

        List meetingAttendanceReports

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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports"
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

    def generate_attendance_report(
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

        Create new navigation property to attendanceReports for me

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_meeting_attendance_report(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get meetingAttendanceReport

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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_meeting_attendance_report(
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

        Update the navigation property attendanceReports in me

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_attendance_report(
        self, onlineMeeting_id: str, meetingAttendanceReport_id: str
    ) -> Any:
        """

        Delete navigation property attendanceReports for me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_my_meeting_att_records(
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

        List attendanceRecords

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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords"
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

    def create_attendance_record(
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

        Create new navigation property to attendanceRecords for me

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_attendance_record(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        attendanceRecord_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get attendanceRecords from me

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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        if attendanceRecord_id is None:
            raise ValueError("Missing required parameter 'attendanceRecord-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords/{attendanceRecord_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_attendance_record(
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

        Update the navigation property attendanceRecords in me

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords/{attendanceRecord_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def deletemy_attendance_record(
        self,
        onlineMeeting_id: str,
        meetingAttendanceReport_id: str,
        attendanceRecord_id: str,
    ) -> Any:
        """

        Delete navigation property attendanceRecords for me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            meetingAttendanceReport_id (string): meetingAttendanceReport-id
            attendanceRecord_id (string): attendanceRecord-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        if attendanceRecord_id is None:
            raise ValueError("Missing required parameter 'attendanceRecord-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords/{attendanceRecord_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_attendance_count(
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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if meetingAttendanceReport_id is None:
            raise ValueError("Missing required parameter 'meetingAttendanceReport-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/{meetingAttendanceReport_id}/attendanceRecords/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_online_meeting_attend_count(
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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendanceReports/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_attendee_report(self, onlineMeeting_id: str) -> Any:
        """

        Get onlineMeeting

        Args:
            onlineMeeting_id (string): onlineMeeting-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendeeReport"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_attendee_report(self, onlineMeeting_id: str, body_content: bytes) -> Any:
        """

        Update attendeeReport for the navigation property onlineMeetings in me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendeeReport"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_attendee_report(self, onlineMeeting_id: str) -> Any:
        """

        Delete attendeeReport for the navigation property onlineMeetings in me

        Args:
            onlineMeeting_id (string): onlineMeeting-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/attendeeReport"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_virtual_appointment_join_url(self, onlineMeeting_id: str) -> dict[str, Any]:
        """

        Invoke function getVirtualAppointmentJoinWebUrl

        Args:
            onlineMeeting_id (string): onlineMeeting-id

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/getVirtualAppointmentJoinWebUrl()"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def send_reminder_sms(
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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/sendVirtualAppointmentReminderSms"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def send_virtual_appointment_sms(
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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        request_body_data = None
        request_body_data = {"messageType": messageType, "attendees": attendees}
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/sendVirtualAppointmentSms"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_online_meeting_recordings(
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

        Get callRecording

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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings"
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

    def create_recording(
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

        Create new navigation property to recordings for me

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_online_meeting_recording(
        self,
        onlineMeeting_id: str,
        callRecording_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get recordings from me

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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_call_recording_by_id(
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

        Update the navigation property recordings in me

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_call_recording(
        self, onlineMeeting_id: str, callRecording_id: str
    ) -> Any:
        """

        Delete navigation property recordings for me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_call_recording_content_by_id(
        self, onlineMeeting_id: str, callRecording_id: str
    ) -> Any:
        """

        Get content for the navigation property recordings from me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}/content"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_recording_content(
        self, onlineMeeting_id: str, callRecording_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property recordings in me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_recording_content(
        self, onlineMeeting_id: str, callRecording_id: str
    ) -> Any:
        """

        Delete content for the navigation property recordings in me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callRecording_id (string): callRecording-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callRecording_id is None:
            raise ValueError("Missing required parameter 'callRecording-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings/{callRecording_id}/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_online_meeting_recordings(
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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_my_meeting_recordings_delta(
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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/recordings/delta()"
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

    def get_online_meeting_transcripts(
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

        Get callTranscript

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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts"
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

    def create_transcript_me(
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

        Create new navigation property to transcripts for me

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_call_transcript_by_id(
        self,
        onlineMeeting_id: str,
        callTranscript_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get transcripts from me

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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_transcript(
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

        Update the navigation property transcripts in me

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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_transcript_by_id(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Delete navigation property transcripts for me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_call_transcript_content_by_id(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Get content for the navigation property transcripts from me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/content"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_transcript_content(
        self, onlineMeeting_id: str, callTranscript_id: str, body_content: bytes
    ) -> Any:
        """

        Update content for the navigation property transcripts in me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/content"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_transcript_content(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Delete content for the navigation property transcripts in me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/content"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_transcript_metadata(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Get metadataContent for the navigation property transcripts from me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Retrieved media content

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/metadataContent"
        query_params = {}
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_my_transcript_metadata(
        self, onlineMeeting_id: str, callTranscript_id: str, body_content: bytes
    ) -> Any:
        """

        Update metadataContent for the navigation property transcripts in me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id
            body_content (bytes | None): Raw binary content for the request body.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        request_body_data = None
        request_body_data = body_content
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/metadataContent"
        query_params = {}
        response = self._put(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/octet-stream",
        )
        return self._handle_response(response)

    def delete_transcript_metadata(
        self, onlineMeeting_id: str, callTranscript_id: str
    ) -> Any:
        """

        Delete metadataContent for the navigation property transcripts in me

        Args:
            onlineMeeting_id (string): onlineMeeting-id
            callTranscript_id (string): callTranscript-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        if callTranscript_id is None:
            raise ValueError("Missing required parameter 'callTranscript-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/{callTranscript_id}/metadataContent"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_online_meeting_transcripts(
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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_transcripts_delta(
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
            me.onlineMeeting
        """
        if onlineMeeting_id is None:
            raise ValueError("Missing required parameter 'onlineMeeting-id'.")
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/{onlineMeeting_id}/transcripts/delta()"
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

    def count_online_meetings(
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
            me.onlineMeeting
        """
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def me_online_meetings_create_or_get(
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
            me.onlineMeeting
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
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/createOrGet"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def list_all_meeting_recordings(
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
            me.onlineMeeting
        """
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/getAllRecordings(meetingOrganizerUserId='@meetingOrganizerUserId',startDateTime=@startDateTime,endDateTime=@endDateTime)"
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

    def get_meeting_transcripts(
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
            me.onlineMeeting
        """
        url = f"{self.main_app_client.base_url}/me/onlineMeetings/getAllTranscripts(meetingOrganizerUserId='@meetingOrganizerUserId',startDateTime=@startDateTime,endDateTime=@endDateTime)"
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

    def list_my_learning_activities(
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

        Get learningCourseActivities from me

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
            me.employeeExperienceUser
        """
        url = f"{self.main_app_client.base_url}/me/employeeExperience/learningCourseActivities"
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

    def get_my_learning_course_activity(
        self,
        learningCourseActivity_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningCourseActivities from me

        Args:
            learningCourseActivity_id (string): learningCourseActivity-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.employeeExperienceUser
        """
        if learningCourseActivity_id is None:
            raise ValueError("Missing required parameter 'learningCourseActivity-id'.")
        url = f"{self.main_app_client.base_url}/me/employeeExperience/learningCourseActivities/{learningCourseActivity_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_my_learning_activity_by_ext_id(
        self,
        externalcourseActivityId: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningCourseActivities from me

        Args:
            externalcourseActivityId (string): externalcourseActivityId
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me.employeeExperienceUser
        """
        if externalcourseActivityId is None:
            raise ValueError("Missing required parameter 'externalcourseActivityId'.")
        url = f"{self.main_app_client.base_url}/me/employeeExperience/learningCourseActivities(externalcourseActivityId='{externalcourseActivityId}')"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_learning_course_activity_count(
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
            me.employeeExperienceUser
        """
        url = f"{self.main_app_client.base_url}/me/employeeExperience/learningCourseActivities/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.me_list_online_meetings,
            self.me_create_online_meetings,
            self.me_get_online_meetings,
            self.me_update_online_meetings,
            self.me_delete_online_meetings,
            self.get_meeting_attendance_reports,
            self.generate_attendance_report,
            self.get_meeting_attendance_report,
            self.update_meeting_attendance_report,
            self.delete_attendance_report,
            self.list_my_meeting_att_records,
            self.create_attendance_record,
            self.get_attendance_record,
            self.update_attendance_record,
            self.deletemy_attendance_record,
            self.get_attendance_count,
            self.get_online_meeting_attend_count,
            self.get_attendee_report,
            self.update_attendee_report,
            self.delete_attendee_report,
            self.get_virtual_appointment_join_url,
            self.send_reminder_sms,
            self.send_virtual_appointment_sms,
            self.get_online_meeting_recordings,
            self.create_recording,
            self.get_online_meeting_recording,
            self.update_call_recording_by_id,
            self.delete_call_recording,
            self.get_call_recording_content_by_id,
            self.update_recording_content,
            self.delete_recording_content,
            self.count_online_meeting_recordings,
            self.get_my_meeting_recordings_delta,
            self.get_online_meeting_transcripts,
            self.create_transcript_me,
            self.get_call_transcript_by_id,
            self.update_transcript,
            self.delete_transcript_by_id,
            self.get_call_transcript_content_by_id,
            self.update_transcript_content,
            self.delete_transcript_content,
            self.get_transcript_metadata,
            self.update_my_transcript_metadata,
            self.delete_transcript_metadata,
            self.count_online_meeting_transcripts,
            self.get_transcripts_delta,
            self.count_online_meetings,
            self.me_online_meetings_create_or_get,
            self.list_all_meeting_recordings,
            self.get_meeting_transcripts,
            self.list_my_learning_activities,
            self.get_my_learning_course_activity,
            self.get_my_learning_activity_by_ext_id,
            self.get_learning_course_activity_count,
        ]
