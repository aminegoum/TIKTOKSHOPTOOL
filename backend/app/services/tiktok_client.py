"""
TikTok Shop API Client
"""
import httpx
import hashlib
import hmac
import time
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..config import settings


class TikTokShopClient:
    """Client for TikTok Shop API interactions"""
    
    def __init__(self, access_token: str = None):
        """
        Initialize TikTok Shop API client
        
        Args:
            access_token: OAuth access token (required for API calls)
        """
        self.access_token = access_token or settings.tiktok_access_token or ""
        self.app_key = settings.tiktok_app_key
        self.app_secret = settings.tiktok_app_secret
        self.base_url = settings.tiktok_api_base_url
        self.shop_cipher = settings.tiktok_shop_cipher or ""
        self.shop_id = settings.tiktok_shop_id or ""
    
    def _generate_signature(self, path: str, params: Dict, body: str = "") -> tuple:
        """
        Generate HMAC-SHA256 signature for TikTok API request
        
        TikTok signature algorithm:
        1. Sort query params alphabetically
        2. Concatenate as: key1value1key2value2...
        3. Prepend API path: /path + params_string
        4. Append request body (if POST with body)
        5. Wrap with app_secret: app_secret + string + app_secret
        6. Generate HMAC-SHA256(app_secret, wrapped_string)
        
        Args:
            path: API endpoint path (e.g., /order/202309/orders/search)
            params: Query parameters (should NOT include sign or timestamp yet)
            body: Request body as JSON string
            
        Returns:
            Tuple of (signature, timestamp)
        """
        timestamp = str(int(time.time()))
        
        # Create a copy of params to avoid modifying the original
        params_for_sign = params.copy()
        
        # Remove sign and timestamp if they exist
        params_for_sign.pop('sign', None)
        params_for_sign.pop('timestamp', None)
        
        # Add timestamp to params for signature
        params_for_sign['timestamp'] = timestamp
        
        # Step 1: Sort parameters alphabetically by key
        sorted_params = sorted(params_for_sign.items())
        
        # Step 2: Concatenate as key1value1key2value2
        # IMPORTANT: All values must be converted to strings
        param_str = "".join([f"{k}{str(v)}" for k, v in sorted_params])
        
        # Step 3: Prepend API path and append body if present
        # For POST with empty body {}, we still append it
        string_to_sign = path + param_str + body
        
        # Step 4: Wrap with app_secret on both sides
        wrapped_string = self.app_secret + string_to_sign + self.app_secret
        
        # Step 5: Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.app_secret.encode(),
            wrapped_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        print(f"\n=== Signature Debug ===")
        print(f"Path: {path}")
        print(f"Timestamp: {timestamp}")
        print(f"Params for signature: {params_for_sign}")
        print(f"Sorted params: {sorted_params}")
        print(f"Param string: {param_str}")
        print(f"Body: {body[:100] if body else '(empty)'}")
        print(f"String to sign: {string_to_sign[:100]}...")
        print(f"Wrapped string: {wrapped_string[:100]}...")
        print(f"Generated signature: {signature}")
        print(f"=== End Signature Debug ===\n")
        
        return signature, timestamp
    
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Dict = None,
        body: Dict = None
    ) -> Dict:
        """
        Make authenticated request to TikTok Shop API
        
        TikTok Shop API requires:
        1. Access token in 'x-tts-access-token' header
        2. Common parameters (app_key, timestamp, sign) in query string
        3. Request body for POST requests
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., /order/202309/orders/search)
            params: Query parameters (will be merged with common params)
            body: Request body for POST requests
        
        Returns:
            API response as dictionary
        """
        params = params or {}
        
        # Add common parameters required by TikTok API
        params["app_key"] = self.app_key
        
        # Generate signature BEFORE adding sign to params
        # Note: timestamp is added inside _generate_signature
        # Body must be JSON with sorted keys and no spaces
        # For POST requests, even empty body should be {}
        if method == "POST":
            if body is None or (isinstance(body, dict) and len(body) == 0):
                body_str = "{}"
            else:
                body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        else:
            # GET requests have no body in signature
            body_str = ""
        signature, timestamp = self._generate_signature(path, params, body_str)
        
        # Add signature and timestamp to params
        params["sign"] = signature
        params["timestamp"] = timestamp
        
        # IMPORTANT: access_token is added AFTER signature generation
        # It goes in query params but is NOT part of the signature
        if self.access_token:
            params["access_token"] = self.access_token
        
        # Build headers - access token MUST be in header too
        headers = {
            "Content-Type": "application/json",
            "x-tts-access-token": self.access_token
        }
        
        # Make request
        url = f"{self.base_url}{path}"
        
        print(f"\n=== TikTok API Request ===")
        print(f"URL: {url}")
        print(f"Method: {method}")
        print(f"Params: {params}")
        print(f"Headers: {dict((k, v[:20] + '...' if len(v) > 20 else v) for k, v in headers.items())}")
        if body:
            print(f"Body: {json.dumps(body, indent=2)}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, params=params, headers=headers)
            elif method == "POST":
                response = await client.post(url, params=params, json=body, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            print(f"Response status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            print(f"=== End Request ===\n")
            
            response.raise_for_status()
            return response.json()
    
    async def get_authorized_shops(self) -> Dict:
        """
        Get list of authorized shops
        
        This is a good test endpoint to verify authentication is working.
        API Version: 202309
        
        Returns:
            List of authorized shops
        """
        return await self._make_request("GET", "/authorization/202309/shops")
    
    async def get_orders(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        page_size: int = 50,
        page_token: str = None,
        order_status: Optional[str] = None,
        sort_field: str = "create_time",
        sort_order: str = "DESC"
    ) -> Dict:
        """
        Get orders from TikTok Shop
        
        Uses the Order Search API endpoint.
        API Version: 202309
        
        IMPORTANT: With 1M+ orders, use sort_field=create_time and sort_order=DESC for recent orders!
        
        Args:
            start_time: Start of date range (optional - omit to get all orders)
            end_time: End of date range (optional - omit to get all orders)
            page_size: Number of orders per page (max 50)
            page_token: Token for pagination (from previous response)
            order_status: Filter by status (optional)
            sort_field: Sort field - TikTok uses "create_time" (default: create_time)
            sort_order: Sort order - "DESC" for newest first, "ASC" for oldest (default: DESC)
        
        Returns:
            Orders data from API with next_page_token for pagination
        """
        # Build request body - filters go in body
        request_body = {}
        
        # Only add date filters if provided
        if start_time and end_time:
            request_body["create_time_from"] = int(start_time.timestamp())
            request_body["create_time_to"] = int(end_time.timestamp())
        
        # Add order status filter if provided
        if order_status:
            request_body["order_status"] = order_status
        
        # Build query params - SORTING GOES IN QUERY PARAMS, NOT BODY!
        params = {
            "page_size": min(page_size, 50),
            "version": "202309",
            "sort_field": sort_field,
            "sort_order": sort_order
        }
        
        # Use page_token for pagination instead of page_number
        if page_token:
            params["page_token"] = page_token
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        # Use correct API endpoint path with version
        return await self._make_request("POST", "/order/202309/orders/search", params=params, body=request_body)
    
    async def get_order_detail(self, order_id: str) -> Dict:
        """
        Get detailed information for a specific order
        
        API Version: 202309
        
        Args:
            order_id: TikTok order ID
            
        Returns:
            Order details from API
        """
        params = {"order_id": order_id}
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
            
        return await self._make_request(
            "GET",
            "/order/202309/orders/detail",
            params=params
        )
    
    async def get_products(
        self,
        page_size: int = 50,
        page_number: int = 1,
        status: Optional[str] = None
    ) -> Dict:
        """
        Get products from TikTok Shop
        
        Uses the Product Search API endpoint.
        API Version: 202309
        
        Args:
            page_size: Number of products per page (max 100)
            page_number: Page number (starts at 1)
            status: Filter by status (optional)
        
        Returns:
            Products data from API
        """
        # Build request body - filter parameters go in body
        request_body = {}
        
        if status:
            request_body["status"] = status
        
        # Build query params - shop_cipher, shop_id, version, and pagination go in query
        params = {
            "page_size": min(page_size, 100),
            "version": "202502"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        # Use correct API endpoint path with version
        return await self._make_request("POST", "/product/202502/products/search", params=params, body=request_body)
    
    async def get_product_detail(self, product_id: str) -> Dict:
        """
        Get detailed information for a specific product
        
        API Version: 202309
        
        Args:
            product_id: TikTok product ID
            
        Returns:
            Product details from API
        """
        return await self._make_request(
            "GET",
            "/product/202309/products/details",
            params={"product_id": product_id}
        )
    
    async def get_finance_transactions(
        self,
        start_time: datetime,
        end_time: datetime,
        page_size: int = 50,
        page_token: str = None
    ) -> Dict:
        """
        Get finance transactions (settlements, payments)
        
        API Version: 202309
        
        Args:
            start_time: Start of date range
            end_time: End of date range
            page_size: Number of records per page
            page_token: Token for pagination
        
        Returns:
            Finance transaction data
        """
        params = {
            "page_size": min(page_size, 50),
            "version": "202309"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        if page_token:
            params["page_token"] = page_token
        
        body = {
            "create_time_from": int(start_time.timestamp()),
            "create_time_to": int(end_time.timestamp())
        }
        
        return await self._make_request(
            "POST",
            "/finance/202309/transactions/search",
            params=params,
            body=body
        )
    
    async def get_settlements(
        self,
        start_time: datetime,
        end_time: datetime,
        page_size: int = 50
    ) -> Dict:
        """
        Get settlement records
        
        API Version: 202309
        
        Args:
            start_time: Start of date range
            end_time: End of date range
            page_size: Number of records per page
        
        Returns:
            Settlement data
        """
        params = {
            "page_size": min(page_size, 50),
            "version": "202309"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        body = {
            "create_time_from": int(start_time.timestamp()),
            "create_time_to": int(end_time.timestamp())
        }
        
        return await self._make_request(
            "POST",
            "/finance/202309/settlements/search",
            params=params,
            body=body
        )
    
    async def get_returns(
        self,
        start_time: datetime,
        end_time: datetime,
        page_size: int = 50,
        page_number: int = 1
    ) -> Dict:
        """
        Get return/refund requests
        
        API Version: 202309
        
        Args:
            start_time: Start of date range
            end_time: End of date range
            page_size: Number of returns per page
            page_number: Page number
        
        Returns:
            Return request data
        """
        params = {
            "page_size": min(page_size, 50),
            "page_number": page_number,
            "version": "202309"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        body = {
            "create_time_from": int(start_time.timestamp()),
            "create_time_to": int(end_time.timestamp())
        }
        
        return await self._make_request(
            "POST",
            "/reverse/202309/reverse_requests/search",
            params=params,
            body=body
        )
    
    async def get_fulfillment_orders(
        self,
        page_size: int = 50,
        page_number: int = 1
    ) -> Dict:
        """
        Get fulfillment orders (for FBT - Fulfilled by TikTok)
        
        API Version: 202309
        
        Args:
            page_size: Number of orders per page
            page_number: Page number
        
        Returns:
            Fulfillment order data
        """
        params = {
            "page_size": min(page_size, 50),
            "page_number": page_number,
            "version": "202309"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "POST",
            "/fulfillment/202309/orders/search",
            params=params,
            body={}
        )
    
    async def get_product_reviews(
        self,
        product_id: str,
        page_size: int = 20,
        page_number: int = 1
    ) -> Dict:
        """
        Get product reviews
        
        API Version: 202309
        
        Args:
            product_id: TikTok product ID
            page_size: Number of reviews per page
            page_number: Page number
        
        Returns:
            Product review data
        """
        params = {
            "product_id": product_id,
            "page_size": min(page_size, 50),
            "page_number": page_number,
            "version": "202309"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/product/202309/reviews",
            params=params
        )
    
    async def get_promotion_activities(
        self,
        page_size: int = 20,
        page_number: int = 1
    ) -> Dict:
        """
        Get active promotion activities
        
        API Version: 202309
        
        Args:
            page_size: Number of promotions per page
            page_number: Page number
        
        Returns:
            Promotion activity data
        """
        params = {
            "page_size": min(page_size, 50),
            "page_number": page_number,
            "version": "202309"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "POST",
            "/promotion/202309/activities/search",
            params=params,
            body={}
        )
    
    async def get_shop_performance(self) -> Dict:
        """
        Get shop performance metrics
        
        API Version: 202309
        
        Returns:
            Shop performance data
        """
        params = {
            "version": "202309"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/seller/202309/performance",
            params=params
        )
    
    async def get_shop_performance_per_hour(
        self,
        date: str,
        currency: str = "LOCAL"
    ) -> Dict:
        """
        Get shop performance per hour for a specific date
        
        API Version: 202510 (Analytics API)
        
        Args:
            date: Date in YYYY-MM-DD format
            currency: Currency code (default: LOCAL)
        
        Returns:
            Hourly performance data including GMV, items sold, visitors, customers
        """
        params = {
            "currency": currency
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            f"/analytics/202510/shop/performance/{date}/performance_per_hour",
            params=params
        )
    
    async def get_shop_performance_overview(
        self,
        start_date: str,
        end_date: str,
        currency: str = "LOCAL"
    ) -> Dict:
        """
        Get shop performance overview for a date range
        
        API Version: 202510 (Analytics API)
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            currency: Currency code (default: LOCAL)
        
        Returns:
            Performance overview with GMV, orders, conversion rates, etc.
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "currency": currency
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/analytics/202510/shop/performance/overview",
            params=params
        )
    
    async def get_shop_performance_metrics(
        self,
        start_date: str,
        end_date: str,
        currency: str = "LOCAL",
        granularity: str = "ALL"
    ) -> Dict:
        """
        Get detailed shop performance metrics
        
        API: /analytics/202509/shop/performance
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            currency: Currency code (default: LOCAL) - USD or LOCAL
            granularity: Data granularity - ALL (aggregate) or 1D (daily)
        
        Returns:
            Detailed performance metrics
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "currency": currency,
            "granularity": granularity
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/analytics/202509/shop/performance",
            params=params
        )
    
    async def get_shop_video_performance_list(
        self,
        start_date: str,
        end_date: str,
        page_size: int = 20,
        page_token: str = None,
        currency: str = "LOCAL",
        sort_field: str = None,
        sort_order: str = "DESC",
        account_type: str = "ALL"
    ) -> Dict:
        """
        Get Shop Video Performance List
        
        API: /analytics/202509/shop_videos/performance
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            page_size: Number of videos per page (max 100)
            page_token: Page token for pagination
            currency: Currency code - USD or LOCAL (default: LOCAL)
            sort_field: Sort field (gmv, gpm, avg_customers, etc.)
            sort_order: Sort direction - ASC or DESC (default: DESC)
            account_type: Account type filter (default: ALL)
        
        Returns:
            Video performance data including GMV from videos
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "page_size": min(page_size, 100),
            "currency": currency,
            "sort_order": sort_order,
            "account_type": account_type
        }
        
        if page_token:
            params["page_token"] = page_token
        
        if sort_field:
            params["sort_field"] = sort_field
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/analytics/202509/shop_videos/performance",
            params=params
        )
    
    async def get_shop_video_performance_overview(
        self,
        start_date: str,
        end_date: str,
        currency: str = "LOCAL",
        today: bool = False,
        granularity: str = "ALL",
        account_type: str = "ALL"
    ) -> Dict:
        """
        Get Shop Video Performance Overview
        
        API: /analytics/202509/shop_videos/overview_performance
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            currency: Currency code - USD or LOCAL (default: LOCAL)
            today: If true, overrides dates with today's real-time metrics
            granularity: Data granularity - ALL (aggregate) or 1D (daily)
            account_type: Account type filter (default: ALL)
        
        Returns:
            Video performance overview
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "currency": currency,
            "granularity": granularity,
            "account_type": account_type
        }
        
        if today:
            params["today"] = "true"
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/analytics/202509/shop_videos/overview_performance",
            params=params
        )
    
    async def get_shop_video_performance_details(
        self,
        video_id: str,
        start_date: str,
        end_date: str,
        currency: str = "LOCAL",
        granularity: str = "ALL"
    ) -> Dict:
        """
        Get Shop Video Performance Details
        
        API: /analytics/202509/shop_videos/{video_id}/performance
        
        Args:
            video_id: TikTok video ID
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            currency: Currency code - USD or LOCAL (default: LOCAL)
            granularity: Data granularity - ALL (aggregate) or 1D (daily)
        
        Returns:
            Detailed performance metrics for a specific video
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "currency": currency,
            "granularity": granularity
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            f"/analytics/202509/shop_videos/{video_id}/performance",
            params=params
        )
    
    async def get_shop_video_product_performance_list(
        self,
        video_id: str,
        start_date: str,
        end_date: str,
        page_size: int = 20,
        page_token: str = None,
        currency: str = "LOCAL",
        sort_field: str = "gmv",
        sort_order: str = "DESC"
    ) -> Dict:
        """
        Get Shop Video Product Performance List
        
        API: /analytics/202509/shop_videos/{video_id}/products/performance
        
        Args:
            video_id: TikTok video ID
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            page_size: Number of products per page (max 100)
            page_token: Page token for pagination
            currency: Currency code - USD or LOCAL (default: LOCAL)
            sort_field: Sort field (gmv, units_sold, daily_avg_buyers)
            sort_order: Sort direction - ASC or DESC (default: DESC)
        
        Returns:
            Product performance data for a specific video
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "page_size": min(page_size, 100),
            "currency": currency,
            "sort_field": sort_field,
            "sort_order": sort_order
        }
        
        if page_token:
            params["page_token"] = page_token
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            f"/analytics/202509/shop_videos/{video_id}/products/performance",
            params=params
        )
    
    async def get_shop_live_performance_per_minutes(
        self,
        live_id: str,
        currency: str = "LOCAL",
        page_token: str = None
    ) -> Dict:
        """
        Get Shop LIVE Performance Per Minutes
        
        API: /analytics/202510/shop_lives/{live_id}/performance_per_minutes
        
        Args:
            live_id: TikTok LIVE stream ID
            currency: Currency code - USD or LOCAL (default: LOCAL)
            page_token: Page token for pagination
        
        Returns:
            Minute-by-minute performance data for LIVE stream
        """
        params = {
            "currency": currency
        }
        
        if page_token:
            params["page_token"] = page_token
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            f"/analytics/202510/shop_lives/{live_id}/performance_per_minutes",
            params=params
        )
    
    async def get_shop_live_products_performance(
        self,
        live_id: str,
        currency: str = "LOCAL",
        sort_field: str = "gmv",
        sort_order: str = "DESC"
    ) -> Dict:
        """
        Get Shop LIVE Products Performance List
        
        API: /analytics/202512/shop/{live_id}/products_performance
        
        Args:
            live_id: TikTok LIVE stream ID
            currency: Currency code - USD or LOCAL (default: LOCAL)
            sort_field: Sort field (direct_gmv, items_sold, customers, etc.)
            sort_order: Sort direction - ASC or DESC (default: DESC)
        
        Returns:
            Product performance data for a specific LIVE stream
        """
        params = {
            "currency": currency,
            "sort_field": sort_field,
            "sort_order": sort_order
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            f"/analytics/202512/shop/{live_id}/products_performance",
            params=params
        )
    
    async def get_shop_live_performance_list(
        self,
        start_date: str,
        end_date: str,
        page_size: int = 20,
        page_token: str = None,
        currency: str = "LOCAL",
        sort_field: str = "gmv",
        sort_order: str = "DESC",
        account_type: str = "ALL"
    ) -> Dict:
        """
        Get Shop LIVE Performance List
        
        API: /analytics/202509/shop_lives/performance
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            page_size: Number of LIVE streams per page (max 100)
            page_token: Page token for pagination
            currency: Currency code - USD or LOCAL (default: LOCAL)
            sort_field: Sort field (gmv, products_added, etc.)
            sort_order: Sort direction - ASC or DESC (default: DESC)
            account_type: Account type filter (default: ALL)
        
        Returns:
            LIVE stream performance data
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "page_size": min(page_size, 100),
            "currency": currency,
            "sort_field": sort_field,
            "sort_order": sort_order,
            "account_type": account_type
        }
        
        if page_token:
            params["page_token"] = page_token
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/analytics/202509/shop_lives/performance",
            params=params
        )
    
    async def get_shop_live_performance_overview(
        self,
        start_date: str,
        end_date: str,
        currency: str = "LOCAL",
        today: bool = False,
        granularity: str = "ALL",
        account_type: str = "ALL"
    ) -> Dict:
        """
        Get Shop LIVE Performance Overview
        
        API: /analytics/202509/shop_lives/overview_performance
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            currency: Currency code - USD or LOCAL (default: LOCAL)
            today: If true, overrides dates with today's real-time metrics
            granularity: Data granularity - ALL (aggregate) or 1D (daily)
            account_type: Account type filter (default: ALL)
        
        Returns:
            LIVE stream performance overview
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "currency": currency,
            "granularity": granularity,
            "account_type": account_type
        }
        
        if today:
            params["today"] = "true"
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/analytics/202509/shop_lives/overview_performance",
            params=params
        )
    
    async def get_product_performance(
        self,
        product_id: str,
        start_date: str,
        end_date: str,
        currency: str = "LOCAL",
        granularity: str = "ALL"
    ) -> Dict:
        """
        Get Shop Product Performance Detail
        
        API: /analytics/202509/shop_products/{product_id}/performance
        
        Args:
            product_id: TikTok product ID
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            currency: Currency code - USD or LOCAL (default: LOCAL)
            granularity: Data granularity - ALL (aggregate) or 1D (daily)
        
        Returns:
            Product performance metrics
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "currency": currency,
            "granularity": granularity
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            f"/analytics/202509/shop_products/{product_id}/performance",
            params=params
        )
    
    async def get_shop_product_performance_list(
        self,
        start_date: str,
        end_date: str,
        page_size: int = 20,
        page_token: str = None,
        currency: str = "LOCAL",
        sort_field: str = "gmv",
        sort_order: str = "DESC",
        category_filter: list = None,
        product_status_filter: str = "ALL"
    ) -> Dict:
        """
        Get Shop Product Performance List
        
        API: /analytics/202509/shop_products/performance
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            page_size: Number of products per page (max 100)
            page_token: Page token for pagination
            currency: Currency code - USD or LOCAL (default: LOCAL)
            sort_field: Sort field (gmv, items_sold, orders)
            sort_order: Sort direction - ASC or DESC (default: DESC)
            category_filter: Category ID array
            product_status_filter: LIVE, INACTIVE, or ALL (default: ALL)
        
        Returns:
            Product performance list
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "page_size": min(page_size, 100),
            "currency": currency,
            "sort_field": sort_field,
            "sort_order": sort_order,
            "product_status_filter": product_status_filter
        }
        
        if page_token:
            params["page_token"] = page_token
        
        if category_filter:
            params["category_filter"] = category_filter
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/analytics/202509/shop_products/performance",
            params=params
        )
    
    async def get_shop_sku_performance_list(
        self,
        start_date: str,
        end_date: str,
        page_size: int = 20,
        page_token: str = None,
        currency: str = "LOCAL",
        sort_field: str = "gmv",
        sort_order: str = "DESC",
        category_filter: list = None,
        product_status_filter: str = "ALL",
        product_ids: list = None
    ) -> Dict:
        """
        Get Shop SKU Performance List
        
        API: /analytics/202509/shop_skus/performance
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            page_size: Number of SKUs per page (max 100)
            page_token: Page token for pagination
            currency: Currency code - USD or LOCAL (default: LOCAL)
            sort_field: Sort field (gmv, sku_orders, units_sold)
            sort_order: Sort direction - ASC or DESC (default: DESC)
            category_filter: Category ID array
            product_status_filter: LIVE, INACTIVE, or ALL (default: ALL)
            product_ids: Filter SKUs by product IDs
        
        Returns:
            SKU performance data
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "page_size": min(page_size, 100),
            "currency": currency,
            "sort_field": sort_field,
            "sort_order": sort_order,
            "product_status_filter": product_status_filter
        }
        
        if page_token:
            params["page_token"] = page_token
        
        if category_filter:
            params["category_filter"] = category_filter
        
        if product_ids:
            params["product_ids"] = product_ids
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            "/analytics/202509/shop_skus/performance",
            params=params
        )
    
    async def get_shop_sku_performance(
        self,
        sku_id: str,
        start_date: str,
        end_date: str,
        currency: str = "LOCAL",
        granularity: str = "ALL"
    ) -> Dict:
        """
        Get Shop SKU Performance
        
        API: /analytics/202509/shop_skus/{sku_id}/performance
        
        Args:
            sku_id: TikTok SKU ID
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (exclusive)
            currency: Currency code - USD or LOCAL (default: LOCAL)
            granularity: Data granularity - ALL (aggregate) or 1D (daily)
        
        Returns:
            SKU performance metrics
        """
        params = {
            "start_date_ge": start_date,
            "end_date_lt": end_date,
            "currency": currency,
            "granularity": granularity
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        return await self._make_request(
            "GET",
            f"/analytics/202509/shop_skus/{sku_id}/performance",
            params=params
        )
    
    # Additional Analytics Endpoints from ANALYTICS_ENDPOINTS.md
    
    async def get_shop_trends(
        self,
        start_date: str,
        end_date: str,
        granularity: str = "daily",
        currency: str = "LOCAL"
    ) -> Dict:
        """
        Get shop performance trends over time
        
        API: /api/shop/202309/analytics/trends
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            granularity: Time granularity (daily, weekly, monthly)
            currency: Currency code (default: LOCAL)
        
        Returns:
            Trend data with time series metrics
            
        Raises:
            ValueError: If date format is invalid or granularity is not supported
        """
        # Validate granularity
        valid_granularities = ["daily", "weekly", "monthly"]
        if granularity not in valid_granularities:
            raise ValueError(f"Invalid granularity '{granularity}'. Must be one of: {', '.join(valid_granularities)}")
        
        # Convert dates to Unix timestamps with validation
        from datetime import datetime
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        
        # Validate date range
        if start_ts > end_ts:
            raise ValueError("start_date must be before or equal to end_date")
        
        params = {
            "start_date": start_ts,
            "end_date": end_ts,
            "granularity": granularity
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        return await self._make_request(
            "GET",
            "/api/shop/202309/analytics/trends",
            params=params
        )
    
    async def get_order_statistics(
        self,
        start_date: str,
        end_date: str,
        status: str = None
    ) -> Dict:
        """
        Get aggregated order statistics and metrics
        
        API: /api/order/202309/analytics/statistics
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            status: Optional order status filter
        
        Returns:
            Order statistics including counts and revenue
            
        Raises:
            ValueError: If date format is invalid
        """
        # Convert dates to Unix timestamps with validation
        from datetime import datetime
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        
        # Validate date range
        if start_ts > end_ts:
            raise ValueError("start_date must be before or equal to end_date")
        
        params = {
            "start_date": start_ts,
            "end_date": end_ts
        }
        
        if status:
            params["status"] = status
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        return await self._make_request(
            "GET",
            "/api/order/202309/analytics/statistics",
            params=params
        )
    
    async def get_order_trends(
        self,
        start_date: str,
        end_date: str,
        granularity: str = "daily"
    ) -> Dict:
        """
        Get order trends over time
        
        API: /api/order/202309/analytics/trends
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            granularity: Time granularity (hourly, daily, weekly)
        
        Returns:
            Order trend data with time series
            
        Raises:
            ValueError: If date format is invalid or granularity is not supported
        """
        # Validate granularity
        valid_granularities = ["hourly", "daily", "weekly"]
        if granularity not in valid_granularities:
            raise ValueError(f"Invalid granularity '{granularity}'. Must be one of: {', '.join(valid_granularities)}")
        
        # Convert dates to Unix timestamps with validation
        from datetime import datetime
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        
        # Validate date range
        if start_ts > end_ts:
            raise ValueError("start_date must be before or equal to end_date")
        
        params = {
            "start_date": start_ts,
            "end_date": end_ts,
            "granularity": granularity
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        return await self._make_request(
            "GET",
            "/api/order/202309/analytics/trends",
            params=params
        )
    
    async def get_traffic_overview(
        self,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Get traffic and visitor metrics for the shop
        
        API: /api/shop/202309/analytics/traffic
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Traffic metrics including visitors and page views
            
        Raises:
            ValueError: If date format is invalid
        """
        # Convert dates to Unix timestamps with validation
        from datetime import datetime
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        
        # Validate date range
        if start_ts > end_ts:
            raise ValueError("start_date must be before or equal to end_date")
        
        params = {
            "start_date": start_ts,
            "end_date": end_ts
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        return await self._make_request(
            "GET",
            "/api/shop/202309/analytics/traffic",
            params=params
        )
    
    async def get_traffic_sources(
        self,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Get breakdown of traffic by source
        
        API: /api/shop/202309/analytics/traffic_sources
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Traffic source breakdown
            
        Raises:
            ValueError: If date format is invalid
        """
        # Convert dates to Unix timestamps with validation
        from datetime import datetime
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        
        # Validate date range
        if start_ts > end_ts:
            raise ValueError("start_date must be before or equal to end_date")
        
        params = {
            "start_date": start_ts,
            "end_date": end_ts
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        return await self._make_request(
            "GET",
            "/api/shop/202309/analytics/traffic_sources",
            params=params
        )
    
    async def get_revenue_report(
        self,
        start_date: str,
        end_date: str,
        currency: str = "LOCAL"
    ) -> Dict:
        """
        Get detailed revenue breakdown and financial metrics
        
        API: /api/finance/202309/analytics/revenue
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            currency: Currency code (default: LOCAL)
        
        Returns:
            Revenue breakdown including gross, net, refunds, fees
            
        Raises:
            ValueError: If date format is invalid
        """
        # Convert dates to Unix timestamps with validation
        from datetime import datetime
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        
        # Validate date range
        if start_ts > end_ts:
            raise ValueError("start_date must be before or equal to end_date")
        
        params = {
            "start_date": start_ts,
            "end_date": end_ts,
            "currency": currency
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        return await self._make_request(
            "GET",
            "/api/finance/202309/analytics/revenue",
            params=params
        )
    
    async def get_settlement_report(
        self,
        start_date: str,
        end_date: str,
        status: str = None
    ) -> Dict:
        """
        Get settlement and payout information
        
        API: /api/finance/202309/analytics/settlements
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            status: Settlement status filter (pending, completed, failed)
        
        Returns:
            Settlement data with payout information
            
        Raises:
            ValueError: If date format is invalid or status is not supported
        """
        # Validate status if provided
        if status:
            valid_statuses = ["pending", "completed", "failed"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}")
        
        # Convert dates to Unix timestamps with validation
        from datetime import datetime
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        
        # Validate date range
        if start_ts > end_ts:
            raise ValueError("start_date must be before or equal to end_date")
        
        params = {
            "start_date": start_ts,
            "end_date": end_ts
        }
        
        if status:
            params["status"] = status
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        return await self._make_request(
            "GET",
            "/api/finance/202309/analytics/settlements",
            params=params
        )
    
    async def get_top_products(
        self,
        start_date: str,
        end_date: str,
        metric: str = "sales",
        limit: int = 10
    ) -> Dict:
        """
        Get top performing products by various metrics
        
        API: /api/product/202309/analytics/top_products
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metric: Metric to sort by (sales, revenue, views, conversion_rate)
            limit: Number of products to return (max 50)
        
        Returns:
            Top products ranked by specified metric
            
        Raises:
            ValueError: If date format is invalid, metric is not supported, or limit is invalid
        """
        # Validate metric
        valid_metrics = ["sales", "revenue", "views", "conversion_rate"]
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric '{metric}'. Must be one of: {', '.join(valid_metrics)}")
        
        # Validate limit
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if limit > 50:
            raise ValueError("limit cannot exceed 50")
        
        # Convert dates to Unix timestamps with validation
        from datetime import datetime
        try:
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        
        # Validate date range
        if start_ts > end_ts:
            raise ValueError("start_date must be before or equal to end_date")
        
        params = {
            "start_date": start_ts,
            "end_date": end_ts,
            "metric": metric,
            "limit": limit
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        if self.shop_id:
            params["shop_id"] = self.shop_id
        
        return await self._make_request(
            "GET",
            "/api/product/202309/analytics/top_products",
            params=params
        )
    
    async def get_inventory(
        self,
        warehouse_id: str = None,
        page_size: int = 50,
        page_number: int = 1
    ) -> Dict:
        """
        Get inventory levels across warehouses
        
        API Version: 202309
        
        Args:
            warehouse_id: Optional warehouse ID filter
            page_size: Number of items per page
            page_number: Page number
        
        Returns:
            Inventory data
        """
        params = {
            "page_size": min(page_size, 100),
            "page_number": page_number,
            "version": "202309"
        }
        
        if self.shop_cipher:
            params["shop_cipher"] = self.shop_cipher
        
        body = {}
        if warehouse_id:
            body["warehouse_id"] = warehouse_id
        
        return await self._make_request(
            "POST",
            "/logistics/202309/inventory/search",
            params=params,
            body=body
        )
    
    @staticmethod
    def get_authorization_url(redirect_uri: str, state: str = None) -> str:
        """
        Generate TikTok OAuth authorization URL
        
        Args:
            redirect_uri: Callback URL after authorization
            state: Optional state parameter for CSRF protection
        
        Returns:
            Authorization URL
        """
        params = {
            "app_key": settings.tiktok_app_key,
            "state": state or "default_state"
        }
        
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{settings.tiktok_auth_url}?{param_str}"
    
    @staticmethod
    async def exchange_code_for_token(auth_code: str) -> Dict:
        """
        Exchange authorization code for access token
        
        Args:
            auth_code: Authorization code from OAuth callback
        
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        # Use the v2 token endpoint
        url = "https://auth.tiktok-shops.com/api/v2/token/get"
        
        params = {
            "app_key": settings.tiktok_app_key,
            "app_secret": settings.tiktok_app_secret,
            "auth_code": auth_code,
            "grant_type": "authorized_code"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
