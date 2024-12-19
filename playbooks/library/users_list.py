#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_test

short_description: This is my test module

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

import os

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        homedirs=dict(type='bool', required=False, default=False),
        old_shell=dict(type='str', required=False, default='/bin/bash'),
        new_shell=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        users=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    # --------
    users = []
    users_for_new_shell = []

    with open('/etc/passwd') as passwd:
        for user in passwd.readlines():
            if not module.params['homedirs']:
                users.append(user.split(':')[0])
                # users.append(user.strip())
            else:
                home_path = user.split(':')[5]
                if home_path.startswith('/home'):
                    users.append(user.split(':')[0])
            if module.params['old_shell']:
                if user.split(':')[6].strip().endswith(module.params['old_shell']):
                    users_for_new_shell.append(user.split(':')[0])

    new_shell = module.params['new_shell']

    if module.params['old_shell'] and new_shell:
        if os.path.isfile(new_shell) and os.access(new_shell, os.X_OK):
            for user in users_for_new_shell:
                answer = module.run_command(f"chsh -s {new_shell} {user}")
                if answer[0] != 0:
                    module.fail_json(msg='Ошибка при установке оболочки', **result)
                else:
                    result['changed'] = True

    # else:
        # module.fail_json(msg='old_shell and new_shell необходимо указывать одновременно', **result)


    result['users'] = users
    result['users_for_new_shell'] = users_for_new_shell

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()