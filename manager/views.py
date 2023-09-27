from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from recruit.models import Recruit
from .models import Study, Task

class StudyView(LoginRequiredMixin,generic.ListView):
    model = Study
    template_name = 'studies/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_studies'] = Study.objects.filter(creator=self.request.user,is_active=True)
        context['in_studies'] = Study.objects.filter(members=self.request.user,is_active=True).exclude(creator=self.request.user)
        context['my_recruits'] = Recruit.objects.filter(creator=self.request.user)
        context['like_recruits'] = Recruit.objects.filter(like_users=self.request.user)
        return context
    
class StudyDetailView(LoginRequiredMixin, generic.DetailView):
    model = Study
    template_name = 'studies/detail.html'
    context_object_name = 'study'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.filter(study=self.object)
        return context
    
    