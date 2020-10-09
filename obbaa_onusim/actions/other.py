# Copyright 2020 Broadband Forum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""TBD."""

from ..action import Action

# these will be moved to their message modules as the messages are defined
create_action = Action(4, 'create')
delete_action = Action(6, 'delete')
get_all_alarms_action = Action(11, 'get-all-alarms')
get_all_alarms_next_action = Action(12, 'get-all-alarms-next')
test_action = Action(18, 'test')
start_download_action = Action(19, 'start-download')
download_section_action = Action(20, 'download-section')
end_download_action = Action(21, 'end-download')
activate_image_action = Action(22, 'activate-image')
commit_image_action = Action(23, 'commit-image')
sync_time_action = Action(24, 'sync_time')
reboot_action = Action(25, 'reboot')
get_next_action = Action(26, 'get-next')
test_result_action = Action(27, 'test-result')
get_current_data_action = Action(28, 'get-current-data')
set_table_action = Action(29, 'set-table')
