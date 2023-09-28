from django.views.generic import ListView

from recruit.forms import SearchForm
from recruit.models import Recruit


# Create your views here.
class RecruitView(ListView):
    model = Recruit
    template_name = "recruits/index.html"
    context_object_name = "recruits"

    def get_queryset(self):
        queryset = Recruit.objects.all()
        query = self.request.GET.get("query")
        tag = self.request.GET.get("tag")

        if query:
            queryset = queryset.filter(title__icontains=query)

        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm()
        if self.request.user.is_authenticated:
            context["in_studies"] = Recruit.objects.filter(
                study__members=self.request.user
            )
            context["liked_studies"] = Recruit.objects.filter(
                like_users=self.request.user
            )
        else:
            context["in_studies"] = None
            context["liked_studies"] = None
        return context
