# Copyright 2023 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A create command implementation for the xprof CLI.

This command is used as part of the xprof CLI to create a xprofiler
instance. This will include other metadata such as labels to the log directory
that are specific to the the xprof instance.
"""

import argparse
import ast
from collections.abc import Mapping, Sequence
import json
import time
import uuid

from google.auth import exceptions
from google.cloud import storage
from cloud_diagnostics_xprof.actions import action
from cloud_diagnostics_xprof.actions import delete_action
from cloud_diagnostics_xprof.actions import list_action

# Frozen to specific version of tensorboard-plugin-profile; updated periodically
# Note used for install and adding to metadata + label.
_TENSORBOARD_PLUGIN_PROFILE_VERSION = '2.19.9'

_DEP_INSTALL_URL = 'https://github.com/AI-Hypercomputer/cloud-diagnostics-xprof/blob/main/README.md#install-dependencies'
_WAIT_TIME_IN_SECONDS = 20
_MAX_WAIT_TIME_IN_SECONDS = 300

# Note that this string will replace multiple variables so string is not
# necessarily valid bash.
_OUTPUT_MESSAGE = r"""
Instance for {LOG_DIRECTORY} has been created.
You can access it via the following,
1. https://{BACKEND_ID}-dot-{REGION}.notebooks.googleusercontent.com
2. xprofiler connect -z {ZONE} -l {LOG_DIRECTORY} -m ssh
Instance is hosted at {VM_NAME} VM.
"""

_TB_LAUNCHED_LABEL = 'tb_launched_ts'
_TB_BACKEND_LABEL = 'tb_backend_id'
_TB_ATTEMPTS_LABEL = 'tb_attempts_count'
_STARTUP_SCRIPT_BEGIN_LABEL = 'startup_script_begin_ts'
_MAX_TB_ATTEMPTS = 19

_STARTUP_SCRIPT_STRING = r"""#! /bin/bash
STARTUP_SCRIPT_BEGIN_TS=$(date +%s)
echo \"Starting setup.\"
apt-get update
apt-get install -yq git supervisor python3 python3-pip python3-distutils python3-virtualenv
# Setup tensorboard webserver
echo \"Setup tensorboard webserver.\"
virtualenv -p python3 tensorboardvenv
source tensorboardvenv/bin/activate
tensorboardvenv/bin/pip3 install tensorflow-cpu
tensorboardvenv/bin/pip3 install --upgrade 'cloud-tpu-profiler'
tensorboardvenv/bin/pip3 install tensorboard-plugin-profile=={TENSORBOARD_PLUGIN_PROFILE_VERSION}
tensorboardvenv/bin/pip3 install importlib-resources
tensorboardvenv/bin/pip3 install etils
tensorboard --logdir {LOG_DIRECTORY} --host 0.0.0.0 --port 6006 &
# Label VM with the current timestamp if TB has launched successfully.
for (( attempt=1; attempt < {MAX_TB_ATTEMPTS}; attempt++ )); do
    p_out=\$(ps -ef| grep tensorboard)
    if [[ \"\$p_out\" == *\"tensorboardvenv\"* ]]; then
        echo \"\$(date): TensorBoard running.\"
        TB_LAUNCHED_TS=\$(date +%s)
        break
    else
        sleep 3
    fi
done

if [[ \"\$attempt\" -ge {MAX_TB_ATTEMPTS} ]]; then
    echo \"TensorBoard failed to launch after multiple attempts.\"
    exit 1
fi
# Setup forwarding agent and proxy
echo \"Setup forwarding agent and proxy.\"
# Remove existing docker packages
echo \"Remove existing docker packages.\"
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
# Install docker
echo \"Install docker.\"
sudo apt install docker.io --yes
# Get inverse proxy mapping file.
echo \"Get inverse proxy mapping file.\"
gcloud storage cp gs://dl-platform-public-configs/proxy-agent-config.json .
# Get proxy URL for this region
echo \"Get proxy URL for this region.\"
PROXY_URL=\$(python3 -c \"import json; import sys; data=json.load(sys.stdin); print(data['agent-docker-containers']['latest']['proxy-urls']['{REGION}'][0])\" < proxy-agent-config.json)
echo -e \"PROXY_URL:\"
echo -e \"PROXY_URL: \${PROXY_URL}\"
# Get VM ID for this proxy url
echo \"Get VM ID for this proxy url.\"
VM_ID=\$(curl -H 'Metadata-Flavor: Google' \"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?format=full&audience=${PROXY_URL}/request-endpoint\"  2>/dev/null)
echo -e \"VM_ID:\"
echo -e \"\${VM_ID}\"
# Generate backend and host id
echo \"Generate backend and host id.\"
RESULT_JSON=\$(curl -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" -H \"X-Inverting-Proxy-VM-ID: \${VM_ID}\" -d \"\" \"\${PROXY_URL}/request-endpoint\" 2>/dev/null)
echo -e \"RESULT_JSON:\"
echo -e \"\${RESULT_JSON}\"
# Extract backend id from response
echo \"Extract backend id from response.\"
BACKEND_ID=\$(python3 -c \"import json; import sys; data=json.loads(sys.argv[1]); print(data['backendID'])\" \"\${RESULT_JSON}\")
echo -e \"BACKEND_ID:\"
echo -e \"\${BACKEND_ID}\"
# Extract hostname from response
echo \"Extract hostname from response.\"
HOSTNAME=\$(python3 -c \"import json; import sys; data=json.loads(sys.argv[1]); print(data['hostname'])\" \"\${RESULT_JSON}\")
echo -e \"HOSTNAME:\"
echo -e \"\${HOSTNAME}\"
# Set container name
CONTAINER_NAME='proxy-agent'
echo -e \"CONTAINER_NAME:\"
echo -e \"\${CONTAINER_NAME}\"
# Set URL for agent container
CONTAINER_URL='gcr.io/inverting-proxy/agent:latest'
echo -e \"CONTAINER_URL:\"
echo -e \"\${CONTAINER_URL}\"
# Start agent container
docker run -d \
--env \"BACKEND=\${BACKEND_ID}\" \
--env \"PROXY=\${PROXY_URL}/\" \
--env \"SHIM_WEBSOCKETS=true\" \
--env \"SHIM_PATH=websocket-shim\" \
--env \"PORT=6006\" \
--net=host \
--restart always \
--name \"\${CONTAINER_NAME}\" \
\"\${CONTAINER_URL}\" &
echo \"Setting endpoint info in metadata.\"
# Show command to user.
JSON_OUTPUT=\$(python3 -c \"import sys; data=dict(); data['{STARTUP_SCRIPT_BEGIN_LABEL}']=sys.argv[1]; data['{TB_LAUNCHED_LABEL}']=sys.argv[2]; data['{TB_ATTEMPTS_LABEL}']=sys.argv[3]; data['{TB_BACKEND_LABEL}']=sys.argv[4]; print(data)\" \"\$STARTUP_SCRIPT_BEGIN_TS\" \"\$TB_LAUNCHED_TS\" \"\$attempt\" \"\${BACKEND_ID}\")
echo -e \"\${JSON_OUTPUT}\" > startup_output.json
echo \"Startup Finished\"
"""

# Used to install dependencies & startup TensorBoard.
# MUST be a raw string otherwise interpreted as file path for startup script.
_STARTUP_ENTRY_STRING: str = r"""#! /bin/bash
python3 -c "print(r'''{STARTUP_SCRIPT_STRING}''')" > startup.sh
chmod 775 startup.sh
. ./startup.sh > startup_output.log
gsutil cp startup_output* {LOG_DIRECTORY}/{INSTANCE_NAME}
"""

# Used for creating the VM instance.
_DEFAULT_EXTRA_ARGS: Mapping[str, str | None] = {
    '--tags': 'default-allow-ssh',
    '--image-family': 'debian-12',
    '--image-project': 'debian-cloud',
    '--scopes': 'cloud-platform',
}

_DEFAULT_EXTRA_ARGS_DESCRIBE: Mapping[str, str] = {
    '--format': 'json',
}


class Create(action.Command):
  """A command to delete a xprofiler instance."""

  def __init__(self):
    super().__init__(
        name='create',
        description='Create a new xprofiler instance.',
    )
    self.vm_name = f'{self.VM_BASE_NAME}-{uuid.uuid4()}'

  def add_subcommand(
      self,
      subparser: argparse._SubParsersAction,
  ) -> None:
    """Creates a subcommand for `create`.

    Args:
        subparser: The subparser to add the create subcommand to.
    """
    create_parser = subparser.add_parser(
        name='create',
        help='Create a xprofiler instance.',
        formatter_class=argparse.RawTextHelpFormatter,  # Keeps format in help.
    )
    create_parser.add_argument(
        '--log-directory',
        '-l',
        metavar='GS_PATH',
        required=True,
        help='The GCS path to the log directory.',
    )
    create_parser.add_argument(
        '--zone',
        '-z',
        metavar='ZONE_NAME',
        required=True,
        help='The GCP zone to create the instance in.',
    )
    create_parser.add_argument(
        '--vm-name',
        '-n',
        metavar='VM_NAME',
        help=(
            'The name of the VM to create. '
            'If not specified, a default name will be used.'
        ),
    )
    create_parser.add_argument(
        '--machine-type',
        '-m',
        metavar='MACHINE_TYPE',
        help='The machine type to use for the VM.',
        default='c4-highmem-8',
    )
    create_parser.add_argument(
        '--auto-delete-on-failure-off',
        action='store_true',
        help=(
            'Will not delete the VM if failure occurs.'
        ),
    )
    create_parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Print the command.',
    )

  def _build_command(
      self,
      args: argparse.Namespace,
      extra_args: Mapping[str, str | None] | None = None,
      verbose: bool = False,
  ) -> Sequence[str]:
    """Builds the create command.

    Note this should not be called directly by the user and should be called
    by the run() method in the action module (using the subparser).

    Args:
      args: The arguments parsed from the command line.
      extra_args: Any extra arguments to pass to the command; will overwrite
        any default args.
      verbose: Whether to print the command and other output.

    Returns:
      The command to create the VM.
    """
    # Make sure we define this if not already since we'll build from it.
    if extra_args is None:
      extra_args = {}

    # Include extra args for creation (overwriting default args).
    extra_args = _DEFAULT_EXTRA_ARGS | extra_args

    labels = {
        self.XPROFILER_VERSION_LABEL_KEY: self.XPROFILER_VERSION,
        'tensorboard_plugin_profile': (
            _TENSORBOARD_PLUGIN_PROFILE_VERSION
            .replace('.', '-')  # No dots; dashes are ok.
        ),
    }
    # Allow labels from extra_args to be passed; append to hardcoded labels.
    if ('--labels' in extra_args) and extra_args['--labels']:
      for user_label in extra_args['--labels'].split(','):
        user_label_key, user_label_value = user_label.split('=')
        # Don't allow user to override the version label.
        if user_label_key != self.XPROFILER_VERSION_LABEL_KEY:
          labels[user_label_key] = user_label_value

    extra_args |= {'--labels': self.format_label_string(labels)}

    if verbose:
      print(f'Will create VM w/ name: {self.vm_name}')

    # Create the startup entry script.
    startup_entry_script = startup_script_string(
        args.log_directory, self.vm_name, args.zone
    )

    if verbose:
      print(f'Using startup script:\n{startup_entry_script}')

    log_directory_formatted_string = (
        'gs://'
        + self.format_string_with_replacements(
            original_string=args.log_directory,
            replacements=self.DEFAULT_STRING_REPLACEMENTS,
        )
    )

    # Include version, log directory, and startup script in metadata.
    extra_args |= {
        '--metadata': (
            f'{self.XPROFILER_VERSION_LABEL_KEY}={self.XPROFILER_VERSION}'
            f',{self.LOG_DIRECTORY_LABEL_KEY}={log_directory_formatted_string}'
            f',startup-script={startup_entry_script}'
            f',tensorboard-plugin-profile={_TENSORBOARD_PLUGIN_PROFILE_VERSION}'
        )
    }

    create_vm_command = [
        self.GCLOUD_COMMAND,
        'compute',
        'instances',
        'create',
        self.vm_name,
        '--machine-type',
        args.machine_type,
    ]
    if args.zone:
      create_vm_command.append(f'--zone={args.zone}')

    # Extensions of any other arguments to the main command.
    if extra_args:
      create_vm_command.extend([
          f'{arg}={value}' if value else f'{arg}'
          for arg, value in extra_args.items()
      ])

    if verbose:
      print(create_vm_command)

    return create_vm_command

  def _build_add_labels_command(
      self,
      args: argparse.Namespace,
      labels: dict[str, str],
  ) -> Sequence[str]:
    """Builds the add labels command.

    Args:
      args: The arguments parsed from the command line.
      labels: key value pairs to add as labels.

    Returns:
      The command to add labels to the VM.
    """
    labels = [f'{k}={v}' for k, v in labels.items()]
    labels_string = ','.join(labels)
    add_labels_command = [
        self.GCLOUD_COMMAND,
        'compute',
        'instances',
        'add-labels',
        self.vm_name,
        f'--labels={labels_string}',
        f'--zone={args.zone}',
    ]

    return add_labels_command

  def _delete_vm(
      self,
      *,
      vm_name: str,
      zone: str,
      verbose: bool = False,
  ) -> str:
    """Deletes the VM that was created."""
    delete_command = delete_action.Delete()
    delete_args = argparse.Namespace(
        vm_name=[vm_name],
        log_directory=None,
        zone=zone,
        quiet=True,
    )
    delete_command_output = delete_command.run(delete_args, verbose=verbose)
    return delete_command_output

  def _validate_run_args(
      self,
      *,
      args: argparse.Namespace,
      verbose: bool = False,
    ) -> None:
    """Validates args for the main command and raises an error if invalid.

    Intended to check arguments passed before the command is run.
    Checks:
      - Log directory (GCS bucket URL) exists.
      - Log directory (GCS bucket URL) has a path part.

    Args:
      args: The arguments parsed from the command line.
      verbose: Whether to print the command and other output.

    Raises:
      ValueError: If the log directory does not exist.
    """
    if not self._is_valid_bucket(
        bucket_name=args.log_directory,
        verbose=verbose,
    ):
      raise ValueError(
          f'Log directory {args.log_directory} does not exist.'
      )

  def _build_suggest_zones_for_machine_type_command(
      self,
      machine_type: str,
      limit: int,
      zones: Sequence[str] | None,
  ) -> Sequence[str]:
    """Suggest zone(s) where the machine type is available.

    Args:
      machine_type: The machine type to suggest zones for.
      limit: The maximum number of zones to suggest.
      zones: The zones to suggest from.

    Returns:
      The gcloud command to get zones for the machine type.
    """
    command = [
        self.GCLOUD_COMMAND,
        'compute',
        'machine-types',
        'list',
        '--filter',
        f'name=\'{machine_type}\'',
        '--format',
        'value(zone)',
    ]
    if zones:
      zones_list = ','.join(zones)
      command.append(f'--zones={zones_list}')
    # Assumes that 0 means no limit.
    if limit > 0:
      command.append(f'--limit={limit}')

    return command

  def _suggest_zones_for_machine_type(
      self,
      machine_type: str,
      limit: int = 10,
      zones: Sequence[str] | None = None,
      verbose: bool = False,
  ) -> Sequence[str]:
    """Suggest zone(s) where the machine type is available.

    Args:
      machine_type: The machine type to suggest zones for.
      limit: The maximum number of zones to suggest.
      zones: The zones to suggest from.
      verbose: Whether to print the command and other output.

    Returns:
      The suggested zones where the machine type is available.
    """
    zones_command = self._build_suggest_zones_for_machine_type_command(
        machine_type=machine_type,
        limit=limit,
        zones=zones,
    )
    if verbose:
      print(f'Running command: {zones_command}')
    # If successful, stdout will be a string separated by newline characters.
    output = self._run_command(zones_command, verbose=verbose)

    # Parse the output and return the zones.
    zones = []
    for line in output.split():
      if line:
        zones.append(line.strip())
    return zones

  def run(
      self,
      args: argparse.Namespace,
      extra_args: Mapping[str, str | None] | None = None,
      verbose: bool = False,
  ) -> str:
    """Run the command.

    Args:
      args: The arguments parsed from the command line.
      extra_args: Any extra arguments to pass to the command.
      verbose: Whether to print the command and other output.

    Returns:
      The output of the command.

    Raises:
      RuntimeError: If the backend server cannot be started.
    """
    # Overwrite args and rebuild extra_args (no shared params)
    # This makes sure we don't have conflict when given to the main command.
    if extra_args is not None:
      extra_args_to_remove = []
      for key in args.__dict__.keys():
        # Need to get the extra_args formatted key (includes the `--`)
        key_extra_args_formatted = action.flag_from_string(key)
        # Move the key-value to main args if it exists in extra_args.
        if key_extra_args_formatted in extra_args:
          args.__dict__[key] = extra_args[key_extra_args_formatted]
          extra_args_to_remove.append(key_extra_args_formatted)
      # Rebuild extra_args to remove the keys that were moved to args.
      extra_args = {
          key: value for key, value in extra_args.items()
          if key not in extra_args_to_remove
      }

    # Will raise an error if args are determined to be invalid.
    self._validate_run_args(args=args, verbose=verbose)

    # Remove trailing slash from log directory.
    # This avoid extra layer of subdirectory while copying to GCS.
    args.log_directory = args.log_directory.rstrip('/')
    if args.vm_name:
      self.vm_name = args.vm_name

    # Check if the VM already exists.
    if verbose:
      print('Checking if VM already exists.')
    list_command = list_action.List()
    list_args = argparse.Namespace(
        zones=[args.zone],
        log_directory=[
            args.log_directory,  # Ensure this is treated as one item.
        ],
        vm_name=None,
        filter=None,
        verbose=verbose,
    )
    list_command_output = list_command.run(list_args, verbose=verbose)
    if verbose:
      print(list_command_output)
    vm_data = json.loads(list_command_output)

    # Make sure we can compare with what we expect the output to looks like.
    log_directory_formatted = 'gs://' + self.format_string_with_replacements(
        original_string=args.log_directory,
        replacements=self.DEFAULT_STRING_REPLACEMENTS,
    )
    # Get all the log directories from the VMs.
    all_vm_log_dirs = (
        list_command.get_log_directory_from_vm(vm=vm, verbose=verbose)
        for vm in vm_data
    )

    # Ask user if they want to create another instance or quit.
    if log_directory_formatted in all_vm_log_dirs:
      print(f'Instance for {args.log_directory} already exists.\n')
      # Display the instances & information to the user.
      list_command.display(
          display_str=list_command_output,
          args=list_args,
          verbose=verbose,
      )
      print('\n')  # Just to make it visually clearer for the user.

      # Prompt user if they want to continue or quit.
      message_to_user = (
          'Do you want to continue to create another instance with the same '
          'log directory? (y/n)\n'
      )
      # Don't proceed is user does not say 'Y'/'y'
      user_input = input(message_to_user).lower()
      if user_input != 'y':
        print('Exiting...')
        stdout = list_command_output
        return stdout

    if verbose:
      print('Creating VM...')

    command = self._build_command(
        args=args,
        extra_args=extra_args,
        verbose=verbose,
    )
    if verbose:
      print(f'Command to run: {command}')

    # Check ValueError if failure is due to invalid machine type.
    try:
      stdout: str = self._run_command(command, verbose=verbose)
    except ValueError as e:
      if verbose:
        print(f'Command failed. Subprocess error:\n{e}')
      # Check if the error is due to an invalid machine type.
      if 'Invalid value for field \'resource.machineType\'' in str(e):
        # Print out command away from suggested zones in case of another error.
        machine_type_zone_command = (
            f'gcloud compute machine-types list'
            f' --filter="name={args.machine_type}"'
            f' --format="value(zone)"'
        )
        message_for_checking_machine_type = (
            f'Please check the machine type w/ {args.zone} and try again. '
            'You can investigate zones with the machine type '
            f'{args.machine_type} available:\n'
            f'{machine_type_zone_command}'
        )
        print(message_for_checking_machine_type)

        suggested_zones = self._suggest_zones_for_machine_type(
            machine_type=args.machine_type,
            verbose=verbose,
        )
        message_for_suggested_zones = (
            'The machine type and zone do not match.\n'
            f'Suggested zones with machine type {args.machine_type}:\n'
            f'{suggested_zones}'
        )
        raise ValueError(message_for_suggested_zones) from e
      else:
        raise e

    timer = 0
    print('Waiting for instance to be created. It can take a few minutes.')
    has_tb_backend_id = False
    backend_id: str | None = None
    while timer < _MAX_WAIT_TIME_IN_SECONDS:
      time.sleep(_WAIT_TIME_IN_SECONDS)
      timer += _WAIT_TIME_IN_SECONDS
      # Extra args are separately needed for the describe command.
      json_output = dict()
      try:
        client = storage.Client()
        bucket_name = self._bucket_from_log_directory(args.log_directory)
        file_path = self._filepath_from_log_directory(args.log_directory)
        bucket = client.bucket(bucket_name)
        if verbose:
          print(f'bucket: {bucket}')
          print(f'file: {file_path}')
        if storage.Blob(bucket=bucket, name=file_path).exists(client):
          json_output = storage.Blob(
              bucket=bucket, name=file_path
          ).download_as_string(client)
          json_output = json_output.decode('utf-8')
          json_output = ast.literal_eval(json_output)
          if verbose:
            print(f'json_output: {json_output}')
      except ValueError as e:
        print(f'Error while reading output json from VM: {e}')
        break
      except exceptions.RefreshError as e:
        print(f'{e}\n Kindly visit {_DEP_INSTALL_URL}')
        break

      if not json_output:
        continue

      # Add labels to the VM.
      add_labels_command = self._build_add_labels_command(
          args=args, labels=json_output
      )
      if verbose:
        print(f'Running command: {add_labels_command}')
      add_labels_command_output = self._run_command(
          add_labels_command, verbose=verbose
      )
      if verbose:
        print(f'add_labels_command_output: {add_labels_command_output}')

      # Must have both labels & backend id must have a value.
      has_tb_backend_id = (
          json_output[_TB_LAUNCHED_LABEL] and json_output[_TB_BACKEND_LABEL]
      )

      if verbose:
        print(f'{has_tb_backend_id=}')

      # Exit if we've reached the max number of attempts for TensorBoard server.
      if (
          _TB_ATTEMPTS_LABEL in json_output
          and int(json_output[_TB_ATTEMPTS_LABEL]) >= _MAX_TB_ATTEMPTS
      ):
        raise RuntimeError('Unable to start backend server.')

      if has_tb_backend_id:
        backend_id = json_output[_TB_BACKEND_LABEL]
        break

    # Print out information since creation was successful.
    if has_tb_backend_id:
      if verbose:
        print(f'Backend id: {backend_id}')
      print(
          _OUTPUT_MESSAGE.format(
              LOG_DIRECTORY=args.log_directory,
              BACKEND_ID=backend_id,
              REGION='-'.join(args.zone.split('-')[:-1]),
              VM_NAME=self.vm_name,
              ZONE=args.zone,
          )
      )
    else:  # Setup failed; perform any cleanup.
      print(
          'Unable to set up instance. Initiating cleanup.\n'
      )

      # Delete the VM that was created unless user specified otherwise.
      if args.auto_delete_on_failure_off:
        if verbose:
          print('Not deleting VM since user specified to not delete.')
        # Warn the user regardless of verbose setting.
        print(
            'Failure in setting up VM.\n'
            'Note that the VM was NOT deleted and may be in a bad state'
            ' and/or unstable.\n'
        )
        print(
            _OUTPUT_MESSAGE.format(
                LOG_DIRECTORY=args.log_directory,
                BACKEND_ID=backend_id,
                REGION='-'.join(args.zone.split('-')[:-1]),
                VM_NAME=self.vm_name,
                ZONE=args.zone,
            )
        )
      else:
        if verbose:
          print('Deleting VM that was created.')
          print(f'Deleting from zone: {args.zone}')
        _ = self._delete_vm(
            vm_name=self.vm_name,
            zone=args.zone,
            verbose=verbose,
        )

    return stdout

  def display(
      self,
      display_str: str | None,
      *,
      args: argparse.Namespace,
      extra_args: Mapping[str, str | None] | None = None,
      verbose: bool = False,
  ) -> None:
    """Display provided string after potential formatting.

    Args:
      display_str: The string to display.
      args: The arguments parsed from the command line.
      extra_args: Any extra arguments to pass to the command.
      verbose: Whether to print the command and other output.
    """
    # No display string is needed for the create command.
    return None

  def _bucket_from_log_directory(self, log_directory: str) -> str:
    """Returns the bucket name from the log directory."""
    return log_directory.split('/')[2]

  def _filepath_from_log_directory(self, log_directory: str) -> str:
    """Returns the file name from the log directory."""
    file_path = '/'.join(log_directory.split('/')[3:])
    if file_path:
      return file_path + '/' + self.vm_name + '/startup_output.json'
    return self.vm_name + '/startup_output.json'


def startup_script_string(log_directory: str, vm_name: str, zone: str) -> str:
  """Returns the startup script string."""
  return _STARTUP_ENTRY_STRING.format(
      STARTUP_SCRIPT_STRING=_STARTUP_SCRIPT_STRING.format(
          LOG_DIRECTORY=log_directory,
          MY_INSTANCE_NAME=vm_name,
          ZONE=zone,
          REGION='-'.join(zone.split('-')[:-1]),
          PROXY_URL='{PROXY_URL}',
          VM_ID='{VM_ID}',
          BACKEND_ID='{BACKEND_ID}',
          HOSTNAME='{HOSTNAME}',
          CONTAINER_NAME='{CONTAINER_NAME}',
          CONTAINER_URL='{CONTAINER_URL}',
          RESULT_JSON='{RESULT_JSON}',
          JSON_OUTPUT='{JSON_OUTPUT}',
          TB_LAUNCHED_LABEL=_TB_LAUNCHED_LABEL,
          TB_BACKEND_LABEL=_TB_BACKEND_LABEL,
          TB_ATTEMPTS_LABEL=_TB_ATTEMPTS_LABEL,
          MAX_TB_ATTEMPTS=_MAX_TB_ATTEMPTS,
          STARTUP_SCRIPT_BEGIN_LABEL=_STARTUP_SCRIPT_BEGIN_LABEL,
          TENSORBOARD_PLUGIN_PROFILE_VERSION=_TENSORBOARD_PLUGIN_PROFILE_VERSION,
      ),
      INSTANCE_NAME=vm_name,
      LOG_DIRECTORY=log_directory,
  )
