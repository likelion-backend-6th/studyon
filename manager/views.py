from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from recruit.models import Recruit
from .models import Study

class StudyView(LoginRequiredMixin,generic.ListView):
    model = Study
    template_name = 'studies/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_studies'] = Study.objects.filter(creator=self.request.user)
        context['in_studies'] = Study.objects.filter(members=self.request.user).exclude(creator=self.request.user)
        context['my_recruits'] = Recruit.objects.filter(creator=self.request.user)
        context['like_recruits'] = Recruit.objects.filter(like_users=self.request.user)
        return context
    