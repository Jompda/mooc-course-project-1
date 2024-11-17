from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import transaction, connection
from .models import Account

# old transfer function vulnerable to injection
@transaction.atomic
def transfer(sender, receiver, amount):
	# TODO: make these use raw sql also?
	# TODO: an example query that exploits this
	acc1 = Account.objects.get(user=sender)
	acc2 = Account.objects.get(user=receiver)

	if sender == receiver:
		return

	if amount <= 0:
		return
	
	if acc1.balance < amount:
		return
	
	cursor = connection.cursor()
	cursor.execute("UPDATE pages_account SET balance = '%s' WHERE id = %s" % (acc1.balance - amount, acc1.id))
	cursor.execute("UPDATE pages_account SET balance = '%s' WHERE id = %s" % (acc2.balance + amount, acc2.id))

	acc1.refresh_from_db()
	acc2.refresh_from_db()


@login_required
def confirmView(request):
	amount = request.session['amount'] # NOTE: Might not be parseable
	to = User.objects.get(username=request.session['to'])

	transfer(request.user, to, int(amount))

	#request.user.account.balance -= amount
	#to.account.balance += amount

	#request.user.account.save()
	#to.account.save()
	
	return redirect('/')

@login_required
def transferView(request):
	request.session['to'] = request.GET.get('to')
	request.session['amount'] = int(request.GET.get('amount'))
	return render(request, 'pages/confirm.html')


@login_required
def homePageView(request):
	accounts = Account.objects.exclude(user_id=request.user.id)
	return render(request, 'pages/index.html', {'accounts': accounts})

# To illustrate CSRF
def csrfView(request):
	return render(request, 'static/csrf.html')
