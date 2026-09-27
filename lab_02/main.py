from itertools import groupby
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
order_file = os.path.join(current_dir, 'orders.txt')

orders = []
mistakes = []
nums = []
statuses = ['новый','в обработке','выполнен','отменён']
with open(order_file, encoding='utf-8') as f: 

    for i,line in enumerate(f.readlines()): 
        line.strip()
        if not line: continue

        line_elements = line.split(";")

        if not line_elements[0].isdigit() or not (line_elements[0].lstrip('-').isdigit()):
            mistakes.append(f'Строка {i+1}: номер заказа должен быть положительным целым числом.')
            continue

        if int(line_elements[0])!=float(line_elements[0]) or int(line_elements[0])<=0:
            mistakes.append(f'Строка {i+1}: номер заказа должен быть положительным целым числом.')
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
        if line_elements[5] not in statuses:
            mistakes.append(f'Строка {i+1}: статус должен входить в перечень допустимых.')
            continue
        
        orders.append({
            "number": int(line_elements[0]),
            "customer" :line_elements[1],
            "category": line_elements[2],
            "quantity": int(line_elements[3]),
            "price": float(line_elements[4]),
            "status": line_elements[5],
            "worth" :int(line_elements[3])* float(line_elements[4])
        })
        nums.append(line_elements[0])


def mistake_list(mistakes):
  report_lines = []
  for mistake in mistakes:
    report_lines.append(mistake + "\n")
  return "".join(report_lines)


def show_all_orders(orders):
  for order in orders:
      items = [f'{key}:{value}' for key,value in list(order.items())[:6]]
      print(", ".join(items))
  print()
  return None


def sort_orders_worth(orders, for_report = 0):
  report_lines = []

  for order in sorted(orders, key = lambda order: order["worth"], reverse = True):
    items = [f'{key}:{value}' for key,value in list(order.items())[:7]]
    if not for_report: print(", ".join(items))

    report_lines.append(", ".join(items) + "\n")
  print()
  return "".join(report_lines)


def sort_orders_category(orders):
  for order in sorted(orders, key = lambda order: (order["category"], -order["worth"])):
    items = [f'{key}:{value}' for key,value in list(order.items())[:6]]
    print(", ".join(items))
  print()
  return None


def find_status(orders):
  print('Введите статус:')
  status = str(input())

  for order in orders:
    if order["status"].lower() == status.lower(): 
      items = [f'{key}:{value}' for key,value in list(order.items())[:6]]
      print(", ".join(items))
  print()
  return None


def find_category(orders):
  print('Введите категорию:')
  category = str(input())

  for order in orders:
    if order["category"].lower() == category.lower(): 
      items = [f'{key}:{value}' for key,value in list(order.items())[:6]]
      print(", ".join(items))
  print()
  return None


def find_customer(orders):
  print('Введите имя:')
  customer = str(input())

  for order in orders:
    if order["customer"].lower() == customer.lower(): 
      items = [f'{key}:{value}' for key,value in list(order.items())[:6]]
      print(", ".join(items))
  print()
  return None


def find_worth(orders, for_report = 0):
  report_lines = []

  for order in orders:
    if order["worth"] >= 5000: 
      items = [f'{key}:{value}' for key,value in list(order.items())[:6]]
      if not for_report: print(", ".join(items))

      report_lines.append(", ".join(items) + "\n")
  print()
  return "".join(report_lines)


def category_stat(orders, for_report = 0):
  report_lines = []
  report_category = []

  if not for_report: print('Статистика по категориям.')
  for category_name, group in groupby(sorted(orders, key=lambda x: x["category"]), key=lambda x: x["category"]):

    order_category = list(group)
    count_orders = len(order_category)
    amount_order = sum(order["quantity"] for order in order_category)
    allover_worth = sum(order["worth"] for order in order_category)
    finished_worth = sum(order["worth"] for order in order_category if order['status'] =='выполнен')

    if for_report==0: print(f'{category_name}: кол-во {count_orders}, кол-во единиц товара {amount_order}, общая стоимость {allover_worth}, стоимость выполненных {finished_worth}, средняя стоимость одного заказа {(allover_worth/count_orders):.2f}')
    report_category.append(category_name + '\n')
    report_lines.append(f'{category_name}: кол-во {count_orders}, кол-во единиц товара {amount_order}, общая стоимость {allover_worth}, стоимость выполненных {finished_worth}, средняя стоимость одного заказа {(allover_worth/count_orders):.2f}' + '\n')
  print()
  if for_report == 1: return "".join(report_lines)
  if for_report == 2: return "".join(report_category)

def status_stat(orders, for_report = 0):
  report_lines =[]

  if not for_report: print('Статистика по статусу.')
  status_count = dict.fromkeys(statuses,0) #statuses = ['новый','в обработке','выполнен','отменён']
  for order in orders:
    status_count[order['status']] +=1

  for key,value in status_count.items():
    if not for_report: print(f'{key}: кол-во заказов - {value}')
    report_lines.append(f'{key}: кол-во заказов - {value}' + '\n')
  print()
  return "".join(report_lines)


def overall_stat(orders,for_report = 0):
  report_lines = []

  if not for_report: print(f'Кол-во заказов: {len(orders)}') 
  report_lines.append(f'Кол-во заказов: {len(orders)}' + '\n') 
  if not for_report:print(f'Кол-во выполненых заказов: {len([order for order in orders if order['status']=='выполнен'])}')
  report_lines.append(f'Кол-во выполненых заказов: {len([order for order in orders if order['status']=='выполнен'])}' + '\n')
  if not for_report:print(f'Кол-во отменённых заказов: {len([order for order in orders if order['status']=='отменён'])}')
  report_lines.append(f'Кол-во отменённых заказов: {len([order for order in orders if order['status']=='отменён'])}' + '\n')
  if not for_report:print(f'Общая стоимость всех заказов: {sum([order['worth'] for order in orders])}')
  report_lines.append(f'Общая стоимость всех заказов: {sum([order['worth'] for order in orders])}' + '\n')
  if not for_report:print(f'Выручка по выполненным заказам: {sum([order['worth'] for order in orders if order['status']=='выполнен'])}')
  report_lines.append(f'Выручка по выполненным заказам: {sum([order['worth'] for order in orders if order['status']=='выполнен'])}' + '\n')
  if not for_report:print(f'Средняя стоимость заказа: { (sum([order['worth'] for order in orders])/ len(orders)):.2f}')
  report_lines.append(f'Средняя стоимость заказа: { (sum([order['worth'] for order in orders])/ len(orders)):.2f}' + '\n')
  if not for_report:print(f'Самый дорогой заказ: {max([order['worth'] for order in orders])}')
  report_lines.append(f'Самый дорогой заказ: {max([order['worth'] for order in orders])}'+ '\n')
  
  customer_count ={}
  for customer_name,group in groupby(sorted(orders, key = lambda x: x['customer']), key= lambda x: x['customer']):
    customer_count[customer_name] = sum([order['worth'] for order in group if order['status']=='выполнен'])
  if not for_report:print(f'Покупатель с наибольшей суммой выполненных заказов: {(best := max(customer_count, key = customer_count.get))}, сумма: {customer_count[best]}')
  report_lines.append(f'Покупатель с наибольшей суммой выполненных заказов: {(best := max(customer_count, key = customer_count.get))}, сумма: {customer_count[best]}' + '\n')
  if not for_report:print()
  return "".join(report_lines)

def statistic(orders):
  category_stat(orders)
  status_stat(orders)
  overall_stat(orders)


def save_report(orders):
  current_dir = os.path.dirname(os.path.abspath(__file__))
  file_path = os.path.join(current_dir, 'orders_report.txt')

  with open(file_path,'w', encoding = 'utf-8') as file:
    file.write("ОТЧЕТ ПО ЗАКАЗАМ.\n\n")
    file.write("1. Количество корректных записей.\n")
    file.write(f"{len(orders)}\n\n")
    file.write("2. Количество некорректных записей.\n")
    file.write(f"{len(mistakes)}\n\n")
    file.write("3. Перечень уникальных категорий.\n")
    file.write(f"{category_stat(orders, for_report = 2)}\n\n")
    file.write("4. Заказы по убыванию стоимости.\n")
    file.write(f"{sort_orders_worth(orders, for_report = 1)}\n\n")
    file.write("5. Перечень крупных заказов.\n")
    file.write(f"{find_worth(orders,for_report= 1)}\n\n")
    file.write("6 Общие показатели.\n")
    file.write(f"{overall_stat(orders,for_report = 1)}\n\n")
    file.write("7. Статистика по категориям.\n")
    file.write(f"{category_stat(orders, for_report = 1)}\n\n")
    file.write("8. Статистика по статусам.\n")
    file.write(f"{status_stat(orders, for_report = 1)}\n\n")
    file.write("9. Список ошибок входных данных.\n")
    file.write(f"{mistake_list(mistakes)}\n\n")


if __name__ == "__main__":
  while True:
    print("1. Показать все заказы")
    print("2. Показать заказы по убыванию стоимости")
    print("3. Показать заказы по категориям")
    print("4. Найти заказы по статусу")
    print("5. Найти заказы по категории")
    print("6. Найти заказы покупателя")
    print("7. Показать крупные заказы")
    print("8. Показать статистику")
    print("9. Сохранить отчёт")
    print("0. Завершить программу")

    user_input = int(input("Выберите пункт меню: "))
    print()

    if user_input == 0: 
      print("Программа завершена.")
      break

    elif user_input == 1: show_all_orders(orders)
    elif user_input == 2: sort_orders_worth(orders)
    elif user_input == 3: sort_orders_category(orders)
    elif user_input == 4: find_status(orders)
    elif user_input == 5: find_category(orders)
    elif user_input == 6: find_customer(orders)
    elif user_input == 7: find_worth(orders)
    elif user_input == 8: statistic(orders)
    elif user_input == 9: save_report(orders)

    else:print("неверно введен пункт. Попробуйте снова.")