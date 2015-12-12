#!/usr/bin/env bash
hadoop fs -rm -r ./page_rank_spark/graph

hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapred.job.name='graph-builder'\
    -D mapred.reduce.tasks=10 \
    -file mapper.py reducer.py urls.txt utils.zip url_id_dict.zip\
    -mapper mapper.py \
    -reducer reducer.py \
    -input /data/sites/lenta.ru/all/doc*\
    -output ./page_rank_spark/graph
