from rest_framework.generics import ListAPIView,CreateAPIView

from users.models import User
from meiduo_admin.serializers.user_serializer import *
from meiduo_admin.pages import MyPage


class UserAPIView(ListAPIView,CreateAPIView):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserDetailSerializer

    pagination_class = MyPage

    def get_queryset(self):
        #获取前端传来的keyword
        keyword = self.request.query_params.get("keyword")
        if keyword:
            return self.queryset.filter(username__contains=keyword)
        return self.queryset.all()


