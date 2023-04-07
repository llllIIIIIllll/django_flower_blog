from django.contrib import admin

from .models import ArticlePost
from .models import ArticleColumn
# 3.23增
class ArticleAdmin(admin.ModelAdmin):

    '''设置列表可显示的字段'''
    list_display = ('title', 'author', 'created', 'status',)
    '''按发布日期排序'''
    ordering = ('-created',)

    actions = ['sub_pass', 'sub_notpass']

    def sub_pass(self, request, queryset):
        #user = request.user
        queryset.update(status = '1')

    def sub_notpass(self, request,queryset):
        #self.user = request.user
        queryset.update(status = '2')



# 注册ArticlePost到admin中
admin.site.register(ArticlePost, ArticleAdmin)
# 注册文章栏目
admin.site.register(ArticleColumn)