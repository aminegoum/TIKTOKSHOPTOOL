"""
Test all TikTok Shop API endpoints to identify which are working
"""
import asyncio
import sys
from datetime import datetime, timedelta
from app.services.tiktok_client import TikTokShopClient
from app.services.token_manager import token_manager
from app.database import SessionLocal

async def test_endpoint(name: str, func, *args, **kwargs):
    """Test a single endpoint and return result"""
    try:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"{'='*60}")
        result = await func(*args, **kwargs)
        
        if isinstance(result, dict):
            code = result.get('code', 'N/A')
            message = result.get('message', 'N/A')
            has_data = 'data' in result
            
            if code == 0:
                print(f"✅ SUCCESS - Code: {code}, Has Data: {has_data}")
                return {'name': name, 'status': 'SUCCESS', 'code': code, 'has_data': has_data}
            else:
                print(f"❌ FAILED - Code: {code}, Message: {message}")
                return {'name': name, 'status': 'FAILED', 'code': code, 'message': message}
        else:
            print(f"✅ SUCCESS - Returned data")
            return {'name': name, 'status': 'SUCCESS', 'code': 'N/A', 'has_data': True}
            
    except Exception as e:
        print(f"❌ ERROR - {str(e)[:200]}")
        return {'name': name, 'status': 'ERROR', 'error': str(e)[:200]}

async def main():
    """Test all endpoints"""
    print("\n" + "="*60)
    print("TikTok Shop API Endpoint Testing")
    print("="*60)
    
    # Get access token
    db = SessionLocal()
    try:
        token_data = token_manager.get_valid_token(db)
        if not token_data:
            print("❌ No valid access token found. Please authenticate first.")
            return
        
        access_token = token_data.access_token
        print(f"✅ Access token found")
        
    finally:
        db.close()
    
    # Initialize client
    client = TikTokShopClient(access_token=access_token)
    
    # Date ranges for testing
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    results = []
    
    # Test Order endpoints
    print("\n" + "="*60)
    print("ORDER ENDPOINTS")
    print("="*60)
    
    results.append(await test_endpoint(
        "Get Orders",
        client.get_orders,
        page_size=10
    ))
    
    # Test Product endpoints
    print("\n" + "="*60)
    print("PRODUCT ENDPOINTS")
    print("="*60)
    
    results.append(await test_endpoint(
        "Get Products",
        client.get_products,
        page_size=10
    ))
    
    # Test Shop Performance endpoints
    print("\n" + "="*60)
    print("SHOP PERFORMANCE ENDPOINTS")
    print("="*60)
    
    results.append(await test_endpoint(
        "Get Shop Performance",
        client.get_shop_performance,
        start_time=start_time,
        end_time=end_time
    ))
    
    results.append(await test_endpoint(
        "Get Shop Performance Per Hour",
        client.get_shop_performance_per_hour,
        start_time=start_time,
        end_time=end_time
    ))
    
    results.append(await test_endpoint(
        "Get Shop Performance Overview",
        client.get_shop_performance_overview,
        start_time=start_time,
        end_time=end_time
    ))
    
    # Test Video Analytics endpoints
    print("\n" + "="*60)
    print("VIDEO ANALYTICS ENDPOINTS")
    print("="*60)
    
    results.append(await test_endpoint(
        "Get Shop Video Performance List",
        client.get_shop_video_performance_list,
        start_time=start_time,
        end_time=end_time
    ))
    
    results.append(await test_endpoint(
        "Get Shop Video Performance Overview",
        client.get_shop_video_performance_overview,
        start_time=start_time,
        end_time=end_time
    ))
    
    # Test LIVE Analytics endpoints
    print("\n" + "="*60)
    print("LIVE ANALYTICS ENDPOINTS")
    print("="*60)
    
    results.append(await test_endpoint(
        "Get Shop LIVE Performance List",
        client.get_shop_live_performance_list,
        start_time=start_time,
        end_time=end_time
    ))
    
    results.append(await test_endpoint(
        "Get Shop LIVE Performance Overview",
        client.get_shop_live_performance_overview,
        start_time=start_time,
        end_time=end_time
    ))
    
    # Test Product Analytics endpoints
    print("\n" + "="*60)
    print("PRODUCT ANALYTICS ENDPOINTS")
    print("="*60)
    
    results.append(await test_endpoint(
        "Get Shop Product Performance List",
        client.get_shop_product_performance_list,
        start_time=start_time,
        end_time=end_time
    ))
    
    results.append(await test_endpoint(
        "Get Shop SKU Performance List",
        client.get_shop_sku_performance_list,
        start_time=start_time,
        end_time=end_time
    ))
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['status'] == 'FAILED')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"\n✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⚠️  Errors: {error_count}")
    print(f"📊 Total: {len(results)}")
    
    print("\n" + "="*60)
    print("WORKING ENDPOINTS")
    print("="*60)
    for r in results:
        if r['status'] == 'SUCCESS':
            print(f"✅ {r['name']}")
    
    print("\n" + "="*60)
    print("FAILING ENDPOINTS")
    print("="*60)
    for r in results:
        if r['status'] in ['FAILED', 'ERROR']:
            status_icon = '❌' if r['status'] == 'FAILED' else '⚠️'
            error_msg = r.get('message', r.get('error', 'Unknown'))
            print(f"{status_icon} {r['name']}: {error_msg}")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
