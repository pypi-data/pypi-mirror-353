# -*- coding: utf-8 -*-

import asyncio
import fire
import json
import random
import os
import tempfile
from typing import Optional, Union, Dict, List, Any

import logging
from my_cli_utilities_common.http_helpers import make_async_request

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('account_pool_cli')

# Configuration constants
class Config:
    BASE_URL = "https://account-pool-mthor.int.rclabenv.com"
    ACCOUNTS_ENDPOINT = f"{BASE_URL}/accounts"
    ACCOUNT_SETTINGS_ENDPOINT = f"{BASE_URL}/accountSettings"
    CACHE_FILE = os.path.join(tempfile.gettempdir(), "account_pool_cli_cache.json")
    DEFAULT_ENV_NAME = "webaqaxmn"
    DEFAULT_BRAND = "1210"
    DISPLAY_WIDTH = 80
    CACHE_DISPLAY_WIDTH = 60
    MAX_DISPLAY_LENGTH = 80

class CacheManager:
    """Handles cache operations for account types."""
    
    @staticmethod
    def save_cache(account_types: List[str], filter_keyword: Optional[str], brand: str) -> None:
        """Save account types to cache."""
        cache_data = {
            "account_types": account_types,
            "filter_keyword": filter_keyword,
            "brand": brand
        }
        try:
            with open(Config.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    @staticmethod
    def load_cache() -> Optional[Dict[str, Any]]:
        """Load cache data."""
        try:
            with open(Config.CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return None
    
    @staticmethod
    def get_account_type_by_index(index: int) -> Optional[str]:
        """Get account type by index from cache."""
        cache_data = CacheManager.load_cache()
        if not cache_data:
            logger.error("No cached account types found. Please run 'ap types' first")
            return None
        
        account_types = cache_data.get("account_types", [])
        if 1 <= index <= len(account_types):
            return account_types[index - 1]  # Convert to 0-based index
        else:
            logger.error(f"Index {index} is out of range. Available indices: 1-{len(account_types)}")
            logger.info("Please run 'ap types' first to see available account types")
            return None
    
    @staticmethod
    def clear_cache() -> bool:
        """Clear the cache file. Returns True if successful."""
        try:
            if os.path.exists(Config.CACHE_FILE):
                os.remove(Config.CACHE_FILE)
                logger.info("Cache cleared successfully")
                return True
            else:
                logger.info("No cache file to clear")
                return False
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


class AccountPoolCli:
    """
    A CLI tool to interact with the Account Pool service.
    Provides commands to fetch random accounts, specific account details by ID,
    or specific account details by main number.
    env_name defaults to 'webaqaxmn' if not provided for relevant commands.
    """

    @staticmethod
    def _print_json(data: Any, title: str = "") -> None:
        """Print JSON data with optional title."""
        if title:
            logger.info(title)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    @staticmethod
    def _is_numeric_string(value: Union[str, int]) -> bool:
        """Check if value is numeric (int or digit string)."""
        return isinstance(value, int) or (isinstance(value, str) and value.isdigit())

    @staticmethod
    def _normalize_phone_number(phone_number: Union[str, int]) -> str:
        """Normalize phone number by adding + prefix if missing."""
        phone_str = str(phone_number)
        return phone_str if phone_str.startswith("+") else "+" + phone_str

    async def _fetch_random_account_async(self, env_name: str, account_type: str) -> None:
        """Fetch a random account asynchronously."""
        params = {"envName": env_name, "accountType": account_type}
        logger.info(f"Fetching random account for type '{account_type}' in env '{env_name}'...")
        
        response_data = await make_async_request(Config.ACCOUNTS_ENDPOINT, params=params)
        if not response_data:
            return

        try:
            accounts_list = response_data.get("accounts")
            if accounts_list:
                random_account = random.choice(accounts_list)
                self._print_json(random_account, "Randomly selected account information:")
            else:
                logger.warning("No matching accounts found, or the 'accounts' list is empty.")
        except (TypeError, KeyError) as e:
            logger.error(f"Failed to extract account information from response data: {e}")
            logger.debug("Raw data received: " + (json.dumps(response_data, indent=2, ensure_ascii=False) if isinstance(response_data, dict) else str(response_data)))

    def get_random_account(self, account_type: Union[str, int], env_name: str = Config.DEFAULT_ENV_NAME) -> None:
        """Fetches a random account from the Account Pool.

        Args:
            account_type: Account type string or index number from 'types' command.
            env_name: Environment name. Defaults to "webaqaxmn".
        """
        if self._is_numeric_string(account_type):
            index = int(account_type)
            actual_account_type = CacheManager.get_account_type_by_index(index)
            if actual_account_type is None:
                return
            logger.info(f"Using account type from index {index}: {actual_account_type}")
            asyncio.run(self._fetch_random_account_async(env_name, actual_account_type))
        else:
            asyncio.run(self._fetch_random_account_async(env_name, str(account_type)))

    def get(self, account_type: Union[str, int], env_name: str = Config.DEFAULT_ENV_NAME) -> None:
        """Short alias for get_random_account. Fetches a random account."""
        self.get_random_account(account_type, env_name)

    async def _fetch_account_by_id_async(self, account_id: str, env_name: str) -> None:
        """Fetch account details by ID asynchronously."""
        url = f"{Config.ACCOUNTS_ENDPOINT}/{account_id}"
        params = {"envName": env_name}
        logger.info(f"Fetching details for account ID {account_id} in env {env_name}...")
        
        account_details = await make_async_request(url, params=params)
        if account_details:
            self._print_json(account_details, "Account details:")

    def get_account_by_id(self, account_id: str, env_name: str = Config.DEFAULT_ENV_NAME) -> None:
        """Fetches specific account details by its ID."""
        asyncio.run(self._fetch_account_by_id_async(account_id, env_name))

    def by_id(self, account_id: str, env_name: str = Config.DEFAULT_ENV_NAME) -> None:
        """Short alias for get_account_by_id. Fetches account by ID."""
        self.get_account_by_id(account_id, env_name)

    async def _fetch_info_by_main_number_async(self, main_number: Union[str, int], env_name: str) -> None:
        """Fetch account info by main number asynchronously."""
        main_number_str = self._normalize_phone_number(main_number)
        params = {"envName": env_name, "mainNumber": main_number_str}
        logger.info(f"Looking up account ID for main number {main_number_str} in env {env_name}...")
        
        response_data = await make_async_request(Config.ACCOUNTS_ENDPOINT, params=params)
        if not response_data:
            return

        try:
            accounts_list = response_data.get("accounts")
            if accounts_list:
                account_summary = accounts_list[0]  # First account for mainNumber lookup
                retrieved_account_id = account_summary.get("_id")
                
                if retrieved_account_id:
                    logger.info(f"Found account ID: {retrieved_account_id}. Fetching details...")
                    await self._fetch_account_by_id_async(retrieved_account_id, env_name)
                else:
                    logger.warning(f"Account found for main number {main_number_str}, but missing '_id' field.")
                    self._print_json(account_summary, "Account summary found:")
            else:
                logger.warning(f"No account found for main number {main_number_str} in environment {env_name}.")
        except (TypeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse or extract account ID from initial lookup: {e}")
            logger.debug("Raw data received: " + (json.dumps(response_data, indent=2, ensure_ascii=False) if isinstance(response_data, dict) else str(response_data)))

    def info(self, main_number: Union[str, int], env_name: str = Config.DEFAULT_ENV_NAME) -> None:
        """Fetches account details by mainNumber (looks up ID first)."""
        asyncio.run(self._fetch_info_by_main_number_async(main_number, env_name))

    async def _list_account_types_async(self, filter_keyword: Optional[str] = None, brand: str = Config.DEFAULT_BRAND) -> None:
        """List account types asynchronously."""
        params = {"brand": brand}
        logger.info(f"Fetching account types for brand {brand}...")
        
        response_data = await make_async_request(Config.ACCOUNT_SETTINGS_ENDPOINT, params=params)
        if not response_data:
            return

        try:
            account_settings = response_data.get("accountSettings")
            if not account_settings:
                logger.warning(f"No account types found for brand {brand}.")
                return

            # Filter account types if keyword provided
            if filter_keyword:
                account_settings = [
                    setting for setting in account_settings 
                    if filter_keyword.lower() in setting.get("accountType", "").lower()
                ]
                
            if not account_settings:
                logger.warning(f"No account types found for brand {brand} with filter '{filter_keyword}'.")
                return

            self._display_account_types(account_settings, filter_keyword, brand)
            
        except (TypeError, KeyError) as e:
            logger.error(f"Failed to extract account types from response: {e}")
            logger.debug("Raw data received: " + (json.dumps(response_data, indent=2, ensure_ascii=False) if isinstance(response_data, dict) else str(response_data)))

    def _display_account_types(self, account_settings: List[Dict], filter_keyword: Optional[str], brand: str) -> None:
        """Display account types and save to cache."""
        filter_info = f" (filtered by '{filter_keyword}')" if filter_keyword else ""
        logger.info(f"Found {len(account_settings)} account types{filter_info}:")
        
        print("\n" + "=" * Config.DISPLAY_WIDTH)
        print(f"Available Account Types{filter_info}:")
        print("=" * Config.DISPLAY_WIDTH)
        
        account_types = []
        for i, setting in enumerate(account_settings, 1):
            account_type = setting.get("accountType", "N/A")
            total = setting.get("total", "N/A")
            auto_fill = setting.get("autoFill", False)
            
            print(f"\n{i}. {account_type}")
            print(f"   Total: {total}, AutoFill: {auto_fill}")
            account_types.append(account_type)
            
        # Save to cache
        CacheManager.save_cache(account_types, filter_keyword, brand)
        
        print("\n" + "=" * Config.DISPLAY_WIDTH)
        print("Copy any account type above to use with the 'get' command")
        print("Or use: ap get <index_number> to get account by index")
        print("Example: ap get 'kamino2(CI-Common-NoGuest,mThor,brand=1210)'")
        print("Example: ap get 2")
        print("=" * Config.DISPLAY_WIDTH)

    def list_account_types(self, filter_keyword: Optional[str] = None, brand: str = Config.DEFAULT_BRAND) -> None:
        """Lists all available account types from account settings."""
        asyncio.run(self._list_account_types_async(filter_keyword, brand))

    def types(self, filter_keyword: Optional[str] = None, brand: str = Config.DEFAULT_BRAND) -> None:
        """Short alias for list_account_types. Lists available account types."""
        self.list_account_types(filter_keyword, brand)

    def cache(self, action: Optional[str] = None) -> None:
        """Manage cache for account types."""
        if action == "clear":
            self._clear_cache()
        else:
            self._show_cache_status()

    def _show_cache_status(self) -> None:
        """Display current cache status."""
        cache_data = CacheManager.load_cache()
        if not cache_data:
            self._display_no_cache_status()
            return
            
        account_types = cache_data.get("account_types", [])
        filter_keyword = cache_data.get("filter_keyword")
        brand = cache_data.get("brand", "Unknown")
        
        print("\n" + "=" * Config.CACHE_DISPLAY_WIDTH)
        print("Account Pool CLI - Cache Status")
        print("=" * Config.CACHE_DISPLAY_WIDTH)
        print(f"Cache file: {Config.CACHE_FILE}")
        print(f"Total cached account types: {len(account_types)}")
        print(f"Brand: {brand}")
        
        if filter_keyword:
            print(f"Filter keyword: '{filter_keyword}'")
        else:
            print("Filter keyword: None (showing all types)")
        
        if account_types:
            print(f"\nAvailable indices: 1-{len(account_types)}")
            print("\nFirst 5 cached account types:")
            for i, account_type in enumerate(account_types[:5], 1):
                display_type = account_type if len(account_type) <= Config.MAX_DISPLAY_LENGTH else account_type[:77] + "..."
                print(f"  {i}. {display_type}")
            
            if len(account_types) > 5:
                print(f"  ... and {len(account_types) - 5} more")
        else:
            print("\nNo account types in cache")
        
        print("\n" + "=" * Config.CACHE_DISPLAY_WIDTH)
        print("Use 'ap cache clear' to clear cache")
        print("Use 'ap types' to refresh cache")
        print("=" * Config.CACHE_DISPLAY_WIDTH)

    def _display_no_cache_status(self) -> None:
        """Display status when no cache is available."""
        print("\n" + "=" * Config.CACHE_DISPLAY_WIDTH)
        print("Account Pool CLI - Cache Status")
        print("=" * Config.CACHE_DISPLAY_WIDTH)
        print("Cache file: Not found")
        print("Status: No cache available")
        print("\nRun 'ap types' to create cache")
        print("=" * Config.CACHE_DISPLAY_WIDTH)

    def _clear_cache(self) -> None:
        """Clear the cache file."""
        if CacheManager.clear_cache():
            print("✓ Cache has been cleared")
        else:
            print("ℹ No cache file found - nothing to clear")

    def help(self) -> None:
        """Display available commands and their short aliases."""
        header_color = "\033[95m"
        bold = "\033[1m"
        end = "\033[0m"
        
        print(f"{header_color}Account Pool CLI Commands{end}")
        print("\nAvailable commands:")
        print(f"  {bold}get_random_account <account_type|index> [env_name]{end}")
        print(f"    {bold}get <account_type|index> [env_name]{end}         - Short alias")
        print(f"  {bold}get_account_by_id <account_id> [env_name]{end}")
        print(f"    {bold}by_id <account_id> [env_name]{end}               - Short alias")
        print(f"  {bold}info <main_number> [env_name]{end}                - Get account by phone number")
        print(f"  {bold}list_account_types [filter_keyword] [brand]{end} - List all available account types")
        print(f"    {bold}types [filter_keyword] [brand]{end}           - Short alias")
        print(f"  {bold}cache [clear]{end}                              - Show cache status or clear cache")
        print(f"  {bold}help{end}                                       - Show this help")
        print(f"\nExamples:")
        print(f"  {bold}ap types{end}                                   - List all account types for brand 1210")
        print(f"  {bold}ap types 4U{end}                                - Filter account types containing '4U'")
        print(f"  {bold}ap types NoGuest{end}                           - Filter account types containing 'NoGuest'")
        print(f"  {bold}ap types phoneNumbers 1211{end}                 - Filter for 'phoneNumbers' in brand 1211")
        print(f"  {bold}ap get 2{end}                                   - Get account using index from types result")
        print(f"  {bold}ap cache{end}                                   - Show current cache status")
        print(f"  {bold}ap cache clear{end}                             - Clear the cache")
        print(f"  {bold}ap get 'kamino2(CI-Common-4U,mThor,brand=1210)'{end}")
        print(f"  {bold}ap by_id 507f1f77bcf86cd799439011{end}")
        print(f"  {bold}ap info 12495002020{end}")

def main_cli_function() -> None:
    """Main CLI entry point."""
    fire.Fire(AccountPoolCli)

if __name__ == "__main__":
    main_cli_function()
