Набор скриптов для генерации сниппетов по заранее заданному набору документов.

*html_text_extractor.py <- просто мой класс для извлечения текста их HTML в приемлимом виде, никак пользоваться не придется
*splitter.py <- скрипт обучивающий модель, которая делит текст по предложениям
*index_builder.py <- скрипт для построения индекса
*snippet_builder.py <- скрипт для построения снипета

Каждый нетривиальный скрипт имеет подсказку при запуске с параметрами -h или --help

В кратце как пользоваться:

1. Запускаем splitter.py

./splitter.py -d sentences.xml -s SentenceSplitter.pkl -b

-b опция отключающая считывание с стандартного потока и просто обучает модель
-s путь к файлу куда записать обученную моделью 
-d путь к обучающему корпусу (парсится в формате opencorp-ы)

2. Запускаем index_builder.py

./index_builder.py -i ./index -s SentenceSplitter.pkl -u ./urls 
-i  путь куда записать индекс
-u папка с документами по которым хотим построить прямой индекс
-s путь к файлу с моделью, которая обучена, чтобы делить предложения

3. Запускаем snippet_builder.py

./snippet_builder.py -s 10 -f file_for_snippet.html -q аптека -i ./index

-s  минимальная длинна снипета в словах
-f имя файла в папке, которая была передана по -u в index_builder.py в нашем случае ./urls
-q запрос по которому мы хотим построить сниппет
-i путь к индексу указанный в index_builder.py по ключу -i

