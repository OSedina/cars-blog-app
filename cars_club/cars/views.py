from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView

from cars.forms import AddPostForm, UploadFileForm
from cars.models import Cars, Category, TagPost, UploadFiles

import uuid

from cars.utils import DataMixin

menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Добавить статью", 'url_name': 'add_page'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        {'title': "Войти", 'url_name': 'login'}
        ]

class CarsHome(DataMixin, ListView):
    def get_queryset(self):
        return Cars.published.all().select_related('cat')

    template_name = 'cars/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        return self.get_mixin_context(super().get_context_data(**kwargs),
                                      title='Главная страница',
                                      cat_selected=0,
                                      )

def handle_uploaded_file(f):
    with open(f"uploads/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@login_required
def about(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fp = UploadFiles(file=form.cleaned_data['file'])
            fp.save()
    else:
        form = UploadFileForm()

    contact_list = Cars.published.all()
    paginator = Paginator(contact_list, 4)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'cars/about.html', {'page_obj': page_obj, 'title': 'О сайте'})


class ShowPost(DataMixin, DetailView):
    model = Cars
    template_name = 'cars/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['post'])

    def get_object(self, queryset=None):
        return get_object_or_404(Cars.published, slug=self.kwargs[self.slug_url_kwarg])

class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    model = Cars
    fields = '__all__'
    template_name = 'cars/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Добавление статьи'
    extra_context = {
        'menu': menu,
        'title': 'Добавление статьи',
    }

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)

class UpdatePage(UpdateView):
    model = Cars
    fields = ['title', 'content', 'photo', 'is_published', 'cat']
    template_name = 'cars/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактирование статьи'
    extra_context = {
        'menu': menu,
        'title': 'Редактирование статьи',
    }


def contact(request):
    contact_list = Cars.published.all()
    paginator = Paginator(contact_list, 4)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'cars/contact.html', {'page_obj': page_obj, 'title': 'Обратная связь'})


def login(request):
    return HttpResponse("Авторизация")


class CarsCategory(DataMixin, ListView):
    template_name = 'cars/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        return self.get_mixin_context(context, title='Категория - ' + cat.name, cat_selected=cat.id, )

    def get_queryset(self):
        return Cars.published.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')

class TagPostList(DataMixin, ListView):
    template_name = 'cars/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: ' + tag.tag)

    def get_queryset(self):
        return Cars.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat')


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


