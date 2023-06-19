import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import (
    IngredientInRecipe,
    Recipe,
    Tag,
    Ingredient,
    User,
    MIN_AMOUNT_INGREDIENTS
)


class Base64ImageField(serializers.ImageField):
    """
    Поле для сериализации картинки.
    """

    def to_internal_value(self, data):
        """
        Метод формирующий отображение картинок.
        """

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для объектов модели User.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """
        Метод формирующий поле is_subscribed.
        """

        user = self.context.get('request').user

        return (
            user.is_authenticated
            and user.follower.filter(author=obj).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для объектов модели Ingredient.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientsInRecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор объектов модели Ingredient для чтения сериализатора рецептов.
    """

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientsInRecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор объектов модели Ingredient для записи сериализатора рецептов.
    """

    id = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи объектов модели Recipe.
    """

    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientsInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'author',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)

    def validate_ingredients(self, value):
        ingredients = value

        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы 1 ингредиент'
            })

        ingredients_list = []

        for item in ingredients:
            id_obj = item['id']
            amount = item['amount']
            ingredient = Ingredient.objects.filter(id=id_obj).exists()
            if not ingredient:
                raise ValidationError(
                    {'ingredients': f'Ингредиента с id={id_obj} не существует'}
                )
            if amount < MIN_AMOUNT_INGREDIENTS:
                raise ValidationError(
                    {
                        'ingredients':
                        f'Ингредиентов не должно '
                        f'быть меньше {MIN_AMOUNT_INGREDIENTS}'
                    }
                )
            if id_obj in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингредианты не должны повторяться'
                })
            ingredients_list.append(id_obj)

        return value

    def validate_tags(self, value):
        tags = value
        tags_list = []

        if not tags:
            raise ValidationError({
                'tags': 'Нужен хотя бы 1 тэг'
            })

        for item in tags:
            tag = Tag.objects.filter(id=item.id)
            if not tag:
                raise ValidationError(
                    {'tags': f'Тега с id={item} не существует'}
                )
            if item in tags_list:
                raise ValidationError({
                    'ingredients': 'Ингредианты не должны повторяться'
                })
            tags_list.append(item)

        return value

    @staticmethod
    def create_ingredients_through_list(ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        self.create_ingredients_through_list(
            recipe=recipe,
            ingredients=ingredients
        )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()

        self.create_ingredients_through_list(
            recipe=instance,
            ingredients=ingredients
        )
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Метод, отвечающий за формат отображение объекта Ingredient.
        """
        request = self.context.get('request')
        return RecipeReadSerializer(
            instance,
            context={'request': request}
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения объектов модели Recipe.
    """

    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientsInRecipeReadSerializer(
        many=True,
        source='ingredientinrecipe'
    )
    author = CustomUserSerializer(read_only=True)

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def _get_is(self, obj, user_related_name):
        """
        Метод формирующий поле is_favorited или is_in_shopping_cart.
        """

        user = self.context.get('request').user

        return (
            user.is_authenticated
            and user_related_name.filter(recipe=obj).exists()
        )

    def get_is_favorited(self, obj):
        """
        Метод формирующий поле is_favorited.
        """

        user = self.context.get('request').user
        return not user.is_authenticated or self._get_is(obj, user.favorites)

    def get_is_in_shopping_cart(self, obj):
        """
        Метод формирующий поле is_in_shopping_cart.
        """

        user = self.context.get('request').user
        return (
            not user.is_authenticated
            or self._get_is(obj, user.shopping_list)
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сокращенная версия сериализатор объектов модели Recipe.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSirializer(serializers.ModelSerializer):
    """
    Сериализатор для предоставления данных по автору.
    """

    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes',
        )

    def get_is_subscribed(self, obj):
        """
        Метод формирующий поле is_subscribed.
        """

        user = self.context.get('request').user

        return (
            user.is_authenticated
            and user.follower.filter(author=obj).exists()
        )

    def get_recipes_count(self, obj):
        """
        Метод формирующий поле recipes_count.
        """

        return obj.recipes.count()

    def get_recipes(self, obj):
        """
        Метод формирующий поле recipes.
        """

        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()

        if limit:
            limit = int(limit)
            recipes = recipes[:limit]

        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)

        return serializer.data
