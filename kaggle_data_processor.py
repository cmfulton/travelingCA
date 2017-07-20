#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
import unicodedata
import csv

# there was a hidden unicode error in kaggle dataset. this got rid of it.
# reading in files with encoding='utf-8'. stackoverflow hint
class KaggleDataProcessor:

    def read(self, products_filename, orders_filename):
        products = {}
        first_row = True
        with open(products_filename, encoding='utf-8') as f:
            r = csv.reader(f)
            for row in r:
                product_id = row[0]
                product_name = row[1]
                if not first_row:
                    products[product_id] = product_name
                first_row = False

        # [ [2, 33120],
        #   [2, 28985],
        #   ...         ]

        # order_id = 2
        # [ ['chicken', 'apple']

        first_row = True
        original_orders = []
        with open(orders_filename, encoding='utf-8') as f:
            r = csv.reader(f)
            order_id = None
            row_index = -1
            previous_order_id = None
            for row in r:
                if first_row:
                    first_row = False
                    continue
                order_id = row[0]
                if previous_order_id != order_id:
                    original_orders.append([])
                    row_index += 1
                product_name = products[row[1]]
                original_orders[row_index].append(product_name)
                previous_order_id = order_id

        return original_orders

    def write(self, data, filename):
        # [[2,2,2,2],
        #  [2,2,2,2],
        # ]
        #
        #
        # [ [2, 33120],
        #   [2, 28985],
        #   ...         ]
        with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for line in data:
                writer.writerow(line)


if __name__ == '__main__':
    data_processor = KaggleDataProcessor()
    data = data_processor.read('products.csv', 'original_orders.csv')
    data_processor.write(data, 'result.csv')
