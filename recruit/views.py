from django.views.generic import ListView

from recruit.models import Recruit


# Create your views here.
class RecruitView(ListView):
    model = Recruit
    template_name = 'recruit/index.html'
    context_object_name = 'recruits'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['in_studies'] = Recruit.objects.filter(study__members=self.request.user)
            context['liked_studies'] = Recruit.objects.filter(like_users=self.request.user)
        else:
            context['in_studies'] = None
            context['liked_studies'] = None
        return context
