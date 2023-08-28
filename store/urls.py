from rest_framework_nested import routers
from . import views

# parent router -> /products, /collections
router = routers.DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)

# children router -> /products/1/reviews
product_router = routers.NestedDefaultRouter(router, "products", lookup="product")
product_router.register("reviews", views.ReviewViewSet, basename="product-reviews")

urlpatterns = router.urls + product_router.urls
