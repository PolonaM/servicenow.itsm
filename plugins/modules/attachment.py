#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: attachment

author:
  - Polona Mihalič (@PolonaM)

short_description: a module that users can use to download attachments using sys_id

description:
  - Create, delete or update a ServiceNow change request.
  - For more information, refer to the ServiceNow change management documentation at
    U(https://docs.servicenow.com/bundle/paris-it-service-management/page/product/change-management/concept/c_ITILChangeManagement.html).
version_added: 1.0.0
extends_documentation_fragment:
  - servicenow.itsm.instance
  - servicenow.itsm.sys_id
  - servicenow.itsm.number
  - servicenow.itsm.attachments
  - servicenow.itsm.change_request_mapping
seealso:
  - module: servicenow.itsm.change_request_info

options:
  state:
    description:
      - The state of the change request.
      - If I(state) value is C(assess) or C(authorize) or C(scheduled) or
        C(implement) or C(review) or C(closed),
        I(assignment_group) parameter must be filled in.
      - For more information on state model and transition,
        refere to the ServiceNow documentation at
        U(https://docs.servicenow.com/bundle/paris-it-service-management/page/product/change-management/concept/c_ChangeStateModel.html)
      - Default choices are C(new), C(assess), C(authorize), C(scheduled), C(implement), C(review), C(closed), C(canceled), C(absent).
        One can override them by setting I(change_request_mapping.state).
    type: str
  type:
    description:
      - Specify what type of change is required.
    choices: [ standard, normal, emergency ]
    type: str
  template:
    description:
      - Predefined template name for standard change request.
      - For more information on templates refer to ServiceNow documentation at
        U(https://docs.servicenow.com/bundle/quebec-it-service-management/page/product/change-management/concept/c_StandardChangeCatalogPlugin.html)
        or find template names on <your_service_id>.service-now.com/nav_to.do?uri=%2Fstd_change_producer_version_list.do%3F
    type: str
  requested_by:
    description:
      - User who requested the change.
    type: str
  assignment_group:
    description:
      - The group that the change request is assigned to.
      - Required if I(state) value is C(assess) or C(authorize) or
        C(scheduled) or C(implement) or C(review) or C(closed).
    type: str
  category:
    description:
      - The category of the change request.
    choices: [ hardware, software, service, system_software, aplication_software,
               network, telecom, documentation, other ]
    type: str
  priority:
    description:
      - Priority is based on impact and urgency, and it identifies how quickly
        the service desk should address the task.
      - Default choices are C(critical), C(high), C(moderate), C(low).
        One can override them by setting I(change_request_mapping.priority).
    type: str
  risk:
    description:
      - The risk level for the change.
      - Default choices are C(high), C(moderate), C(low).
        One can override them by setting I(change_request_mapping.risk).
    type: str
  impact:
    description:
      - Impact is a measure of the effect of an incident, problem,
        or change on business processes.
      - Default choices are C(high), C(medium), C(low).
        One can override them by setting I(change_request_mapping.impact).
    type: str
  urgency:
    description:
      - The extent to which resolution of an change request can bear delay.
      - Default choices are C(high), C(medium), C(low).
        One can override them by setting I(change_request_mapping.urgency).
    type: str
  short_description:
    description:
      - A summary of the change request.
    type: str
  description:
    description:
      - A detailed description of the change request.
    type: str
  close_code:
    description:
      - Provide information on how the change request was resolved.
      - The change request must have this parameter set prior to
        transitioning to the C(closed) state.
    choices: [ successful, successful_issues, unsuccessful ]
    type: str
  close_notes:
    description:
      - Resolution notes added by the user who closed the change request.
      - The change request must have this parameter set prior to
        transitioning to the C(closed) state.
    type: str
  on_hold:
    description:
      - A change request can be put on hold when I(state)
        is not in the C(new), C(canceled), or C(closed).
    type: bool
  hold_reason:
    description:
      - Reason why change request is on hold.
      - Required if change request's I(on_hold) value will be C(true).
    type: str
  other:
    description:
      - Optional remaining parameters.
      - For more information on optional parameters, refer to the ServiceNow
        change request documentation at
        U(https://docs.servicenow.com/bundle/paris-it-service-management/page/product/change-management/task/t_CreateAChange.html).
    type: dict
"""

EXAMPLES = """
- name: Download examples
  hosts: localhost
  vars:
    sn_host: https://dev121244.service-now.com
    sn_username: admin
    sn_password: rv6F4iErP+=M
    sn_attachment_id: 0061f0c510247200964f77ffeec6c4de
  tasks:
  - name: ServiceNow download attachment module
    servicenow.itsm.attachment:
      instance:
        host: "{{ sn_host }}"
        username: "{{ sn_username }}"
        password: "{{ sn_password }}"
      dest: /tmp/sn-attachment
      sys_id: "{{ sn_attachment_id }}"
    tags:
      - download-attachment-sn
"""

import hashlib

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import (
    arguments,
    client,
    attachment,
    errors,
)


def get_checksum_dest(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def get_checksum_src(binary_data):
    h = hashlib.sha256()
    # Should we implement also block_size reading?
    # while True:
    #     chunk = response.data.read(h.block_size) # replace read 
    #     if not chunk:
    #         break
    #     h.update(chunk)
    h.update(binary_data)
    return h.hexdigest()


def run(module, attachment_client):
    response = attachment_client.get_attachment(
      module.params["sys_id"],
      module.params["dest"]
      )
    checksum_src = get_checksum_src(response.data)
    checksum_dest = get_checksum_dest(module.params["dest"])

    return response, checksum_src, checksum_dest


def main():
    module_args = dict(
        arguments.get_spec(
            "instance", "sys_id"  # why is there also attachment? Is sys_id for the attachment or table?
        ),
        dest=dict(
            type="str",
        ),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        snow_client = client.Client(**module.params["instance"])
        attachment_client = attachment.AttachmentClient(snow_client)
        response, checksum_src, checksum_dest = run(module, attachment_client)
        module.exit_json(
          changed=True,  # Changed True because we change the content of the computer where playbook runs
          checksum_dest=checksum_dest,
          checksum_src=checksum_src,
          # dest="/tmp/sn-attachment",
          # elapsed=2, # The number of seconds that elapsed while performing the download
          # gid=1001, # group id of the file
          # group="polonamihalic", # group of the file
          # md5sum="e67247842e8d985fd709ff18599699c2", # md5 checksum of the file after download - WHY DO WE NEED THIS?
          # mode="0664", # permissions of the target
          # msg="OK (unknown bytes)", # the HTTP message from the request
          # owner="polonamihalic", # owner of the file
          # size=1905, # size of the target
          # src="/home/polonamihalic/.ansible/tmp/ansible-tmp-1656593431.4899359-251579-202476144348026/tmp6w1hml3g", # source file used after download
          # state="file", # state of the target
          status_code=response.status, # the HTTP status code from the request
          # uid=1001, # owner id of the file, after execution
          # url= "https://dev121244.service-now.com/api/now/attachment/11138a9e97901110166e318c1253afd9/file" # the actual URL used for the request
          )
    except errors.ServiceNowError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
