from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import transaction, connection
from .models import Account


"""
A07:2021-Identification and Authentication Failures: Allows brute-force attacks
The decorator login_required doesn't provide rate-limiting per IP-address, nor account protection via lockdown.
Fix by keeping track of login attempts by IP-address and setting a hard limit for a certain amount of time.
Botnets with multiple IP-addresses are still a problem though. To protect an account,
the limit can also be set for the account itself, causing it to get locked.

A09:2021-Security Logging and Monitoring Failures: No persistent logging
For instance, money transfers are not logged anywhere making it impossible to
follow the trails and possibly reverse malicious actions.
"""
@login_required
def homePageView(request):
	accounts = Account.objects.exclude(user_id=request.user.id)
	return render(request, 'pages/index.html', {'accounts': accounts})


# A01:2021-Broken access control: Allows users to performs tasks not in their scope.
@login_required
def transferView(request):
	"""
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

# A03:2021-Injection
@login_required
def confirmView(request):
	sender_id = request.GET.get('sender')
	receiver_id = request.GET.get('receiver')
	amount = int(request.GET.get('amount'))

	# Client-provided content is passed directly to a vulnerable function.
	transfer(sender_id, receiver_id, amount)
	Account.objects.get(id=sender_id).refresh_from_db()
	Account.objects.get(id=receiver_id).refresh_from_db()

	""" Fix by bypassing vulnerable function and retrieving transaction details from server state.
	with transaction.atomic():
		amount = request.session['amount']
		to = User.objects.get(username=request.session['to'])
		# Check that the sender actually has enough balance.
		request.user.account.balance -= amount
		to.account.balance += amount
		request.user.account.save()
		to.account.save()
    """
	return redirect('/')
# END OF A01:2021-Broken access control

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
