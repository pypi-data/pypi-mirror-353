from typing import Any, List, Optional
from .api_segment_base import APISegmentBase


class EmployeeexperienceApi(APISegmentBase):

    def __init__(self, main_app_client: Any):
        super().__init__(main_app_client)

    def get_learning_provider(
        self,
        learningProvider_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningProvider

        Args:
            learningProvider_id (string): learningProvider-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_learning_provider(
        self,
        learningProvider_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        isCourseActivitySyncEnabled: Optional[bool] = None,
        loginWebUrl: Optional[str] = None,
        longLogoWebUrlForDarkTheme: Optional[str] = None,
        longLogoWebUrlForLightTheme: Optional[str] = None,
        squareLogoWebUrlForDarkTheme: Optional[str] = None,
        squareLogoWebUrlForLightTheme: Optional[str] = None,
        learningContents: Optional[List[Any]] = None,
        learningCourseActivities: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update learningProvider

        Args:
            learningProvider_id (string): learningProvider-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name that appears in Viva Learning. Required.
            isCourseActivitySyncEnabled (boolean): Indicates whether a provider can ingest learning course activity records. The default value is false. Set to true to make learningCourseActivities available for this provider.
            loginWebUrl (string): Authentication URL to access the courses for the provider. Optional.
            longLogoWebUrlForDarkTheme (string): The long logo URL for the dark mode that needs to be a publicly accessible image. This image would be saved to the blob storage of Viva Learning for rendering within the Viva Learning app. Required.
            longLogoWebUrlForLightTheme (string): The long logo URL for the light mode that needs to be a publicly accessible image. This image would be saved to the blob storage of Viva Learning for rendering within the Viva Learning app. Required.
            squareLogoWebUrlForDarkTheme (string): The square logo URL for the dark mode that needs to be a publicly accessible image. This image would be saved to the blob storage of Viva Learning for rendering within the Viva Learning app. Required.
            squareLogoWebUrlForLightTheme (string): The square logo URL for the light mode that needs to be a publicly accessible image. This image would be saved to the blob storage of Viva Learning for rendering within the Viva Learning app. Required.
            learningContents (array): Learning catalog items for the provider.
            learningCourseActivities (array): learningCourseActivities

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "isCourseActivitySyncEnabled": isCourseActivitySyncEnabled,
            "loginWebUrl": loginWebUrl,
            "longLogoWebUrlForDarkTheme": longLogoWebUrlForDarkTheme,
            "longLogoWebUrlForLightTheme": longLogoWebUrlForLightTheme,
            "squareLogoWebUrlForDarkTheme": squareLogoWebUrlForDarkTheme,
            "squareLogoWebUrlForLightTheme": squareLogoWebUrlForLightTheme,
            "learningContents": learningContents,
            "learningCourseActivities": learningCourseActivities,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_learning_provider_by_id(self, learningProvider_id: str) -> Any:
        """

        Delete learningProvider

        Args:
            learningProvider_id (string): learningProvider-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def list_learning_contents(
        self,
        learningProvider_id: str,
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

        List learningContents

        Args:
            learningProvider_id (string): learningProvider-id
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
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents"
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

    def create_learning_content(
        self,
        learningProvider_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        additionalTags: Optional[List[str]] = None,
        contentWebUrl: Optional[str] = None,
        contributors: Optional[List[str]] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        duration: Optional[str] = None,
        externalId: Optional[str] = None,
        format: Optional[str] = None,
        isActive: Optional[bool] = None,
        isPremium: Optional[bool] = None,
        isSearchable: Optional[bool] = None,
        languageTag: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        level: Optional[Any] = None,
        numberOfPages: Optional[float] = None,
        skillTags: Optional[List[str]] = None,
        sourceName: Optional[str] = None,
        thumbnailWebUrl: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to learningContents for employeeExperience

        Args:
            learningProvider_id (string): learningProvider-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            additionalTags (array): Keywords, topics, and other tags associated with the learning content. Optional.
            contentWebUrl (string): The content web URL for the learning content. Required.
            contributors (array): The authors, creators, or contributors of the learning content. Optional.
            createdDateTime (string): The date and time when the learning content was created. The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Optional.
            description (string): The description or summary for the learning content. Optional.
            duration (string): The duration of the learning content in seconds. The value is represented in ISO 8601 format for durations. Optional.
            externalId (string): Unique external content ID for the learning content. Required.
            format (string): The format of the learning content. For example, Course, Video, Book, Book Summary, Audiobook Summary. Optional.
            isActive (boolean): Indicates whether the content is active or not. Inactive content doesn't show up in the UI. The default value is true. Optional.
            isPremium (boolean): Indicates whether the learning content requires the user to sign-in on the learning provider platform or not. The default value is false. Optional.
            isSearchable (boolean): Indicates whether the learning content is searchable or not. The default value is true. Optional.
            languageTag (string): The language of the learning content, for example, en-us or fr-fr. Required.
            lastModifiedDateTime (string): The date and time when the learning content was last modified. The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Optional.
            level (string): The difficulty level of the learning content. Possible values are: Beginner, Intermediate, Advanced, unknownFutureValue. Optional.
            numberOfPages (number): The number of pages of the learning content, for example, 9. Optional.
            skillTags (array): The skills tags associated with the learning content. Optional.
            sourceName (string): The source name of the learning content, such as LinkedIn Learning or Coursera. Optional.
            thumbnailWebUrl (string): The URL of learning content thumbnail image. Optional.
            title (string): The title of the learning content. Required.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "additionalTags": additionalTags,
            "contentWebUrl": contentWebUrl,
            "contributors": contributors,
            "createdDateTime": createdDateTime,
            "description": description,
            "duration": duration,
            "externalId": externalId,
            "format": format,
            "isActive": isActive,
            "isPremium": isPremium,
            "isSearchable": isSearchable,
            "languageTag": languageTag,
            "lastModifiedDateTime": lastModifiedDateTime,
            "level": level,
            "numberOfPages": numberOfPages,
            "skillTags": skillTags,
            "sourceName": sourceName,
            "thumbnailWebUrl": thumbnailWebUrl,
            "title": title,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_learning_contents_by_provider(
        self,
        learningProvider_id: str,
        learningContent_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningContent

        Args:
            learningProvider_id (string): learningProvider-id
            learningContent_id (string): learningContent-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if learningContent_id is None:
            raise ValueError("Missing required parameter 'learningContent-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents/{learningContent_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_learning_content(
        self,
        learningProvider_id: str,
        learningContent_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        additionalTags: Optional[List[str]] = None,
        contentWebUrl: Optional[str] = None,
        contributors: Optional[List[str]] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        duration: Optional[str] = None,
        externalId: Optional[str] = None,
        format: Optional[str] = None,
        isActive: Optional[bool] = None,
        isPremium: Optional[bool] = None,
        isSearchable: Optional[bool] = None,
        languageTag: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        level: Optional[Any] = None,
        numberOfPages: Optional[float] = None,
        skillTags: Optional[List[str]] = None,
        sourceName: Optional[str] = None,
        thumbnailWebUrl: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property learningContents in employeeExperience

        Args:
            learningProvider_id (string): learningProvider-id
            learningContent_id (string): learningContent-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            additionalTags (array): Keywords, topics, and other tags associated with the learning content. Optional.
            contentWebUrl (string): The content web URL for the learning content. Required.
            contributors (array): The authors, creators, or contributors of the learning content. Optional.
            createdDateTime (string): The date and time when the learning content was created. The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Optional.
            description (string): The description or summary for the learning content. Optional.
            duration (string): The duration of the learning content in seconds. The value is represented in ISO 8601 format for durations. Optional.
            externalId (string): Unique external content ID for the learning content. Required.
            format (string): The format of the learning content. For example, Course, Video, Book, Book Summary, Audiobook Summary. Optional.
            isActive (boolean): Indicates whether the content is active or not. Inactive content doesn't show up in the UI. The default value is true. Optional.
            isPremium (boolean): Indicates whether the learning content requires the user to sign-in on the learning provider platform or not. The default value is false. Optional.
            isSearchable (boolean): Indicates whether the learning content is searchable or not. The default value is true. Optional.
            languageTag (string): The language of the learning content, for example, en-us or fr-fr. Required.
            lastModifiedDateTime (string): The date and time when the learning content was last modified. The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Optional.
            level (string): The difficulty level of the learning content. Possible values are: Beginner, Intermediate, Advanced, unknownFutureValue. Optional.
            numberOfPages (number): The number of pages of the learning content, for example, 9. Optional.
            skillTags (array): The skills tags associated with the learning content. Optional.
            sourceName (string): The source name of the learning content, such as LinkedIn Learning or Coursera. Optional.
            thumbnailWebUrl (string): The URL of learning content thumbnail image. Optional.
            title (string): The title of the learning content. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if learningContent_id is None:
            raise ValueError("Missing required parameter 'learningContent-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "additionalTags": additionalTags,
            "contentWebUrl": contentWebUrl,
            "contributors": contributors,
            "createdDateTime": createdDateTime,
            "description": description,
            "duration": duration,
            "externalId": externalId,
            "format": format,
            "isActive": isActive,
            "isPremium": isPremium,
            "isSearchable": isSearchable,
            "languageTag": languageTag,
            "lastModifiedDateTime": lastModifiedDateTime,
            "level": level,
            "numberOfPages": numberOfPages,
            "skillTags": skillTags,
            "sourceName": sourceName,
            "thumbnailWebUrl": thumbnailWebUrl,
            "title": title,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents/{learningContent_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def del_prov_learn_content_by_id(
        self, learningProvider_id: str, learningContent_id: str
    ) -> Any:
        """

        Delete learningContent

        Args:
            learningProvider_id (string): learningProvider-id
            learningContent_id (string): learningContent-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if learningContent_id is None:
            raise ValueError("Missing required parameter 'learningContent-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents/{learningContent_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_learning_content_by_external_id(
        self,
        learningProvider_id: str,
        externalId: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningContent

        Args:
            learningProvider_id (string): learningProvider-id
            externalId (string): externalId
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if externalId is None:
            raise ValueError("Missing required parameter 'externalId'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents(externalId='{externalId}')"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_learning_content(
        self,
        learningProvider_id: str,
        externalId: str,
        atodata_type: str,
        id: Optional[str] = None,
        additionalTags: Optional[List[str]] = None,
        contentWebUrl: Optional[str] = None,
        contributors: Optional[List[str]] = None,
        createdDateTime: Optional[str] = None,
        description: Optional[str] = None,
        duration: Optional[str] = None,
        externalId_body: Optional[str] = None,
        format: Optional[str] = None,
        isActive: Optional[bool] = None,
        isPremium: Optional[bool] = None,
        isSearchable: Optional[bool] = None,
        languageTag: Optional[str] = None,
        lastModifiedDateTime: Optional[str] = None,
        level: Optional[Any] = None,
        numberOfPages: Optional[float] = None,
        skillTags: Optional[List[str]] = None,
        sourceName: Optional[str] = None,
        thumbnailWebUrl: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property learningContents in employeeExperience

        Args:
            learningProvider_id (string): learningProvider-id
            externalId (string): externalId
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            additionalTags (array): Keywords, topics, and other tags associated with the learning content. Optional.
            contentWebUrl (string): The content web URL for the learning content. Required.
            contributors (array): The authors, creators, or contributors of the learning content. Optional.
            createdDateTime (string): The date and time when the learning content was created. The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Optional.
            description (string): The description or summary for the learning content. Optional.
            duration (string): The duration of the learning content in seconds. The value is represented in ISO 8601 format for durations. Optional.
            externalId_body (string): Unique external content ID for the learning content. Required.
            format (string): The format of the learning content. For example, Course, Video, Book, Book Summary, Audiobook Summary. Optional.
            isActive (boolean): Indicates whether the content is active or not. Inactive content doesn't show up in the UI. The default value is true. Optional.
            isPremium (boolean): Indicates whether the learning content requires the user to sign-in on the learning provider platform or not. The default value is false. Optional.
            isSearchable (boolean): Indicates whether the learning content is searchable or not. The default value is true. Optional.
            languageTag (string): The language of the learning content, for example, en-us or fr-fr. Required.
            lastModifiedDateTime (string): The date and time when the learning content was last modified. The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z. Optional.
            level (string): The difficulty level of the learning content. Possible values are: Beginner, Intermediate, Advanced, unknownFutureValue. Optional.
            numberOfPages (number): The number of pages of the learning content, for example, 9. Optional.
            skillTags (array): The skills tags associated with the learning content. Optional.
            sourceName (string): The source name of the learning content, such as LinkedIn Learning or Coursera. Optional.
            thumbnailWebUrl (string): The URL of learning content thumbnail image. Optional.
            title (string): The title of the learning content. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if externalId is None:
            raise ValueError("Missing required parameter 'externalId'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "additionalTags": additionalTags,
            "contentWebUrl": contentWebUrl,
            "contributors": contributors,
            "createdDateTime": createdDateTime,
            "description": description,
            "duration": duration,
            "externalId": externalId_body,
            "format": format,
            "isActive": isActive,
            "isPremium": isPremium,
            "isSearchable": isSearchable,
            "languageTag": languageTag,
            "lastModifiedDateTime": lastModifiedDateTime,
            "level": level,
            "numberOfPages": numberOfPages,
            "skillTags": skillTags,
            "sourceName": sourceName,
            "thumbnailWebUrl": thumbnailWebUrl,
            "title": title,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents(externalId='{externalId}')"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def del_prov_learn_content_by_ext_id(
        self, learningProvider_id: str, externalId: str
    ) -> Any:
        """

        Delete learningContent

        Args:
            learningProvider_id (string): learningProvider-id
            externalId (string): externalId

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if externalId is None:
            raise ValueError("Missing required parameter 'externalId'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents(externalId='{externalId}')"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_learning_content_count(
        self,
        learningProvider_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            learningProvider_id (string): learningProvider-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningContents/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_learning_course_activities(
        self,
        learningProvider_id: str,
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

        Get learningCourseActivity

        Args:
            learningProvider_id (string): learningProvider-id
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
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities"
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

    def create_learning_course_activity(
        self,
        learningProvider_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        completedDateTime: Optional[str] = None,
        completionPercentage: Optional[float] = None,
        externalcourseActivityId: Optional[str] = None,
        learnerUserId: Optional[str] = None,
        learningContentId: Optional[str] = None,
        learningProviderId: Optional[str] = None,
        status: Optional[Any] = None,
    ) -> Any:
        """

        Create learningCourseActivity

        Args:
            learningProvider_id (string): learningProvider-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            completedDateTime (string): Date and time when the assignment was completed. Optional.
            completionPercentage (number): The percentage completion value of the course activity. Optional.
            externalcourseActivityId (string): externalcourseActivityId
            learnerUserId (string): The user ID of the learner to whom the activity is assigned. Required.
            learningContentId (string): The ID of the learning content created in Viva Learning. Required.
            learningProviderId (string): The registration ID of the provider. Required.
            status (string): The status of the course activity. Possible values are: notStarted, inProgress, completed. Required.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "completedDateTime": completedDateTime,
            "completionPercentage": completionPercentage,
            "externalcourseActivityId": externalcourseActivityId,
            "learnerUserId": learnerUserId,
            "learningContentId": learningContentId,
            "learningProviderId": learningProviderId,
            "status": status,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_prov_learn_course_activity(
        self,
        learningProvider_id: str,
        learningCourseActivity_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningCourseActivities from employeeExperience

        Args:
            learningProvider_id (string): learningProvider-id
            learningCourseActivity_id (string): learningCourseActivity-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if learningCourseActivity_id is None:
            raise ValueError("Missing required parameter 'learningCourseActivity-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities/{learningCourseActivity_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_prov_course_activity_by_id(
        self,
        learningProvider_id: str,
        learningCourseActivity_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        completedDateTime: Optional[str] = None,
        completionPercentage: Optional[float] = None,
        externalcourseActivityId: Optional[str] = None,
        learnerUserId: Optional[str] = None,
        learningContentId: Optional[str] = None,
        learningProviderId: Optional[str] = None,
        status: Optional[Any] = None,
    ) -> Any:
        """

        Update learningCourseActivity

        Args:
            learningProvider_id (string): learningProvider-id
            learningCourseActivity_id (string): learningCourseActivity-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            completedDateTime (string): Date and time when the assignment was completed. Optional.
            completionPercentage (number): The percentage completion value of the course activity. Optional.
            externalcourseActivityId (string): externalcourseActivityId
            learnerUserId (string): The user ID of the learner to whom the activity is assigned. Required.
            learningContentId (string): The ID of the learning content created in Viva Learning. Required.
            learningProviderId (string): The registration ID of the provider. Required.
            status (string): The status of the course activity. Possible values are: notStarted, inProgress, completed. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if learningCourseActivity_id is None:
            raise ValueError("Missing required parameter 'learningCourseActivity-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "completedDateTime": completedDateTime,
            "completionPercentage": completionPercentage,
            "externalcourseActivityId": externalcourseActivityId,
            "learnerUserId": learnerUserId,
            "learningContentId": learningContentId,
            "learningProviderId": learningProviderId,
            "status": status,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities/{learningCourseActivity_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_learning_course_activity(
        self, learningProvider_id: str, learningCourseActivity_id: str
    ) -> Any:
        """

        Delete learningCourseActivity

        Args:
            learningProvider_id (string): learningProvider-id
            learningCourseActivity_id (string): learningCourseActivity-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if learningCourseActivity_id is None:
            raise ValueError("Missing required parameter 'learningCourseActivity-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities/{learningCourseActivity_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_provider_course_activity(
        self,
        learningProvider_id: str,
        externalcourseActivityId: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningCourseActivities from employeeExperience

        Args:
            learningProvider_id (string): learningProvider-id
            externalcourseActivityId (string): externalcourseActivityId
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if externalcourseActivityId is None:
            raise ValueError("Missing required parameter 'externalcourseActivityId'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities(externalcourseActivityId='{externalcourseActivityId}')"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_prov_course_actvty_by_ext_id(
        self,
        learningProvider_id: str,
        externalcourseActivityId: str,
        atodata_type: str,
        id: Optional[str] = None,
        completedDateTime: Optional[str] = None,
        completionPercentage: Optional[float] = None,
        externalcourseActivityId_body: Optional[str] = None,
        learnerUserId: Optional[str] = None,
        learningContentId: Optional[str] = None,
        learningProviderId: Optional[str] = None,
        status: Optional[Any] = None,
    ) -> Any:
        """

        Update learningCourseActivity

        Args:
            learningProvider_id (string): learningProvider-id
            externalcourseActivityId (string): externalcourseActivityId
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            completedDateTime (string): Date and time when the assignment was completed. Optional.
            completionPercentage (number): The percentage completion value of the course activity. Optional.
            externalcourseActivityId_body (string): externalcourseActivityId
            learnerUserId (string): The user ID of the learner to whom the activity is assigned. Required.
            learningContentId (string): The ID of the learning content created in Viva Learning. Required.
            learningProviderId (string): The registration ID of the provider. Required.
            status (string): The status of the course activity. Possible values are: notStarted, inProgress, completed. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if externalcourseActivityId is None:
            raise ValueError("Missing required parameter 'externalcourseActivityId'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "completedDateTime": completedDateTime,
            "completionPercentage": completionPercentage,
            "externalcourseActivityId": externalcourseActivityId_body,
            "learnerUserId": learnerUserId,
            "learningContentId": learningContentId,
            "learningProviderId": learningProviderId,
            "status": status,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities(externalcourseActivityId='{externalcourseActivityId}')"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_learning_activity_by_ext(
        self, learningProvider_id: str, externalcourseActivityId: str
    ) -> Any:
        """

        Delete learningCourseActivity

        Args:
            learningProvider_id (string): learningProvider-id
            externalcourseActivityId (string): externalcourseActivityId

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        if externalcourseActivityId is None:
            raise ValueError("Missing required parameter 'externalcourseActivityId'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities(externalcourseActivityId='{externalcourseActivityId}')"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def count_learning_course_activities(
        self,
        learningProvider_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            learningProvider_id (string): learningProvider-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        if learningProvider_id is None:
            raise ValueError("Missing required parameter 'learningProvider-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/{learningProvider_id}/learningCourseActivities/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_learning_providers(
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
            employeeExperience.learningProvider
        """
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_communities(
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

        List communities

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
            employeeExperience.community
        """
        url = f"{self.main_app_client.base_url}/employeeExperience/communities"
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

    def create_community_experience(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        groupId: Optional[str] = None,
        privacy: Optional[str] = None,
        group: Optional[Any] = None,
        owners: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create community

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            description (string): The description of the community. The maximum length is 1,024 characters.
            displayName (string): The name of the community. The maximum length is 255 characters.
            groupId (string): The ID of the Microsoft 365 group that manages the membership of this community.
            privacy (string): Types of communityPrivacy.
            group (string): The Microsoft 365 group that manages the membership of this community.
            owners (array): The admins of the community. Limited to 100 users. If this property isn't specified when you create the community, the calling user is automatically assigned as the community owner.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "description": description,
            "displayName": displayName,
            "groupId": groupId,
            "privacy": privacy,
            "group": group,
            "owners": owners,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/communities"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_community_details(
        self,
        community_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get community

        Args:
            community_id (string): community-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_community(
        self,
        community_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        groupId: Optional[str] = None,
        privacy: Optional[str] = None,
        group: Optional[Any] = None,
        owners: Optional[List[Any]] = None,
    ) -> Any:
        """

        Update community

        Args:
            community_id (string): community-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            description (string): The description of the community. The maximum length is 1,024 characters.
            displayName (string): The name of the community. The maximum length is 255 characters.
            groupId (string): The ID of the Microsoft 365 group that manages the membership of this community.
            privacy (string): Types of communityPrivacy.
            group (string): The Microsoft 365 group that manages the membership of this community.
            owners (array): The admins of the community. Limited to 100 users. If this property isn't specified when you create the community, the calling user is automatically assigned as the community owner.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "description": description,
            "displayName": displayName,
            "groupId": groupId,
            "privacy": privacy,
            "group": group,
            "owners": owners,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_community_by_id(self, community_id: str) -> Any:
        """

        Delete community

        Args:
            community_id (string): community-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_community_group(
        self,
        community_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get group from employeeExperience

        Args:
            community_id (string): community-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/group"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_community_provisioning_errors(
        self,
        community_id: str,
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
            community_id (string): community-id
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
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/group/serviceProvisioningErrors"
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

    def get_group_service_errors_count(
        self,
        community_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            community_id (string): community-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/group/serviceProvisioningErrors/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_community_owners(
        self,
        community_id: str,
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

        Get owners from employeeExperience

        Args:
            community_id (string): community-id
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
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/owners"
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

    def get_community_owners(
        self,
        community_id: str,
        user_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get owners from employeeExperience

        Args:
            community_id (string): community-id
            user_id (string): user-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/owners/{user_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_mailbox_settings(
        self,
        community_id: str,
        user_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """

        Get mailboxSettings property value

        Args:
            community_id (string): community-id
            user_id (string): user-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Entity result.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/owners/{user_id}/mailboxSettings"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_community_mailbox_setting(
        self,
        community_id: str,
        user_id: str,
        atodata_type: str,
        archiveFolder: Optional[str] = None,
        automaticRepliesSetting: Optional[Any] = None,
        dateFormat: Optional[str] = None,
        delegateMeetingMessageDeliveryOptions: Optional[Any] = None,
        language: Optional[Any] = None,
        timeFormat: Optional[str] = None,
        timeZone: Optional[str] = None,
        userPurpose: Optional[Any] = None,
        workingHours: Optional[Any] = None,
    ) -> dict[str, Any]:
        """

        Update property mailboxSettings value.

        Args:
            community_id (string): community-id
            user_id (string): user-id
            atodata_type (string): @odata.type
            archiveFolder (string): Folder ID of an archive folder for the user.
            automaticRepliesSetting (string): Configuration settings to automatically notify the sender of an incoming email with a message from the signed-in user.
            dateFormat (string): The date format for the user's mailbox.
            delegateMeetingMessageDeliveryOptions (string): If the user has a calendar delegate, this specifies whether the delegate, mailbox owner, or both receive meeting messages and meeting responses. Possible values are: sendToDelegateAndInformationToPrincipal, sendToDelegateAndPrincipal, sendToDelegateOnly.
            language (string): The locale information for the user, including the preferred language and country/region.
            timeFormat (string): The time format for the user's mailbox.
            timeZone (string): The default time zone for the user's mailbox.
            userPurpose (string): The purpose of the mailbox. Differentiates a mailbox for a single user from a shared mailbox and equipment mailbox in Exchange Online. Possible values are: user, linked, shared, room, equipment, others, unknownFutureValue. Read-only.
            workingHours (string): The days of the week and hours in a specific time zone that the user works.

        Returns:
            dict[str, Any]: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        request_body_data = None
        request_body_data = {
            "archiveFolder": archiveFolder,
            "automaticRepliesSetting": automaticRepliesSetting,
            "dateFormat": dateFormat,
            "delegateMeetingMessageDeliveryOptions": delegateMeetingMessageDeliveryOptions,
            "language": language,
            "timeFormat": timeFormat,
            "timeZone": timeZone,
            "userPurpose": userPurpose,
            "workingHours": workingHours,
            "@odata.type": atodata_type,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/owners/{user_id}/mailboxSettings"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def get_community_owner_service_errors(
        self,
        community_id: str,
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

        Get serviceProvisioningErrors property value

        Args:
            community_id (string): community-id
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
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/owners/{user_id}/serviceProvisioningErrors"
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

    def get_service_provisioning_count(
        self,
        community_id: str,
        user_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            community_id (string): community-id
            user_id (string): user-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/owners/{user_id}/serviceProvisioningErrors/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_community_owner_by_user(
        self,
        community_id: str,
        userPrincipalName: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get owners from employeeExperience

        Args:
            community_id (string): community-id
            userPrincipalName (string): userPrincipalName
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        if userPrincipalName is None:
            raise ValueError("Missing required parameter 'userPrincipalName'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/owners(userPrincipalName='{userPrincipalName}')"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_community_owners(
        self,
        community_id: str,
        search: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> Any:
        """

        Get the number of the resource

        Args:
            community_id (string): community-id
            search (string): Search items by search phrases
            filter (string): Filter items by property values

        Returns:
            Any: The count of the resource

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.community
        """
        if community_id is None:
            raise ValueError("Missing required parameter 'community-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/{community_id}/owners/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def count_employee_communities(
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
            employeeExperience.community
        """
        url = f"{self.main_app_client.base_url}/employeeExperience/communities/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_employee_engagement(
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

        Get engagementAsyncOperation

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
            employeeExperience.engagementAsyncOperation
        """
        url = f"{self.main_app_client.base_url}/employeeExperience/engagementAsyncOperations"
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

    def create_engagement_operation(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        lastActionDateTime: Optional[str] = None,
        resourceLocation: Optional[str] = None,
        status: Optional[Any] = None,
        statusDetail: Optional[str] = None,
        operationType: Optional[Any] = None,
        resourceId: Optional[str] = None,
    ) -> Any:
        """

        Create new navigation property to engagementAsyncOperations for employeeExperience

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdDateTime (string): The start time of the operation. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            lastActionDateTime (string): The time of the last action in the operation. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            resourceLocation (string): URI of the resource that the operation is performed on.
            status (string): The status of the operation. The possible values are: notStarted, running, succeeded, failed, unknownFutureValue.
            statusDetail (string): Details about the status of the operation.
            operationType (string): The type of the long-running operation. The possible values are: createCommunity, unknownFutureValue.
            resourceId (string): The ID of the object created or modified as a result of this async operation.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.engagementAsyncOperation
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdDateTime": createdDateTime,
            "lastActionDateTime": lastActionDateTime,
            "resourceLocation": resourceLocation,
            "status": status,
            "statusDetail": statusDetail,
            "operationType": operationType,
            "resourceId": resourceId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/engagementAsyncOperations"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_engagement_async_operation(
        self,
        engagementAsyncOperation_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get engagementAsyncOperation

        Args:
            engagementAsyncOperation_id (string): engagementAsyncOperation-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.engagementAsyncOperation
        """
        if engagementAsyncOperation_id is None:
            raise ValueError(
                "Missing required parameter 'engagementAsyncOperation-id'."
            )
        url = f"{self.main_app_client.base_url}/employeeExperience/engagementAsyncOperations/{engagementAsyncOperation_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_engagement_async_operation(
        self,
        engagementAsyncOperation_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        createdDateTime: Optional[str] = None,
        lastActionDateTime: Optional[str] = None,
        resourceLocation: Optional[str] = None,
        status: Optional[Any] = None,
        statusDetail: Optional[str] = None,
        operationType: Optional[Any] = None,
        resourceId: Optional[str] = None,
    ) -> Any:
        """

        Update the navigation property engagementAsyncOperations in employeeExperience

        Args:
            engagementAsyncOperation_id (string): engagementAsyncOperation-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            createdDateTime (string): The start time of the operation. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            lastActionDateTime (string): The time of the last action in the operation. The timestamp type represents date and time information using ISO 8601 format and is always in UTC. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
            resourceLocation (string): URI of the resource that the operation is performed on.
            status (string): The status of the operation. The possible values are: notStarted, running, succeeded, failed, unknownFutureValue.
            statusDetail (string): Details about the status of the operation.
            operationType (string): The type of the long-running operation. The possible values are: createCommunity, unknownFutureValue.
            resourceId (string): The ID of the object created or modified as a result of this async operation.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.engagementAsyncOperation
        """
        if engagementAsyncOperation_id is None:
            raise ValueError(
                "Missing required parameter 'engagementAsyncOperation-id'."
            )
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "createdDateTime": createdDateTime,
            "lastActionDateTime": lastActionDateTime,
            "resourceLocation": resourceLocation,
            "status": status,
            "statusDetail": statusDetail,
            "operationType": operationType,
            "resourceId": resourceId,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/engagementAsyncOperations/{engagementAsyncOperation_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_engagement_async_operation(
        self, engagementAsyncOperation_id: str
    ) -> Any:
        """

        Delete navigation property engagementAsyncOperations for employeeExperience

        Args:
            engagementAsyncOperation_id (string): engagementAsyncOperation-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.engagementAsyncOperation
        """
        if engagementAsyncOperation_id is None:
            raise ValueError(
                "Missing required parameter 'engagementAsyncOperation-id'."
            )
        url = f"{self.main_app_client.base_url}/employeeExperience/engagementAsyncOperations/{engagementAsyncOperation_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_engagement_op_count_async(
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
            employeeExperience.engagementAsyncOperation
        """
        url = f"{self.main_app_client.base_url}/employeeExperience/engagementAsyncOperations/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_learn_course_activities(
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

        Get learningCourseActivity

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
            employeeExperience.learningCourseActivity
        """
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities"
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

    def create_learning_activity(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        completedDateTime: Optional[str] = None,
        completionPercentage: Optional[float] = None,
        externalcourseActivityId: Optional[str] = None,
        learnerUserId: Optional[str] = None,
        learningContentId: Optional[str] = None,
        learningProviderId: Optional[str] = None,
        status: Optional[Any] = None,
    ) -> Any:
        """

        Create new navigation property to learningCourseActivities for employeeExperience

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            completedDateTime (string): Date and time when the assignment was completed. Optional.
            completionPercentage (number): The percentage completion value of the course activity. Optional.
            externalcourseActivityId (string): externalcourseActivityId
            learnerUserId (string): The user ID of the learner to whom the activity is assigned. Required.
            learningContentId (string): The ID of the learning content created in Viva Learning. Required.
            learningProviderId (string): The registration ID of the provider. Required.
            status (string): The status of the course activity. Possible values are: notStarted, inProgress, completed. Required.

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningCourseActivity
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "completedDateTime": completedDateTime,
            "completionPercentage": completionPercentage,
            "externalcourseActivityId": externalcourseActivityId,
            "learnerUserId": learnerUserId,
            "learningContentId": learningContentId,
            "learningProviderId": learningProviderId,
            "status": status,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def get_learn_course_activity_by_id(
        self,
        learningCourseActivity_id: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningCourseActivity

        Args:
            learningCourseActivity_id (string): learningCourseActivity-id
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningCourseActivity
        """
        if learningCourseActivity_id is None:
            raise ValueError("Missing required parameter 'learningCourseActivity-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities/{learningCourseActivity_id}"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def patch_learning_course_activity(
        self,
        learningCourseActivity_id: str,
        atodata_type: str,
        id: Optional[str] = None,
        completedDateTime: Optional[str] = None,
        completionPercentage: Optional[float] = None,
        externalcourseActivityId: Optional[str] = None,
        learnerUserId: Optional[str] = None,
        learningContentId: Optional[str] = None,
        learningProviderId: Optional[str] = None,
        status: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property learningCourseActivities in employeeExperience

        Args:
            learningCourseActivity_id (string): learningCourseActivity-id
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            completedDateTime (string): Date and time when the assignment was completed. Optional.
            completionPercentage (number): The percentage completion value of the course activity. Optional.
            externalcourseActivityId (string): externalcourseActivityId
            learnerUserId (string): The user ID of the learner to whom the activity is assigned. Required.
            learningContentId (string): The ID of the learning content created in Viva Learning. Required.
            learningProviderId (string): The registration ID of the provider. Required.
            status (string): The status of the course activity. Possible values are: notStarted, inProgress, completed. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningCourseActivity
        """
        if learningCourseActivity_id is None:
            raise ValueError("Missing required parameter 'learningCourseActivity-id'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "completedDateTime": completedDateTime,
            "completionPercentage": completionPercentage,
            "externalcourseActivityId": externalcourseActivityId,
            "learnerUserId": learnerUserId,
            "learningContentId": learningContentId,
            "learningProviderId": learningProviderId,
            "status": status,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities/{learningCourseActivity_id}"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_learning_activity(self, learningCourseActivity_id: str) -> Any:
        """

        Delete navigation property learningCourseActivities for employeeExperience

        Args:
            learningCourseActivity_id (string): learningCourseActivity-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningCourseActivity
        """
        if learningCourseActivity_id is None:
            raise ValueError("Missing required parameter 'learningCourseActivity-id'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities/{learningCourseActivity_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_learn_course_activity_by_ext_id(
        self,
        externalcourseActivityId: str,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """

        Get learningCourseActivity

        Args:
            externalcourseActivityId (string): externalcourseActivityId
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningCourseActivity
        """
        if externalcourseActivityId is None:
            raise ValueError("Missing required parameter 'externalcourseActivityId'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities(externalcourseActivityId='{externalcourseActivityId}')"
        query_params = {
            k: v for k, v in [("$select", select), ("$expand", expand)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def update_learning_activity_by_id(
        self,
        externalcourseActivityId: str,
        atodata_type: str,
        id: Optional[str] = None,
        completedDateTime: Optional[str] = None,
        completionPercentage: Optional[float] = None,
        externalcourseActivityId_body: Optional[str] = None,
        learnerUserId: Optional[str] = None,
        learningContentId: Optional[str] = None,
        learningProviderId: Optional[str] = None,
        status: Optional[Any] = None,
    ) -> Any:
        """

        Update the navigation property learningCourseActivities in employeeExperience

        Args:
            externalcourseActivityId (string): externalcourseActivityId
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            completedDateTime (string): Date and time when the assignment was completed. Optional.
            completionPercentage (number): The percentage completion value of the course activity. Optional.
            externalcourseActivityId_body (string): externalcourseActivityId
            learnerUserId (string): The user ID of the learner to whom the activity is assigned. Required.
            learningContentId (string): The ID of the learning content created in Viva Learning. Required.
            learningProviderId (string): The registration ID of the provider. Required.
            status (string): The status of the course activity. Possible values are: notStarted, inProgress, completed. Required.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningCourseActivity
        """
        if externalcourseActivityId is None:
            raise ValueError("Missing required parameter 'externalcourseActivityId'.")
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "completedDateTime": completedDateTime,
            "completionPercentage": completionPercentage,
            "externalcourseActivityId": externalcourseActivityId_body,
            "learnerUserId": learnerUserId,
            "learningContentId": learningContentId,
            "learningProviderId": learningProviderId,
            "status": status,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities(externalcourseActivityId='{externalcourseActivityId}')"
        query_params = {}
        response = self._patch(url, data=request_body_data, params=query_params)
        return self._handle_response(response)

    def delete_external_course_activity(self, externalcourseActivityId: str) -> Any:
        """

        Delete navigation property learningCourseActivities for employeeExperience

        Args:
            externalcourseActivityId (string): externalcourseActivityId

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningCourseActivity
        """
        if externalcourseActivityId is None:
            raise ValueError("Missing required parameter 'externalcourseActivityId'.")
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities(externalcourseActivityId='{externalcourseActivityId}')"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def get_learning_course_count(
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
            employeeExperience.learningCourseActivity
        """
        url = f"{self.main_app_client.base_url}/employeeExperience/learningCourseActivities/$count"
        query_params = {
            k: v for k, v in [("$search", search), ("$filter", filter)] if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def list_learning_providers(
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

        List learningProviders

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
            employeeExperience.learningProvider
        """
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders"
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

    def create_learning_provider(
        self,
        atodata_type: str,
        id: Optional[str] = None,
        displayName: Optional[str] = None,
        isCourseActivitySyncEnabled: Optional[bool] = None,
        loginWebUrl: Optional[str] = None,
        longLogoWebUrlForDarkTheme: Optional[str] = None,
        longLogoWebUrlForLightTheme: Optional[str] = None,
        squareLogoWebUrlForDarkTheme: Optional[str] = None,
        squareLogoWebUrlForLightTheme: Optional[str] = None,
        learningContents: Optional[List[Any]] = None,
        learningCourseActivities: Optional[List[Any]] = None,
    ) -> Any:
        """

        Create learningProvider

        Args:
            atodata_type (string): @odata.type
            id (string): The unique identifier for an entity. Read-only.
            displayName (string): The display name that appears in Viva Learning. Required.
            isCourseActivitySyncEnabled (boolean): Indicates whether a provider can ingest learning course activity records. The default value is false. Set to true to make learningCourseActivities available for this provider.
            loginWebUrl (string): Authentication URL to access the courses for the provider. Optional.
            longLogoWebUrlForDarkTheme (string): The long logo URL for the dark mode that needs to be a publicly accessible image. This image would be saved to the blob storage of Viva Learning for rendering within the Viva Learning app. Required.
            longLogoWebUrlForLightTheme (string): The long logo URL for the light mode that needs to be a publicly accessible image. This image would be saved to the blob storage of Viva Learning for rendering within the Viva Learning app. Required.
            squareLogoWebUrlForDarkTheme (string): The square logo URL for the dark mode that needs to be a publicly accessible image. This image would be saved to the blob storage of Viva Learning for rendering within the Viva Learning app. Required.
            squareLogoWebUrlForLightTheme (string): The square logo URL for the light mode that needs to be a publicly accessible image. This image would be saved to the blob storage of Viva Learning for rendering within the Viva Learning app. Required.
            learningContents (array): Learning catalog items for the provider.
            learningCourseActivities (array): learningCourseActivities

        Returns:
            Any: Created navigation property.

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            employeeExperience.learningProvider
        """
        request_body_data = None
        request_body_data = {
            "id": id,
            "@odata.type": atodata_type,
            "displayName": displayName,
            "isCourseActivitySyncEnabled": isCourseActivitySyncEnabled,
            "loginWebUrl": loginWebUrl,
            "longLogoWebUrlForDarkTheme": longLogoWebUrlForDarkTheme,
            "longLogoWebUrlForLightTheme": longLogoWebUrlForLightTheme,
            "squareLogoWebUrlForDarkTheme": squareLogoWebUrlForDarkTheme,
            "squareLogoWebUrlForLightTheme": squareLogoWebUrlForLightTheme,
            "learningContents": learningContents,
            "learningCourseActivities": learningCourseActivities,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.main_app_client.base_url}/employeeExperience/learningProviders"
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
            self.get_learning_provider,
            self.update_learning_provider,
            self.delete_learning_provider_by_id,
            self.list_learning_contents,
            self.create_learning_content,
            self.get_learning_contents_by_provider,
            self.update_learning_content,
            self.del_prov_learn_content_by_id,
            self.get_learning_content_by_external_id,
            self.patch_learning_content,
            self.del_prov_learn_content_by_ext_id,
            self.get_learning_content_count,
            self.list_learning_course_activities,
            self.create_learning_course_activity,
            self.get_prov_learn_course_activity,
            self.update_prov_course_activity_by_id,
            self.delete_learning_course_activity,
            self.get_provider_course_activity,
            self.update_prov_course_actvty_by_ext_id,
            self.delete_learning_activity_by_ext,
            self.count_learning_course_activities,
            self.count_learning_providers,
            self.list_communities,
            self.create_community_experience,
            self.get_community_details,
            self.update_community,
            self.delete_community_by_id,
            self.get_community_group,
            self.get_community_provisioning_errors,
            self.get_group_service_errors_count,
            self.list_community_owners,
            self.get_community_owners,
            self.get_mailbox_settings,
            self.update_community_mailbox_setting,
            self.get_community_owner_service_errors,
            self.get_service_provisioning_count,
            self.get_community_owner_by_user,
            self.count_community_owners,
            self.count_employee_communities,
            self.get_employee_engagement,
            self.create_engagement_operation,
            self.get_engagement_async_operation,
            self.update_engagement_async_operation,
            self.delete_engagement_async_operation,
            self.get_engagement_op_count_async,
            self.list_learn_course_activities,
            self.create_learning_activity,
            self.get_learn_course_activity_by_id,
            self.patch_learning_course_activity,
            self.delete_learning_activity,
            self.get_learn_course_activity_by_ext_id,
            self.update_learning_activity_by_id,
            self.delete_external_course_activity,
            self.get_learning_course_count,
            self.list_learning_providers,
            self.create_learning_provider,
        ]
