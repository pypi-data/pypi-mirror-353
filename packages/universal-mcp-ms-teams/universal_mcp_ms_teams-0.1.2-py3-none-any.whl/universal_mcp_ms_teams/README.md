# MsTeamsApp MCP Server

An MCP Server for the MsTeamsApp API.

## 🛠️ Tool List

This is automatically generated from OpenAPI schema for the MsTeamsApp API.


| Tool | Description |
|------|-------------|
| `list_teams_apps` | List teamsApp |
| `publish_teams_app` | Publish teamsApp |
| `get_teams_apps_from_catalogs` | Get teamsApps from appCatalogs |
| `update_app_catalog_teams_app_by_id` | Update the navigation property teamsApps in appCatalogs |
| `delete_teams_app` | Delete teamsApp |
| `get_app_definitions` | Get appDefinitions from appCatalogs |
| `create_teams_app_definition` | Update teamsApp |
| `get_app_definition_by_id` | Get appDefinitions from appCatalogs |
| `update_app_definition` | Publish teamsApp |
| `delete_teams_app_definition` | Delete navigation property appDefinitions for appCatalogs |
| `get_teams_app_bot` | Get teamworkBot |
| `update_bot_definition` | Update the navigation property bot in appCatalogs |
| `delete_bot_definition` | Delete navigation property bot for appCatalogs |
| `count_teams_app_definitions` | Get the number of the resource |
| `get_app_catalog_count` | Get the number of the resource |
| `list_chats` | List chats |
| `create_chat_operation` | Create chat |
| `get_chat` | Get chat |
| `update_chat_details` | Update chat |
| `delete_chat_by_id` | Delete chat |
| `list_chat_apps` | List apps in chat |
| `add_app_to_chat` | Add app to chat |
| `get_installed_app_in_chat_by_teams_ap` | Get installed app in chat |
| `update_chat_installed_apps` | Update the navigation property installedApps in chats |
| `uninstall_app_in_chat` | Uninstall app in a chat |
| `upgrade_teams_app_installation` | Invoke action upgrade |
| `get_teams_app_from_chat` | Get teamsApp from chats |
| `get_installed_app_definition` | Get teamsAppDefinition from chats |
| `get_chat_installed_app_total` | Get the number of the resource |
| `get_chat_last_preview` | Get lastMessagePreview from chats |
| `patch_chat_last_message_preview` | Update the navigation property lastMessagePreview in chats |
| `delete_chat_last_message_preview` | Delete navigation property lastMessagePreview for chats |
| `list_chat_members` | List conversationMembers |
| `add_member_to_chat` | Add member to a chat |
| `get_conversation_member_by_chat_and` | Get conversationMember |
| `update_chat_member` | Update the navigation property members in chats |
| `remove_conversation_member_from_ch` | Remove member from chat |
| `get_chat_member_number` | Get the number of the resource |
| `add_chat_member` | Invoke action add |
| `remove_chat_member` | Invoke action remove |
| `list_chat_messages` | List messages in a chat |
| `post_chat_message` | Send chatMessage in a channel or a chat |
| `get_chat_message_detail` | Get chatMessage in a channel or chat |
| `update_chat_messages` | Update the navigation property messages in chats |
| `delete_chat_messages` | Delete navigation property messages for chats |
| `list_hosted_contents` | List hostedContents |
| `create_chat_message_hosted_content` | Create new navigation property to hostedContents for chats |
| `get_chat_message_content` | Get chatMessageHostedContent |
| `update_chat_message_content` | Update the navigation property hostedContents in chats |
| `del_chat_msg_hosted_content` | Delete navigation property hostedContents for chats |
| `get_chat_msg_hosted_content_val` | List hostedContents |
| `update_chat_hosted_content_val` | Update media content for the navigation property hostedContents in chats |
| `del_chat_msg_host_content_val` | Delete media content for the navigation property hostedContents in chats |
| `count_chat_msg_hosted_contents` | Get the number of the resource |
| `set_chat_reaction` | Invoke action setReaction |
| `soft_delete_chat_message_by_id` | Invoke action softDelete |
| `undo_soft_delete_message` | Invoke action undoSoftDelete |
| `unset_reaction_on_chat_message` | Invoke action unsetReaction |
| `read_chat_replies` | Get replies from chats |
| `create_chat_reply` | Create new navigation property to replies for chats |
| `get_chat_replies` | Get replies from chats |
| `update_chat_replies` | Update the navigation property replies in chats |
| `delete_chat_reply` | Delete navigation property replies for chats |
| `get_hosted_contents` | Get hostedContents from chats |
| `add_chat_message_hosted_content` | Create new navigation property to hostedContents for chats |
| `get_chat_message_hosted_content` | Get hostedContents from chats |
| `patch_chat_reply_hosted_content` | Update the navigation property hostedContents in chats |
| `del_chat_reply_hosted_content` | Delete navigation property hostedContents for chats |
| `get_chat_hosted_content_value` | Get media content for the navigation property hostedContents from chats |
| `update_chat_rply_hosted_content_val` | Update media content for the navigation property hostedContents in chats |
| `del_chat_reply_host_content_val` | Delete media content for the navigation property hostedContents in chats |
| `count_chat_message_replies_content` | Get the number of the resource |
| `set_chat_reply_reaction` | Invoke action setReaction |
| `soft_delete_chat_reply` | Invoke action softDelete |
| `undo_soft_delete_reply` | Invoke action undoSoftDelete |
| `unset_chat_message_reply_reaction` | Invoke action unsetReaction |
| `get_chat_message_reply_count` | Get the number of the resource |
| `chat_message_reply_delta_invoke` | Invoke function delta |
| `get_chat_messages_count` | Get the number of the resource |
| `get_chat_message_delta` | Invoke function delta |
| `hide_for_user_action` | Invoke action hideForUser |
| `mark_chat_read_for_user_action` | Invoke action markChatReadForUser |
| `mark_chat_unread` | Invoke action markChatUnreadForUser |
| `send_activity_notice` | Invoke action sendActivityNotification |
| `unhide_for_user_chat` | Invoke action unhideForUser |
| `list_chat_permission_grants` | List permissionGrants of a chat |
| `create_chat_permission_grant` | Create new navigation property to permissionGrants for chats |
| `get_chat_permission_grants` | Get permissionGrants from chats |
| `update_permission_grants_in_chat` | Update the navigation property permissionGrants in chats |
| `delete_chat_permission_grants` | Delete navigation property permissionGrants for chats |
| `get_chat_permission_grant_count` | Get the number of the resource |
| `get_pinned_chat_messages` | List pinnedChatMessages in a chat |
| `pin_chat_message` | Pin a message in a chat |
| `get_chat_pinned_message_by_id` | Get pinnedMessages from chats |
| `update_pinned_messages_in_chat` | Update the navigation property pinnedMessages in chats |
| `unpin_message_from_chat` | Unpin a message from a chat |
| `get_pinned_chat_message` | Get message from chats |
| `get_chat_pinned_messages_count` | Get the number of the resource |
| `list_chat_tabs` | List tabs in chat |
| `add_chat_tab` | Add tab to chat |
| `get_chat_tab` | Get tab in chat |
| `update_chat_tab` | Update tab in chat |
| `delete_chat_tab` | Delete tab from chat |
| `get_chat_teams_app` | Get teamsApp from chats |
| `get_chat_tab_count` | Get the number of the resource |
| `get_chat_count` | Get the number of the resource |
| `get_all_chat_messages` | Invoke function getAllMessages |
| `get_retained_messages_list` | Invoke function getAllRetainedMessages |
| `get_group_team` | Get team from groups |
| `create_team_from_group` | Create team from group |
| `delete_group_team` | Delete navigation property team for groups |
| `fetch_groups_team_all_channels` | Get allChannels from groups |
| `get_group_team_all_channels` | Get allChannels from groups |
| `get_group_team_channels_count` | Get the number of the resource |
| `get_group_team_channels` | Get channels from groups |
| `create_group_channel` | Create new navigation property to channels for groups |
| `get_group_channels` | Get channels from groups |
| `update_group_channels` | Update the navigation property channels in groups |
| `delete_group_channel` | Delete navigation property channels for groups |
| `list_channel_members` | Get allMembers from groups |
| `create_group_team_channel_all_membe` | Create new navigation property to allMembers for groups |
| `get_channel_member_details` | Get allMembers from groups |
| `update_group_team_channel_member` | Update the navigation property allMembers in groups |
| `delete_group_channel_member` | Delete navigation property allMembers for groups |
| `count_channel_members` | Get the number of the resource |
| `add_group_channel_all_members` | Invoke action add |
| `remove_channel_members` | Invoke action remove |
| `get_files_folder` | Get filesFolder from groups |
| `get_files_content` | Get content for the navigation property filesFolder from groups |
| `update_files_folder_content` | Update content for the navigation property filesFolder in groups |
| `delete_file_content` | Delete content for the navigation property filesFolder in groups |
| `get_group_team_channel_members` | Get members from groups |
| `create_group_team_channel_member` | Create new navigation property to members for groups |
| `get_group_channel_members` | Get members from groups |
| `update_channel_member` | Update the navigation property members in groups |
| `delete_member_from_channel` | Delete navigation property members for groups |
| `get_channel_member_count` | Get the number of the resource |
| `add_team_channel_member` | Invoke action add |
| `remove_channel_member` | Invoke action remove |
| `get_group_messages` | Get messages from groups |
| `create_group_channel_message` | Create new navigation property to messages for groups |
| `get_group_channel_messages` | Get messages from groups |
| `update_message` | Update the navigation property messages in groups |
| `delete_message_in_channel` | Delete navigation property messages for groups |
| `list_group_team_channel_message_hos` | Get hostedContents from groups |
| `add_hosted_content` | Create new navigation property to hostedContents for groups |
| `get_team_channel_message_hosted_con` | Get hostedContents from groups |
| `patch_hosted_content` | Update the navigation property hostedContents in groups |
| `delete_group_team_channel_message_h` | Delete navigation property hostedContents for groups |
| `get_group_channel_message_hosted_co` | Get media content for the navigation property hostedContents from groups |
| `update_group_team_channel_msg_hoste` | Update media content for the navigation property hostedContents in groups |
| `delete_hosted_content` | Delete media content for the navigation property hostedContents in groups |
| `get_hosted_content_count` | Get the number of the resource |
| `set_reaction_on_group_team_channel_m` | Invoke action setReaction |
| `soft_delete_channel_message` | Invoke action softDelete |
| `restore_group_channel_message` | Invoke action undoSoftDelete |
| `unset_reaction_on_message` | Invoke action unsetReaction |
| `get_chat_message_replies` | Get replies from groups |
| `create_reply_in_message` | Create new navigation property to replies for groups |
| `get_reply_messages` | Get replies from groups |
| `update_reply_message` | Update the navigation property replies in groups |
| `delete_channel_message_reply_by_id` | Delete navigation property replies for groups |
| `get_group_team_channel_msg_replies_h` | Get hostedContents from groups |
| `add_reply_content` | Create new navigation property to hostedContents for groups |
| `get_hosted_content_by_reply_id` | Get hostedContents from groups |
| `update_hosted_content_reply` | Update the navigation property hostedContents in groups |
| `delete_hosted_content_by_message_id` | Delete navigation property hostedContents for groups |
| `get_group_team_channel_msg_hosted_co` | Get media content for the navigation property hostedContents from groups |
| `update_group_team_channel_reply_hos` | Update media content for the navigation property hostedContents in groups |
| `delete_group_team_channel_message_r` | Delete media content for the navigation property hostedContents in groups |
| `count_hosted_contents_replies` | Get the number of the resource |
| `set_reaction_to_message_reply` | Invoke action setReaction |
| `soft_delete_channel_message_reply` | Invoke action softDelete |
| `undo_message_reply_soft_delete` | Invoke action undoSoftDelete |
| `unset_reaction_on_reply` | Invoke action unsetReaction |
| `get_reply_count` | Get the number of the resource |
| `get_microsoft_graph_delta_replies` | Invoke function delta |
| `get_group_channel_message_count` | Get the number of the resource |
| `get_channel_messages_delta` | Invoke function delta |
| `archive_team_channel` | Invoke action archive |
| `complete_group_channel_migration` | Invoke action completeMigration |
| `check_user_access` | Invoke function doesUserHaveAccess |
| `provision_email_to_channel` | Invoke action provisionEmail |
| `remove_channel_email` | Invoke action removeEmail |
| `unarchive_channel` | Invoke action unarchive |
| `get_channel_shared_teams` | Get sharedWithTeams from groups |
| `add_team_to_channel` | Create new navigation property to sharedWithTeams for groups |
| `get_shared_with_team_info` | Get sharedWithTeams from groups |
| `update_team_channel_sharing` | Update the navigation property sharedWithTeams in groups |
| `delete_shared_team_channel` | Delete navigation property sharedWithTeams for groups |
| `get_shared_channel_members` | Get allowedMembers from groups |
| `get_channel_allowed_member_by_ids` | Get allowedMembers from groups |
| `count_allowed_members_by_channel_te` | Get the number of the resource |
| `get_shared_team_info` | Get team from groups |
| `get_shared_with_teams_count_in_chann` | Get the number of the resource |
| `get_group_team_tabs` | Get tabs from groups |
| `create_group_tab` | Create new navigation property to tabs for groups |
| `get_group_tabs` | Get tabs from groups |
| `update_group_tab` | Update the navigation property tabs in groups |
| `delete_group_tab` | Delete navigation property tabs for groups |
| `get_teams_app_tab` | Get teamsApp from groups |
| `get_channel_tabs_count` | Get the number of the resource |
| `get_group_channel_total` | Get the number of the resource |
| `get_group_team_channel_messages_all` | Invoke function getAllMessages |
| `get_retained_messages` | Invoke function getAllRetainedMessages |
| `get_group_team_data` | Get group from groups |
| `get_group_service_errors` | Get serviceProvisioningErrors property value |
| `count_service_provisioning_errors` | Get the number of the resource |
| `get_group_incoming_channels` | Get incomingChannels from groups |
| `get_incoming_channels_by_group` | Get incomingChannels from groups |
| `get_incoming_channels_count` | Get the number of the resource |
| `list_group_team_apps` | Get installedApps from groups |
| `add_group_installed_app` | Create new navigation property to installedApps for groups |
| `get_group_installed_apps` | Get installedApps from groups |
| `patch_installed_apps` | Update the navigation property installedApps in groups |
| `delete_installed_app_for_group_team` | Delete navigation property installedApps for groups |
| `upgrade_teams_app` | Invoke action upgrade |
| `get_teams_app_details` | Get teamsApp from groups |
| `get_teams_app_definition` | Get teamsAppDefinition from groups |
| `count_group_team_apps` | Get the number of the resource |
| `get_group_members` | Get members from groups |
| `create_group_member` | Create new navigation property to members for groups |
| `get_group_team_members` | Get members from groups |
| `update_group_team_member` | Update the navigation property members in groups |
| `delete_group_member` | Delete navigation property members for groups |
| `get_group_team_member_count` | Get the number of the resource |
| `add_group_team_member_action` | Invoke action add |
| `remove_team_member_action` | Invoke action remove |
| `archive_group_team` | Invoke action archive |
| `clone_team_group` | Invoke action clone |
| `complete_group_team_migration` | Invoke action completeMigration |
| `send_activity_notification_to_grou` | Invoke action sendActivityNotification |
| `unarchive_group_team` | Invoke action unarchive |
| `get_group_operations` | Get operations from groups |
| `create_group_team_operation` | Create new navigation property to operations for groups |
| `get_group_team_operations` | Get operations from groups |
| `update_group_operations` | Update the navigation property operations in groups |
| `delete_group_operation` | Delete navigation property operations for groups |
| `get_group_team_count` | Get the number of the resource |
| `list_group_team_permission_grants` | Get permissionGrants from groups |
| `create_permission_grant` | Create new navigation property to permissionGrants for groups |
| `get_group_permission_grants` | Get permissionGrants from groups |
| `update_permission_grant` | Update the navigation property permissionGrants in groups |
| `delete_group_permission_grant` | Delete navigation property permissionGrants for groups |
| `get_group_permission_grants_count` | Get the number of the resource |
| `get_group_team_picture` | Get photo from groups |
| `patch_group_team_photo` | Update the navigation property photo in groups |
| `get_group_team_photo` | Get media content for the navigation property photo from groups |
| `put_group_team_photo_content` | Update media content for the navigation property photo in groups |
| `delete_group_team_photo` | Delete media content for the navigation property photo in groups |
| `get_group_primary` | Get primaryChannel from groups |
| `patch_primary_channel` | Update the navigation property primaryChannel in groups |
| `delete_primary_channel` | Delete navigation property primaryChannel for groups |
| `fetch_team_primary_channel_members` | Get allMembers from groups |
| `create_primary_channel_all_members` | Create new navigation property to allMembers for groups |
| `get_group_primary_channel_member` | Get allMembers from groups |
| `update_team_member` | Update the navigation property allMembers in groups |
| `delete_primary_channel_member` | Delete navigation property allMembers for groups |
| `get_primary_channel_member_count` | Get the number of the resource |
| `add_group_team_members` | Invoke action add |
| `remove_primary_channel_members` | Invoke action remove |
| `get_group_primary_channel_folder` | Get filesFolder from groups |
| `get_primary_channel_files_content` | Get content for the navigation property filesFolder from groups |
| `update_primary_channel_content` | Update content for the navigation property filesFolder in groups |
| `delete_group_files_folder_content` | Delete content for the navigation property filesFolder in groups |
| `list_primary_channel_members` | Get members from groups |
| `create_primary_channel_member_for_g` | Create new navigation property to members for groups |
| `get_primary_channel_members` | Get members from groups |
| `update_primary_channel_member` | Update the navigation property members in groups |
| `delete_member_from_primary_channel` | Delete navigation property members for groups |
| `count_primary_channel_members` | Get the number of the resource |
| `add_primary_channel_member` | Invoke action add |
| `remove_group_team_member` | Invoke action remove |
| `get_primary_channel_messages` | Get messages from groups |
| `post_primary_channel_message` | Create new navigation property to messages for groups |
| `get_primary_channel_message` | Get messages from groups |
| `update_primary_channel_message` | Update the navigation property messages in groups |
| `delete_primary_channel_message` | Delete navigation property messages for groups |
| `get_hosted_content_by_message_id` | Get hostedContents from groups |
| `add_hosted_content_to_group_message` | Create new navigation property to hostedContents for groups |
| `get_group_team_primary_channel_mess` | Get hostedContents from groups |
| `patch_group_team_primary_channel_me` | Update the navigation property hostedContents in groups |
| `delete_message_hosted_content` | Delete navigation property hostedContents for groups |
| `get_group_team_primary_channel_msg_h` | Get media content for the navigation property hostedContents from groups |
| `update_group_team_primary_msg_hoste` | Update media content for the navigation property hostedContents in groups |
| `delete_group_team_primary_channel_m` | Delete media content for the navigation property hostedContents in groups |
| `count_hosted_content` | Get the number of the resource |
| `set_reaction_to_chat_message` | Invoke action setReaction |
| `soft_delete_group_channel_message` | Invoke action softDelete |
| `undo_soft_delete_chat_message` | Invoke action undoSoftDelete |
| `unset_reaction_for_primary_channel` | Invoke action unsetReaction |
| `get_primary_channel_replies` | Get replies from groups |
| `create_reply_to_message` | Create new navigation property to replies for groups |
| `list_group_team_primary_channel_mes` | Get replies from groups |
| `update_primary_channel_reply` | Update the navigation property replies in groups |
| `delete_reply_message` | Delete navigation property replies for groups |
| `get_reply_contents` | Get hostedContents from groups |
| `create_reply_hosted_content` | Create new navigation property to hostedContents for groups |
| `get_hosted_content_reply` | Get hostedContents from groups |
| `patch_group_team_msg_reply_hosted_co` | Update the navigation property hostedContents in groups |
| `delete_group_team_primary_channel_r` | Delete navigation property hostedContents for groups |
| `get_group_team_channel_msg_reply_hos` | Get media content for the navigation property hostedContents from groups |
| `update_group_team_primary_channel_m` | Update media content for the navigation property hostedContents in groups |
| `delete_group_team_primary_ch_reply_h` | Delete media content for the navigation property hostedContents in groups |
| `get_group_team_primary_channel_repl` | Get the number of the resource |
| `set_reply_reaction` | Invoke action setReaction |
| `soft_delete_group_message_reply` | Invoke action softDelete |
| `undo_soft_delete_chat_message_reply` | Invoke action undoSoftDelete |
| `unset_reaction_to_reply` | Invoke action unsetReaction |
| `count_primary_channel_replies` | Get the number of the resource |
| `get_primary_channel_replies_delta` | Invoke function delta |
| `count_primary_channel_messages` | Get the number of the resource |
| `get_primary_channel_messages_delta` | Invoke function delta |
| `archive_primary_channel` | Invoke action archive |
| `complete_group_migration` | Invoke action completeMigration |
| `check_user_access_to_group` | Invoke function doesUserHaveAccess |
| `provision_primary_email` | Invoke action provisionEmail |
| `remove_primary_channel_email` | Invoke action removeEmail |
| `unarchive_primary_channel` | Invoke action unarchive |
| `get_shared_with_teams` | Get sharedWithTeams from groups |
| `share_primary_channel_teams` | Create new navigation property to sharedWithTeams for groups |
| `get_shared_channel_teams` | Get sharedWithTeams from groups |
| `update_shared_team_channel_info` | Update the navigation property sharedWithTeams in groups |
| `remove_group_team_primary_channel_s` | Delete navigation property sharedWithTeams for groups |
| `list_allowed_members_in_shared_chan` | Get allowedMembers from groups |
| `get_channel_team_allowed_member` | Get allowedMembers from groups |
| `count_allowed_members` | Get the number of the resource |
| `get_shared_channel_team_info` | Get team from groups |
| `get_shared_teams_count` | Get the number of the resource |
| `list_group_team_primary_channel_tab` | Get tabs from groups |
| `create_primary_channel_tab` | Create new navigation property to tabs for groups |
| `get_primary_channel_tab` | Get tabs from groups |
| `update_primary_channel_tab` | Update the navigation property tabs in groups |
| `delete_primary_channel_tab` | Delete navigation property tabs for groups |
| `get_primary_channel_tabs_app` | Get teamsApp from groups |
| `count_primary_channel_tabs` | Get the number of the resource |
| `get_group_schedule` | Get schedule from groups |
| `update_group_schedule` | Update the navigation property schedule in groups |
| `delete_group_schedule` | Delete navigation property schedule for groups |
| `get_group_day_notes` | Get dayNotes from groups |
| `add_day_notes_to_group_team_schedule` | Create new navigation property to dayNotes for groups |
| `get_group_team_day_notes` | Get dayNotes from groups |
| `update_day_note` | Update the navigation property dayNotes in groups |
| `delete_day_note_by_id` | Delete navigation property dayNotes for groups |
| `get_group_day_note_count` | Get the number of the resource |
| `share_team_schedule` | Invoke action share |
| `list_group_shift_requests` | Get offerShiftRequests from groups |
| `offer_shift_requests_to_group` | Create new navigation property to offerShiftRequests for groups |
| `get_offer_shift_request_details` | Get offerShiftRequests from groups |
| `update_offer_shift_request` | Update the navigation property offerShiftRequests in groups |
| `delete_group_team_schedule_offer_sh` | Delete navigation property offerShiftRequests for groups |
| `count_group_shift_requests` | Get the number of the resource |
| `list_group_team_open_shift_change_re` | Get openShiftChangeRequests from groups |
| `create_open_shift_change_request` | Create new navigation property to openShiftChangeRequests for groups |
| `get_open_shift_change_request` | Get openShiftChangeRequests from groups |
| `patch_group_team_open_shift_change_r` | Update the navigation property openShiftChangeRequests in groups |
| `delete_open_shift_change_request` | Delete navigation property openShiftChangeRequests for groups |
| `count_open_shift_requests` | Get the number of the resource |
| `get_open_shifts` | Get openShifts from groups |
| `open_shifts_in_group` | Create new navigation property to openShifts for groups |
| `get_open_shift_details` | Get openShifts from groups |
| `update_open_shift` | Update the navigation property openShifts in groups |
| `delete_open_shift_by_id` | Delete navigation property openShifts for groups |
| `get_open_shifts_count` | Get the number of the resource |
| `get_group_scheduling_groups` | Get schedulingGroups from groups |
| `create_scheduling_group` | Create new navigation property to schedulingGroups for groups |
| `get_scheduling_group_details` | Get schedulingGroups from groups |
| `patch_group_team_schedule_scheduli` | Update the navigation property schedulingGroups in groups |
| `delete_group_team_scheduling_group` | Delete navigation property schedulingGroups for groups |
| `count_scheduling_groups_for_team` | Get the number of the resource |
| `get_group_team_shifts` | Get shifts from groups |
| `schedule_group_shifts` | Create new navigation property to shifts for groups |
| `get_group_shifts` | Get shifts from groups |
| `update_shift_details` | Update the navigation property shifts in groups |
| `delete_group_team_shift_by_id` | Delete navigation property shifts for groups |
| `get_shifts_count` | Get the number of the resource |
| `get_swap_shift_change_requests` | Get swapShiftsChangeRequests from groups |
| `swap_shift_requests` | Create new navigation property to swapShiftsChangeRequests for groups |
| `get_swap_shifts_change_request_by_id` | Get swapShiftsChangeRequests from groups |
| `update_swap_shifts_change_request` | Update the navigation property swapShiftsChangeRequests in groups |
| `delete_swap_shift_request` | Delete navigation property swapShiftsChangeRequests for groups |
| `get_group_swap_shifts_count` | Get the number of the resource |
| `get_group_time_cards` | Get timeCards from groups |
| `create_time_card_for_group` | Create new navigation property to timeCards for groups |
| `get_group_time_card_schedule` | Get timeCards from groups |
| `update_time_card` | Update the navigation property timeCards in groups |
| `delete_time_card` | Delete navigation property timeCards for groups |
| `clock_out_time_card` | Invoke action clockOut |
| `confirm_time_card` | Invoke action confirm |
| `end_break_time_card` | Invoke action endBreak |
| `start_group_team_time_card_break` | Invoke action startBreak |
| `get_team_schedule_count` | Get the number of the resource |
| `clock_in_team_schedule` | Invoke action clockIn |
| `list_time_off_reasons_for_group` | Get timeOffReasons from groups |
| `create_time_off_reasons` | Create new navigation property to timeOffReasons for groups |
| `get_team_time_off_reasons` | Get timeOffReasons from groups |
| `update_time_off_reason` | Update the navigation property timeOffReasons in groups |
| `delete_time_off_reason` | Delete navigation property timeOffReasons for groups |
| `get_team_time_off_reasons_count` | Get the number of the resource |
| `list_group_time_off_requests` | Get timeOffRequests from groups |
| `create_group_team_schedule_time_off` | Create new navigation property to timeOffRequests for groups |
| `get_time_off_request_by_id` | Get timeOffRequests from groups |
| `update_time_off_request` | Update the navigation property timeOffRequests in groups |
| `delete_time_off_request_by_id` | Delete navigation property timeOffRequests for groups |
| `get_team_time_off_requests_count` | Get the number of the resource |
| `get_team_times_off` | Get timesOff from groups |
| `create_times_off` | Create new navigation property to timesOff for groups |
| `get_group_time_off_details` | Get timesOff from groups |
| `update_time_off_by_id` | Update the navigation property timesOff in groups |
| `delete_time_off_from_group` | Delete navigation property timesOff for groups |
| `get_group_times_off_count` | Get the number of the resource |
| `get_group_tags` | Get tags from groups |
| `add_group_team_tag` | Create new navigation property to tags for groups |
| `get_group_team_tag_list` | Get tags from groups |
| `patch_group_team_tag_by_id` | Update the navigation property tags in groups |
| `delete_group_team_tags` | Delete navigation property tags for groups |
| `get_team_members_by_group` | Get members from groups |
| `create_group_team_tag_member` | Create new navigation property to members for groups |
| `get_group_team_tag_members` | Get members from groups |
| `update_group_team_tag_member` | Update the navigation property members in groups |
| `delete_group_tag_member` | Delete navigation property members for groups |
| `get_team_tag_member_count` | Get the number of the resource |
| `get_group_tag_count` | Get the number of the resource |
| `get_group_template` | Get template from groups |
| `list_teams` | List teams |
| `create_team` | Create team |
| `get_team_info` | Get team |
| `update_team` | Update team |
| `delete_team_entity` | Delete entity from teams |
| `list_all_team_channels` | List allChannels |
| `get_team_channels` | Get allChannels from teams |
| `get_team_all_channels_count` | Get the number of the resource |
| `list_channels_for_team` | List channels |
| `create_team_channel` | Create channel |
| `get_team_channel_info` | Get channel |
| `update_channel` | Patch channel |
| `delete_channel` | Delete channel |
| `list_all_team_channel_members` | List allMembers |
| `create_team_channel_members` | Create new navigation property to allMembers for teams |
| `get_team_channel_members_details` | Get allMembers from teams |
| `update_conversation_member_in_team` | Update the navigation property allMembers in teams |
| `delete_team_channel_member` | Delete navigation property allMembers for teams |
| `count_team_channel_members` | Get the number of the resource |
| `add_channel_members` | Invoke action add |
| `remove_team_channel_all_members` | Invoke action remove |
| `get_team_channel_files_folder` | Get filesFolder |
| `get_files_folder_content` | Get content for the navigation property filesFolder from teams |
| `update_team_channel_file_content` | Update content for the navigation property filesFolder in teams |
| `delete_team_channel_file_content` | Delete content for the navigation property filesFolder in teams |
| `list_channel_members_by_team_and_cha` | List members of a channel |
| `add_member_to_channel_teamwise` | Add member to channel |
| `get_channel_member` | Get member of channel |
| `update_channel_member_by_id` | Update member in channel |
| `delete_conversation_member` | Delete conversationMember |
| `get_member_count` | Get the number of the resource |
| `add_team_channel_member_action` | Invoke action add |
| `remove_member_action` | Invoke action remove |
| `list_channel_messages_by_id` | List channel messages |
| `send_chat_message` | Send chatMessage in a channel or a chat |
| `get_chat_message` | Get chatMessage in a channel or chat |
| `update_chat_message_by_team_channel` | Update chatMessage |
| `delete_team_channel_message` | Delete navigation property messages for teams |
| `list_channel_msg_hosted_content` | List hostedContents |
| `create_message_hosted_content` | Create new navigation property to hostedContents for teams |
| `get_chat_message_hosted_content_by_i` | Get hostedContents from teams |
| `update_hosted_content_details` | Update the navigation property hostedContents in teams |
| `del_ch_msg_hosted_content` | Delete navigation property hostedContents for teams |
| `get_channel_msg_hosted_content_val` | List hostedContents |
| `update_team_hosted_content_val` | Update media content for the navigation property hostedContents in teams |
| `delete_channel_message_hosted_cont` | Delete media content for the navigation property hostedContents in teams |
| `count_message_hosted_contents_by_me` | Get the number of the resource |
| `set_reaction_on_channel_message` | Invoke action setReaction |
| `soft_delete_chat_message` | Invoke action softDelete |
| `restore_team_channel_message` | Invoke action undoSoftDelete |
| `unset_reaction_from_message` | Invoke action unsetReaction |
| `get_replies` | List replies |
| `create_channel_message_reply` | Reply to a message in a channel |
| `get_chat_message_reply` | Get chatMessage in a channel or chat |
| `update_message_reply` | Update the navigation property replies in teams |
| `delete_team_channel_message_reply_b` | Delete navigation property replies for teams |
| `list_reply_hosted_contents_by_messa` | List hostedContents |
| `create_hosted_content_link` | Create new navigation property to hostedContents for teams |
| `get_channel_reply_hosted_content` | Get hostedContents from teams |
| `patch_ch_reply_hosted_content` | Update the navigation property hostedContents in teams |
| `del_ch_msg_reply_hosted_content` | Delete navigation property hostedContents for teams |
| `get_ch_msg_reply_hosted_content_val` | List hostedContents |
| `update_msg_reply_hosted_content` | Update media content for the navigation property hostedContents in teams |
| `delete_hosted_content_by_message_re` | Delete media content for the navigation property hostedContents in teams |
| `count_ch_msg_reply_host_contents` | Get the number of the resource |
| `add_reaction_to_reply` | Invoke action setReaction |
| `soft_delete_channel_message_reply_p` | Invoke action softDelete |
| `undo_soft_delete_team_message_reply` | Invoke action undoSoftDelete |
| `unset_message_reaction_reply` | Invoke action unsetReaction |
| `count_replies` | Get the number of the resource |
| `get_delta_replies_for_message` | Invoke function delta |
| `get_team_channel_message_count` | Get the number of the resource |
| `delta_team_channel_messages` | Invoke function delta |
| `archive_channel_action` | Invoke action archive |
| `complete_team_channel_migration` | Invoke action completeMigration |
| `check_channel_user_access` | Invoke function doesUserHaveAccess |
| `teams_channels_provision_email_pos` | Invoke action provisionEmail |
| `remove_channel_email_from_team` | Invoke action removeEmail |
| `unarchive_team_channel` | Invoke action unarchive |
| `list_channel_shared_teams` | List sharedWithChannelTeamInfo |
| `share_channel_with_team` | Create new navigation property to sharedWithTeams for teams |
| `get_shared_teams_channels_info` | Get sharedWithChannelTeamInfo |
| `update_shared_with_team_info` | Update the navigation property sharedWithTeams in teams |
| `delete_shared_team_channel_link` | Delete sharedWithChannelTeamInfo |
| `list_channel_allowed_members_by_tea` | List allowedMembers |
| `get_channel_allowed_member_by_id` | Get allowedMembers from teams |
| `get_shared_team_members_count` | Get the number of the resource |
| `get_shared_team_channel_info` | Get team from teams |
| `count_shared_with_teams_in_channel` | Get the number of the resource |
| `get_channel_tabs` | List tabs in channel |
| `add_channel_tab` | Add tab to channel |
| `get_team_tab_info` | Get tab |
| `update_tab_info` | Update tab |
| `delete_channel_tab_by_id` | Delete tab from channel |
| `get_teams_app_data` | Get teamsApp from teams |
| `count_team_channel_tabs` | Get the number of the resource |
| `count_team_channels` | Get the number of the resource |
| `get_team_channel_messages` | Invoke function getAllMessages |
| `get_retained_messages_by_team_id` | Invoke function getAllRetainedMessages |
| `get_team_group` | Get group from teams |
| `list_service_provisioning_errors` | Get serviceProvisioningErrors property value |
| `get_team_provisioning_errors_count` | Get the number of the resource |
| `get_incoming_team_channels` | List incomingChannels |
| `get_incoming_channel_by_team_id` | Get incomingChannels from teams |
| `get_team_incoming_channels_count` | Get the number of the resource |
| `get_team_apps` | List apps in team |
| `add_team_app` | Add app to team |
| `get_installed_team_app` | Get installed app in team |
| `update_teams_installed_app_navigat` | Update the navigation property installedApps in teams |
| `remove_team_installed_app` | Remove app from team |
| `upgrade_team_app` | Invoke action upgrade |
| `get_teams_app_detail` | Get teamsApp from teams |
| `get_app_definition` | Get teamsAppDefinition from teams |
| `get_installed_app_count` | Get the number of the resource |
| `get_team_members_list` | List members of team |
| `add_member_to_team` | Add member to team |
| `get_team_member_details` | Get member of team |
| `update_team_member_conversation_me` | Update member in team |
| `remove_team_member_by_id` | Remove member from team |
| `get_team_member_count` | Get the number of the resource |
| `add_team_members_by_graph_action` | Invoke action add |
| `remove_team_member_by_graph_action` | Invoke action remove |
| `team_archive_action` | Invoke action archive |
| `clone_team_action` | Invoke action clone |
| `complete_team_migration_action` | Invoke action completeMigration |
| `teams_send_activity_notif` | Invoke action sendActivityNotification |
| `unarchive_team_operation` | Invoke action unarchive |
| `get_team_operations_by_id` | Get operations from teams |
| `create_team_operation` | Create new navigation property to operations for teams |
| `get_teams_async_operation_by_id` | Get operations from teams |
| `update_team_operation` | Update the navigation property operations in teams |
| `delete_teams_async_operation_for_te` | Delete navigation property operations for teams |
| `get_team_operation_count` | Get the number of the resource |
| `list_team_permission_grants` | List permissionGrants of a team |
| `create_team_permission_grant` | Create new navigation property to permissionGrants for teams |
| `get_permission_grant_by_team_resour` | Get permissionGrants from teams |
| `update_team_permission_grants` | Update the navigation property permissionGrants in teams |
| `delete_team_permission_grant` | Delete navigation property permissionGrants for teams |
| `count_permission_grants` | Get the number of the resource |
| `get_team_profile_photo` | Get profilePhoto |
| `update_team_photo` | Update profilePhoto |
| `get_profile_photo` | Get profilePhoto |
| `update_team_photo_content` | Update profilePhoto |
| `delete_team_photo_content` | Delete media content for the navigation property photo in teams |
| `get_primary_team_channel` | Get primaryChannel |
| `update_team_primary_channel` | Update the navigation property primaryChannel in teams |
| `delete_team_primary_channel` | Delete navigation property primaryChannel for teams |
| `list_team_primary_channel_members` | Get allMembers from teams |
| `add_team_primary_channel_members` | Create new navigation property to allMembers for teams |
| `get_team_primary_channel_members` | Get allMembers from teams |
| `update_primary_channel_members` | Update the navigation property allMembers in teams |
| `remove_conversation_member` | Delete navigation property allMembers for teams |
| `count_team_primary_channel_members` | Get the number of the resource |
| `add_primary_channel_all_members_act` | Invoke action add |
| `remove_team_members` | Invoke action remove |
| `get_team_files_folder` | Get filesFolder from teams |
| `get_team_primary_channel_content` | Get content for the navigation property filesFolder from teams |
| `upload_team_folder_content` | Update content for the navigation property filesFolder in teams |
| `delete_team_files_folder_content` | Delete content for the navigation property filesFolder in teams |
| `get_team_primary_members` | Get members from teams |
| `add_team_channel_members` | Create new navigation property to members for teams |
| `get_team_primary_channel_member_by_i` | Get members from teams |
| `update_conversation_member_by_id` | Update the navigation property members in teams |
| `delete_team_primary_channel_member` | Delete navigation property members for teams |
| `get_team_primary_channel_member_cou` | Get the number of the resource |
| `add_team_primary_channel_member` | Invoke action add |
| `remove_team_primary_channel_member` | Invoke action remove |
| `list_team_primary_channel_messages` | Get messages from teams |
| `create_team_message` | Create new navigation property to messages for teams |
| `get_team_primary_messages` | Get messages from teams |
| `patch_team_message_by_id` | Update the navigation property messages in teams |
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
| `set_reaction_to_primary_channel_mes` | Invoke action setReaction |
| `soft_delete_team_channel_message` | Invoke action softDelete |
| `teams_undo_soft_delete_message` | Invoke action undoSoftDelete |
| `unset_reaction_by_message_id` | Invoke action unsetReaction |
| `list_replies_by_message_id` | Get replies from teams |
| `create_reply_to_chat_message` | Create new navigation property to replies for teams |
| `get_team_primary_channel_message_re` | Get replies from teams |
| `update_reply` | Update the navigation property replies in teams |
| `delete_reply` | Delete navigation property replies for teams |
| `list_team_reply_hosted_contents_by_i` | Get hostedContents from teams |
| `create_team_reply_hosted_content` | Create new navigation property to hostedContents for teams |
| `get_pri_ch_reply_hosted_content` | Get hostedContents from teams |
| `patch_pri_ch_reply_hosted_content` | Update the navigation property hostedContents in teams |
| `del_pri_ch_reply_hosted_content` | Delete navigation property hostedContents for teams |
| `get_pri_ch_reply_host_content_val` | Get media content for the navigation property hostedContents from teams |
| `put_pri_ch_reply_hosted_content_val` | Update media content for the navigation property hostedContents in teams |
| `del_pri_ch_reply_host_cont_val` | Delete media content for the navigation property hostedContents in teams |
| `count_hosted_content_replies` | Get the number of the resource |
| `set_reaction_to_reply` | Invoke action setReaction |
| `soft_delete_reply_message` | Invoke action softDelete |
| `undo_reply_soft_delete` | Invoke action undoSoftDelete |
| `unset_reply_reaction` | Invoke action unsetReaction |
| `get_primary_channel_replies_count` | Get the number of the resource |
| `get_delta_replies` | Invoke function delta |
| `get_primary_channel_message_count` | Get the number of the resource |
| `list_primary_channel_messages` | Invoke function delta |
| `archive_team_primary_channel` | Invoke action archive |
| `complete_team_migration` | Invoke action completeMigration |
| `check_user_access_in_channel` | Invoke function doesUserHaveAccess |
| `provision_team_email` | Invoke action provisionEmail |
| `remove_primary_team_email` | Invoke action removeEmail |
| `unarchive_team_primary_channel` | Invoke action unarchive |
| `list_primary_channel_shared_teams` | Get sharedWithTeams from teams |
| `share_primary_channel_with_teams` | Create new navigation property to sharedWithTeams for teams |
| `get_shared_channel_info_by_id` | Get sharedWithTeams from teams |
| `update_shared_channel_team_info` | Update the navigation property sharedWithTeams in teams |
| `remove_shared_with_team` | Delete navigation property sharedWithTeams for teams |
| `get_shared_members` | Get allowedMembers from teams |
| `get_team_channel_shared_member_by_id` | Get allowedMembers from teams |
| `count_shared_team_members` | Get the number of the resource |
| `get_shared_channel_team_info_team` | Get team from teams |
| `get_primary_channel_shared_with_tea` | Get the number of the resource |
| `get_team_tabs` | Get tabs from teams |
| `create_team_tab` | Create new navigation property to tabs for teams |
| `get_team_primary_tabs` | Get tabs from teams |
| `update_team_tab` | Update the navigation property tabs in teams |
| `delete_team_tab` | Delete navigation property tabs for teams |
| `get_teams_app_by_tab_id` | Get teamsApp from teams |
| `get_team_primary_channel_tabs_count` | Get the number of the resource |
| `get_team_schedule` | Get schedule |
| `update_team_schedule` | Create or replace schedule |
| `delete_team_schedule` | Delete navigation property schedule for teams |
| `get_team_day_notes` | Get dayNotes from teams |
| `create_team_schedule_day_note` | Create new navigation property to dayNotes for teams |
| `get_team_schedule_day_note` | Get dayNotes from teams |
| `update_team_day_note` | Update the navigation property dayNotes in teams |
| `delete_team_day_note` | Delete navigation property dayNotes for teams |
| `get_team_schedule_day_notes_count` | Get the number of the resource |
| `share_team_schedule_action` | Invoke action share |
| `get_team_shift_requests` | List offerShiftRequest |
| `offer_shift_requests` | Create offerShiftRequest |
| `get_team_schedule_offer_shifts` | Get offerShiftRequest |
| `patch_offer_shift_request` | Update the navigation property offerShiftRequests in teams |
| `delete_shift_offer_request` | Delete navigation property offerShiftRequests for teams |
| `count_shift_offer_requests` | Get the number of the resource |
| `get_team_open_shift_requests` | List openShiftChangeRequests |
| `create_open_shift_change_requests` | Create openShiftChangeRequest |
| `get_open_shift_change_request_by_id` | Get openShiftChangeRequest |
| `patch_open_shift_change_request_by_i` | Update the navigation property openShiftChangeRequests in teams |
| `remove_open_shift_change_request` | Delete navigation property openShiftChangeRequests for teams |
| `count_open_shift_change_requests` | Get the number of the resource |
| `list_team_open_shifts` | List openShifts |
| `create_open_shift_for_team_schedule` | Create openShift |
| `get_open_shift_by_team_id` | Get openShift |
| `update_open_shift_details` | Update openShift |
| `delete_open_shift` | Delete openShift |
| `count_open_shifts` | Get the number of the resource |
| `get_scheduling_groups` | List scheduleGroups |
| `create_scheduling_group_for_team` | Create schedulingGroup |
| `get_team_schedule_scheduling_group` | Get schedulingGroup |
| `replace_scheduling_group_in_team_sc` | Replace schedulingGroup |
| `delete_scheduling_group_by_id` | Delete schedulingGroup |
| `count_scheduling_groups` | Get the number of the resource |
| `get_team_shifts` | List shifts |
| `create_team_schedule_shift` | Create shift |
| `get_team_shift` | Get shift |
| `replace_shift` | Replace shift |
| `delete_shift_by_team_id` | Delete shift |
| `get_team_shift_count` | Get the number of the resource |
| `list_swap_shift_change_requests` | List swapShiftsChangeRequest |
| `swap_shifts_change_request` | Create swapShiftsChangeRequest |
| `swap_shift_request_read` | Get swapShiftsChangeRequest |
| `update_swap_shift_request` | Update the navigation property swapShiftsChangeRequests in teams |
| `delete_swap_shifts_change_request` | Delete navigation property swapShiftsChangeRequests for teams |
| `count_swap_shift_requests` | Get the number of the resource |
| `list_team_time_cards` | List timeCard |
| `create_team_schedule_time_card` | Create timeCard |
| `get_team_time_cards` | Get timeCards from teams |
| `update_team_schedule_time_card_by_id` | Update the navigation property timeCards in teams |
| `delete_time_card_by_id` | Delete timeCard |
| `clock_out_time_card_for_team_by_id` | Invoke action clockOut |
| `confirm_team_time_card` | Invoke action confirm |
| `end_time_card_break` | Invoke action endBreak |
| `start_break_time_card` | Invoke action startBreak |
| `get_team_time_cards_count` | Get the number of the resource |
| `clock_in_time_card` | Invoke action clockIn |
| `list_team_time_off_reasons` | List timeOffReasons |
| `add_team_schedule_reason` | Create timeOffReason |
| `get_time_off_reason` | Get timeOffReason |
| `update_time_off_reason_by_id` | Replace timeOffReason |
| `delete_time_off_reason_by_id` | Delete timeOffReason |
| `get_team_schedule_reasons_count` | Get the number of the resource |
| `list_time_off_requests` | List timeOffRequest |
| `create_team_time_off_request` | Create new navigation property to timeOffRequests for teams |
| `get_team_time_off_request_details` | Get timeOffRequest |
| `update_time_off_request_by_id` | Update the navigation property timeOffRequests in teams |
| `delete_team_time_off_request` | Delete timeOffRequest |
| `get_team_time_off_count` | Get the number of the resource |
| `get_team_schedule_times_off` | List timesOff |
| `create_time_off` | Create timeOff |
| `get_team_time_off_details` | Get timeOff |
| `patch_time_off_entry` | Replace timeOff |
| `delete_time_off_entry` | Delete timeOff |
| `get_team_schedule_times_off_count` | Get the number of the resource |
| `list_teamwork_tags_by_team_id` | List teamworkTags |
| `create_team_tag` | Create teamworkTag |
| `get_teamwork_tag` | Get teamworkTag |
| `update_teamwork_tag` | Update teamworkTag |
| `delete_teamwork_tag` | Delete teamworkTag |
| `list_teamwork_tag_members` | List members in a teamworkTag |
| `create_teamwork_tag_member` | Create teamworkTagMember |
| `get_teamwork_tag_member` | Get teamworkTagMember |
| `update_team_tag_member` | Update the navigation property members in teams |
| `delete_teamwork_tag_member` | Delete teamworkTagMember |
| `get_team_tag_members_count` | Get the number of the resource |
| `count_team_tags` | Get the number of the resource |
| `get_team_template` | Get template from teams |
| `get_team_count` | Get the number of the resource |
| `get_all_team_messages` | Invoke function getAllMessages |
| `get_teamwork_info` | Get teamwork |
| `patch_teamwork` | Update teamwork |
| `list_deleted_chats` | Get deletedChat |
| `link_deleted_chats_to_teamwork` | Create new navigation property to deletedChats for teamwork |
| `get_deleted_chat` | Get deletedChat |
| `update_teamwork_deleted_chat` | Update the navigation property deletedChats in teamwork |
| `delete_teamwork_deleted_chat` | Delete navigation property deletedChats for teamwork |
| `undo_delete_chat` | Invoke action undoDelete |
| `get_deleted_chats_count` | Get the number of the resource |
| `list_deleted_teams` | List deletedTeams |
| `create_teamwork_deleted_teams_link` | Create new navigation property to deletedTeams for teamwork |
| `get_teamwork_deleted_teams` | Get deletedTeams from teamwork |
| `patch_teamwork_deleted_team` | Update the navigation property deletedTeams in teamwork |
| `delete_teamwork_deleted_team` | Delete navigation property deletedTeams for teamwork |
| `get_deleted_team_channels` | Get channels from teamwork |
| `create_deleted_team_channels` | Create new navigation property to channels for teamwork |
| `get_deleted_team_channel` | Get channels from teamwork |
| `update_deleted_team_channel` | Update the navigation property channels in teamwork |
| `delete_team_channel_by_id` | Delete navigation property channels for teamwork |
| `list_deleted_team_channel_members` | Get allMembers from teamwork |
| `add_team_members_to_channel` | Create new navigation property to allMembers for teamwork |
| `get_member_details` | Get allMembers from teamwork |
| `update_team_channel_member` | Update the navigation property allMembers in teamwork |
| `delete_team_member` | Delete navigation property allMembers for teamwork |
| `get_deleted_team_channel_all_member` | Get the number of the resource |
| `add_microsoft_graph_members` | Invoke action add |
| `remove_channel_members_by_team_id` | Invoke action remove |
| `list_team_channel_files` | Get filesFolder from teamwork |
| `get_deleted_team_channel_files_cont` | Get content for the navigation property filesFolder from teamwork |
| `update_deleted_team_channel_file` | Update content for the navigation property filesFolder in teamwork |
| `delete_channel_file_content` | Delete content for the navigation property filesFolder in teamwork |
| `get_deleted_team_channel_members` | Get members from teamwork |
| `create_teamwork_channel_members` | Create new navigation property to members for teamwork |
| `get_team_channel_member` | Get members from teamwork |
| `update_member_in_channel` | Update the navigation property members in teamwork |
| `delete_team_members` | Delete navigation property members for teamwork |
| `get_deleted_team_channel_members_co` | Get the number of the resource |
| `add_channel_member` | Invoke action add |
| `remove_team_channel_member` | Invoke action remove |
| `get_deleted_team_channel_messages` | Get messages from teamwork |
| `send_team_message` | Create new navigation property to messages for teamwork |
| `get_deleted_team_channel_message` | Get messages from teamwork |
| `update_team_channel_message` | Update the navigation property messages in teamwork |
| `delete_chat_message` | Delete navigation property messages for teamwork |
| `get_hosted_content_by_message` | Get hostedContents from teamwork |
| `create_deleted_team_channel_msg_hos` | Create new navigation property to hostedContents for teamwork |
| `get_deleted_team_channel_message_ho` | Get hostedContents from teamwork |
| `update_chat_message_hosted_content` | Update the navigation property hostedContents in teamwork |
| `delete_deleted_team_channel_messag` | Delete navigation property hostedContents for teamwork |
| `get_deleted_team_channel_message_me` | Get media content for the navigation property hostedContents from teamwork |
| `put_deleted_team_channel_msg_hosted` | Update media content for the navigation property hostedContents in teamwork |
| `delete_hosted_content_value_by_ids` | Delete media content for the navigation property hostedContents in teamwork |
| `count_deleted_team_channel_message` | Get the number of the resource |
| `set_reaction_on_deleted_team_messag` | Invoke action setReaction |
| `soft_delete_team_chat` | Invoke action softDelete |
| `restore_deleted_message` | Invoke action undoSoftDelete |
| `unset_reaction` | Invoke action unsetReaction |
| `get_deleted_team_channel_replies` | Get replies from teamwork |
| `add_channel_message_reply` | Create new navigation property to replies for teamwork |
| `get_channel_message_reply` | Get replies from teamwork |
| `update_team_message_reply` | Update the navigation property replies in teamwork |
| `delete_team_message_reply` | Delete navigation property replies for teamwork |
| `get_deleted_team_channel_reply_host` | Get hostedContents from teamwork |
| `add_reply_to_deleted_team_message` | Create new navigation property to hostedContents for teamwork |
| `get_deleted_team_channel_message_re` | Get hostedContents from teamwork |
| `patch_deleted_team_channel_message` | Update the navigation property hostedContents in teamwork |
| `delete_deleted_team_channel_msg_rep` | Delete navigation property hostedContents for teamwork |
| `get_team_content` | Get media content for the navigation property hostedContents from teamwork |
| `update_deleted_team_channel_msg_hos` | Update media content for the navigation property hostedContents in teamwork |
| `delete_teamwork_content` | Delete media content for the navigation property hostedContents in teamwork |
| `count_hosted_replies` | Get the number of the resource |
| `set_reaction_on_message_reply` | Invoke action setReaction |
| `soft_delete_team_message_reply` | Invoke action softDelete |
| `restore_message_reply` | Invoke action undoSoftDelete |
| `unset_reaction_in_reply` | Invoke action unsetReaction |
| `count_team_message_replies` | Get the number of the resource |
| `get_delta_message_replies` | Invoke function delta |
| `count_deleted_channel_messages` | Get the number of the resource |
| `get_team_channel_messages_delta` | Invoke function delta |
| `archive_deleted_team_channel` | Invoke action archive |
| `complete_channel_migration` | Invoke action completeMigration |
| `has_user_access_to_channel` | Invoke function doesUserHaveAccess |
| `provision_email_channel` | Invoke action provisionEmail |
| `remove_email_channel` | Invoke action removeEmail |
| `unarchive_team_channel_post` | Invoke action unarchive |
| `get_shared_teams_for_channel` | Get sharedWithTeams from teamwork |
| `share_channels_with_teams` | Create new navigation property to sharedWithTeams for teamwork |
| `get_shared_teams_info` | Get sharedWithTeams from teamwork |
| `update_shared_with_teams` | Update the navigation property sharedWithTeams in teamwork |
| `delete_shared_with_team_channel` | Delete navigation property sharedWithTeams for teamwork |
| `get_shared_team_allowed_members` | Get allowedMembers from teamwork |
| `get_allowed_members_by_team_channel` | Get allowedMembers from teamwork |
| `get_deleted_team_channel_shared_tea` | Get the number of the resource |
| `get_shared_team_details` | Get team from teamwork |
| `count_shared_teams_in_channel` | Get the number of the resource |
| `get_deleted_team_channel_tabs` | Get tabs from teamwork |
| `add_tab_to_channel` | Create new navigation property to tabs for teamwork |
| `get_deleted_team_tab_info` | Get tabs from teamwork |
| `update_teams_tab` | Update the navigation property tabs in teamwork |
| `delete_teams_tab` | Delete navigation property tabs for teamwork |
| `get_teams_app_tab_details` | Get teamsApp from teamwork |
| `count_deleted_team_tabs` | Get the number of the resource |
| `get_deleted_team_channels_count` | Get the number of the resource |
| `get_team_messages` | Invoke function getAllMessages |
| `get_all_retained_channel_messages` | Invoke function getAllRetainedMessages |
| `get_team_deleted_count` | Get the number of the resource |
| `get_all_deleted_team_messages` | Invoke function getAllMessages |
| `send_activity_notification_to_reci` | Invoke action sendActivityNotificationToRecipients |
| `get_team_app_settings` | Get teamsAppSettings |
| `update_teams_app_settings` | Update teamsAppSettings |
| `delete_teams_app_setting` | Delete navigation property teamsAppSettings for teamwork |
| `list_workforce_integrations` | List workforceIntegrations |
| `create_workforce_integration` | Create workforceIntegration |
| `get_workforce_integration` | Get workforceIntegration |
| `update_workforce_integration` | Update workforceIntegration |
| `delete_workforce_integration_by_id` | Delete workforceIntegration |
| `get_workforce_integration_count` | Get the number of the resource |
| `list_user_chats` | List chats |
| `create_user_chat_link` | Create new navigation property to chats for users |
| `get_chat_details` | Get chat |
| `update_user_chat` | Update the navigation property chats in users |
| `delete_user_chat` | Delete navigation property chats for users |
| `get_installed_apps` | Get installedApps from users |
| `create_installed_app` | Create new navigation property to installedApps for users |
| `get_installed_apps_by_user_chat` | Get installedApps from users |
| `update_user_chat_installed_app` | Update the navigation property installedApps in users |
| `delete_user_chat_app` | Delete navigation property installedApps for users |
| `upgrade_chat_app` | Invoke action upgrade |
| `get_teams_app` | Get teamsApp from users |
| `fetch_chat_teams_app_definition` | Get teamsAppDefinition from users |
| `count_installed_apps` | Get the number of the resource |
| `get_chat_last_message_preview` | Get lastMessagePreview from users |
| `update_last_message_preview` | Update the navigation property lastMessagePreview in users |
| `delete_last_message_preview` | Delete navigation property lastMessagePreview for users |
| `list_user_chat_members` | Get members from users |
| `create_chat_member` | Create new navigation property to members for users |
| `get_chat_members` | Get members from users |
| `update_chat_members` | Update the navigation property members in users |
| `delete_chat_member` | Delete navigation property members for users |
| `get_chat_member_count` | Get the number of the resource |
| `add_microsoft_graph_member_to_chat` | Invoke action add |
| `remove_chat_member_post` | Invoke action remove |
| `get_messages_by_user_chat` | Get messages from users |
| `create_user_chat_message` | Create new navigation property to messages for users |
| `get_chat_messages` | Get messages from users |
| `update_user_chat_message` | Update the navigation property messages in users |
| `delete_user_chat_message_by_id` | Delete navigation property messages for users |
| `get_user_chat_message_hosted_conten` | Get hostedContents from users |
| `create_user_chat_message_hosted_con` | Create new navigation property to hostedContents for users |
| `get_messages_chat_hosted_content_by` | Get hostedContents from users |
| `patch_user_chat_message_hosted_cont` | Update the navigation property hostedContents in users |
| `delete_chat_message_hosted_content` | Delete navigation property hostedContents for users |
| `get_chat_message_hosted_content_val` | Get media content for the navigation property hostedContents from users |
| `update_user_chat_message_hosted_con` | Update media content for the navigation property hostedContents in users |
| `delete_user_chat_message_hosted_con` | Delete media content for the navigation property hostedContents in users |
| `count_chat_message_hosted_contents` | Get the number of the resource |
| `set_reaction_on_chat_message_by_user` | Invoke action setReaction |
| `soft_delete_user_chat_message` | Invoke action softDelete |
| `undo_chat_message_soft_delete` | Invoke action undoSoftDelete |
| `unset_chat_message_reaction` | Invoke action unsetReaction |
| `get_replies_from_user_chat_message` | Get replies from users |
| `create_reply_link` | Create new navigation property to replies for users |
| `get_replies_from_chat_message` | Get replies from users |
| `update_user_message_reply_by_id` | Update the navigation property replies in users |
| `delete_user_chat_reply` | Delete navigation property replies for users |
| `list_message_reply_hosted_contents` | Get hostedContents from users |
| `create_user_chat_message_reply_host` | Create new navigation property to hostedContents for users |
| `get_user_chat_message_reply_hosted_c` | Get hostedContents from users |
| `patch_user_chat_message_reply_hoste` | Update the navigation property hostedContents in users |
| `delete_reply_hosted_content` | Delete navigation property hostedContents for users |
| `get_hosted_content` | Get media content for the navigation property hostedContents from users |
| `update_user_chat_message_reply_host` | Update media content for the navigation property hostedContents in users |
| `delete_user_chat_reply_hosted_conte` | Delete media content for the navigation property hostedContents in users |
| `count_chat_message_replies` | Get the number of the resource |
| `set_chat_message_reaction_reply` | Invoke action setReaction |
| `soft_delete_chat_message_reply_by_id` | Invoke action softDelete |
| `undo_chat_message_reply_soft_delete` | Invoke action undoSoftDelete |
| `unset_chat_message_reply_reaction_u` | Invoke action unsetReaction |
| `get_chat_message_replies_count` | Get the number of the resource |
| `get_user_chat_message_reply_delta` | Invoke function delta |
| `get_chat_message_count` | Get the number of the resource |
| `get_chats_delta_messages` | Invoke function delta |
| `hide_user_chat` | Invoke action hideForUser |
| `mark_chat_read_for_user` | Invoke action markChatReadForUser |
| `mark_chat_unread_for_user` | Invoke action markChatUnreadForUser |
| `send_activity_notification_to_chat` | Invoke action sendActivityNotification |
| `unhide_chat_for_user` | Invoke action unhideForUser |
| `fetch_user_chat_permissions` | Get permissionGrants from users |
| `grant_chat_permission` | Create new navigation property to permissionGrants for users |
| `get_user_chat_permission_grant_by_id` | Get permissionGrants from users |
| `update_chat_permission_grant` | Update the navigation property permissionGrants in users |
| `delete_permission_grant` | Delete navigation property permissionGrants for users |
| `count_user_chat_permissions` | Get the number of the resource |
| `get_pinned_messages` | Get pinnedMessages from users |
| `create_pinned_message` | Create new navigation property to pinnedMessages for users |
| `get_pinned_messages_for_user_chat` | Get pinnedMessages from users |
| `update_pinned_messages` | Update the navigation property pinnedMessages in users |
| `delete_user_chat_pinned_message` | Delete navigation property pinnedMessages for users |
| `get_pinned_chat_message_details` | Get message from users |
| `get_pinned_message_count` | Get the number of the resource |
| `list_user_chat_tabs` | Get tabs from users |
| `create_user_chat_tab` | Create new navigation property to tabs for users |
| `get_tabs_for_user` | Get tabs from users |
| `update_user_tabs` | Update the navigation property tabs in users |
| `delete_user_tab` | Delete navigation property tabs for users |
| `get_teams_app_info` | Get teamsApp from users |
| `get_tab_count` | Get the number of the resource |
| `get_chat_count_by_user` | Get the number of the resource |
| `get_user_chat_messages` | Invoke function getAllMessages |
| `get_retained_messages_by_user` | Invoke function getAllRetainedMessages |
| `list_user_joined_teams` | Get joinedTeams from users |
| `create_user_joined_team_relation` | Create new navigation property to joinedTeams for users |
| `get_joined_teams_by_user` | Get joinedTeams from users |
| `patch_user_team_association` | Update the navigation property joinedTeams in users |
| `delete_user_team` | Delete navigation property joinedTeams for users |
| `get_user_joined_teams_channels` | Get allChannels from users |
| `get_channels_by_user_team` | Get allChannels from users |
| `get_team_channels_count` | Get the number of the resource |
| `get_channels_by_user_team_id` | Get channels from users |
| `create_user_channel_link` | Create new navigation property to channels for users |
| `get_channels_from_user_team` | Get channels from users |
| `update_user_channel` | Update the navigation property channels in users |
| `delete_user_channel` | Delete navigation property channels for users |
| `get_channel_members` | Get allMembers from users |
| `create_user_team_channel_members` | Create new navigation property to allMembers for users |
| `get_conversation_members` | Get allMembers from users |
| `patch_conversation_member` | Update the navigation property allMembers in users |
| `delete_user_team_channel_conversat` | Delete navigation property allMembers for users |
| `get_channel_members_count` | Get the number of the resource |
| `add_microsoft_graph_member` | Invoke action add |
| `remove_channel_all_members` | Invoke action remove |
| `get_files_folder_details` | Get filesFolder from users |
| `get_team_channel_files_content` | Get content for the navigation property filesFolder from users |
| `update_file_content` | Update content for the navigation property filesFolder in users |
| `delete_files_folder_content` | Delete content for the navigation property filesFolder in users |
| `list_channel_team_member` | Get members from users |
| `add_member_to_channel` | Create new navigation property to members for users |
| `get_user_joined_team_channel_member` | Get members from users |
| `update_conversation_member` | Update the navigation property members in users |
| `delete_user_joined_team_channel_mem` | Delete navigation property members for users |
| `get_team_channel_members_count` | Get the number of the resource |
| `add_user_team_channel_member_by_grap` | Invoke action add |
| `remove_channel_member_by_graph_id` | Invoke action remove |
| `list_user_team_channel_messages` | Get messages from users |
| `create_message_in_channel` | Create new navigation property to messages for users |
| `get_team_channel_message` | Get messages from users |
| `update_chat_message` | Update the navigation property messages in users |
| `delete_team_message` | Delete navigation property messages for users |
| `list_user_chat_message_hosted_conte` | Get hostedContents from users |
| `create_user_team_channel_message_ho` | Create new navigation property to hostedContents for users |
| `get_user_team_channel_message_hoste` | Get hostedContents from users |
| `patch_user_team_channel_message_hos` | Update the navigation property hostedContents in users |
| `delete_user_team_channel_message_ho` | Delete navigation property hostedContents for users |
| `get_user_channel_message_hosted_con` | Get media content for the navigation property hostedContents from users |
| `update_user_team_channel_message_ho` | Update media content for the navigation property hostedContents in users |
| `delete_user_team_channel_msg_hosted` | Delete media content for the navigation property hostedContents in users |
| `get_chat_message_hosted_contents_co` | Get the number of the resource |
| `set_chat_message_reaction` | Invoke action setReaction |
| `soft_delete_channel_message_post` | Invoke action softDelete |
| `restore_chat_message_from_soft_dele` | Invoke action undoSoftDelete |
| `unset_chat_reaction` | Invoke action unsetReaction |
| `get_channel_message_replies_by_ids` | Get replies from users |
| `add_message_reply` | Create new navigation property to replies for users |
| `get_reply_message` | Get replies from users |
| `update_reply_to_message` | Update the navigation property replies in users |
| `delete_chat_message_reply` | Delete navigation property replies for users |
| `list_user_team_channel_message_repl` | Get hostedContents from users |
| `create_reply_content` | Create new navigation property to hostedContents for users |
| `get_user_team_channel_reply_hosted_c` | Get hostedContents from users |
| `update_hosted_content_message` | Update the navigation property hostedContents in users |
| `delete_user_team_channel_message_re` | Delete navigation property hostedContents for users |
| `get_user_team_channel_message_reply` | Get media content for the navigation property hostedContents from users |
| `update_reply_hosted_content_value` | Update media content for the navigation property hostedContents in users |
| `delete_user_team_channel_msg_reply_h` | Delete media content for the navigation property hostedContents in users |
| `get_chat_message_reply_hosted_conte` | Get the number of the resource |
| `set_reaction_for_message_reply` | Invoke action setReaction |
| `soft_delete_channel_message_reply_b` | Invoke action softDelete |
| `undo_soft_delete_replies` | Invoke action undoSoftDelete |
| `unset_reaction_from_message_reply` | Invoke action unsetReaction |
| `get_replies_count` | Get the number of the resource |
| `get_channel_message_delta_replies` | Invoke function delta |
| `count_user_team_channel_messages` | Get the number of the resource |
| `get_user_team_channel_message_delta` | Invoke function delta |
| `archive_channel` | Invoke action archive |
| `complete_migration_channel` | Invoke action completeMigration |
| `check_user_channel_access` | Invoke function doesUserHaveAccess |
| `provision_channel_email` | Invoke action provisionEmail |
| `remove_email_from_channel` | Invoke action removeEmail |
| `post_unarchive_channel_for_user_tea` | Invoke action unarchive |
| `get_shared_teams` | Get sharedWithTeams from users |
| `add_team_to_shared_channel` | Create new navigation property to sharedWithTeams for users |
| `get_shared_teams_details` | Get sharedWithTeams from users |
| `patch_shared_channel_team_info` | Update the navigation property sharedWithTeams in users |
| `delete_shared_with_team_info` | Delete navigation property sharedWithTeams for users |
| `get_shared_channel_allowed_members` | Get allowedMembers from users |
| `get_allowed_members_in_channel` | Get allowedMembers from users |
| `get_shared_with_channel_allowed_mem` | Get the number of the resource |
| `get_shared_team_channels` | Get team from users |
| `get_shared_team_channels_count` | Get the number of the resource |
| `get_user_team_channel_tabs` | Get tabs from users |
| `add_tab_to_user_channel` | Create new navigation property to tabs for users |
| `get_team_tab_details` | Get tabs from users |
| `update_tab` | Update the navigation property tabs in users |
| `delete_tab` | Delete navigation property tabs for users |
| `get_teams_tab_details` | Get teamsApp from users |
| `get_team_channel_tabs_count` | Get the number of the resource |
| `get_team_channel_count` | Get the number of the resource |
| `get_user_team_all_channel_messages` | Invoke function getAllMessages |
| `get_all_retained_team_messages` | Invoke function getAllRetainedMessages |
| `get_user_group_details` | Get group from users |
| `get_service_provisioning_errors` | Get serviceProvisioningErrors property value |
| `get_team_service_errors_count` | Get the number of the resource |
| `get_team_incoming_channels` | Get incomingChannels from users |
| `get_team_channel` | Get incomingChannels from users |
| `count_incoming_channels` | Get the number of the resource |
| `get_installed_apps_for_team` | Get installedApps from users |
| `install_app_for_team` | Create new navigation property to installedApps for users |
| `get_user_team_installed_app_by_id` | Get installedApps from users |
| `update_teams_app_installation` | Update the navigation property installedApps in users |
| `delete_app_installation` | Delete navigation property installedApps for users |
| `upgrade_app_installation` | Invoke action upgrade |
| `get_team_app_details` | Get teamsApp from users |
| `get_app_installation_details` | Get teamsAppDefinition from users |
| `count_user_installed_apps` | Get the number of the resource |
| `get_member_list_for_user_team` | Get members from users |
| `create_user_team_member` | Create new navigation property to members for users |
| `get_team_members_data` | Get members from users |
| `patch_user_team_member` | Update the navigation property members in users |
| `delete_conversation_member_from_us` | Delete navigation property members for users |
| `count_team_members` | Get the number of the resource |
| `add_team_member_to_joined_team` | Invoke action add |
| `remove_team_member_from_user` | Invoke action remove |
| `archive_team_membership` | Invoke action archive |
| `clone_team_by_graph` | Invoke action clone |
| `complete_migration_team` | Invoke action completeMigration |
| `send_activity_to_team` | Invoke action sendActivityNotification |
| `unarchive_team_membership` | Invoke action unarchive |
| `get_user_team_operations` | Get operations from users |
| `add_team_operation` | Create new navigation property to operations for users |
| `get_team_operations` | Get operations from users |
| `patch_async_operation` | Update the navigation property operations in users |
| `delete_async_team_operation` | Delete navigation property operations for users |
| `get_team_operations_count` | Get the number of the resource |
| `get_team_permission_grants` | Get permissionGrants from users |
| `grant_user_permission` | Create new navigation property to permissionGrants for users |
| `get_permission_grants` | Get permissionGrants from users |
| `update_user_team_permission_grant` | Update the navigation property permissionGrants in users |
| `delete_user_team_permission_grant` | Delete navigation property permissionGrants for users |
| `get_team_permission_count` | Get the number of the resource |
| `get_team_photo_from_user` | Get photo from users |
| `patch_user_team_photo` | Update the navigation property photo in users |
| `get_team_photo` | Get media content for the navigation property photo from users |
| `update_user_team_photo` | Update media content for the navigation property photo in users |
| `delete_team_photo` | Delete media content for the navigation property photo in users |
| `get_primary_channel` | Get primaryChannel from users |
| `update_primary_channel` | Update the navigation property primaryChannel in users |
| `delete_primary_channel_from_team` | Delete navigation property primaryChannel for users |
| `list_team_members` | Get allMembers from users |
| `add_team_members` | Create new navigation property to allMembers for users |
| `get_team_members` | Get allMembers from users |
| `patch_user_joined_team_primary_chan` | Update the navigation property allMembers in users |
| `remove_user_team_primary_channel_me` | Delete navigation property allMembers for users |
| `count_user_team_channel_members` | Get the number of the resource |
| `add_team_member` | Invoke action add |
| `remove_team_member_from_channel` | Invoke action remove |
| `get_user_team_channel_files_folder` | Get filesFolder from users |
| `get_team_files_content` | Get content for the navigation property filesFolder from users |
| `update_user_team_file_content` | Update content for the navigation property filesFolder in users |
| `delete_content_folder` | Delete content for the navigation property filesFolder in users |
| `list_team_channel_members` | Get members from users |
| `add_member_to_primary_channel` | Create new navigation property to members for users |
| `get_team_channel_members` | Get members from users |
| `update_user_team_members` | Update the navigation property members in users |
| `delete_user_joined_team_primary_cha` | Delete navigation property members for users |
| `get_team_members_count` | Get the number of the resource |
| `add_member_to_primary_channel_team` | Invoke action add |
| `remove_team_member` | Invoke action remove |
| `get_user_team_channel_messages` | Get messages from users |
| `create_message_in_primary_channel` | Create new navigation property to messages for users |
| `get_team_message` | Get messages from users |
| `update_message_by_id` | Update the navigation property messages in users |
| `delete_message_in_primary_channel` | Delete navigation property messages for users |
| `get_user_team_primary_channel_messa` | Get hostedContents from users |
| `create_user_team_message_hosted_con` | Create new navigation property to hostedContents for users |
| `get_user_joined_team_primary_channe` | Get hostedContents from users |
| `patch_message_hosted_content` | Update the navigation property hostedContents in users |
| `delete_user_team_primary_channel_ms` | Delete navigation property hostedContents for users |
| `get_user_team_primary_channel_msg_ho` | Get media content for the navigation property hostedContents from users |
| `update_user_team_primary_channel_ms` | Update media content for the navigation property hostedContents in users |
| `delete_user_team_channel_content` | Delete media content for the navigation property hostedContents in users |
| `get_primary_channel_msg_hosted_coun` | Get the number of the resource |
| `set_reaction_on_primary_channel_mes` | Invoke action setReaction |
| `soft_delete_message` | Invoke action softDelete |
| `user_joined_team_primary_channel_me` | Invoke action undoSoftDelete |
| `unset_reaction_for_message` | Invoke action unsetReaction |
| `list_user_joined_team_primary_chann` | Get replies from users |
| `create_reply` | Create new navigation property to replies for users |
| `get_channel_message_reply_by_ids` | Get replies from users |
| `update_channel_reply_by_id` | Update the navigation property replies in users |
| `delete_user_joined_team_channel_mes` | Delete navigation property replies for users |
| `get_chat_replies_hosted_contents` | Get hostedContents from users |
| `add_hosted_content_reply` | Create new navigation property to hostedContents for users |
| `get_user_team_reply_hosted_content_b` | Get hostedContents from users |
| `patch_channel_reply_hosted_content` | Update the navigation property hostedContents in users |
| `delete_user_joined_team_channel_rep` | Delete navigation property hostedContents for users |
| `get_hosted_content_value` | Get media content for the navigation property hostedContents from users |
| `update_user_team_channel_reply_host` | Update media content for the navigation property hostedContents in users |
| `delete_user_team_channel_reply_host` | Delete media content for the navigation property hostedContents in users |
| `count_primary_channel_message_repl` | Get the number of the resource |
| `plaintext` | Invoke action setReaction |
| `soft_delete_team_chat_reply_by_id` | Invoke action softDelete |
| `undo_soft_delete_message_reply` | Invoke action undoSoftDelete |
| `unset_channel_message_reply_reacti` | Invoke action unsetReaction |
| `count_user_team_message_replies` | Get the number of the resource |
| `get_replies_delta` | Invoke function delta |
| `get_user_team_channel_message_count` | Get the number of the resource |
| `get_delta_messages` | Invoke function delta |
| `archive_user_team_primary_channel` | Invoke action archive |
| `complete_migration_team_channel` | Invoke action completeMigration |
| `get_team_access` | Invoke function doesUserHaveAccess |
| `provision_email_for_team` | Invoke action provisionEmail |
| `remove_team_email` | Invoke action removeEmail |
| `unarchive_primary_channel_action` | Invoke action unarchive |
| `list_shared_teams` | Get sharedWithTeams from users |
| `share_team_channel` | Create new navigation property to sharedWithTeams for users |
| `get_shared_teams_channels` | Get sharedWithTeams from users |
| `update_team_channel_shared_info` | Update the navigation property sharedWithTeams in users |
| `delete_shared_team_info` | Delete navigation property sharedWithTeams for users |
| `get_shared_with_channel_members` | Get allowedMembers from users |
| `get_shared_with_team_members` | Get allowedMembers from users |
| `count_shared_with_team_members` | Get the number of the resource |
| `get_shared_channel_team_info_by_id` | Get team from users |
| `count_shared_with_teams_in_primary_c` | Get the number of the resource |
| `get_tabs_from_user` | Get tabs from users |
| `create_primary_tab` | Create new navigation property to tabs for users |
| `get_teams_tab` | Get tabs from users |
| `update_user_team_tab` | Update the navigation property tabs in users |
| `delete_tab_by_id` | Delete navigation property tabs for users |
| `get_team_tab_app` | Get teamsApp from users |
| `count_user_team_tabs` | Get the number of the resource |
| `get_user_joined_team_schedule` | Get schedule from users |
| `update_user_team_schedule` | Update the navigation property schedule in users |
| `delete_user_schedule` | Delete navigation property schedule for users |
| `get_day_notes_for_user_team` | Get dayNotes from users |
| `add_day_notes_to_team_schedule` | Create new navigation property to dayNotes for users |
| `get_day_note_schedule` | Get dayNotes from users |
| `update_day_note_schedule` | Update the navigation property dayNotes in users |
| `delete_day_note_by_user_team_id` | Delete navigation property dayNotes for users |
| `count_user_team_day_notes` | Get the number of the resource |
| `share_joined_team_schedule` | Invoke action share |
| `get_offer_shift_requests` | Get offerShiftRequests from users |
| `offer_shift_request_in_team` | Create new navigation property to offerShiftRequests for users |
| `get_shift_requests` | Get offerShiftRequests from users |
| `update_shift_request` | Update the navigation property offerShiftRequests in users |
| `delete_user_joined_team_schedule_of` | Delete navigation property offerShiftRequests for users |
| `count_user_shift_requests` | Get the number of the resource |
| `get_open_shift_requests` | Get openShiftChangeRequests from users |
| `create_open_shift_request` | Create new navigation property to openShiftChangeRequests for users |
| `get_user_team_open_shift_change_requ` | Get openShiftChangeRequests from users |
| `patch_open_shift_change_request` | Update the navigation property openShiftChangeRequests in users |
| `delete_open_shift_request` | Delete navigation property openShiftChangeRequests for users |
| `get_open_shift_count` | Get the number of the resource |
| `list_user_open_shifts` | Get openShifts from users |
| `claim_open_shifts` | Create new navigation property to openShifts for users |
| `get_user_open_shift_by_id` | Get openShifts from users |
| `update_open_shift_for_user_team` | Update the navigation property openShifts in users |
| `delete_user_team_open_shift` | Delete navigation property openShifts for users |
| `get_user_team_open_shifts_count` | Get the number of the resource |
| `list_user_team_scheduling_groups` | Get schedulingGroups from users |
| `create_user_team_scheduling_group` | Create new navigation property to schedulingGroups for users |
| `get_scheduling_group_schedule` | Get schedulingGroups from users |
| `patch_user_team_scheduling_group_na` | Update the navigation property schedulingGroups in users |
| `delete_user_joined_team_scheduling` | Delete navigation property schedulingGroups for users |
| `get_scheduling_group_count` | Get the number of the resource |
| `list_user_team_shifts` | Get shifts from users |
| `create_shift_for_team` | Create new navigation property to shifts for users |
| `get_shift_details` | Get shifts from users |
| `update_user_shift_details` | Update the navigation property shifts in users |
| `delete_shift_for_user` | Delete navigation property shifts for users |
| `get_shift_count` | Get the number of the resource |
| `get_team_user_swap_shift_requests` | Get swapShiftsChangeRequests from users |
| `swap_shifts_request` | Create new navigation property to swapShiftsChangeRequests for users |
| `get_swap_shifts_change_request` | Get swapShiftsChangeRequests from users |
| `update_swap_shifts_request` | Update the navigation property swapShiftsChangeRequests in users |
| `delete_swap_shift_change_request` | Delete navigation property swapShiftsChangeRequests for users |
| `get_swap_shift_requests_count` | Get the number of the resource |
| `get_team_schedule_time_cards` | Get timeCards from users |
| `create_time_card_for_team` | Create new navigation property to timeCards for users |
| `get_time_card_details` | Get timeCards from users |
| `update_user_team_time_card` | Update the navigation property timeCards in users |
| `delete_user_team_time_card_by_id` | Delete navigation property timeCards for users |
| `clock_out_team_time_card` | Invoke action clockOut |
| `confirm_time_card_schedule` | Invoke action confirm |
| `end_break_time_card_by_user_team_id` | Invoke action endBreak |
| `start_break_for_user_time_card` | Invoke action startBreak |
| `count_user_team_time_cards` | Get the number of the resource |
| `clock_in_team_user` | Invoke action clockIn |
| `list_time_off_reasons` | Get timeOffReasons from users |
| `create_time_off_reason` | Create new navigation property to timeOffReasons for users |
| `get_team_user_time_off_reasons` | Get timeOffReasons from users |
| `update_user_team_time_off_reason` | Update the navigation property timeOffReasons in users |
| `delete_time_off_reason_for_user` | Delete navigation property timeOffReasons for users |
| `count_user_team_time_off_reasons` | Get the number of the resource |
| `get_time_off_requests_for_team` | Get timeOffRequests from users |
| `user_joined_team_schedule_create_ti` | Create new navigation property to timeOffRequests for users |
| `get_team_time_off_request` | Get timeOffRequests from users |
| `update_user_team_time_off_request` | Update the navigation property timeOffRequests in users |
| `delete_time_off_request` | Delete navigation property timeOffRequests for users |
| `get_time_off_request_count` | Get the number of the resource |
| `get_times_off_schedule` | Get timesOff from users |
| `post_user_team_schedule_off` | Create new navigation property to timesOff for users |
| `get_team_user_time_off` | Get timesOff from users |
| `update_user_time_off` | Update the navigation property timesOff in users |
| `delete_user_team_time_off_by_id` | Delete navigation property timesOff for users |
| `get_team_times_off_count` | Get the number of the resource |
| `get_team_tags_for_user` | Get tags from users |
| `create_user_team_tag` | Create new navigation property to tags for users |
| `get_tags_from_user` | Get tags from users |
| `update_user_team_tag_by_id` | Update the navigation property tags in users |
| `delete_user_team_tag` | Delete navigation property tags for users |
| `get_team_members_by_tag_id` | Get members from users |
| `add_teamwork_tag_member` | Create new navigation property to members for users |
| `get_teamwork_tag_members` | Get members from users |
| `update_teamwork_tag_member` | Update the navigation property members in users |
| `delete_tag_member` | Delete navigation property members for users |
| `count_teamwork_tag_members` | Get the number of the resource |
| `get_tag_count` | Get the number of the resource |
| `get_user_template` | Get template from users |
| `get_joined_teams_count` | Get the number of the resource |
| `get_joined_team_messages` | Invoke function getAllMessages |
| `get_user_teamwork_data` | Get userTeamwork |
| `update_user_teamwork` | Update the navigation property teamwork in users |
| `delete_user_teamwork` | Delete navigation property teamwork for users |
| `get_associated_teams` | Get associatedTeams from users |
| `associate_team_to_user` | Create new navigation property to associatedTeams for users |
| `get_associated_teams_by_user` | Get associatedTeams from users |
| `update_associated_team_info` | Update the navigation property associatedTeams in users |
| `delete_associated_team` | Delete navigation property associatedTeams for users |
| `get_associated_team` | Get team from users |
| `get_associated_teams_count` | Get the number of the resource |
| `get_user_installed_apps` | List apps installed for user |
| `install_app_for_user` | Install app for user |
| `get_user_installed_app` | Get installed app for user |
| `patch_user_teamwork_app` | Update the navigation property installedApps in users |
| `delete_installed_app` | Uninstall app for user |
| `get_chat_app_installation` | Get chat between user and teamsApp |
| `get_installed_teams_app` | Get teamsApp from users |
| `get_installed_app_details` | Get teamsAppDefinition from users |
| `get_installed_apps_count` | Get the number of the resource |
| `send_user_team_activity` | Invoke action sendActivityNotification |
