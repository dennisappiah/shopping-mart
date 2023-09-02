from rest_framework_nested import routers
from . import views

# parent router -> /products, /collections
router = routers.DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)
router.register("carts", views.CartViewSet, basename="carts")
router.register("customers", views.CustomerViewSet)
router.register("orders", views.OrderViewSet, basename="orders")

# children router -> /products/1/reviews
product_router = routers.NestedDefaultRouter(router, "products", lookup="product")
product_router.register("reviews", views.ReviewViewSet, basename="product-reviews")

cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewSet, basename="cart-items")


urlpatterns = router.urls + product_router.urls + cart_router.urls
