import os
import copy
from data_structures import LinkedList, Stack, Queue, HashTable

REQUESTS_FILE = 'input.txt'
REPORT_FILE = 'requests_report.txt'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRIORITIES = LinkedList()
PRIORITIES.append('обычная')
PRIORITIES.append('срочная')

TYPES = LinkedList()
TYPES.append('ремонт')
TYPES.append('консультация')
TYPES.append('установка')

def list_contains(linked_list, item):
    curr = linked_list.head
    while curr is not None:
        if curr.value == item:
            return True
        curr = curr.next
    return False

def recursive_walk(node):
    if node is None:
        return []
    return [node.value] + recursive_walk(node.next)

def recursive_search(node, req_id):
    if node is None:
        return None
    if isinstance(node.value, HashTable) and node.value.get('номер') == req_id:
        return node.value
    return recursive_search(node.next, req_id)

def find_request(regular_q, urgent_q, history_list, req_id):
    reg_res = recursive_search(regular_q.head, req_id)
    if reg_res is not None:
        return f'Заявка в обычной очереди: {reg_res}.'
        
    urg_res = recursive_search(urgent_q.head, req_id)
    if urg_res is not None:
        return f'Заявка в срочной очереди: {urg_res}.'
        
    hist_res = recursive_search(history_list.head, req_id)
    if hist_res is not None:
        return f'Заявка выполнена: {hist_res}.'
        
    return 'Заявки нет в системе.'

def load_and_parse_requests():
    regular_q = Queue()
    urgent_q = Queue()
    errors = LinkedList()
    valid_count = 0
    existing_ids = LinkedList()

    file_path = os.path.join(BASE_DIR,REQUESTS_FILE)
    if not os.path.exists(file_path):
        errors.append(f"Файл {REQUESTS_FILE} не найден")
        return regular_q, urgent_q, errors, 0
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue 
            fields = [field.strip() for field in line.split(';')]
            if len(fields) != 5:
                errors.append(f"Строка {idx}: неверное количество полей.")
                continue
                
            num_str, client, r_type, category, priority = fields
            try:
                n = int(num_str)
                if n <= 0:
                    raise ValueError
            except ValueError:
                errors.append(f'Строка {idx}: номер заявки не положительное целое число.')
                continue
                
            req_id = int(num_str)
            if list_contains(existing_ids, req_id):
                errors.append(f"Строка {idx}: повторяющийся номер заявки {req_id}.")
                continue
            if not client or not category:
                errors.append(f"Строка {idx}: пустое обязательное поле.")
                continue
            if not list_contains(TYPES, r_type):
                errors.append(f"Строка {idx}: неизвестный тип заявки: '{r_type}'.")
                continue
            if not list_contains(PRIORITIES, priority):
                errors.append(f"Строка {idx}: неизвестный приоритет: '{priority}'.")
                continue
 
            request = HashTable()
            request.put('номер', req_id)
            request.put('клиент', client)
            request.put('тип', r_type)
            request.put('категория', category)
            request.put('приоритет', priority)
            request.put('порядковый_номер', valid_count + 1)
            
            existing_ids.append(req_id)
            valid_count += 1
            
            if priority == 'срочная':
                urgent_q.enqueue(request)
            else:
                regular_q.enqueue(request)
                
    return regular_q, urgent_q, errors, valid_count

def process_request(regular_q, urgent_q, history_list, hash_table, stack_undo, state_container):
    if not urgent_q.is_empty():
        req = urgent_q.dequeue()
    elif not regular_q.is_empty():
        req = regular_q.dequeue()
    else:
        return None
        
    state_container.put('counter',state_container.get('counter') +1)
    req.put('номер_обслуживания', state_container.get('counter'))
    
    history_list.append(req)
    hash_table.put(req.get('номер'), req)
    stack_undo.push(req.get('номер'))
    return req

def cancel_request(regular_q, urgent_q, req_id):
    if urgent_q.remove_by_id(req_id):
        return True
    if regular_q.remove_by_id(req_id):
        return True
    return False

def undo_last_processed(stack_undo, hash_table):
    if stack_undo.is_empty():
        return None
    req_id = stack_undo.pop()
    hash_table.remove(req_id)  
    return req_id

class CategoryStats:
    def __init__(self):
        self.count = 0
        self.urgent_count = 0
        self.max_wait = 0
        self.wait_times_sum = 0 
        
    def __repr__(self):
        avg_wait = self.wait_times_sum / self.count if self.count > 0 else 0.0
        return f"Count: {self.count}, Urgent: {self.urgent_count}, Avg Wait: {avg_wait:.2f}, Max Wait: {self.max_wait}"

def calculate_statistics(history_list):
    stats = HashTable()
    stats.put('ремонт', CategoryStats())
    stats.put('консультация', CategoryStats())
    stats.put('установка', CategoryStats())
    
    curr = history_list.head
    while curr is not None:

        req = curr.value  
        t = req.get('тип')
        cat_stats = stats.get(t)

        if cat_stats is not None:
            cat_stats.count += 1

            if req.get('приоритет') == 'срочная':
                cat_stats.urgent_count += 1     

            wait_time = req.get('номер_обслуживания') - req.get('порядковый_номер')
            if wait_time < 0:
                wait_time = 0       

            cat_stats.wait_times_sum += wait_time
            if wait_time > cat_stats.max_wait:
                cat_stats.max_wait = wait_time  

        curr = curr.next
    return stats

def get_unique_categories():
    categories = LinkedList()

    file_path = os.path.join(BASE_DIR,REQUESTS_FILE)
    if not os.path.exists(file_path):
        return categories
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            fields = line.split(';')

            if len(fields) == 5:
                cat = fields[3].strip()
                if cat and not list_contains(categories, cat):
                    categories.append(cat)

    return categories

def save_report(valid_count, errors, history_list):
    unique_cats = get_unique_categories()
    stats = calculate_statistics(history_list)

    output_file_path = os.path.join(BASE_DIR,REPORT_FILE)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write("ИТОГОВЫЙ ОТЧЕТ СЕРВИСНОГО ЦЕНТРА \n\n")
        f.write(f"1. Количество корректных записей: {valid_count}\n")
        
        err_count = 0
        err_curr = errors.head
        while err_curr:
            err_count += 1
            err_curr = err_curr.next
        f.write(f"2. Количество некорректных записей: {err_count}\n\n")
        
        f.write("3. Перечень уникальных категорий:\n")
        cat_curr = unique_cats.head
        while cat_curr:
            f.write(f" - {cat_curr.value}\n")
            cat_curr = cat_curr.next
        f.write("\n")

        f.write("4. Статистика по типам заявок:\n")
        type_curr = TYPES.head
        while type_curr:
            t = type_curr.value
            s = stats.get(t)
            avg_wait = s.wait_times_sum / s.count if s.count > 0 else 0.0
            f.write(f" Тип: {t}\n")
            f.write(f"   - Всего обслужено: {s.count}\n")
            f.write(f"   - Срочных заявок: {s.urgent_count}\n")
            f.write(f"   - Среднее время ожидания: {avg_wait:.2f}\n")
            f.write(f"   - Максимальное время ожидания: {s.max_wait}\n")
            type_curr = type_curr.next
        f.write("\n")

        f.write("5. Список всех обслуженных заявок:\n")
        req_curr = history_list.head
        while req_curr:
            req = req_curr.value
            f.write(f" ID: {req.get('номер')} | Клиент: {req.get('клиент')} | Тип: {req.get('тип')} | Приоритет: {req.get('приоритет')}\n")
            req_curr = req_curr.next
        f.write("\n")

        f.write("6. Список ошибок входных данных:\n")
        err_curr = errors.head
        while err_curr:
            f.write(f" - {err_curr.value}\n")
            err_curr = err_curr.next


def run_automated_tests():

    q1 = Queue()
    req_test = HashTable()
    req_test.put('номер', 999)
    q1.enqueue(req_test)
    assert q1.dequeue().get('номер') == 999, "Тест 1 провален"
    assert q1.is_empty() is True, "Тест 1.1 провален"


    reg_q = Queue()
    urg_q = Queue()
    hist_ll = LinkedList()
    st_undo = Stack()
    container = HashTable()
    container.put('counter', 0)
    
    req_reg = HashTable()
    req_reg.put('номер', 1001)
    req_reg.put('приоритет', 'обычная')
    reg_q.enqueue(req_reg)
    
    req_urg = HashTable()
    req_urg.put('номер', 7777)
    req_urg.put('приоритет', 'срочная')
    urg_q.enqueue(req_urg)
    
    served = process_request(reg_q, urg_q, hist_ll, HashTable(), st_undo, container)
    assert served.get('номер') == 7777, "Тест 2 провален (порядок приоритетов)"


    q_empty = Queue()
    try:
        q_empty.dequeue()
        assert False, "Тест 3 провален: пустая очередь не выбросила IndexError"
    except IndexError:
        pass  


    q_mid = Queue()
    r1 = HashTable(); r1.put('номер', 10); q_mid.enqueue(r1)
    r2 = HashTable(); r2.put('номер', 20); q_mid.enqueue(r2)
    r3 = HashTable(); r3.put('номер', 30); q_mid.enqueue(r3)
    
    assert q_mid.remove_by_id(20) is True, "Тест 4 провален (удаление не вернуло True)"
    assert q_mid.dequeue().get('номер') == 10, "Тест 4.1 провален"
    assert q_mid.dequeue().get('номер') == 30, "Тест 4.2 провален"

   
    q_none = Queue()
    r_none = HashTable(); r_none.put('номер', 55); q_none.enqueue(r_none)
    assert q_none.remove_by_id(999) is False, "Тест 5 провален"

    
    s_empty = Stack()
    try:
        s_empty.pop()
        assert False, "Тест 6 провален: пустой стек не выбросил IndexError"
    except IndexError:
        pass  


    ll_rev = LinkedList()
    ll_rev.append(100)
    ll_rev.append(200)
    ll_rev.reverse()
    assert ll_rev.head.value == 200, "Тест 7 провален"
    assert ll_rev.tail.value == 100, "Тест 7.1 провален"


    ll_walk = LinkedList()
    ll_walk.append(5)
    ll_walk.append(15)
    walked_list = recursive_walk(ll_walk.head)
    assert walked_list.__getitem__(0) == 5, "Тест 8 провален: первый элемент неверный"
    assert walked_list.__getitem__(1) == 15, "Тест 8 провален: второй элемент неверный"

    
    empty_hist = LinkedList()
    stat_res = calculate_statistics(empty_hist)
    assert stat_res.get('ремонт').count == 0, "Тест 9 провален"
    assert stat_res.get('установка').count == 0, "Тест 9.1 провален"



def main():

    run_automated_tests()

    regular_q, urgent_q, errors, valid_count = load_and_parse_requests()
    hash_table = HashTable()
    stack_undo = Stack()
    history_list = LinkedList()
    
    state_container = HashTable()
    state_container.put('counter', 0)

    menu = """1. Показать заявки в очередях
2. Обслужить заявку
3. Отменить заявку по номеру
4. Отменить последнюю принятую заявку
5. Показать историю обслуживания
6. Развернуть историю
7. Показать статистику
8. Найти заявку по номеру
9. Сохранить отчёт
0. Завершить программу"""

    n = 0
    while True:
        if n!=2: print("\n" + menu)
        try:
            n = int(input("Выберите пункт меню: "))
        except ValueError:
            print('Неверный формат ввода. Введите число от 0 до 9.')
            continue

        if n == 0:
            print("Работа программы завершена.")
            break
            
        elif n == 1: 
            print('Срочные заявки:')
            print(recursive_walk(urgent_q.head))
            print('Обычные заявки:')
            print(recursive_walk(regular_q.head))
            
        elif n == 2:
            req = process_request(regular_q, urgent_q, history_list, hash_table, stack_undo, state_container)
            if req:
                print(f"Заявка {req.get('номер')} успешно обслужена.")
            else:
                print("Очереди пусты, нет заявок для обслуживания.")
                
        elif n == 3:
            try:
                req_id = int(input("Введите номер заявки для отмены: "))
                if cancel_request(regular_q, urgent_q, req_id):
                    print(f"Заявка {req_id} успешно отменена.")
                else:
                    print(f"Заявка {req_id} не найдена в очередях.")
            except ValueError:
                print("Ошибка: Номер должен быть числом.")
                
        elif n == 4:
            undone_id = undo_last_processed(stack_undo, hash_table)
            if undone_id:
                print(f"Обслуживание заявки {undone_id} успешно отменено.")
            else:
                print("Стек отмены пуст.")
                
        elif n == 5:
            print("История обслуживания:")
            print(recursive_walk(history_list.head))
            
        elif n == 6:
            history_list.reverse()
            print("История обслуживания развернута.")
            print(recursive_walk(history_list.head))
            
        elif n == 7:
            stats = calculate_statistics(history_list)
            types_to_show = TYPES
            print("Статистика по типам заявок:")
            curr = types_to_show.head
            while curr:
                t = curr.value
                s = stats.get(t)
                if s:
                    avg_wait = s.wait_times_sum / s.count if s.count > 0 else 0.0
                    print(f" - {t}: Всего={s.count}, Срочных={s.urgent_count}, Ср.ожидание={avg_wait:.2f}, Макс.ожидание={s.max_wait}")
                curr = curr.next
                    
        elif n == 8:
            try:
                req_id = int(input("Введите номер заявки для поиска: "))
                print(find_request(regular_q, urgent_q, history_list, req_id))
            except ValueError:
                print("Ошибка: Номер должен быть числом.")
                
        elif n == 9:
            save_report(valid_count, errors, history_list)
            print(f"Отчет успешно сохранен в файл: {REPORT_FILE}")
            
        else: 
            print('Неверный пункт меню.')


if __name__ == '__main__':
    main()
