# -*- coding: utf- 8 -*-
import os
import sys
from random import randrange

from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings

from searcher import Searcher
from direct_index import DirectIndex


@require_http_methods(['GET'])
def index(request):
    return render(request, 'templates/index.html', content_type="text/html")


def get_search_results(query):
    index = DirectIndex(settings.DIRECT_INDEX_PATH)
    index_files_path = settings.INVERSE_INDEX_DIR
    searcher = Searcher(os.path.join(index_files_path, "index.txt"),
                            os.path.join(index_files_path, "dict.txt"),
                            os.path.join(index_files_path, "urls.txt"))
    query_result_ids = searcher.search(query.encode("utf-8"), return_urls_only=True)
    query_result = list()

    for url_id in query_result_ids:
        record = index.record_by_id(randrange(300))
        query_result.append({"url": url_id[1],
                             "snippet": record.summary,
                             "image": record.img_url,
                             "title": record.title})
    return query_result


@require_http_methods(['GET'])
def search(request):
    query = request.GET.get("query", "")
    return render(request, 'templates/search.html', locals(), content_type="text/html")

@require_http_methods(['GET'])
def searchJSON(request):
    query = request.GET.get("query", "")
    query_result_dict = dict()
    if query != "":
        query_result_dict["result"] = get_search_results(query)
        query_result_dict["len"] = len(query_result_dict["result"])
        if not query_result_dict["result"]:
            query_result_dict = {"error": "No results"}
    else:
        query_result_dict = {"error": "Empty query"}

    return JsonResponse(query_result_dict)

@require_http_methods(['GET'])
def hello(request):
    return HttpResponse('Hello %s!' % request.GET.get('name', 'anonymous'))
