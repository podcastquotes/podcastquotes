import json
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from core.forms import SaveQuoteForm
from quotes_app.models import Quote, SavedQuote, UserProfile
    
class JSONFormMixin(object):
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict), content_type='application/json')
        response.status = 200 if valid_form else 500
        return response
    
class SaveQuoteFormBaseView(FormView):
    form_class = SaveQuoteForm
    
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict))
        response.status = 200 if valid_form else 500
        return response
    
    def form_valid(self, form):
        quote = get_object_or_404(Quote, pk=form.data["quote"])
        saver = get_object_or_404(User, pk=self.request.user.id)
        try:
            prev_sq = SavedQuote.objects.get(quote=quote, saver=saver)
            was_saved = True
        except ObjectDoesNotExist:
            was_saved = False

        ret = {"success": 1}
        if not was_saved:
            sq = SavedQuote.objects.create(quote=quote, saver=saver)
            ret["savedquote"] = 1
        else:
            sq = SavedQuote.objects.get(quote=quote, saver=saver)
            sq.delete()
            ret["unsavedquote"] = 1
        return self.create_response(ret, True)
        
    def form_invalid(self, form):
        ret = {"success": 0, "form_errors": form.errors }
        return self.create_response(ret, False)
    
class SaveQuoteFormView(JSONFormMixin, SaveQuoteFormBaseView):
    pass