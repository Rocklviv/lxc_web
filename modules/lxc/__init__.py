__author__ = 'user'
from bottle import *
import lxc
import json
import sys
import os
from libs import du

class mod_lxc():

  def __init__(self):
    return

  def dashboard(self):
    """
    Get's list of available containers.
    :return: json
    """
    response.set_header('Content-Type:', 'application/json')
    return json.dumps('{containers: %s}' % self._get_list_containers())

  def create(self):
    """
    Creates LXC container.
    :return: json
    """
    data = request.body.readline()
    response.set_header('Content-Type:', 'application/json')
    if not data:
      abort(400, json.dumps( MISSING_FIELDS_STATUS ))
    else:
      data = json.loads(data.decode('utf-8'))
      try:
        template = data['template']
        container = data['container_name']
      except Exception as e:
        abort(400, json.dumps( MISSING_FIELDS_STATUS ))

      if not self._check_containers(container):
        cnt = lxc.Container(container)
        cnt.create(template=template)
        if self._check_containers(container):
          creds = self._get_credentials(template, container)
          return json.dumps(CREATE_SUCCESS_STATUS % (container, creds))
        else:
          return json.dumps(NOT_CREATE_STATUS)
      else:
        return json.dumps(EXISTS_CONTAINER_STATUS % container)

  def destroy(self):
    """

    :return: json
    """
    data = request.body.readline()
    response.set_header('Content-Type:', 'application/json')
    if not data:
      abort('400', json.dumps(MISSING_FIELD_STATUS % 'container_name'))
    else:
      data = json.loads(data.decode('utf-8'))
      try:
        container = data['container_name']
      except Exception as e:
        abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))

      if self._check_containers(container):
        cnt = lxc.Container(container)
        cnt.destroy()
        return json.dumps(DESTROYED_SUCCESS_STATUS % container)
      else:
        return json.dumps(NOT_EXISTS_CONTAINER_STATUS % container)


  def start(self):
    """

    :return:
    """
    data = request.body.readline()
    response.set_header('Content-Type:', 'application/json')
    if not data:
      abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))
    else:
      print(data)
      data = json.loads(data.decode('utf-8'))
      try:
        container = data['container_name']
      except Exception as e:
        abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))

      if self._check_containers(container):
        cnt = lxc.Container(container)
        cnt.start()
        return json.dumps(STARTED_SUCCESS_STATUS % container)
      else:
        return json.dumps(NOT_EXISTS_CONTAINER_STATUS % container)


  def stop(self):
    """

    :return:
    """
    data = request.body.readline()
    response.set_header('Content-Type:', 'application/json')
    if not data:
      abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))
    else:
      data = json.loads(data.decode('utf-8'))
      try:
        container = data['container_name']
      except Exception as e:
        abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))

      if self._check_containers(container):
        cnt = lxc.Container(container)
        cnt.stop()
        return json.dumps(STOPED_SUCCESS_STATUS % container)
      else:
        return json.dumps(NOT_EXISTS_CONTAINER_STATUS % container)


  def freeze(self):
    """

    :return:
    """
    data = request.body.readline()
    response.set_header('Content-Type:', 'application/json')
    if not data:
      abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))
    else:
      data = json.loads(data.decode('utf-8'))
      try:
        container = data['container_name']
      except Exception as e:
        abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))

      if self._check_containers(container):
        cnt = lxc.Container(container)
        cnt.freeze()
        return json.dumps(FREEZED_SUCCESS_STATUS % container)
      else:
        return json.dumps(NOT_EXISTS_CONTAINER_STATUS % container)


  def unfreeze(self):
    """

    :return:
    """
    data = request.body.readline()
    response.set_header('Content-Type:', 'application/json')
    if not data:
      abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))
    else:
      data = json.loads(data.decode('utf-8'))
      try:
        container = data['container_name']
      except Exception as e:
        abort(400, json.dumps(MISSING_FIELD_STATUS % 'container_name'))

      if self._check_containers(container):
        cnt = lxc.Container(container)
        cnt.unfreeze()
        return json.dumps(UNFREEZED_SUCCESS_STATUS % container)
      else:
        return json.dumps(NOT_EXISTS_CONTAINER_STATUS % container)


  def _get_list_containers(self):
    """
    :return: list
    """
    lst_cnt = list()
    cnt = lxc.list_containers(True, True, True, False)
    d = {}
    for ins in cnt:
      d['name'] = ins.name
      d['state'] = ins.state
      d['size'] = self._get_fs_size(ins.name)
      d['release'] = ins.config_file_name
      lst_cnt.append(d)

    return lst_cnt


  def _get_fs_size(self, container_name):
    cnt = lxc.Container(container_name)
    rootfs = cnt.get_config_item('lxc.rootfs')
    total_size = 0
    start_path = str(rootfs).replace('config', 'rootfs')
    for dirpath, dirnames, filenames in os.walk(start_path):
      for f in filenames:
        fp = os.path.join(dirpath, f)
        try:
          if os.path.islink(fp):
            continue
          total_size += os.path.getsize(fp)
        except FileNotFoundError:
          pass
    r = int(int(len(str(total_size))) / 3)
    total_size = total_size / (1024 ** r)
    if not int(total_size):
        total_size = total_size * 1024
        r = r -1
    size = ('%.1f%s' % (float(total_size), ['B', 'K', 'M', 'G', 'T'][r]))
    return size


  def _check_containers(self, container_name):
    """
    :return: boolean
    """
    list = self._get_list_containers()


  def _get_credentials(self, template, container):
    credentials = ''
    if template == 'ubuntu':
      credentials = 'ubuntu / ubuntu'
    elif template == 'debian':
      credentials = 'root / root (Please use passwd to change root password)'
    elif template == 'centos':
      creds = open('/var/lib/lxc/%s/tmp_root_pass' % container, 'r')
      file = creds.readlines()
      for line in file:
        credentials = line.replace(container, '')
    return credentials.replace('\n', '').replace('--', ' - ')


CREATE_SUCCESS_STATUS = "{ status: 0, message: 'Container created! Credentials for container: %s - %s' }"
NOT_CREATE_STATUS = "{ status: 1, message: 'Not created' }"
EXISTS_CONTAINER_STATUS = "{ status: 2, message: 'Container %s exists' }"
NOT_EXISTS_CONTAINER_STATUS = "{ status: 3, message: 'Container %s does not exists' }"
MISSING_FIELDS_STATUS = "{ status: 4, message: 'Missing required field(s)' }"
MISSING_FIELD_STATUS = "{ status: 5, message: 'Missing required filed %s' }"
DESTROYED_SUCCESS_STATUS = "{ status: 0, message: 'Container %s destroyed' }"
STARTED_SUCCESS_STATUS = "{ status: 0, message: 'Container %s started successfully' }"
STOPED_SUCCESS_STATUS = "{ status: 0, message: 'Container %s stopped successfully' }"
FREEZED_SUCCESS_STATUS = "{ status: 0, message: 'Container %s freezed successfully' }"
UNFREEZED_SUCCESS_STATUS = "{ status: 0, message: 'Container %s unfreezed successfully' }"