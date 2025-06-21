from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from .forms import CommentForm
from .functions import resize_image_if_needed
from .models import Comment, CommentFile


class LoadCommentFormView(View):
    def get(self, request, *args, **kwargs):
        form = CommentForm()
        html = render_to_string('comments/includes/form.html', {'form': form}, request=request)
        return JsonResponse({'form_html': html})



class CommentListView(FormMixin, ListView):
    model = Comment
    template_name = 'comments/index.html'
    context_object_name = 'comments'
    paginate_by = 25
    form_class = CommentForm
    success_url = reverse_lazy('comments:index')

    def get_queryset(self):
        queryset = Comment.objects.filter(parent__isnull=True)
        sort = self.request.GET.get('sort')
        order = self.request.GET.get('order', 'desc')

        if sort in ['user_name', 'email', 'created_at']:
            sort_field = sort if order == 'asc' else f'-{sort}'
            queryset = queryset.order_by(sort_field)
        else:
            queryset = queryset.order_by('-created_at')  # LIFO по умолчанию

        return queryset

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

        allowed_extensions = settings.ALLOWED_EXTENSIONS
        for file in uploaded_files:
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                file_errors.append(f"{file.name}: запрещённый формат.")
            elif ext == 'txt' and file.size > 100 * 1024:
                file_errors.append(f"{file.name}: TXT-файл > 100КБ.")

        if form.is_valid() and not file_errors:
            comment = Comment.objects.create(
                user_name=form.cleaned_data['user_name'],
                email=form.cleaned_data['email'],
                home_page=form.cleaned_data.get('home_page'),
                text=form.cleaned_data['text'],
                parent_id=form.cleaned_data.get('parent_id'),
            )

            for file in uploaded_files:
                new_file = resize_image_if_needed(file)
                CommentFile.objects.create(comment=comment, file=new_file)

            # AJAX-ответ (inline и основная форма)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                comment_html = render_to_string(
                    'comments/includes/comment_block.html',
                    {'comment': comment},
                    request=request
                )
                return JsonResponse({'comment_html': comment_html, 'message': 'Комментарий успешно добавлен!'}, status=200)


            return redirect(self.get_success_url())

        # Добавление ошибок, если файлы некорректны
        if file_errors:
            for msg in file_errors:
                form.add_error(None, msg)


        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('comments/includes/form.html', {'form': form}, request=request)
            return JsonResponse({'form_html': html}, status=400)

        # обычный ререндер с ошибками
        return self.render_to_response(self.get_context_data(form=form))
