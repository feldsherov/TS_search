Техническое замечание, я все делал виртуальным окружением anaconda https://www.continuum.io/downloads
В связи с этим у меня обычный python не хотел открывать shelve созданные этим виртуальным окружением, которые я использую в качестве словарей.

1.Для запуска на hadoop кластере использовать скрипт run.sh, или подобный ему. Важно, чтобы был архив utils.zip там набор моих утилит и еще с доисторических времен bs4. И еще лежат мои библиотечки для сжатия.

2. После того как завершена mapred задача, копируем весь вывод в одну локальную директорию, например mapred_out. (Я это делал локально: у меня уверенно не хватает места на сервере)

3. Строим индекс:

./index_builder.py <имя директории с выводом mapred задачи> <путь куда сохранить индекс> <путь до файла с урлами>

4. Сам поиск:

./search.py -i <путь к индексу, который указывали при постороении> -m mode [-o]
-m:  b - бинарный поиск
     ps - пассажный алгоритм
     bm25 - bm25

Скрипт ./search.py поддерживает параметр --help

Для индекса, который выложил все запускается так ./index_biulder.py -i index -m ps 

5. Оценка качества:

Вот здесь начинается драмма, которую я так и не одалел

./quality.py -i <путь к индексу> -p <путь к файлу с маркерами>

Теперь общие впечатления от результатов:

В итоговом результате, на полном индексе поднимается в среднем процентов 30 маркеров. Не пнимаю почему, очень долго с этим боролся, но после парсинга и выдирания текста не находится часть слов.

Общий поучительный эффект чувствуется, хотя, точно, можно лучше. Пассажи обгоняют bm, bm обгоняет рандом.

Результаты запуска скрипта:

Вывод на 100-м шаге.
-----------------------------
mismatch 67                  <- количество запросов для которых маркер не поднялся
bool_pos_mean 1214.264706    <- средняя позиция для булева поиска
bm_pos_mean 294.823529       <- средняя позиция для bm
ps_mismatch 11               <- в пассажный алгоритм уходят первые 100 из bm, так что дополнительно потерянный для пассажей
ps_pos_mean 41.000000        <- средняя позиция для пассажей
-----------------------------

Вывод на 221 шаге.
-----------------------------
mismatch 148
bool_pos_mean 966.851351
bm_pos_mean 224.270270
ps_mismatch 15
ps_pos_mean 40.983051
-----------------------------
