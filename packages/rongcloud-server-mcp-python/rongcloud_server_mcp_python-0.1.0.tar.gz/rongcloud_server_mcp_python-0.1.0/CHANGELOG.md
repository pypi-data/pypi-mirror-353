# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-06-06

### Added

- `RongCloudClient`: Client for RongCloud IM service API
- `register_user` tool: Register a new user via RongCloud and return the user's token.
- `get_user_info` tool: Retrieve user information using RongCloud.
- `send_private_text_message` tool: Sends private messages and returns generated message IDs mapped to each recipient user ID
- `send_group_text_message` tool: Sends group messages and returns generated message IDs mapped to each target group ID
- `get_private_messages` tool: Retrieves historical private messages between two users within a specified time range.
- `create_group` tool: Creates a new group chat in RongCloud with specified members.
- `dismiss_group` tool: Permanently deletes a group chat from RongCloud.
- `get_group_members` tool: Retrieves the complete member list of an existing group chat in RongCloud.
- `join_group` tool: Adds one or more users to a specified group chat via RongCloud.
- `quit_group` tool: Removes one or more users from a RongCloud group chat.
- `get_current_time_millis` tool: Get the current time in milliseconds since Unix epoch (January 1, 1970 UTC).
- Environment variable configuration support for RongCloud credentials
