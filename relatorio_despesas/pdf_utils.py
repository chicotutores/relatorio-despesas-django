# -*- coding: utf-8 -*-

import os
import urllib2
from reportlab.lib.pagesizes import A4
from reportlab.lib import utils
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Image, Table

class PDFUtil:

    def __init__(self, mBuffer):
        self.buffer = mBuffer
        self.pageSize = A4
        self.width, self.height = self.pageSize

    def get_image(self, path, width=1 * cm):
        img = utils.ImageReader(path)
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        return Image(path, width=width, height=(width * aspect))

    def expensesPdf(self, expenses):

        doc = SimpleDocTemplate(self.buffer,
                                rightMargin=72,
                                leftMargin=72,
                                topMargin=30,
                                bottomMargin=72,
                                pagesize=self.pageSize)

        content = []

        tableData = []

        row = []

        index = 0

        for expense in expenses:

            filename = expense.image.path

            if not os.path.exists(filename):
                response = urllib2.urlopen(expense.image.url)
                f = open(filename, 'w')
                f.write(response.read())
                f.close()

            row.append(self.get_image(filename, 8*cm))

            index += 1

            if index == 2:

                tableData.append(row)

                row = []

                index = 0

        table = Table(tableData)

        content.append(table)

        doc.build(content)

        pdf = self.buffer.getvalue()

        self.buffer.close()

        return pdf