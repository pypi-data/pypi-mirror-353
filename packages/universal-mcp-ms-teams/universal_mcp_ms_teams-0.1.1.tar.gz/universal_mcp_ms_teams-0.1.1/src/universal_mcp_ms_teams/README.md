# MsTeamsApp MCP Server

An MCP Server for the MsTeamsApp API.

## 🛠️ Tool List

This is automatically generated from OpenAPI schema for the MsTeamsApp API.


| Tool | Description |
|------|-------------|
| `app_catalogs_list_teams_apps` | List teamsApp |
| `app_catalogs_create_teams_apps` | Publish teamsApp |
| `app_catalogs_get_teams_apps` | Get teamsApps from appCatalogs |
| `app_catalogs_update_teams_apps` | Update the navigation property teamsApps in appCatalogs |
| `app_catalogs_delete_teams_apps` | Delete teamsApp |
| `get_app_definitions` | Get appDefinitions from appCatalogs |
| `create_teams_app_definition` | Update teamsApp |
| `get_app_definition_by_id` | Get appDefinitions from appCatalogs |
| `update_app_definition` | Publish teamsApp |
| `delete_teams_app_definition` | Delete navigation property appDefinitions for appCatalogs |
| `get_teams_app_bot` | Get teamworkBot |
| `update_bot_definition` | Update the navigation property bot in appCatalogs |
| `delete_bot_definition` | Delete navigation property bot for appCatalogs |
| `count_teams_app_definitions` | Get the number of the resource |
| `teams_list_installed_apps` | List apps in team |
| `teams_create_installed_apps` | Add app to team |
| `teams_get_installed_apps` | Get installed app in team |
| `teams_update_installed_apps` | Update the navigation property installedApps in teams |
| `teams_delete_installed_apps` | Remove app from team |
| `upgrade_teams_app_installation` | Invoke action upgrade |
| `get_teams_app_details` | Get teamsApp from teams |
| `get_teams_app_definition` | Get teamsAppDefinition from teams |
| `count_installed_apps` | Get the number of the resource |
| `teams_team_list_team` | List teams |
| `teams_team_create_team` | Create team |
| `teams_team_get_team` | Get team |
| `teams_team_update_team` | Update team |
| `teams_team_delete_team` | Delete entity from teams |
| `teams_list_all_channels` | List allChannels |
| `teams_get_all_channels` | Get allChannels from teams |
| `count_team_channels` | Get the number of the resource |
| `teams_list_channels` | List channels |
| `teams_create_channels` | Create channel |
| `teams_get_channels` | Get channel |
| `teams_update_channels` | Patch channel |
| `teams_delete_channels` | Delete channel |
| `teams_channels_list_all_members` | List allMembers |
| `get_team_channel_members` | Create new navigation property to allMembers for teams |
| `teams_channels_get_all_members` | Get allMembers from teams |
| `update_member_details` | Update the navigation property allMembers in teams |
| `delete_conversation_member` | Delete navigation property allMembers for teams |
| `count_team_channel_members` | Get the number of the resource |
| `add_channel_member` | Invoke action add |
| `remove_team_channel_member` | Invoke action remove |
| `teams_channels_get_files_folder` | Get filesFolder |
| `get_files_folder_content` | Get content for the navigation property filesFolder from teams |
| `update_files_folder_content` | Update content for the navigation property filesFolder in teams |
| `delete_files_folder_content` | Delete content for the navigation property filesFolder in teams |
| `teams_channels_list_members` | List members of a channel |
| `teams_channels_create_members` | Add conversationMember |
| `teams_channels_get_members` | Get member of channel |
| `teams_channels_update_members` | Update conversationMember |
| `teams_channels_delete_members` | Remove member from channel |
| `get_team_channel_members_count` | Get the number of the resource |
| `add_channel_members_bulk` | Invoke action add |
| `remove_member_from_channel` | Invoke action remove |
| `teams_channels_list_messages` | List channel messages |
| `teams_channels_create_messages` | Send chatMessage in channel |
| `teams_channels_get_messages` | Get chatMessage in a channel or chat |
| `teams_channels_update_messages` | Update chatMessage |
| `teams_channels_delete_messages` | Delete navigation property messages for teams |
| `list_channel_msg_hosted_content` | List hostedContents |
| `add_hosted_content` | Create new navigation property to hostedContents for teams |
| `get_hosted_content_details` | Get hostedContents from teams |
| `update_hosted_content_details` | Update the navigation property hostedContents in teams |
| `del_ch_msg_hosted_content` | Delete navigation property hostedContents for teams |
| `get_channel_msg_hosted_content_val` | List hostedContents |
| `update_team_hosted_content_val` | Update media content for the navigation property hostedContents in teams |
| `delete_hosted_content_by_message_id` | Delete media content for the navigation property hostedContents in teams |
| `get_hosted_content_count` | Get the number of the resource |
| `set_reaction_to_message` | Invoke action setReaction |
| `soft_delete_message` | Invoke action softDelete |
| `undo_soft_delete_message` | Invoke action undoSoftDelete |
| `unset_reaction_to_message` | Invoke action unsetReaction |
| `list_channel_message_replies` | List replies |
| `create_channel_message_reply` | Send replies to a message in a channel |
| `get_replies_by_message_id` | Get chatMessage in a channel or chat |
| `update_reply_message` | Update the navigation property replies in teams |
| `delete_message_reply` | Delete navigation property replies for teams |
| `get_hosted_content_replies` | List hostedContents |
| `create_hosted_content_reply` | Create new navigation property to hostedContents for teams |
| `get_channel_reply_hosted_content` | Get hostedContents from teams |
| `patch_ch_reply_hosted_content` | Update the navigation property hostedContents in teams |
| `del_ch_msg_reply_hosted_content` | Delete navigation property hostedContents for teams |
| `get_ch_msg_reply_hosted_content_val` | List hostedContents |
| `update_msg_reply_hosted_content` | Update media content for the navigation property hostedContents in teams |
| `delete_hosted_content_value` | Delete media content for the navigation property hostedContents in teams |
| `count_ch_msg_reply_host_contents` | Get the number of the resource |
| `set_reaction_to_reply` | Invoke action setReaction |
| `soft_delete_reply` | Invoke action softDelete |
| `undo_soft_delete_reply` | Invoke action undoSoftDelete |
| `unset_reaction` | Invoke action unsetReaction |
| `count_replies` | Get the number of the resource |
| `get_chat_message_replies_delta` | Invoke function delta |
| `count_channel_messages` | Get the number of the resource |
| `get_team_channel_messages_delta` | Invoke function delta |
| `archive_team_channel` | Invoke action archive |
| `complete_team_channel_migration` | Invoke action completeMigration |
| `check_user_channel_access` | Invoke function doesUserHaveAccess |
| `provision_team_email` | Invoke action provisionEmail |
| `remove_team_channel_email` | Invoke action removeEmail |
| `unarchive_channel` | Invoke action unarchive |
| `list_channel_shared_teams` | List sharedWithChannelTeamInfo |
| `share_channel_with_team` | Create new navigation property to sharedWithTeams for teams |
| `get_shared_teams_channels_info` | Get sharedWithChannelTeamInfo |
| `update_shared_with_team_info` | Update the navigation property sharedWithTeams in teams |
| `delete_shared_team_channel` | Delete sharedWithChannelTeamInfo |
| `get_shared_channel_members` | List allowedMembers |
| `get_shared_team_members` | Get allowedMembers from teams |
| `count_allowed_members` | Get the number of the resource |
| `get_shared_channel_team_info` | Get team from teams |
| `get_shared_teams_count` | Get the number of the resource |
| `teams_channels_list_tabs` | List tabs in channel |
| `teams_channels_create_tabs` | Add tab to channel |
| `teams_channels_get_tabs` | Get tab |
| `teams_channels_update_tabs` | Update tab |
| `teams_channels_delete_tabs` | Delete tab from channel |
| `get_teams_app_tab` | Get teamsApp from teams |
| `get_team_channel_tabs_count` | Get the number of the resource |
| `teams_channels_get_count_a` | Get the number of the resource |
| `get_team_channel_messages` | Invoke function getAllMessages |
| `get_retained_messages_by_team_id` | Invoke function getAllRetainedMessages |
| `teams_get_group` | Get group from teams |
| `list_service_provisioning_errors` | Get serviceProvisioningErrors property value |
| `count_service_provisioning_errors` | Get the number of the resource |
| `teams_list_incoming_channels` | List incomingChannels |
| `teams_get_incoming_channels` | Get incomingChannels from teams |
| `count_team_incoming_channels` | Get the number of the resource |
| `teams_list_members` | List members of team |
| `teams_create_members` | Add member to team |
| `teams_get_members` | Get member of team |
| `teams_update_members` | Update member in team |
| `teams_delete_members` | Remove member from team |
| `teams_members_get_count_b` | Get the number of the resource |
| `teams_team_members_add` | Invoke action add |
| `teams_team_members_remove` | Invoke action remove |
| `teams_team_archive` | Invoke action archive |
| `teams_team_clone` | Invoke action clone |
| `teams_team_complete_migration` | Invoke action completeMigration |
| `send_team_notification` | Invoke action sendActivityNotification |
| `teams_team_unarchive` | Invoke action unarchive |
| `teams_list_operations` | Get operations from teams |
| `teams_create_operations` | Create new navigation property to operations for teams |
| `teams_get_operations` | Get operations from teams |
| `teams_update_operations` | Update the navigation property operations in teams |
| `teams_delete_operations` | Delete navigation property operations for teams |
| `teams_operations_get_count_af` | Get the number of the resource |
| `teams_list_permission_grants` | List permissionGrants of a team |
| `teams_create_permission_grants` | Create new navigation property to permissionGrants for teams |
| `teams_get_permission_grants` | Get permissionGrants from teams |
| `teams_update_permission_grants` | Update the navigation property permissionGrants in teams |
| `teams_delete_permission_grants` | Delete navigation property permissionGrants for teams |
| `count_team_permission_grants` | Get the number of the resource |
| `teams_get_photo` | Get profilePhoto |
| `teams_update_photo` | Update profilePhoto |
| `teams_get_photo_content` | Get profilePhoto |
| `teams_update_photo_content` | Update profilePhoto |
| `teams_delete_photo_content` | Delete media content for the navigation property photo in teams |
| `teams_get_primary_channel` | Get primaryChannel |
| `teams_update_primary_channel` | Update the navigation property primaryChannel in teams |
| `teams_delete_primary_channel` | Delete navigation property primaryChannel for teams |
| `list_team_primary_channel_members` | Get allMembers from teams |
| `add_team_primary_channel_members` | Create new navigation property to allMembers for teams |
| `get_team_primary_channel_members` | Get allMembers from teams |
| `update_primary_channel_members` | Update the navigation property allMembers in teams |
| `remove_conversation_member` | Delete navigation property allMembers for teams |
| `count_team_primary_channel_members` | Get the number of the resource |
| `add_team_members_bulk` | Invoke action add |
| `remove_primary_channel_member` | Invoke action remove |
| `get_files_folder` | Get filesFolder from teams |
| `get_team_primary_channel_content` | Get content for the navigation property filesFolder from teams |
| `upload_team_folder_content` | Update content for the navigation property filesFolder in teams |
| `delete_team_files_folder_content` | Delete content for the navigation property filesFolder in teams |
| `list_primary_channel_members` | Get members from teams |
| `add_primary_channel_member` | Create new navigation property to members for teams |
| `get_team_members` | Get members from teams |
| `update_team_member` | Update the navigation property members in teams |
| `delete_team_primary_channel_member` | Delete navigation property members for teams |
| `get_primary_channel_member_count` | Get the number of the resource |
| `add_team_primary_channel_member` | Invoke action add |
| `remove_team_member` | Invoke action remove |
| `list_team_primary_channel_messages` | Get messages from teams |
| `create_team_message` | Create new navigation property to messages for teams |
| `get_team_primary_channel_messages` | Get messages from teams |
| `update_primary_channel_message` | Update the navigation property messages in teams |
| `delete_message_by_id` | Delete navigation property messages for teams |
| `get_team_channel_msg_hosted` | Get hostedContents from teams |
| `upload_hosted_content` | Create new navigation property to hostedContents for teams |
| `read_hosted_content` | Get hostedContents from teams |
| `patch_pri_ch_hosted_content` | Update the navigation property hostedContents in teams |
| `del_pri_ch_msg_hosted_content` | Delete navigation property hostedContents for teams |
| `get_hosted_message_content_by_id` | Get media content for the navigation property hostedContents from teams |
| `put_pri_ch_hosted_content_val` | Update media content for the navigation property hostedContents in teams |
| `del_pri_ch_msg_host_content_val` | Delete media content for the navigation property hostedContents in teams |
| `get_hosted_contents_count` | Get the number of the resource |
| `set_reaction_to_chat_message` | Invoke action setReaction |
| `soft_delete_chat_message` | Invoke action softDelete |
| `restore_primary_channel_message` | Invoke action undoSoftDelete |
| `unset_reaction_message` | Invoke action unsetReaction |
| `list_replies_by_message_id` | Get replies from teams |
| `create_reply_to_chat_message` | Create new navigation property to replies for teams |
| `get_primary_channel_replies` | Get replies from teams |
| `update_primary_channel_reply` | Update the navigation property replies in teams |
| `delete_reply` | Delete navigation property replies for teams |
| `get_reply_contents` | Get hostedContents from teams |
| `create_team_reply_hosted_content` | Create new navigation property to hostedContents for teams |
| `get_pri_ch_reply_hosted_content` | Get hostedContents from teams |
| `patch_pri_ch_reply_hosted_content` | Update the navigation property hostedContents in teams |
| `del_pri_ch_reply_hosted_content` | Delete navigation property hostedContents for teams |
| `get_pri_ch_reply_host_content_val` | Get media content for the navigation property hostedContents from teams |
| `put_pri_ch_reply_hosted_content_val` | Update media content for the navigation property hostedContents in teams |
| `del_pri_ch_reply_host_cont_val` | Delete media content for the navigation property hostedContents in teams |
| `count_hosted_content_replies` | Get the number of the resource |
| `set_reaction_to_reply_message` | Invoke action setReaction |
| `delete_reply_message` | Invoke action softDelete |
| `undo_team_message_reply_delete` | Invoke action undoSoftDelete |
| `unset_team_message_reply_reaction` | Invoke action unsetReaction |
| `get_primary_channel_replies_count` | Get the number of the resource |
| `get_reply_delta` | Invoke function delta |
| `get_primary_channel_message_count` | Get the number of the resource |
| `get_primary_channel_messages_delta` | Invoke function delta |
| `archive_primary_channel` | Invoke action archive |
| `complete_team_migration` | Invoke action completeMigration |
| `has_primary_channel_access` | Invoke function doesUserHaveAccess |
| `provision_team_channel_email` | Invoke action provisionEmail |
| `remove_team_primary_channel_email` | Invoke action removeEmail |
| `unarchive_primary_channel` | Invoke action unarchive |
| `list_primary_channel_shared_teams` | Get sharedWithTeams from teams |
| `share_primary_channel_with_teams` | Create new navigation property to sharedWithTeams for teams |
| `get_shared_channel_info_by_id` | Get sharedWithTeams from teams |
| `update_shared_channel_team_info` | Update the navigation property sharedWithTeams in teams |
| `delete_shared_channel_team_info` | Delete navigation property sharedWithTeams for teams |
| `get_shared_members` | Get allowedMembers from teams |
| `get_team_channel_shared_member_by_id` | Get allowedMembers from teams |
| `get_shared_team_members_count` | Get the number of the resource |
| `get_shared_with_team_info` | Get team from teams |
| `get_shared_team_count` | Get the number of the resource |
| `teams_primary_channel_list_tabs` | Get tabs from teams |
| `create_team_tab` | Create new navigation property to tabs for teams |
| `teams_primary_channel_get_tabs` | Get tabs from teams |
| `update_team_tab` | Update the navigation property tabs in teams |
| `delete_primary_channel_tab` | Delete navigation property tabs for teams |
| `get_teams_app_by_tab_id` | Get teamsApp from teams |
| `get_team_primary_channel_tabs_count` | Get the number of the resource |
| `teams_get_schedule` | Get schedule |
| `teams_set_schedule` | Create or replace schedule |
| `teams_delete_schedule` | Delete navigation property schedule for teams |
| `teams_schedule_list_day_notes` | Get dayNotes from teams |
| `teams_schedule_create_day_notes` | Create new navigation property to dayNotes for teams |
| `teams_schedule_get_day_notes` | Get dayNotes from teams |
| `teams_schedule_update_day_notes` | Update the navigation property dayNotes in teams |
| `teams_schedule_delete_day_notes` | Delete navigation property dayNotes for teams |
| `get_day_notes_count` | Get the number of the resource |
| `teams_team_schedule_share` | Invoke action share |
| `get_team_shift_requests` | List offerShiftRequest |
| `offer_shift_requests` | Create offerShiftRequest |
| `get_team_schedule_offer_shifts` | Get offerShiftRequest |
| `patch_offer_shift_request` | Update the navigation property offerShiftRequests in teams |
| `delete_shift_offer_request` | Delete navigation property offerShiftRequests for teams |
| `count_shift_offer_requests` | Get the number of the resource |
| `get_open_shift_change_requests` | List openShiftChangeRequests |
| `create_open_shift_change_request` | Create openShiftChangeRequest |
| `get_open_shift_change_request` | Get openShiftChangeRequest |
| `update_open_shift_change_request` | Update the navigation property openShiftChangeRequests in teams |
| `delete_open_shift_change_request` | Delete navigation property openShiftChangeRequests for teams |
| `count_open_shift_change_requests` | Get the number of the resource |
| `teams_schedule_list_open_shifts` | List openShifts |
| `create_open_shifts` | Create openShift |
| `teams_schedule_get_open_shifts` | Get openShift |
| `update_open_shift` | Update openShift |
| `delete_open_shift_by_id` | Delete openShift |
| `count_open_shifts` | Get the number of the resource |
| `get_scheduling_groups` | List scheduleGroups |
| `create_scheduling_group` | Create schedulingGroup |
| `get_team_schedule_scheduling_group` | Get schedulingGroup |
| `update_scheduling_group` | Replace schedulingGroup |
| `delete_scheduling_group` | Delete schedulingGroup |
| `count_scheduling_groups` | Get the number of the resource |
| `teams_schedule_list_shifts` | List shifts |
| `teams_schedule_create_shifts` | Create shift |
| `teams_schedule_get_shifts` | Get shift |
| `teams_schedule_update_shifts` | Replace shift |
| `teams_schedule_delete_shifts` | Delete shift |
| `get_schedule_shifts_count_by_team_id` | Get the number of the resource |
| `get_swap_shift_change_requests` | List swapShiftsChangeRequest |
| `swap_shift_requests` | Create swapShiftsChangeRequest |
| `swap_shift_request_read` | Get swapShiftsChangeRequest |
| `update_swap_shift_request` | Update the navigation property swapShiftsChangeRequests in teams |
| `delete_swap_shifts_change_request` | Delete navigation property swapShiftsChangeRequests for teams |
| `count_swap_shift_requests` | Get the number of the resource |
| `teams_schedule_list_time_cards` | List timeCard |
| `teams_schedule_create_time_cards` | Create timeCard |
| `teams_schedule_get_time_cards` | Get timeCards from teams |
| `teams_schedule_update_time_cards` | Update the navigation property timeCards in teams |
| `teams_schedule_delete_time_cards` | Delete timeCard |
| `clock_out_time_card` | Invoke action clockOut |
| `confirm_time_card` | Invoke action confirm |
| `end_team_break` | Invoke action endBreak |
| `start_time_card_break` | Invoke action startBreak |
| `get_team_schedule_count` | Get the number of the resource |
| `clock_in_team_schedule` | Invoke action clockIn |
| `get_team_time_off_reasons` | List timeOffReasons |
| `create_time_off_reasons` | Create timeOffReason |
| `get_time_off_reason_by_id` | Get timeOffReason |
| `update_time_off_reason_by_id` | Replace timeOffReason |
| `delete_time_off_reason_by_id` | Delete timeOffReason |
| `get_team_time_off_reasons_count` | Get the number of the resource |
| `list_time_off_requests` | List timeOffRequest |
| `create_time_off_request` | Create timeOffRequest |
| `get_team_time_off_request_details` | Get timeOffRequest |
| `update_time_off_request` | Update the navigation property timeOffRequests in teams |
| `delete_team_time_off_request` | Delete timeOffRequest |
| `get_team_time_off_count` | Get the number of the resource |
| `teams_schedule_list_times_off` | List timesOff |
| `teams_schedule_create_times_off` | Create timeOff |
| `teams_schedule_get_times_off` | Get timeOff |
| `teams_schedule_update_times_off` | Replace timeOff |
| `teams_schedule_delete_times_off` | Delete timeOff |
| `get_team_schedule_times_off_count` | Get the number of the resource |
| `teams_list_tags` | List teamworkTags |
| `teams_create_tags` | Create teamworkTag |
| `teams_get_tags` | Get teamworkTag |
| `teams_update_tags` | Update teamworkTag |
| `teams_delete_tags` | Delete teamworkTag |
| `teams_tags_list_members` | List members in a teamworkTag |
| `teams_tags_create_members` | Create teamworkTagMember |
| `teams_tags_get_members` | Get teamworkTagMember |
| `teams_tags_update_members` | Update the navigation property members in teams |
| `teams_tags_delete_members` | Delete teamworkTagMember |
| `get_team_tag_member_count` | Get the number of the resource |
| `teams_tags_get_count_db` | Get the number of the resource |
| `teams_get_template` | Get template from teams |
| `teams_get_count_ff` | Get the number of the resource |
| `teams_get_all_messages` | Invoke function getAllMessages |
| `list_team_templates` | Get entities from teamsTemplates |
| `create_team_template` | Add new entity to teamsTemplates |
| `get_teams_template_by_id` | Get entity from teamsTemplates by key |
| `update_teams_template` | Update entity in teamsTemplates |
| `delete_team_template_by_id` | Delete entity from teamsTemplates |
| `teams_templates_get_count_ba` | Get the number of the resource |
| `chats_chat_list_chat` | List chats |
| `chats_chat_create_chat` | Create chat |
| `chats_chat_get_chat` | Get chat |
| `chats_chat_update_chat` | Update chat |
| `chats_chat_delete_chat` | Delete chat |
| `chats_list_installed_apps` | List apps in chat |
| `chats_create_installed_apps` | Add app to chat |
| `chats_get_installed_apps` | Get installed app in chat |
| `chats_update_installed_apps` | Update the navigation property installedApps in chats |
| `chats_delete_installed_apps` | Uninstall app in a chat |
| `upgrade_installed_app` | Invoke action upgrade |
| `get_teams_app` | Get teamsApp from chats |
| `get_installed_app_definition` | Get teamsAppDefinition from chats |
| `get_chat_apps_count` | Get the number of the resource |
| `chats_get_last_message_preview` | Get lastMessagePreview from chats |
| `chats_update_last_message_preview` | Update the navigation property lastMessagePreview in chats |
| `chats_delete_last_message_preview` | Delete navigation property lastMessagePreview for chats |
| `chats_list_members` | List conversationMembers |
| `chats_create_members` | Add member to a chat |
| `chats_get_members` | Get conversationMember in a chat |
| `chats_update_members` | Update the navigation property members in chats |
| `chats_delete_members` | Remove member from chat |
| `chats_members_get_count` | Get the number of the resource |
| `chats_chat_members_add` | Invoke action add |
| `chats_chat_members_remove` | Invoke action remove |
| `chats_list_messages` | List messages in a chat |
| `chats_create_messages` | Send message in a chat |
| `chats_get_messages` | Get chatMessage in a channel or chat |
| `chats_update_messages` | Update the navigation property messages in chats |
| `chats_delete_messages` | Delete navigation property messages for chats |
| `get_hosted_content_by_message_id` | List hostedContents |
| `create_hosted_content` | Create new navigation property to hostedContents for chats |
| `get_chat_msg_hosted_content` | Get chatMessageHostedContent |
| `update_chat_message_content` | Update the navigation property hostedContents in chats |
| `del_chat_msg_hosted_content` | Delete navigation property hostedContents for chats |
| `get_chat_msg_hosted_content_val` | List hostedContents |
| `update_chat_hosted_content_val` | Update media content for the navigation property hostedContents in chats |
| `del_chat_msg_host_content_val` | Delete media content for the navigation property hostedContents in chats |
| `count_chat_msg_hosted_contents` | Get the number of the resource |
| `set_chat_message_reaction` | Invoke action setReaction |
| `delete_message_softly` | Invoke action softDelete |
| `restore_soft_deleted_message` | Invoke action undoSoftDelete |
| `unset_message_reaction` | Invoke action unsetReaction |
| `chats_messages_list_replies` | Get replies from chats |
| `chats_messages_create_replies` | Create new navigation property to replies for chats |
| `chats_messages_get_replies` | Get replies from chats |
| `chats_messages_update_replies` | Update the navigation property replies in chats |
| `chats_messages_delete_replies` | Delete navigation property replies for chats |
| `get_hosted_contents` | Get hostedContents from chats |
| `add_chat_message_hosted_content` | Create new navigation property to hostedContents for chats |
| `get_chat_message_hosted_content` | Get hostedContents from chats |
| `patch_chat_reply_hosted_content` | Update the navigation property hostedContents in chats |
| `del_chat_reply_hosted_content` | Delete navigation property hostedContents for chats |
| `get_chat_hosted_content_value` | Get media content for the navigation property hostedContents from chats |
| `update_chat_rply_hosted_content_val` | Update media content for the navigation property hostedContents in chats |
| `del_chat_reply_host_content_val` | Delete media content for the navigation property hostedContents in chats |
| `count_chat_message_replies_content` | Get the number of the resource |
| `set_chat_message_reply_reaction` | Invoke action setReaction |
| `soft_delete_message_reply` | Invoke action softDelete |
| `undo_soft_delete_chat_message_reply` | Invoke action undoSoftDelete |
| `unset_chat_message_reaction` | Invoke action unsetReaction |
| `get_chat_replies_count` | Get the number of the resource |
| `get_chat_replies_delta` | Invoke function delta |
| `chats_messages_get_count_dde` | Get the number of the resource |
| `chats_chat_messages_delta` | Invoke function delta |
| `chats_chat_hide_for_user` | Invoke action hideForUser |
| `chats_chat_mark_chat_read_for_user` | Invoke action markChatReadForUser |
| `mark_chat_unread_for_user` | Invoke action markChatUnreadForUser |
| `send_chat_notification` | Invoke action sendActivityNotification |
| `chats_chat_unhide_for_user` | Invoke action unhideForUser |
| `chats_list_permission_grants` | List permissionGrants of a chat |
| `chats_create_permission_grants` | Create new navigation property to permissionGrants for chats |
| `chats_get_permission_grants` | Get permissionGrants from chats |
| `chats_update_permission_grants` | Update the navigation property permissionGrants in chats |
| `chats_delete_permission_grants` | Delete navigation property permissionGrants for chats |
| `get_chat_permission_count` | Get the number of the resource |
| `chats_list_pinned_messages` | List pinnedChatMessages in a chat |
| `chats_create_pinned_messages` | Pin a message in a chat |
| `chats_get_pinned_messages` | Get pinnedMessages from chats |
| `chats_update_pinned_messages` | Update the navigation property pinnedMessages in chats |
| `chats_delete_pinned_messages` | Unpin a message from a chat |
| `get_pinned_chat_message_detail` | Get message from chats |
| `get_chat_pinned_messages_count` | Get the number of the resource |
| `chats_list_tabs` | List tabs in chat |
| `chats_create_tabs` | Add tab to chat |
| `chats_get_tabs` | Get tab in chat |
| `chats_update_tabs` | Update tab in chat |
| `chats_delete_tabs` | Delete tab from chat |
| `chats_tabs_get_teams_app` | Get teamsApp from chats |
| `chats_tabs_get_count_b` | Get the number of the resource |
| `chats_get_count_c` | Get the number of the resource |
| `chats_get_all_messages` | Invoke function getAllMessages |
| `chats_get_all_retained_messages` | Invoke function getAllRetainedMessages |
| `me_list_online_meetings` | Get onlineMeeting |
| `me_create_online_meetings` | Create onlineMeeting |
| `me_get_online_meetings` | Get onlineMeeting |
| `me_update_online_meetings` | Update onlineMeeting |
| `me_delete_online_meetings` | Delete onlineMeeting |
| `get_meeting_attendance_reports` | List meetingAttendanceReports |
| `generate_attendance_report` | Create new navigation property to attendanceReports for me |
| `get_meeting_attendance_report` | Get meetingAttendanceReport |
| `update_meeting_attendance_report` | Update the navigation property attendanceReports in me |
| `delete_attendance_report` | Delete navigation property attendanceReports for me |
| `list_my_meeting_att_records` | List attendanceRecords |
| `create_attendance_record` | Create new navigation property to attendanceRecords for me |
| `get_attendance_record` | Get attendanceRecords from me |
| `update_attendance_record` | Update the navigation property attendanceRecords in me |
| `deletemy_attendance_record` | Delete navigation property attendanceRecords for me |
| `get_attendance_count` | Get the number of the resource |
| `get_online_meeting_attend_count` | Get the number of the resource |
| `get_attendee_report` | Get onlineMeeting |
| `update_attendee_report` | Update attendeeReport for the navigation property onlineMeetings in me |
| `delete_attendee_report` | Delete attendeeReport for the navigation property onlineMeetings in me |
| `get_virtual_appointment_join_url` | Invoke function getVirtualAppointmentJoinWebUrl |
| `send_reminder_sms` | Invoke action sendVirtualAppointmentReminderSms |
| `send_virtual_appointment_sms` | Invoke action sendVirtualAppointmentSms |
| `get_online_meeting_recordings` | Get callRecording |
| `create_recording` | Create new navigation property to recordings for me |
| `get_online_meeting_recording` | Get recordings from me |
| `update_call_recording_by_id` | Update the navigation property recordings in me |
| `delete_call_recording` | Delete navigation property recordings for me |
| `get_call_recording_content_by_id` | Get content for the navigation property recordings from me |
| `update_recording_content` | Update content for the navigation property recordings in me |
| `delete_recording_content` | Delete content for the navigation property recordings in me |
| `count_online_meeting_recordings` | Get the number of the resource |
| `get_my_meeting_recordings_delta` | Invoke function delta |
| `get_online_meeting_transcripts` | Get callTranscript |
| `create_transcript_me` | Create new navigation property to transcripts for me |
| `get_call_transcript_by_id` | Get transcripts from me |
| `update_transcript` | Update the navigation property transcripts in me |
| `delete_transcript_by_id` | Delete navigation property transcripts for me |
| `get_call_transcript_content_by_id` | Get content for the navigation property transcripts from me |
| `update_transcript_content` | Update content for the navigation property transcripts in me |
| `delete_transcript_content` | Delete content for the navigation property transcripts in me |
| `get_transcript_metadata` | Get metadataContent for the navigation property transcripts from me |
| `update_my_transcript_metadata` | Update metadataContent for the navigation property transcripts in me |
| `delete_transcript_metadata` | Delete metadataContent for the navigation property transcripts in me |
| `count_online_meeting_transcripts` | Get the number of the resource |
| `get_transcripts_delta` | Invoke function delta |
| `count_online_meetings` | Get the number of the resource |
| `me_online_meetings_create_or_get` | Invoke action createOrGet |
| `list_all_meeting_recordings` | Invoke function getAllRecordings |
| `get_meeting_transcripts` | Invoke function getAllTranscripts |
| `list_my_learning_activities` | Get learningCourseActivities from me |
| `get_my_learning_course_activity` | Get learningCourseActivities from me |
| `get_my_learning_activity_by_ext_id` | Get learningCourseActivities from me |
| `get_learning_course_activity_count` | Get the number of the resource |
| `list_communications` | Get communications |
| `patch_communication` | Update communications |
| `communications_list_call_records` | List callRecords |
| `create_call_record` | Create new navigation property to callRecords for communications |
| `communications_get_call_records` | Get callRecord |
| `update_call_record` | Update the navigation property callRecords in communications |
| `delete_call_record_by_id` | Delete navigation property callRecords for communications |
| `get_call_record_organizer_v` | Get organizer_v2 from communications |
| `update_call_record_organizer_v` | Update the navigation property organizer_v2 in communications |
| `delete_call_record_organizer` | Delete navigation property organizer_v2 for communications |
| `get_call_record_participants_v` | List participants_v2 |
| `add_call_record_participants_v` | Create new navigation property to participants_v2 for communications |
| `get_participant_by_id_v` | Get participants_v2 from communications |
| `update_call_participant_v` | Update the navigation property participants_v2 in communications |
| `delete_participant_by_id` | Delete navigation property participants_v2 for communications |
| `get_call_record_participants_count` | Get the number of the resource |
| `get_call_record_sessions` | List sessions |
| `create_call_record_session` | Create new navigation property to sessions for communications |
| `get_call_session_by_id` | Get sessions from communications |
| `update_call_session` | Update the navigation property sessions in communications |
| `delete_call_session` | Delete navigation property sessions for communications |
| `get_call_segments` | Get segments from communications |
| `create_segment` | Create new navigation property to segments for communications |
| `get_call_segment` | Get segments from communications |
| `update_call_record_segment` | Update the navigation property segments in communications |
| `delete_segment_by_id` | Delete navigation property segments for communications |
| `count_call_segments` | Get the number of the resource |
| `count_call_record_sessions` | Get the number of the resource |
| `get_call_records_count` | Get the number of the resource |
| `get_direct_routing_calls` | Invoke function getDirectRoutingCalls |
| `get_pstn_calls` | Invoke function getPstnCalls |
| `communications_list_calls` | Get call |
| `communications_create_calls` | Create call |
| `communications_get_calls` | Get call |
| `communications_update_calls` | Update the navigation property calls in communications |
| `communications_delete_calls` | Delete call |
| `get_audio_routing_groups` | List audioRoutingGroups |
| `add_audio_routing_group` | Create audioRoutingGroup |
| `get_audio_routing_group_details` | Get audioRoutingGroup |
| `update_call_audio_routing_group` | Update audioRoutingGroup |
| `delete_audio_routing_group` | Delete audioRoutingGroup |
| `get_audio_routing_groups_count` | Get the number of the resource |
| `get_content_sharing_sessions` | List contentSharingSessions |
| `create_content_sharing_session` | Create new navigation property to contentSharingSessions for communications |
| `get_call_content_sharing_session` | Get contentSharingSession |
| `update_content_sharing_session` | Update the navigation property contentSharingSessions in communications |
| `delete_content_sharing_session` | Delete navigation property contentSharingSessions for communications |
| `count_call_content_sessions` | Get the number of the resource |
| `add_large_gallery_view` | Invoke action addLargeGalleryView |
| `answer_call_by_id` | Invoke action answer |
| `cancel_media_processing_by_call_id` | Invoke action cancelMediaProcessing |
| `change_screen_sharing_role` | Invoke action changeScreenSharingRole |
| `keep_call_alive` | Invoke action keepAlive |
| `communications_calls_call_mute` | Invoke action mute |
| `play_call_prompt` | Invoke action playPrompt |
| `record_call_response` | Invoke action recordResponse |
| `redirect_call_by_id` | Invoke action redirect |
| `reject_call_by_id` | Invoke action reject |
| `send_dtmf_tones_to_call` | Invoke action sendDtmfTones |
| `subscribe_to_call_tone` | Invoke action subscribeToTone |
| `transfer_call_by_id` | Invoke action transfer |
| `unmute_call` | Invoke action unmute |
| `update_call_recording_status` | Invoke action updateRecordingStatus |
| `get_call_operations` | Get addLargeGalleryViewOperation |
| `create_call_operation` | Create new navigation property to operations for communications |
| `get_comms_operation_details` | Get addLargeGalleryViewOperation |
| `patch_call_operation` | Update the navigation property operations in communications |
| `delete_comms_operation` | Delete navigation property operations for communications |
| `count_call_operations` | Get the number of the resource |
| `get_call_participants` | List participants |
| `add_call_participant` | Create new navigation property to participants for communications |
| `get_call_participant` | Get participant |
| `update_call_participant` | Update the navigation property participants in communications |
| `delete_participant_from_call` | Delete participant |
| `mute_participant` | Invoke action mute |
| `start_hold_music_for_participant` | Invoke action startHoldMusic |
| `stop_hold_music_for_participant` | Invoke action stopHoldMusic |
| `get_call_participants_count` | Get the number of the resource |
| `invite_call_participant` | Invoke action invite |
| `get_calls_count` | Get the number of the resource |
| `log_teleconference_device_quality` | Invoke action logTeleconferenceDeviceQuality |
| `get_presences_by_user` | Invoke action getPresencesByUserId |
| `list_online_meetings` | Get onlineMeeting |
| `create_online_meeting` | Create new navigation property to onlineMeetings for communications |
| `get_online_meeting_details` | Get onlineMeetings from communications |
| `update_online_meeting` | Update the navigation property onlineMeetings in communications |
| `delete_online_meeting_by_id` | Delete navigation property onlineMeetings for communications |
| `get_attendance_report` | Get attendanceReports from communications |
| `create_meeting_attendance_report` | Create new navigation property to attendanceReports for communications |
| `get_attendance_report_details` | Get attendanceReports from communications |
| `update_attendance_report` | Update the navigation property attendanceReports in communications |
| `delete_meeting_attendance_report` | Delete navigation property attendanceReports for communications |
| `list_comm_meeting_att_records` | Get attendanceRecords from communications |
| `add_attendance_record` | Create new navigation property to attendanceRecords for communications |
| `get_attendance_record_details` | Get attendanceRecords from communications |
| `update_attendance_record_by_id` | Update the navigation property attendanceRecords in communications |
| `deletecomm_attendance_record` | Delete navigation property attendanceRecords for communications |
| `get_attendance_records_count` | Get the number of the resource |
| `get_meeting_attendance_count` | Get the number of the resource |
| `get_attendee_report_by_meeting_id` | Get attendeeReport for the navigation property onlineMeetings from communications |
| `upload_attendee_report_stream` | Update attendeeReport for the navigation property onlineMeetings in communications |
| `delete_comm_online_mtg_att_report` | Delete attendeeReport for the navigation property onlineMeetings in communications |
| `get_virtual_join_url` | Invoke function getVirtualAppointmentJoinWebUrl |
| `send_virtual_meeting_reminder_sms` | Invoke action sendVirtualAppointmentReminderSms |
| `send_online_meeting_sms` | Invoke action sendVirtualAppointmentSms |
| `list_meeting_recordings` | Get recordings from communications |
| `start_recording` | Create new navigation property to recordings for communications |
| `get_recording` | Get recordings from communications |
| `update_meeting_recording` | Update the navigation property recordings in communications |
| `delete_call_recording_by_id` | Delete navigation property recordings for communications |
| `get_meeting_recording_content` | Get content for the navigation property recordings from communications |
| `upload_recording_content` | Update content for the navigation property recordings in communications |
| `delete_call_recording_content_by_id` | Delete content for the navigation property recordings in communications |
| `count_recordings` | Get the number of the resource |
| `get_comm_meeting_recordings_delta` | Invoke function delta |
| `get_online_meeting_transcript` | Get transcripts from communications |
| `create_transcript_comm` | Create new navigation property to transcripts for communications |
| `get_transcript_data` | Get transcripts from communications |
| `patch_transcript` | Update the navigation property transcripts in communications |
| `delete_transcript` | Delete navigation property transcripts for communications |
| `get_transcript_content_by_id` | Get content for the navigation property transcripts from communications |
| `update_call_transcript_content` | Update content for the navigation property transcripts in communications |
| `delete_transcript_content_by_id` | Delete content for the navigation property transcripts in communications |
| `get_metadata_content` | Get metadataContent for the navigation property transcripts from communications |
| `update_comm_transcript_metadata` | Update metadataContent for the navigation property transcripts in communications |
| `delete_metadata_content` | Delete metadataContent for the navigation property transcripts in communications |
| `count_online_meeting_transcript` | Get the number of the resource |
| `get_meeting_transcripts_delta` | Invoke function delta |
| `get_online_meetings_count` | Get the number of the resource |
| `create_or_get_online_meeting` | Invoke action createOrGet |
| `get_recordings_by_organizer` | Invoke function getAllRecordings |
| `get_all_meeting_transcripts` | Invoke function getAllTranscripts |
| `communications_list_presences` | Get presence |
| `communications_create_presences` | Create new navigation property to presences for communications |
| `communications_get_presences` | Get presence |
| `communications_update_presences` | Update the navigation property presences in communications |
| `communications_delete_presences` | Delete navigation property presences for communications |
| `clear_presence_by_id` | Invoke action clearPresence |
| `clear_user_presence` | Invoke action clearUserPreferredPresence |
| `set_presence_by_id` | Invoke action setPresence |
| `set_presence_status_message` | Invoke action setStatusMessage |
| `set_preferred_presence` | Invoke action setUserPreferredPresence |
| `count_communications_presences` | Get the number of the resource |
| `get_learning_provider` | Get learningProvider |
| `update_learning_provider` | Update learningProvider |
| `delete_learning_provider_by_id` | Delete learningProvider |
| `list_learning_contents` | List learningContents |
| `create_learning_content` | Create new navigation property to learningContents for employeeExperience |
| `get_learning_contents_by_provider` | Get learningContent |
| `update_learning_content` | Update the navigation property learningContents in employeeExperience |
| `del_prov_learn_content_by_id` | Delete learningContent |
| `get_learning_content_by_external_id` | Get learningContent |
| `patch_learning_content` | Update the navigation property learningContents in employeeExperience |
| `del_prov_learn_content_by_ext_id` | Delete learningContent |
| `get_learning_content_count` | Get the number of the resource |
| `list_learning_course_activities` | Get learningCourseActivity |
| `create_learning_course_activity` | Create learningCourseActivity |
| `get_prov_learn_course_activity` | Get learningCourseActivities from employeeExperience |
| `update_prov_course_activity_by_id` | Update learningCourseActivity |
| `delete_learning_course_activity` | Delete learningCourseActivity |
| `get_provider_course_activity` | Get learningCourseActivities from employeeExperience |
| `update_prov_course_actvty_by_ext_id` | Update learningCourseActivity |
| `delete_learning_activity_by_ext` | Delete learningCourseActivity |
| `count_learning_course_activities` | Get the number of the resource |
| `count_learning_providers` | Get the number of the resource |
| `list_communities` | List communities |
| `create_community_experience` | Create community |
| `get_community_details` | Get community |
| `update_community` | Update community |
| `delete_community_by_id` | Delete community |
| `get_community_group` | Get group from employeeExperience |
| `get_community_provisioning_errors` | Get serviceProvisioningErrors property value |
| `get_group_service_errors_count` | Get the number of the resource |
| `list_community_owners` | Get owners from employeeExperience |
| `get_community_owners` | Get owners from employeeExperience |
| `get_mailbox_settings` | Get mailboxSettings property value |
| `update_community_mailbox_setting` | Update property mailboxSettings value. |
| `get_community_owner_service_errors` | Get serviceProvisioningErrors property value |
| `get_service_provisioning_count` | Get the number of the resource |
| `get_community_owner_by_user` | Get owners from employeeExperience |
| `count_community_owners` | Get the number of the resource |
| `count_employee_communities` | Get the number of the resource |
| `get_employee_engagement` | Get engagementAsyncOperation |
| `create_engagement_operation` | Create new navigation property to engagementAsyncOperations for employeeExperience |
| `get_engagement_async_operation` | Get engagementAsyncOperation |
| `update_engagement_async_operation` | Update the navigation property engagementAsyncOperations in employeeExperience |
| `delete_engagement_async_operation` | Delete navigation property engagementAsyncOperations for employeeExperience |
| `get_engagement_op_count_async` | Get the number of the resource |
| `list_learn_course_activities` | Get learningCourseActivity |
| `create_learning_activity` | Create new navigation property to learningCourseActivities for employeeExperience |
| `get_learn_course_activity_by_id` | Get learningCourseActivity |
| `patch_learning_course_activity` | Update the navigation property learningCourseActivities in employeeExperience |
| `delete_learning_activity` | Delete navigation property learningCourseActivities for employeeExperience |
| `get_learn_course_activity_by_ext_id` | Get learningCourseActivity |
| `update_learning_activity_by_id` | Update the navigation property learningCourseActivities in employeeExperience |
| `delete_external_course_activity` | Delete navigation property learningCourseActivities for employeeExperience |
| `get_learning_course_count` | Get the number of the resource |
| `list_learning_providers` | List learningProviders |
| `create_learning_provider` | Create learningProvider |
| `copilot_get_users` | Get users from copilot |
| `copilot_update_users` | Update the navigation property users in copilot |
| `copilot_delete_users` | Delete navigation property users for copilot |
| `get_interaction_history` | Get interactionHistory from copilot |
| `update_interaction_history` | Update the navigation property interactionHistory in copilot |
| `delete_interaction_history` | Delete navigation property interactionHistory for copilot |
| `list_enterprise_user_interactions` | Invoke function getAllEnterpriseInteractions |
| `copilot_users_get_count_ed` | Get the number of the resource |
| `list_workforce_integrations` | List workforceIntegrations |
| `create_workforce_integration` | Create workforceIntegration |
| `get_workforce_integration` | Get workforceIntegration |
| `update_workforce_integration` | Update workforceIntegration |
| `delete_workforce_integration_by_id` | Delete workforceIntegration |
| `get_workforce_integration_count` | Get the number of the resource |
| `list_installed_apps_by_user` | List apps installed for user |
| `install_app_for_user` | Install app for user |
| `get_user_teamwork_app_installation` | Get installed app for user |
| `patch_user_teamwork_app` | Update the navigation property installedApps in users |
| `delete_installed_app` | Uninstall app for user |
| `users_get_teamwork` | Get userTeamwork |
| `users_update_teamwork` | Update the navigation property teamwork in users |
| `users_delete_teamwork` | Delete navigation property teamwork for users |
| `get_associated_teams` | Get associatedTeams from users |
| `associate_team_to_user` | Create new navigation property to associatedTeams for users |
| `get_associated_teams_by_user` | Get associatedTeams from users |
| `update_associated_team_info` | Update the navigation property associatedTeams in users |
| `delete_associated_team` | Delete navigation property associatedTeams for users |
| `get_associated_team` | Get team from users |
| `get_associated_teams_count` | Get the number of the resource |
| `get_chat_app_installation` | Get chat between user and teamsApp |
| `get_installed_teams_app` | Get teamsApp from users |
| `get_installed_app_details` | Get teamsAppDefinition from users |
| `get_installed_apps_count` | Get the number of the resource |
| `send_user_activity_notification` | Invoke action sendActivityNotification |
