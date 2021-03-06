# Copyright (C) 2014-2016  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Author: Michael Simacek <msimacek@redhat.com>
# Author: Mikolaj Izdebski <mizdebsk@redhat.com>

from __future__ import print_function

import koji
import logging

from rpm import RPMSENSE_LESS, RPMSENSE_GREATER, RPMSENSE_EQUAL

from koschei.config import get_config


class KojiSession(object):
    def __init__(self, koji_id='primary', anonymous=True):
        self.koji_id = koji_id
        self.config = get_config('koji_config' if koji_id == 'primary' else
                                 'secondary_koji_config')
        self.__anonymous = anonymous
        self.__proxied = self.__new_session()

    def __new_session(self):
        server = self.config['server']
        opts = {
            'anon_retry': True,
            'max_retries': 1000,
            'offline_retry': True,
            'offline_retry_interval': 120,
            'timeout': 3600,
        }
        opts.update(self.config.get('session_opts', {}))
        session = koji.ClientSession(server, opts)
        if not self.__anonymous:
            getattr(session, self.config['login_method'])(**self.config['login_args'])
        return session

    def __getattr__(self, name):
        return getattr(self.__proxied, name)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in ('config', 'koji_id'):
            object.__setattr__(self, name, value)
        else:
            object.__setattr__(self.__proxied, name, value)


def itercall(koji_session, args, koji_call):
    chunk_size = get_config('koji_config.multicall_chunk_size')
    while args:
        koji_session.multicall = True
        for arg in args[:chunk_size]:
            koji_call(koji_session, arg)
        for [info] in koji_session.multiCall():
            yield info
        args = args[chunk_size:]


def prepare_build_opts(opts=None):
    build_opts = get_config('koji_config').get('build_opts', {}).copy()
    if opts:
        build_opts.update(opts)
    build_opts['scratch'] = True
    return build_opts


def get_last_srpm(koji_session, tag, name):
    rel_pathinfo = koji.PathInfo(topdir=get_config('koji_config.srpm_relative_path_root'))
    info = koji_session.listTagged(tag, latest=True,
                                   package=name, inherit=True)
    if info:
        srpms = koji_session.listRPMs(buildID=info[0]['build_id'],
                                      arches='src')
        if srpms:
            return (srpms[0],
                    rel_pathinfo.build(info[0]) + '/' +
                    rel_pathinfo.rpm(srpms[0]))


def koji_scratch_build(session, target_tag, name, source, build_opts):
    build_opts = prepare_build_opts(build_opts)
    logging.info('Intiating koji build for %(name)s:\n\tsource=%(source)s\
                 \n\ttarget=%(target)s\n\tbuild_opts=%(build_opts)s',
                 dict(name=name, target=target_tag, source=source,
                      build_opts=build_opts))
    task_id = session.build(source, target_tag, build_opts,
                            priority=get_config('koji_config.task_priority'))
    logging.info('Submitted koji scratch build for %s, task_id=%d', name, task_id)
    return task_id


def is_koji_fault(session, task_id):
    """
    Return true iff specified finished Koji task was ended due to Koji fault.
    """
    try:
        session.getTaskResult(task_id)
        return False
    except koji.GenericError:
        return False
    except koji.Fault:
        return True


def get_build_group(koji_session, tag_name, group_name):
    groups = koji_session.getTagGroups(tag_name)
    [packages] = [group['packagelist'] for group in groups if group['name'] == group_name]
    return [package['package'] for package in packages
            if not package['blocked'] and package['type'] in ('default', 'mandatory')]


def get_rpm_requires(koji_session, nvras):
    deps_list = itercall(koji_session, nvras,
                         lambda k, nvra: k.getRPMDeps(nvra, koji.DEP_REQUIRE))
    for deps in deps_list:
        requires = []
        for dep in deps:
            flags = dep['flags']
            if flags & ~(RPMSENSE_LESS | RPMSENSE_GREATER | RPMSENSE_EQUAL):
                continue
            order = ""
            while flags:
                old = flags
                flags &= flags - 1
                order += {RPMSENSE_LESS: '<',
                          RPMSENSE_GREATER: '>',
                          RPMSENSE_EQUAL: '='}[old ^ flags]
            requires.append(("%s %s %s" % (dep['name'], order, dep['version'])).rstrip())
        yield requires


def get_koji_load(koji_session):
    channel = koji_session.getChannel('default')
    build_arches = get_config('koji_config').get('build_arches')
    hosts = koji_session.listHosts(build_arches, channel['id'], enabled=True)
    max_load = 0
    assert build_arches
    for arch in build_arches:
        arch_hosts = [host for host in hosts if arch in host['arches']]
        capacity = sum(host['capacity'] for host in arch_hosts)
        load = sum(min(host['task_load'], host['capacity']) if host['ready']
                   else host['capacity'] for host in arch_hosts)
        max_load = max(max_load, load / capacity if capacity else 1.0)
    return max_load


def get_latest_repo(koji_session, build_tag):
    return koji_session.getRepo(build_tag, state=koji.REPO_READY)
