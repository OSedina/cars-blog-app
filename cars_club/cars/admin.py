from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import Cars, Category


@admin.register(Cars)
class CarsAdmin(admin.ModelAdmin):
    list_display = ('title', 'post_photo', 'time_create', 'is_published', 'cat')
    list_display_links = ('title', )
    ordering = ['time_create', 'title']
    list_editable = ('is_published', )
    list_per_page = 10
    actions = ['set_published', 'set_draft' ]
    search_fields = ['title__startswith', 'cat__name']

    fields = ['title', 'slug','photo', 'post_photo', 'content', 'cat', 'tags']
    readonly_fields = ['post_photo']
    save_on_top = True

    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']

    @admin.display(description="Изображение")
    def post_photo(self, cars: Cars):
        if cars.photo:
            return mark_safe(f"<img src='{cars.photo.url}' width=50>")
        return "Без фото"

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Cars.Status.PUBLISHED)
        self.message_user(request, f"Изменено {count} записи(ей).")

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Cars.Status.DRAFT)
        self.message_user(request, f"{count} записи(ей) сняты с публикации!", messages.WARNING)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
