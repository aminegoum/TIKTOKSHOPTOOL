"""
Test all TikTok Shop Dashboard API endpoints via HTTP
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_endpoint(name: str, method: str, path: str, params: dict = None, json_data: dict = None):
    """Test a single API endpoint"""
    try:
        url = f"{BASE_URL}{path}"
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"Method: {method} {path}")
        if params:
            print(f"Params: {params}")
        print(f"{'='*60}")
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return {'name': name, 'status': 'ERROR', 'error': 'Unsupported method'}
        
        status_code = response.status_code
        
        if status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS - Status: {status_code}")
                print(f"Response preview: {json.dumps(data, indent=2)[:200]}...")
                return {'name': name, 'status': 'SUCCESS', 'code': status_code, 'has_data': bool(data)}
            except:
                print(f"✅ SUCCESS - Status: {status_code} (non-JSON response)")
                return {'name': name, 'status': 'SUCCESS', 'code': status_code, 'has_data': True}
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', 'Unknown error')
            except:
                error_msg = response.text[:200]
            
            print(f"❌ FAILED - Status: {status_code}")
            print(f"Error: {error_msg}")
            return {'name': name, 'status': 'FAILED', 'code': status_code, 'message': error_msg}
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR - Cannot connect to {BASE_URL}")
        return {'name': name, 'status': 'ERROR', 'error': 'Connection refused - is the server running?'}
    except requests.exceptions.Timeout:
        print(f"⚠️  TIMEOUT - Request took too long")
        return {'name': name, 'status': 'ERROR', 'error': 'Request timeout'}
    except Exception as e:
        print(f"❌ ERROR - {str(e)[:200]}")
        return {'name': name, 'status': 'ERROR', 'error': str(e)[:200]}

def main():
    """Test all API endpoints"""
    print("\n" + "="*60)
    print("TikTok Shop Dashboard API Testing")
    print("="*60)
    
    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    results = []
    
    # Test Health endpoints
    print("\n" + "="*60)
    print("HEALTH & STATUS ENDPOINTS")
    print("="*60)
    
    results.append(test_endpoint(
        "Root Endpoint",
        "GET",
        "/"
    ))
    
    results.append(test_endpoint(
        "Health Check",
        "GET",
        "/health"
    ))
    
    # Test Auth endpoints
    print("\n" + "="*60)
    print("AUTHENTICATION ENDPOINTS")
    print("="*60)
    
    results.append(test_endpoint(
        "Auth Status",
        "GET",
        "/api/auth/status"
    ))
    
    results.append(test_endpoint(
        "Get Auth URL",
        "GET",
        "/api/auth/url"
    ))
    
    # Test Sync endpoints
    print("\n" + "="*60)
    print("SYNC ENDPOINTS")
    print("="*60)
    
    results.append(test_endpoint(
        "Sync Status",
        "GET",
        "/api/sync/status"
    ))
    
    # Test KPI endpoints
    print("\n" + "="*60)
    print("KPI ENDPOINTS")
    print("="*60)
    
    results.append(test_endpoint(
        "Get KPIs",
        "GET",
        "/api/kpis"
    ))
    
    results.append(test_endpoint(
        "Get Daily Trends",
        "GET",
        "/api/kpis/trends/daily",
        params={"days": 7}
    ))
    
    results.append(test_endpoint(
        "Get Order Status Breakdown",
        "GET",
        "/api/kpis/orders/status"
    ))
    
    # Test Analytics endpoints
    print("\n" + "="*60)
    print("ANALYTICS ENDPOINTS")
    print("="*60)
    
    results.append(test_endpoint(
        "Shop Performance",
        "GET",
        "/api/analytics/shop/performance",
        params={"start_date": start_date, "end_date": end_date}
    ))
    
    results.append(test_endpoint(
        "Shop Performance Per Hour",
        "GET",
        "/api/analytics/shop/performance/hourly",
        params={"start_date": start_date, "end_date": end_date}
    ))
    
    results.append(test_endpoint(
        "Shop Performance Overview",
        "GET",
        "/api/analytics/shop/performance/overview",
        params={"start_date": start_date, "end_date": end_date}
    ))
    
    results.append(test_endpoint(
        "Video Performance List",
        "GET",
        "/api/analytics/videos/performance",
        params={"start_date": start_date, "end_date": end_date}
    ))
    
    results.append(test_endpoint(
        "Video Performance Overview",
        "GET",
        "/api/analytics/videos/overview",
        params={"start_date": start_date, "end_date": end_date}
    ))
    
    results.append(test_endpoint(
        "LIVE Performance List",
        "GET",
        "/api/analytics/lives/performance",
        params={"start_date": start_date, "end_date": end_date}
    ))
    
    results.append(test_endpoint(
        "LIVE Performance Overview",
        "GET",
        "/api/analytics/lives/overview",
        params={"start_date": start_date, "end_date": end_date}
    ))
    
    results.append(test_endpoint(
        "Product Performance List",
        "GET",
        "/api/analytics/products/performance",
        params={"start_date": start_date, "end_date": end_date}
    ))
    
    results.append(test_endpoint(
        "SKU Performance List",
        "GET",
        "/api/analytics/skus/performance",
        params={"start_date": start_date, "end_date": end_date}
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
    
    # Return exit code based on results
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    exit(main())
