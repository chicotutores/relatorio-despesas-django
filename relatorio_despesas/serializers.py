# -*- coding: utf-8 -*-
from models import *

from rest_framework import serializers

class ExpenseSerializer(serializers.ModelSerializer):

    photo_url = serializers.SerializerMethodField()
    expense_type = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = ('id', 'date', 'expense_type', 'value', 'note', 'photo_url')

    def get_photo_url(self, expense):
        request = self.context.get('request')
        photo_url = expense.image.url
        return request.build_absolute_uri(photo_url)

    def get_expense_type(self, expense):
        request = self.context.get('request')
        return expense.get_type_display()