from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Count
from . models import Product,Collection,Review,Cart,CartItem,Customer,Order,OrderItem,ProductImage
from . serializers import ProductSerializer,CollectionSerializer,ReviewSerializer,CartSerializer,CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer,CustomerSerializer,OrderSerializer,CreateOrderSerializer,UpdateOrderSerializer,ProductImageSerializer

from rest_framework.mixins import ListModelMixin,CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin

from rest_framework.viewsets import ModelViewSet,GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from . filters import ProductFilter
from . pagination import DefaultPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.mixins import CreateModelMixin
from . filters import ProductFilter
from rest_framework.decorators import action
from . permissions import IsAdminOrReadOnly,FullDjanoModelPermissions,ViewCustomerHistoryPermission
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser,DjangoModelPermissions

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all() 
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    pagination_class = DefaultPagination
    filterset_class = ProductFilter
    ordering_fields = ['unit_price', 'last_update']
    permission_classes = [IsAdminOrReadOnly]
   
    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request,*args,**kwargs):
        if OrderItem.objects.filter(product_id = kwargs['pk'].count() > 0):
            return Response({'error': 'Product cannot be deleted because it is associated with a order item'},status = status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args,**kwargs)


    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    def delete(self, request,pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0: 
            return Response({'error': 'Collection cannot be deleted because it is associated with a Product'},status = status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk '])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']
    
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer    
        
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
   
    def get_queryset(self):
        return CartItem.objects \
        .filter(cart_id = self.kwargs['cart_pk']) \
        .select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
     
    @action(detail=True,permission_classes = [ViewCustomerHistoryPermission] )
    def history(self, request, pk):
        return Response('ok')
 

    @action(detail=False,methods = ['GET','PUT'],permission_classes=[IsAuthenticated])
    def me(self,request):
        customer =Customer.objects.get(user_id = request.user.id)
        if request.method == 'GET': 
           serializer = CustomerSerializer(customer)
           return Response(serializer.data)

        elif request.method =='PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception =True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete','head','options']
    
    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data,context =  {'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer


    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id = self.user)
        return Order.objects.filter(customer_id = customer_id)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])


    
# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     def delete(self, request,pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0: 
#             return Response({'error': 'Product cannot be deleted because it is associated with a order item'},status = status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status = status.HTTP_204_NO_CONTENT)

     


# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.select_related('collection').all()
#     serializer_class = ProductSerializer
    

#     def get_serializer_context(self):
#         return {'request': self.request}

   
    # def get(self, request):
    #     product = Product.objects.select_related('collection').all()
    #     serializer = ProductSerializer(product,many=True, context = {'request':request})
    #     data =  serializer.data
    #     return Response(data)

    # def post(self, request):
    #     serializer = ProductSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     data =  serializer.data
    #     return Response(data, status = status.HTTP_201_CREATED)

    # def delete(self, request,pk):
    #     product = get_object_or_404(Product, pk=pk)
    #     if product.orderitems.count() > 0: 
    #         return Response({'error': 'Product cannot be deleted because it is associated with a order item'},status = status.HTTP_405_METHOD_NOT_ALLOWED)
    #     product.delete()
    #     return Response(status = status.HTTP_204_NO_CONTENT)


     
    # def get(self, request,id):
    #     product = get_object_or_404(Product, pk=id)
    #     serializer = ProductSerializer(product)
    #     data = serializer.data
    #     return Response(data)

    # def put(self, request,id):
    #     product = get_object_or_404(Product, pk=id)
    #     serializer = ProductSerializer(product,data = request.data)
    #     serializer.is_valid(raise_exception =True)
    #     serializer.save()
    #     return Response(serializer.data, status = status.HTTP_201_CREATED)

    

# @api_view(['GET', "POST"])
# def product_list(request):
#     if request.method == 'GET':
#        product = Product.objects.select_related('collection').all()
#        serializer = ProductSerializer(product,many=True, context = {'request':request})
#        data =  serializer.data
#        return Response(data)
#     elif request.method == "POST":
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
        
#         return Response(serializer.data, status = status.HTTP_201_CREATED)
        
# @api_view(['GET','PUT','DELETE'])
# def product_detail(request,id):
#     product = get_object_or_404(Product, pk=id)
#     if request.method == 'GET':
#         serializer = ProductSerializer(product)
#         data = serializer.data
#         return Response(data)
    
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product,data = request.data)
#         serializer.is_valid(raise_exception =True)
#         serializer.save()
#         return Response(serializer.data, status = status.HTTP_201_CREATED)

#     elif request.method == 'DELETE':
#         if product.orderitems.count() > 0: 
#             return Response({'error': 'Product cannot be deleted because it is associated with a order item'},status = status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status = status.HTTP_204_NO_CONTENT)


# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializer


# @api_view(['GET', "POST"])
# def collection_list(request):
#     if request.method == 'GET':
#        collection = Collection.objects.annotate(products_count=Count('products')).all()
#        serializer = CollectionSerializer(collection,many=True)
#        data =  serializer.data
#        return Response(data)
#     elif request.method == "POST":
#         serializer = Collection(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status= status.HTTP_201_CREATED)


# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count = Count('products'))
#     serializer_class = CollectionSerializer
#     def delete(self, request,pk):
#         collection = get_object_or_404(Collection, pk=pk)
#         if collection.products.count() > 0: 
#             return Response({'error': 'Collection cannot be deleted because it is associated with a Product'},status = status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status = status.HTTP_204_NO_CONTENT)



# @api_view(['GET','PUT','DELETE'])
# def collection_detail(request, pk):
#     collection = get_object_or_404(
#         Collection.objects.annotate(products_count = Count('products'))
#               , pk=pk)
#     if request.method == 'GET':
#         serializer = CollectionSerializer(collection)
#         data = serializer.data
#         return Response(data)
    
#     elif request.method == 'PUT':
#         serializer = CollectionSerializer(collection,data = request.data)
#         serializer.is_valid(raise_exception =True)
#         serializer.save()
#         return Response(serializer.data, status = status.HTTP_201_CREATED) 

#     elif request.method == 'DELETE':
#         if collection.products.count() > 0: 
#             return Response({'error': 'Collection cannot be deleted because it is associated with a Product'},status = status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status = status.HTTP_204_NO_CONTENT)


