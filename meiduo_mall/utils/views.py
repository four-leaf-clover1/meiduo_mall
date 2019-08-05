from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginRequiredView(LoginRequiredMixin,View):
    """判断用户登入类"""

    pass
