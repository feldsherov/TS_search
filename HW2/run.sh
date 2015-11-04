hadoop fs -rm -r ./povarenok

hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -file mapper.py reducer.py third_party.zip\
    -mapper mapper.py \
    -reducer reducer.py \
    -input /data/sites/povarenok.ru/1_1000/docs* \
    -output ./povarenok/
