import pytest
from datetime import datetime, timedelta, timezone

from quake_sdk.client import QuakeClient
from quake_sdk.exceptions import QuakeInvalidRequestException, QuakeAPIException
from quake_sdk.models import (
    RealtimeSearchQuery, ScrollSearchQuery, AggregationQuery,
    ServiceSearchResponse, ServiceScrollResponse, ServiceAggregationResponse
)

class TestServiceScroll:
    def test_scroll_service_data(self, client: QuakeClient):
        """测试服务数据滚动（深度分页）。"""
        base_query_str = 'service:"http"' 
        initial_query_params = ScrollSearchQuery(query=base_query_str, size=1, latest=True)
        
        try:
            initial_response = client.scroll_service_data(initial_query_params)
        except QuakeAPIException as e:
            if "u3011" in str(e.api_code) or "permission" in str(e.message).lower() or "权限" in str(e.message):
                pytest.skip(f"由于潜在的权限/级别限制，跳过滚动测试: {e}")
            raise

        assert initial_response.code == 0
        assert initial_response.meta is not None
        
        pagination_id = initial_response.meta.pagination_id
        total_results = initial_response.meta.total
        if isinstance(total_results, dict): 
            total_results = total_results.get("value", 0)
        
        assert total_results is not None

        if initial_response.data and len(initial_response.data) > 0:
            first_item_ip = initial_response.data[0].ip
        else:
            first_item_ip = None

        if pagination_id and total_results > 1 :
            next_page_query_params = ScrollSearchQuery(
                query=base_query_str, 
                size=1,               
                latest=True,          
                pagination_id=pagination_id
            )
            
            next_response = client.scroll_service_data(next_page_query_params)
            assert next_response.code == 0
            assert next_response.data is not None
            
            if len(next_response.data) > 0:
                assert "http" in next_response.data[0].service.name # Allow "http/ssl"
                if first_item_ip and next_response.data[0].ip != first_item_ip:
                    print(f"滚动测试：初始 IP {first_item_ip}, 下一页 IP {next_response.data[0].ip}")
                elif len(initial_response.data) == 0 and len(next_response.data) > 0:
                     print(f"滚动测试：初始页为空, 下一页 IP {next_response.data[0].ip}")
                else:
                    print("滚动测试：下一页项目可能与初始页相同，或初始页为空。")
            else:
                print("滚动测试：下一页未返回数据，这可能是预期的。")
        else:
            skip_reason = "数据不足 (total <= 1)" if total_results <=1 else "未返回 pagination_id"
            if not initial_response.data:
                skip_reason += " 且第一页无数据"
            pytest.skip(f"跳过滚动继续: {skip_reason}. 总数: {total_results}, PagID: {pagination_id}")

    def test_scroll_service_data_with_all_params(self, client: QuakeClient):
        """测试使用各种参数进行服务数据滚动。"""
        base_query_str = 'service:"http" AND country_cn:"中国"'
        
        prelim_query = RealtimeSearchQuery(query=base_query_str, size=1, latest=True)
        prelim_response = client.search_service_data(prelim_query)
        assert prelim_response.code == 0
        if not (prelim_response.data and len(prelim_response.data) > 0 and prelim_response.data[0].time):
            pytest.skip("无法确定滚动时间范围测试的有效时间。未找到查询的最近数据。")

        try:
            recent_time_dt = prelim_response.data[0].time
            if not isinstance(recent_time_dt, datetime):
                 recent_time_dt = datetime.fromisoformat(recent_time_dt.replace('Z', '+00:00'))
        except Exception as e:
            pytest.skip(f"无法从初步响应中解析时间以进行滚动时间范围测试: {e}")

        if recent_time_dt.tzinfo is None:
            recent_time_dt = recent_time_dt.replace(tzinfo=timezone.utc)
        
        end_time_dt = recent_time_dt
        start_time_dt = end_time_dt - timedelta(days=7)

        start_time_str = start_time_dt.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time_dt.strftime("%Y-%m-%d %H:%M:%S")

        scroll_params = ScrollSearchQuery(
            query=base_query_str,
            size=2, 
            latest=False, 
            ignore_cache=True,
            start_time=start_time_str,
            end_time=end_time_str,
            include=["ip", "port", "service.name", "time", "location.city_cn"],
            exclude=["service.response", "service.cert"]
        )
        
        try:
            response1 = client.scroll_service_data(scroll_params)
        except QuakeAPIException as e:
            if "u3011" in str(e.api_code) or "permission" in str(e.message).lower() or "权限" in str(e.message) or "付费" in str(e.message):
                pytest.skip(f"由于权限/级别原因，跳过 scroll_service_data_with_all_params: {e}")
            if "u3017" in str(e.api_code): 
                 pytest.skip(f"由于密钥可能不支持该功能，跳过 scroll_service_data_with_all_params: {e}")
            raise

        assert response1.code == 0
        assert response1.meta is not None
        pagination_id1 = response1.meta.pagination_id
        
        if response1.data:
            assert len(response1.data) <= 2
            for item in response1.data:
                assert item.ip is not None
                assert item.port is not None
                assert "http" in item.service.name # Allow "http/ssl"
                assert item.time is not None
                assert item.location.city_cn is not None
                assert not hasattr(item.service, 'response') or item.service.response is None 
                assert not hasattr(item.service, 'cert') or item.service.cert is None 
                
                item_time_dt = item.time
                if not isinstance(item_time_dt, datetime):
                    item_time_dt = datetime.fromisoformat(item_time_dt.replace('Z', '+00:00'))
                if item_time_dt.tzinfo is None:
                    item_time_dt = item_time_dt.replace(tzinfo=timezone.utc)
                assert start_time_dt - timedelta(seconds=1) <= item_time_dt <= end_time_dt + timedelta(seconds=1)

        if pagination_id1 and (response1.meta.total.get("value", 0) if isinstance(response1.meta.total, dict) else response1.meta.total) > len(response1.data or []):
            scroll_params_page2 = scroll_params.model_copy(update={"pagination_id": pagination_id1})
            
            response2 = client.scroll_service_data(scroll_params_page2)
            assert response2.code == 0
            if response2.data:
                assert len(response2.data) <= 2
                for item in response2.data:
                    assert item.ip is not None
                    assert "http" in item.service.name # Allow "http/ssl"
            print("使用所有参数滚动：成功获取第二页。")
        else:
            print("使用所有参数滚动：数据不足或没有用于第二页的 pagination_id。") 