

def get_breadcrumb(cat3):
    """根据三级类型来构造面包屑导航数据"""
    cat1 = cat3.parent.parent
    cat1.url = cat1.goodschannel_set.all()[0].url

    breadcrumb = {
        'cat1' : cat1,
        'cat2' : cat3.parent,
        'cat3' : cat3

    }

    return breadcrumb