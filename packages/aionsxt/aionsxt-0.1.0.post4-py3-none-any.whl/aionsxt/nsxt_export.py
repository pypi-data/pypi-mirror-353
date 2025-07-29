"""
# Created : 2024-02-19
# Last Modified : 2025-06-03
# Product : VMC / NSX-T
# Description : NsxtAsync and NsxtExport Classes/Methods
"""

__author__ = 'Antoine Richado'
__version__ = '0.1.0'
__copyright__ = ''

import configparser
import os
import json
import aiofiles
import glob
import urllib3
import time

from aiohttp import ClientSession, ClientResponseError, ClientTimeout
from zipfile import ZipFile
from typing import Union, Dict, Tuple, List, Optional, Any
from datetime import datetime
from colorama import Fore, Back, Style

urllib3.disable_warnings()

# ----- class nsxt export methods
class NsxtExport:
    """a class to handle importing parts of VMC NSX-T"""

    def __init__(self, **kwargs: Any) -> None:
        """
        - *args allows to pass a varying number of -positional arguments-
        - **kwargs allows to pass a varying number of -keyword (or named)-
        - unpacking operator (*) or (**)
        """

        self.nsxmgr = kwargs['NSX_MGR']
        self.headers = kwargs['NSX_HEADERS']
        self.nsxurl = kwargs['NSX_URL']
        self.config_path = kwargs['INI_PATH']
        self.export_path = kwargs['EXPORT_PATH']
        self.domain = 'default'

        self.session = ClientSession()
        self.timeout = ClientTimeout(total=20)  # 20 secs before api call timeout

        """ export files names """
        self.script_path = os.path.dirname(os.path.realpath(__file__))  # current execution script path
        self.export_purge_before_run: Union[bool, None] = True  # purge any previously exported JSON files (overwrite by aio_config.ini)
        self.export_history: Union[bool, None] = True  # export_history is set to True, how many previous zip files to keep before deleting the oldest file
        self.max_export_history_files = ""  # how many previous zip files to keep before deleting the oldest file? -1 for unlimite

        """ nsx-t manager """
        self.mgw_services_fname = ""  # manager services export filename
        self.mgw_context_profiles_fname = ""  # manager context profiles export filename

        """ nsx-t policy """
        self.cgw_tags_fname = ""  # policy tags export filename
        self.cgw_tags_detailed_fname = ""  # policy objects assigned per tags
        self.cgw_services_fname = ""  # policy services export filename
        self.cgw_context_profiles_fname = ""  # policy context profiles export filename

        """ export security rules """
        self.cgw_gateway_policies_export = True
        self.cgw_forwarding_policies_export = True
        self.cgw_gateway_policies_fname = ""  # gateway policies rules
        self.cgw_forwarding_policies_fname = ""  # forwarding policies rules

        self.dfw_security_policies_export = True  # dfw for gmw and cgw use api definition "security-policies" to export dfw
        self.dfw_securepolicy_sections_fname = ""  # distributed firewall sections filename (security policy)
        self.dwf_securepolicy_sections_rules_fname = ""  # dfw security policies detailed rules

        self.cgw_segments_export = True  # export nsx-t segments
        self.cgw_segments_fname = ""  # nsxt segments export filename
        self.cgw_segments_profiles_fname = ""  # nsxt segments profiles export filename
        self.mgw_groups_fname = ""  # management groups export filename
        self.cgw_groups_fname = ""  # compute gateway groups export filename
        self.mgw_firewall_export = True  # management gateway firewall rules export (overwrite by aio_config.ini)
        self.cgw_firewall_export = True  # compute gateway firewall rules export (overwrite by aio_config.ini)
        self.mgw_fname = ""  # management gateway firewall rules

        self.__config_loader()

    # ----- load options from aio_config files
    def __config_loader(self) -> None:
        """ load all configuration variables from aio_config.ini and aws.ini """
        
        aio_config = configparser.ConfigParser()
        aio_config.read(self.config_path)

        # ----- aio_config.ini options
        """ aio_config.ini options """
        self.export_folder                          = aio_config.get("exportConfig", "export_folder")
        #self.export_path = aio_config.get("exportConfig", "export_path")

        """ keep previous versions of the exported JSON files """
        self.export_history                         = self.__load_config_bool(aio_config, "exportConfig", "export_history")

        """ Purge any previously exported JSON files before a new export is run? """
        self.export_purge_before_run                = self.__load_config_bool(aio_config, "exportConfig", "export_purge_before_run")

        """ If export_history is true, do you want to purge the exported JSON files after they are zipped into the archive? """
        self.export_purge_after_zip                 = self.__load_config_bool(aio_config, "exportConfig", "export_purge_after_zip")

        """ If export_history is set to True, how many previous zip files to keep before deleting the oldest file? -1 for unlimited """
        self.max_export_history_files               = aio_config.get("exportConfig", "max_export_history_files")

        """ os where python run or aws s3 bucket """
        self.export_type                            = aio_config.get("exportConfig", "export_type")

        """ nsx-t virtual machines tags """
        self.cgw_tags_fname                         = aio_config.get("exportConfig", "cgw_tags_fname")
        self.cgw_tags_detailed_fname                = aio_config.get("exportConfig", "cgw_tags_detailed_fname")

        """ nsx-t virtual machines """
        self.vm_fname                               = aio_config.get("exportConfig", "vm_fname")

        """ Services """
        self.mgw_services_fname                     = aio_config.get("exportConfig", "mgw_services_fname")
        self.cgw_services_fname                     = aio_config.get("exportConfig", "cgw_services_fname")

        """ security groups """
        self.mgw_groups_fname                       = aio_config.get("exportConfig", "mgw_groups_fname")
        self.cgw_groups_fname                       = aio_config.get("exportConfig", "cgw_groups_fname")

        """ Context Profiles """
        self.mgw_context_profiles_fname             = aio_config.get("exportConfig", "mgw_context_profiles_fname")
        self.cgw_context_profiles_fname             = aio_config.get("exportConfig", "cgw_context_profiles_fname")

        """ management gateway MGW """
        self.mgw_fname                              = aio_config.get("exportConfig", "mgw_fname")

        """ network segments CGW """
        self.cgw_segments_fname                     = aio_config.get("exportConfig", "cgw_segments_fname")
        self.cgw_segments_profiles_fname            = aio_config.get("exportConfig", "cgw_segments_profiles_fname")

        """ policy rules """
        self.cgw_gateway_policies_fname             = aio_config.get("exportConfig", "cgw_gateway_policies_fname")
        self.cgw_forwarding_policies_fname          = aio_config.get("exportConfig", "cgw_forwarding_policies_fname")

        """ distributed firewall rules """
        self.dfw_securepolicy_sections_fname        = aio_config.get("exportConfig", "dfw_securepolicy_sections_fname")
        self.dfw_securepolicy_sections_rules_fname  = aio_config.get("exportConfig", "dfw_securepolicy_sections_rules_fname")

    # ----- get tags and tags details
    async def export_tags(self) -> Union[Tuple[List[Any], Dict[Any, Any]], None]:
        """ 
        ClientSession.get
        export policy inventory tags and assigned objects
        nsx manager -> policy -> inventory -> tags
        """

        tags = []

        uripath = '/policy/api/v1/infra/tags'

        # return a list of found tags
        tags = await self.get_object_definition(uripath, 'nsx policy tags')

        if tags:

            print(Style.NORMAL + Back.BLACK + Fore.YELLOW + "\t- exporting nsx policy objects assigned to tags")

            # dictionary of assigned objects to tags
            tag_assigned_objects = {}  # dict()

            for tag in tags:
                tagscope = tag['scope']
                tagname = tag['tag']

                apiurl = f'{self.nsxurl}/policy/api/v1/infra/tags/effective-resources?scope={tagscope}&tag={tagname}'

                try:
                    response = await self.session.get(apiurl, headers=self.headers, ssl=False, timeout=self.timeout)
                    # raise an aiohttp.ClientResponseError
                    response.raise_for_status()

                    json_response = await response.json()
                    tag_assigned_objects[tag["tag"]] = json_response['results']
                except ClientResponseError as e:
                    print(Style.NORMAL + Back.BLACK + Fore.RED + f'\t- error getting tag assigned objects: {e.status} {e.message}')

            return tags, tag_assigned_objects

        return None

    # ----- export virtual machines iventory
    async def export_virtual_machines(self) -> List[str]:
        """
        ClientSession.post
        export virtual machines
        nsx manager -> policy -> inventory -> virtual machines
        """

        print(Style.NORMAL + Back.BLACK + Fore.YELLOW + "\t- exporting nsx policy virtual machines")

        resultlist = []
        apiurl: Any = None
        cursor = None
        lastcursor = None

        uripath = '/policy/api/v1/search/aggregate?page_size=100&sort_by=display_name&sort_ascending=true'

        payload = {"primary": {"resource_type": "VirtualMachine"}, "context": "projects:ALL", "data_source": "ALL"}

        # while "cursor" in json_response:
        while True:
            if not cursor:
                apiurl = f'{self.nsxurl}{uripath}'
            if cursor:
                apiurl = f'{self.nsxurl}{uripath}&cursor={cursor}'

            response = await self.session.post(apiurl, headers=self.headers, data=json.dumps(payload), ssl=False, timeout=self.timeout)
            # raise an aiohttp.ClientResponseError
            response.raise_for_status()

            json_response = await response.json()  # async operation

            # valide is json response get a cursor
            cursor = json_response.get('cursor', None)

            if cursor is None or cursor == lastcursor:
                # no cursor found so we exit the while True loop or sometimes the next cursor 
                # is the same that the previous one so we need to exit too
                resultlist.extend(json_response['results'])
                break

            # if the cursor is different from the last one then we extent the list
            resultlist.extend(json_response['results'])
            lastcursor = cursor

        return resultlist

    # ----- export policy networking segments list
    async def export_segments(self) -> Union[Tuple[List[Any], Dict[Any, Any]], None]:
        """
        ClientSession.get
        export policy networking nsx segments
        nsx manager -> policy -> networking -> segments -> segment list
        """

        segments = []

        uripath = '/policy/api/v1/infra/segments'

        segments = await self.get_object_definition(uripath, 'nsx policy segments')

        if segments:

            print(Style.NORMAL + Back.BLACK + Fore.YELLOW + "\t- exporting nsx policy segment details")

            segments_profiles = {}

            for segment in segments:

                apiurl = f'{self.nsxurl}/policy/api/v1/infra/segments/{segment["id"]}/segment-security-profile-binding-maps'

                try:
                    response = await self.session.get(apiurl, headers=self.headers, ssl=False, timeout=self.timeout)
                    # raise an aiohttp.ClientResponseError
                    response.raise_for_status()

                    json_response = await response.json()
                    segments = json_response['results']
                    segment_id = segment['id']
                    displayname = segment['display_name']
                    index = f'{segment_id}=>{displayname}'
                    segments_profiles[index] = json_response['results']
                except ClientResponseError as e:
                    print(Style.NORMAL + Back.BLACK + Fore.RED + f'\t- error getting segment details: {e.status} {e.message}')

            return segments, segments_profiles

        return None

    # ----- export distributed firewall rules (security-policies api definition)
    async def export_dfw_rules(self) -> Union[Tuple[List[Any], Dict[Any, Any]], None]:
        """
        export policy security distributed firewall rules to a JSON file
        Policy -> Security -> Policy Management -> Distributed Firewall -> Category Specific Rules
        """

        dfw_rules = []

        uripath = f'/policy/api/v1/infra/domains/{self.domain}/security-policies'

        dfw_rules = await self.get_object_definition(uripath, 'nsx policy dfw rules')

        if dfw_rules:

            print(Style.NORMAL + Back.BLACK + Fore.YELLOW + "\t- exporting nsx policy dfw rules details")

            dfw_rules_detailed = {}

            # for each policy we find detailed rules (cmap -> communication-maps)
            for cmap in dfw_rules:

                # sleep for 1/10 of a second
                time.sleep(1 / 10)

                apiurl = f'{self.nsxurl}/policy/api/v1/infra/domains/{self.domain}/security-policies/{cmap["id"]}/rules'

                try:
                    response = await self.session.get(apiurl, headers=self.headers, ssl=False, timeout=self.timeout)
                    # raise an aiohttp.ClientResponseError
                    response.raise_for_status()

                    json_response = await response.json()
                    dfw_rules_detailed[cmap["id"]] = json_response
                except ClientResponseError as e:
                    print(Style.NORMAL + Back.BLACK + Fore.RED + f'\t- error getting fw rule details: {e.status} {e.message}')

            return dfw_rules, dfw_rules_detailed

        return None

    # ----- write json to file
    async def write_json_to_file(self, filename: str, data: Any) -> None:
        """ Write data to a JSON file.

        - Args:
            filename (str): The name of the file to write to.
            data (Any): The data to write to the file.
        """
        if not filename:
            print(Style.NORMAL + Back.BLACK + Fore.RED + f'\t- invalid filename: {filename}')
            return
        if not data:
            print(Style.NORMAL + Back.BLACK + Fore.RED + f'\t- no data to write to file: {filename}')
            return
        
        async with aiofiles.open(filename, 'w') as outfile:
            print(Style.NORMAL + Back.BLACK + Fore.YELLOW + f'\t- writing to json file {filename}')
            await outfile.write(json.dumps(data, indent=4))

    # ----- load options from config files
    def purge_json_files(self) -> bool:
        """ removes the JSON export files before a new export """

        # ----- glob search \\*.json
        files = glob.glob(f'{self.export_path}\\{self.export_folder}\\*.json', recursive=True)
        returnval = True
        for file_path in files:
            try:
                os.remove(file_path)
                print(Style.NORMAL + Back.BLACK + Fore.MAGENTA + 'Deleted', file_path)
            except Exception as e:
                print(Style.NORMAL + Back.BLACK + Fore.RED + 'Error deleting', file_path)
                print(str(e))
                returnval = False

        return returnval

    # ----- zip json files
    def zip_json_files(self) -> Any:
        """ creates a zipfile of exported JSON files """

        files = glob.glob(f'{self.export_path}\\{self.export_folder}\\*.json')
        curenttime = datetime.now()
        # filename example: 2020-12-02_09-57-13_json-export.zip
        filename = f'{self.nsxmgr}_{curenttime.strftime("%Y-%m-%d_%H-%M-%S")}_json-export.zip'

        try:
            print(Style.BRIGHT + Back.BLACK + Fore.BLUE + f'\n\t-> create export zip file name: {filename}')

            zip_path = f'{self.export_path}\\{self.export_folder}\\{filename}'
            with ZipFile(zip_path, 'w') as zip_instance:
                for file in files:
                    zip_instance.write(file, os.path.basename(file))
            return filename
        except Exception as e:
            print('error writing zipfile: ', str(e))
            return False

    # ----- purge zip files
    def purge_zip_files(self) -> bool:
        """ clean up old zipfiles """

        if int(self.max_export_history_files) == -1:
            print('maximum zips configured as unlimited.')
            return True
        retval = True
        files = glob.glob(f'{self.export_path}\\{self.export_folder}\\*.zip')

        # return the time of last modification
        files.sort(key=os.path.getmtime)
        print(len(files), "zipfiles found with a configured maximum of", self.max_export_history_files)

        if len(files) > int(self.max_export_history_files):
            num_to_purge = len(files) - int(self.max_export_history_files)
            print('need to purge:', num_to_purge)

            # files[0:num_to_purge] is a slicing notation that specifies a sub-list containing
            # the elements of files from index 0 to index num_to_purge (the first x elements)
            for file in files[0:num_to_purge]:
                try:
                    os.remove(file)
                    print('purged', file)
                except Exception as e:
                    retval = False
                    print('error purging:', file, str(e))
        return retval

    # ----- purge json folders
    def purge_json_folders(self) -> bool:
        """ clean up older folders """

        if int(self.max_export_history_files) == -1:
            print('maximum folders configured as unlimited.')
            return True
        retval = True
        folders = glob.glob(f'{self.export_path}\\{self.export_folder}\\*')

        # return the time of last modification
        folders.sort(key=os.path.getmtime)
        print(len(folders), "folder(s) found with a configured maximum of", self.max_export_history_files)

        if len(folders) > int(self.max_export_history_files):
            num_to_purge = len(folders) - int(self.max_export_history_files)
            print('need to purge:', num_to_purge)

            # folders[0:num_to_purge] is a slicing notation that specifies a sub-list containing
            # the elements of folders from index 0 to index num_to_purge (the first x elements)
            for folder in folders[0:num_to_purge]:
                # remove files from folder before removing folder
                for file in os.listdir(folder):
                    os.remove(f'{folder}\\{file}')
                try:
                    os.rmdir(folder)
                    print('purged', folder)
                except Exception as e:
                    retval = False
                    print('error purging:', folder, str(e))
        return retval

    # ----- export nsx objects definitions
    async def get_object_definition(self, uripath: str, message: str) -> list[Any]:
        """ Get NSX object definitions.

        - Args:
            uripath (str): The API endpoint URI path.
            message (str): A message describing the export operation.

        - Returns:
            list[Any]: A list of NSX object definitions.
        """

        print(Style.NORMAL + Back.BLACK + Fore.YELLOW + f'\t- exporting {message}')

        resultlist = []
        apiurl: Any = None
        cursor = None
        lastcursor = None

        # while "cursor" in json_response:
        while True:
            if not cursor:
                apiurl = f'{self.nsxurl}{uripath}'
            if cursor:
                apiurl = f'{self.nsxurl}{uripath}?page_size=100&cursor={cursor}'

            try:
                response = await self.session.get(apiurl, headers=self.headers, ssl=False, timeout=self.timeout)
                # raise an aiohttp.ClientResponseError
                response.raise_for_status()

                json_response = await response.json()  # async operation

                # valide is json response get a cursor
                cursor = json_response.get('cursor', None)

                if cursor is None or cursor == lastcursor:
                    # no cursor found so we exit the while True loop or sometimes the next cursor
                    # is the same that the previous one so we need to exit too
                    resultlist.extend(json_response['results'])
                    break

                # if the cursor is different from the last one then we extent the list
                resultlist.extend(json_response['results'])
                lastcursor = cursor

            except ClientResponseError as e:
                print(Style.NORMAL + Back.BLACK + Fore.RED + f'\t- error getting {message}: {e.status} {e.message}')

        return resultlist

    # ----- convert true/false text as boolean
    def __load_config_bool(self, config: Any, section: Any, key: Any) -> Optional[bool]:
        """ Load a True/False flag from the config file.

        - Args:
            config (Any): The config object.
            section (Any): The section in the config.
            key (Any): The key to look for.

        - Returns:
            Optional[bool]: The boolean value or None if not found.
        """
        
        if not config.has_section(section):
            print(Style.NORMAL + Back.BLACK + Fore.RED + f'\t- section {section} not found in config file')
            return None
        
        configoption = config.get(section, key)

        if configoption.lower() == 'true':
            return True
        if configoption.lower() == 'false':
            return False

        return None
