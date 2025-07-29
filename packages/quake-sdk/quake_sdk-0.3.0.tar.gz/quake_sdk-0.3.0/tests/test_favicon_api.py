import pytest

from quake_sdk.client import QuakeClient
from quake_sdk.exceptions import QuakeAPIException
from quake_sdk.models import FaviconSimilarityQuery, SimilarIconResponse

class TestFaviconSimilarity:
    def test_query_similar_icons(self, client: QuakeClient):
        """Tests favicon similarity query."""
        favicon_hash = "950e530fa6eeffba7a78b77a93afae28" 
        
        query_params = FaviconSimilarityQuery(
            favicon_hash=favicon_hash,
            similar=0.9,
            size=1
        )
        try:
            response = client.query_similar_icons(query_params)
            print(f"API Response: {response}")  # Print the response
        except QuakeAPIException as e:
             if "u3011" in str(e.api_code) or "permission" in str(e.message).lower() or "权限" in str(e.message):
                pytest.skip(f"Skipping favicon test due to potential permission/tier limitation: {e}")
             if "u3017" in str(e.api_code) or "not support" in str(e.message).lower(): 
                pytest.skip(f"Skipping favicon test as feature might not be supported by key: {e}")
             raise

        assert isinstance(response, SimilarIconResponse), "Response should be an instance of SimilarIconResponse"
        assert response.code == 0
        assert response.message == "Successful."
        assert response.data is not None
        assert isinstance(response.data, list)
        
        if len(response.data) > 0:
            for icon_data in response.data:
                assert hasattr(icon_data, 'key'), "Each icon_data should have a 'key' attribute"
                assert icon_data.key is not None, "icon_data.key should not be None"
                assert isinstance(icon_data.key, str), "icon_data.key should be a string"
                
                assert hasattr(icon_data, 'doc_count'), "Each icon_data should have a 'doc_count' attribute"
                assert icon_data.doc_count >= 0, "icon_data.doc_count should be non-negative"
                assert isinstance(icon_data.doc_count, int), "icon_data.doc_count should be an integer"
            
            # Assert that the expected favicon_hash is present in the results
            assert any(icon.key == favicon_hash for icon in response.data), \
                f"Expected favicon hash {favicon_hash} not found in response data keys: {[icon.key for icon in response.data]}"
        else:
            # If data is empty, the specific key cannot be present, so this should fail unless it's an expected empty result.
            # For this specific request, if data is empty, the assertion for the key will implicitly fail if we reach here without skipping.
            # However, the user's request implies that the key *should* be there.
            # So, if response.data is empty, we should probably assert False or let the any() check handle it if it's not skipped.
            # The current structure will print the message and then the test might pass if no other assertion fails.
            # To ensure the test fails if the key is expected but data is empty, we can add an assertion here or rely on the `any` check.
            # For now, let's assume if data is empty, the `any` check will correctly not find the key,
            # and if the test *requires* data, it should fail.
            # The current skip conditions might mean empty data is acceptable in some cases.
            # Let's make the assertion for the key more explicit if data is empty and the key is expected.
            # Given the user's request, if data is empty, it's an implicit failure for finding the key.
            # The `any` check will correctly evaluate to False if response.data is empty.
            # We might want to raise an assertion error if data is empty and a specific key was expected.
            # For now, the `any` check after the loop will cover this. If data is empty, `any` will be false.
            print(f"Favicon similarity query for {favicon_hash} returned no results. This might be okay if the test is designed to handle it.")
            # If the test *requires* this specific key, and data is empty, it should fail.
            # The `any` check below will handle this. If response.data is empty, `any(...)` will be false.
            # To be more explicit if data is empty and the key is expected:
            assert len(response.data) > 0, f"Expected favicon hash {favicon_hash} but received no data."
            assert any(icon.key == favicon_hash for icon in response.data), \
                f"Expected favicon hash {favicon_hash} not found in response data keys: {[icon.key for icon in response.data]}"
