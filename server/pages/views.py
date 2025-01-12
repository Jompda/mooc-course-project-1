from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.views.decorators.csrf import csrf_protect
from .models import Account
# A09:2021-Security Logging and Monitoring Failures
# Uncomment lines below and lines containing logger to enable logging.
#import logging
#logger = logging.getLogger(__name__)


@login_required
def homePageView(request):
	accounts = Account.objects.exclude(user_id=request.user.id)
	return render(request, 'pages/index.html', {'accounts': accounts})


@login_required
def transferView(request):
	"""
	A01:2021-Broken access control
	Program provides the client a context which contains account ids which the client then sends back to complete the transfer.
	During this time, the client can manipulate the ids and amount to their will, giving any authenticated user ability to
	transfer any amount from any account to any account.
	"""
	context = {
		'sender': request.user.account.id,
		'receiver': User.objects.get(username=request.GET.get('to')).account.id,
		'amount': request.GET.get('amount')
	}
	"""
	Fix is not to provide context and to use session to store the transaction details serverside. Access control is taken care of by the login_required
	decorator because that way request.user gets populated which is then used to determine the sender.
	Example:
	request.session['to'] = request.GET.get('to')
	request.session['amount'] = int(request.GET.get('amount'))
    """
	return render(request, 'pages/confirm.html', context)

# CSRF fix below
# @csrf_protect
@login_required
# A01:2021-Broken access control: Allows users to performs tasks not in their scope.
# Propagates from above
def confirmView(request):
	sender_id = request.GET.get('sender')
	receiver_id = request.GET.get('receiver')
	amount = int(request.GET.get('amount'))

	# A03:2021-Injection
	# FIX ON LINE 60 INSIDE COMMENT
	# Client-provided content is passed directly to a vulnerable function.
	transfer(sender_id, receiver_id, amount)
	Account.objects.get(id=sender_id).refresh_from_db()
	Account.objects.get(id=receiver_id).refresh_from_db()

	""" Fix flaw 3 by bypassing vulnerable function and retrieving transaction details from server state.
	with transaction.atomic():
		amount = request.session['amount']
		to = User.objects.get(username=request.session['to'])
		# Check that the sender actually has enough balance.
		request.user.account.balance -= amount
		to.account.balance += amount
		request.user.account.save()
		to.account.save()
    """
	#logger.info("TRANSFERRED %d from %s to %s", amount, sender_id, receiver_id)
	return redirect('/')

# Vulnerable to SQL injection
# Injection can happen in any SQL statement due to lack of sanitation.
@transaction.atomic
def transfer(sender, receiver, amount):
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
# END OF A03:2021-Injection



# To illustrate CSRF vulnerability.
def csrfView(request):
	return render(request, 'static/csrf.html')
