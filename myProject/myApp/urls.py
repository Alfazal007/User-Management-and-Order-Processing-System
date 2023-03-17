from django.urls import path, include
from . import views
urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('menu-items/', views.menu_item_view),
    path('menu-items/<int:menu_item_id>', views.single_item_view),
    path('groups/manager/users', views.manager_view),
    path('groups/manager/users/<str:manager_username>', views.single_manager_view),
    path('groups/delivery-crew/users', views.delivery_crew_view),
    path('groups/delivery-crew/users/<str:username>', views.single_delivery_crew_view),
    path('cart/menu-items', views.cart_items),
    path('orders', views.order_handler),
    path('orders/<int:id_of_order>', views.single_order_handler),
]
