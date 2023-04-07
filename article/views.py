from django.shortcuts import render, redirect
import markdown
from markdown_del_ins import DelInsExtension
from markdown.extensions.footnotes import FootnoteExtension
from .models import ArticlePost
from django.http import HttpResponse
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
# 引入 Q 对象
from django.db.models import Q  #对多个参数进行查询
from comment.models import Comment
from .models import ArticleColumn
# 引入评论表单
from comment.forms import CommentForm


def article_list(request):
    search = request.GET.get('search')
    if search:
        article_list=ArticlePost.objects.filter(
            Q(title__icontains=search)|
            Q(body__icontains=search)
        )
    else:
        search=''
        article_list=ArticlePost.objects.all()

    article_list = article_list.filter(
        Q(author_id=request.user.id) |
        Q(status=1)
    )

    # 取出所有博客文章
    # article_list = ArticlePost.objects.all()
    paginator = Paginator(article_list,10)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    # 需要传递给模板（templates）的对象
    context = {'articles': articles,'search':search}
    # render函数：载入模板，并返回context对象

    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)

    md = markdown.Markdown(
        extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        DelInsExtension(),
        FootnoteExtension(),
        'markdown.extensions.toc',
        'mdx_math',
        ],

        extension_configs = {
            'mdx_math': {
                'enable_dollar_delimiter': True,  # 启用美元符号 $ 作为公式分隔符
            },
        }

    )

    article.body = md.convert(article.body)



    # comments.body = md.convert(comments.body)
    # 引入评论表单
    comment_form = CommentForm()
    # comment_form.body=md.convert(comment_form.body)
    # 需要传递给模板的对象
    context = { 'article': article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form,}
    # 载入模板，并返回context对象
    return render(request, 'article/detail.html', context)


# 写文章的视图

@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = { 'article_post_form': article_post_form, 'columns': columns }
        # 返回模板
        return render(request, 'article/create.html', context)


# 删文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        # 根据 id 获取需要删除的文章
        article = ArticlePost.objects.get(id=id)
        # 调用.delete()方法删除文章
        article.delete()
        # 完成删除后返回文章列表
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

# 更新文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = { 'article': article, 'article_post_form': article_post_form, 'columns': columns, }
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)


