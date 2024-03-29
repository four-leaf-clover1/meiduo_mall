from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    """自定义文件存储类"""

    def _open(self,name,mode='rb'):
        """
        当要打开某个文件时会来调用此方法
        :param name: 要打开的文件名
        :param mode: 打开文件的模式
        """
        pass

    def _save(self,name,content):
        """
        当要上传图片就会调用此方法
        :param name: 要上传的文件名
        :param content: 要上传的图片二进制数据
        :return: file_id
        """
        pass

    def url(self,name):
        """
        当要下载图片时，image.url时就会来调用此方法
        :param name: 要下载的图片file_id
        :return: 要下载图片的绝对路径
        """

        return 'http://192.168.15.93:8888/' + name