def test_search_page_loads(auth_client):
    response = auth_client.get("/search")
    assert response.status_code == 200


def test_search_empty_query(auth_client):
    response = auth_client.get("/search?q=")
    assert response.status_code == 200
    assert b"What are you looking for?" in response.data


def test_search_posts(auth_client):
    auth_client.post(
        "/posts/new",
        data={
            "title": "Python async await guide",
            "body": "A guide to async programming",
            "topic_id": "",
        },
    )
    response = auth_client.get("/search?q=python")
    assert response.status_code == 200
    assert b"Python async await guide" in response.data


def test_search_no_results(auth_client):
    response = auth_client.get("/search?q=notaword123")
    assert response.status_code == 200
    assert b"No posts found" in response.data


def test_search_topics(auth_client):
    auth_client.post(
        "/topics/new",
        data={"name": "rustlang", "description": "The Rust programming language"},
    )
    response = auth_client.get("/search?q=rust&type=topics")
    assert response.status_code == 200
    assert b"rustlang" in response.data
