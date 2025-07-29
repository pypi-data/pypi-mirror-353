import pytest
from datetime import datetime, timedelta, timezone

from quake_sdk.client import QuakeClient
from quake_sdk.exceptions import QuakeInvalidRequestException, QuakeAPIException
from quake_sdk.models import (
    RealtimeSearchQuery, ScrollSearchQuery, AggregationQuery,
    ServiceSearchResponse, ServiceScrollResponse, ServiceAggregationResponse
)

class TestServiceAggregation:
    def test_aggregate_service_data(self, client: QuakeClient):
        """测试服务数据聚合。"""
        agg_query = AggregationQuery(
            query="country_cn:\"中国\"",
            aggregation_list=["service", "port"],
            size=3, 
            latest=True
        )
        try:
            response = client.aggregate_service_data(agg_query)
        except QuakeAPIException as e:
            if "u3011" in str(e.api_code) or "permission" in str(e.message).lower() or "权限" in str(e.message):
                pytest.skip(f"由于潜在的权限/级别限制，跳过服务聚合测试: {e}")
            raise

        print(f"Response for test_aggregate_service_data: {response.model_dump_json(indent=2)}")
        assert response.code == 0
        assert response.message == "Successful." # 成功的消息通常是英文
        assert response.data is not None
        
        for agg_field in agg_query.aggregation_list:
            assert agg_field in response.data, f"聚合字段 {agg_field} 未在响应中找到"
            assert isinstance(response.data[agg_field], list)
            if len(response.data[agg_field]) > 0:
                bucket = response.data[agg_field][0]
                assert hasattr(bucket, 'key') and bucket.key is not None
                assert hasattr(bucket, 'doc_count') and bucket.doc_count >= 0
            else:
                print(f"{agg_field} 的服务聚合未返回任何桶。这可能是正常的。")

    def test_aggregate_service_data_with_all_params(self, client: QuakeClient):
        """测试使用各种参数进行服务数据聚合。"""
        base_query_str = 'country_cn:"中国" AND app:"nginx"' 
        
        prelim_query = RealtimeSearchQuery(query=base_query_str, size=1, latest=True)
        prelim_response = client.search_service_data(prelim_query)
        assert prelim_response.code == 0
        if not (prelim_response.data and len(prelim_response.data) > 0 and prelim_response.data[0].time):
            pytest.skip("无法确定聚合时间范围测试的有效时间。")

        try:
            recent_time_dt = prelim_response.data[0].time
            if not isinstance(recent_time_dt, datetime):
                 recent_time_dt = datetime.fromisoformat(recent_time_dt.replace('Z', '+00:00'))
        except Exception as e:
            pytest.skip(f"无法从初步响应中解析时间以进行聚合时间范围测试: {e}")

        if recent_time_dt.tzinfo is None:
            recent_time_dt = recent_time_dt.replace(tzinfo=timezone.utc)
        
        end_time_dt = recent_time_dt
        start_time_dt = end_time_dt - timedelta(days=30) 

        start_time_str = start_time_dt.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time_dt.strftime("%Y-%m-%d %H:%M:%S")

        agg_params = AggregationQuery(
            query=base_query_str,
            size=3, 
            latest=False, 
            ignore_cache=True,
            start_time=start_time_str,
            end_time=end_time_str,
            aggregation_list=["port", "service.http.status_code"]
        )

        try:
            response = client.aggregate_service_data(agg_params)
        except QuakeAPIException as e:
            if "u3011" in str(e.api_code) or "permission" in str(e.message).lower() or "权限" in str(e.message) or "付费" in str(e.message):
                pytest.skip(f"由于权限/级别原因，跳过 aggregate_service_data_with_all_params: {e}")
            if "u3017" in str(e.api_code):
                 pytest.skip(f"由于密钥可能不支持该功能，跳过 aggregate_service_data_with_all_params: {e}")
            raise
        
        assert response.code == 0
        assert response.message == "Successful." # 成功的消息通常是英文
        assert response.data is not None

        if "port" in response.data:
            assert isinstance(response.data["port"], list)
            if len(response.data["port"]) > 0:
                bucket = response.data["port"][0]
                assert hasattr(bucket, 'key') and bucket.key is not None
                assert hasattr(bucket, 'doc_count') and bucket.doc_count >= 0
            else:
                print("port 的 all_params 聚合未返回任何桶。这可能是正常的。")
        else:
            print("警告：all_params 测试的响应数据中缺少 'port' 聚合字段。")


        if "service.http.status_code" in response.data:
            assert isinstance(response.data["service.http.status_code"], list)
        
        print("使用所有参数的聚合测试已完成。") 