# -*- coding: utf-8 -*-
from base64 import b64decode
from io import BytesIO

import unidecode
from django.core.files.base import ContentFile
from django.http import HttpResponse

from relatorio_despesas.pdf_utils import PDFUtil
from serializers import *
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
import xlsxwriter
import StringIO

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):

    try:

        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:

            return Response({'message': 'Usuário logado com sucesso'})

        else:

            return Response({'message': 'Usuário ou senha inválidos'}, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({'message': 'Usuário não encontrado, verifique suas informações o'},
                        status=status.HTTP_400_BAD_REQUEST)

    except Exception, e:
        return Response({'message': 'Não foi possível realizar o login, por favor tente novamente'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def signUp(request):

    try:
        username = request.data.get('username')
        password = request.data.get('password')
        firstName = request.data.get('firstName')
        lastName = request.data.get('lastName')
        project = request.data.get('project')
        client = request.data.get('client')
        bank = request.data.get('bank')
        agency = request.data.get('agency')
        account = request.data.get('account')
        document = request.data.get('document')

        userCount = User.objects.filter(username=username).count()

        if userCount > 0:
            return Response({'message': 'Usuário já existente, poe favor escolha outro'},
                        status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        user.first_name = firstName
        user.last_name = lastName
        user.save()

        employee = Employee(project=project,
                            client=client,
                            bank=bank,
                            agency=agency,
                            account=account,
                            document=document,
                            user=user)
        employee.save()

        return Response({'message': 'Usuário criado com sucesso'})

    except Exception, e:
        return Response({'message': 'Não foi possível fazer seu cadastro, por favor tente novamente'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def saveExpense(request):

    try:

        username = request.data.get('username')
        image = request.data.get('image')
        date = request.data.get('date')
        expenseType = request.data.get('type')
        value = request.data.get('value')
        note = request.data.get('note')

        user = User.objects.get(username=username)
        imageData = b64decode(image)
        imageData = ContentFile(imageData, username + '.jpeg')
        floatValue = float(value)
        datefield = datetime.datetime.strptime(date, '%Y-%m-%d')
        expense = Expense(user=user,
                          date=datefield,
                          type=expenseType,
                          value=floatValue,
                          note=note,
                          image=imageData)
        expense.save()
        return Response({'message': 'Despesa salva com sucesso!'})

    except Exception, e:
        return Response({'message': 'Não foi possível cadastrar sua despesa, por favor tente novamente'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def getExpensesPdfReport(request):

    try:

        username = request.query_params.get('username')
        expenses = Expense.objects.filter(user__username=username).order_by('-date')

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatórioRespostas.pdf"'
        buffer = BytesIO()
        pdfUtil = PDFUtil(buffer)
        pdf = pdfUtil.expensesPdf(expenses)

        response.write(pdf)

        return response

    except Exception, e:
        return Response({'message': 'Não foi possível consultar suas despesa, por favor tente novamente'},
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def getExpenses(request):

    try:

        username = request.query_params.get('username')
        expenses = []

        for expense in Expense.objects.filter(user__username=username).order_by('-date'):
            expenseSerializer = ExpenseSerializer(expense, context={'request': request})
            expenses.append(expenseSerializer.data)

        return Response({'message': expenses})

    except Exception:
        return Response({'message': 'Não foi possível consultar suas despesa, por favor tente novamente'},
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def deleteAllExpenses(request):

    try:

        username = request.data.get('username')

        Expense.objects.filter(user__username=username).delete()

        return Response({'message': 'Despesas excluídas com sucesso'})

    except Exception:
        return Response({'message': 'Não foi possível deletar suas despesas, por favor tente novamente'},
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def deleteExpense(request):

    try:

        id = request.data.get('id')

        Expense.objects.get(id=id).delete()

    except Exception:
        return Response({'message': 'Não foi possível deletar sua despesa, por favor tente novamente'},
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def renameExpenses(request):

    expenses = Expense.objects.filter(user__username='douglasnunes').order_by('date')

    initialDateString = request.query_params.get('initialDate')

    finalDateString = request.query_params.get('finalDate')

    initialDate = datetime.datetime.strptime(initialDateString, '%Y-%m-%d')

    finalDate = datetime.datetime.strptime(finalDateString, '%Y-%m-%d')

    finalPath = "douglasnunes-" + str(initialDate.month) + "-" + str(initialDate.year)

    expenseCount = 1

    for expense in expenses:

        if initialDate.date() <= expense.date <= finalDate.date():

            oldPath = expense.image.path

            expense.image.name = "notas/" + finalPath + "/" + str(expenseCount) + ".jpg"

            newPath = expense.image.path.replace("/" + str(expenseCount) + ".jpg", "")

            if not os.path.exists(newPath):

                os.mkdir(newPath)

            os.rename(oldPath, expense.image.path)

            expense.save()

            expenseCount += 1

    return Response({"message": "Despesas renomeadas com sucesso"})


@api_view(['GET'])
@permission_classes([AllowAny])
def exportExpensesExcel(request):

    try:

        username = request.query_params.get('username')

        balance = request.query_params.get('balance')

        initialDateString = request.query_params.get('initialDate')

        finalDateString = request.query_params.get('finalDate')

        initialDate = datetime.datetime.strptime(initialDateString, '%Y-%m-%d')

        finalDate = datetime.datetime.strptime(finalDateString, '%Y-%m-%d')

        balance = float(balance)

        employee = Employee.objects.get(user__username='douglasnunes')

        expenses = Expense.objects.filter(user__username='douglasnunes').order_by('date')

        output = StringIO.StringIO()

        workbook = xlsxwriter.Workbook(output)
        title = workbook.add_format()
        title.set_font_size(30)
        title.set_bold()
        bold = workbook.add_format()
        bold.set_bold()
        bold.set_font_size(20)
        bold.set_border(1)
        worksheet = workbook.add_worksheet()
        worksheet.insert_image(2, 1, 'ifLogo.png', {'x_scale': 1.3, 'y_scale': 1.0})
        worksheet.write(2, 6, 'Relatorio de Despesas', title)
        worksheet.hide_gridlines(2)

        worksheet.merge_range('B6:D6', 'Projeto', bold)
        worksheet.merge_range('B7:D7', 'Cliente:', bold)
        worksheet.merge_range('B8:D8', 'Consultor:', bold)
        worksheet.merge_range('B9:D9', 'Periodo:', bold)
        worksheet.merge_range('B10:D10', 'Banco:', bold)
        worksheet.merge_range('B11:D11', 'Agencia:', bold)
        worksheet.merge_range('B12:D12', 'Conta corrente:', bold)
        worksheet.merge_range('B13:D13', 'CPF:', bold)

        red_font = workbook.add_format()
        red_font.set_font_size(20)
        red_font.set_font_color('red')
        red_font.set_border(1)

        worksheet.merge_range('E6:K6', employee.project, red_font)
        worksheet.merge_range('E7:K7', employee.client, red_font)
        worksheet.merge_range('E8:K8', employee.user.first_name + ' ' + employee.user.last_name, red_font)
        worksheet.merge_range('E9:K9', initialDateString + ' a ' + finalDateString, red_font)
        worksheet.merge_range('E10:K10', employee.bank, red_font)
        worksheet.merge_range('E11:K11', employee.agency, red_font)
        worksheet.merge_range('E12:K12', employee.account, red_font)
        worksheet.merge_range('E13:K13', employee.document, red_font)

        money_format = workbook.add_format()
        money_format.set_num_format('R$ #,##0.00')
        money_format.set_border(1)
        money_format.set_font_size(20)

        worksheet.merge_range('B15:H15', 'Saldo Anterior =', bold)
        worksheet.merge_range('B16:H16', 'Valor Total de Adiantamento =', bold)
        worksheet.merge_range('B17:H17', 'Valor Total do Relatorio =', bold)
        worksheet.merge_range('B18:H18', 'Valor Total Geral de Reembolso =', bold)

        boldCenter = workbook.add_format()
        boldCenter.set_bold()
        boldCenter.set_font_size(20)
        boldCenter.set_border(1)
        boldCenter.set_align('center')
        boldCenter.set_valign('vcenter')

        worksheet.set_row(20, 20)

        worksheet.merge_range('B20:C23', 'Data', boldCenter)
        worksheet.merge_range('D20:G23', 'Tipo de Despesa', boldCenter)
        worksheet.merge_range('H20:I23', 'Valor', boldCenter)
        worksheet.merge_range('J20:R23', 'Justificativa', boldCenter)

        borderWrap = workbook.add_format()
        borderWrap.set_font_size(15)
        borderWrap.set_text_wrap()
        borderWrap.set_border(1)
        borderWrap.set_align('center')
        borderWrap.set_valign('vcenter')

        borderWrapMoney = workbook.add_format()
        borderWrapMoney.set_font_size(15)
        borderWrapMoney.set_text_wrap()
        borderWrapMoney.set_border(1)
        borderWrapMoney.set_num_format('R$ #,##0.00')
        borderWrapMoney.set_align('center')
        borderWrapMoney.set_valign('vcenter')

        borderWrapDate = workbook.add_format()
        borderWrapDate.set_font_size(15)
        borderWrapDate.set_text_wrap()
        borderWrapDate.set_border(1)
        borderWrapDate.set_num_format('dd/mm/yy')
        borderWrapDate.set_align('center')
        borderWrapDate.set_valign('vcenter')

        currentRow = 24
        expenseCount = 1
        expensesValue = 0.0

        moneyFormatBold = workbook.add_format()
        moneyFormatBold.set_num_format('R$ #,##0.00')
        moneyFormatBold.set_border(1)
        moneyFormatBold.set_font_size(20)
        moneyFormatBold.set_bold()
        moneyFormatBold.set_align('center')
        moneyFormatBold.set_valign('vcenter')

        for expense in expenses:
            if initialDate.date() <= expense.date <= finalDate.date():
                expensesValue += expense.value
                worksheet.merge_range('A' + str(currentRow) + ':A' + str(currentRow+1), expenseCount, borderWrap)
                dateRange = 'B'+str(currentRow)+':C'+str(currentRow+1)
                worksheet.merge_range(dateRange, expense.date, borderWrapDate)
                expenseTypeRange = 'D'+str(currentRow)+':G'+str(currentRow+1)
                worksheet.merge_range(expenseTypeRange, expense.get_type_display(), borderWrap)
                expenseValueRange = 'H' + str(currentRow) + ':I' + str(currentRow+1)
                worksheet.merge_range(expenseValueRange, expense.value, borderWrapMoney)
                expenseNoteRange = 'J' + str(currentRow) + ':R' + str(currentRow+1)
                worksheet.merge_range(expenseNoteRange, expense.note, borderWrap)
                currentRow += 2
                expenseCount += 1

        worksheet.merge_range('B'+str(currentRow)+':C'+str(currentRow+1), 'TOTAL', boldCenter)
        worksheet.merge_range('D'+str(currentRow)+':G'+str(currentRow+1), '', boldCenter)
        worksheet.merge_range('J' + str(currentRow) + ':R' + str(currentRow+1), '', boldCenter)
        worksheet.merge_range('H' + str(currentRow) + ':I' + str(currentRow+1), expensesValue, moneyFormatBold)

        worksheet.merge_range('I15:K15', balance, money_format)
        worksheet.merge_range('I16:K16', 2400, money_format)
        worksheet.merge_range('I17:K17', expensesValue, money_format)
        totalValue = (balance + 2400) - expensesValue
        worksheet.merge_range('I18:K18', totalValue, money_format)

        workbook.close()

        output.seek(0)
        
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=relatorio.xlsx'
        return response
    except Exception, e:
        return Response({'message': 'Não foi possível gerar seu relatório, por favor tente novamente'},
                        status=status.HTTP_400_BAD_REQUEST)
