class VoteFormView(FormView):
    form_class = VoteForm
    
    def form_valid(self, form):
        print "form is valid"
        print form.data["quote"]
        print "this is the vote type -->" + str(form.data["vote_type"])
        print self.request.user.id
        print self.request.user
        q = get_object_or_404(Quote, pk=form.data["quote"])
        v = get_object_or_404(User, pk=self.request.user.id)
        t = form.data["vote_type"]
        prev_vote = Vote.objects.filter(voter=v, quote=q)
        print "prev_vote[0].vote_type below"
        print prev_vote[0].vote_type
        has_voted = (prev_vote.count() > 0)
        print "has voted = " + str(has_voted)
        if not has_voted:
            print "if not has_voted"
            Vote.objects.create(voter=v, quote=q, vote_type=t)
        else:
            if form.data["vote_type"] == 1 and prev_vote[0].vote_type == 1:
                prev_vote[0].delete()
            elif form.data["vote_type"] == 1 and prev_vote[0].vote_type == -1:
                prev_vote[0].vote_type = 1
                prev_vote[0].save()
            elif form.data["vote_type"] == -1 and prev_vote[0].vote_type == -1:
                prev_vote[0].delete()
            elif form.data["vote_type"] == -1 and prev_vote[0].vote_type == 1:
                prev_vote[0].vote_type = -1
                prev_vote[0].save()
            else:
                print "prev_vote[0].vote_type --->" + str(prev_vote[0].vote_type)
                prev_vote[0].vote_type = 100
                print "this is the new vote type --->" + str(prev_vote[0].vote_type)
                prev_vote[0].save()
        return redirect("/")
        
    def form_invalid(self, form):
        print form.errors
        print form.data["quote"]
        print form.data["vote_type"]
        print self.request.user.id
        print("invalid")
        return redirect("/")