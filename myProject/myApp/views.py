from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .models import *
from .serializers import *
from django.contrib.auth.models import User, Group
from rest_framework.permissions import IsAuthenticated
import datetime
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

# Create your views here.

@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def menu_item_view(request):
    if request.method == "GET":
        items = MenuItem.objects.all()
        title = request.query_params.get('title')
        price = request.query_params.get('price')
        if title:
            items = items.filter(title=title)
        if price:
            items = items.filter(price__lte = price)
        items_to_view = MenuItemSerializer(items, many=True)
        return Response(items_to_view.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        if request.user.groups.filter(name="Manager").exists():
            items_to_add = MenuItemSerializer(data=request.data)
            items_to_add.is_valid(raise_exception=True)
            items_to_add.save()
            return Response({'message' : 'Updated'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message' : 'You are not authorized'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_item_view(request, menu_item_id):
    try:
        item = MenuItem.objects.get(pk = menu_item_id)
    except MenuItem.DoesNotExist:
        return Response({"message" : "Menu item does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        item_to_view = MenuItemSerializer(item)
        return Response(item_to_view.data, status = status.HTTP_200_OK)
    elif request.method == "PATCH":
        if request.user.groups.filter(name="Manager").exists():
            if request.method == "PATCH":
                item_to_update = MenuItemSerializer(instance=item, data=request.data, partial=True)
                item_to_update.is_valid(raise_exception=True)
                item_to_update.save()
                return Response({"message" : "contents updated refresh to view the changes"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message" : "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)
    elif request.method == "PUT":
        if request.user.groups.filter(name="Manager").exists():
            if request.method == "PUT":
                item_to_update = MenuItemSerializer(instance=item, data=request.data)
                item_to_update.is_valid(raise_exception=True)
                item_to_update.save()
                return Response({"message" : "contents updated refresh to view the changes"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message" : "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == "DELETE":
        if request.user.groups.filter(name="Manager").exists():
            item.delete()
            return Response({"message" : "delete successful"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message" : "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
def manager_view(request):
    if request.user.groups.filter(name="Manager").exists():
        if request.method == "GET":
            group = Group.objects.get(name="Manager")
            users = User.objects.filter(groups=group)
            users_to_display = UserSerializer(users, many=True)
            return Response(users_to_display.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            username = request.POST.get('username')
            group = Group.objects.get(name="Manager")
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message" : "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            user.groups.add(group)
            return Response({"message" : "User added to manager group"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"message" : "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)


@api_view(["DELETE"])
def single_manager_view(request, manager_username):
    if request.user.groups.filter(name="Manager").exists():
        group = Group.objects.get(name="Manager")
        try:
            user = User.objects.get(username=manager_username)
        except User.DoesNotExist:
            return Response({"message" : "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        user.groups.remove(group)
        return Response({"message" : "user removed from the group"}, status=status.HTTP_200_OK)
    else:
        return Response({"message" : "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", 'POST'])
def delivery_crew_view(request):
    if request.user.groups.filter(name="Manager").exists():
        if request.method == "GET":
            group = Group.objects.get(name="Delivery crew")
            users = User.objects.filter(groups = group)
            users_to_display = UserSerializer(users, many=True)
            return Response(users_to_display.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            username = request.POST.get('username')
            group = Group.objects.get(name="Delivery crew")
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message" : "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            user.groups.add(group)
            return Response({"message" : "User has been added to delivery crew group"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"message" : "You are not authorized"}, status= status.HTTP_403_FORBIDDEN)


@api_view(["DELETE"])
def single_delivery_crew_view(request, username):
    if request.user.groups.filter(name="Manager").exists():
        group = Group.objects.get(name="Delivery crew")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"message" : "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        user.groups.remove(group)
        return Response({"message" : "user removed from group"}, status=status.HTTP_200_OK)
    else:
        return Response({"message" : "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_items(request):
    if request.method == "GET":
        user_cart = Cart.objects.filter(user = request.user)
        item_to_display = CartSerializer(user_cart, many=True)
        return Response(item_to_display.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        item_to_update = CartSerializer(data=request.data, context={'request' : request})
        item_to_update.is_valid(raise_exception=True)
        item_to_update.save()
        return Response({"message" : "Item has been updated"}, status=status.HTTP_201_CREATED)
    elif request.method == "DELETE":
        user_cart = Cart.objects.filter(user=request.user)
        user_cart.delete()
        return Response({"message" : "The objects have been deleted"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_handler(request):
    if request.method == "GET":
        if request.user.groups.filter(name="Manager").exists():
            order = Order.objects.all()
            order_to_display = OrderSerializer(order, many=True)
            return Response(order_to_display.data, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name="Delivery crew").exists():
            order = Order.objects.filter(delivery_crew = request.user.id)
            print(request.user.id)
            order_to_display = OrderSerializer(order, many=True)
            return Response(order_to_display.data, status=status.HTTP_200_OK)
        else:
            user_order = Order.objects.filter(user=request.user)
            user_orders_to_display = OrderSerializer(user_order, many=True)
            return Response(user_orders_to_display.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        user_cart_items = Cart.objects.filter(user = request.user)
        total = sum(item.price for item in user_cart_items)
        user = request.user
        date = datetime.date.today()
        order = Order(user=user, date=date, total=total, status = False)
        order.save()
        for item in user_cart_items:
            order_item_menuItem =  item.menuitem
            order_item_quantity =  item.quantity
            order_item_unitprice =  item.unit_price
            order_item_price =  item.price
            order_item = OrderItem(order = request.user, menuitem=item.menuitem, quantity=order_item_quantity, unit_price=order_item_unitprice, price=order_item_price)
            order_item.save()
        user_cart_items.delete()
        return Response({"message" : "updated successfully"},status=status.HTTP_200_OK)


@api_view(['GET', 'DELETE', "PATCH", "PUT"])
@permission_classes([IsAuthenticated])
def single_order_handler(request, id_of_order):
    if request.method == "GET":
        if request.user.id == id_of_order:
            order_items = OrderItem.objects.filter(order=request.user.id)
            order_to_display =  OrderItemSerializer(order_items, many=True)
            return Response(order_to_display.data, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "You cannot see this section"}, status=status.HTTP_403_FORBIDDEN)
    elif request.method == "DELETE":
        if request.user.groups.filter(name="Manager").exists():
            order_to_delete = OrderItem.objects.get(id=id_of_order)
            order_to_delete.delete()
            return Response({"message" : "successfully deleted"}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "You are not authorized to do this"}, status=status.HTTP_403_FORBIDDEN)
    elif request.method == "PATCH":
        if request.user.groups.filter(name="Delivery crew").exists():
            status_to_update = request.data.get("status")
            order_to_update = Order.objects.get(id=id_of_order)
            if request.user == order_to_update.delivery_crew:
                if status_to_update == '0':
                    order_to_update.status = False
                elif status_to_update == '1':
                    order_to_update.status = True
                else:
                    order_to_update.status = False
                order_to_update.save()
                return Response({"message" : "Updated status successful"})
            else:
                return Response({"message" : "You are not authorized"})
        elif request.user.groups.filter(name="Manager").exists():
            dict = {}
            if request.data.get("status"):
                status_to_update = request.data.get("status")
                order_to_update = Order.objects.get(id=id_of_order)
                if status_to_update == '0':
                    order_to_update.status = False
                elif status_to_update == '1':
                    order_to_update.status = True
                else:
                    order_to_update.status = False
                order_to_update.save()
                dict.update({"message1" : "Updated status successful"})

            if request.data.get("delivery_crew"):
                delivery_guy = User.objects.get(id=request.data.get("delivery_crew"))
                if delivery_guy.groups.filter(name="Delivery crew").exists():
                    dict.update({"message2" : "the right guy"})
                else:
                    dict.update({"message3" : "Not the right guy"})
            return Response(dict, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "You are not authorized"})
    elif request.method == "PUT":
        item_to_update = OrderItem.objects.get(id = id_of_order)
        if request.user == item_to_update.order:
            updated_item = OrderItemSerializer(instance=item_to_update, data=request.data)
            updated_item.is_valid(raise_exception=True)
            updated_item.save()
            return Response({"message" : "Data updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "Not authorized for you"}, status=status.HTTP_404_NOT_FOUND)