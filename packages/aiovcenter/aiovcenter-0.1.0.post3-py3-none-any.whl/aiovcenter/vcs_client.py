"""
# Created : 2024-02-19
# Last Modified : 2025-01-20
# Product : vCenter Server
# Description : vCenter Class/Methods
"""

__author__ = ''
__version__ = '0.1.0'
__copyright__ = ''
__vcenter_version__ = '8.0'

import asyncio
import importlib
import sys
import urllib3

from typing import Type, Union, Self, Dict, List, Any
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from colorama import Fore, Back, Style

urllib3.disable_warnings()


class AsyncVcenterPyVmomi():
    """ async class's methods """

    # __init__ constructor method
    def __init__(self, **kwargs: Dict[str, Any]) -> None:

        """ load modules from this class instead of loading at the start of the script """
        self.ssl    = importlib.import_module('ssl')        # __import__('ssl')
        self.atexit = importlib.import_module('atexit')     # __import__('atexit')

        self.username    = kwargs["USERNAME"]
        self.password    = kwargs["PASSWORD"]
        self.vchost      = kwargs['HOST']        # vcenter host
        self.port        = kwargs['PORT']        # default 443
        self.vc_url      = f'https://{self.vchost}:{self.port}'
        self.si: Type[Any]
        self.content: Type[Any]
        self.session_id: str
        self.datacenters: Any

    # ----- open session
    async def __aenter__(self) -> Self:
        """ create vcenter session """

        print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'connect to vcenter server {self.vchost} (asyncio)')

        try:

            # ----- Disable SSL certificate verification
            #/ context=self.ssl.SSLContext(self.ssl.PROTOCOL_SSLv23)
            #/ context.verify_mode=self.ssl.CERT_NONE
            context = self.ssl._create_unverified_context()

            self.si = await asyncio.to_thread(
                SmartConnect,
                host=self.vchost,
                port=self.port,
                user=self.username,
                pwd=self.password,
                sslContext=context
            )

        except Exception as err:
            print(f'\nfailed to connect to {self.vchost}: {err}')
            sys.exit(1)

        self.content = self.si.RetrieveContent()

        return self

    # ----- close session
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """ delete vcenter sessions """

        if self.si:
            await self.a_disconnect()

    # ----- connect vcenter
    async def a_connect(self) -> Self:
        """ create vcenter session """

        print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'connect to vcenter server {self.vchost} (asyncio)')

        loop = asyncio.get_event_loop()

        try:

            context = self.ssl.SSLContext(self.ssl.PROTOCOL_SSLv23)
            context.verify_mode = self.ssl.CERT_NONE
            #/ context = self.ssl._create_unverified_context()

            self.si = await loop.run_in_executor(
                None,
                lambda: SmartConnect(
                    host=self.vchost,
                    port=self.port,
                    user=self.username,
                    pwd=self.password,
                    sslContext=context
                )
            )

            self.atexit.register(Disconnect, self.si)

        except Exception as err:
            print(f'\nfailed to connect to {self.vchost}: {err}')
            sys.exit(1)

        self.content = self.si.RetrieveContent()

        return self

    # ----- disconnect vcenter
    async def a_disconnect(self) -> None:
        """ disconnect from vcenter """

        if self.si:
            await asyncio.to_thread(Disconnect, self.si)
            print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'closing vcenter session on {self.vchost}')

    # ----- get vcenter objects
    async def a_get_all_objs(self, vimtype: Any) -> List[Any]:
        """ Get vcenter objects from root folder

        - Args:
            vimtype (Any): _description_

        - Returns:
            List[Any]: _description_
        """
        print(f'return {vimtype} objects (asyncio)')

        loop = asyncio.get_event_loop()

        obj_view = self.content.viewManager.CreateContainerView(self.content.rootFolder, vimtype, True)
        obj_list = await loop.run_in_executor(None, lambda: [obj for obj in obj_view.view])
        obj_view.Destroy()

        return obj_list

    # ----- get datacenter
    async def a_get_datacenter(self, dc_name: str) -> Any:
        """ Get a datacenter object

        - Args:
            dc_name (str): Name of the datacenter

        - Returns:
            Any: Datacenter object or None if not found
        """

        print(Style.NORMAL + Back.BLACK + Fore.WHITE + f'\treturn datacenter object {dc_name} (asyncio)')

        for entity in self.content.rootFolder.childEntity:
            if entity.name == dc_name and isinstance(entity, vim.Datacenter):
                return entity

        return None

    # ----- list datacenters
    async def a_list_datacenters(self) -> Union[List[str] | Any]:
        """ Get the list of datacenters

        - Returns:
            Union[List[str] | Any]: List of datacenter names or None if not found
        """

        print(Style.NORMAL + Back.BLACK + Fore.WHITE + "\treturn datacenters name  (asyncio)")

        self.datacenters = self.content.rootFolder.childEntity
        datacenters: List[str] = [dc.name for dc in self.datacenters]

        return datacenters

    # ----- list clusters by datacenter
    async def a_list_clusters(self, dc_name: str) -> Union[List[str] | Any]:
        """ Get the list of clusters in a datacenter

        - Args:
            dc_name (str): Name of the datacenter

        - Returns:
            Union[List[str] | Any]: List of cluster names or None if not found
        """

        print(Style.NORMAL + Back.BLACK + Fore.WHITE + "\treturn clusters name (asyncio)")

        datacenter = await self.a_get_datacenter(dc_name)

        loop = asyncio.get_event_loop()

        clusters: List[str] = await loop.run_in_executor(None, lambda: [clt.name for clt in datacenter.hostFolder.childEntity if isinstance(clt, vim.ClusterComputeResource)])
        return clusters

    # ----- list datastores by datacenter
    async def a_list_datastores(self, dc_name: str) -> Union[List[str] | Any]:
        """ Get the list of datastores in a datacenter

        - Args:
            dc_name (str): Name of the datacenter

        - Returns:
            Union[List[str] | Any]: List of datastore names or None if not found
        """

        print(Style.NORMAL + Back.BLACK + Fore.WHITE + "\treturn datastores name (asyncio)")

        datacenter = await self.a_get_datacenter(dc_name)

        loop = asyncio.get_event_loop()

        datastores: List[str] = await loop.run_in_executor(None, lambda: [ds.name for ds in datacenter.datastore])
        return datastores

    # ----- list distributed portgroups by datacenter
    async def a_list_distributed_portgroups(self, dc_name: str) -> Union[List[str] | Any]:
        """ Get the list of distributed port groups in a datacenter

        - Args:
            dc_name (str): Name of the datacenter

        - Returns:
            Union[List[str] | Any]: List of distributed port group names or None if not found
        """
        
        print(Style.NORMAL + Back.BLACK + Fore.WHITE + "\treturn distributed port groups name (asyncio)")

        datacenter = await self.a_get_datacenter(dc_name)

        loop = asyncio.get_event_loop()

        portgroups: List[str] = await loop.run_in_executor(None, lambda: [dvpg.name for dvpg in datacenter.networkFolder.childEntity if isinstance(dvpg, vim.dvs.DistributedVirtualPortgroup)])
        return portgroups
