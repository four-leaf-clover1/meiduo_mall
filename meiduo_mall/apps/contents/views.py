from django.shortcuts import render
from django.views import View


from .utils import get_categories
from .models import Content,ContentCategory

class IndexView(View):

    def get(self, request):

        #定义用来包装所有广告数据的大字典
        contents = {}
        #查询所有广告类别数据
        contents_cat_qs = ContentCategory.objects.all()
        for content_cat in contents_cat_qs:
            contents[content_cat.key] = content_cat.content_set.filter(status=True).order_by('sequence')

        #准备模型渲染数据
        context = {
            'categories': get_categories(),
            'contents' : contents

        }
        return render(request, 'index.html',context)