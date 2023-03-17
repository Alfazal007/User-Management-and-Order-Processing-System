from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True,required=False , default=1)
    class Meta:
        model = MenuItem
        fields = ['title', 'price','featured' , 'category', 'category_id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    menuItem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    # user_id = serializers.IntegerField(write_only=True)
    def create(self, validated_data):
        # get the authenticated user's ID from the request object
        user_id = self.context['request'].user.id
        # set the user_id in the validated data
        validated_data['user_id'] = user_id
        # create and return the instance
        instance = Cart(**validated_data)
        instance.save()
        return instance

    class Meta:
        model = Cart
        fields = ['user', 'menuItem', 'quantity', 'unit_price', 'price', 'menuitem_id', 'user_id']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delivery_crew = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    order = UserSerializer(read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']

# class OrderItem(models.Model):
#     order = models.ForeignKey(User, on_delete=models.CASCADE)
#     menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
#     quantity = models.SmallIntegerField()
#     unit_price = models.DecimalField(max_digits=6, decimal_places=2)
#     price = models.DecimalField(max_digits=6, decimal_places=2)

#     class Meta:
#         unique_together = ('order', 'menuitem')
