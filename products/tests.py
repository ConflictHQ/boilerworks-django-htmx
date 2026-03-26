import pytest
from django.urls import reverse

from .models import Product


@pytest.fixture
def sample_product(db, admin_user):
    return Product.objects.create(name="Test Widget", price="29.99", sku="TST-001", created_by=admin_user)


@pytest.mark.django_db
class TestProductList:
    def test_list_requires_login(self, client):
        response = client.get(reverse("products:list"))
        assert response.status_code == 302

    def test_list_renders_for_superuser(self, admin_client, sample_product):
        response = admin_client.get(reverse("products:list"))
        assert response.status_code == 200
        assert b"Test Widget" in response.content

    def test_list_renders_for_viewer(self, viewer_client, sample_product):
        response = viewer_client.get(reverse("products:list"))
        assert response.status_code == 200
        assert b"Test Widget" in response.content

    def test_list_denied_for_user_without_perm(self, no_perm_client, sample_product):
        response = no_perm_client.get(reverse("products:list"))
        assert response.status_code == 403

    def test_list_htmx_returns_partial(self, admin_client, sample_product):
        response = admin_client.get(reverse("products:list"), HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert b"product-table" in response.content
        assert b"<!DOCTYPE" not in response.content  # partial, not full page

    def test_list_search_filters(self, admin_client, admin_user):
        Product.objects.create(name="Alpha", price="10.00", created_by=admin_user)
        Product.objects.create(name="Beta", price="20.00", created_by=admin_user)
        response = admin_client.get(reverse("products:list") + "?search=Alpha")
        assert b"Alpha" in response.content
        assert b"Beta" not in response.content


@pytest.mark.django_db
class TestProductCreate:
    def test_create_form_renders(self, admin_client):
        response = admin_client.get(reverse("products:create"))
        assert response.status_code == 200
        assert b"New Product" in response.content

    def test_create_saves_product(self, admin_client, admin_user):
        response = admin_client.post(
            reverse("products:create"),
            {"name": "New Gadget", "description": "A new gadget", "price": "49.99", "sku": "NGT-001", "is_active": True},
        )
        assert response.status_code == 302
        product = Product.objects.get(sku="NGT-001")
        assert product.name == "New Gadget"
        assert product.created_by == admin_user

    def test_create_denied_for_viewer(self, viewer_client):
        response = viewer_client.get(reverse("products:create"))
        assert response.status_code == 403

    def test_create_invalid_data_shows_errors(self, admin_client):
        response = admin_client.post(reverse("products:create"), {"name": "", "price": ""})
        assert response.status_code == 200  # re-renders form with errors


@pytest.mark.django_db
class TestProductDetail:
    def test_detail_renders(self, admin_client, sample_product):
        response = admin_client.get(reverse("products:detail", kwargs={"slug": sample_product.slug}))
        assert response.status_code == 200
        assert b"Test Widget" in response.content
        assert str(sample_product.guid).encode() in response.content

    def test_detail_404_for_deleted(self, admin_client, sample_product, admin_user):
        sample_product.soft_delete(user=admin_user)
        response = admin_client.get(reverse("products:detail", kwargs={"slug": sample_product.slug}))
        assert response.status_code == 404


@pytest.mark.django_db
class TestProductUpdate:
    def test_update_form_renders(self, admin_client, sample_product):
        response = admin_client.get(reverse("products:update", kwargs={"slug": sample_product.slug}))
        assert response.status_code == 200
        assert b"Edit Product" in response.content

    def test_update_saves_changes(self, admin_client, sample_product):
        response = admin_client.post(
            reverse("products:update", kwargs={"slug": sample_product.slug}),
            {"name": "Updated Widget", "description": "Updated", "price": "39.99", "sku": "TST-001", "is_active": True},
        )
        assert response.status_code == 302
        sample_product.refresh_from_db()
        assert sample_product.name == "Updated Widget"
        from decimal import Decimal

        assert sample_product.price == Decimal("39.99")

    def test_update_denied_for_viewer(self, viewer_client, sample_product):
        response = viewer_client.get(reverse("products:update", kwargs={"slug": sample_product.slug}))
        assert response.status_code == 403


@pytest.mark.django_db
class TestProductDelete:
    def test_delete_confirm_renders(self, admin_client, sample_product):
        response = admin_client.get(reverse("products:delete", kwargs={"slug": sample_product.slug}))
        assert response.status_code == 200
        assert b"Delete Product" in response.content

    def test_delete_soft_deletes(self, admin_client, sample_product):
        response = admin_client.post(reverse("products:delete", kwargs={"slug": sample_product.slug}))
        assert response.status_code == 302
        sample_product.refresh_from_db()
        assert sample_product.is_deleted

    def test_delete_htmx_returns_redirect_header(self, admin_client, sample_product):
        response = admin_client.post(
            reverse("products:delete", kwargs={"slug": sample_product.slug}),
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200
        assert response.headers.get("HX-Redirect") == "/products/"

    def test_delete_denied_for_viewer(self, viewer_client, sample_product):
        response = viewer_client.post(reverse("products:delete", kwargs={"slug": sample_product.slug}))
        assert response.status_code == 403
