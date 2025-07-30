# aiotdlib CHANGELOG

## 0.24.1

* The predefined values of ClientOptions are now being set up properly.

## 0.24.0 - TDLib 1.8.31

* TDLib version upgraded to 1.8.31. If you use self-built TDLib binaries, you should update them to
  the [supported version](https://github.com/tdlib/td/commit/8f19c751dc296cedb9a921badb7a02a8c0cb1aeb).

## 0.23.4

* All updates handlers now are called asynchronously in background. It allows making another requests in updates handlers.

## 0.23.3

* Fixed blocking authorization flow

## 0.23.2

* Ignore extra env variables in ClientSettings

## 0.23.1

* Added proper base64 encoded serialization for Bytes type

## 0.23.0 - TDLib 1.8.30, Pydantic V2, Multiple Client instances

> This update may contain breaking changes in some scenarios, please read carefully and update your code accordingly

### !! BREAKING CHANGES !!

* TDLib version upgraded to 1.8.30. If you use self-built TDLib binaries, you should update them to
  the [supported version](https://github.com/tdlib/td/commit/4257a341bd08c1fa4d5329b7ecc75cf15563aa23).

* Now library supports only Pydantic v2. If you use Pydantic v1, you should upgrade it to v2. You can follow migration
  guide [here](https://docs.pydantic.dev/latest/migration/)

* The client now accepts a single parameter of type ClientSettings. This parameter is optional. If it is omitted,
  default settings will be used, with parameters filled from environment variables. Look for [README.md](./README.md)
  for more information.

* `ClientProxyType` is moved to `aiotdlib.client_settings` module

* `ClientParseMode` is moved to `aiotdlib.client_settings` module

* `ClientProxySettings` is moved to `aiotdlib.client_settings` module

* `ClientOptions` is moved to `aiotdlib.client_settings` module

* `ClientSettings` is moved to `aiotdlib.client_settings` module

* Some of the fields in API types and functions now have default values *(ESPECIALLY BOOLEANS)*. Make sure it won't
  break your code and update it accordingly. Feel free to open any pull request to fix this problem in types generator.

### Added

* Now you can create multiple Client instances in a single process using the same TD instance. Thanks to @truenicoco for
  helping us move in this direction!

### Removed

* Now client logger follows default log level and can be changed directly with `logging.getLogger(...)`. Client logger
  name now follows pattern "Client_{client_id}"

### Updated

* The client settings have been updated to set default properties such as 'enable_storage_optimizer' and '
  ignore_file_names'. The handling of setting options has been improved to support setting options with None values.
  Event registration in the client cache has been refactored to provide clearer semantics and easier removal of event
  handlers. Logging and handling of updates have also been refined to catch and handle exceptions more effectively.

* Minor fixes and improvements

## 0.22.0

### !! BREAKING CHANGES !!

In this release added a check of Pydantic version. If you have Pydantic v2 and higher `NotImplementedError` will be
raised.

This version of library will be the last one with Pydantic v1 support.

## 0.21.0

> No information about this release

## 0.20.0 - TDLib 1.8.4

* Improved generator: Now some fields have default values. Detected nullable values now are null by default.

* Resolved circular imports error in types. Refactored types module. All types now are stored into single file. (Fixed
  #57)

* TDLib binaries upgraded
  to [available version](https://github.com/pylakey/td/commit/958fed6e8e440afe87b57c98216a5c8d3f3caed8) (1.8.14) (for
  24.06.2023)

* All integer model fields now have `le` constraints as they mentioned in tdlib (`Int32`, `Int53`, `Int64`)

* All types and functions regenerated

* Upgraded all deps
*
* Another minor fixes and improvements

### !! BREAKING CHANGES !!

* Due to python limitations, some arguments changed their position in functions signature. If you pass them as
  positional arguments, make sure they passed in correct order now!

* No client options are set now by default! Make sure you pass them as options parameter of `Client`

* As library wasn't updated for so long, you should check all used tdlib apis used by you before migrating to this
  version!

* Refactored `aiotdlib.api` module, `aiotdlib.api.BaseObject` refactored and moved
  to `aiotdlib.api.types.base.BaseObject`

## 0.19.1 - Hotfix

### Fixed

* Fixed #31

## 0.19.0 - TDLib 1.8.4

### Breaking

* Most of `Client` class methods renamed to match python protected members convention

### Fixed

* Fixed #17

* Fixed #25 by removing wrong update handler

### Added

* Added reactions related updates handlers in `ClientCache`

* Added missing params in methods docs

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/6d485aa0b672ca4b5eccf05d6e5538c6988f12ef) (1.8.4 from
  now)

* API types and functions regenerated

* Upgraded dependencies

## 0.18.0 - TDLib 1.8.3

> This update may contain some breaking API changes!

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/f295ef3a0d3545970bfd658c3443496be3d28397) (1.8.3 from
  now)

* API types and functions regenerated

* Prebuilt TDLib binary for linux arm64 is not more provided, but you can build them yourself and use with aiotdlib

> Prebuilt binaries for other systems and platforms will not be provided as well in future aiotdlib releases

## 0.17.0 - TDLib 1.8.1

> This update may contain some breaking API changes!

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/1e1ab5d1b0e4811e6d9e1584a82da08448d0cada) (1.8.1 from
  now)

* API types and functions regenerated

## 0.16.0 - TDLib 1.8.0

> This update may contain some breaking API changes!

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/fa8feefed70d64271945e9d5fd010b957d93c8cd) (1.8.0 from
  now)

* API types and functions regenerated

## 0.15.1

### Updated

* Fixed options setup (#8)

* Removed ignore_sensitive_content_restrictions from available options as it is not editable by user

* Fixed import typo (#9)

## 0.15.0 - TDLib 1.7.11

> This update contains some breaking API changes!

### Added

* Added ability pass TDLib options as `Client` constructor parameter

* `Client.get_my_id` method to retrieve currently connected user ID

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/218de37c3ada07b5acf793eb5638f5e476526eb2) (1.7.11 from
  now)

* API types and functions regenerated

* Improved chats info caching

## 0.14.0 - TDLib 1.7.10

> This update contains some breaking API changes!

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/6bd7e04875f0a323fc316d5be73358330134c9c8) (1.7.10 from
  now)

* API types and functions regenerated

## 0.13.2 - Bugfix

### Updated

* Fixed small bug with settings validation

* Slightly reformatted Client constructor for better usability

## 0.13.1 - Bugfix

### Updated

* Fixed [#6](https://github.com/pylakey/aiotdlib/issues/6)

> This bug was related to [this](https://github.com/tdlib/td/commit/c69293e1ccc6c36f3134475a1bdb821db6d07ce0) TDLib's
> commit

## 0.13.0 - TDLib 1.7.9

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/eb346f5573040803d4424049dd2ba8aaa039fa56) (1.7.9 from
  now)

* API types and functions regenerated

## 0.12.2

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/3abac232874093c6d3f1002545ce5161b8a09702)

* API types and functions regenerated

## 0.12.1

### Updated

* Fixed default export

## 0.12.0

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/3b0b4775dff3fafa020b9d6207d5315e21f056c5)

* API types and functions regenerated

> **Some ot types and functions have incompatible changes**!

## 0.11.2

### Updated

* Bring back some lost TD functions (Fix for #4)

## 0.11.1 - Environment variables

### Added

* `Client` parameters now could be set via environment variables with AIOTDLIB_* prefix. For example:
  AIOTDLIB_API_ID=123456

* [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/) supported too.

> Constructor parameters has higher priority than env variables and docker secrets. You can read more about this
> behaviour in [Pydantic docs](https://pydantic-docs.helpmanual.io/usage/settings/#field-value-priority)

## 0.11.0 - TDLib 1.7.8

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/0126cec2686e3b95cc1b6dfb5676d364da0e091b) (1.7.8 from
  now)

* API types and functions regenerated

## 0.10.2 - Minor update of TDLib

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/bee2893533b2d62b42f90e1b8bb4f197c2321dfa)

* API types and functions regenerated

## 0.10.1 - Minor fixes

## 0.10.0 - TDLib 1.7.7

### Added

* Added `Client.get_main_list_chats_all` helper method to get the whole main chats list

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/7135caa2bef38939f58e9e206db83fd316236682) (1.7.7 from
  now)

* Default value of `limit` parameter in method `Client.get_main_list_chats` was changed to 100

* Default value of `limit` parameter in method `ClientCache.get_main_list_chats` was changed to 100

* Chats in `ClientCache.get_main_list_chats` are loaded using
  new [loadChats](https://github.com/pylakey/td/blob/master/td/generate/scheme/td_api.tl#L4096) TDLib function

* Added new `NotFound` helper exception for errors with code 400

* Removed usage of deprecated `td_set_log_verbosity_level` function of TDJson
  instance. [setLogVerbosityLevel](https://github.com/pylakey/td/blob/master/td/generate/scheme/td_api.tl#L5587) is used
  instead

* API types and functions regenerated

## 0.9.0 - Upgrade to latest TDLib

> This update may contain breaking changes in some scenarios

### Updated

* Slightly improved generator. Nullable parameters of some api functions now have Optional type

* Changed file structure for prebuilt binaries

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/97fccf7f27c84009460389fdd294739db510f47f)

* API types and functions regenerated

### Removed

* Totally removed `stop_signals` parameter of `Client.idle` method

## 0.8.5 - Bugfix

### Updated

* `stop_signals` parameter of `Client.idle` method is deprecated now and will be totally removed soon

* Fixed [#2](https://github.com/pylakey/aiotdlib/issues/2)

## 0.8.4 - Upgraded TDLib

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/d161323858a782bc500d188b9ae916982526c262)

* API types and functions regenerated

## 0.8.3 - Minor fixes

### Added

* Added `force_update: bool = False` parameter to `Client` class getters. When set to True locally cached values will be
  refreshed from tdlib

### Updated

* Fixed an error when `Client.get_supergroup` and `Client.get_supergroup_full_info` returned `BasicGroup`
  and `BasicGroupFullInfo` instead of `Supergroup` and `SupergroupFullInfo` respectively

## 0.8.2 - Upgrade to latest TDLib

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/f8ab675ad14080b1609b5904c366052c814d1788)

* API types and functions regenerated

## 0.8.1 - Hotfix

### Fixed

* Added missing generated file from new TDLib

## 0.8.0 - TDLib 1.7.6

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/d4dc4f2a50f39b1c05efd955a6e9de0db2b197bc) (1.7.6 from
  now)

* API types and functions regenerated

## 0.7.1 - Docker support

### Added

* Added docker support. Fell free to use [this image](https://hub.docker.com/repository/docker/pylakey/aiotdlib)

## 0.7.0 - Upgraded TDLib (Layer 131)

### Updated

* TDLib binaries upgraded to
  latest [available version](https://github.com/pylakey/td/commit/c45535d607463adb0cd20fcadf43e8f793b1fb24)

* API types and functions regenerated

## 0.6.2 - Prebuilt binary for Linux

### Updated

* Added prebuilt binary for Linux (Built with Ubuntu 20)

## 0.6.1 - TDLib 1.7.5

### Updated

* TDLib upgraded to version 1.7.5

* API types and functions regenerated with new API available in TDLib 1.7.5

## 0.6.0 - Improved filters system, Chat history iteration and Minor Improvements

### Added

* New high-level API method `Client.iter_chat_history` to iterate over messages in chat

* Added `Client.run` method to synchronously run client. Useful for faster bots coding (Included example in README.md)

### Updated

* Improved filters system

* Added a few useful predefined filters

## 0.5.0 - TDLib v1.7.4 and new API features

### Updated

* TDLib upgraded to version 1.7.4

* API types and functions regenerated with new API available in TDLib 1.7.4

## 0.4.2 - UJSON and new TDLibJson API

### Updated

* Added ujson dependency to improve performance of json encoding/decoding

* `TDJson` class now uses new TDLibJson api to work with requests

## 0.4.1

### Updated

* Fixed a bug when main chats list was requested from bot session

## 0.4.0 - TG options cache, Media messages

### BREAKING CHANGES

* `timeout` parameter of `Client.request` changed to `request_timeout`

* `AsyncResult` renamed to `PendingRequest`

* `Client.send_message` renamed to `Client.send_text`

### Added

* all methods of API class now have `request_timeout` parameter

### Updated

* added workaround for all aliased fields of `BaseObject` subclasses

* `PendingRequest.id` is property now and returns `request_id` of outgoing request passed to constructor

* `ClientCache` now handles telegram options updates and provides `get_option_value` method to retrieve option value by
  name

* Messages now can be sent in semi-synchronous way: `SendMessage` request would wait for `UpdateMessageSendSucceeded`
  event.

* Added some high-level methods
  to `Client`: `send_photo`, `send_video`, `send_animation`, `send_document`, `send_audio`, `send_voice_note`, `send_video_note`, `forward_messages`

* Request main chats list if session was authorized for the first time to avoid Chat not found errors and initialize
  inner TDLib chats cache

## 0.3.0 - Proxy

### Added

* Added proxy support. Proxy settings now available in Client
  initializer. [Example](https://github.com/pylakey/aiotdlib#proxy)

## 0.2.1

### Updated

* Minor refactoring

* Updated TDLib binary

## 0.2.0 - Usability improvements

### Added

* `@extra` field of incoming updates now available in `EXTRA` attribute of `BaseObject` and is empty dict by default. It
  is useful to store some user data there

* New filter factory `create_bot_command_filter(command: str)` to create specified command handler (useful for bots).
  This filter parses message text as command and puts `bot_command` and `bot_command_args` to `update.EXTRA`

* `Client.text_message_handler` method for registration of text message handlers
  > this method is universal and can be used directly or as decorator

* `Client.bot_command_handler` method for registration of text message handlers with texts started with "/"
  > this method is universal and can be used directly or as decorator

* `Client.parse_text` method to parse text entities according to `parse_mode` parameter. By default, `parse_mode`
  parameter from constructor will is used

* New high-level API method `Client.edit_message` - Edits the text of a message (or a text of a game message). Returns
  the edited message after the edit is completed on the server side

## 0.1.0 - Client cache, TDLib parameters constraints

### Added

* Cache mechanism for chats, users and both types of groups

* New high-level API method `Client.get_main_list_chats(limit: int)` - Returns an ordered list of chats in a main chat
  list.

* Multiple raw methods wrappers which work the same but returns cached entity if it was found in
  cache: `get_chat`, `get_user`, `get_user_full_info`, `get_basic_group`, `get_basic_group_full_info`, `get_supergroup`, `get_supergroup_full_info`, `get_secret_chat`

* TL Schema parser now parses some parameters constraints in TL Schema such as nullability of parameter, min and max
  length

### Updated

* API objects were regenerated with updated parser

## 0.0.2 - Automated parsing message text

### Added

* added `parse_mode` param to `Client` class. Default parse mode for high-level methods like `send_message`. Default: "
  html"

### Updated

* `Client.send_message` now automatically parses text entities in text. Text will be parsed according to `parse_mode`
  option passed in constructor

### Removed

* Removed redundant `CurrentAuthorizationState` class

## 0.0.1 - First Public Release