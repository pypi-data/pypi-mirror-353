import pytest

from quake_sdk.client import QuakeClient
from quake_sdk.models import FilterableFieldsResponse

class TestFilterableFields:
    def test_get_service_filterable_fields(self, client: QuakeClient):
        response = client.get_service_filterable_fields()
        assert response.code == 0
        assert response.message == "Successful." # Note: Message ends with a period
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        assert "ip" in response.data
        assert "port" in response.data
        assert "service.name" in response.data # Example service field

    def test_get_host_filterable_fields(self, client: QuakeClient):
        response = client.get_host_filterable_fields()
        assert response.code == 0
        assert response.message == "Successful."
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        assert "ip" in response.data
        assert "location.country_cn" in response.data # Example host field

    def test_get_service_aggregation_fields(self, client: QuakeClient):
        response = client.get_service_aggregation_fields()
        assert response.code == 0
        assert response.message == "Successful."
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        assert "service" in response.data # Example aggregation field for service
        assert "country_cn" in response.data

    def test_get_host_aggregation_fields(self, client: QuakeClient):
        response = client.get_host_aggregation_fields()
        assert response.code == 0
        assert response.message == "Successful."
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        assert "port" in response.data # Example aggregation field for host
        assert "os" in response.data
