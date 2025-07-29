import pytest

from quake_sdk.client import QuakeClient
from quake_sdk.exceptions import QuakeInvalidRequestException, QuakeAPIException
from quake_sdk.models import RealtimeSearchQuery, ScrollSearchQuery, AggregationQuery

class TestErrorHandlingAndBoundaries:
    def test_search_service_data_unsupported_field_for_service(self, client: QuakeClient):
        """Tests querying service data with a field only valid for host data (e.g., location.gps)."""
        query = RealtimeSearchQuery(query="location.gps:[-90 TO 90]", size=1)
        with pytest.raises(QuakeInvalidRequestException) as exc_info:
            client.search_service_data(query)
        assert exc_info.value.api_code == "u3017" 
        assert "不支持该字段查询" in exc_info.value.message or "not support" in exc_info.value.message.lower()

    def test_search_service_data_size_zero(self, client: QuakeClient):
        """Tests service search with size=0."""
        query = RealtimeSearchQuery(query="port:80", size=0)
        response = client.search_service_data(query)
        assert response.code == 0
        assert response.data is not None
        print(f"Service search with size=0 returned {len(response.data)} items.")

    def test_scroll_service_data_size_zero(self, client: QuakeClient):
        """Tests service scroll with size=0."""
        query = ScrollSearchQuery(query="port:443", size=0)
        try:
            response = client.scroll_service_data(query)
            assert response.code == 0
            assert response.data is not None
            print(f"Service scroll with size=0 returned {len(response.data)} items.")
            if response.meta and response.meta.pagination_id:
                print(f"Service scroll with size=0 got pagination_id: {response.meta.pagination_id}")
        except QuakeInvalidRequestException as e:
            assert e.api_code in ["u3010", "u3009", "u3015"] 
            print(f"Service scroll with size=0 failed as expected with code {e.api_code}: {e.message}")
        except QuakeAPIException as e: 
            if "u3011" in str(e.api_code) or "permission" in str(e.message).lower() or "权限" in str(e.message):
                 pytest.skip(f"Skipping scroll size=0 test due to permission/tier: {e}")
            raise


    def test_aggregate_service_data_size_zero(self, client: QuakeClient):
        """Tests service aggregation with size=0 for buckets."""
        agg_query = AggregationQuery(
            query="port:80", 
            aggregation_list=["service.name"], 
            size=0
        )
        response = client.aggregate_service_data(agg_query)
        assert response.code == 0
        assert response.data is not None
        if "service.name" in response.data:
            assert isinstance(response.data["service.name"], list)
            print(f"Service aggregation with size=0 returned {len(response.data['service.name'])} buckets.")

    def test_search_service_data_start_beyond_total(self, client: QuakeClient):
        """Tests service search where start index is beyond total results."""
        query_total = RealtimeSearchQuery(query="app:nginx", size=1)
        response_total = client.search_service_data(query_total)
        assert response_total.code == 0
        
        total_count = 0
        if response_total.meta and response_total.meta.pagination and response_total.meta.pagination.total is not None:
            total_count = response_total.meta.pagination.total
        
        if total_count == 0 and not response_total.data: 
            pytest.skip("Skipping start_beyond_total test as base query 'app:nginx' returned no results.")

        start_index = total_count + 10 if total_count > 0 else 10000 
        if total_count == 0 and response_total.data: 
            start_index = 20 

        query_beyond = RealtimeSearchQuery(query="app:nginx", size=10, start=start_index)
        response_beyond = client.search_service_data(query_beyond)
        assert response_beyond.code == 0
        assert response_beyond.data is not None
        assert len(response_beyond.data) == 0
        print(f"Service search with start={start_index} (total ~{total_count}) returned {len(response_beyond.data)} items as expected.")
