from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, Tag
from recipes.models import RecipeIngredient, ShoppingCart
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from users.models import Subscribe, User

from .filters import RecipeFilter
from .mixins import ListRetrieveViewSet
from .pagination import CustomPaginator
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    SetPasswordSerializer,
    SubscribeAuthorSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserReadSerializer,
)


class UserViewSet(mixins.CreateModelMixin, ListRetrieveViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreateSerializer

    @action(
        detail=False, methods=['get'], pagination_class=None,
        permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['post'],
        permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Пароль успешно изменен!'},
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'],
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPaginator)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, id=pk)

        if request.method == 'POST':
            serializer = SubscribeAuthorSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            _, created = Subscribe.objects.get_or_create(
                user=request.user, author=author
            )
            if created:
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                "Subscribe already exists", status=status.HTTP_200_OK)

        get_object_or_404(Subscribe, user=request.user, author=author).delete()
        return Response(
            {'detail': 'Успешная отписка'},
            status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def toggle_favorite_or_cart(
            self,
            request,
            recipe,
            serializer_class,
            related_field
    ):
        if request.method == 'POST':
            if not related_field.filter(
                    user=request.user, recipe=recipe).exists():
                related_field.create(
                    user=request.user, recipe=recipe)
                serializer = serializer_class(
                    recipe, context={'request': request})
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            return Response(
                {'errors': 'Рецепт уже в избранном.'},
                status=status.HTTP_400_BAD_REQUEST)

        related_field.filter(user=request.user, recipe=recipe).delete()
        return Response(
            {'detail': 'Успешное удаление'},
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        return self.toggle_favorite_or_cart(
            request, recipe, RecipeSerializer, Favorite.objects)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.toggle_favorite_or_cart(
            request, recipe, RecipeSerializer, ShoppingCart.objects)

def create_shoping_list(user: "MyUser") -> str:
    """Сфомировать список ингридкетов для покупки.

    Args:
        user (MyUser):
            Пользователь, для которго будет создаваться список.

    Returns:
        str:
            Список продуктов с указанием необходимого количества.
    """
    shopping_list = [
        f"Список покупок для:\n\n{user.first_name}\n"
        f"{dt.now().strftime(DATE_TIME_FORMAT)}\n"
    ]
    Ingredient = apps.get_model("recipes", "Ingredient")
    ingredients = (
        Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
        .values("name", measurement=F("measurement_unit"))
        .annotate(amount=Sum("recipe__amount"))
    )
    ing_list = (
        f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
        for ing in ingredients
    )
    shopping_list.extend(ing_list)

    shopping_list.append("\nПосчитано в Foodgram")
    return "\n".join(shopping_list)

@action(
    detail=False,
    methods=['get'],
)
def download_shopping_cart(self, request):
    user = self.request.user
    if not user.carts.exists():
        return Response(status=HTTP_400_BAD_REQUEST)

    filename = f"{user.username}_shopping_list.txt"
    shopping_list = create_shoping_list(user)
    response = HttpResponse(
        shopping_list, content_type="text.txt; charset=utf-8"
    )
    response["Content-Disposition"] = f"attachment; filename={filename}"
    return response

    # ingredients = (
    #     RecipeIngredient.objects
    #     .filter(recipe__shopping_recipe__user=request.user)
    #     .values('ingredient')
    #     .annotate(total_amount=Sum('amount'))
    #     .values_list(
    #         'ingredient__name',
    #         'total_amount',
    #         'ingredient__measurement_unit',
    #     )
    # )
    #
    # wishlist = []
    # for item in ingredients:
    #     wishlist.append(
    #         f'{item[0]} - {item[2]} {item[1]}'
    #     )
    #
    # wishlist = '\n'.join(wishlist)
    # response = HttpResponse(wishlist, 'Content-Type: text/plain')
    # response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
    # return response
