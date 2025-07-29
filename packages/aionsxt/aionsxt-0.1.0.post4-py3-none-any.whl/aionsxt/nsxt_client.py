"""
# Created : 2024-02-19
# Last Modified : 2025-03-14
# Product : VMC / NSX-T
# Description : NsxtAsync and NsxtExport Classes/Methods
"""

__author__ = 'Antoine Richado'
__version__ = '0.1.0'
__copyright__ = ''

import json
import aiohttp
import urllib3

from typing import Union, Self, Dict, List, Any
from datetime import datetime
from colorama import Fore, Back, Style

urllib3.disable_warnings()

# ----- parent class and methods
class AsyncNsxt():
    """ this class uses aiohttp.ClientSession library to make ASYNC api requests """

    # __init__ constructor method
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """
        - *args allows to pass a varying number of -positional arguments-
        - **kwargs allows to pass a varying number of -keyword (or named)-
        - unpacking operator (*) or (**)
        """

        username                     = str(kwargs['NSX_USER'])
        password                     = str(kwargs['NSX_PASS'])
        self.mgr_ip                  = kwargs['NSX_MGR']
        self.port                    = kwargs['NSX_PORT']
        self.path                    = kwargs['NSX_PATH']  # /api
        self.nsx_url                 = f'https://{self.mgr_ip}:{self.port}'
        self.auth: Dict[str, Any]    = {'j_username': username, 'j_password': password}
        self.headers: Dict[str, str] = {}

        timeout                     = aiohttp.ClientTimeout(total=20)
        connector                   = aiohttp.TCPConnector(ssl=False)
        self.session                = aiohttp.ClientSession(connector=connector, timeout=timeout)

    # ----- open session
    async def __aenter__(self) -> Self:
        """
        aiohttp.ClientSession.post
        authenticates nsx and create session object for subsequent api calls
        """
        login_url = f'{self.nsx_url}/api/session/create'

        # connection to nsx
        async with self.session.post(login_url, data=self.auth) as response:

            # raise an aiohttp.ClientResponseError
            response.raise_for_status()

            cookie_var = response.headers['Set-Cookie']
            token_var = response.headers['X-XSRF-TOKEN']

            self.headers = {'Cookie': cookie_var, 'X-XSRF-TOKEN': token_var, "content-type": "application/json"}

            lastjson_response = f'API Call Status {response.status}'
            print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'logged in to nsx {self.mgr_ip}', end=" (enter context manager & asyncio) - ")
            print(lastjson_response)

            return self

    # ----- close session
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        aiohttp.ClientSession.close
        delete nsx session
        """

        logout_url = f'{self.nsx_url}/api/session/destroy'

        async with self.session.delete(logout_url) as response:

            # raise an aiohttp.ClientResponseError
            response.raise_for_status()

            lastjson_response = f'API Call Status {response.status}'
            print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'logged out from nsx {self.mgr_ip}', end=" (exiting context manager & asyncio) - ")
            print(lastjson_response)

            await self.session.close()

    # ----- login to nsx-t manager
    async def a_login(self) -> Self:
        """
        aiohttp.ClientSession.post
        authenticates nsx and create session object for subsequent api calls
        """

        login_url = f'{self.nsx_url}/api/session/create'

        response = await self.session.post(login_url, data=self.auth)

        response.raise_for_status()

        cookie_var = response.headers['Set-Cookie']
        token_var = response.headers['X-XSRF-TOKEN']

        self.headers = {'Cookie': cookie_var, 'X-XSRF-TOKEN': token_var, "content-type": "application/json"}

        lastjson_response = f'API Call Status {response.status}'
        print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'logged in to nsx {self.mgr_ip}', end=" (asyncio) - ")
        print(lastjson_response)

        return self

    # ----- close ClientSession()
    async def a_logout(self) -> None:
        """
        aiohttp.ClientSession.close
        delete nsx session
        """

        logout_url = f'{self.nsx_url}/api/session/destroy'

        response = await self.session.delete(logout_url)

        # raise an aiohttp.ClientResponseError
        response.raise_for_status()

        lastjson_response = f'API Call Status {response.status}'
        print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'logged out from nsx {self.mgr_ip}', end=" (asyncio) - ")
        print(lastjson_response)

        await self.session.close()

    # ----- get registration token
    async def a_get_registration_token(self, expiration_time: datetime) -> Any:
        """ Get NSX registration token for adding new NSX Edge or other appliances

        - Args:
            expiration_time (datetime): Expiration time for the token

        - Returns:
            Any: The registration token
        """
        
        print(Style.NORMAL + Back.BLACK + Fore.YELLOW + "getting nsx registration token (asyncio)")
        apiurl = f'{self.nsx_url}/api/v1/aaa/registration-token'

        # change default token expiration time and convert to text
        text_time = expiration_time.strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "expires_at": text_time
        }
        
        response = await self.session.post(apiurl, headers=self.headers, data=json.dumps(payload))

        # raise an aiohttp.ClientResponseError
        response.raise_for_status()

        # json.loads(response.text)
        json_response = await response.json()
        print("Response JSON:", json_response["token"])  # Debug print
        return json_response["token"]

    # ----- get vms
    async def a_get_all_vms(self) -> Union[Dict[str, Any], Any]:
        """ Returns all vms found in nsx-t manager

        - Returns:
            Dict[str, Any]: JSON response containing all vms
        """
        
        print(Style.NORMAL + Back.BLACK + Fore.YELLOW + "getting all vms (asyncio)")
        
        # GET "/api/v1/fabric/virtual-machines?limit=1000&offset=0&sort_by=display_name&sort_ascending=true"
        apiurl = f'{self.nsx_url}/api/v1/fabric/virtual-machines'

        response = await self.session.get(apiurl, headers=self.headers)

        # raise an aiohttp.ClientResponseError
        response.raise_for_status()

        return await response.json()

    # ----- get vm info
    async def a_get_vm_info(self, instance_name: str) -> Union[Dict[str, Any], Any]:
        """ Returns vm info for a specific vm instance name

        - Args:
            instance_name (str): Name of the virtual machine instance
        - Returns:
            Dict[str, Any]: JSON response containing vm info
        """
        
        print(Style.NORMAL + Back.BLACK + Fore.YELLOW + f"getting vm info for {instance_name} (asyncio)")
        
        # search query for vm by display_name
        apiurl = f'{self.nsx_url}/api/v1/search/query?query=resource_type:VirtualMachine AND display_name:{instance_name}'

        response = await self.session.get(apiurl, headers=self.headers)

        # raise an aiohttp.ClientResponseError
        response.raise_for_status()

        return await response.json()

    # ----- get vm tags
    async def a_get_vm_tags(self, instance_name: str) -> Union[List[Any], None]:
        """ Returns vm tags for a specific vm instance name

        - Args:
            instance_name (str): Name of the virtual machine instance
        - Returns:
            Union[List[Any], None]: List of tags or None if not found
        """

        print(Style.NORMAL + Back.BLACK + Fore.YELLOW + f"getting vm tags for {instance_name} (asyncio)")
        
        vm_info = await self.a_get_vm_info(instance_name)
        info_result = vm_info['results']

        if info_result:

            try:
                tags: List[Any] = info_result[0]["tags"]
                print(Style.NORMAL + Back.BLACK + Fore.GREEN + "\t- vm's tags found (asyncio)")
                return tags
            except Exception as e:
                print(Style.NORMAL + Back.BLACK + Fore.YELLOW + f'\t- no {e} found')

        else:
            print(Style.NORMAL + Back.BLACK + Fore.RED + '\t- nsx: vm not found')

        return None

    # ----- add vm tags
    async def a_add_deny_tag(self, instance_name: str) -> Union[Dict[str, Any], Any]:
        """ Adds a deny tag to a specific vm instance name

        - Args:
            instance_name (str): Name of the virtual machine instance
        - Returns:
            Union[Dict[str, Any], Any]: JSON response or None if successful
        """

        print(Style.NORMAL + Back.BLACK + Fore.YELLOW + "adding tags (asyncio)")

        vm_info = await self.a_get_vm_info(instance_name)
        info_result = vm_info['results']

        if info_result:
            instance_id = info_result[0]["external_id"]

            # POST "/api/v1/fabric/virtual-machines?action=add_tags"
            # POST "/api/v1/fabric/virtual-machines?action=update_tags"
            # params = 'action=add_tags'
            apiurl = f'{self.nsx_url}/api/v1/fabric/virtual-machines?action=add_tags'

            payload = {
                "external_id": instance_id,
                "tags": [
                    {
                        "scope": "srv",
                        "tag": "deny"
                    },
                ]
            }

            response = await self.session.post(apiurl, headers=self.headers, data=json.dumps(payload))

            # raise an aiohttp.ClientResponseError
            response.raise_for_status()

            if response.status == 204:
                print(Style.NORMAL + Back.BLACK + Fore.WHITE + f'\t-> nsx tags on {instance_name} assigned')                
                return None  # 204 No Content, nothing to parse

            return await response.json()

        print(Style.NORMAL + Back.BLACK + Fore.RED + "vm not found in nsx")
        return None
