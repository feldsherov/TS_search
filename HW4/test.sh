#/bin/bash

cat ./1_1000/docs-000.txt | python mapper.py | sort | python reducer.py 
