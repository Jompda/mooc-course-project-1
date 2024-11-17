from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import transaction, connection
from .models import Account

# old transfer function vulnerable to injection
@transaction.atomic
def transfer(sender, receiver, amount):
	# TODO: an example query that exploits this
	if sender == receiver:
		return
	
	cursor = connection.cursor()

	cursor.execute("SELECT balance FROM pages_account WHERE id = %s" % sender)
	acc1_balance = cursor.fetchone()[0]
	cursor.execute("SELECT balance FROM pages_account WHERE id = %s" % receiver)
	acc2_balance = cursor.fetchone()[0]

	if amount <= 0:
		return
	
	if acc1_balance < amount:
		return
	
	cursor.execute("UPDATE pages_account SET balance = '%s' WHERE id = %s" % (acc1_balance - amount, sender))
	cursor.execute("UPDATE pages_account SET balance = '%s' WHERE id = %s" % (acc2_balance + amount, receiver))


@login_required
def confirmView(request):
	amount = request.session['amount'] # NOTE: Might not be parseable
	receiver = User.objects.get(username=request.session['to'])

	transfer(request.user.account.id, receiver.account.id, int(amount))
	request.user.account.refresh_from_db()
	receiver.account.refresh_from_db()
	
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
