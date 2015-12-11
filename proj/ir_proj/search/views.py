# -*- coding: utf- 8 -*-
import os
import sys

from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpResponse

from searcher import Searcher


@require_http_methods(['GET'])
def index(request):
    return render(request, 'templates/index.html', content_type="text/html")

@require_http_methods(['GET'])
def search(request):
    index_files_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "index_files")
    query = request.GET.get("query", "")
    query_result = None
    if query != "":
        searcher = Searcher(os.path.join(index_files_path, "index.txt"),
                            os.path.join(index_files_path, "dict.txt"),
                            os.path.join(index_files_path, "urls.txt"))
        query_result = searcher.search(query.encode("utf-8"), return_urls_only=True)
        if not query_result:
            query_result = [u"Упс, кажется, ничего не нашлось."]

    else:
        query_result = [u"Ну как мы найдем что-то по пустому запросу?"]

    ln = len(query_result)
    return render(request, 'templates/content.tmpl', locals(), content_type="text/html")

@require_http_methods(['GET'])
def hello(request):
    return HttpResponse('Hello %s!' % request.GET.get('name', 'anonymous'))
