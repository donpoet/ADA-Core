import httpx
import pytest

@pytest.mark.e2e
def test_chat_conversation_flow():
    with httpx.Client(base_url="http://localhost:8000", timeout=300) as client:

        response = client.post(
            "/chat",
            json={
                "prompt": "Mein Name ist Michael.",
            },
        )

        # Check whether request goes through
        assert response.status_code == 200

        # Get data
        first_data = response.json()

        # Assert conversation logic is working
        assert "conversation_id" in first_data
        assert first_data["conversation_id"] is not None

        conversation_id = first_data["conversation_id"]

        # Continue on the same conversation
        response = client.post(
            "/chat",
            json={
                "conversation_id": conversation_id,
                "prompt": "Wie heiße ich?",
            },
        )

        # Assert request successful
        assert response.status_code == 200

        second_data = response.json()

        # Assert same conversation and correct output
        assert second_data["conversation_id"] == conversation_id
        assert "Michael" in second_data["response"]