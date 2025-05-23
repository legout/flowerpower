"""
Basic tests for FlowerPower Web UI
"""

import asyncio
import json

from app import app


async def test_routes():
    """Test basic route accessibility"""
    print("🧪 Testing FlowerPower Web UI Routes")
    print("=" * 40)

    # Create test client
    request, response = await app.asgi_client.get("/")
    assert response.status == 200
    assert "FlowerPower" in response.text
    print("✅ Home page loads correctly")

    # Test projects list
    request, response = await app.asgi_client.get("/projects")
    assert response.status == 200
    assert "Projects" in response.text
    print("✅ Projects page loads correctly")

    # Test new project form
    request, response = await app.asgi_client.get("/projects/new")
    assert response.status == 200
    assert "Create New Project" in response.text
    print("✅ New project form loads correctly")

    # Test API endpoint
    request, response = await app.asgi_client.get("/api/projects")
    assert response.status == 200
    data = json.loads(response.text)
    assert "projects" in data
    print("✅ API endpoint works correctly")

    # Test project detail
    request, response = await app.asgi_client.get("/projects/1")
    assert response.status == 200
    print("✅ Project detail page loads correctly")

    # Test non-existent project
    request, response = await app.asgi_client.get("/projects/999")
    assert response.status == 200
    assert "Project Not Found" in response.text
    print("✅ 404 handling works correctly")

    print("\n🎉 All tests passed!")


async def test_project_creation():
    """Test project creation via form submission"""
    print("\n🧪 Testing Project Creation")
    print("=" * 30)

    # Test valid project creation
    form_data = {"name": "Test Project", "description": "A test project for validation"}

    request, response = await app.asgi_client.post("/projects", data=form_data)
    assert response.status == 200
    data = json.loads(response.text)
    assert data["status"] == "success"
    print("✅ Project creation works correctly")

    # Test empty name validation
    form_data = {"name": "", "description": "Project with empty name"}

    request, response = await app.asgi_client.post("/projects", data=form_data)
    assert response.status == 200
    data = json.loads(response.text)
    assert data["status"] == "error"
    print("✅ Empty name validation works correctly")

    print("\n🎉 Project creation tests passed!")


def test_template_generation():
    """Test htpy template generation"""
    print("\n🧪 Testing Template Generation")
    print("=" * 30)

    from app import base_layout, project_card
    from htpy import html as h

    # Test base layout
    content = h.div("Test content")
    layout = base_layout("Test Page", content)
    assert "Test Page - FlowerPower" in layout
    assert "Test content" in layout
    assert "data-ds-stream" in layout
    print("✅ Base layout generation works correctly")

    # Test project card
    test_project = {
        "id": 1,
        "name": "Test Project",
        "description": "Test description",
        "created_at": "2025-01-23T12:00:00Z",
    }

    card_html = str(project_card(test_project))
    assert "Test Project" in card_html
    assert "Test description" in card_html
    assert "2025-01-23" in card_html
    print("✅ Project card generation works correctly")

    print("\n🎉 Template generation tests passed!")


async def main():
    """Run all tests"""
    try:
        test_template_generation()
        await test_routes()
        await test_project_creation()

        print("\n" + "=" * 50)
        print("🎉 All FlowerPower Web UI tests passed!")
        print("✨ Application is ready for deployment")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
