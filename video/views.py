from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from recruit.models import Study


@login_required
def index(request, study_id):
    user = request.user
    study = get_object_or_404(Study, id=study_id, members=user)
    context = {
        "study": study,
    }
    return render(request, "video/index.html", context)
