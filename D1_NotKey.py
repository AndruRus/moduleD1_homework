import sys 
import requests    

base_url = "https://api.trello.com/1/{}" 
auth_params = {    
    'key': "Вставьте key",    
    'token': "Вставьте token", 
}
board_id = "Вставьте расширенный Id доски"  

# как получить расширенный Id доски   
# Должен получиться через JSON:
# Перейдите на свою доску Trello
# Добавьте ".json" в конец URL
# Отформатируйте JSON так, чтобы он был удобочитаемым (вы можете найти программу просмотра JSON в Интернете)
# Найдите idBoard - здесь будет указан ваш полный идентификатор доски объявлений.
# URL должен выглядеть так:
# https://trello.com/b/BaDyGlxp/<название доски> .json

def read():      
    # Получим данные всех колонок на доске:      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
      
    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:      
    for column in column_data:      
        print(column['name'])    
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()  
        # Добавьте рядом с названием колонки цифру, отражающую количество задач в ней  
        print(column['name'] + " - ({})".format(len(task_data)))  

        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'] + '\t' + task['id'])


def create(name, column_name):
    # реализуем передачцу Id
    column_id = column_check(column_name)
    if column_id is None:
        column_id = create_column(column_name)['id']
    requests.post(base_url.format('cards'), data={'name': name, 'idList': column_id, **auth_params})


def move(name, column_name):
    # получим данные колонок и задач
    # обработка совпадений
    duplicate_tasks = get_task_duplicates(name)
    if len(duplicate_tasks) > 1:
        print("Задач с таким названием несколько штук:")
        for index, task in enumerate(duplicate_tasks):
            task_column_name = requests.get(base_url.format('lists') + '/' + task['idList'], params=auth_params).json()['name']
            print("Задача №{}\tid: {}\tНаходится в колонке: {}\t ".format(index, task['id'], task_column_name))
        task_id = input("Пожалуйста, введите ID задачи, которую нужно переместить: ")
    else:
        task_id = duplicate_tasks[0]['id']

    # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # найдём колонку по Id и используем
    column_id = column_check(column_name)
    if column_id is None:
        column_id = create_column(column_name)['id']
    # перемещаем
    requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column_id, **auth_params})


def column_check(column_name):
    # проверка существования колонки
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    for column in column_data:
        if column['name'] == column_name:
            return column['id']
    return


def create_column(column_name):
    # создаём колонки
    return requests.post(base_url.format('lists'), data={'name': column_name, 'idBoard': board_id, **auth_params}).json()


def get_task_duplicates(task_name):
    # колонки на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    duplicate_tasks = []
    # колоноки с повторяющимися именами
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == task_name:
                duplicate_tasks.append(task)
    return duplicate_tasks


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':
        create_column(sys.argv[2])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])