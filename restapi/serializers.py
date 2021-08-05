from django.contrib.auth.models import  Group
from common.models import CmnUsers
from rest_framework import serializers
from common.models import (InvItemCategories, InvItemSubCategories,InvItemMasters, CmnBusinessSectors,
                           InvItemBatches, InvItemBatchLines)
from common import (sysutil,commonutil)

"""
First up we're going to define some serializers. Let's create a new module named 
tutorial/quickstart/serializers.py that we'll use for our data representations.
"""


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CmnUsers
        fields = ['url', 'user_name', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class REFCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvItemCategories
        fields = ['category_id', 'category_name']

    def create(self, validated_data):
        category = InvItemCategories.objects.filter(category_id=validated_data['category_id'])
        print('category create ',category)
        return category

    def update(self, validated_data):
        category = InvItemCategories.objects.filter(category_id=validated_data['category_id'])
        print('category update',category)
        return category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvItemCategories
        #fields = ['category_id', 'category_name']
        fields = '__all__'
        read_only_fields = ['category_id']
    def create(self, validated_data):
        print('in category create')
        category = InvItemCategories(**validated_data)
        return category

class SubCategorySerializer(serializers.ModelSerializer):
    print('in Sub cat serializer')
    #iic_category_id = REFCategorySerializer()
    category_name = serializers.CharField()
    class Meta:
        model = InvItemSubCategories
        fields = [f.name  for f in model._meta.get_fields()]+['category_name']
        read_only_fields = ['sub_category_id','category_name']
        #fields = fields + ['category_name']

        #fields = ['sub_category_id', 'sub_category_name','iic_category_id']

    def create(self, validated_data):
        print('in create')
        subcategory = InvItemSubCategories(**validated_data)
        if not commonutil.hasintvalue(subcategory.sub_category_id):
            subcategory.sub_category_id = sysutil.get_sequenceval('inv_item_sub_categories_s.nextval')
        subcategory.save()
        return subcategory

    def update(self, instance, validated_data):
        print(instance, validated_data)
        category_data = validated_data.pop('iic_category_id')
        iic_category_id, created = InvItemCategories.objects.get_or_create(category_name=category_data['category_name'])
        for fname, fvalue in validated_data.items():
            setattr(instance, fname, fvalue)
        instance.iic_category_id = iic_category_id
        instance.save()
        return instance

class BusinessSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmnBusinessSectors
        fields = '__all__'
    def create(self, validated_data):
        data = validated_data
        return CmnBusinessSectors.objects.create(**data)


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvItemMasters
        fields = '__all__'

class ItemBatchSerialized(serializers.ModelSerializer):
    class Meta:
        model = InvItemBatches
        fields = '__all__'

    def create(self, validated_data):
        data = validated_data
        return InvItemBatches.objects.create(**data)

    def update(self, instance, validated_data):
        for fname, fvalue in validated_data.items():
            setattr(instance, fname, fvalue)
        instance.save()
        return instance


class ItemBatchLinesSerialized(serializers.ModelSerializer):
    class Meta:
        model = InvItemBatchLines
        fields = '__all__'

    def create(self, validated_data):
        data = validated_data
        return InvItemBatchLines.objects.create(**data)

    def update(self, instance, validated_data):
        for fname, fvalue in validated_data.items():
            setattr(instance, fname, fvalue)
        instance.save()
        return instance

class ItemBatchLinesGetSerialized(ItemBatchSerialized):
    batch_id = ItemBatchSerialized
