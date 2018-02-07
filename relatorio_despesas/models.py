# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
from django.contrib.auth.models import User
from django.db import models

EXPENSE_TYPE = (('EST', 'Pedágio e Estacionamento'), ('FGB', 'Frigobar'), ('KM', 'Kilometragem'),
                ('LAV', 'Lavanderia'), ('BKF', 'Café da manhã'), ('REF', 'Refeição'),
                ('TRP', 'Transporte'), ('TLF', 'Telefone'))

def get_upload_path(instance, filename):
    extension = filename.split('.')[-1]
    new_file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.' + extension
    return os.path.join('notas', new_file_name)

def get_upload_archive_path(instance, filename):
    extension = filename.split('.')[-1]
    new_file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.' + extension
    return os.path.join('planilhas', new_file_name)

class Expense(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField(verbose_name='Data')
    type = models.CharField(verbose_name='Tipo', choices=EXPENSE_TYPE, max_length=50)
    value = models.FloatField(verbose_name='Valor')
    note = models.CharField(verbose_name='Observações', max_length=200, blank=True)
    image = models.ImageField(verbose_name='Foto', upload_to=get_upload_path)

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'

    def __str__(self):
        return self.type.encode('utf8', errors='replace')

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(verbose_name='Saldo', default=0.0)
    project = models.CharField(max_length=50, verbose_name='Projeto', blank=True)
    client = models.CharField(max_length=100, verbose_name='Cliente', blank=True)
    bank = models.CharField(max_length=100, verbose_name='Banco', blank=True)
    agency = models.CharField(max_length=10, verbose_name='Agência', blank=True)
    account = models.CharField(max_length=20, verbose_name='Conta corrente', blank=True)
    document = models.CharField(max_length=20, verbose_name='CPF', blank=True)
    expensesFile = models.FileField(null=True, blank=True, upload_to=get_upload_archive_path)

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'

    def __str__(self):
        return self.user.first_name.encode('utf8', errors='replace') + self.user.last_name.encode('utf8', errors='replace')