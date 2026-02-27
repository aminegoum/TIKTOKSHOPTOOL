"""
Script to update all analytics methods in tiktok_client.py with correct parameter names
Based on analytics_full.json specifications
"""

# This script documents the required changes for all analytics methods
# The key changes are:
# 1. start_date -> start_date_ge (greater than or equal, inclusive)
# 2. end_date -> end_date_lt (less than, exclusive)
# 3. page_number -> page_token (for pagination)
# 4. Add granularity parameter where applicable

REQUIRED_UPDATES = {
    "get_shop_performance_metrics": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "add": ["granularity"]
        }
    },
    "get_shop_video_performance_list": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "page_number": "page_token",
            "add": ["sort_field", "sort_order", "account_type"]
        }
    },
    "get_shop_video_performance_overview": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "add": ["today", "granularity", "account_type"]
        }
    },
    "get_shop_video_performance_details": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "add": ["granularity"]
        }
    },
    "get_shop_video_product_performance_list": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "page_number": "page_token",
            "add": ["sort_field", "sort_order"]
        }
    },
    "get_shop_live_performance_list": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "page_number": "page_token",
            "add": ["sort_field", "sort_order", "account_type"]
        }
    },
    "get_shop_live_performance_overview": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "add": ["today", "granularity", "account_type"]
        }
    },
    "get_shop_live_performance_per_minutes": {
        "params": {
            "add": ["page_token"]  # No date params for this endpoint
        }
    },
    "get_shop_live_products_performance": {
        "params": {
            "page_number": "page_token",  # No date params
            "add": ["sort_field", "sort_order"]
        }
    },
    "get_shop_product_performance_list": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "page_number": "page_token",
            "add": ["sort_field", "sort_order", "category_filter", "product_status_filter"]
        }
    },
    "get_product_performance": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "add": ["granularity"]
        }
    },
    "get_shop_sku_performance_list": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "page_number": "page_token",
            "add": ["sort_field", "sort_order", "category_filter", "product_status_filter", "product_ids"]
        }
    },
    "get_shop_sku_performance": {
        "params": {
            "start_date": "start_date_ge",
            "end_date": "end_date_lt",
            "add": ["granularity"]
        }
    }
}

print("Analytics Methods Parameter Updates Required:")
print("=" * 80)
for method, changes in REQUIRED_UPDATES.items():
    print(f"\n{method}:")
    if "start_date" in changes["params"]:
        print(f"  - Change: start_date -> start_date_ge")
    if "end_date" in changes["params"]:
        print(f"  - Change: end_date -> end_date_lt")
    if "page_number" in changes["params"]:
        print(f"  - Change: page_number -> page_token")
    if "add" in changes["params"]:
        print(f"  - Add optional params: {', '.join(changes['params']['add'])}")
