from django.contrib.auth.models import  Group
from common.models import CmnUsers
from rest_framework import serializers
from common.models import (InvItemCategories, InvItemSubCategories,InvItemMasters, CmnBusinessSectors,
                           InvItemBatches, InvItemBatchLines, InvItemSalesUnits, InvItemBarcodes,
                           CmnUnitOfMeasurements, CmnTaxCodes, ArCustomers,ArCustomerProfiles,
                           InvManufacturers, InvLocations,InvItemLocations)
from common import (sysutil,commonutil)
from common.submodels import (imp_models, ecomm_models)

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
    iic_category_id = REFCategorySerializer()
    class Meta:
        model = InvItemSubCategories
        fields = '__all__'
        # [f.name  for f in model._meta.get_fields()]+['category_name']
        read_only_fields = ['sub_category_id']
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
        order_by = ['item_id']


class SalesUnitsSerializer(serializers.ModelSerializer):
    #iim_item_id = ItemSerializer()
    class Meta:
        model = InvItemSalesUnits
        fields = '__all__'
        order_by = ['iim_item_id','su_id']


class BarcodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvItemBarcodes
        fields = '__all__'
        order_by = ['barcode']

class REFItemBatchLinesSerialized(serializers.ModelSerializer):
    class Meta:
        model = InvItemBatchLines
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


class REFItemBatchSerialized(serializers.ModelSerializer):
    class Meta:
        model = InvItemBatches
        fields = ['batch_id','item_batch_category']

    def create(self, validated_data):
        data = {}
        return InvItemBatches.objects.create(**data)

    def update(self, instance, validated_data):
       return instance

class ItemBatchLinesSerialized(serializers.ModelSerializer):
    batch_id = REFItemBatchSerialized()
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


class UOMSerialized(serializers.ModelSerializer):
    class Meta:
        model = CmnUnitOfMeasurements
        fields = '__all__'

    def create(self, validated_data):
        data = validated_data
        return CmnUnitOfMeasurements.objects.create(**data)

    def update(self, instance, validated_data):
        for fname, fvalue in validated_data.items():
            setattr(instance, fname, fvalue)
        instance.save()
        return instance



class TaxcCodesSerialized(serializers.ModelSerializer):
    class Meta:
        model = CmnTaxCodes
        fields = '__all__'

    def create(self, validated_data):
        data = validated_data
        return CmnTaxCodes.objects.create(**data)

    def update(self, instance, validated_data):
        for fname, fvalue in validated_data.items():
            setattr(instance, fname, fvalue)
        instance.save()
        return instance

class CustomersSerialized(serializers.ModelSerializer):
    class Meta:
        model = ArCustomers
        #fields = '__all__'
        exclude = ['host_image_path1', 'host_image_path2']

    def create(self, validated_data):
        data = validated_data
        return ArCustomers.objects.create(**data)

    def update(self, instance, validated_data):
        for fname, fvalue in validated_data.items():
            setattr(instance, fname, fvalue)
        instance.save()
        return instance

class ManfSerialized(serializers.ModelSerializer):
    class Meta:
        model = InvManufacturers
        fields = '__all__'
        #exclude = ['host_image_path1', 'host_image_path2']

    def create(self, validated_data):
        data = validated_data
        return InvManufacturers.objects.create(**data)

    def update(self, instance, validated_data):
        for fname, fvalue in validated_data.items():
            setattr(instance, fname, fvalue)
        #instance.save()
        return instance


class StoreSerialized(serializers.ModelSerializer):
    class Meta:
        model = InvLocations
        fields = '__all__'
        #exclude = ['host_image_path1', 'host_image_path2']

    def create(self, validated_data):
        data = validated_data
        data = {}
        return InvLocations.objects.create(**data)

    def update(self, instance, validated_data):
        for fname, fvalue in validated_data.items():
            setattr(instance, fname, fvalue)
        #instance.save()
        return instance


class LocationStockSerialized(serializers.ModelSerializer):
    class Meta:
        model = InvItemLocations
        fields = ['location_id','item_id','quantity','last_update_date','creation_date']

    def create(self, validated_data):
        data = {}
        return InvItemLocations.objects.none()

    def update(self, instance, validated_data):
        return instance

## ecommerce section


class EcommOrderStatInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ecomm_models.EcommOrderstatusinfo
        fields = '__all__'
    def create(self, validated_data):
        data = validated_data
        return ecomm_models.EcommOrderstatusinfo.objects.create(**data)

class EcommOrderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ecomm_models.EcommOrderinfo
        fields = '__all__'
    def create(self, validated_data):
        data = validated_data
        return ecomm_models.EcommOrderinfo.objects.create(**data)


class EcommOrderDetailInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ecomm_models.EcommOrderdetailsinfo
        fields = '__all__'
    def create(self, validated_data):
        data = validated_data
        return ecomm_models.EcommOrderdetailsinfo.objects.create(**data)


class EcommOrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ecomm_models.EcommOrderaddress
        fields = '__all__'
    def create(self, validated_data):
        data = validated_data
        return ecomm_models.EcommOrderaddress.objects.create(**data)


class EcommOrderPaymentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ecomm_models.EcommOrderpaymentinfo
        fields = '__all__'
    def create(self, validated_data):
        data = validated_data
        return ecomm_models.EcommOrderpaymentinfo.objects.create(**data)
