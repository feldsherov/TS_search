1.Для запуска на hadoop кластере использовать скрипт run.sh, или подобный ему. Важно, чтобы был архив third_party, потому что на кластере так и не bs4. И еще лежат мои библиотечки для сжатия.

2. После того как завершена mapred задача, копируем весь вывод в одну локальную директорию, например mapred_out.

3. Строим индекс:

./index_creator.py <имя директории с выводом mapred задачи> <путь куда сохранить индекс> <путь до файла с урлами>

4. Сам поиск:

./search.py <путь к индексу, который указывали при постороении>

Этот скрипт ждет на ввод запрос в формате описанном в уловии ДЗ, но у меня операции обозначаются, как & и |.

 Пример запроса: рыба & (сладкая | кислая)
