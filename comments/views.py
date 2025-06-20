from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from .forms import CommentForm
from .functions import resize_image_if_needed
from .models import Comment, CommentFile



class CommentListView(FormMixin, ListView):
    model = Comment
    template_name = 'comments/index.html'
    context_object_name = 'comments'
    paginate_by = 25
    form_class = CommentForm
    success_url = reverse_lazy('comments:index')

    def get_queryset(self):
        return Comment.objects.filter(parent__isnull=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form()

        uploaded_files = request.FILES.getlist('files')
        file_errors = []

        # Валидация файлов вручную
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'txt']
        for file in uploaded_files:
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                file_errors.append(f"{file.name}: запрещённый формат.")
            elif ext == 'txt' and file.size > 100 * 1024:
                file_errors.append(f"{file.name}: TXT-файл > 100КБ.")

        if form.is_valid() and not file_errors:
            # Создание комментария
            comment = Comment.objects.create(
                user_name=form.cleaned_data['user_name'],
                email=form.cleaned_data['email'],
                home_page=form.cleaned_data.get('home_page'),
                text=form.cleaned_data['text'],
                parent_id=form.cleaned_data.get('parent_id'),
            )

            # Сохранение файлов
            for file in uploaded_files:
                new_file = resize_image_if_needed(file)
                CommentFile.objects.create(comment=comment, file=new_file)

            return redirect(self.get_success_url())

        # Добавление ошибок вручную, если были проблемы с файлами
        if file_errors:
            for msg in file_errors:
                form.add_error(None, msg)

        return self.render_to_response(self.get_context_data(form=form))