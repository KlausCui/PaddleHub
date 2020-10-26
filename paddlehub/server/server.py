#coding:utf-8
# Copyright (c) 2020  PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
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

from collections import OrderedDict
from typing import List

from paddlehub.server import ServerSource, GitSource
from paddlehub.utils import utils

PADDLEHUB_PUBLIC_SERVER = 'http://paddlepaddle.org.cn/paddlehub'


class HubServer(object):
    '''PaddleHub server'''

    def __init__(self):
        self.sources = OrderedDict()

    def _generate_source(self, url: str, source_type: str = 'git'):
        if source_type == 'server':
            source = ServerSource(url)
        elif source_type == 'git':
            source = GitSource(url)
        else:
            raise RuntimeError('Unknown source type {}.'.format(source_type))
        return source

    def _get_source_key(self, url: str):
        return 'source_{}'.format(utils.md5(url))

    def add_source(self, url: str, source_type: str = 'git'):
        '''Add a module source(GitSource or ServerSource)'''
        key = self._get_source_key(url)
        self.sources[key] = self._generate_source(url, source_type)

    def remove_source(self, url: str = None, key: str = None):
        '''Remove a module source'''
        self.sources.pop(key)

    def get_source(self, url: str):
        ''''''
        key = self._get_source_key(url)
        return self.sources.get(key, None)

    def search_module(self,
                      name: str,
                      version: str = None,
                      source: str = None,
                      update: bool = False,
                      branch: str = None) -> List[dict]:
        '''
        Search PaddleHub module

        Args:
            name(str) : PaddleHub module name
            version(str) : PaddleHub module version
        '''
        return self.search_resource(
            type='module', name=name, version=version, source=source, update=update, branch=branch)

    def search_resource(self,
                        type: str,
                        name: str,
                        version: str = None,
                        source: str = None,
                        update: bool = False,
                        branch: str = None) -> List[dict]:
        '''
        Search PaddleHub Resource

        Args:
            type(str) : Resource type
            name(str) : Resource name
            version(str) : Resource version
        '''
        sources = self.sources.values() if not source else [self._generate_source(source)]
        for source in sources:
            if isinstance(source, GitSource) and update:
                source.update()

            if isinstance(source, GitSource) and branch:
                source.checkout(branch)

            result = source.search_resource(name=name, type=type, version=version)
            if result:
                return result
        return []

    def get_module_info(self, name: str, source: str = None) -> dict:
        '''
        '''
        sources = self.sources.values() if not source else [self._generate_source(source)]
        for source in sources:
            result = source.get_module_info(name=name)
            if result:
                return result
        return {}


module_server = HubServer()
module_server.add_source(PADDLEHUB_PUBLIC_SERVER, source_type='server')
