import requests   # Imports the 'requests' library for making HTTP requests.
import base64     # Imports the 'base64' library for encoding and decoding data using Base64 encoding.
import json       # Imports the 'json' library to work with JSON data.
import pandas as pd  # Imports the 'pandas' library for data manipulation, especially working with DataFrames.
import time       # Imports the 'time' library for time-related functions like sleep.

class AuvikNetworksConnection:
    BASE_URL = "https://auvikapi.eu1.my.auvik.com/v1"  # Sets the base URL for Auvik's API.

    # Define endpoints as class constants in a dictionary
    ENDPOINTS = {   # Defines the API endpoints for different operations as constants.
        'tenants': '/tenants',                    # Endpoint for retrieving tenants.
        'tenant_details': '/tenants/detail',      # Endpoint for retrieving tenant details.
        'device_info': '/inventory/device/info',  # Endpoint for retrieving device information.
        'authentication': '/authentication/verify', # Endpoint for verifying authentication.
        'device_availability_statistics': '/stat/deviceAvailability/{statId}', # Endpoint for uptime information
        'device_notes': '/inventory/entity/note'
    }

    def __init__(self, username: str = None, password: str = None):  
        """ Initializes the AuvikNetworks connection. 
            Args: 
                username (str): The Auvik username. 
                password (str): The Auvik API token.
        """
        self.username = username   # Stores the provided username in the instance variable.
        self.password = password   # Stores the provided password (API token) in the instance variable.

        if not self.username or not self.password:  # Checks if username or password is missing.
            raise ValueError("Username and password must be provided.")  # Raises an error if any credential is missing.

        self.headers = {}   # Initializes an empty dictionary to store HTTP request headers.
        self.page_size = 100  # Sets the default page size for API requests.

        self.get_access_token()  # Calls the method to get the access token (authenticates).

    def get_access_token(self):  # Defines the method to authenticate and get the access token.
        """
        Establishes the connection to Auvik by authenticating and setting up the session.
        credentials needs to be stored in utf-8.
        """
        creds = f"{self.username}:{self.password}"  # Combines username and password into a string.
        creds_b64 = base64.b64encode(creds.encode('utf-8')).decode('utf-8')  # Encodes the credentials using Base64.
        self.headers = {
            "Authorization": f"Basic {creds_b64}"  # Sets the 'Authorization' header for HTTP requests using the encoded credentials.
        }

        login_uri = f"{self.BASE_URL}{self.ENDPOINTS['authentication']}"  # Creates the full URL for authentication.
        response = requests.get(login_uri, headers=self.headers)  # Sends a GET request to the login URL with headers.

        response_text = response.text  # Retrieves the response content as text.

        if response.status_code != 200:
            raise Exception(f"Authentication failed: {response.text}")
        print("Authentication successful.")

    def _handle_output(self, response_data, json_output: bool = False):
        """
        Handles the output format for API responses.

        Args:
            response_data (dict or list): The data returned from an API response.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame.
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The formatted output based on the json_output flag.
        """
        if json_output:
            return json.dumps(response_data, indent=4)  # Return as a JSON string
        else:
            df = pd.json_normalize(response_data)  # Convert JSON data to a pandas DataFrame
            return df  # Return DataFrame


    def get(self, endpoint: str, params: dict = None, include_detail: bool = False, debug: bool = False):
        """
        Voert een geauthentiseerde GET-request uit naar de Auvik API met cursor-based paginatie en retry-logica.

        Args:
            endpoint (str): Het API-endpoint (relatief pad).
            params (dict): Optionele queryparameters (zoals {'page[first]': 100}).
            include_detail (bool): Combineer 'data' en 'included' tot één set per item.
            debug (bool): Print debugging-informatie.

        Returns:
            list: Gecombineerde lijst met resultaten van alle pagina's.
        """
        base_url = f"{self.BASE_URL}{endpoint}"
        all_data = []
        retries = 3
        retry_delay = 1  # seconden

        # Eerste request: gebruik base_url + params
        next_url = base_url
        use_params = params.copy() if params else {}

        while next_url:
            for attempt in range(retries):
                try:
                    if debug:
                        print(f"[Request] {next_url}")
                        if use_params:
                            print(f"[Params] {use_params}")

                    response = requests.get(next_url, headers=self.headers, params=use_params)

                    if response.status_code != 200:
                        print(f"[Error {response.status_code}] {response.text}")
                        break  # Verlaat retry-loop

                    data = response.json()

                    page_data = data.get("data", [])
                    included = data.get("included", [])
                    processed_page = []

                    if include_detail:
                        data_dict = {item["id"]: item for item in page_data}
                        included_dict = {item["id"]: item for item in included}

                        for item_id, item_data in data_dict.items():
                            combined_item = item_data.copy()
                            relationships = item_data.get("relationships", {})
                            for rel_key, rel_val in relationships.items():
                                rel_items = rel_val.get("data", [])
                                if isinstance(rel_items, dict):
                                    rel_items = [rel_items]
                                for rel in rel_items:
                                    rel_id = rel.get("id")
                                    if rel_id in included_dict:
                                        combined_item[f"{rel_key}_attributes"] = included_dict[rel_id].get("attributes", {})
                                        combined_item[f"{rel_key}_links"] = included_dict[rel_id].get("links", {})
                            processed_page.append(combined_item)
                    else:
                        processed_page = page_data

                    all_data.extend(processed_page)

                    # Volgende pagina ophalen via link['next']
                    next_url = data.get("links", {}).get("next")
                    use_params = None  # Niet meer nodig, want next_url bevat alle queryparams

                    if debug and next_url:
                        print(f"[Next] {next_url}")
                    break  # Success, verlaat retry-loop

                except requests.exceptions.RequestException as e:
                    print(f"[Exception] {e}")
                    if attempt < retries - 1:
                        print(f"Retrying in {retry_delay} seconds (attempt {attempt + 2}/{retries})...")
                        time.sleep(retry_delay)
                    else:
                        print("Max retries reached. Aborting.")
                        return all_data

                except ValueError:
                    print("[JSON Error] Ongeldige JSON-respons ontvangen.")
                    print(response.text)
                    return all_data

            if not next_url:
                break

        return all_data


    def get_tenants(self, json_output: bool = False):  # Method to get tenant information from Auvik.
        """
        Retrieves tenant information from Auvik.

        Args:
            json_output (bool): If True, returns the output in JSON format as a string. Defaults to False.

        Returns:
            A DataFrame containing tenant information. If `json_output` is True, returns the data in JSON string format instead.
        """

        endpoint = self.ENDPOINTS['tenants']

        response_data = self.get(endpoint)  # Calls the 'get' method with the tenants endpoint.
        return self._handle_output(response_data, json_output)  # Returns the processed output as JSON or DataFrame.

    def get_tenant_details(self, domain_prefix: str, json_output: bool = False):  # Method to get detailed info for a tenant.
        """
        Retrieves detailed information for a specific tenant.

        Args:
            domain_prefix (str): The tenant domain prefix.
            json_output (bool): If True, returns the output in JSON format as a string. Defaults to False.

        Returns:
            A DataFrame containing tenant details. If `json_output` is True, returns the data in JSON string format instead.
        """
        endpoint = self.ENDPOINTS['tenant_details']
        params = {
            "tenantDomainPrefix": domain_prefix  # Sets the tenant domain prefix parameter.
        }
        response_data = self.get(endpoint, params=params)  # Calls the 'get' method with the tenant details endpoint and parameters.
        return self._handle_output(response_data, json_output)  # Returns the processed output as JSON or DataFrame.

    def get_auvik_devices_info(self, tenant_id: str = None, device_type: str = None, include_detail: bool = False, json_output: bool = False):  # Method to retrieve device info.
        """
        Retrieves device information from Auvik.

        Args:
            tenant_id (str): The tenant ID.
            filter[deviceType]: If given, it only shows devicetypes. Diffrent types are: "unknown" "switch" "l3Switch" "router" "accessPoint" 
                "firewall" "workstation" "server" "storage" "printer" "copier" "hypervisor" "multimedia" "phone" "tablet" "handheld" "virtualAppliance" "bridge" 
                "controller" "hub" "modem" "ups" "module" "loadBalancer" "camera" "telecommunications" "packetProcessor" "chassis" "airConditioner" "virtualMachine" "pdu" "ipPhone" 
                "backhaul" "internetOfThings" "voipSwitch" "stack" "backupDevice" "timeClock" "lightingDevice" "audioVisual" "securityAppliance" "utm" "alarm" "buildingManagement" "ipmi" "thinAccessPoint" "thinClient"
            include_detail (bool): If true, returns device detail fields: discoveryStatus, manageStatus, trafficInsightsStatus.
            json_output (bool): If True, returns the output in JSON format as a string. Defaults to False.

        Returns:
            A DataFrame containing device information. If `json_output` is True, returns the data in JSON string format instead.
        """
        endpoint = self.ENDPOINTS['device_info']
        params = {
            "tenants": tenant_id,  # Sets the tenant ID parameter.
            "filter[deviceType]": device_type  # Sets the filter for device type.
        }

        if include_detail:  # If include_detail is True, adds additional fields to the request.
            params['include'] = 'deviceDetail'  # Includes detailed information in the response.
            params['fields[deviceDetail]'] = 'discoveryStatus,manageStatus,trafficInsightsStatus,tenant'  # Specifies which detail fields to return.

        response_data = self.get(endpoint, params=params, include_detail=True)  # Calls the 'get' method with the device info endpoint and parameters.
        return self._handle_output(response_data, json_output)  # Returns the processed output as JSON or DataFrame.
    
    def get_device_availability_statistics(self, device_id, statistic_type="uptime", from_time=None, until_time=None, interval = "day", json_output=False):
        """
        Retrieves device availability statistics from Auvik.

        Args:
            device_id (str): The device ID.
            statistic_type (str): Type of statistic (default: "uptime" other option: "outage" ).
            Interval (str): Interval type. Default "Day". Other options: "minute" "hour"
            from_time: From date in format: 2025-01-01T01:00:00.000Z
            until_time: Until date in format: 2025-01-01T01:00:00.000Z
            json_output (bool): If True, returns output in JSON format.

        Returns:
            DataFrame with availability statistics (or JSON string if json_output=True).
        """
        
        endpoint = self.ENDPOINTS['device_availability_statistics'].replace("{statId}", str(statistic_type))
        params = {
            "filter[fromTime]": from_time,
            "filter[thruTime]": until_time,
            "filter[interval]": interval,
            "filter[deviceId]": device_id
        }

        response_data = self.get(endpoint, params=params)

        # Return an empty DataFrame if no data is available
        if not response_data:
            return pd.DataFrame()

        structured_data = []

        for item in response_data:
            base_info = {
                "id": item.get("id"),
                "type": item.get("type"),
                "reportPeriod.fromTime": item["attributes"]["reportPeriod"]["fromTime"],
                "reportPeriod.thruTime": item["attributes"]["reportPeriod"]["thruTime"],
                "interval": item["attributes"]["interval"],
                "statType": item["attributes"]["statType"],
                "device.id": item["relationships"]["device"]["data"]["id"],
                "device.type": item["relationships"]["device"]["data"]["type"],
                "device.name": item["relationships"]["device"]["data"].get("deviceName"),
                "device.typeName": item["relationships"]["device"]["data"].get("deviceType"),
                "tenant.id": item["relationships"]["tenant"]["data"]["id"],
                "tenant.domainPrefix": item["relationships"]["tenant"]["data"]["attributes"]["domainPrefix"]
            }

            # Extract stats
            stats = item["attributes"]["stats"]
            for stat_entry in stats:
                availability_info = {}

                # Store labels and units
                for i, legend in enumerate(stat_entry["legend"]):
                    availability_info[f"availability.{legend}.unit"] = stat_entry["unit"][i]

                # Split each data entry into separate rows
                for data_entry in stat_entry["data"]:
                    row = base_info.copy()  # Preserve base data
                    for i, legend in enumerate(stat_entry["legend"]):
                        value = data_entry[i]
                        if legend == "Recorded At":  # Convert Unix minutes to human-readable time
                            value = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(value * 60))
                        row[f"availability.{legend}"] = value
                    
                    row.update(availability_info)  # Add units to the row
                    structured_data.append(row)

        # Convert to DataFrame
        df = pd.DataFrame(structured_data)

        return df if not json_output else df.to_json(orient="records", indent=4)
    
    def get_device_notes (self, device_id: str = None, json_output: bool = False):  # Method to get tenant information from Auvik.
        """
        Retrieves device notes information from Auvik.

        Args:
            json_output (bool): If True, returns the output in JSON format as a string. Defaults to False.

        Returns:
            A DataFrame containing tenant information. If `json_output` is True, returns the data in JSON string format instead.
        """

        endpoint = self.ENDPOINTS['device_notes']

        params = {
            "filter[entityId]" : device_id
        }

        response_data = self.get(endpoint, params=params)  # Calls the 'get' method with the tenants endpoint.
        return self._handle_output(response_data, json_output)  # Returns the processed output as JSON or DataFrame.
