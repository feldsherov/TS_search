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
from spell import Spell
from snippet_builder import SnippetBuilder


class QueryHandler:
    def __init__(self):
        self.sp = Spell(settings.SPELL_WORDS_NUM)
        self.index = DirectIndex(settings.DIRECT_INDEX_PATH)
        self.searcher = Searcher(os.path.join(settings.INVERSE_INDEX_DIR, "index.txt"),
                                 os.path.join(settings.INVERSE_INDEX_DIR, "dict.txt"),
                                 os.path.join(settings.INVERSE_INDEX_DIR, "urls.txt"))
        self.snippet_builder = SnippetBuilder()

    def get_search_results(self, query):
        index = self.index
        searcher = self.searcher
        query_result_ids = searcher.search(query.encode("utf-8"), return_urls_only=True)
        query_result = list()

        for url_id in query_result_ids[10]:
            record = index.record_by_id(randrange(300))
            try:
                snippet = self.snippet_builder.build_snippet(record, query.encode("utf-8"))
            except Exception as e:
                snippet = u" SnipetBuilder упал" + e.message

            query_result.append({"url": url_id[1],
                                 "snippet": snippet,
                                 "image": record.img_url,
                                 "title": record.title})
        return query_result

    def spell(self, query):
        return self.sp.spell(query)

qhandler = QueryHandler()

@require_http_methods(['GET'])
def index(request):
    return render(request, 'templates/index.html', content_type="text/html")

@require_http_methods(['GET'])
def search(request):
    query = request.GET.get("query", "")
    return render(request, 'templates/search.html', locals(), content_type="text/html")

@require_http_methods(['GET'])
def searchJSON(request):
    global qhandler
    query = request.GET.get("query", "")
    query_result_dict = dict()
    if query != "":
        query_result_dict["result"] = qhandler.get_search_results(query)
        query_result_dict["len"] = len(query_result_dict["result"])
        query_result_dict["spell"] = qhandler.spell(query)
        if not query_result_dict["result"]:
            query_result_dict = {"error": "No results"}
    else:
        query_result_dict = {"error": "Empty query"}

    return JsonResponse(query_result_dict)

@require_http_methods(['GET'])
def hello(request):
    return HttpResponse('Hello %s!' % request.GET.get('name', 'anonymous'))
