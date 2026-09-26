order_file = r"C:\Users\user\theoretical_foundations_of_informatics\lab_02\orders.txt"

orders = []
mistakes = []
nums = []
status = ['новый','в обработке','выполнен','отменён']
with open(order_file, encoding='utf-8') as f: 

    for i,line in enumerate(f.readlines()): 
        line.strip()
        if not line: continue

        line_elements = line.split(";")

        if not line_elements[0].isdigit() or not (line_elements[0].lstrip('-').isdigit()):
            mistakes.append(f'Строка {i+1}: номер заказа должен быть положительным целфм числом.')
            continue

        if int(line_elements[0])!=float(line_elements[0]) or int(line_elements[0])<=0:
            mistakes.append(f'Строка {i+1}: номер заказа должен быть положительным целфм числом.')
            continue

        if len(line_elements)!=6:
            mistakes.append(f'Строка {i+1}: строка должна содержать ровно шесть полей.')
            continue

        if line_elements[0] in nums:
            mistakes.append(f'Строка {i+1}: номера заказов не должны повторяться.')
            continue

        if line_elements[1] =='':
            mistakes.append(f'Строка {i+1}: имя покупателя должно быть непустой строкой.')
            continue

        if line_elements[2] =='':
            mistakes.append(f'Строка {i+1}: категория товара не должна быть пустой строкой.')
            continue

        if not line_elements[3].isdigit():
            mistakes.append(f'Строка {i+1}: количество должно быть положительным целым числом.')
            continue
        
        if int(line_elements[3])!=float(line_elements[3]) or int(line_elements[3])<=0:
            mistakes.append(f'Строка {i+1}: количество должно быть положительным целым числом.')
            continue

        if float(line_elements[4])<=0:
            mistakes.append(f'Строка {i+1}: цена должна быть положительной.')
            continue

        line_elements[5] = line_elements[5].replace("\n", "")
        if line_elements[5] not in status:
            mistakes.append(f'Строка {i+1}: статус должен входить в перечень допустимых.')
            continue
        
        orders.append({
            "number": int(line_elements[0]),
            "customer" :line_elements[1],
            "category": line_elements[2],
            "quantity": int(line_elements[3]),
            "price": float(line_elements[4]),
            "status": line_elements[5]
        })
        nums.append(line_elements[0])
print(orders)