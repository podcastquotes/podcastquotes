import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from core.forms import VoteForm
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile


@login_required
def vote(request, quote_id, vote_type_id):
    q = get_object_or_404(Quote, pk=quote_id)
    v = get_object_or_404(User, pk=request.user.id)
    t = int(vote_type_id)
    vote, created = Vote.objects.get_or_create(voter=v, quote=q)
    if vote.vote_type == 1 and t == 1:
        vote.vote_type = 0
    elif vote.vote_type == 1 and t == -1:
        vote.vote_type = -1
    elif vote.vote_type == -1 and t == -1:
        vote.vote_type = 0
    elif vote.vote_type == -1 and t == 1:
        vote.vote_type = 1
    else:
        vote.vote_type = t
    vote.save()
    return HttpResponseRedirect('/')
    
class JSONFormMixin(object):
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict), content_type='application/json')
        response.status = 200 if valid_form else 500
        return response
    
class VoteFormBaseView(FormView):
    form_class = VoteForm
    
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict))
        response.status = 200 if valid_form else 500
        return response
    
    def form_valid(self, form):
        quote = get_object_or_404(Quote, pk=form.data["quote"])
        voter = get_object_or_404(User, pk=self.request.user.id)
        t = int(form.data["vote_type"])
        prev_votes = Vote.objects.filter(quote=quote, voter=voter)
        has_voted = (len(prev_votes) >0)
        
        ret = {"success": 1}
        if not has_voted:
            if t == 1:
                # create upvote
                v = Vote.objects.create(quote=quote, voter=voter, vote_type=t)
                ret["newupvoteobj"] = 1
            elif t == -1:
                # create downvote
                v = Vote.objects.create(quote=quote, voter=voter, vote_type=t)
                ret["newdownvoteobj"] = 1
        else:
            if prev_votes[0].vote_type == 1 and t == 1:
                prev_votes[0].vote_type = 0
                ret["un_upvoted"] = 1
            elif prev_votes[0].vote_type == 1 and t == -1:
                prev_votes[0].vote_type = -1
                ret["downvoteobj"] = 1
            elif prev_votes[0].vote_type == -1 and t == 1:
                prev_votes[0].vote_type = 1
                ret["upvoteobj"] = 1
            elif prev_votes[0].vote_type == -1 and t == -1:
                prev_votes[0].vote_type = 0
                ret["un_downvoted"] = 1
            elif prev_votes[0].vote_type == 0 and t == 1:
                prev_votes[0].vote_type = 1
                ret["newupvoteobj"] = 1
            elif prev_votes[0].vote_type == 0 and t == -1:
                prev_votes[0].vote_type = -1
                ret["newdownvoteobj"] = 1
            prev_votes[0].save()
        return self.create_response(ret, True)
        
    def form_invalid(self, form):
        ret = {"success": 0, "form_errors": form.errors }
        return self.create_response(ret, False)
    
class VoteFormView(JSONFormMixin, VoteFormBaseView):
    pass